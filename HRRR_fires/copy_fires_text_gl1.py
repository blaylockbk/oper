## Brian Blaylock
## 29 August 2016


# 1 - Copy large_fire.txt from gl1 to my oper directory
# 2- Copy current fire perimeter from gl1 to oper directory


import shutil
from datetime import datetime

# Copy large fire file to current
fire_file = '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/large_fire.txt'
date = datetime.strftime(datetime.now(),'%Y-%m-%d')
destination = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt'
shutil.copyfile(fire_file,destination)
print "copied Fires text file to ~/oper/HRRR_fires"

# Copy shape file of fire perimeter
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.shp',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.shp')
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.shx',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.shx')
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.dbf',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.dbf')
print "copied Fires perimeter shapefile to ~/oper/HRRR_fires"