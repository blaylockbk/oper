# Brian Blaylock
# May 8, 2017                                  Jazz might get swept tonight :(

"""
Plot HRRR point forecasts for large fires in the United States
An extension to the HRRR Golf scripts.
Runs every hour. Sometimes hangs if the HRRR forecasts aren't on NOMADS quick
enough.

To do list:
[X] Updated December 12, 2017 with new active fires shape.
[ ] What causes the Segmentation Fault (core dumped)??
[ ] Include Subhourly files files
[ ] If the forecast isn't in yet, there is not valid time, and the script fails
"""

import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"?
import numpy as np
from datetime import date, datetime, timedelta
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates
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
sys.path.append('/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/lib/python2.7/site-packages/')
sys.path.append('B:\pyBKB_v2')

from BB_downloads.HRRR_S3 import *
from BB_MesoWest.MesoWest_timeseries import get_mesowest_ts
from BB_MesoWest.MesoWest_radius import get_mesowest_radius
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *
from BB_basemap.draw_maps import draw_CONUS_cyl_map
from BB_data.grid_manager import pluck_point_new
from BB_data.active_fires import get_fires, get_incidents, download_fire_perimeter_shapefile
from BB_cmap.landuse_colormap import LU_MODIS21
from MetPy_BB.plots import ctables


## 1) Download most recent active fire perimeters shapefile
try:
    download_fire_perimeter_shapefile()
    print "Downloaded the most recent active fire perimeters."
except:
    print "Can not download new fire perimeters. Using old file."


## 2) Create Locations Dictionary
## 5) Get the HRRR data from NOMADS
DATE = datetime.utcnow() - timedelta(hours=1)
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)

print "Local DATE:", datetime.now()
print "  UTC DATE:", DATE

# Get a location dictionary of the active fires
try:  
    location = get_fires()['FIRES']
    print 'Retrieved fires from Active Fire Mapping Program'
except:  
    location = get_incidents(limit_num=10)
    print 'Retrieved fires from InciWeb'

print "There are", len(location.keys()), "large fires."

# Assign some known MesoWest Station ID's to a fire
for l in location:
    if l == 'BRIANHEAD':
        location[l]['is MesoWest'] = 'TT047'


## 3) Create map objects for each fire and store in dictionary.
#     This speeds up plotting by creating each map once.
maps = {}
for loc in location.keys():
    l = location[loc]
    m = Basemap(resolution='i', projection='cyl',\
                llcrnrlon=l['longitude']-.75, llcrnrlat=l['latitude']-.75,\
                urcrnrlon=l['longitude']+.75, urcrnrlat=l['latitude']+.75,)
    maps[loc] = m  



# Create directories that don't exist
for S in location.keys():
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), S.replace(' ', '_'))
    if not os.path.exists(SAVE):
        # make the SAVE directory if fire doesn't already exist
        os.makedirs(SAVE)
        print "created dir for", S 

## 4) Create a landuse map for each the fire and surrounding area
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
LU = get_hrrr_variable(datetime(2018,1,1), 'VGTYP:surface')
cm, labels = LU_MODIS21()
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), locName.replace(' ', '_'))
    if not os.path.exists(SAVE+'Landuse.png'):
        plt.figure(100)
        print "need to make", SAVE+'Landuse.png'
        maps[locName].pcolormesh(LU['lon'], LU['lat'], LU['value'],
                                cmap=cm, vmin=1, vmax=len(labels) + 1,
                                latlon=True)
        cb = plt.colorbar(orientation='vertical', pad=.01, shrink=.95)
        cb.set_ticks(np.arange(0.5, len(labels) + 1))
        cb.ax.set_yticklabels(labels)
        maps[locName].scatter(l['longitude'], l['latitude'], marker='+', c='crimson', s=100, latlon=True)
        maps[locName].drawstates()
        maps[locName].drawcounties()
        plt.title('Landuse near %s' % locName)
        plt.savefig(SAVE+'Landuse.png')  
        print "created landuse maps for", locName
        plt.close()

