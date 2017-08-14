# Brian Blaylock
# May 24, 2017                            I got an Azure account today

"""
Create windroses for last two days of HRRR and MesoWest data
"""

import matplotlib as mpl
#mpl.use('Agg')		#required for the CRON job or cgi script. Says "do not open plot in a window"??
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
mpl.rcParams['savefig.transparent'] = False

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')


from BB_rose.windrose import WindroseAxes
from BB_wx_calcs.wind import wind_uv_to_spd, wind_uv_to_dir, wind_spddir_to_uv
from BB_wx_calcs.units import *


def new_axes():
    fig = plt.figure(facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax

#...and adjust the legend box

def set_legend(ax):
    l = ax.legend()
    #plt.setp(l.get_texts())
    plt.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), prop={'size':10})

def plot_rose(l):
    """
    l is a dictionary with MesoWest and HRRR data at the station for a period of time
    """
    MW = l['MesoWest']
    HR = l['HRRR']
    HR['wind_speed'] = [wind_uv_to_spd(HR['u'][i], HR['v'][i]) for i in range(len(HR['u']))]
    HR['wind_direction'] = [wind_uv_to_dir(HR['u'][i], HR['v'][i]) for i in range(len(HR['u']))]


    # Make the wind rose - MesoWest
    axMW = new_axes()
    axMW.bar(MW['wind_direction'], MW['wind_speed'],
             nsector=16,
             normed=True,
             bins=range(0, 20, 2))
    # Create a legend
    set_legend(axMW)
    plt.title("MesoWest %s (%s) \n %s - %s" % (MW['STID'], MW['NAME'], MW['DATETIME'][0].strftime('%d %b %Y'), MW['DATETIME'][-1].strftime('%d %b %Y')))
    plt.grid(True)
    # Grid at 5% intervals
    plt.yticks(np.arange(5, 105, 5))
    axMW.set_yticklabels(['5%', '10%', '15%', '20%', '25%', '30%', '35%', '40%'])

    # Change the plot range
    axMW.set_rmax(np.max(np.sum(axMW._info['table'], axis=0)))

    plt.savefig(l['SAVE']+'/'+MW['STID']+'/rose_MW.png')
    print "Saved a windrose - MesoWest", MW['STID']
    plt.clf()
    plt.cla()

    # Make the wind rose - HRRR
    axHR = new_axes()
    axHR.bar(HR['wind_direction'], HR['wind_speed'],
             nsector=16,
             normed=True,
             bins=range(0, 20, 2))
    # Create a legend
    set_legend(axHR)
    plt.title("HRRR %s (%s) \n %s - %s" % (HR['STID'], HR['NAME'], HR['DATETIME'][0].strftime('%d %b %Y'), MW['DATETIME'][-1].strftime('%d %b %Y')))
    plt.grid(True)
    # Grid at 5% intervals
    plt.yticks(np.arange(5, 105, 5))
    axHR.set_yticklabels(['5%', '10%', '15%', '20%', '25%', '30%', '35%', '40%'])

    # Change the plot range
    axHR.set_rmax(np.max(np.sum(axHR._info['table'], axis=0)))

    plt.savefig(l['SAVE']+'/'+MW['STID']+'/rose_HR.png')
    print "Saved a windrose - HRRR", HR['STID'], l['SAVE']

    plt.clf()
    plt.cla()

if __name__ == '__main__':
    L = {'SAVE':'./',
         'MesoWest':{'STID':'',
                     'NAME':'test',
                     'DATETIME':[datetime(2016, 7, 4), datetime(2017, 3, 4)],
                     'wind_direction': np.arange(1, 360),
                     'wind_speed':np.arange(1, 360)/10},
         'HRRR':{'STID':'testHRRRid',
                 'NAME':'testHRRR',
                 'DATETIME':[datetime(2016, 7, 4), datetime(2017, 3, 4)],
                 'u': np.arange(1, 50),
                 'v':np.arange(1, 50)}}

    plot_rose(L)
