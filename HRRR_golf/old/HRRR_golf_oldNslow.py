# Brian Blaylock
# April 24, 2017                                    Jazz are going to Game 5!!!

"""
Dallin Naulu, the superintendant over grounds at Spanish Oaks Golf Course,
inspired me to make a golf weather product using the raw HRRR
weather data. Something that displays the temperature, humidity, wind, and 
precipitation forecast with a pannel showing the simulated radar for the
surrounding area. This product can be used for any location, not just a golf
course. Added Utah Lake, Lagoon, and some MesoWest locations of interest.

To do list:
[X] Need an efficient pollywog funciton, that gets pollywog for several points 
    after downloading the file only once! i.e. download file then pluck severl
    points.
[X] Efficient use of 2D field data, only download the file once to create
    multiple maps.
[ ] Speed up by sending each forecast hour plot through a different thread.
[ ] Speed up by using multithreading to create pollywogs.
[ ] Move operations to wx1, but need to create my own radar colorbar (pint doesn't work there)
[ ] Do I want to smooth out the Radar Reflectivity??? Nah!
[ ] Text labels over scatter points that show values.
[ ] What causes the Segmentation Fault (core dumped)??
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
P_temp = get_hrrr_pollywog_multi(DATE, 'TMP:2 m', location)
P_dwpt = get_hrrr_pollywog_multi(DATE, 'DPT:2 m', location)
P_wind = get_hrrr_pollywog_multi(DATE, 'WIND:10 m', location)
P_gust = get_hrrr_pollywog_multi(DATE, 'GUST:surface', location)
P_u = get_hrrr_pollywog_multi(DATE, 'UGRD:10 m', location)
P_v = get_hrrr_pollywog_multi(DATE, 'VGRD:10 m', location)
P_prec = get_hrrr_pollywog_multi(DATE, 'APCP:surface', location)

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

# Make a dictionary of map object for each location.
# (This speeds up plotting by creating each map once.)
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                llcrnrlon=l['longitude']-.1, llcrnrlat=l['latitude']-.1,\
                urcrnrlon=l['longitude']+.1, urcrnrlat=l['latitude']+.1,)
    maps[loc] = m

for fxx in range(0, 19):
    # 2.2) Radar Reflectivity and winds for entire CONUS
    H = get_hrrr_variable(DATE, 'REFC:entire atmosphere', fxx=fxx, model='hrrr')
    H_U = get_hrrr_variable(DATE, 'UGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_V = get_hrrr_variable(DATE, 'VGRD:10 m', fxx=fxx, model='hrrr', value_only=True)

    # Convert Units (meters per second -> miles per hour)
    H_U['value'] = mps_to_MPH(H_U['value'])
    H_V['value'] = mps_to_MPH(H_V['value'])

    # Mask out empty reflectivity values
    dBZ = H['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked

    # Loop through each location to make plots for this time
    for loc in location.keys():
        print "\n--> Working on:", loc

        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/%s/' % loc
        if not os.path.exists(SAVE):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer2.php'
            os.link(photo_viewer, SAVE+'photo_viewer2.php')

        # 3) Create a Map and plot for each location
        plt.clf()
        plt.cla()

        # Get the dictionary for the location, includes lat/lon, name, timezone
        l = location[loc]
        tz = l['timezone']

        # Super Title
        plt.suptitle('HRRR Forecast: %s' % (l['name']), y=1)

        # 3.1) Map
        ax1 = plt.subplot(1, 2, 1)

        # Add ESRI background image
        maps[loc].arcgisimage(service='World_Shaded_Relief',
                              xpixels=500,
                              verbose=False)

        # Project the lat/lon on th map
        x, y = m(l['longitude'], l['latitude']) # Location
        X, Y = m(H['lon'], H['lat'])            # HRRR grid

        # Plot point for location
        maps[loc].scatter(x, y, s=100, color='white', edgecolor='k', zorder=100)

        # Overlay Simulated Radar Reflectivity
        ctable = 'NWSReflectivity'
        norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
        maps[loc].pcolormesh(X, Y, dBZ, norm=norm, cmap=cmap, alpha=.5)
        cb = plt.colorbar(orientation='horizontal', pad=0.01, shrink=0.7)
        cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=5 mph, Full=10 mph, Flag=50 mph')

        # Overlay wind barbs (need to trim this array before we plot it)
        # First need to trim the array
        cut_v, cut_h = pluck_point_new(l['latitude'],
                                       l['longitude'],
                                       H['lat'],
                                       H['lon'])
        maps[loc].barbs(X[cut_v-5:cut_v+5, cut_h-5:cut_h+5],
                        Y[cut_v-5:cut_v+5, cut_h-5:cut_h+5],
                        H_U['value'][cut_v-5:cut_v+5, cut_h-5:cut_h+5],
                        H_V['value'][cut_v-5:cut_v+5, cut_h-5:cut_h+5],
                        zorder=200)

        # Overlay observed winds, if they are available (first two hours)
        if fxx in [0, 1]:
            MW_date = P_temp['DATETIME'][fxx]
            b = get_mesowest_radius(MW_date, 15,
                                    extra='&radius=%s,%s,20' % (l['latitude'], l['longitude']),
                                    variables='wind_speed,wind_direction')
            if len(b['NAME']) > 0:
                MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'], b['wind_direction'])
                MW_u = mps_to_MPH(MW_u)
                MW_v = mps_to_MPH(MW_v)
                MWx, MWy = maps[loc](b['LON'], b['LAT'])
                ax1.barbs(MWx, MWy, MW_u, MW_v,
                        color='r',
                        barb_increments=dict(half=5, full=10, flag=50))

        # Overlay Utah Roads
        BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
        maps[loc].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
                                'roads',
                                linewidth=.5)

        # Title over map
        ax1.set_title('          UTC: %s\nLocal Time: %s' % (DATE+timedelta(hours=fxx), DATE+timedelta(hours=fxx)-timedelta(hours=tz)))

        # 3.2) Temperature/Dew Point
        ax2 = plt.subplot(3, 2, 2)
        tempF = P_temp[loc]
        dwptF = P_dwpt[loc]
        ax2.plot(P_temp['DATETIME'], tempF, c='r', label='Temperature')
        ax2.scatter(P_temp['DATETIME'][fxx], tempF[fxx], c='r', s=60)
        ax2.plot(P_dwpt['DATETIME'], dwptF, c='g', label='Dew Point')
        ax2.scatter(P_dwpt['DATETIME'][fxx], dwptF[fxx], c='g', s=60)
        if l['is MesoWest'] is True:
            a = get_mesowest_ts(loc, DATE, datetime.utcnow(),
                                variables='air_temp,wind_speed,dew_point_temperature')
            if a != 'ERROR':
                ax2.plot(a['DATETIME'], CtoF(a['air_temp']), c='k', ls='--')
                ax2.plot(a['DATETIME'], CtoF(a['dew_point_temperature']), c='k', ls='--')

        leg2 = ax2.legend()
        leg2.get_frame().set_linewidth(0)
        ax2.grid()
        ax2.set_ylabel('Degrees (F)')
        ax2.set_xlim([P_temp['DATETIME'][0], P_temp['DATETIME'][-1]])
        if l['is MesoWest'] is True and a != 'ERROR':
            maxT = np.nanmax([np.nanmax(tempF), np.nanmax(CtoF(a['air_temp']))])
            minT = np.nanmin([np.nanmin(dwptF), np.nanmin(CtoF(a['dew_point_temperature']))])
        else:
            maxT = np.nanmax(tempF)
            minT = np.nanmin(dwptF)
        ax2.set_ylim([minT-3, maxT+3])
        ax2.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax2.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter(''))

        ax2.set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (H['anlys'].strftime('%Y %b %d, %H:%M'), fxx, H['valid'].strftime('%Y %b %d, %H:%M')))

        # 3.3) Wind speed and Barbs
        ax3 = plt.subplot(3, 2, 4)
        ax3.plot(P_gust['DATETIME'], P_gust[loc], c='chocolate', label='Instantaneous Wind Gust')
        ax3.scatter(P_gust['DATETIME'][fxx], P_gust[loc][fxx], c='chocolate', s=60)
        ax3.plot(P_wind['DATETIME'], P_wind[loc], c='darkorange', label='Previous Hour Max Wind')
        ax3.scatter(P_wind['DATETIME'][fxx], P_wind[loc][fxx], c='darkorange', s=60)
        if l['is MesoWest'] is True:
            # we alreaded loaded mesowest data into a
            if a != 'ERROR':
                ax3.plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--')

        # plt.barbs can not take a datetime object, so find the date indexes:
        idx = mpl.dates.date2num(P_u['DATETIME'])
        ax3.barbs(idx, wind_uv_to_spd(P_u[loc], P_v[loc]), P_u[loc], P_v[loc],
                  length=6,
                  barb_increments=dict(half=5, full=10, flag=50))

        leg3 = ax3.legend()
        leg3.get_frame().set_linewidth(0)
        ax3.grid()
        #ax3.set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
        ax3.set_ylabel('Wind Speed (mph)')
        ax3.set_ylim([0, np.nanmax(P_gust[loc])+3])
        ax3.set_yticks([0, np.nanmax(P_gust[loc])+3], 2.5)
        ax3.set_xlim([P_gust['DATETIME'][0], P_gust['DATETIME'][-1]])
        ax3.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax3.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter(''))

        # 3.4) Accumulated Precipitation
        local = np.array(P_prec['DATETIME']) - timedelta(hours=tz)
        accumP = np.add.accumulate(P_prec[loc])
        ax4 = plt.subplot(3, 2, 6)
        ax4.bar(local, P_prec[loc], width=.04, color='dodgerblue', label='1 hour Precipitation')
        ax4.plot(local, accumP, color='limegreen', label='Accumulated Precipitation')
        ax4.scatter(local[fxx], accumP[fxx], color='limegreen', s=60)
        ax4.set_xlim([local[0], local[-1]])
        ax4.set_ylim([0, np.nanmax(accumP)+.1])
        ax4.xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
        ax4.xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))

        leg4 = ax4.legend()
        leg4.get_frame().set_linewidth(0)
        ax4.grid()
        ax4.set_ylabel('Precipitation (in)')

        # 4) Save figure
        plt.savefig(SAVE+'f%02d.png' % (fxx))
        print "saved:", SAVE+'f%02d.png' % fxx
