# Brian Blaylock
# May 11, 2017                          My roommate Jake moved to Boise today

"""
Email a weather warning when criteria is met at a particular station
"""
import numpy as np
import smtplib
from datetime import datetime, timedelta

def wind_warning(location, P_wind, warn_stn):
    """
    l is the locaitons dictionary (contains timezone info)
    pollywog is the pollywog dictionary returned from get_hrrr_pollywog_multi
    warn_stn is the station ID you want the warning for
    """
    # Check for extreame values and send email alert
    warn_wind = 25
    if np.nanmax(P_wind[warn_stn]) >= warn_wind:
        """
        send an email with details from pollywog
        """
        # Send the Email
        sender = 'brian.blaylock@utah.edu'
        if warn_stn == 'UKBKB':
            receivers = ['blaylockbk@gmail.com', 'blaylock@sfcn.org']
        else:
            receivers = ['blaylockbk@gmail.com']
        subject = 'HRRR Weather Alert: High Winds for ' + warn_stn
        msg_header = "From: " + sender + "\n" + \
                    "To: " + ','.join(receivers) + "\n" + \
                    "Subject: " + subject + "\n\n"
        msg = "Extreme Wind Speeds Forecasted in the HRRR at %s\n\n" % warn_stn
        msg += 'Fxx   Date/Time        Wind Speed (MPH)     \n'
        msg += '--------------------------------------------\n'
        for i in range(len(P_wind[warn_stn])):
            if P_wind[warn_stn][i] > warn_wind:
                msg += 'f%02d: %s     %.1f MPH <---\n' % (i, (P_wind['DATETIME'][i]-timedelta(hours=location[warn_stn]['timezone'])).strftime('%d %b %I:%M %p'), P_wind[warn_stn][i])
            else:
                msg += 'f%02d: %s     %.1f MPH\n' % (i, (P_wind['DATETIME'][i]-timedelta(hours=location[warn_stn]['timezone'])).strftime('%d %b %I:%M %p'), P_wind[warn_stn][i])
        message =  msg_header + msg
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            smtpObj.quit()
            print "Successfully sent email"
        except SMTPException:
            print "Error: unable to send email"

def temp_warning(location, P_temp, warn_stn):
    """
    l is the locaitons dictionary (contains timezone info)
    pollywog is the pollywog dictionary returned from get_hrrr_pollywog_multi
    warn_stn is the station ID you want the warning for
    """
    # Check for extreme values and send email alert
    if datetime.now().month in [1, 2, 3, 11, 12]:
        warn_freez = 10
    else:
        warn_freez = 32
    warn_heat = 100
    if np.nanmin(P_temp[warn_stn]) <= warn_freez or np.nanmax(P_temp[warn_stn]) >= warn_heat:
        """
        send an email with details from pollywog
        """
        # Send the Email
        sender = 'brian.blaylock@utah.edu'
        if warn_stn == 'UKBKB':
            receivers = ['blaylockbk@gmail.com', 'blaylock@sfcn.org']
        else:
            receivers = ['blaylockbk@gmail.com']
        subject = 'HRRR Weather Alert: Extreme Temperature for ' + warn_stn
        msg_header = "From: " + sender + "\n" + \
                    "To: " + ','.join(receivers) + "\n" + \
                    "Subject: " + subject + "\n\n"
        msg = "Extreme Temperature Forecasted in the HRRR at %s\n\n" % warn_stn
        msg += 'Fxx   Date/Time        Temperature (F)     \n'
        msg += '-------------------------------------------\n'
        for i in range(len(P_temp[warn_stn])):
            if P_temp[warn_stn][i] <= warn_freez or P_temp[warn_stn][i] >= warn_heat:
                msg += 'f%02d: %s     %.1f F <---\n' % (i, (P_temp['DATETIME'][i]-timedelta(hours=location[warn_stn]['timezone'])).strftime('%d %b %I:%M %p'), P_temp[warn_stn][i])
            else:
                msg += 'f%02d: %s     %.1f F\n' % (i, (P_temp['DATETIME'][i]-timedelta(hours=location[warn_stn]['timezone'])).strftime('%d %b %I:%M %p'), P_temp[warn_stn][i])
        message =  msg_header + msg
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            smtpObj.quit()
            print "Successfully sent email"
        except SMTPException:
            print "Error: unable to send email"
