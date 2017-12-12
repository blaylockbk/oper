# Brian Blaylock
# May 8, 2017                           Thunderstorms outside right now! :)

"""
This manager does a few housekeeping tasks.
1. Deletes directories of old fires.
2. Builds the webpage to select forecasts for the current fires.
3. Creates a map of the current fires.
"""

from datetime import date, datetime
import numpy as np
import os
import shutil
import urllib2

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')  #for running on CHPC boxes
from BB_data.active_fires import get_fires
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
<<<<<<< HEAD
    #fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab
    url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % datetime.strftime(date.today(), "%Y-%m-%d")
    text = urllib2.urlopen(url)
    fires = np.genfromtxt(text, names=True, dtype=None, delimiter='\t')
=======
    fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab

    fires = np.genfromtxt(fires_file, names=True, dtype=None, delimiter='\t')
>>>>>>> 82063767f6a12aea5ce995a5b9fbc04123b6a87b
    #fires2 = get_fires()
    # 1) Locations (dictionary)
    location = {}
    for F in range(0, len(fires)):
        FIRE = fires[F]
        # 1) Get Latitude and Longitude for the indexed large fire [fire]
        # No HRRR data for Alaska or Hawaii, so don't do it.
        # Also, don't bother running fires less than 1000 acres or greater than 3 million acres
        if FIRE[7] < 1000 or FIRE[7] > 3000000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
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

<!--===========================================================================
This page is created dynamically in the scirpt /oper/HRRR_fires/manager.py
============================================================================-->

<body>
<a name="TOP"></a>
<script src="./js/site/sitemenu.js"></script>	

<h1 align="center"><i class="fa fa-free-code-camp" aria-hidden="true"></i> HRRR Fire Forecasts</h1>
<center>
<div class="row" id="content">
    <div class=" col-md-1">
    </div>
    <div class=" col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_golf.html" style="width:100%"> <i class="fa fa-map-marker" aria-hidden="true"></i> Point Forecast</a>      
    </div>
    <div class="col-md-2">
<a class='btn btn-danger active' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_fires.html" style="width:100%"><i class="fa fa-free-code-camp" aria-hidden="true"></i> Fires Forecast</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_custom.html" style="width:100%"> <i class="fa fa-map-o" aria-hidden="true"></i> Custom Maps</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrrX-hrrr.cgi" style="width:100%"> <i class="fa fa-map" aria-hidden="true"></i> Compare Maps</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html" style="width:100%"> <i class="fa fa-database" aria-hidden="true"></i> HRRR Archive</a>
    </div>
</div>
</center>

<center>
<div id="container-fluid" style="max-width:1200px">
  
<h3>Active Fires >1000 Acres</h3>

<div class="row">
  <div class="col-md-6">
