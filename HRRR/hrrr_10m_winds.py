# Brian Blaylock
#
# Plotting netCDF data that has been converted from grib2 format (see get_process_hrrr.csh)

## Uses system arguments. To run type: python hrrr_10m_winds.py [file_name.nc] [map_domain]

## Must Convert grib2 file to a netcdf file
## in LINUX Terminal: 'wgrib2 gribfile.grib2 -netcdf newfile.nc'

## Lake and road shape files available here: 
## http://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2015&layergroup=Water

#------------------------------------------
# Future or Completed Changes:
#------------------------------------------
# Oct 29, 2015: Use a dictionary to sepcify location specific parameters like thin amount, units, lat, lon, etc. for speeding up processing.
# May 09, 2016: Plot MesoWest winds for analysis hour
# Future:       Change Map processing for speed. Draw map once and use lat/lon bounds for figure domain
# Future:       Use multiprocessing module for multiprocessing and faster plots (http://sebastianraschka.com/Articles/2014_multiprocessing_intro.html)



print ""
print ""

import sys,getopt
#from netCDF4 import Dataset  # use scipy instead (we don't have netCDF4 installed yet. If you use netCDF4 the syntax is slightly different)
from scipy.io import netcdf
import matplotlib
matplotlib.use('Agg')		#required for the CRON job. Says "do not open plot in a window"??
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.axes as maxes

# Now import modules of my own invention
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')
from functions_domains_models import get_domain
from BB_MesoWest import mesowest_stations_radius as MWr

def find_nearest(array, value):
    return (np.abs(array-value)).argmin()
    
def cut_data(bl_lat,tr_lat,bl_lon,tr_lon):
    '''    
    Cut down full netcdf data for domain for faster plotting.
    input: the bottom left corner and top right corner lat/lon coordinates
        bl_lat = bottom left latitude
        tr_lat = top right latitude
        bl_lon = bottom left longitude
        tr_lon = top right longitude
    return: the max and min of each the arrays x and y coordinates    
    
	lat and lon are global variables of the grids lat and lon
    '''
    lat_limit = np.logical_and(lat>bl_lat,lat<tr_lat)
    lon_limit = np.logical_and(lon>bl_lon,lon<tr_lon)
    
    total_limit = np.logical_and(lat_limit,lon_limit)
    
    xmin = np.min(np.where(total_limit==True)[0])-5 # +/- a buffer to cover map area (prevents white space in plot area) 
    xmax = np.max(np.where(total_limit==True)[0])+5
    ymin = np.min(np.where(total_limit==True)[1])-5
    ymax = np.max(np.where(total_limit==True)[1])+5
       
    return xmin,xmax,ymin,ymax
	
def thin_grids():
    '''
    Under Construction!!!
    Thins the amount of data to reduce the number of wind barbs
    '''

# Dicitonaries of Map Domains
        # Notes: 'thin' is used to thin out the wind barbs.
domains = {
'''
'uintah_basin': {
                'map_domain'    :'Uintah_Basin',                
                'name'          :'Uintah Basin',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :3,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :39.73,                
                'bot_left_lon'  :-111.,
                'top_right_lat' :41.,                
                'top_right_lon' :-109.
                },
'''				
'salt_lake_valley': {
                'map_domain'    :'Salt_Lake_Valley',
                'name'          :'Salt Lake Valley',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :1,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :40.4,
                'bot_left_lon'  :-112.19785,
                'top_right_lat' :40.9,
                'top_right_lon' :-111.60
                },
'utah_valley': {
                'map_domain'    :'Utah_Valley',
                'name'          :'Utah Valley',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :1,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :40.001550,
                'bot_left_lon'  :-111.901389,
                'top_right_lat' :40.451040,
                'top_right_lon' :-111.501889
                },
'utah_lake': {
                'map_domain'    :'Utah_Lake',
                'name'          :'Utah Lake',
                'map_projection':'cyl',
                'units'         :'mph',
                'thin'          :1,
                'max_speed'     :30,
                'time_zone'     :6,
                'bot_left_lat'  :40.,
                'bot_left_lon'  :-111.951,
                'top_right_lat' :40.375,
                'top_right_lon' :-111.65
                } # remember to add the , and } if you uncomment the stuff below!!!
}
'''
'bear_lake': {
                'map_domain'    :'Bear_Lake',
                'name'          :'Bear Lake',
                'map_projection':'cyl',
                'units'         :'mph',
                'thin'          :1,
                'max_speed'     :30,
                'time_zone'     :6,
                'bot_left_lat'  :41.826247,
                'bot_left_lon'  :-111.455473,
                'top_right_lat' :42.153301,
                'top_right_lon' :-111.189903
                },
'moses_lake': {
                'map_domain'    :'Moses_Lake',
                'name'          :'Moses Lake (WA)',
                'map_projection':'cyl',
                'units'         :'mph',
                'thin'          :1,
                'max_speed'     :30,
                'time_zone'     :7,
                'bot_left_lat'  :47.050935,
                'bot_left_lon'  :-119.403803,
                'top_right_lat' :47.193245,
                'top_right_lon' :-119.252493
                }
'''

