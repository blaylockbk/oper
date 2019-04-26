#!/bin/csh
#
#--------------------------------------------------------------------------------------
# Run the Python Script for plotting HRRR point forecasts
# CRON job on meso4, every hour
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 04/25/2017  First set into operations
#	bkb: 04/26/2019  Set a catch in case the previous process is running
#--------------------------------------------------------------------------------------

set dateStart = `date +%Y-%m-%d_%H:%M`

setenv SCRIPTDIR "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_golf/"

if (-e ${SCRIPTDIR}/hrrr_golf.status) then
	echo "$dateStart PREVIOUS HRRR GOLF PROCESS ON MESO4 STILL RUNNING" | mail -s "HRRR GOLF ERROR: Attempt to restart" blaylockbk@gmail.com
	echo "Attempt to kill old processes that fail"
	pkill -f ${SCRIPTDIR}/HRRR_golf.py
	rm -f ${SCRIPTDIR}/hrrr_golf.status
	echo "Restart downloads"
endif

touch ${SCRIPTDIR}/hrrr_golf.status

limit coredumpsize 0

cd /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_golf/

module load bbanaconda3
python /uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_golf/HRRR_golf.py

echo Begin: $dateStart
echo End:   `date +%Y-%m-%d_%H:%M`

rm -f ${SCRIPTDIR}/hrrr_golf.status

exit
