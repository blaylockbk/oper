#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR hovmoller forecasts
# CRON job on wx4, every hour
#--------------------------------------------------------------------------------------

limit coredumpsize 0


set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires"

if (-e ${SCRIPTDIR}/hrrrHOV.status) then
	mail -s "HRRR FIRES HOV Processing: skipping process cycle" blaylockbk@gmail.com <<EOF
	Skipping a HRRR FIRES HOV Processing cycle on meso4: $dateStart
## EOF
	echo "PREVIOUS HRRR FIRES HOV PROCESS ON MESO4 STILL RUNNING"
	#echo "SEE YOU NEXT TIME!"
	exit
endif

touch ${SCRIPTDIR}/hrrrHOV.status

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/

module load python/2.7.11

python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_hovmoller_fires.py
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_hovmoller_fires_redflag.py

rm -f ${SCRIPTDIR}/hrrrHOV.status

exit
