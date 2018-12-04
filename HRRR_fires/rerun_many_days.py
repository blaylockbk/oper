# Brian Blaylock
# December 4, 2018

"""
reRun Fires for a range of dates
"""

from datetime import datetime, timedelta
import os

sDATE = datetime(2018, 11, 8)
eDATE = datetime(2018, 11, 10)
hours = (eDATE-sDATE).days * 24
DATES = [sDATE + timedelta(hours=h) for h in range(hours)]

for d in DATES:
    os.system('python HRRR_fires.py %s %s %s %s' % (d.year, d.month, d.day, d.hour))