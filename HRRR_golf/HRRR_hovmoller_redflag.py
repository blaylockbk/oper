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
import location_dic

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
        'Relative Humidity':{'HRRR var':'RH:2 m',
                                  'MW var':'relative_humidity',
                                  'units': '%',
                                  'cmap':'BrBG',
                                  'save':'RH',
                                  'contour':range(0, 100, 10)},
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

#==============================================================================
# 1) Get Locations Dictionary
locations = location_dic.get_all()

#
# Retrieve a "Hovmoller" array, all forecasts for a period of time, for
# each station in the location dictionary.
wind_hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                variable='WIND:10 m',
                                area_stats=half_box)
rh_hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                variable='RH:2 m',
                                area_stats=half_box)
#
for stn in locations.keys():
    print "\nWorking on %s" % (stn)
    SAVE = SAVE_dir + '%s/' % stn.replace(' ','_')
    if not os.path.exists(SAVE):
        # make the SAVE directory if it doesn't already exist
        os.makedirs(SAVE)
        print "created:", SAVE
        # then link the photo viewer
        photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer_fire.php'
        os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
    #
    wind_hovCenter = wind_hovmoller[stn]['box center']
    wind_hovCenter = np.ma.array(wind_hovCenter)
    wind_hovCenter[np.isnan(wind_hovCenter)] = np.ma.masked
    #
    rh_hovCenter = rh_hovmoller[stn]['box center']
    rh_hovCenter = np.ma.array(rh_hovCenter)
    rh_hovCenter[np.isnan(rh_hovCenter)] = np.ma.masked
    #
    wind_hovBoxMax = wind_hovmoller[stn]['max']
    wind_hovBoxMax = np.ma.array(wind_hovBoxMax)
    wind_hovBoxMax[np.isnan(wind_hovBoxMax)] = np.ma.masked
    #
    rh_hovBoxMax = rh_hovmoller[stn]['max']
    rh_hovBoxMax = np.ma.array(rh_hovBoxMax)
    rh_hovBoxMax[np.isnan(rh_hovBoxMax)] = np.ma.masked
    #
    #
    ### RED FLAG HOVMOLLER
    RF_hovCenter = np.logical_and(wind_hovCenter>6.7, rh_hovCenter<20)
    RF_hovBoxMax = np.logical_and(wind_hovBoxMax>6.7, rh_hovBoxMax<20)
    #
    #
    #
    # Plot the Hovmoller diagram
    plt.clf()
    plt.cla()
    fig = plt.figure(1)
    ax1 = plt.subplot(111)
    #
    plt.suptitle('%s Red Flag Conditions (wind > 6.7 m/s and RH < 20%%)\n%s - %s' % \
                (stn, sDATE.strftime('%Y-%m-%d %H:%M'),\
                    eDATE.strftime('%Y-%m-%d %H:%M')))
    #
    # HRRR Hovmoller
    hv = ax1.pcolormesh(wind_hovmoller['valid_1d+'], wind_hovmoller['fxx_1d+'], RF_hovCenter,
                        cmap='Reds', vmax=1, vmin=0)
    ax1.set_xlim(wind_hovmoller['valid_1d+'][0], wind_hovmoller['valid_1d+'][-1])
    ax1.set_ylim(0, 19)
    ax1.set_yticks(range(0, 19, 3))
    ax1.axes.xaxis.set_ticklabels([])
    ax1.set_ylabel('HRRR Forecast Hour')
    #
    # HRRR hovmoller max (contour)
    CS = ax1.contour(wind_hovmoller['valid_2d'], wind_hovmoller['fxx_2d'], RF_hovBoxMax-RF_hovCenter,
                        colors='k', levels=[1])
    plt.clabel(CS, inline=1, fontsize=10, fmt='%1.f')
    #
    ax1.grid()
    #
    fig.subplots_adjust(hspace=0, right=0.8)
    cbar_ax = fig.add_axes([0.82, 0.15, 0.02, 0.7])
    cb = fig.colorbar(hv, cax=cbar_ax)
    cb.ax.set_ylabel('Red Flag')
    #
    ax1.xaxis.set_major_locator(HourLocator(byhour=range(0,24,3)))
    dateFmt = DateFormatter('%b %d\n%H:%M')
    ax1.xaxis.set_major_formatter(dateFmt)
    #
    ax1.set_xlabel(r'Contour shows difference between maximum value in %s km$\mathregular{^{2}}$ box centered at %s %s and the value at the center point.' \
                % (half_box*6, locations[stn]['latitude'], locations[stn]['longitude']), fontsize=8)
    #
    plt.savefig(SAVE+'RedFlag.png')
