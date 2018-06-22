# Brian Blaylock
# June 19, 2018                    Going to Wallabys for dinner with my wife :)

"""
Make plots showing proximity of lightning flashes from GLM to currect fires
"""

import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"?
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
import numpy as np
from pyproj import Geod

## Reset the defaults (see more here: http://matplotlib.org/users/customizing.html)
mpl.rcParams['figure.max_open_warning'] = 100
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
from BB_GOES16.get_GLM import get_GLM_files_for_range, accumulate_GLM
from BB_rose.distancerose import WindroseAxes
from BB_downloads.HRRR_S3 import get_hrrr_variable, hrrr_subset
from BB_data.active_fires import get_fires, get_incidents


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

#location = {location.keys()[0]:location[location.keys()[0]]}

## Create map objects for each fire and store in dictionary.
print 'creating maps, and adding to locations dictionary'
for loc in location.keys():
    l = location[loc]
    mapsize = 5.25
    m = Basemap(resolution='i', projection='cyl', area_thresh=50000,\
                llcrnrlon=l['longitude']-mapsize, llcrnrlat=l['latitude']-mapsize,\
                urcrnrlon=l['longitude']+mapsize, urcrnrlat=l['latitude']+mapsize,)
    location[loc]['map'] = m

# Create directories that don't exist
for S in location.keys():
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), S.replace(' ', '_'))
    if not os.path.exists(SAVE):
        # make the SAVE directory if fire doesn't already exist
        os.makedirs(SAVE)
        print "created dir for", S 

# Get Data
eDATE = DATE
prev30 = eDATE - timedelta(minutes=30)
prev60 = eDATE - timedelta(minutes=60)
prev90 = eDATE - timedelta(minutes=90)

print 'getting GLM'
GLM_prev_60_90 = accumulate_GLM(get_GLM_files_for_range(prev90, prev60)) # 60-90 minutes ago
GLM_prev_30_60 = accumulate_GLM(get_GLM_files_for_range(prev60, prev30)) # 30-60 minutes ago
GLM_prev_00_30 = accumulate_GLM(get_GLM_files_for_range(prev30, eDATE)) # 0-30 minutes ago

print 'getting HRRR'
H = get_hrrr_variable(eDATE, 'UVGRD:500 mb', verbose=False)

# Set radius in miles
miles = 300
meters = 1609.344 * miles

# Set the earth elipse for pyproj.Geod
g = Geod(ellps='clrk66')



###############################################################################
for loc in location.keys():
    l = location[loc]
    # Perform distance calculation between fire and flashes
    for data, name in [(GLM_prev_00_30,'prev 00-30'), (GLM_prev_30_60, 'prev 30-60'), (GLM_prev_60_90, 'prev 60-90')]:
        FIRE_lon = l['longitude']*np.ones_like(data['longitude'])
        FIRE_lat = l['latitude']*np.ones_like(data['latitude'])
        azimuth, backward, distance = g.inv(FIRE_lon, FIRE_lat, data['longitude'], data['latitude'])
        azimuth[azimuth<0] += 360
        miles_away = distance/1609.344
        if len(azimuth[miles_away<miles]) > 0:
            location[loc][name] = {'degrees': azimuth[miles_away<miles],
                                   'distance': miles_away[miles_away<miles]}
        else:
            location[loc][name] = {'degrees': [None],
                                   'distance': [None]}
###############################################################################


def plot_radius(r, cenlat, cenlon):
    """
    r      - radius in meters
    cenlat - center latitude
    cenlon - center longitude
    """
    endlon = []
    endlat = []
    for i in range(360):
        fwdlon, fwdlat, backaz = g.fwd(cenlon, cenlat, i, r)
        endlon.append(fwdlon)
        endlat.append(fwdlat)
    m.plot(endlon, endlat,
           color='crimson',
           linewidth=3,
           latlon=True,
           zorder=1)

def plot_winds(H, thin=30):
    m.barbs(H['lon'][::thin,::thin], H['lat'][::thin,::thin],
            H['UGRD'][::thin,::thin], H['VGRD'][::thin,::thin],
            length=5,
            color='green',
            latlon=True,
            barb_increments={'half':2.5, 'full':5,'flag':25},
            zorder=5)
    plt.xlabel(r'HRRR 500 hPa Winds: Half, Full, Flag = 2.5, 5, 25 ms$\mathregular{^{-1}}$, respectively')


# Loop over all locations
for i, loc in enumerate(location):
    plt.clf()
    plt.cla()
    plt.figure()
    print loc
    l = location[loc] # the location dictionary contents for the fire
    #
    plot_radius(meters, l['latitude'], l['longitude'])
    plot_winds(H)
    #
    l['map'].scatter(GLM_prev_60_90['longitude'], GLM_prev_60_90['latitude'],
                     s=40, edgecolor='k', linewidth=.5,
                     color='w',
                     latlon=True,
                     label='60-90 minutes ago',
                     zorder=10)
    l['map'].scatter(GLM_prev_30_60['longitude'], GLM_prev_30_60['latitude'],
                     s=30, edgecolor='k', linewidth=.5,
                     color='grey',
                     latlon=True,
                     label='30-60 minutes ago',
                     zorder=10)
    l['map'].scatter(GLM_prev_00_30['longitude'], GLM_prev_00_30['latitude'],
                     s=20, edgecolor='k', linewidth=.5,
                     color='k',
                     latlon=True,
                     label='00-30 minutes ago',
                     zorder=10)
    #
    l['map'].scatter(l['longitude'], l['latitude'],
                     s=50,
                     marker='+',
                     zorder=10)
    #
    l['map'].drawstates()
    l['map'].drawcountries()
    l['map'].arcgisimage(service='World_Shaded_Relief', xpixels=500, dpi=100)
    #
    plt.title(loc, fontweight="semibold", loc='left')
    plt.title(eDATE.strftime('Valid: %Y-%b-%d %H:%M UTC'), loc='right')
    plt.ylabel('Radius = %s Miles' % miles)
    #
    leg = plt.legend(scatterpoints=1, framealpha=1, loc=2, fontsize=7)
    leg.get_frame().set_linewidth(0)
    #
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
    plt.savefig(SAVE+'GLM_map')
    print "Saved: %s" % SAVE+'GLM_map'
    

