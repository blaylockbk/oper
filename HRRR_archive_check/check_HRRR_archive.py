## Brian Blaylock

## 5 October 2016

# Check which HRRR data sets are missing from the archive
# 
### Prints tables for one month
### To run, change the month to the desired month, and output the data
### to a file
### python check_HRRR.archive.py > HRRR_archive_2016-mm.txt
### where mm is the month you are running for

import os.path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

base = '/uufs/chpc.utah.edu/common/home/horel-group/archive/'

sDate = datetime(2016,11,1)

# Keep track of missing files
missing_sfc = []
missing_prs = []

month_delta = relativedelta(months=1)
plus_one_month = sDate+month_delta

while sDate < plus_one_month:
    strDate = sDate.strftime('%Y%m%d')
    
    hrrr_dir = base+strDate+'/models/hrrr/'    
    
    hours = range(0,24)
    forecasts = range(0,19)

    print 'Date:', sDate.strftime('%Y-%m-%d')
    print 'sfc  - HRRR surface fields'

    # print a header with the forecast hours: hour | f00 | f01 | f02| ...    
    f_header = ' hour |'    
    for z in forecasts:
        f_header = f_header + ' f%02d |' % (z)
    print f_header
    
    # Now fill in the line for each hour
    for h in hours:
        h_line = '  %02d  |' % (h)
        for f in forecasts:
            sfc_file = hrrr_dir+'hrrr.t%02dz.wrfsfcf%02d.grib2' % (h,f)

            sfc_exist = os.path.isfile(sfc_file)
            if sfc_exist==True:            
                h_line = h_line + ' [X] |'
            else:
                h_line = h_line + ' [ ] |'
                missing_sfc.append(sfc_file)
        print h_line
    
    
    ## Do again for the pressure data
    print '\nprs  - HRRR pressure fields'
   
    # print a header with the forecast hours: hour | f00 | f01 | f02| ...    
    f_header = ' hour |'    
    for z in forecasts:
        f_header = f_header + ' f%02d |' % (z)
    print f_header
    
    # Now fill in the line for each hour
    for h in hours:
        h_line = '  %02d  |' % (h)
        for f in forecasts:
            prs_file = hrrr_dir+'hrrr.t%02dz.wrfprsf%02d.grib2' % (h,f)

            prs_exist = os.path.isfile(prs_file)
            if prs_exist==True:            
                h_line = h_line + ' [X] |'
            else:
                h_line = h_line + ' [ ] |'
                if f < 0:
                    missing_prs.append(prs_file)
        print h_line            
                
    
    sDate = sDate + timedelta(days=1)
    print "\n"
   
   
# Print out missing data files
#print "missing sfc"
#for i in missing_sfc:
#    print i

#print "\nmissing prs"
#for i in missing_prs:
#    print i
