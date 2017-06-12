## Brian Blaylock

## 27 July 2016

# create the HRRR table for point duirng a large file
# to verify HRRR forecasts for large fires

#------------------------------------------------------------------
# To Do:
#   Add script to download map of fire from NASA worldview
#------------------------------------------------------------------

import matplotlib as mpl
mpl.use('Agg')		#required for the CRON job. Says "do not open plot in a window"??

import numpy as np
import os
from datetime import datetime, timedelta
import pygrib #requires the CHPC python version --% module load python/2.7.3
import multiprocessing #:)

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB')  #for running on CHPC boxes
sys.path.append('B:\pyBKB')  # local path for testing on my machine 

from BB_MesoWest.MesoWest_stations_radius import get_mesowest_radius_stations, get_mesowest_stations
from BB_HRRR.save_HRRR_MesoWest_point_FIRES import save_HRRR_MesoWest_point
from BB_HRRR.save_MesoWest_tophour import save_MesoWest_tophour
from BB_HRRR.plot_HRRR_vs_MesoWest_tophour import plot_ts
from functions_domains_models import get_domain

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def KtoC(Tk):
    """
    convert temperature from Kelvin to Celsius
    """
    return Tk-273.15


get_today = datetime.strftime(datetime.now(),'%Y-%m-%d')

#fires_file = '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/large_fire.txt'    # copied from gl1 by the gl1 crontab
#fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire2.txt' # used for custom fires
fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire_'+get_today+'.txt' # Operational file: local version copied from the gl1 crontab

fires = np.genfromtxt(fires_file,names=True,dtype=None,delimiter='\t')
#column names:
    #0  INAME - Incident Name
    #1  INUM
    #2  CAUSE
    #3  REP_DATE - reported date
    #4  START_DATE
    #5  IMT_TYPE
    #6  STATE
    #7  AREA
    #8  P_CNT - Percent Contained
    #9  EXP_CTN - Expected Containment
    #10 LAT
    #11 LONG
    #12 COUNTY
print "there are", len(fires), "large fires"  


# Time to begin MesoWest verification. Start at yesterday at 0000 UTC and we'll run until today (24 hours)
today = datetime(datetime.now().year,datetime.now().month,datetime.now().day)
request_date = today-timedelta(days=1)  
#request_date = datetime(2016,7,28) # earliest available day for HRRR forecasts. Can do earlier if you only do forecasts = ['f00']

# Start the fires dict with the extra other stations we wish to verify
start_API = request_date.strftime('%Y%m%d') 
end_API = datetime.now().strftime('%Y%m%d')
start_API2 = request_date.strftime('%Y%m%d%H%M') 
end_API2 = datetime.now().strftime('%Y%m%d%H%M')
extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'

stn_str = 'KSLC,UKBKB,WBB,NAA,LGCUT,EYSC'
b = get_mesowest_stations(start_API+','+end_API,stn_str,extra=extraAPI,v=False)            

fires_dict = {}
fires_dict['Other'] = {'stations':b,   
                      'f_name':'', #since these aren't for a fire, these are the directory we will save the other stations in.
                      's_DATE':'',
                      'f_lat':np.nan,
                      'f_lon':np.nan
                      }

#forecasts = ['f00','f01','f02','f03','f04','f05','f06','f07','f08','f09','f10','f11','f12','f13','f14','f15']
forecasts = ['f00','f06','f12']

# Create Directories for "Other" stations if it doesn't exist
base_dir = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
for forecast_hour in forecasts:
    out_dir = '%sOther/%s/' % (base_dir,forecast_hour) # the dir of the fire with the forecast hour
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)        
        print 'created:',out_dir
    
    fig_dir = '%sOther/figs/' % (base_dir)
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)
        print 'created:',fig_dir

# Now get and save the MesoWest data at the top of the hour for those stations
print "get other mesowest stations first"
MW_top_hour_other = save_MesoWest_tophour(b['STNID'],base_dir+'/Other/',start_API2,end_API2)




# def do_the_fire(): ## Could put this all in a funciton to use multiprocessing :)
"""
Input: 
    fire- the index number of the fire from text file. Ranges from 0 to len(fires)
    forecast_hour- the forecast hour as a string f##. Ranges from f00 (analysis) to f15
    
What it does:
    1) Reads the large_fire.txt file. Gets fire name, 
       start date, latitude, and longitude for an index value 
       which represents the fire/line number in the file.
    2) Creates new directories for each fire [NAME_s_date]
       and creates a directory for the forecast hour requested.
    3) Get all MesoWest stations within a 25 mile radius of
       the fires latitude and longitude. Returns a dictionary
       of the station names/IDs, latitudes, longitudes, elevations.
    4) Open HRRR file, find the grid point for each station,
       get the HRRR value for that point, save to a .csv file.
       Repeat until all values are plucked from fire start date
       to current time.
    5) Get the MesoWest observations nearest the top of the hour
       for each HRRR time, store in .csv file.
    6) Calculate Statistics for the fire.
    7) Create statistics plots comparing the HRRR data and the
       observed MesoWest data.
       
    Multiprocessing method: do one forecast hour per processor
"""


