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

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires"

if (-e ${SCRIPTDIR}/hrrrGOES.status) then
	mail -s "HRRR FIRES GOES Processing: skipping process cycle" blaylockbk@gmail.com <<EOF
	Skipping a HRRR FIRES GOES Processing cycle on meso4: $dateStart
## EOF
	echo "PREVIOUS HRRR FIRES GOES PROCESS ON MESO4 STILL RUNNING"
	#echo "SEE YOU NEXT TIME!"
	exit
endif

touch ${SCRIPTDIR}/hrrrGOES.status

module load python/2.7.3

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GOES_image.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GLM_proximity.py

rm -f ${SCRIPTDIR}/hrrrGOES.status

exit
