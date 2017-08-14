## Brian Blaylock
## 29 August 2016

"""
1 - Copy large fire file from web to my oper directory
1 - Copy large_fire.txt from gl1 to my oper directory (broken)
2 - Copy current fire perimeter from gl1 to oper directory

Note: must run on gl1 crontab, becuase that is where the files are located
"""


import shutil
import urllib
from datetime import datetime

# 1. Copy large fire file from web to directory
date = datetime.strftime(datetime.now(), '%Y-%m-%d')
url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % date
urllib.urlretrieve(url, "/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt")
print "copied Fires text file from FSAPPS to ~/oper/HRRR_fires"

"""
# 1. Copy large fire file from gl1 to directory
fire_file = '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/large_fire.txt'
date = datetime.strftime(datetime.now(),'%Y-%m-%d')
destination = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt'
shutil.copyfile(fire_file,destination)

print "copied Fires text file from gl1 to ~/oper/HRRR_fires"
"""

# 2. Copy shape file of fire perimeter from gl1 to directory
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.shp',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.shp')
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.shx',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.shx')
shutil.copyfile('/uufs/chpc.utah.edu/host/gl/data/mapserver/perim/current/perim.dbf',
                '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/perim.dbf')

print "copied Fires perimeter shapefile from gl1 to ~/oper/HRRR_fires"
