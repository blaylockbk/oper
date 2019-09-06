# Brian Blaylock
# April 24, 2017                                    Jazz are going to Game 5!!!
# April 09, 2019 for python 3                                      It's raining

"""
The superintendant at Spanish Oaks Golf Course, Dallin Naulu,
inspired me to make a golf weather product using the raw HRRR
weather data. Something that displays the temperature, humidity, wind, and 
precipitation forecast with a panel showing the simulated radar for the
surrounding area. This product can be used for any location, not just a golf
course. Added Utah Lake, Lagoon, and some MesoWest locations of interest.

(I apologize the plotting is horrendously confusing. This helps improve speed.
Permenant map elements are created first, and are stored in a dictionary. 
Then the elements for each hour are added, the figure is save, then the
temporary plot element is removed before the next forecast hour is run. This 
completes 22 mins faster than the original script.)
"""
import matplotlib as mpl
mpl.use('Agg') #required for the CRON job. Says "do not open plot in a window"??
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
mpl.rcParams['figure.max_open_warning'] = 30

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v3')

from BB_HRRR.HRRR_Pando import get_hrrr_variable, get_hrrr_all_run,\
                               get_hrrr_latlon, \
                               hrrr_subset, LocDic_hrrr_pollywog
from BB_maps.my_basemap import draw_centermap
from BB_MesoWest.get_MesoWest import get_mesowest_ts, get_mesowest_radius
from metpy.plots import ctables
from BB_wx_calcs.wind import wind_uv_to_spd, wind_spddir_to_uv
from BB_wx_calcs.units import *
from BB_cmap.landuse_colormap import LU_MODIS21
import location_dic
from HRRR_warning import *


## 1) Get Locations Dictionary
location = location_dic.get_all()

'''
# shorten the dictionary for quick testing:
L = {}
for i in list(location.keys())[0:2]:
    L[i] = location[i]
location = L
'''

## 2) Make map object for each location and store in a dictionary
print('Make %s Maps (this takes a while if location_dic has a lot of locations)' % len(location))
for name, loc in location.items():
    FILE = './saved_map_objects/%s.npy' % name
    if os.path.exists(FILE):
        m = np.load(FILE, allow_pickle=True).item()
        print('loaded %s map from file' % name)
    else:
        center = (loc['latitude'], loc['longitude'])
        m = draw_centermap(center, size=(.3,.3))
        # Save the map object for later use
        np.save(FILE, m)
        print('saved %s map to file' % name)
    ## Store map object in location dictionary
    location[name]['map'] = m

## 3) Create a landuse image for each locations
##    Create new figure once a day because landuse ice cover changes on lakes
if datetime.utcnow().hour == 0:
    LU = get_hrrr_variable(datetime.now(), 'VGTYP:surface')
    LU_cmap = LU_MODIS21()
    for n, (name, loc) in enumerate(location.items()):
        print('Generating LandUse map for %s' % name)
        LU_SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/%s/LandUse.png' % name.replace(' ', '_')
        plt.figure(1000)
        loc['map'].pcolormesh(LU['lon'], LU['lat'], LU['value'],
                                cmap=LU_cmap['cmap'],
                                vmin=LU_cmap['vmin'],
                                vmax=LU_cmap['vmax'])
        cb = plt.colorbar(orientation='vertical', pad=.01, shrink=.95)
        cb.set_ticks(np.arange(0.5, len(LU_cmap['labels']) + 1))
        cb.ax.set_yticklabels(LU_cmap['labels'])
        loc['map'].scatter(loc['longitude'], loc['latitude'],
                            marker='+', c='maroon', s=100)
        loc['map'].drawstates()
        loc['map'].drawcounties()
        plt.title('Landuse near %s' % name)
        plt.show()
        plt.savefig(LU_SAVE)  
        print("created landuse maps for ", name)
        plt.close()


## 4) Get the HRRR data from NOMADS
# NOTE: ~1-hour delay in forecasts, so set date to one hour ago and round to 
#       nearest hour.
DATE = datetime.utcnow() - timedelta(hours=1) # hour delay in forecasts available
DATE = datetime(DATE.year, DATE.month, DATE.day, DATE.hour)

print("Current Local DATE:", datetime.now())
print("  Request UTC DATE:", DATE)

