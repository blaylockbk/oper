#!/bin/csh
#
#-----------------------------------------------------------------------------
# Run the Python Script for plotting past HRRR forecasts for the defined
# locations.
# - HRRR_hovmoller.py - previous 3 days, color mesh all forecast versus valid time.
# - HRRR_analys.py - previous 2 days time series for analysis, F06, F12, and F18
#
# CRON job on Meso4, every morning at 1:00 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Updates:
#	bkb: 05/19/2017  First set into operations
#	
#-----------------------------------------------------------------------------

limit coredumpsize 0

module load python/2.7.3

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_hovmoller.py

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_anlys.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_anlys.py 6
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_anlys.py 12
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_anlys.py 18

exit