''' Still need to figure out how to plot the entire HRRR field
if map_domain =="Full_HRRR":
        ## Set the Map Boundary as the Data Boundary
        domain="HRRR"
        bot_left_lat = lat[0][0]
        bot_right_lat = lat[0][-1]
        top_left_lat = lat[-1][0]
        top_right_lat = lat[-1][-1]
        
        bot_left_lon = lon[0][0]
        bot_right_lon = lon[0][-1]
        top_left_lon = lon[-1][0]
        top_right_lon = lon[-1][-1]
#Untill processing is faster, don't include full_utah. You can get this
# from weather.utah.edu        
'full_utah': {
                'map_domain'    :'Full_Utah',
                'name'          :'Utah',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :7,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :36.5,
                'bot_left_lon'  :-114.5,
                'top_right_lat' :42.5,
                'top_right_lon' :-108.5
                },
'cache_valley': {
                'map_domain'    :'Cache_Valley',
                'name'          :'Cache Valley',
                'map_projection':'cyl',
                'units'         :'m/s',
                'thin'          :1,
                'max_speed'     :25,
                'time_zone'     :6,
                'bot_left_lat'  :,
                'bot_left_lon'  :,
                'top_right_lat' :,
                'top_right_lon' :
                },
'''

#--------------------------------------------------
# Load the system arguments and set other settings    
#--------------------------------------------------
file_name = sys.argv[1]   # Raw HRRR netCDF file name must be this format: YYYYMMDDHHFHHhrrr.nc
tz        = sys.argv[2]   # Time Option [Local or UTC]

# Set universal figure margins for plot
width = 5
height = 4

BASE    = '/uufs/chpc.utah.edu/common/home/u0553130/'
FIG_DIR = BASE+'public_html/oper/current_HRRR/'
RAW_DIR = BASE+'oper/HRRR/raw_HRRR/'
#--------------------------------------------------

#--------------------------------------------------
# Open file in a netCDF reader
#--------------------------------------------------
# open HRRR .nc file
nc = netcdf.netcdf_file(RAW_DIR+file_name,'r')

# Grab these variables for now
#acc_precip = nc.variables['APCP_surface'][:][0]
#comref = nc.variables['REFC_entireatmosphere'][:][0]
lon = nc.variables['longitude'][:] - 360 #put longitude in degrees west rather than degrees east(negative degrees)
lon = lon.copy()
lat = nc.variables['latitude'][:]
lat = lat.copy()
u = nc.variables['UGRD_10maboveground'][:][0]
u = u.copy()
v = nc.variables['VGRD_10maboveground'][:][0]
v = v.copy()


nc.close()
#Calculate wind magnitude
spd = np.sqrt((u*u)+(v*v))

# open HRRR terrain file, get needed data, then close it.
terrain_file = 'geoHRRR.NC'
ter_nc = netcdf.netcdf_file(RAW_DIR+terrain_file,'r')
height = ter_nc.variables['HGT_M'][0,:,:]
height = height.copy()
ter_lon = ter_nc.variables['XLONG_M'][0]
ter_lon = ter_lon.copy()
ter_lat = ter_nc.variables['XLAT_M'][0]
ter_lat = ter_lat.copy()
ter_nc.close()

