# Brian Blaylock
# June 13, 2017                      Golden State beats the Cavs. James is sad.

"""
For a MesoWest Station, create a hovmoller-style diagram to show how the HRRR
forecasted variables change between each successive forecast.

1) Hovmoller Point
2) Hovmoller Max in area
"""
print "\n--------------------------------------------------------"
print "  Working on the HRRR hovmollers (HRRR_hovmoller.py)"
print "--------------------------------------------------------\n"

import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')		#required for the CRON job or cgi script. Says "do not open plot in a window"??
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
mpl.rcParams['figure.figsize'] = [16, 8]
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
today = datetime.now()
sDATE = datetime(today.year, today.month, today.day)-timedelta(days=2)
eDATE = datetime(today.year, today.month, today.day)


# Directory to save figures (subdirectory will be created for each stnID)
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_hovmoller/'

# Create specifications (spex) for each variable we want to plot
spex = {'Wind Speed':{'HRRR var':'WIND:10 m',
                      'MW var':'wind_speed',
                      'units': r'ms$\mathregular{^{-1}}$',
                      'cmap':'magma_r'},
        'Air Temperature':{'HRRR var':'TMP:2 m',
                           'MW var':'air_temp',
                           'units': 'C',
                           'cmap':'Spectral_r'},
        'Dew Point Temperature':{'HRRR var':'DPT:2 m',
                                 'MW var':'dew_point_temperature',
                                 'units': 'C',
                                 'cmap': 'BrBG'},
        '1hr Accumulated Precipitation':{'HRRR var':'APCP:surface',
                                         'MW var':'precip_accum_five_minute',
                                         'units': 'mm',
                                         'cmap': 'BuPu'},
       }

#==============================================================================

## 1) Get Locations Dictionary
location = location_dic.get_all()

locations = {}
for l in location:
    print l
    if location[l]['is MesoWest'] == True:
        locations[l] = location[l]


for s in spex:
    print "\nWorking on", s
    S = spex[s]
    #
    # Retreive a "Hovmoller" array, all forecasts for a period of time, for
    # each station in the locaiton dicionary.
    hovmoller = get_hrrr_hovmoller(sDATE, eDATE, locations,
                                   variable=S['HRRR var'],
                                   reduce_CPUs=0)
    #
    first_mw_attempt = S['MW var']
    for stn in locations.keys():
        print "\nWorking on %s %s" % (stn, s)
        SAVE = SAVE_dir + '%s/' % stn
        if not os.path.exists(SAVE):
            # make the SAVE directory if it doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer.php'
            os.link(photo_viewer, SAVE+'photo_viewer.php')
        #
        # Get data from the MesoWest Station
        #
        S['MW var'] = first_mw_attempt
        a = get_mesowest_ts(stn, sDATE, eDATE, variables=first_mw_attempt)
        # Aak, so many different precipitatin variables. Try each one until we
        # find one that works...
        if a == 'ERROR':
            a = get_mesowest_ts(stn, sDATE, eDATE, variables='precip_accum_one_hour')
            S['MW var'] = 'precip_accum_one_hour'
            if a == 'ERROR':
                a = get_mesowest_ts(stn, sDATE, eDATE, variables='precip_accum')
                S['MW var'] = 'precip_accum'
                if a == 'ERROR':
                    a = get_mesowest_ts(stn, sDATE, eDATE, variables='precip_accum_24_hour')
                    S['MW var'] = 'precip_accum_24_hour'
                    if a == 'ERROR':
                        # the variable probably isn't available (*precipitation*), so fill with nans
                        dates_1d = hovmoller['valid_1d+'][:-1]
                        a = {'DATETIME':dates_1d,
                             'no_precip_obs':[np.nan for i in range(len(dates_1d))]}
                        S['MW var'] = 'no_precip_obs'
        #
        # Apply offset to data if necessary
        if s == 'Air Temperature' or s == 'Dew Point Temperature':
            hovmoller[stn] = hovmoller[stn]-273.15
        #
        #
        hmin = np.nanmin([np.nanmin(a[S['MW var']]), np.nanmin(hovmoller[stn])])
        hmax = np.nanmax([np.nanmax(a[S['MW var']]), np.nanmax(hovmoller[stn])])
        #
        # Plot the Hovmoller diagram
        plt.clf()
        plt.cla()
        fig = plt.figure(1)
        ax1 = plt.subplot2grid((8, 1), (0, 0), rowspan=7)
        ax2 = plt.subplot(8, 1, 8)
        #
        plt.suptitle('%s %s\n%s - %s' % \
                    (stn, s, sDATE.strftime('%Y-%m-%d %H:%M'),\
                        eDATE.strftime('%Y-%m-%d %H:%M')))
        #
        # HRRR Hovmoller (tall subplot on top)
        hv = ax1.pcolormesh(hovmoller['valid_1d+'], hovmoller['fxx_1d+'], hovmoller[stn],
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        ax1.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        ax1.set_ylim(0, 19)
        ax1.set_yticks(range(0, 19, 3))
        ax1.axes.xaxis.set_ticklabels([])
        ax1.set_ylabel('HRRR Forecast Hour')
        #
        # Observed mesh (thin subplot on bottom)
        mw = ax2.pcolormesh(a['DATETIME'], range(3), [a[S['MW var']], a[S['MW var']]],
                            cmap=S['cmap'],
                            vmax=hmax,
                            vmin=hmin)
        ax2.axes.yaxis.set_ticklabels([])
        ax2.set_yticks([])
        ax2.set_ylabel('Observed')
        ax2.set_xlim(hovmoller['valid_1d+'][0], hovmoller['valid_1d+'][-1])
        #
        ax1.grid()
        ax2.grid()
        #
        fig.subplots_adjust(hspace=0, right=0.8)
        cbar_ax = fig.add_axes([0.82, 0.15, 0.02, 0.7])
        cb = fig.colorbar(hv, cax=cbar_ax)
        cb.ax.set_ylabel('%s (%s)' % (s, S['units']))
        #
        ax1.xaxis.set_major_locator(HourLocator(byhour=[0, 6, 12, 18]))
        ax2.xaxis.set_major_locator(HourLocator(byhour=[0, 6, 12, 18]))
        dateFmt = DateFormatter('%b %d\n%H:%M')
        ax2.xaxis.set_major_formatter(dateFmt)
        #
        plt.savefig(SAVE+'%s_%s.png' % (stn, S['MW var']))
