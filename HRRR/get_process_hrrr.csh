#!/bin/csh
#
#
#--------------------------------------------------------------------------------------
# Process HRRR data for web visualization. Run every hour at 30 minutes after the hour.
# 1) Convert raw GRIB2 HRRR from horel-group/archive to a NetCDF
# 2) Plot the HRRR 10 m winds with Python and put in a public_html directory
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# Updates:
#	bkb: 10/29/2015  First set into operations
#	
# To Do:
# 1) run python on multi processors for faster processing 
# 2) fix other date time issues
# 3) re-write this scripting process in Python, not cshell
#--------------------------------------------------------------------------------------

limit coredumpsize 0
#
setenv DATA /uufs/chpc.utah.edu/common/home/horel-group/archive
setenv SCRIPTDIR ~/oper/HRRR

# Remove the old HRRR data from the directory
rm -f ~/oper/HRRR/raw_HRRR/*.nc
cd ~


set cyz  = `date -u +%C`
set yrz  = `date -u +%y`
set monz = `date -u +%m`
set dayz = `date -u +%d`
set hrz  = `date -u +%H`
echo $hrz

if ($hrz == 00) then
	@ hrz = 23
	@ dayz = ($dayz - 1)
else
	@ hrz = ($hrz - 1) # compensate hours for what the U actually has archived (about an hour hours delay)
endif
	
if ($hrz<10) then 
	set hrz = 0$hrz
	echo $hrz
endif


echo $hrz

echo $cyz

echo $cyz $yrz $monz $dayz

foreach f ( 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 )
    echo $cyz$yrz$monz${dayz}${hrz} F$f

    # convert grib2 HRRR to NetCDF and store in my directory
    /usr/local/bin/wgrib2 ${DATA}/$cyz$yrz$monz${dayz}/models/hrrr/$cyz$yrz$monz${dayz}${hrz}F${f}hrrr.grib2 -netcdf ~/oper/HRRR/raw_HRRR/$cyz$yrz$monz${dayz}${hrz}F${f}hrrr.nc

    echo ""
    echo Running hrrr_10m_winds.py for $cyz$yrz$monz${dayz}${hrz}F${f}hrrr.nc
    /usr/local/bin/python ${SCRIPTDIR}/hrrr_10m_winds.py $cyz$yrz$monz${dayz}${hrz}F${f}hrrr.nc Local

    end

# When Finished, delete all the raw_hrrr files
rm -f ~/oper/HRRR/raw_HRRR/*.nc
    
exit
