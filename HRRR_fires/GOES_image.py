# Brian Blaylock
# May 21, 2018

"""
Make GOES-16 True Color and Fire Temperature image for a fire area
"""

import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"?
import numpy as np
from netCDF4 import Dataset
import h5py
from pyproj import Proj  
from datetime import date, datetime, timedelta
import os
import urllib2
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.max_open_warning'] = 100
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
mpl.rcParams['figure.max_open_warning'] = 30

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')

from BB_basemap.draw_maps import draw_CONUS_cyl_map
from BB_data.active_fires import get_fires, get_incidents, download_fire_perimeter_shapefile
from BB_GOES16.get_GOES16 import get_GOES16_truecolor, get_GOES16_firetemperature

## Create Locations Dictionary
DATE = datetime.utcnow() - timedelta(hours=1)
# Get a location dictionary of the active fires
try:  
    location = get_fires(DATE=DATE, min_size=1000)['FIRES']
    print 'Retrieved fires from Active Fire Mapping Program'
except:  
    location = get_incidents(limit_num=10)
    print 'Retrieved fires from InciWeb'

print "There are", len(location.keys()), "large fires."

## Create map objects for each fire and store in dictionary.
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl', area_thresh=50000,\
                llcrnrlon=l['longitude']-2.25, llcrnrlat=l['latitude']-2.25,\
                urcrnrlon=l['longitude']+2.25, urcrnrlat=l['latitude']+2.25,)
    maps[loc] = m

# Create directories that don't exist
for S in location.keys():
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), S.replace(' ', '_'))
    if not os.path.exists(SAVE):
        # make the SAVE directory if fire doesn't already exist
        os.makedirs(SAVE)
        print "created dir for", S 

## -------------------------------------------------------------------------
# Get premade lon/lat grids
h = h5py.File('/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/goes16_conus_latlon_east.h5', 'r')
lons = h['longitude'][:]
lats = h['latitude'][:]

# List files in todays directory:
DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/ABI-L2-MCMIPC/%s/' % DATE.strftime('%Y%m%d')
list_files = filter(lambda x: x[-3:]=='.nc', os.listdir(DIR))
list_files.sort()

# list of start dates
goes_starts = [datetime.strptime(i.split('_')[3], 's%Y%j%H%M%S%f') for i in list_files] 

def goes_start_equals_hour(file_name):
    return (datetime.strptime(file_name.split('_')[3], 's%Y%j%H%M%S%f')).hour==DATE.hour

hour_files = filter(lambda x: goes_start_equals_hour(x), list_files)

for C_file in hour_files:
    file_date = datetime.strptime(C_file.split('_')[3], 's%Y%j%H%M%S%f')
    C = Dataset(DIR+C_file, 'r')

    ## ---- TRUE COLOR ------------------------------------------------------------
    ## ----------------------------------------------------------------------------
    TC = get_GOES16_truecolor(DIR+C_file, only_RGB=False, night_IR=True)
    print 'File date:', TC['DATE']

    ## ---- FIRE TEMPERATURE ------------------------------------------------------
    ## ----------------------------------------------------------------------------
    FT = get_GOES16_firetemperature(DIR+C_file, only_RGB=False)


    ## ---- Make Plots for All fires ----------------------------------------------
    ## ----------------------------------------------------------------------------
    for loc in location.keys():
        # Now we can plot the GOES data on the HRRR map domain and projection
        fig, (ax1, ax2) = plt.subplots(1, 2)
        plt.sca(ax1)

        # The values of R are ignored becuase we plot the color in colorTuple, but pcolormesh still needs its shape.
        newmap = maps[loc].pcolormesh(lons, lats, TC['TrueColor'][:,:,1], color=TC['rgb_tuple'], latlon=True)
        newmap.set_array(None) # without this line, the linewidth is set to zero, but the RGB colorTuple is ignored. I don't know why.

        maps[loc].drawstates()
        maps[loc].drawcountries()
        maps[loc].drawcoastlines()
        maps[loc].drawcounties()
        maps[loc].scatter(location[loc]['longitude'], location[loc]['latitude'],
                        edgecolor='magenta',
                        facecolor='none',
                        marker='o',
                        s=200,
                        zorder=10)

        plt.title('True Color')

        plt.sca(ax2)
        # The values of R are ignored becuase we plot the color in colorTuple, but pcolormesh still needs its shape.
        newmap = maps[loc].pcolormesh(lons, lats, FT['TrueColor'][:,:,1], color=FT['rgb_tuple'], latlon=True)
        newmap.set_array(None) # without this line, the linewidth is set to zero, but the RGB colorTuple is ignored. I don't know why.

        maps[loc].drawstates()
        maps[loc].drawcountries()
        maps[loc].drawcoastlines()
        maps[loc].drawcounties()
        maps[loc].scatter(location[loc]['longitude'], location[loc]['latitude'],
                        edgecolor='magenta',
                        facecolor='none',
                        marker='o',
                        s=200,
                        zorder=10)

        plt.title('Fire Temperature')

        plt.suptitle('%s Fire\nGOES-16 %s' % (loc, TC['DATE'].strftime('%B %d, %Y %H:%M UTC')))
        
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
        plt.savefig(SAVE+'G%02d' % file_date.minute)
        print "Saved: %s" % SAVE+'G%02d' % file_date.minute

    C.close()