# Pollywogs: Pluck HRRR value at all locations for each variable.
# These are dictionaries:
# {'DATETIME':[array of dates], 'station name': [values for each datetime], ...}
print("plucking values from HRRR")
P_temp = LocDic_hrrr_pollywog(DATE, 'TMP:2 m', location, verbose=False); print("got Temp")
P_dwpt = LocDic_hrrr_pollywog(DATE, 'DPT:2 m', location, verbose=False); print("got Dwpt")
P_wind = LocDic_hrrr_pollywog(DATE, 'WIND:10 m', location, verbose=False); print("got Wind")
P_gust = LocDic_hrrr_pollywog(DATE, 'GUST:surface', location, verbose=False); print("got Gust")
P_UV = LocDic_hrrr_pollywog(DATE, 'UVGRD:10 m', location, verbose=False); print("got UGRD and VGRD")
P_prec = LocDic_hrrr_pollywog(DATE, 'APCP:surface', location, verbose=False); print("got Precip")
P_accum = {} # Accumulated precipitation

# Convert the units of each Pollywog and each location
for name in location:
    # Convert Units for the variables in the Pollywog
    P_temp[name] = K_to_F(P_temp[name])
    P_dwpt[name] = K_to_F(P_dwpt[name])
    P_wind[name] = mps_to_MPH(P_wind[name])
    P_gust[name] = mps_to_MPH(P_gust[name])
    P_UV[name] = mps_to_MPH(P_UV[name])
    P_prec[name] = mm_to_inches(P_prec[name])
    P_accum[name] = np.add.accumulate(P_prec[name]) # Accumulated Precipitation


## 5) Check for extreme values and send email alert
try:
    for warn in ['UKBKB', 'KSLC']:
        wind_warning(location, P_wind, warn)
        temp_warning(location, P_temp, warn)
except:
    print('(warnings did not work for some reason)')
    pass


## 6) Create a figure for each location and add permenant elements
# NOTE: Keys in the 'fig' dictionary for each location:
#  loc[name]['fig'] = {0: the main figure,
#                      1: the left map axes,
#                      2: the right top plot axes,
#                      3: the right middle plot axes,
#                      4: the right bottom plot axes}
print('Making permenant figure elements...')
for n, (name, loc) in enumerate(location.items()):
    print('   Working on --> %s' % name)
    tz = loc['timezone']
    location[name]['fig'] = {0:plt.figure(n)}
    plt.suptitle('HRRR Forecast: %s' % (loc['name']), y=1)
    #
    ## Plot: Map - background, roads, radar, wind barbs (left)
    loc['fig'][1] = loc['fig'][0].add_subplot(121) # left map
    loc['map'].drawcounties()
    loc['map'].arcgisimage(service='World_Shaded_Relief', xpixels=700, verbose=False)
    #
    ## Overlay Utah Roads
    utah_roads = '/uufs/chpc.utah.edu/common/home/u0553130/shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads'
    loc['map'].readshapefile(utah_roads, 'roads', linewidth=.5, color='dimgrey')
    #
    ## Center marker for the location of interest
    loc['map'].scatter(loc['longitude'], loc['latitude'], s=100, color='white', edgecolor='k', zorder=100, latlon=True)
    #
    ## Plot: Temperature, dewpoint (right top)
    loc['fig'][2] = loc['fig'][0].add_subplot(322)
    loc['fig'][2].plot(P_temp['DATETIME'], P_temp[name], c='r', label='Temperature', zorder=50)
    loc['fig'][2].plot(P_dwpt['DATETIME'], P_dwpt[name], c='g', label='Dew Point', zorder=50)
    leg2 = loc['fig'][2].legend()
    leg2.get_frame().set_linewidth(0)
    loc['fig'][2].grid()
    loc['fig'][2].set_ylabel('Degrees (F)')
    loc['fig'][2].set_xlim([P_temp['DATETIME'][0], P_temp['DATETIME'][-1]])
    loc['fig'][2].set_ylim([np.nanmin(P_dwpt[name])-3, np.nanmax(P_temp[name])+3])
    loc['fig'][2].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    loc['fig'][2].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    loc['fig'][2].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    ## Plot: Wind speed, gust, barbs (right middle)
    loc['fig'][3] = loc['fig'][0].add_subplot(324)
    loc['fig'][3].plot(P_gust['DATETIME'], P_gust[name], c='chocolate', label='Instantaneous Wind Gust', zorder=50)
    loc['fig'][3].plot(P_wind['DATETIME'], P_wind[name], c='darkorange', label='Previous Hour Max Wind', zorder=50)
    # plt.barbs can not take a datetime object, so find the date indexes:
    idx = mpl.dates.date2num(P_UV['DATETIME'])
    loc['fig'][3].barbs(idx, P_UV[name][:,2], P_UV[name][:,0], P_UV[name][:,1],
                           length=6,
                           barb_increments=dict(half=5, full=10, flag=50), zorder=50)
    leg3 = loc['fig'][3].legend()
    leg3.get_frame().set_linewidth(0)
    loc['fig'][3].grid()
    loc['fig'][3].set_ylabel('Wind Speed (mph)')
    loc['fig'][3].set_ylim([0, np.nanmax(P_gust[name])+3])
    loc['fig'][3].set_yticks([0, np.nanmax(P_gust[name])+3], 2.5)
    loc['fig'][3].set_xlim([P_gust['DATETIME'][0], P_gust['DATETIME'][-1]])
    loc['fig'][3].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    loc['fig'][3].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    loc['fig'][3].xaxis.set_major_formatter(mdates.DateFormatter(''))
    #
    ## Plot: Accumulated precipitation (right bottom)
    loc['fig'][4] = loc['fig'][0].add_subplot(326)
    loc['fig'][4].bar(P_prec['DATETIME'], P_prec[name], width=.04, color='dodgerblue', label='1 hour Precipitation', zorder=50)
    loc['fig'][4].plot(P_prec['DATETIME'], P_accum[name], color='limegreen', label='Accumulated Precipitation', zorder=50)
    loc['fig'][4].set_xlim([P_prec['DATETIME'][0], P_prec['DATETIME'][-1]])
    loc['fig'][4].set_ylim([0, np.nanmax(P_accum[name])+.1])
    loc['fig'][4].xaxis.set_major_locator(mdates.HourLocator(range(0, 24, 3)))
    loc['fig'][4].xaxis.set_minor_locator(mdates.HourLocator(range(0, 24, 1)))
    loc['fig'][4].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d\n%H:%M'))
    leg4 = loc['fig'][4].legend()
    leg4.get_frame().set_linewidth(0)
    loc['fig'][4].grid()
    loc['fig'][4].set_ylabel('Precipitation (in)')
    #
    ## Finally, add MesoWest timeseries to plots if it is available
    if loc['is MesoWest'] is True:
        a = get_mesowest_ts(name, DATE, datetime.utcnow(),
                            variables='air_temp,wind_speed,dew_point_temperature')
        if a != 'ERROR':
            try:
                loc['fig'][2].plot(a['DATETIME'], C_to_F(a['air_temp']), c='k', ls='--', zorder=50)
            except:
                print('%s no MesoWest air temperature' % a['NAME'])
            try:
                loc['fig'][2].plot(a['DATETIME'], C_to_F(a['dew_point_temperature']), c='k', ls='--', zorder=50)
                maxT = np.nanmax([np.nanmax(P_temp[name]), np.nanmax(C_to_F(a['air_temp']))])
                minT = np.nanmin([np.nanmin(P_dwpt[name]), np.nanmin(C_to_F(a['dew_point_temperature']))])
                loc['fig'][2].set_ylim([minT-3, maxT+3])
            except:
                print('%s no MesoWest dew point' % a['NAME'])
            try:
                loc['fig'][3].plot(a['DATETIME'], mps_to_MPH(a['wind_speed']), c='k', ls='--', zorder=50)
            except:
                print('%s no MesoWest wind speed' % a['NAME'])
            

