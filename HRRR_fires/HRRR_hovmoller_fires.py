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
SAVE_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'

# Create specifications (spex) for each variable we want to plot
spex = {'10 m MAX Wind Speed':{'HRRR var':'WIND:10 m',
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
        '2 m Temperature':{'HRRR var':'TMP:2 m',
                           'MW var':'air_temp',
                           'units': 'C',
                           'cmap':'Spectral_r',
                           'save':'TMP',
                           'contour':range(-20, 50, 5)}, 
        '2 m Dew Point':{'HRRR var':'DPT:2 m',
                           'MW var':'dew_point_temperature',
                           'units': 'C',
                           'cmap':'BrBG',
                           'save':'DPT',
                           'contour':range(-20, 50, 5)},                                  
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

get_today = datetime.strftime(date.today(), "%Y-%m-%d")
daylight = time.daylight # If daylight is on (1) then subtract from timezone.

#==============================================================================
# 1) Read in large fires file:
#fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab
url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % get_today
text = urllib2.urlopen(url)
fires = np.genfromtxt(text, names=True, dtype=None,delimiter='\t')
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
locations = {}
for F in range(0, len(fires)):
    FIRE = fires[F]
    # 1) Get Latitude and Longitude for the indexed large fire [fire]
    # No HRRR data for Alaska or Hawaii, so don't do it.
    # Also, don't bother running fires less than 1000 acres
    if FIRE[7] < 1000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
        continue
    locations[FIRE[0]] = {'latitude': FIRE[10],
                          'longitude': FIRE[11],
                          'name': FIRE[0],
                          'start':FIRE[4],
                          'state': FIRE[6],
                          'area': FIRE[7],
                          'start date': FIRE[4],
                          'is MesoWest': False
                         }

for s in spex:
    S = spex[s]
    #
    # Retrieve a "Hovmoller" array, all forecasts for a period of time, for
    # each station in the location dictionary.
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
        if s == '2 m Temperature' or s == '2 m Dew Point':
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
