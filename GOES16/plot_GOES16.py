# Brian Blaylock
# September 22, 2017         I'm marrying the prettiest girl next month :)

"""
Plot a True Color GOES-16 image and save for viewing on-line
"""

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os
from datetime import datetime, timedelta

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2/')
from BB_basemap.draw_maps import draw_CONUS_HRRR_map, draw_Utah_map
from BB_GOES16.get_GOES16 import get_GOES16_truecolor
from BB_downloads.HRRR_S3 import get_hrrr_variable

import matplotlib as mpl
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

# Draw map objects
mHRRR = draw_CONUS_HRRR_map()
mUtah = draw_Utah_map()

# Where to save the files
SAVEDIR = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/GOES16/'

def map_HRRR_domain(G, H):
    # Plot on HRRR domain Map
    # G is the goes16 data dictionary
    plt.clf()
    plt.cla()
    
    # Plot GOES-16 image
    newmap = mHRRR.pcolormesh(G['LONS'], G['LATS'], G['TrueColor'][:,:,1],
                              color=G['rgb'],
                              linewidth=0,
                              latlon=True)
    newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
    
    # Plot HRRR data
    cs = mHRRR.contour(H['lon'], H['lat'], H['value'], latlon=True, colors='slategrey', levels=range(4980, 6100, 60))
    plt.clabel(cs, fmt = '%1.0f')

    mHRRR.drawcoastlines()
    mHRRR.drawstates()
    mHRRR.drawcounties()
    plt.title('GOES-16 True Color: %s\nHRRR 500 mb Height: %s' \
              % (G['DATE'].strftime('%Y %b %d %H:%M UTC'), H['valid'].strftime('%Y %b %d %H:%M UTC')))
    plt.savefig(SAVEDIR+'CONUS/%s.png' % G['DATE'].strftime('%Y%m%d_%H%M'))

def map_UTAH_domain(G):
    # Plot on Utah Map
    plt.clf()
    plt.cla()
    newmap = mUtah.pcolormesh(G['LONS'], G['LATS'], G['TrueColor'][:,:,1],
                            color=G['rgb'],
                            linewidth=0,
                            latlon=True)
    newmap.set_array(None) # must have this line if using pcolormesh and linewidth=0
    mUtah.drawstates()
    mUtah.drawcoastlines()
    plt.title('GOES-16 True Color: %s' % G['DATE'].strftime('%Y %b %d %H:%M UTC'))
    plt.savefig(SAVEDIR+'UTAH/%s.png' % G['DATE'].strftime('%Y%m%d_%H%M'))

def make_plots(FILE):
    # Get HRRR Temperature
    scanStart =  datetime.strptime(flist[0].split('/')[-1].split('_')[3], 's%Y%j%H%M%S%f')
    DATE_hour = datetime(scanStart.year, scanStart.month, scanStart.day, scanStart.hour)
    H = get_hrrr_variable(DATE_hour, variable="HGT:500 mb")

    # Get GOES data dictionary
    G = get_GOES16_truecolor(FILE)

    # Make and save images
    map_HRRR_domain(G, H)
    map_UTAH_domain(G)

if __name__ == '__main__':

    # Get file name:
    DIR = '/uufs/chpc.utah.edu/common/home/horel-group/archive/20170922/BB_test/goes16/'
    FILES = os.listdir(DIR)
    
    flist = [DIR+f for f in FILES]

    import multiprocessing #:)
    p = multiprocessing.Pool(6)
    p.map(make_plots, flist)
