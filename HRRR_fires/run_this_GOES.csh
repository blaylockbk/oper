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

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires_GOES/"

if (-e ${SCRIPTDIR}hrrr_fires_GOES.status) then
	echo "$dateStart PREVIOUS HRRR fires_GOES PROCESS ON MESO4 STILL RUNNING" | mail -s "HRRR fires_GOES ERROR: Attempt to restart" blaylockbk@gmail.com
	echo "Attempt to kill old processes that failed"
	pkill -f ${SCRIPTDIR}HRRR_fires_GOES.py
	rm -f ${SCRIPTDIR}hrrr_fires_GOES.status
	echo "Restart downloads"
endif

touch ${SCRIPTDIR}hrrr_fires_GOES.status

module load python/2.7.3

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GOES_image.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GLM_proximity.py

rm -f ${SCRIPTDIR}/hrrr_fires_GOES.status

exit
