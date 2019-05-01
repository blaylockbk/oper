## Brian Blaylock
## May 1, 2019

"""
Delete old files we don't need. These files are in multiple directories
"""

import os
from datetime import datetime

def remove(DATE):
    for H in range(24):
        BASE = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
        DIRS = BASE + '%s/%02d00/' % (DATE.strftime('%Y-%m-%d'), H)
        try:
            dirs = os.listdir(DIRS)
        except:
            continue

        for d in dirs:
            # This is a list of fires I want to keep
            if d not in ['416', 'BURRO', 'BUZZARD', 'DOLLAR_RIDGE', 'LAKE_CHRISTINE', \
                        'WESTON_PASS', 'TRAIL_MOUNTAIN', 'BALD_MOUNTAIN', 'POLE_CREEK', \
                        'CAMP', 'WOOLSEY']:
                print('rm -r %s%s' % (DIRS, d))
                os.system('rm -r %s%s' % (DIRS, d))

if __name__ == '__main__':
    remove(datetime(2018, 7, 14))