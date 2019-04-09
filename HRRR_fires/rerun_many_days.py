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

script = 'HRRR_hovmoller_fires.py'

for d in DATES:
    os.system('python %s %s %s %s %s' % (script, d.year, d.month, d.day, d.hour))