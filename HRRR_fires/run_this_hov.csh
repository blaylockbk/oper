#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts
# CRON job on wx4, every hour
#--------------------------------------------------------------------------------------

limit coredumpsize 0

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

module load python/2.7.11
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_hovmoller_fires.py

exit