# Pollywogs: Pluck HRRR value at all locations for each variable.
#      These are dictionaries:
#      {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}
P_temp = LocDic_hrrr_pollywog(DATE, 'TMP:2 m', location, verbose=False); print 'got temps'
P_dwpt = LocDic_hrrr_pollywog(DATE, 'DPT:2 m', location, verbose=False); print 'got dwpt'
P_wind = LocDic_hrrr_pollywog(DATE, 'WIND:10 m', location, verbose=False); print 'got wind'
P_gust = LocDic_hrrr_pollywog(DATE, 'GUST:surface', location, verbose=False); print 'got gust'
P_UV = LocDic_hrrr_pollywog(DATE, 'UVGRD:10 m', location, verbose=False); print 'got U and V wind vectors'
P_prec = LocDic_hrrr_pollywog(DATE, 'APCP:surface', location, verbose=False); print 'got prec'
P_accum = {}

# Convert the units of each Pollywog and each location
for loc in location.keys():
    # Convert Units for the variables in the Pollywog
    P_temp[loc] = KtoF(P_temp[loc])
    P_dwpt[loc] = KtoF(P_dwpt[loc])
    #P_wind[loc] = mps_to_MPH(P_wind[loc])
    #P_gust[loc] = mps_to_MPH(P_gust[loc])
    #P_UV[loc] = mps_to_MPH(P_UV[loc])
    P_prec[loc] = mm_to_inches(P_prec[loc])
    P_accum[loc] = np.add.accumulate(P_prec[loc])



