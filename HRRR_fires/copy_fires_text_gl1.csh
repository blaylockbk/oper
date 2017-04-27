#!/bin/csh
#
#
# Before we can do all the HRRR stuff we need to copy the fire list from gl1 to my space
# Then we can run my stuff on meso3 or meso4
#--------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 08/10/2016  First set into operations
#	bkb: 08/29/2016  Moved CRONTAB to gl1
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0
#

# Copy the fires list to the oper/HRRR_fires directory
#     Note: Must run on gl1 because that is where the file is located

echo "hi, i'm working"

set today = `date -u +%Y-%m-%d`
echo $today

#rm -f /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt
cp -v /uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/large_fire.txt /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire_{$today}.txt

chmod 664 /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire_{$today}.txt
    
exit
