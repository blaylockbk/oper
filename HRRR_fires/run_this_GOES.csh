#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting GOES images for each fire
# CRON job on meso4, every hour
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 05/23/2018  First set into operations
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0

module load python/2.7.3

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GOES_image.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GLM_proximity.py

exit
