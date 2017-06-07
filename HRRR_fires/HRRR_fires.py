# Brian Blaylock
# May 8, 2017                                  Jazz might get swept tonight :(

"""
An extenstion to the HRRR Golf scripts, these create forecasts for large fires
in the United States.

To do list:
[ ] Speed up by sending each forecast hour plot through a different thread.
[ ] Speed up by using multithreading to create pollywogs.
[ ] Move operations to wx1, but need to create my own radar colorbar (pint doesn't work there)
[ ] Do I want to smooth out the Radar Reflectivity??? Nah!
[ ] Text labels over scatter points that show values.
[ ] What causes the Segmentation Fault (core dumped)??
[ ] Include Subhourly files files
"""
import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import date, datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.figsize'] = [15, 6]
mpl.rcParams['figure.titlesize'] = 15
mpl.rcParams['figure.titleweight'] = 'bold'
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['lines.linewidth'] = 1.8
mpl.rcParams['grid.linewidth'] = .25
mpl.rcParams['figure.subplot.wspace'] = 0.05
mpl.rcParams['figure.subplot.hspace'] = 0.05
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = True

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_oper import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from MetPy_BB.plots import ctables
from BB_data.grid_manager import pluck_point_new
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *
from BB_basemap.draw_maps import draw_CONUS_cyl_map

get_today = datetime.strftime(date.today(), "%Y-%m-%d")
daylight = time.daylight # If daylight is on (1) then subtract from timezone.

# 1) Read in large fires file:
fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab

fires = np.genfromtxt(fires_file, names=True, dtype=None,delimiter='\t')
#column names:
    # 0  INAME - Incident Name
    # 1  INUM
    # 2  CAUSE
    # 3  REP_DATE - reported date
    # 4  START_DATE
    # 5  IMT_TYPE
    # 6  STATE
    # 7  AREA
    # 8  P_CNT - Percent Contained
    # 9  EXP_CTN - Expected Containment
    # 10 LAT
    # 11 LONG
    # 12 COUNTY
print "there are", len(fires), "large fires"

# 1) Locations (dictionary)
location = {}
for F in range(0,len(fires)):
    FIRE = fires[F]
    # 1) Get Latitude and Longitude for the indexed large fire [fire]
    # No HRRR data for Alaska or Hawaii, so don't do it.
    # Also, don't bother running fires less than 1000 acres
    if FIRE[7] < 1000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
        continue
    location[FIRE[0]] = {'latitude': FIRE[10],
                         'longitude': FIRE[11],
                         'name': FIRE[0],
                         'state': FIRE[6],
                         'area': FIRE[7],
                         'start date': FIRE[4],
                         'is MesoWest': False
                        }

# 2) Get the HRRR data from NOMADS
DATE = datetime.utcnow() - timedelta(hours=1)
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)

print "Local DATE:", datetime.now()
print "  UTC DATE:", DATE

# 2.1) Pollywogs: Pluck HRRR value at all locations for each variable.
#      These are dictionaries:
#      {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}
P_temp = get_hrrr_pollywog_multi(DATE, 'TMP:2 m', location, verbose=False); print 'got temps'
P_dwpt = get_hrrr_pollywog_multi(DATE, 'DPT:2 m', location, verbose=False); print 'got dwpt'
P_wind = get_hrrr_pollywog_multi(DATE, 'WIND:10 m', location, verbose=False); print 'got wind'
P_gust = get_hrrr_pollywog_multi(DATE, 'GUST:surface', location, verbose=False); print 'got gust'
P_u = get_hrrr_pollywog_multi(DATE, 'UGRD:10 m', location, verbose=False); print 'got u vectors'
P_v = get_hrrr_pollywog_multi(DATE, 'VGRD:10 m', location, verbose=False); print 'got v vectors'
P_prec = get_hrrr_pollywog_multi(DATE, 'APCP:surface', location, verbose=False); print 'got prec'
P_accum = {}
P_ref = get_hrrr_pollywog_multi(DATE, 'REFC:entire atmosphere', location, verbose=False); print 'got composite reflectivity'

# Convert the units of each Pollywog and each location
for loc in location.keys():
    # Convert Units for the variables in the Pollywog
    P_temp[loc] = KtoF(P_temp[loc])
    P_dwpt[loc] = KtoF(P_dwpt[loc])
    P_wind[loc] = mps_to_MPH(P_wind[loc])
    P_gust[loc] = mps_to_MPH(P_gust[loc])
    P_u[loc] = mps_to_MPH(P_u[loc])
    P_v[loc] = mps_to_MPH(P_v[loc])
    P_prec[loc] = mm_to_inches(P_prec[loc])
    P_accum[loc] = np.add.accumulate(P_prec[loc])

# Check for high winds and append to alerts list and webpage
from HRRR_fires_alerts import *
alert_wind(location, P_wind, P_gust, P_ref)
write_alerts_html()

# Make a dictionary of map object for each location.
# (This speeds up plotting by creating each map once.)
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                llcrnrlon=l['longitude']-.75, llcrnrlat=l['latitude']-.75,\
                urcrnrlon=l['longitude']+.75, urcrnrlat=l['latitude']+.75,)
    maps[loc] = m

