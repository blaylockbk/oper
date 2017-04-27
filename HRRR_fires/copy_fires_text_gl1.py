## Brian Blaylock
## 29 August 2016


# Copy large_fire.txt from gl1 to my oper directory


import shutil
from datetime import datetime

fire_file = '/uufs/chpc.utah.edu/host/gl/oper/mesowest/fire/large_fire.txt'

date = datetime.strftime(datetime.now(),'%Y-%m-%d')

destination = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire_'+date+'.txt'

shutil.copyfile(fire_file,destination)