for i, loc in enumerate(location):
    plt.clf()
    plt.cla()
    plt.figure(figsize=[10,6])
    l = location[loc] # the location dictionary contents for the fire
    #
    plt.hist([l['prev 00-30']['distance'], l['prev 30-60']['distance'], l['prev 60-90']['distance']],
            stacked=True,
            color=['k', 'grey', 'w'],
            bins=range(0,miles+1,20))
    plt.xlim(0, miles)
    plt.xticks(range(0,miles+1,20))
    plt.xlabel('miles from %s fire' % loc)
    plt.ylabel('GLM flashes')
    plt.title(loc+' '+eDATE.strftime('%Y-%b-%d %H:%M UTC\n'), loc='left', fontweight='semibold')
    plt.title('white : 60-90 mins ago\ngrey : 30-60 mins ago\nblack : 00-30 mins ago', loc='right', fontsize=8)
    #
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
    plt.savefig(SAVE+'GLM_histogram')
    print "Saved: %s" % SAVE+'GLM_histogram'
    


for i, loc in enumerate(location):
    plt.clf()
    plt.cla()
    plt.figure(figsize=[10,6])
    l = location[loc] # the location dictionary contents for the fire
    #
    plt.scatter(l['prev 60-90']['degrees'], l['prev 60-90']['distance'],
                color='white',
                s=40, edgecolor='k', linewidth=.5,
                label='60-90 mins ago',
                zorder=10)
    plt.scatter(l['prev 30-60']['degrees'], l['prev 30-60']['distance'],
                color='grey',
                s=30, edgecolor='k', linewidth=.5,
                label='30-60 mins ago',
                zorder=10)
    plt.scatter(l['prev 00-30']['degrees'], l['prev 00-30']['distance'],
                color='k',
                s=20, edgecolor='k', linewidth=.5,
                label='00-30 mins ago',
                zorder=10)
    plt.xlabel('Direction (degrees from north)')
    plt.ylim([0,miles])
    plt.xlim([0,360])
    plt.xticks(range(0,361,45), ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    plt.grid()
    plt.title('GLM Flash Propogation', loc='left', fontweight='semibold')
    plt.title(eDATE.strftime('Valid: %Y-%b-%d %H:%M UTC'), loc='right')
    #
    plt.ylabel('Miles from Fire')
    leg = plt.legend(scatterpoints=1, framealpha=1, loc='best', fontsize=7)
    leg.get_frame().set_linewidth(1)
    #
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
    plt.savefig(SAVE+'GLM_proximity')
    print "Saved: %s" % SAVE+'GLM_proximity'
    
##--- Lightning Roses ---------------------------------------------------------
#A quick way to create new windrose axes...
def new_axes():
    fig = plt.figure(figsize=(6,8), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)
    return ax

for i, loc in enumerate(location):
    plt.clf()
    plt.cla()
    plt.figure(figsize=[8,5])
    l = location[loc] # the location dictionary contents for the fire
    #
    # Maximum count in each directional bin for A, B, and C
    AA = [j if j < 360-22.5 else j-360 for j in l['prev 00-30']['degrees']]
    BB = [j if j < 360-22.5 else j-360 for j in l['prev 30-60']['degrees']]
    CC = [j if j < 360-22.5 else j-360 for j in l['prev 60-90']['degrees']]
    max_r = np.max([np.max(np.histogram(i, bins=8, range=(-22.5,360-22.5))[0]) for i in [AA, BB, CC]])
    max_r = np.floor(max_r/5)*5+5
    for i, I, MM in [[l['prev 00-30']['distance'], l['prev 00-30']['degrees'], '00-30'],
                     [l['prev 30-60']['distance'], l['prev 30-60']['degrees'], '30-60'],
                     [l['prev 60-90']['distance'], l['prev 60-90']['degrees'], '60-90']]:
        ws = i
        wd = I
        #
        ax = new_axes()
        if i[0] != None:
            #ax.contourf(wd, ws, nsector=16, bins=np.arange(0, miles, 20), cmap=cm.viridis)
            ax.bar(wd, ws, nsector = 8, normed=False,
                bins = np.arange(0,miles+1,20),
                opening=.95, edgecolor='w',
                cmap=cm.inferno_r)
            #
            leg = plt.legend(loc='bottom left', bbox_to_anchor=(1.8, 1.0),prop={'size':15})
            leg.draw_frame(False)
            #
            #
            #table = ax._info['table']
            #wd_freq = np.sum(table, axis=0)
            #ax.set_rmax(np.floor(max(wd_freq)/5)*5+5) #set rmax to upper number divisible by 5
        ax.set_rmax(max_r)
        plt.grid(True)
        plt.yticks(np.arange(20,max_r,20))
        ax.set_yticklabels(np.arange(20,max_r,20), fontsize = 15)
        #
        plt.title('Number of GLM Flashes within 150 miles in each direction of fire\nDistance from fire colored to scale\nlast %s minutes\n' % MM)
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), loc.replace(' ', '_'))
        plt.savefig(SAVE+'GLM_rose%s' % MM[-2:])
        print "Saved: %s" % SAVE+'GLM_rose%s' % MM[-2:]
        