# Create a figure for each location. Add permenant elements to each.
print 'making permenant figure elements...'
figs = {}
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    figs[locName] = {0:plt.figure(n)}
    # Super Title
    if l['state'] != 'Not Reported':
        plt.suptitle('HRRR Forecast: %s, %s' % (l['name'], l['state']), y=1)
    else:
        plt.suptitle('HRRR Forecast: %s, (state not reported)' % (l['name']), y=1)
    # Map - background, roads, radar, wind barbs
    figs[locName][1] = figs[locName][0].add_subplot(121)
    maps[locName].drawcounties()
    maps[locName].drawstates()
    maps[locName].arcgisimage(service='World_Shaded_Relief',
                              xpixels=500,
                              verbose=False)
    #
    # Overlay Fire Perimeters
    per = maps[locName].readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim','perim', drawbounds=False)
    patches = []
    print 'finding fire perimeter patches...',
    for info, shape in zip(maps[locName].perim_info, maps[locName].perim):
        # Check if the boundary is one of the large active fires
        if info['FIRENAME'].upper() in location.keys():
            patches.append(Polygon(np.array(shape), True) )
    figs[locName][1].add_collection(PatchCollection(patches, facecolor='indianred', alpha=.65, edgecolor='k', linewidths=.1, zorder=1))
    print 'Done!'
    #
    # Overlay Utah Roads
    #BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    #maps[locName].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
    #                            'roads',
    #                            linewidth=.5)
    x, y = m(l['longitude'], l['latitude']) # Location
    maps[locName].scatter(x, y, s=100, color='white', edgecolor='k', zorder=100)
    #
    # Plot: Temperature, dewpoint
    figs[locName][2] = figs[locName][0].add_subplot(322)
    figs[locName][2].plot(P_temp['DATETIME'], P_temp[locName], c='r', label='Temperature')
    figs[locName][2].plot(P_dwpt['DATETIME'], P_dwpt[locName], c='g', label='Dew Point')
    leg2 = figs[locName][2].legend()
    leg2.get_frame().set_linewidth(0)
    figs[locName][2].grid()
    figs[locName][2].set_ylabel('Degrees (F)')
    figs[locName][2].set_xlim([P_temp['DATETIME'][0], P_temp['DATETIME'][-1]])
    figs[locName][2].set_ylim([np.nanmin(P_dwpt[locName])-3, np.nanmax(P_temp[locName])+3])
    figs[locName][2].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][2].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][2].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Wind speed, gust, barbs
    figs[locName][3] = figs[locName][0].add_subplot(324)
    figs[locName][3].plot(P_gust['DATETIME'], P_gust[locName], c='chocolate', label='Instantaneous Wind Gust')
    figs[locName][3].plot(P_wind['DATETIME'], P_wind[locName], c='darkorange', label='Previous Hour Max Wind')
    # plt.barbs can not take a datetime object, so find the date indexes:
    idx = mpl.dates.date2num(P_u['DATETIME'])
    figs[locName][3].barbs(idx, wind_uv_to_spd(P_u[locName], P_v[locName]), P_u[locName], P_v[locName],
                           length=6,
                           barb_increments=dict(half=5, full=10, flag=50))
    leg3 = figs[locName][3].legend()
    leg3.get_frame().set_linewidth(0)
    figs[locName][3].grid()
    #figs[locName][3].set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
    figs[locName][3].set_ylabel('Wind Speed (mph)')
    figs[locName][3].set_ylim([0, np.nanmax(P_gust[locName])+3])
    figs[locName][3].set_yticks([0, np.nanmax(P_gust[locName])+3], 2.5)
    figs[locName][3].set_xlim([P_gust['DATETIME'][0], P_gust['DATETIME'][-1]])
    figs[locName][3].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][3].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][3].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Accumulated precip
    figs[locName][4] = figs[locName][0].add_subplot(326)
    figs[locName][4].bar(P_prec['DATETIME'], P_prec[locName], width=.04, color='dodgerblue', label='1 hour Precipitation')
    figs[locName][4].plot(P_prec['DATETIME'], P_accum[locName], color='limegreen', label='Accumulated Precipitation')
    figs[locName][4].set_xlim([P_prec['DATETIME'][0], P_prec['DATETIME'][-1]])
    figs[locName][4].set_ylim([0, np.nanmax(P_accum[locName])+.1])
    figs[locName][4].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][4].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][4].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))
    leg4 = figs[locName][4].legend()
    leg4.get_frame().set_linewidth(0)
    figs[locName][4].grid()
    figs[locName][4].set_ylabel('Precipitation (in)')
    #
    # Finally, add MesoWest data if it is available
    if l['is MesoWest'] is True:
        a = get_mesowest_ts(locName, DATE, datetime.utcnow(),
                            variables='air_temp,wind_speed,dew_point_temperature')
        if a != 'ERROR':
            figs[locName][2].plot(a['DATETIME'], CtoF(a['air_temp']), c='k', ls='--')
            figs[locName][2].plot(a['DATETIME'], CtoF(a['dew_point_temperature']), c='k', ls='--')
            figs[locName][3].plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--')

