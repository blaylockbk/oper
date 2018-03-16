#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts 90-day mean bias and RSME
# CRON job on Meso4, once a month
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 03/15/2018  First set into operations
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_90day_bias/

module load python/2.7.3
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_90day_bias/HRRR_average_error_over_period.py
exit
