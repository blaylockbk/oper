### Brian Blaylock
### 12 August 2016


# Need more help with shapefiles??
# http://basemaptutorial.readthedocs.io/en/latest/shapefile.html


# Plot fires shape file with MesoWest stations

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_MesoWest.MesoWest_stations_radius import get_mesowest_radius_stations, get_mesowest_stations



## Get 10-m winds and reflectivity from the HRRR for 


plt.figure(1, figsize=[12,12])

bot_left_lat = 30
bot_left_lon = -125
top_right_lat = 50
top_right_lon = -90


bot_left_lat = 43.565
bot_left_lon = -116.276
top_right_lat = 44.222
top_right_lon = -115.29

## Map in cylindrical projection (data points may apear skewed)
m = Basemap(resolution='i',projection='cyl',\
    llcrnrlon=bot_left_lon,llcrnrlat=bot_left_lat,\
    urcrnrlon=top_right_lon,urcrnrlat=top_right_lat,)

m.arcgisimage(service='NatGeo_World_Map', xpixels = 1000, dpi=100, verbose= True)

m.drawcoastlines()
m.drawcountries()
m.drawcounties(linewidth=2)
m.drawstates(linewidth=5)



perimiter = '160804'

# Draw other shape files (selected lakes, Utah roads, county lines)
# point shapefiles are not drawn on a map!
#p1 = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/perim_160801','perim', linewidth=2, color='b')
#p3 = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/perim_160803','perim', linewidth=1, color='r')
p4 = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/perim_'+perimiter,'perim', linewidth=1, color='indianred')

# Smoke lines are really messy
#s = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/smoke_160804','smoke', linewidth=2,color='g')

# cannot create a line for this. 
#f = m.readshapefile('/uufs/chpc.utah.edu/common/home/u0553130/fire_shape/fire_160804','fire', linewidth=3,color='r')



# What stations
stn_str = 'HFNC1,TT029'
request_date = datetime(2016,8,3,0) 
request_end = datetime(2016,8,6,12)
#request_date = datetime(2016,7,28) # earliest available day for HRRR forecasts. Can do earlier if you only do forecasts = ['f00']

# Start the fires dict with the extra other stations we wish to verify
start_API = request_date.strftime('%Y%m%d') 
end_API = request_end.strftime('%Y%m%d')
start_API2 = request_date.strftime('%Y%m%d%H%M') 
end_API2 = datetime.now().strftime('%Y%m%d%H%M')
extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'
b = get_mesowest_stations(start_API+','+end_API,stn_str,extra=extraAPI,v=False)


# What is the Lat/Lon of these stations?
lats = b['LAT']
lons = b['LON']

m.scatter(lons,lats,color='firebrick',s=150,zorder=500)
plt.text(lons[0],lats[0],b['STNID'][0],zorder=500)
plt.text(lons[1],lats[1],b['STNID'][1],zorder=500)

#m.scatter(-116.2146,43.6187,s=250) # Boise
#plt.text(-116.2146,43.6187,'Boise') # Boise
m.scatter(-116.,44.1,color='dodgerblue',s=150) # sounding location\ 19 August 2016 1400 UTC
plt.text(-116.,44.1,'sounding 08192016') # sounding location\ 19 August 2016 1400 UTC

plt.title('Pioneer Fire: '+perimiter)
plt.savefig('PioneerFire'+perimiter+'.png',bbox_inches='tight')
plt.show()