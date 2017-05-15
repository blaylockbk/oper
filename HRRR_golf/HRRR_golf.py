# Brian Blaylock
# April 24, 2017                                    Jazz are going to Game 5!!!

"""
Dallin Naulu, the superintendant over grounds at Spanish Oaks Golf Course,
inspired me to make a golf weather product using the raw HRRR
weather data. Something that displays the temperature, humidity, wind, and 
precipitation forecast with a pannel showing the simulated radar for the
surrounding area. This product can be used for any location, not just a golf
course. Added Utah Lake, Lagoon, and some MesoWest locations of interest.

(I appologize the plotting is horrendously confusing. This helps imporve speed.
Permenant map elements are created first, and are stored in a dictionary. 
Then the elements for each hour are added, the figure is save, then the
temporary plot element is removed before the next forecast hour is run. This 
completes 22 mins faster than the original script.)

To do list:
[X] Need an efficient pollywog funciton, that gets pollywog for several points 
    after downloading the file only once! i.e. download file then pluck severl
    points.
[X] Efficient use of 2D field data, only download the file once to create
    multiple maps.
[ ] Speed up by sending each forecast hour plot through a different thread.
    (issues passing figure objects between functions)
[ ] Speed up by using multithreading to create pollywogs.
[ ] Move operations to wx1, but need to create my own radar colorbar (pint doesn't work there)
[ ] Do I want to smooth out the Radar Reflectivity??? Nah!
[ ] Text labels over scatter points that show values. (why do I get a segmentation fault?)
[ ] Include Subhourly files files (would increase download time signifiantly??)
[ ] Add email alerts for certain criteria (gusts greater than 80 mph, temps > 100, temps < 32)
"""
import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates


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

daylight = time.daylight # If daylight is on (1) then subtract from timezone.