for forecast_hour in forecasts:

    for fire in range(0,len(fires)):
    #for fire in range(0,4):
        # 1) Get Latitude and Longitude for the indexed large fire [fire]
        
        # No HRRR data for Alaska or Hawaii, so don't do it
        if fires[fire][6] == 'Alaska' or fires[fire][6] == 'Hawaii':
            continue
        
        name = fires[fire][0]   # Fire Name
        s_date = fires[fire][4] # Fire Start Date
        if s_date == 'Not Reported':
            # if start date isn't reported, then set the start date as the reported date
            s_date = fires[fire][3] 
        DATE = datetime.strptime(s_date,'%d-%b-%y') # Fire Start Date
        if DATE < datetime(2016,7,28): #only have forecasts after July 28, 2016       
            DATE = datetime(2016,7,28)
        lat = fires[fire][-3]   # Fire Lat
        lon = fires[fire][-2]   # Fire Lon
        
        print '\n---working on-------------------------'
        print name, s_date, lat, lon, DATE
        print   '--------------------------------------'    
        
        
        # 2) Create a new directory for the fire by name and start date. [FIRE NAME_DD-MMM-YY] 
        #    Include a directory for the forecast hour: f00-f15     
        #    Also create a figure directory for that fire.
        fire_dir = '%s/%s_%s/' % (base_dir,name,s_date)   #the dir of the fire
        out_dir = fire_dir+'%s/' % (forecast_hour) # the dir of the fire with the forecast hour
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)        
            print 'created:',out_dir
        
        fig_dir = fire_dir+'figs/'
        if not os.path.exists(fig_dir):
            os.makedirs(fig_dir)
            print 'created:',fig_dir
        
        
        # 3) Get the MesoWest Stations within a 25 mile radius of the fire
        #   get_mesowest_radius_stations(obrange,lat,lon,radius)
        #   a is a dictionary that includes all the stations names/IDs, lat/lon, and elevation
        # EXTRA ! Only get stations within the times we have, and with the variables we can compare with HRRR        
        start_API = request_date.strftime('%Y%m%d') 
        end_API = datetime.now().strftime('%Y%m%d')
        extraAPI = '&varoperator=or&vars=wind_speed,wind_direction,air_temp,dew_point_temperature'
        a = get_mesowest_radius_stations(start_API+','+end_API,str(lat),str(lon),'25',extra=extraAPI,v=False)
        
        
        stnids = a['STNID']
        print "found",len(stnids),"MesoWest stations"
        
    
        fires_dict[name+'_'+s_date] =   {'stations':a,   # stations within radius of fire defined above
                                         'f_name':name, # fire name                                         
                                         's_DATE':DATE, # fire start date
                                         'f_lat':lat,   # fire latitude
                                         'f_lon':lon}   # fire longitude
        # 5) Get the MesoWest observations for the same time as the HRRR files.
        #    Create a .csv for faster future plotting so we don't have constantly make API calls.
        # --> do a different stnid for each processor
        # Only need to perform this once, we'll do it if forecast_hour == 'f00' and if we have 
        if forecast_hour=='f00' and stnids[0]!=None:
            MW_top_hour_fires = save_MesoWest_tophour(stnids,fire_dir,start_API2,end_API2)

    
    # 4) Get the HRRR for each hour for each station and create a .csv with the data.
    #    fires_dict: Pass in all the station data for every fire so we only have to open the HRRR file up once. (this saves lots of time cuz Pygrib is sloooow)
    #    fire_dir: tell the script where the fire directory is.
    #              Save the map to this file. Append to path to get station and forecast hour.
           
    save_HRRR_MesoWest_point(fires_dict,request_date,forecast_hour,base_dir)
    print "got the HRRR data for MesoWest points in the",name,"fire for",forecast_hour
        
    
    

    
    
    # 6, 7) Calculate Stats, Create a plot of the HRRR versus MesoWest data
    # stnids: a list of station IDs we have HRRR data for and will compare with MesoWest Observations
    # out_dir: the directory the .csv forecast hour was saved with the begining of the file name because '../f01/f01'+'_KSLC.csv'
    #HRRR,MW = plot_ts(stnids[0:3],out_dir+forecast_hour,fig_dir)
    #print "created plots"
    
    

  
###################################################################

## Use multiprocessing to save time
## One processor per forecast time
   
fire_num = range(0,len(fires))


#num_proc = multiprocessing.cpu_count() # use all processors/Count number of processors
#num_proc = 1
#p = multiprocessing.Pool(num_proc)
#p.map(do_the_fire,fire_num)

#do_the_fire()