for domain in domains:
    plt.cla()
    plt.clf()
    plt.close()
    
    MP = domains[domain]['map_projection']
    units = domains[domain]['units']
    spd_max = domains[domain]['max_speed']
    tz_offset = domains[domain]['time_zone']
    thin = domains[domain]['thin']
    map_domain = domains[domain]['map_domain']
    name = domains[domain]['name']

    print map_domain,MP,units,spd_max,tz_offset,thin

    # Begin Processing
    #----------------------------------------------------------
    print ''    
    print 'Begin Processing', domains[domain]['name']
    
    # Get Date  # Raw HRRR netCDF file name must be this format: YYYYMMDDHHFHHhrrr
    model_time = file_name[0:10]
    forec_hour = file_name[11:13]
    date = datetime.strptime(model_time,'%Y%m%d%H')
    valid_time = date+timedelta(hours=int(forec_hour))
    print 'model run date:', date
    if tz == 'UTC':
        str_mod_init = datetime.strftime(date,'%Y %b %d %H:00 UTC')
        str_valid_time = datetime.strftime(valid_time,'%Y %b %d %H:00 UTC')
        str_save_time = datetime.strftime(valid_time,'%Y%b%d%H00 UTC')
    if tz == 'Local':
        str_mod_init = datetime.strftime(date-timedelta(hours=tz_offset),'%Y %b %d %H:00 Local')
        str_valid_time = datetime.strftime(valid_time-timedelta(hours=tz_offset),'%Y %b %d %H:00 Local') 
        str_save_time = datetime.strftime(valid_time-timedelta(hours=tz_offset),'%Y%b%d%H00 Local')
    print 'model initialized', str_mod_init
    print 'vaild hour', str_valid_time
    	
    bot_left_lat = domains[domain]['bot_left_lat']
    bot_left_lon = domains[domain]['bot_left_lon']
    top_right_lat = domains[domain]['top_right_lat']
    top_right_lon = domains[domain]['top_right_lon']
        
	# Use the function to trim the data for faster plotting
    xmin,xmax,ymin,ymax = cut_data(bot_left_lat,top_right_lat,bot_left_lon,top_right_lon)
	# redefine the variables with the trimmed limits
    lat_trim = lat[xmin:xmax,ymin:ymax]
    lon_trim = lon[xmin:xmax,ymin:ymax]
    u_trim   = u[xmin:xmax,ymin:ymax]
    v_trim   = v[xmin:xmax,ymin:ymax]
    spd_trim = spd[xmin:xmax,ymin:ymax]
    
    # Before plotting, adjust the wind speed units to mph if specified
    if units=='mph':
        u_trim   = u_trim*2.2369
        v_trim   = v_trim*2.2369
        spd_trim = spd_trim*2.2369    

    #-------------------------------------------
    # BEGIN ACTUAL PROCESSING HERE
    #-------------------------------------------
    print "plotting", domains[domain]['name']
    
    # Draw the base map behind it with the lats and
    # lons calculated earlier
    # lons calculated earlier
    # see documentation here: http://matplotlib.org/basemap/api/basemap_api.html
    
    if MP == 'cyl':
        ## Map in cylindrical projection (data points may apear skewed)
        m = Basemap(resolution='i',projection='cyl',\
            llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
            urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    
    
    if MP == 'lcc':
        ## Map in HRRR projected Coordinates
        m = Basemap(resolution='i',projection='lcc',\
            lat_0=38.5,lon_0=-97.5,lat_1=38.5,\
            lat_2=38.5,\
            llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
            urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)
    
    
    
    # This sets the standard grid point structure at full resolution
    # Converts WRF lat and long to the maps x an y coordinate
    x,y = m(lon_trim,lat_trim)
    ter_x,ter_y = m(ter_lon,ter_lat)
    
    
    m.drawstates(color='k', linewidth=1.25)
    m.drawcoastlines(color='k')
    m.drawcountries(color='k', linewidth=1.25)
    m.drawcounties(linewidth=.4,linestyle="solid", color="orange")
    
    #looking online it looks like mapscale is buggy and draws the wrong scales, but I haven't tried it yet
    #m.drawmapscale(lon, lat,lon0,lat0,length)
    
    # Draw other shape files (selected lakes, Utah roads, county lines)
    m.readshapefile(BASE+'shape_files/tl_2015_UtahLake_areawater/tl_2015_49049_areawater','lakes', linewidth=1.5)
    #m.readshapefile(BASE+'shape_files/tl_2015_BearLakeUT_areawater/tl_2015_49033_areawater','lakes', linewidth=1.5)
    #m.readshapefile(BASE+'shape_files/tl_2015_BearLakeID_areawater/tl_2015_16007_areawater','lakes', linewidth=1.5)
    #m.readshapefile(BASE+'shape_files/tl_2015_MosesLake_areawater/tl_2015_53025_areawater','lakes', linewidth=1.5)
    m.readshapefile(BASE+'shape_files/tl_2015_UtahRoads_prisecroads/tl_2015_49_prisecroads','roads', linewidth=.25)
    
    # Plot settings
    plt.figure(1, figsize=(width,height))
    plt.rc("figure.subplot", left = .001)
    plt.rc("figure.subplot", right = .999)
    plt.rc("figure.subplot", bottom = .001)
    plt.rc("figure.subplot", top = .999)
    plt.tight_layout(pad=5.08)
    
    #scale figure size to bigger image
    N = 2
    params = plt.gcf()
    plSize = params.get_size_inches()
    params.set_size_inches((plSize[0]*N, plSize[1]*N))
    
    plt.title('%s HRRR 10m Wind Forecast \nValid: %s' % (name, str_valid_time), \
    			fontsize=18,bbox=dict(facecolor='white', alpha=0.95),\
    			x=.5,y=.93,weight = 'demibold',style='oblique', \
    			stretch='normal', family='sans-serif')
    plt.xlabel('Model Initialized %s' % (str_mod_init), \
    			fontsize=12,\
    			x=.5,y=1.01,weight = 'demibold', \
    			stretch='normal', family='sans-serif',color="grey")
    
    im = plt.contourf(x,y,spd_trim, 
                        levels=np.arange(0,np.max(spd),.25),
                        cmap = plt.cm.Greens,
                        extend="max")
    #plt.pcolormesh(x,y,spd,cmap=plt.cm.Greens) #show each grid point explicitly
    cbar = plt.colorbar(orientation='vertical',ticks=np.arange(0,spd_max,2.5), shrink=0.8)
    cbar.set_label('Wind Speed ('+units+')')
    #cbar.ax.set_yticklabels(['< -1', '0', '> 1'])
    
    plt.clim(0,spd_max)
    
    #---Plot Terrain Data--------------The is the HRRR model terrain, not the actual terrain
    ter_con = plt.contour(ter_x,ter_y,height,np.arange(0,np.max(height),100),\
            colors='grey',width=5,linewidths=.5)
    levels = np.arange(1000,3500,100)
    plt.clabel(ter_con,levels, # label every second level
           inline=1,fontsize=7,
           fmt='%1.fm', #label format
           )
    
    ## Wind Barbs
    if units == 'm/s':
        HALF = 2.5
        FULL = 5
        FLAG = 25
    if units == 'mph':
        HALF = 2.5
        FULL = 5
        FLAG = 25
    cbar.set_label('Wind Speed ('+units+')\nBarbs: half='+str(HALF)+' full='+str(FULL)+' flag='+str(FLAG))
    if thin != 1:
        thin_x = x[0:np.shape(x)[0]:thin,0:np.shape(x)[1]:thin]
        thin_y = y[0:np.shape(x)[0]:thin,0:np.shape(x)[1]:thin]
        thin_u = u_trim[0:np.shape(x)[0]:thin,0:np.shape(x)[1]:thin]
        thin_v = v_trim[0:np.shape(x)[0]:thin,0:np.shape(x)[1]:thin]
        barbs = m.barbs(thin_x,thin_y,thin_u,thin_v,length=6,barbcolor="k",\
                   flagcolor='r',linewidth=.5,\
                    barb_increments=dict(half=HALF, full=FULL, flag=FLAG))
    else:
        barbs = m.barbs(x,y,u_trim,v_trim,length=6,barbcolor="k",\
                   flagcolor='r',linewidth=.5,\
                    barb_increments=dict(half=HALF, full=FULL, flag=FLAG))
    
    
      
    ## Plot MesoWest data for Analysis hour
    print 'forecast hour:',forec_hour
    if forec_hour=='00':
        mesowest_time= model_time+'00' 
        middle_index_row = np.shape(lat_trim)[0]/2
        middle_index_col = np.shape(lat_trim)[1]/2
        radius = '%s,%s,50' % (lat_trim[middle_index_row,middle_index_col],lon_trim[middle_index_row,middle_index_col])
        print "---------------------------------------------"        
        print "plot MesoWest", mesowest_time, radius, map_domain
        print "---------------------------------------------"
        a = MWr.get_mesowest_radius_winds(mesowest_time,'10',radius=radius,v=True)
        
        MWu,MWv = MWr.wind_spddir_to_uv(a['WIND_SPEED'],a['WIND_DIR'])
        
        x,y = m(a['LON'],a['LAT'])
        m.barbs(x,y,MWu,MWv,
                length=6.5,barbcolor="b",\
                flagcolor='r',linewidth=.85,\
                barb_increments=dict(half=HALF, full=FULL, flag=FLAG))
                
        print '-------------'
        nearest_lon = find_nearest(lon_trim,a['LON'][0])
        nearest_lat = find_nearest(lat_trim,a['LAT'][0])
        print a['LON'][0], nearest_lon, nearest_lat
        print '-------------'    
    
    print 'saving', FIG_DIR+str(forec_hour)+map_domain+'.png'
    plt.savefig(FIG_DIR+str(forec_hour)+map_domain+'.png',bbox_inches='tight',dpi=72)
    #plt.show()