## Now, add the element that changes, save the figure for each forecast.
# 2.2) Get Radar Reflectivity and winds for entire CONUS for every forecast
HH_refc = get_hrrr_all_run(DATE, 'REFC:entire')
HH_u, HH_v, HH_spd = get_hrrr_all_run(DATE, 'UVGRD:10 m')
Hlat, Hlon = get_hrrr_latlon(DICT=False)

# Convert Units (meters per second -> miles per hour)
HH_u = mps_to_MPH(np.array(HH_u))
HH_v = mps_to_MPH(np.array(HH_v))
HH_spd = mps_to_MPH(np.array(HH_spd))

for fxx in range(0, 19):
    for n, (name, loc) in enumerate(location.items()):
        tz = loc['timezone']
        print("  --> Working on: F%02d %s" % (fxx, name))
        ## Get grids for this particular forecast time...
        H_refc = HH_refc[fxx]
        H_u = HH_u[fxx]
        H_v = HH_v[fxx]       
        #
        ## Define a save directory
        SAVE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_golf/%s/' % name
        if not os.path.exists(SAVE):
            # make the SAVE directory if id doesn't already exist
            os.makedirs(SAVE)
            print("created:", SAVE)
            # then link the photo viewer
            photo_viewer = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/photo_viewer/photo_viewer2.php'
            os.link(photo_viewer, SAVE+'photo_viewer2.php')
        #
        ## Title over map
        loc['fig'][1].set_title('          UTC: %s\nLocal Time: %s' % (DATE+timedelta(hours=fxx), DATE+timedelta(hours=fxx)-timedelta(hours=tz)))
        loc['fig'][2].set_title('       Run (UTC): %s f%02d\nValid (UTC): %s' % (DATE.strftime('%Y %b %d, %H:%M'), fxx, (DATE+timedelta(hours=fxx)).strftime('%Y %b %d, %H:%M')))
        #
        ## Trim the data for much faster plotting
        H_refc_dict = {'lat': Hlat, 'lon': Hlon, 'value':H_refc}
        H_u_dict = {'lat': Hlat, 'lon': Hlon, 'value':H_u}
        H_v_dict = {'lat': Hlat, 'lon': Hlon, 'value':H_v}
        trim_refc = hrrr_subset(H_refc_dict, half_box=15, 
                                lat=loc['latitude'], lon=loc['longitude'],
                                thin=1, verbose=False)
        trim_u = hrrr_subset(H_u_dict, half_box=15,
                                lat=loc['latitude'], lon=loc['longitude'],
                                thin=1, verbose=False)
        trim_v = hrrr_subset(H_v_dict, half_box=15,
                             lat=loc['latitude'], lon=loc['longitude'],
                             thin=1, verbose=False)
        #
        ## Overlay Simulated Radar Reflectivity on map
        ctable = 'NWSReflectivity'
        norm, cmap = ctables.registry.get_with_steps(ctable, 5, 5)
        radar = loc['fig'][1].pcolormesh(trim_refc['lon'], trim_refc['lat'], trim_refc['value'],
                                         norm=norm, cmap=cmap, alpha=.5)
        if fxx == 0:
            # Solution for adding colorbar from stackoverflow
            # http://stackoverflow.com/questions/32462881/add-colorbar-to-existing-axis
            from mpl_toolkits.axes_grid1 import make_axes_locatable
            divider = make_axes_locatable(loc['fig'][1])
            cax = divider.append_axes('bottom', size='5%', pad=0.05)
            cb = loc['fig'][0].colorbar(radar, cax=cax, orientation='horizontal')
            cb.set_label('Simulated Radar Reflectivity (dBZ)\n\nBarbs: Half=5 mph, Full=10 mph, Flag=50 mph')
        #
        ## Add HRRR Wind Barbs
        barbs = loc['fig'][1].barbs(trim_u['lon'], trim_u['lat'],
                                    trim_u['value'], trim_v['value'],
                                    zorder=200, length=6)
        #
        ## Add nearby MesoWest wind barbs, if available. 
        try:
            MW_date = P_temp['DATETIME'][fxx]
            b = get_mesowest_radius(MW_date, name, variables='wind_speed,wind_direction')
            if len(b['NAME']) > 0:
                MW_u, MW_v = wind_spddir_to_uv(b['wind_speed'], b['wind_direction'])
                MW_u = mps_to_MPH(MW_u)
                MW_v = mps_to_MPH(MW_v)
                MW_barbs = loc['fig'][1].barbs(b['LON'], b['LAT'], MW_u, MW_v,
                                                  color='r', zorder=500,
                                                  barb_increments=dict(half=5, full=10, flag=50))
        except:
            print('!!!! Could Not plot MesoWest wind barbs: f%02d' % fxx)
        #
        #
        # 3.2) Temperature/Dew Point
        tempF = P_temp[name]
        dwptF = P_dwpt[name]
        pntTemp = loc['fig'][2].scatter(P_temp['DATETIME'][fxx], tempF[fxx], c='r', s=60, zorder=100)
        pntDwpt = loc['fig'][2].scatter(P_dwpt['DATETIME'][fxx], dwptF[fxx], c='g', s=60, zorder=100)
        #
        # 3.3) Wind speed and Barbs
        pntGust = loc['fig'][3].scatter(P_gust['DATETIME'][fxx], P_gust[name][fxx], c='chocolate', s=60, zorder=100)
        pntWind = loc['fig'][3].scatter(P_wind['DATETIME'][fxx], P_wind[name][fxx], c='darkorange', s=60, zorder=100)
        #
        # 3.4) Accumulated Precipitation
        pntPrec = loc['fig'][4].scatter(P_prec['DATETIME'][fxx], P_accum[name][fxx], c='limegreen', s=60, zorder=100)
        #
        # 4) Save figure
        loc['fig'][4].set_xlabel('\nFigure generated at %s Mountain Time' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')), fontsize=8)
        loc['fig'][0].savefig(SAVE+'f%02d.png' % (fxx))
        print("===>> SAVED Figure: %s" % (SAVE+'f%02d.png' % (fxx)))
        #
        pntTemp.remove()
        pntDwpt.remove()
        pntGust.remove()
        pntWind.remove()
        pntPrec.remove()
        barbs.remove()
        radar.remove()
        try:
            MW_barbs.remove()
        except:
            # No barbs were plotted
            pass
    print("Finished:", fxx)