# Now add the element that changes, save the figure, and remove elements from plot.
# Only download the HRRR grid once per forecast hour.
for fxx in range(0, 19):
    # Loop through each location to make plots for this time
    # 2.2) Radar Reflectivity and winds for entire CONUS
    H = get_hrrr_variable(DATE, 'REFC:entire atmosphere', fxx=fxx, model='hrrr')
    H_U = get_hrrr_variable(DATE, 'UGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_V = get_hrrr_variable(DATE, 'VGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    #
    # Convert Units (meters per second -> miles per hour)
    H_U['value'] = mps_to_MPH(H_U['value'])
    H_V['value'] = mps_to_MPH(H_V['value'])
    #
    # Mask out empty reflectivity values
    dBZ = H['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked
    #
    for n in locs_idx:
        locName = locs[n]
        l = location[locName]
        print "\n--> Working on:", locName, fxx
        #
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/' % locName.replace(' ', '_')
        if not os.path.exists(SAVE):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer_fire.php'
            os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
        # Title over map
        figs[locName][1].set_title('UTC: %s' % (DATE+timedelta(hours=fxx)))
        figs[locName][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (H['anlys'].strftime('%Y %b %d, %H:%M'), fxx, H['valid'].strftime('%Y %b %d, %H:%M')))
        #
        # Project on map
        X, Y = maps[locName](H['lon'], H['lat'])            # HRRR grid
        # Trim the data
        cut_v, cut_h = pluck_point_new(l['latitude'],
                                       l['longitude'],
                                       H['lat'],
                                       H['lon'])
        bfr = 35
        trim_X = X[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_Y = Y[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_dBZ = dBZ[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_H_U = H_U['value'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        trim_H_V = H_V['value'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
        #
        # Overlay Simulated Radar Reflectivity
        ctable = 'NWSReflectivity'
        norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
        radar = figs[locName][1].pcolormesh(trim_X, trim_Y, trim_dBZ, norm=norm, cmap=cmap, alpha=.5)
        if fxx == 0:
            # Solution for adding colorbar from stackoverflow
            # http://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(figs[locName][1])
            cax = divider.append_axes('bottom', size='5%', pad=0.05)
            cb = figs[locName][0].colorbar(radar, cax=cax, orientation='horizontal')
            cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=5 mph, Full=10 mph, Flag=50 mph')
        #
        # Add nearby MesoWest 
        if fxx in [0, 1]:
            MW_date = P_temp['DATETIME'][fxx]
            b = get_mesowest_radius(MW_date, 15,
                                    extra='&radius=%s,%s,60' % (l['latitude'], l['longitude']),
                                    variables='wind_speed,wind_direction')
            if len(b['NAME']) > 0:
                MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'], b['wind_direction'])
                MW_u = mps_to_MPH(MW_u)
                MW_v = mps_to_MPH(MW_v)
                MWx, MWy = maps[loc](b['LON'], b['LAT'])
                MW_barbs = figs[locName][1].barbs(MWx, MWy, MW_u, MW_v,
                                                  color='r',
                                                  barb_increments=dict(half=5, full=10, flag=50))
        #
        # Wind Barbs
        # Overlay wind barbs (need to trim this array before we plot it)
        # First need to trim the array
        barbs = figs[locName][1].barbs(trim_X[::3,::3], trim_Y[::3,::3], trim_H_U[::3,::3], trim_H_V[::3,::3], zorder=200, length=5)
        #
        # 3.2) Temperature/Dew Point
        tempF = P_temp[locName]
        dwptF = P_dwpt[locName]
        pntTemp = figs[locName][2].scatter(P_temp['DATETIME'][fxx], tempF[fxx], c='r', s=60)
        pntDwpt = figs[locName][2].scatter(P_dwpt['DATETIME'][fxx], dwptF[fxx], c='g', s=60)
        #
        # 3.3) Wind speed and Barbs
        pntGust = figs[locName][3].scatter(P_gust['DATETIME'][fxx], P_gust[locName][fxx], c='chocolate', s=60)
        pntWind = figs[locName][3].scatter(P_wind['DATETIME'][fxx], P_wind[locName][fxx], c='darkorange', s=60)
        #
        # 3.4) Accumulated Precipitation
        pntPrec = figs[locName][4].scatter(P_prec['DATETIME'][fxx], P_accum[locName][fxx], edgecolor="k", color='limegreen', s=60)
        #
        # 4) Save figure
        figs[locName][0].savefig(SAVE+'f%02d.png' % (fxx))
        #
        pntTemp.remove()
        pntDwpt.remove()
        pntGust.remove()
        pntWind.remove()
        pntPrec.remove()
        barbs.remove()
        radar.remove()
        try:
            MW_barbs.remove()
        except:
            # No barbs were plotted
            pass
    print "Finished:", fxx

# Do some webpage managment:
#  - Removes old fires from the directory
#  - Edits HTML to include current fires
#  - Plots a map of the fires
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/')
from manager import *
remove_old_fires(location)
write_HRRR_fires_HTML(location)
draw_fires_on_map(location)
