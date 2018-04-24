#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts
# CRON job on Meso4, every hour
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 04/23/2018  First set into operations
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_yesterday/

module load python/2.7.11
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_yesterday/plot_yesterday.py
exit