# 1) Locations (dictionary)
location = {'Oaks': {'latitude':40.084,
                     'longitude':-111.598,
                     'name':'Spanish Oaks Golf Course',
                     'timezone': 7-daylight,        # Timezone offset from UTC
                     'is MesoWest': False},         # Is the Key a MesoWest ID?
            'UKBKB': {'latitude':40.09867,
                      'longitude':-111.62767,
                      'name':'Spanish Fork Bench',
                      'timezone': 7-daylight,
                      'is MesoWest': True},
            'KSLC':{'latitude':40.77069,
                    'longitude':-111.96503,
                    'name':'Salt Lake International Airport',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'WBB':{'latitude':40.76623,
                   'longitude':-111.84755,
                   'name':'William Browning Building',
                   'timezone': 7-daylight,
                   'is MesoWest': True},
            'FREUT':{'latitude':41.15461,
                     'longitude':-112.32998,
                     'name':'Fremont Island - Miller Hill',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'GNI':{'latitude':41.33216,
                   'longitude':-112.85432,
                   'name':'Gunnison Island',
                   'timezone': 7-daylight,
                   'is MesoWest': True},
            'NAA':{'latitude':40.71152,
                   'longitude':-112.01448,
                   'name':'Neil Armstrong Academy',
                   'timezone': 7-daylight,
                   'is MesoWest': True},
            'UtahLake':{'latitude':40.159,
                        'longitude':-111.778,
                        'name':'Utah Lake',
                        'timezone': 7-daylight,
                        'is MesoWest': False},
            'UTPKL':{'latitude':40.98985,
                     'longitude':-111.90130,
                     'name':'Lagoon (UTPKL)',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'Orderville':{'latitude':37.276,
                          'longitude':-112.638,
                          'name':'Orderville',
                          'timezone': 7-daylight,
                          'is MesoWest': False},
            'BFLAT':{'latitude':40.784,
                     'longitude':-113.829,
                     'name':'Bonneville Salt Flats',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'UFD09':{'latitude':40.925,
                     'longitude':-112.159,
                     'name':'Antelope Island',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'KHIF':{'latitude':41.11112,
                    'longitude':-111.96229,
                    'name':'Hill Air Force Base',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'FPS':{'latitude':40.45689,
                   'longitude':-111.90483,
                   'name':'Flight Park South',
                   'timezone': 7-daylight,
                   'is MesoWest': True},
            'EYSC':{'latitude':40.24715,
                    'longitude':-111.65001,
                    'name':'Brigham Young University',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'UCC23':{'latitude':41.7665,
                     'longitude':-111.8105,
                     'name':'North Logan',
                     'timezone': 7-daylight,
                     'is MesoWest': True}
           }


# 2) Get the HRRR data from NOMADS
DATE = datetime.utcnow() - timedelta(hours=1)
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)

print "Local DATE:", datetime.now()
print "  UTC DATE:", DATE

# 2.1) Pollywogs: Pluck HRRR value at all locations for each variable.
#      These are dictionaries:
#      {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}
print "plucking values from HRRR"
P_temp = get_hrrr_pollywog_multi(DATE, 'TMP:2 m', location, verbose=False); print "got Temp"
P_dwpt = get_hrrr_pollywog_multi(DATE, 'DPT:2 m', location, verbose=False); print "got Dwpt"
P_wind = get_hrrr_pollywog_multi(DATE, 'WIND:10 m', location, verbose=False); print "got Wind"
P_gust = get_hrrr_pollywog_multi(DATE, 'GUST:surface', location, verbose=False); print "got Gust"
P_u = get_hrrr_pollywog_multi(DATE, 'UGRD:10 m', location, verbose=False); print "got U10"
P_v = get_hrrr_pollywog_multi(DATE, 'VGRD:10 m', location, verbose=False); print "got V10"
P_prec = get_hrrr_pollywog_multi(DATE, 'APCP:surface', location, verbose=False); print "got Precip"

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

# Check for extreame values and send email alert
from HRRR_warning import *
for warn in ['UKBKB', 'KSLC']:
    wind_warning(location, P_wind, warn)
    temp_warning(location, P_temp, warn)

maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                llcrnrlon=l['longitude']-.25, llcrnrlat=l['latitude']-.25,\
                urcrnrlon=l['longitude']+.25, urcrnrlat=l['latitude']+.25,)
    maps[loc] = m


# Create a figure for each location. Add permenant elements to each.
print 'making permenant figure elements...'
figs = {}
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    tz = l['timezone']
    figs[locName] = {0:plt.figure(n)}
    plt.suptitle('HRRR Forecast: %s' % (l['name']), y=1)
    # Map - background, roads, radar, wind barbs
    figs[locName][1] = figs[locName][0].add_subplot(121)
    maps[locName].drawcounties()
    maps[locName].arcgisimage(service='World_Shaded_Relief',
                              xpixels=700, # Utah lake wont show if it's less than 700
                              verbose=False)
    # Overlay Utah Roads
    BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    maps[locName].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
                                'roads',
                                linewidth=.5,
                                color='dimgrey')
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
    local = np.array(P_prec['DATETIME']) - timedelta(hours=tz)
    accumP = np.add.accumulate(P_prec[locName])
    figs[locName][4].bar(local, P_prec[locName], width=.04, color='dodgerblue', label='1 hour Precipitation')
    figs[locName][4].plot(local, accumP, color='limegreen', label='Accumulated Precipitation')
    figs[locName][4].set_xlim([local[0], local[-1]])
    figs[locName][4].set_ylim([0, np.nanmax(accumP)+.1])
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
            maxT = np.nanmax([np.nanmax(P_temp[locName]), np.nanmax(CtoF(a['air_temp']))])
            minT = np.nanmin([np.nanmin(P_dwpt[locName]), np.nanmin(CtoF(a['dew_point_temperature']))])
            figs[locName][2].set_ylim([minT-3, maxT+3])

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
        tz = l['timezone']
        print "\n--> Working on:", locName, fxx
        #
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/%s/' % locName
        if not os.path.exists(SAVE):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer2.php'
            os.link(photo_viewer, SAVE+'photo_viewer2.php')
        # Title over map
        figs[locName][1].set_title('          UTC: %s\nLocal Time: %s' % (DATE+timedelta(hours=fxx), DATE+timedelta(hours=fxx)-timedelta(hours=tz)))
        figs[locName][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (H['anlys'].strftime('%Y %b %d, %H:%M'), fxx, H['valid'].strftime('%Y %b %d, %H:%M')))
        #
        # Project on map
        X, Y = maps[locName](H['lon'], H['lat'])            # HRRR grid
        # Trim the data
        cut_v, cut_h = pluck_point_new(l['latitude'],
                                       l['longitude'],
                                       H['lat'],
                                       H['lon'])
        bfr = 15
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
                                    extra='&radius=%s,%s,30' % (l['latitude'], l['longitude']),
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
        barbs = figs[locName][1].barbs(trim_X, trim_Y, trim_H_U, trim_H_V, zorder=200, length=6)
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
        pntPrec = figs[locName][4].scatter(local[fxx], accumP[fxx], edgecolor="k", color='limegreen', s=60)
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
