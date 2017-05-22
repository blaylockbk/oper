#!/bin/csh
#
#-----------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point analylses for prveious 3 days 
# CRON job on Meso4, every morning at 1:00 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Updates:
#	bkb: 05/19/2017  First set into operations
#	
#-----------------------------------------------------------------------------

limit coredumpsize 0

module load python/2.7.3
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_anlys/HRRR_anlys.py
exit
