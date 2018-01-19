# Brian Blaylock
# July 5, 2017                Back to work after a holiday, we have new carpet.

"""
For a MesoWest Station, create a hovmoller-style diagram to show how the HRRR
forecasted variables change between each successive forecast.

1) Hovmoller Point
2) Hovmoller Max in area
"""
print "\n--------------------------------------------------------"
print "  Working on the HRRR hovmollers GOLF (HRRR_hovmoller.py)"
print "--------------------------------------------------------\n"

import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import datetime, timedelta
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import point_hrrr_time_series_multi, get_hrrr_hovmoller
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from matplotlib.dates import DateFormatter, HourLocator

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
mpl.rcParams['figure.subplot.hspace'] = 0.01
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['legend.framealpha'] = .75
mpl.rcParams['legend.loc'] = 'best'
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.dpi'] = 100
mpl.rcParams['savefig.transparent'] = False

#==============================================================================
# Date range
UTC_now = datetime.utcnow()
sDATE = datetime(UTC_now.year, UTC_now.month, UTC_now.day, UTC_now.hour)-timedelta(hours=6)
eDATE = datetime(UTC_now.year, UTC_now.month, UTC_now.day, UTC_now.hour)+timedelta(hours=18)

# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/'

# Create specifications (spex) for each variable we want to plot
spex = {'Wind Speed':{'HRRR var':'WIND:10 m',
                      'MW var':'wind_speed',
                      'units': r'ms$\mathregular{^{-1}}$',
                      'cmap':'magma_r',
                      'save':'WIND',
                      'contour':range(2, 50, 2)},
        'Simulated Reflectivity':{'HRRR var':'REFC:entire atmosphere',
                                  'MW var':'reflectivity',
                                  'units': 'dBZ',
                                  'cmap':'gist_ncar',
                                  'save':'REF',
                                  'contour':range(20, 100, 20)},
        #'Solar Radiation':{'HRRR var':'DSWRF:surface',
        #                   'MW var':'solar_radiation',
        #                   'units': r'W m$\mathregular{^{-2}}$',
        #                   'cmap':'magma',
        #                   'save':'SOL',
        #                   'contour':range(300, 1000, 100)},
       }

# For Hovmoller statistics, define the half box.
# The demisions of the box will be (halfbox*2)*3km**2. 
# ex. if halfbox=3, then the variable statistics will be calculeted for a 18km**2 box
# centered at the station latitude/longitude.
half_box = 9

#==============================================================================
daylight = time.daylight # If daylight is on (1) then subtract from timezone.

# 1) Locations (dictionary)
locations = {'Oaks': {'latitude':40.084,
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
             'C8635':{'latitude':41.11112,
                      'longitude':-111.96229,
                      'name':'Hill Air Force Base (CW8635)',
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
                      'is MesoWest': True},
             'KIDA':{'latitude':43.52083,
                     'longitude':-112.06611,
                     'name':'Idaho Falls',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'ALT':{'latitude':40.571,
                   'longitude':-111.631,
                   'name':'Alta Top',
                   'timezone': 7-daylight,
                   'is MesoWest': True},
            'SND':{'latitude':40.368386 ,
                   'longitude':-111.593964,
                   'name':'Sundance Summit',
                   'timezone': 7-daylight,
                   'is MesoWest': True} 
            }

for s in spex:
    S = spex[s]
    #
    # Retreive a "Hovmoller" array, all forecasts for a period of time, for
    # each station in the locaiton dicionary.
    hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                   variable=S['HRRR var'],
                                   area_stats=half_box)
    #
    first_mw_attempt = S['MW var']
    for stn in locations.keys():
        print "\nWorking on %s %s" % (stn, s)
        SAVE = SAVE_dir + '%s/' % stn.replace(' ','_')
        if not os.path.exists(SAVE):
            # make the SAVE directory if it doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer_fire.php'
            os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
        #
        # Apply offset to data if necessary
        if s == 'Air Temperature' or s == 'Dew Point Temperature':
            hovmoller[stn]['max'] = hovmoller[stn]['max']-273.15
            hovmoller[stn]['box center'] = hovmoller[stn]['box center']-273.15
        #
        hovCenter = hovmoller[stn]['box center']
        hovCenter = np.ma.array(hovCenter)
        hovCenter[np.isnan(hovCenter)] = np.ma.masked
        #
        hovBoxMax = hovmoller[stn]['max']
        hovBoxMax = np.ma.array(hovBoxMax)
        hovBoxMax[np.isnan(hovBoxMax)] = np.ma.masked
        #
        #
        if s == 'Simulated Reflectivity':
            hmin = 0
            hmax = 80
        else:
            hmin = np.nanmin(hovCenter)
            hmax = np.nanmax(hovCenter)
        #
        # Plot the Hovmoller diagram
        plt.clf()
        plt.cla()
        fig = plt.figure(1)
        ax1 = plt.subplot(111)
        #
        plt.suptitle('%s %s\n%s - %s' % \
                    (stn, s, sDATE.strftime('%Y-%m-%d %H:%M'),\
                        eDATE.strftime('%Y-%m-%d %H:%M')))
        #
        # HRRR Hovmoller
        hv = ax1.pcolormesh(hovmoller['valid_1d+'], hovmoller['fxx_1d+'], hovCenter,
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        ax1.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        ax1.set_ylim(0, 19)
        ax1.set_yticks(range(0, 19, 3))
        ax1.axes.xaxis.set_ticklabels([])
        ax1.set_ylabel('HRRR Forecast Hour')
        #
        # HRRR hovmoller max (contour)
        CS = ax1.contour(hovmoller['valid_2d'], hovmoller['fxx_2d'], hovBoxMax-hovCenter,
                         colors='k',
                         levels=S['contour'])
        plt.clabel(CS, inline=1, fontsize=10, fmt='%1.f')
        #
        ax1.grid()
        #
        fig.subplots_adjust(hspace=0, right=0.8)
        cbar_ax = fig.add_axes([0.82, 0.15, 0.02, 0.7])
        cb = fig.colorbar(hv, cax=cbar_ax)
        cb.ax.set_ylabel('%s (%s)' % (s, S['units']))
        #
        ax1.xaxis.set_major_locator(HourLocator(byhour=range(0,24,3)))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        ax1.xaxis.set_major_formatter(dateFmt)
        #
        ax1.set_xlabel(r'Contour shows difference between maximum value in %s km$\mathregular{^{2}}$ box centered at %s %s and the value at the center point.' \
                    % (half_box*6, locations[stn]['latitude'], locations[stn]['longitude']), fontsize=8)
        #
        plt.savefig(SAVE+S['save']+'.png')
