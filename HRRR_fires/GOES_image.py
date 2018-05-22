# Brian Blaylock
# May 21, 2018

"""
Make GOES-16 True Color and Fire Temperature image for a fire area
"""

import matplotlib as mpl
#mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"?
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
from BB_data.active_fires import download_fire_perimeter_shapefile
from BB_GOES16.get_GOES16 import get_GOES16_truecolor, get_GOES16_firetemperature

## Create Locations Dictionary
get_today = datetime.strftime(date.today(), "%Y-%m-%d")
url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % get_today
text = urllib2.urlopen(url)

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

location = {}

for i, f in enumerate(text):
    line = f.split('\t')
    if i==0 or int(line[7]) < 1000 or int(line[7]) > 3000000 or line[6] == 'Alaska' or line[6] == 'Hawaii':
        continue
    location[line[0]] = {'latitude': float(line[10]),
                         'longitude': float(line[11]),
                         'name': line[0],
                         'state': line[6],
                         'area': int(line[7]),
                         'start date': line[4],
                         'is MesoWest': False
                         }
print "There are", len(location.keys()), "large fires."

## Create map objects for each fire and store in dictionary.
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl', area_thresh=50000,\
                llcrnrlon=l['longitude']-2.75, llcrnrlat=l['latitude']-2.75,\
                urcrnrlon=l['longitude']+2.75, urcrnrlat=l['latitude']+2.75,)
    maps[loc] = m


## -------------------------------------------------------------------------
# Get premade lon/lat grids
h = h5py.File('/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/goes16_conus_latlon_east.h5', 'r')
lons = h['longitude'][:]
lats = h['latitude'][:]

# Get most recent GOES-16 image in the archive
DATE = datetime.utcnow() - timedelta(hours=1)
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)
print 'Now date:', DATE

# List files in todays directory:
DIR = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/ABI-L2-MCMIPC/%s/' % DATE.strftime('%Y%m%d')
list_files = filter(lambda x: x[-3:]=='.nc', os.listdir(DIR))
list_files.sort()
C_file = list_files[-13]
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
                      s=100,
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
                      s=100,
                      zorder=10)

    plt.title('Fire Temperature')

    plt.suptitle('%s Fire\nGOES-16 %s' % (loc, TC['DATE'].strftime('%B %d, %Y %H:%M UTC')))
    
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
    plt.savefig(SAVE+'GOES')
    print "Saved: %s" % SAVE

C.close()