## 6) Main Figures: Create a figure for each location. Add permenant elements to each.
print 'making permenant figure elements...'
figs = {}
locs = location.keys() # a list of all the locations
locs_idx = range(len(locs)) # a number index for each location
for n in locs_idx:
    locName = locs[n]
    l = location[locName]
    figs[locName] = {0:plt.figure(n)}
    # Super Title
    if l['state'] != 'Not Reported':
        plt.suptitle('HRRR Forecast: %s, %s' % (locName, l['state']), y=1)
    else:
        plt.suptitle('HRRR Forecast: %s, (state not reported)' % (locName), y=1)
    # Map - background, roads, radar, wind barbs
    figs[locName][1] = figs[locName][0].add_subplot(121)
    maps[locName].drawcounties()
    maps[locName].drawstates()
    maps[locName].arcgisimage(service='World_Shaded_Relief',
                              xpixels=500,
                              verbose=False)
    #
    # Overlay Fire Perimeters
    try:
        per = maps[locName].readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/fire_shapefiles/active_perimeters_dd83', 'perim', drawbounds=False)
        patches = []
        print 'finding fire perimeter patches for '+locName+' fire...',
        for info, shape in zip(maps[locName].perim_info, maps[locName].perim):
            # Check if the boundary is one of the large active fires
            if info['FIRENAME'].upper() in location.keys():
                patches.append(Polygon(np.array(shape), True) )
        figs[locName][1].add_collection(PatchCollection(patches, facecolor='indianred', alpha=.65, edgecolor='k', linewidths=.1, zorder=1))
        print 'Done!'
    except:
        print "Couldn't draw any new shapes"
    """
    try:
        per = maps[locName].readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim','perim', drawbounds=False)
        patches = []
        print 'finding fire perimeter patches for '+locName+' fire...',
        for info, shape in zip(maps[locName].perim_info, maps[locName].perim):
            # Check if the boundary is one of the large active fires
            if info['FIRENAME'].upper() in location.keys():
                patches.append(Polygon(np.array(shape), True) )
        figs[locName][1].add_collection(PatchCollection(patches, facecolor='indianred', alpha=.65, edgecolor='k', linewidths=.1, zorder=1))
        print 'Done!'
    except:
        pass
    """

    #
    # Overlay Utah Roads
    #BASE = '/uufs/chpc.utah.edu/common/home/u0553130/'
    #maps[locName].readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads',
    #                            'roads',
    #                            linewidth=.5)
    #
    # Point for fire start location on map.
    x, y = m(l['longitude'], l['latitude']) # Location
    maps[locName].scatter(x, y, s=100, color='white', edgecolor='k', zorder=100)
    #
    # Plot: Temperature, dewpoint
    figs[locName][2] = figs[locName][0].add_subplot(322)
    figs[locName][2].plot(P_temp['DATETIME'], P_temp[locName], c='r', label='Temperature')
    figs[locName][2].plot(P_dwpt['DATETIME'], P_dwpt[locName], c='g', label='Dew Point')
    leg2 = figs[locName][2].legend()
    leg2.get_frame().set_linewidth(0)
    figs[locName][2].grid()
    figs[locName][2].set_ylabel('Degrees (F)')
    figs[locName][2].set_xlim([P_temp['DATETIME'][0], P_temp['DATETIME'][-1]])
    figs[locName][2].set_ylim([np.nanmin(P_dwpt[locName])-3, np.nanmax(P_temp[locName])+3])
    figs[locName][2].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][2].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][2].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Wind speed, gust, barbs
    figs[locName][3] = figs[locName][0].add_subplot(324)
    figs[locName][3].plot(P_gust['DATETIME'], P_gust[locName], c='chocolate', label='Instantaneous Wind Gust')
    figs[locName][3].plot(P_wind['DATETIME'], P_wind[locName], c='darkorange', label='Previous Hour Max Wind')
    # plt.barbs can not take a datetime object, so find the date indexes:
    idx = mpl.dates.date2num(P_UV['DATETIME'])
    figs[locName][3].barbs(idx, P_UV[locName][:,2], P_UV[locName][:,0], P_UV[locName][:,1],
                           length=6,
                           barb_increments=dict(half=2.5, full=5, flag=25))
    leg3 = figs[locName][3].legend()
    leg3.get_frame().set_linewidth(0)
    figs[locName][3].grid()
    figs[locName][3].set_ylabel(r'Wind Speed (ms$\mathregular{^{-1}}$)')
    #figs[locName][3].set_ylabel('Wind Speed (mph)')
    figs[locName][3].set_ylim([0, np.nanmax(P_gust[locName])+3])
    figs[locName][3].set_yticks([0, np.nanmax(P_gust[locName])+3], 2.5)
    figs[locName][3].set_xlim([P_gust['DATETIME'][0], P_gust['DATETIME'][-1]])
    figs[locName][3].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][3].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][3].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    # Plot: Accumulated precip
    figs[locName][4] = figs[locName][0].add_subplot(326)
    figs[locName][4].bar(P_prec['DATETIME'], P_prec[locName], width=.04, color='dodgerblue', label='1 hour Precipitation')
    figs[locName][4].plot(P_prec['DATETIME'], P_accum[locName], color='limegreen', label='Accumulated Precipitation')
    figs[locName][4].set_xlim([P_prec['DATETIME'][0], P_prec['DATETIME'][-1]])
    figs[locName][4].set_ylim([0, np.nanmax(P_accum[locName])+.1])
    figs[locName][4].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    figs[locName][4].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    figs[locName][4].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))
    leg4 = figs[locName][4].legend()
    leg4.get_frame().set_linewidth(0)
    figs[locName][4].grid()
    figs[locName][4].set_ylabel('Precipitation (in)')
    #
    # Finally, add MesoWest data if it is available
    if l['is MesoWest'] != False:
        a = get_mesowest_ts(l['is MesoWest'], DATE, datetime.utcnow(),
                            variables='air_temp,wind_speed,dew_point_temperature')
        if a != 'ERROR':
            figs[locName][2].plot(a['DATETIME'], CtoF(a['air_temp']), c='k', ls='--')
            figs[locName][2].plot(a['DATETIME'], CtoF(a['dew_point_temperature']), c='k', ls='--')
            #figs[locName][3].plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--')
            figs[locName][3].plot(a['DATETIME'], a['wind_speed'], c='k', ls='--')

