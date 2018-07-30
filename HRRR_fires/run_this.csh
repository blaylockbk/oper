#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts
# CRON job on Meso4, every hour
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 04/25/2017  First set into operations
#	
#--------------------------------------------------------------------------------------

limit coredumpsize 0

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires"

if (-e ${SCRIPTDIR}/hrrr.status) then
	mail -s "HRRR FIRES Processing: skipping process cycle" blaylockbk@gmail.com <<EOF
	Skipping a HRRR FIRES Processing cycle on meso4: $dateStart
## EOF
	echo "PREVIOUS HRRR FIRES PROCESS ON MESO4 STILL RUNNING"
	#echo "SEE YOU NEXT TIME!"
	exit
endif

touch ${SCRIPTDIR}/hrrr.status

module load python/2.7.3

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/manager.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_fires.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/GOES_image.py

rm -f ${SCRIPTDIR}/hrrr.status

exit
