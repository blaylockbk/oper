# Brian Blaylock
# June 13, 2017                      Golden State beats the Cavs. James is sad.

"""
For a MesoWest Station, create a hovmoller-style diagram to show how the HRRR
forecasted variables change between each successive forecast.

1) Hovmoller Point
2) Hovmoller Max in area
"""
print "\n--------------------------------------------------------"
print "  Working on the HRRR hovmollers fires (HRRR_hovmoller_fires.py)"
print "--------------------------------------------------------\n"

import matplotlib as mpl
mpl.use('Agg')#required for the CRON job. Says "do not open plot in a window"??
import numpy as np
from datetime import date, datetime, timedelta
import time
import urllib2
import matplotlib.pyplot as plt
import os

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_STNinfo import get_station_info
from BB_data.active_fires import get_fires, get_incidents, download_fire_perimeter_shapefile
from BB_cmap.NWS_standard_cmap import *

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
#SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'

# Create specifications (spex) for each variable we want to plot
spex = {'10 m MAX Wind Speed':{'HRRR var':'WIND:10 m',
                      'MW var':'wind_speed',
                      'units': r'ms$\mathregular{^{-1}}$',
                      'cmap':cm_wind(),
                      'save':'WIND',
                      'contour':range(5, 50, 5),
                      'vmax':60,
                      'vmin':0},
        'Simulated Reflectivity':{'HRRR var':'REFC:entire atmosphere',
                                  'MW var':'reflectivity',
                                  'units': 'dBZ',
                                  'cmap':'gist_ncar',
                                  'save':'REF',
                                  'contour':range(20, 100, 20),
                                  'vmax':80,
                                  'vmin':0},
        '2 m Temperature':{'HRRR var':'TMP:2 m',
                           'MW var':'air_temp',
                           'units': 'C',
                           'cmap':cm_temp(),
                           'save':'TMP',
                           'contour':range(-20, 50, 5),
                           'vmax':50,
                           'vmin':-50},
        '2 m Dew Point':{'HRRR var':'DPT:2 m',
                           'MW var':'dew_point_temperature',
                           'units': 'C',
                           'cmap':cm_dpt(),
                           'save':'DPT',
                           'contour':range(-20, 50, 5),
                           'vmax':-18,
                           'vmin':27},
        '2 m Relative Humidity':{'HRRR var':'RH:2 m',
                                 'MW var':'relative_humidity',
                                 'units': '%',
                                 'cmap':cm_rh(),
                                 'save':'RH',
                                 'contour':range(100,121,10),
                                 'vmax':5,
                                 'vmin':90},
        #'1 h Accumulated Precipitation':{'HRRR var':'APCP:surface',
        #                                 'MW var':'accumulated_precip',
        #                                 'units': 'mm',
        #                                 'cmap':cm_precip(),
        #                                 'save':'PCP',
        #                                 'contour':range(50,101,5),
        #                                 'vmax':762,
        #                                 'vmin':0},
        #'Solar Radiation':{'HRRR var':'DSWRF:surface',
        #                   'MW var':'solar_radiation',
        #                   'units': r'W m$\mathregular{^{-2}}$',
        #                   'cmap':'magma',
        #                   'save':'SOL',
        #                   'contour':range(300, 1000, 100)},
       }

# For Hovmoller statistics, define the half box.
# The dimensions of the box will be (halfbox*2)*3km**2. 
# ex. if halfbox=3, then the variable statistics will be calculeted for a 18km**2 box
# centered at the station latitude/longitude.
half_box = 9

# Get a location dictionary of the active fires
try:  
    location = get_fires()['FIRES']
    print 'Retrieved fires from Active Fire Mapping Program'
except:  
    location = get_incidents(limit_num=10)
    print 'Retrieved fires from InciWeb'

for s in spex:
    print s
    S = spex[s]
    #
    # Retrieve a "Hovmoller" array, all forecasts for a period of time, for
    # each station in the location dictionary.
    hovmoller = LocDic_hrrr_hovmoller(sDATE, eDATE, location,
                                      variable=S['HRRR var'],
                                      area_stats=half_box)
    #
    first_mw_attempt = S['MW var']
    for stn in location.keys():
        print "\nWorking on %s %s" % (stn, s)
        #SAVE = SAVE_dir + '%s/' % stn.replace(' ','_')
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % ((UTC_now-timedelta(hours=1)).strftime('%Y-%m-%d/%H00'), stn.replace(' ', '_'))
        if not os.path.exists(SAVE):
            # make the SAVE directory if it doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            #photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer_fire.php'
            #os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
        #
        # Apply offset to data if necessary
        if s == '2 m Temperature' or s == '2 m Dew Point':
            hovmoller[stn]['max'] = hovmoller[stn]['max']-273.15
            hovmoller[stn]['box center value'] = hovmoller[stn]['box center value']-273.15
        #
        hovCenter = hovmoller[stn]['box center value']
        hovCenter = np.ma.array(hovCenter)
        hovCenter[np.isnan(hovCenter)] = np.ma.masked
        #
        hovBoxMax = hovmoller[stn]['max']
        hovBoxMax = np.ma.array(hovBoxMax)
        hovBoxMax[np.isnan(hovBoxMax)] = np.ma.masked
        #
        #
        try:
            hmin = S['vmin']
            hmax = S['vmax']
        except:
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
                    % (half_box*6, location[stn]['latitude'], location[stn]['longitude']), fontsize=8)
        #
        plt.savefig(SAVE+S['save']+'.png')