# Now add the element that changes, save the figure, and remove elements from plot.
# Only download the HRRR grid once per forecast hour.
for fxx in range(0, 19):
    # Loop through each location to make plots for this time
    # 2.2) Radar Reflectivity and winds for entire CONUS
    H = get_hrrr_variable(DATE, 'REFC:entire atmosphere', fxx=fxx, model='hrrr')
    H_UV = get_hrrr_variable(DATE, 'UVGRD:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_spd = get_hrrr_variable(DATE, 'WIND:10 m', fxx=fxx, model='hrrr', value_only=True)
    H_gst = get_hrrr_variable(DATE, 'GUST:surface', fxx=fxx, model='hrrr', value_only=True)
    #
    #
    # Mask out empty reflectivity values
    dBZ = H['value']
    dBZ = np.ma.array(dBZ)
    dBZ[dBZ == -10] = np.ma.masked
    #
    #
    # Use the retrieved grids for each fire map...
    for n in locs_idx:
        locName = locs[n]
        l = location[locName]
        print "\n--> Working on:", locName, fxx
        #
        #SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/' % locName.replace(' ', '_')
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/%s/%s/' % (DATE.strftime('%Y-%m-%d/%H00'), locName.replace(' ', '_'))
        if not os.path.exists(SAVE):
            # make the SAVE directory if fire doesn't already exist
            os.makedirs(SAVE)
            print "created:", SAVE
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer_fire.php'
            os.link(photo_viewer, SAVE+'photo_viewer_fire.php')
        # Title over map
        if np.shape(H['value']) > 0:
            figs[locName][1].set_title('UTC: %s' % (DATE+timedelta(hours=fxx)))
            figs[locName][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (H['anlys'].strftime('%Y %b %d, %H:%M'), fxx, H['valid'].strftime('%Y %b %d, %H:%M')))
        else:
            figs[locName][1].set_title('UTC: %s' % (DATE+timedelta(hours=fxx)))
            figs[locName][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % ('NOT AVAILABLE, CHECK NOMADS FOR FILE', fxx, 'NOT AVAILABLE, CHECK NOMADS FOR FILE'))
        #
        if np.shape(H['value']) > 0:
            # Project on map
            X, Y = maps[locName](H['lon'], H['lat'])            # HRRR grid
            # Trim the data
            cut_v, cut_h = pluck_point_new(l['latitude'],
                                        l['longitude'],
                                        H['lat'],
                                        H['lon'])
            bfr = 35
            trim_X = X[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
            trim_Y = Y[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
            trim_dBZ = dBZ[cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
            trim_H_U = H_UV['UGRD'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
            trim_H_V = H_UV['VGRD'][cut_v-bfr:cut_v+bfr, cut_h-bfr:cut_h+bfr]
            #
            #####################################################################################
            #### Alerts #########################################################################
            # Alerts: Check for high winds in the vicinity of the fire
            '''
            alert_box_bfr1 = 15 # a 90x90 km box
            alert_box_bfr2 = 25 # a 150x150 km box
            alert_box_wind = H_spd['value'][cut_v-alert_box_bfr1:cut_v+alert_box_bfr1, cut_h-alert_box_bfr1:cut_h+alert_box_bfr1]
            alert_box_gust = H_gst['value'][cut_v-alert_box_bfr1:cut_v+alert_box_bfr1, cut_h-alert_box_bfr1:cut_h+alert_box_bfr1]
            alert_box_ref = H['value'][cut_v-alert_box_bfr2:cut_v+alert_box_bfr2, cut_h-alert_box_bfr2:cut_h+alert_box_bfr2]
            #
            max_alert_box_wind = np.nanmax(alert_box_wind)
            if max_alert_box_wind > 15: # 15 m/s
                print "!! Alert--Wind speed greater than 15 m/s:", locName
                myfile = open("/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_fires_alerts.csv", "a")
                max_alert_box_gust = np.nanmax(alert_box_gust)
                max_alert_box_ref = np.nanmax(alert_box_ref)
                validDate = (DATE + timedelta(hours=fxx)).strftime('%Y-%m-%d_%H%M')
                fileDate = '%04d%02d%02d/hrrr.t%02dz.wrfsfcf%02d.grib2' % (DATE.year, DATE.month, DATE.day, DATE.hour, fxx)
                write_this = ','.join([validDate, locName, l['state'], str(l['area']), str(max_alert_box_wind), str(max_alert_box_gust), str(max_alert_box_ref), fileDate, str(l['latitude']), str(l['longitude'])])
                myfile.write(write_this+'\n')
                myfile.close()
            '''
            #####################################################################################
            #####################################################################################
            #
            # Overlay Simulated Radar Reflectivity
            ctable = 'NWSReflectivity'
            norm, cmap = ctables.registry.get_with_steps(ctable, -0, 5)
            radar = figs[locName][1].pcolormesh(trim_X, trim_Y, trim_dBZ,
                                                norm=norm,
                                                cmap=cmap,
                                                alpha=.5)
            if fxx == 0:
                # Solution for adding colorbar from stackoverflow
                # http://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
                from mpl_toolkits.axes_grid1 import make_axes_locatable
                divider = make_axes_locatable(figs[locName][1])
                cax = divider.append_axes('bottom', size='5%', pad=0.05)
                cb = figs[locName][0].colorbar(radar, cax=cax, orientation='horizontal')
                #cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=5 mph, Full=10 mph, Flag=50 mph')
                cb.set_label('Simulated Radar Reflectivity (dBZ)\n\n'+ r'Barbs: Half=2.5 ms$\mathregular{^{-1}}$, Full=5 ms$\mathregular{^{-1}}$, Flag=25 ms$\mathregular{^{-1}}$')
            #
            # Add nearby MesoWest
            if fxx in [0, 1]:
                MW_date = P_temp['DATETIME'][fxx]
                b = get_mesowest_radius(MW_date, 15,
                                        extra='&radius=%s,%s,60' % (l['latitude'], l['longitude']),
                                        variables='wind_speed,wind_direction')
                if len(b['NAME']) > 0:
                    MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'], b['wind_direction'])
                    #MW_u = mps_to_MPH(MW_u)
                    #MW_v = mps_to_MPH(MW_v)
                    MWx, MWy = maps[loc](b['LON'], b['LAT'])
                    MW_barbs = figs[locName][1].barbs(MWx, MWy, MW_u, MW_v,
                                                    color='r',
                                                    barb_increments=dict(half=2.5, full=5, flag=25))
                if l['is MesoWest'] != False:
                    stn_point = figs[locName][1].scatter(a['LON'], a['LAT'], color='r', s=15)
                    stn_text = figs[locName][1].text(a['LON'], a['LAT'], a['STID'], color='r', fontsize=9)
            #
            # Wind Barbs
            # Overlay wind barbs (need to trim this array before we plot it)
            # First need to trim the array
            barbs = figs[locName][1].barbs(trim_X[::3,::3], trim_Y[::3,::3],
                                           trim_H_U[::3,::3], trim_H_V[::3,::3],
                                           zorder=200, length=5)
            #
            # 3.2) Temperature/Dew Point
            tempF = P_temp[locName]
            dwptF = P_dwpt[locName]
            pntTemp = figs[locName][2].scatter(P_temp['DATETIME'][fxx], tempF[fxx], c='r', s=60)
            pntDwpt = figs[locName][2].scatter(P_dwpt['DATETIME'][fxx], dwptF[fxx], c='g', s=60)
            #
            # 3.3) Wind speed and Barbs Point
            pntGust = figs[locName][3].scatter(P_gust['DATETIME'][fxx], P_gust[locName][fxx], c='chocolate', s=60)
            pntWind = figs[locName][3].scatter(P_wind['DATETIME'][fxx], P_wind[locName][fxx], c='darkorange', s=60)
            #
            # 3.4) Accumulated Precipitation Point
            pntPrec = figs[locName][4].scatter(P_prec['DATETIME'][fxx], P_accum[locName][fxx], edgecolor="k", color='limegreen', s=60)
            #
            # 4) Save figure
            figs[locName][0].savefig(SAVE+'f%02d.png' % (fxx))
            print "Saved:", SAVE+'f%02d.png' % (fxx)
            #
            # Remove temporary data for next plot
            pntTemp.remove()
            pntDwpt.remove()
            pntGust.remove()
            pntWind.remove()
            pntPrec.remove()
            barbs.remove()
            radar.remove()
            try:
                MW_barbs.remove()
                stn_point.remove()
                stn_text.remove()
            except:
                # No barbs were plotted
                pass
    print "Finished:", fxx

# Do some webpage management:
#  - Removes old fires from the directory
#  - Edits HTML to include current fires
#  - Plots a map of the fires
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/')
from manager import *
remove_old_fires()
write_HRRR_fires_HTML()
draw_fires_on_map()
