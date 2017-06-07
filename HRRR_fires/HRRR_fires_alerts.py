# Brian Blaylock
# June 6, 2017

"""
If 10-m wind is greater than 15 m/s, 
    1. Append weather alerts file
    2. Re-generate wx alert page with new data from each alert in the file

# Note: the incomeing winds dictionaries are in units of MPH, need to conver to
#       m/s every time it is used.
"""

import numpy as np

def MPH_to_ms(MPH):
    return MPH*.447
def ms_to_MPH(MS):
    return MS*2.2369

def alert_wind(location, P_wind, P_gust, P_ref):
    """
    Appends the HRRR_fires_alert.txt file with new info
    #
    location - a dictionary consisting of the fire names
    P_wind - a dictionary of HRRR pollywogs 10-m wind for each fire
    P_gust - a dictionary of HRRR pollywogs wind gust for each fire
    P_ref  - a dictionary of HRRR pollywog reflectivity for each fire
    """
    # Open the alert file (we want to append to it)
    myfile = open("/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_fires_alerts.csv", "a")
    # Loop through each observation and check for wind criteria.
    # If it meets the criteria, then append the file with some data.
    for loc in location.keys():
        for i in range(len(P_wind[loc])):
            if P_wind[loc][i] > ms_to_MPH(15):
                write_this = P_wind['DATETIME'][i].strftime('%Y-%m-%d_%H%M')+','
                write_this += loc +','
                write_this += location[loc]['state'] +','
                write_this += '%s,' % location[loc]['area']
                write_this += '%.2f,' % P_wind[loc][i]
                write_this += '%.2f,' % P_gust[loc][i]
                write_this += '%.2f,' % P_ref[loc][i]
                anlys_date = P_wind['DATETIME'][0]
                write_this += "%04d%02d%02d/hrrr.t%02dz.wrfsfcf%02d.grib2," % (anlys_date.year, anlys_date.month, anlys_date.day, anlys_date.hour, i)
                write_this += '%.2f,' % location[loc]['latitude']
                write_this += '%.2f' % location[loc]['longitude']
                write_this += '\n'
                myfile.write(write_this)
    myfile.close()

def write_alerts_html():
    alerts = np.genfromtxt('/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/HRRR_fires_alerts.csv', dtype=None, delimiter=',', names=True)
    html = """
    <html>
    <head>
    <title>HRRR Fires</title>
    <link rel="stylesheet" href="./css/brian_style.css" />
    <script src="./js/site/siteopen.js"></script>
    </head>
    <body>
    <a name="TOP"></a>
    <script src="./js/site/sitemenu.js"></script>	
    <h1 align="center"><i class="fa fa-free-code-camp" aria-hidden="true"></i> HRRR Fires Alert</h1>
    <center>
    <div id="container" style="max-width:900px">
    <h3>HRRR 10m wind >15 m/s</h3>
    <table class="table sortable">
    <tr><th>Valid DateTime</th> <th>Forecast Hour</th> <th>Fire</th> <th>State</th> <th>Size (acres)</th> <th>10m Wind (ms-1)</th> <th>Surface Gust (ms-1)</th> <th>Composite Reflectivity (dBZ)</th> <th>Download Grib2 CONUS File*</th><th>View Area Snapshot</th></tr>"""
    for a in alerts:
        html += "<tr><td>%s</td>" % a[0]
        html += "<td>%s</td>" % a[7][25:28]
        html += "<td>%s</td>" % a[1]
        html += "<td>%s</td>" % a[2]
        html += "<td>%s</td>" % '{:,}'.format(a[3])
        html += "<td>%.1f</td>" % MPH_to_ms(a[4])
        html += "<td>%.1f</td>" % MPH_to_ms(a[5])
        html += "<td>%.1f</td>" % a[6]
        html += "<td><a class='btn btn-default' role='button' href='http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_sample_fire.cgi?model=hrrr&validdate=%s&name=%s&fxx=%s&lat=%s&lon=%s' target='_blank'><i class='fa fa-picture-o' aria-hidden='true'></i> Sample</a></td>" % (a[0], a[1], a[7][26:28], a[8], a[9])
        html += "<td><a class='btn btn-default' role='button' href='https://pando-rgw01.chpc.utah.edu/HRRR/oper/sfc/%s' target='_blank'><i class='fa fa-download' aria-hidden='true'></i> GRIB2</a></td></tr>" % a[7]
    html += """
    </table>
    <center>
    <p>*Note: Grib2 files are available for download on Pando archive one day after HRRR run time.
    </div>
    </center>
    <script src="./js/site/siteclose.js"></script>
    </body>
    </html>"""
    save_here = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/hrrr_fires_alert.html'
    page = open(save_here, "w")
    page.write(html)
    page.close()