<table class="table sortable">
<tr><th>Name</th> <th>State</th> <th>Size (acres)</th> <th>Start Date</th></tr>
"""
    for F in sorted(location, key=location.get(0)):      
        button = """
        <div class="btn-group" role="group" aria-label="..." style="padding-bottom:3px">
        <a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/"""+location[F]['name'].replace(' ', '_')+"""/photo_viewer_fire.php" type="button" class="btn btn-warning" style="width:175px"><b>"""+location[F]['name']+"""</b></a>  <div class="btn-group" role="group">
        <button type="button" class="btn btn-warning dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-clock-o" aria-hidden="true"></i>
        <span class="caret"></span>
        </button>
        <ul class="dropdown-menu">
        <li>Other Data/Figures:</li>
        <li><a href="http://home.chpc.utah.edu/~u0553130/PhD/HRRR_fires/"""+location[F]['name'].replace(' ', '_')+"""">More Plots</a></li>
        <li><a href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_fires_alert.cgi?fire="""+location[F]['name']+"""">Past Wind Events</a></li>
        </ul>
        </div>
        </div>"""
        #OLD BUTTON# html_text += """<tr><td><a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/%s/photo_viewer_fire.php" class="btn btn-warning btn-block"><b>%s</b></a></td>""" % (location[F]['name'].replace(' ', '_'), location[F]['name'])
        html_text += """<tr><td>%s</td>""" % (button)
        html_text += """<td>%s</td> <td>%s</td><td>%s</td></tr>""" % (location[F]['state'], '{:,}'.format(int(location[F]['area'])), location[F]['start date'])
    html_text += """
</table>
</div>
  <div class="col-md-6">
<center>
<br><br>
<img src='http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/firemap.png' style="width=100%;max-width:600px">
<br><hr><br>
<<<<<<< HEAD
    <div class="col-md-6">
    <p><a class='btn btn-primary' style='width:100%' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_fires_alert.cgi" >Past Wind Events <i class="far fa-clock"></i></a>
    <p><a class='btn btn-default' style='width:100%' href="https://fsapps.nwcg.gov/afm/" target="_blank">Active Fire Mapping Program <i class="fa fa-external-link-alt"></i></a>
    <p><a class='btn btn-default' style='width:100%' href="https://inciweb.nwcg.gov/" target="_blank">Incident Information System <i class="fa fa-external-link-alt"></i></a>
    <p><a class='btn btn-default' style='width:100%' href="http://rammb-slider.cira.colostate.edu/?sat=goes-16&sec=conus&x=1638&y=3522&z=3&im=12&ts=1&st=0&et=0&speed=200&motion=loop&map=1&lat=0&p%5B0%5D=16&opacity%5B0%5D=1&hidden%5B0%5D=0&pause=20170626150038&slider=-1&hide_controls=0&mouse_draw=0&s=rammb-slider" target="_blank">GOES-16 Viewer <i class="fa fa-external-link-alt"></i></a>
    </div>
    <div class="col-md-6">
    <p><a class='btn btn-default' style='width:100%' href="https://rmgsc.cr.usgs.gov/outgoing/GeoMAC/ActiveFirePerimeters.kml" target="_blank">Active Fire KMZ USGS <i class="fa fa-external-link-alt"></i></a>
    <p><a class='btn btn-default' style='width:100%' href="https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/active-fire-data" target="_blank">Active Fire KMZ EarthData <i class="fa fa-external-link-alt"></i></a>
    <p><a class='btn btn-success' style='width:100%' href="https://rmgsc.cr.usgs.gov/outgoing/GeoMAC/current_year_fire_data/current_year_all_states/" target="_blank">Active Fire Perimeter ShapeFile <i class="fa fa-external-link-alt"></i></a>
    <p><a class='btn btn-success' style='width:100%' href="https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_"""+datetime.strftime(date.today(), "%Y-%m-%d")+""".txt" target="_blank">Active Fire Text <i class="fa fa-external-link-alt"></i></a>
    </div>
=======
<p><a class='btn btn-primary' style='width:250px' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_fires_alert.cgi" >Past Wind Events</a>
<p><a class='btn btn-default' style='width:250px' href="https://fsapps.nwcg.gov/afm/" target="_blank">Active Fire Mapping Program <i class="fa fa-external-link" aria-hidden="true"></i></a>
<p><a class='btn btn-default' style='width:250px' href="https://inciweb.nwcg.gov/" target="_blank">Incident Information System <i class="fa fa-external-link" aria-hidden="true"></i></a>
<p><a class='btn btn-default' style='width:250px' href="http://rammb-slider.cira.colostate.edu/?sat=goes-16&sec=conus&x=1638&y=3522&z=3&im=12&ts=1&st=0&et=0&speed=200&motion=loop&map=1&lat=0&p%5B0%5D=16&opacity%5B0%5D=1&hidden%5B0%5D=0&pause=20170626150038&slider=-1&hide_controls=0&mouse_draw=0&s=rammb-slider" target="_blank">GOES-16 Viewer <i class="fa fa-external-link" aria-hidden="true"></i></a>
<p><a class='btn btn-default' style='width:250px' href="https://rmgsc.cr.usgs.gov/outgoing/GeoMAC/ActiveFirePerimeters.kml" target="_blank">Active Fire KMZ USGS <i class="fa fa-external-link" aria-hidden="true"></i></a>
<p><a class='btn btn-default' style='width:250px' href="https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/active-fire-data" target="_blank">Active Fire KMZ EarthData <i class="fa fa-external-link" aria-hidden="true"></i></a>
<p><a class='btn btn-default' style='width:250px' href="https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_"""+datetime.strftime(date.today(), "%Y-%m-%d")+""".txt" target="_blank">Active Fire Text <i class="fa fa-external-link" aria-hidden="true"></i></a>
>>>>>>> parent of d2e4dd6... updates
</center>
</div>
</div>
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


def draw_fires_on_map():
    """
    Draw a map of the United States, and mark the large fires, based on size
    """
    #fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire.txt' # Operational file: local version copied from the gl1 crontab
    url = 'https://fsapps.nwcg.gov/afm/data/lg_fire/lg_fire_info_%s.txt' % datetime.strftime(date.today(), "%Y-%m-%d")
    text = urllib2.urlopen(url)
    fires = np.genfromtxt(text, names=True, dtype=None, delimiter='\t')
    # 1) Locations (dictionary)
    location = {}
    bot_left_lat  = fires['LAT'][0]
    bot_left_lon  = fires['LONG'][0]
    top_right_lat = fires['LAT'][0]
    top_right_lon = fires['LONG'][0]
    for F in range(0, len(fires)):
        FIRE = fires[F]
        # 1) Get Latitude and Longitude for the indexed large fire [fire]
        # No HRRR data for Alaska or Hawaii, so don't do it.
        # Also, don't bother running fires less than 1000 acres or greater than 3 million acres
        if FIRE[7] < 1000 or FIRE[7] > 3000000 or FIRE[6] == 'Alaska' or FIRE[6] == 'Hawaii':
            continue
        location[FIRE[0]] = {'latitude': FIRE[10],
                             'longitude': FIRE[11],
                             'name': FIRE[0],
                             'state': FIRE[6],
                             'area': FIRE[7],
                             'start date': FIRE[4],
                             'is MesoWest': False
                            }
        bot_left_lat  = np.minimum(bot_left_lat, FIRE[10])
        bot_left_lon  = np.minimum(bot_left_lon, FIRE[11])
        top_right_lat = np.maximum(top_right_lat, FIRE[10])
        top_right_lon = np.maximum(top_right_lon, FIRE[11])

    plt.figure(100)
    #m = draw_CONUS_cyl_map()
    bot_left_lat  -= 1
    bot_left_lon  -= 1
    top_right_lat += 1
    top_right_lon += 2
    print bot_left_lat, bot_left_lon, top_right_lat, top_right_lon
    m = Basemap(resolution='i', projection='cyl', area_thresh=1500,\
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)

    m.arcgisimage(service='World_Shaded_Relief', dpi=1000)
    m.drawstates(linewidth=.1)
    m.drawcoastlines(linewidth=.15)
    m.drawcountries(linewidth=.1)
    for F in location:
        x, y = m(location[F]['longitude'], location[F]['latitude'])
        m.scatter(x, y, s=location[F]['area']/300, c='orangered',edgecolors='none')
        plt.text(x+.1, y+.1, location[F]['name'], fontsize=7)
    plt.xlabel('Updated %s' % datetime.now().strftime('%Y-%B-%d %H:%M MT'), fontsize=7)
    plt.title('Active Fires Larger than 1000 Acres\n%s' % (date.today().strftime('%B %d, %Y')), fontsize=15)

    plt.savefig('/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/firemap.png', bbox_inches="tight")
    return location

if __name__ == '__main__':
    write_HRRR_fires_HTML()
    l = draw_fires_on_map()
    