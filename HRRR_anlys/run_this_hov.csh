#!/bin/csh
#
#-----------------------------------------------------------------------------
# Run the Python Script for plotting past HRRR forecasts for the defined
# locations.
# - HRRR_hovmoller.py - previous 2 days, colormesh all forecast versus valid time.
#
# CRON job on Meso4, every morning at 1:00 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Updates:
#	bkb: 05/19/2017  First set into operations
#	
#-----------------------------------------------------------------------------

limit coredumpsize 0

module load python/2.7.11

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_hovmoller.py

exit
