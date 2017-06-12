# Brian Blaylock
# May 8, 2017                           Thunderstorms outside right now! :)

"""
This manager builds the webpage to select each fire and removes old fires
"""

from datetime import date, datetime
import numpy as np
import os
import shutil

import matplotlib.pyplot as plt

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')  #for running on CHPC boxes

from BB_basemap.draw_maps import draw_CONUS_cyl_map

def remove_old_fires(fires):
    """
    fires is a dictionary. Each key is a fire name.
    We want to remove the directories that are no longer active
    """
    path = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
    dirs = os.listdir(path)
    for D in dirs:
        if D != 'firemap.png':
            if D.replace('_', ' ') not in fires.keys():
                # Looks like the fire isn't active anymore
                shutil.rmtree(path+D)

def write_HRRR_fires_HTML():
    """
    fires is a dictionary. Each key is a fire name.
    """
    fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab

    fires = np.genfromtxt(fires_file, names=True, dtype=None, delimiter='\t')
    # 1) Locations (dictionary)
    location = {}
    for F in range(0, len(fires)):
        FIRE = fires[F]
        # 1) Get Latitude and Longitude for the indexed large fire [fire]
        # No HRRR data for Alaska or Hawaii, so don't do it.
        # Also, don't bother running fires less than 1000 acres
        if FIRE[7] < 1000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
            continue
        location[FIRE[0]] = {'latitude': FIRE[10],
                             'longitude': FIRE[11],
                             'name': FIRE[0],
                             'state': FIRE[6],
                             'area': FIRE[7],
                             'start date': FIRE[4],
                             'is MesoWest': False
                            }

    html_text = """
<html>

<head>
<title>HRRR Fires</title>
<link rel="stylesheet" href="./css/brian_style.css" />
<script src="./js/site/siteopen.js"></script>
</head>


<body>
<a name="TOP"></a>
<script src="./js/site/sitemenu.js"></script>	

<h1 align="center"><i class="fa fa-free-code-camp" aria-hidden="true"></i> HRRR Fire Forecasts</h1>
<center>
<div id="container" style="max-width:500px">
  
<h3>Active Fires >1000 Acres <a href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_fires_alert.html" class='btn btn-primary'>Past Wind Events</a></h3>

<table class="table sortable">
<tr><th>Name</th> <th>State</th> <th>Size (acres)</th> <th>Start Date</th></tr>
"""
    for F in sorted(location, key=location.get(0)):
        html_text += """<tr><td><a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/%s/photo_viewer_fire.php" class="btn btn-warning btn-block">%s</a></td>""" % (location[F]['name'].replace(' ', '_'), location[F]['name'])
        html_text += """<td>%s</td> <td>%s</td><td>%s</td></tr>""" % (location[F]['state'], '{:,}'.format(location[F]['area']), location[F]['start date'])
    html_text += """
</table>

<center>
<p><a href="https://fsapps.nwcg.gov/afm/">Active Fire Mapping Program</a>
<p><a href="https://inciweb.nwcg.gov/">Incident Information System</a>
<img src='http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/firemap.png' style="width=100%;max-width:600px">
</center>

</div>
</center>
<script src="./js/site/siteclose.js"></script>
</body>
</html>
"""

    save_here = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/Brian_Blaylock/hrrr_fires.html'
    html = open(save_here, "w")
    html.write(html_text)
    html.close()


def draw_fires_on_map(fires):
    """
    Draw a map of the United States, and mark the large fires, based on size
    """
    plt.figure(100)
    m = draw_CONUS_cyl_map()
    m.arcgisimage(service='World_Shaded_Relief', dpi=500)
    m.drawstates(linewidth=.1)
    m.drawcoastlines(linewidth=.15)
    m.drawcountries(linewidth=.1)
    for F in fires:
        x, y = m(fires[F]['longitude'], fires[F]['latitude'])
        m.scatter(x, y, s=fires[F]['area']/500, c='orangered',edgecolors='none')
        plt.text(x+.5, y+.5, fires[F]['name'], fontsize=10)

    plt.title('Active Fires Larger than 1000 Acres\n%s' % (date.today().strftime('%B %d, %Y')), fontsize=15)

    plt.savefig('/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/firemap.png', bbox_inches="tight")

if __name__ == '__main__':
    write_HRRR_fires_HTML()