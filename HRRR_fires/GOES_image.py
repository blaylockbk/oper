# Brian Blaylock
# May 21, 2018

"""
Make GOES-16 True Color and Fire Temperature image blend for a fire area
"""

import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"?
import numpy as np
from netCDF4 import Dataset
import h5py
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.max_open_warning'] = 100
mpl.rcParams['figure.figsize'] = [6, 6]
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
sys.path.append('B:\pyBKB_v2')
from BB_data.active_fires import get_fires, get_incidents
from BB_GOES16.get_ABI import get_GOES16_truecolor, get_GOES16_firetemperature, file_nearest
from BB_GOES16.get_GLM import get_GLM_files_for_ABI, accumulate_GLM

## Create Locations Dictionary
DATE = datetime.utcnow() - timedelta(hours=1)
# Get a location dictionary of the active fires
try:  
    location = get_fires(DATE=DATE)['FIRES']
    print 'Retrieved fires from Active Fire Mapping Program'
except:  
    location = get_incidents(limit_num=10)
    print 'Retrieved fires from InciWeb'

print "There are", len(location.keys()), "large fires."

## Create map objects for each fire and store in dictionary.
maps = {}
for loc in location.keys():
    l = location[loc]
    mapsize = 4.25
    m = Basemap(resolution='i', projection='cyl', area_thresh=50000,\
                llcrnrlon=l['longitude']-mapsize, llcrnrlat=l['latitude']-mapsize,\
                urcrnrlon=l['longitude']+mapsize, urcrnrlat=l['latitude']+mapsize,)
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

# List NetCDF files in today's directory:
DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/ABI-L2-MCMIPC/%s/' % DATE.strftime('%Y%m%d')
list_files = filter(lambda x: x[-3:]=='.nc', os.listdir(DIR))
list_files.sort()

# list of start dates
goes_starts = [datetime.strptime(i.split('_')[3], 's%Y%j%H%M%S%f') for i in list_files] 

def goes_start_equals_hour(file_name):
    return (datetime.strptime(file_name.split('_')[3], 's%Y%j%H%M%S%f')).hour==DATE.hour

hour_files = filter(lambda x: goes_start_equals_hour(x), list_files)

def make_plots(C_file):
    file_date = datetime.strptime(C_file.split('_')[3], 's%Y%j%H%M%S%f')
    C = Dataset(DIR+C_file, 'r')

    ## ---- TRUE COLOR --------------------------------------------------------
    ## ------------------------------------------------------------------------
    TC = get_GOES16_truecolor(DIR+C_file, only_RGB=False, night_IR=True)
    print 'File date:', TC['DATE']

    ## ---- FIRE TEMPERATURE --------------------------------------------------
    ## ------------------------------------------------------------------------
    FT = get_GOES16_firetemperature(DIR+C_file, only_RGB=False)

    ## ---- Geostationary Lightning Mapper ------------------------------------
    ## ------------------------------------------------------------------------
    GLM = accumulate_GLM(get_GLM_files_for_ABI(C_file))

    ## ---- BLEND TRUE COLOR/FIRE TEMPERATURE ---------------------------------
    max_RGB = np.nanmax([FT['rgb_tuple'], TC['rgb_tuple']], axis=0)


    ## ---- Make Plots for All fires ------------------------------------------
    ## ------------------------------------------------------------------------
    for loc in location.keys():
        plt.cla()
        plt.clf()

        timer = datetime.now()
        print timer
        # Plot RGB Blend
        newmap = maps[loc].pcolormesh(lons, lats, TC['TrueColor'][:,:,1],
                                      color=max_RGB,
                                      zorder=1,
                                      latlon=True)
        newmap.set_array(None) # without this line, the linewidth is set to zero, but the RGB colorTuple is ignored. I don't know why.
        print datetime.now() - timer, 'ABI Blend'

        # Plot GLM Flashes
        maps[loc].scatter(GLM['longitude'], GLM['latitude'],
                          marker='+',
                          color='yellow',
                          latlon=True)
        print datetime.now() - timer, 'GLM'

        # Plot other map elements
        maps[loc].drawstates(zorder=5)
        maps[loc].drawcountries(zorder=5)
        maps[loc].drawcoastlines(zorder=5)
        maps[loc].drawcounties(zorder=5)
        maps[loc].scatter(location[loc]['longitude'], location[loc]['latitude'],
                        edgecolor='powderblue',
                        facecolor='none',
                        marker='o',
                        s=200,
                        zorder=10)
        print datetime.now() - timer, 'map elements'

        plt.title('True Color and Fire Temperature Blend')        
        plt.title('%s Fire\nGOES-16 True Color and Fire Temperature Blend' % (loc))
        plt.xlabel(TC['DATE'].strftime('%B %d, %Y %H:%M UTC'))
        print datetime.now() - timer, 'labels'

        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
        plt.savefig(SAVE+'G%02d' % file_date.minute)
        print datetime.now() - timer, 'saved'
        print "Saved: %s" % SAVE+'G%02d' % file_date.minute
        

    C.close()


import multiprocessing #:)

# Multiprocessing :)
num_proc = 12                          # only 12 files to analyse
p = multiprocessing.Pool(num_proc)
p.map(make_plots, hour_files)
p.close()
