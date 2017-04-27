#!/bin/csh
#
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting and emailing KSL data daily
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 05/10/2016  First set into operations
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0
#

/uufs/chpc.utah.edu/sys/pkg/python/2.7.3_rhel6/bin/python /uufs/chpc.utah.edu/common/home/u0553130/oper/KSL/plot_KSL_daily.py

rm -f /uufs/chpc.utah.edu/common/home/u0553130/oper/KSL/*.txt
    
exit
