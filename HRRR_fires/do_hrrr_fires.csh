#!/bin/csh
#
#
#--------------------------------------------------------------------------------------
# Get HRRR data for each MesoWest station within 25 miles of each major wildfire.
# Perform this function once a day early morning for the previous day.
# 1) create the HRRR tables for each station near each fire.
# 2) get the MesoWest data for each HRRR hour and save.
# 3) create plots of time series and maps of the biases. 
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 08/10/2015  First set into operations
#	
# To Do:
# 1) run python on multi processors for faster processing 
#--------------------------------------------------------------------------------------

limit coredumpsize 0
#


# load a python version that has pygrib
module load python/2.7.3


python ~/oper/HRRR_fires/create_HRRR_table.py

    
exit
