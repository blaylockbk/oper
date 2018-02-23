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
[ ] Include Subhourly files files (would increase download time significantly??)
[ ] Add email alerts for certain criteria (gusts greater than 80 mph, temps > 100, temps < 32)
"""
import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates
import h5py


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
mpl.rcParams['savefig.transparent'] = False

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from MetPy_BB.plots import ctables
from BB_data.grid_manager import pluck_point_new
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *
from BB_cmap.landuse_colormap import LU_MODIS21
import location_dic

## 1) Get Locations Dictionary
location = location_dic.get_all()

"""
# shorten the dictionary for quick testing:
L = {}
for i in location.keys()[0:2]:
    L[i]=location[i]

location = L
"""

## 2) Make map object for each location and store in a dictionary
maps = {}
for loc in location:
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                llcrnrlon=l['longitude']-.3, llcrnrlat=l['latitude']-.3,\
                urcrnrlon=l['longitude']+.3, urcrnrlat=l['latitude']+.3,)
    maps[loc] = m


## 3) Create a landuse image for each the locations
##    Create new figure every day because landuse ice cover changes on lakes
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
LU = get_hrrr_variable(datetime.now(), 'VGTYP:surface')
cm, labels = LU_MODIS21()
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    LU_SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/%s/LandUse.png' % locName.replace(' ', '_')
    #if not os.path.isfile(LU_SAVE):
    if False:
        plt.figure(100)
        print "need to make", LU_SAVE
        maps[locName].pcolormesh(LU['lon'], LU['lat'], LU['value'],
                                cmap=cm, vmin=1, vmax=len(labels) + 1,
                                latlon=True)
        cb = plt.colorbar(orientation='vertical', pad=.01, shrink=.95)
        cb.set_ticks(np.arange(0.5, len(labels) + 1))
        cb.ax.set_yticklabels(labels)
        maps[locName].scatter(l['longitude'], l['latitude'], marker='+', c='maroon', s=100, latlon=True)
        maps[locName].drawstates()
        maps[locName].drawcounties()
        plt.title('Landuse near %s' % locName)
        plt.savefig(LU_SAVE)  
        print "created landuse maps for ", locName
        plt.close()


## 4) Get the HRRR data from NOMADS
DATE = datetime.utcnow() - timedelta(hours=1) # hour delay in forecasts available
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)

print " My DATE:", datetime.now()
print "UTC DATE:", DATE

# Pollywogs: Pluck HRRR value at all locations for each variable.
# These are dictionaries:
# {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}
print "plucking values from HRRR"
P_temp = get_hrrr_pollywog_multi(DATE, 'TMP:2 m', location, verbose=False); print "got Temp"
P_dwpt = get_hrrr_pollywog_multi(DATE, 'DPT:2 m', location, verbose=False); print "got Dwpt"
P_wind = get_hrrr_pollywog_multi(DATE, 'WIND:10 m', location, verbose=False); print "got Wind"
P_gust = get_hrrr_pollywog_multi(DATE, 'GUST:surface', location, verbose=False); print "got Gust"
P_u = get_hrrr_pollywog_multi(DATE, 'UGRD:10 m', location, verbose=False); print "got U10"
P_v = get_hrrr_pollywog_multi(DATE, 'VGRD:10 m', location, verbose=False); print "got V10"
P_prec = get_hrrr_pollywog_multi(DATE, 'APCP:surface', location, verbose=False); print "got Precip"
P_accum = {} # Accumulated precipitation

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
    P_accum[loc] = np.add.accumulate(P_prec[loc]) # Accumulated Precipitation


## 5) Check for extreme values and send email alert
from HRRR_warning import *
try:
    for warn in ['UKBKB', 'KSLC']:
        wind_warning(location, P_wind, warn)
        temp_warning(location, P_temp, warn)
except:
    pass


## 6) Create a figure for each location and add permenant elements
print 'Making permenant figure elements...'
figs = {}
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
for n in locs_idx:
    locName = locs[n]
    print '   --> %s' % locName
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
    maps[locName].scatter(l['longitude'], l['latitude'], s=100, color='white', edgecolor='k', zorder=100, latlon=True)
    #
    # Plot: Temperature, dewpoint
    figs[locName][2] = figs[locName][0].add_subplot(322)
    figs[locName][2].plot(P_temp['DATETIME'], P_temp[locName], c='r', label='Temperature', zorder=50)
    figs[locName][2].plot(P_dwpt['DATETIME'], P_dwpt[locName], c='g', label='Dew Point', zorder=50)
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
    figs[locName][3].plot(P_gust['DATETIME'], P_gust[locName], c='chocolate', label='Instantaneous Wind Gust', zorder=50)
    figs[locName][3].plot(P_wind['DATETIME'], P_wind[locName], c='darkorange', label='Previous Hour Max Wind', zorder=50)
    # plt.barbs can not take a datetime object, so find the date indexes:
    idx = mpl.dates.date2num(P_u['DATETIME'])
    figs[locName][3].barbs(idx, wind_uv_to_spd(P_u[locName], P_v[locName]), P_u[locName], P_v[locName],
                           length=6,
                           barb_increments=dict(half=5, full=10, flag=50), zorder=50)
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
    figs[locName][4].bar(P_prec['DATETIME'], P_prec[locName], width=.04, color='dodgerblue', label='1 hour Precipitation', zorder=50)
    figs[locName][4].plot(P_prec['DATETIME'], P_accum[locName], color='limegreen', label='Accumulated Precipitation', zorder=50)
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
            figs[locName][2].plot(a['DATETIME'], CtoF(a['air_temp']), c='k', ls='--', zorder=50)
            figs[locName][2].plot(a['DATETIME'], CtoF(a['dew_point_temperature']), c='k', ls='--', zorder=50)
            figs[locName][3].plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--', zorder=50)
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
        if not os.path.exists(SAVE+'OSG_climo/'):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE+'OSG_climo/')
            print "created:", SAVE+'OSG_climo/'
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
        pntTemp = figs[locName][2].scatter(P_temp['DATETIME'][fxx], tempF[fxx], c='r', s=60, zorder=100)
        pntDwpt = figs[locName][2].scatter(P_dwpt['DATETIME'][fxx], dwptF[fxx], c='g', s=60, zorder=100)
        #
        # 3.3) Wind speed and Barbs
        pntGust = figs[locName][3].scatter(P_gust['DATETIME'][fxx], P_gust[locName][fxx], c='chocolate', s=60, zorder=100)
        pntWind = figs[locName][3].scatter(P_wind['DATETIME'][fxx], P_wind[locName][fxx], c='darkorange', s=60, zorder=100)
        #
        # 3.4) Accumulated Precipitation
        pntPrec = figs[locName][4].scatter(P_prec['DATETIME'][fxx], P_accum[locName][fxx], edgecolor="k", color='limegreen', s=60, zorder=100)
        #
        # 4) Save figure
        figs[locName][0].savefig(SAVE+'f%02d.png' % (fxx))

        # --- Create Climatology graph ----------------------------------------
        if fxx == 0:
            var = 'TMP:2 m'
            variable = var.replace(':', '_').replace(' ', '_')
            x = cut_v[0]
            y = cut_h[0]
            OSG_DIR = '/uufs/chpc.utah.edu/common/home/horel-group2/blaylock/HRRR_OSG/hourly30/%s/' % (variable)
            p100 = np.array([])
            p75 = np.array([])
            p50 = np.array([])
            p25 = np.array([])
            p00 = np.array([])
            for D in P_temp['DATETIME']:
                FILE = 'OSG_HRRR_%s_m%02d_d%02d_h%02d_f00.h5' % (variable, D.month, D.day, D.hour)
                with h5py.File(OSG_DIR+FILE, 'r') as f:
                    p100 = np.append(p100, f['p100'][x][y])
                    p75 = np.append(p75, f['p75'][x][y])
                    p50 = np.append(p50, f['p50'][x][y])
                    p25 = np.append(p25, f['p25'][x][y])
                    p00 = np.append(p00, f['p00'][x][y])
            if var == 'TMP:2 m' or var == 'DPT:2 m':
                p100 = KtoF(p100)
                p75 = KtoF(p75)
                p50 = KtoF(p50)
                p25 = KtoF(p25)
                p00 = KtoF(p00)
            OSG1 = figs[locName][2].fill_between(P_temp['DATETIME'], p100, p00, color='lightgrey',zorder=1, alpha=.25)
            OSG2 = figs[locName][2].fill_between(P_temp['DATETIME'], p25, p75, color='grey',zorder=1, alpha=.25)
            OSG3 = figs[locName][2].plot(P_temp['DATETIME'], p50, color='lightgrey',zorder=1, alpha=.25)
        figs[locName][0].savefig(SAVE+'/OSG_climo/'+'f%02d.png' % (fxx))
        # ---------------------------------------------------------------------

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
