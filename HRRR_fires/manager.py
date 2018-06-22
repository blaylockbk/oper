# Brian Blaylock
# May 8, 2017                           Thunderstorms outside right now! :)

"""
This manager does a few housekeeping tasks.
1. Deletes directories of old fires.
2. Builds the webpage to select forecasts for the current fires.
3. Creates a map of the current fires.
"""

from datetime import date, datetime, timedelta
import numpy as np
import os
import shutil
import urllib2
import h5py

import matplotlib as mpl
mpl.use('Agg')      # required for CRON job

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')  #for running on CHPC boxes
from BB_data.active_fires import get_fires, get_incidents, download_fire_perimeter_shapefile
from BB_basemap.draw_maps import draw_CONUS_cyl_map
from BB_GOES16.get_ABI import get_GOES16_truecolor, get_GOES16_firetemperature, file_nearest
from BB_GOES16.get_GLM import get_GLM_files_for_ABI, accumulate_GLM

def remove_old_fires(keep_days=5):
    """
    Remove the directories and images for three days ago.
    """
    path = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
    dirs = os.listdir(path)
    days_ago = (datetime.utcnow()-timedelta(days=keep_days)).strftime('%Y-%m-%d')
    if days_ago in dirs:
        shutil.rmtree(path+days_ago)

def write_HRRR_fires_HTML():
    """
    fires is a dictionary. Each key is a fire name.
    """
    # Get a location dictionary of the active fires
    try:  
        location = get_fires()['FIRES']
        print 'Retrieved fires from Active Fire Mapping Program'
    except:  
        location = get_incidents(limit_num=10)
        print 'Retrieved fires from InciWeb'

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

<h1 align="center"><i class="fa fa-fire-extinguisher"></i> HRRR Fire Forecasts</h1>
<center>
<div class="row" id="content">
    <div class=" col-md-1">
    </div>
    <div class=" col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_golf.html" style="width:100%"> <i class="fa fa-map-marker-alt"></i> Point Forecast</a>      
    </div>
    <div class="col-md-2">
<a class='btn btn-danger active' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_fires.html" style="width:100%"><i class="fa fa-fire-extinguisher"></i> Fires Forecast</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_custom.html" style="width:100%"> <i class="far fa-map"></i> Custom Maps</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrrX-hrrr.cgi" style="width:100%"> <i class="fa fa-map"></i> Compare Maps</a>
    </div>
    <div class="col-md-2">
<a class='btn btn-danger' role='button' href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html" style="width:100%"> <i class="fa fa-database"></i> HRRR Archive</a>
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
        <a href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/photo_viewer_fire.cgi?FIRE="""+F.replace(' ', '_')+"""" class="btn btn-warning" style="width:175px"><b><i class="fab fa-gripfire"></i> """+F+"""</b></a>  <div class="btn-group" role="group">
        <!--
        <a class="btn btn-warning dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="far fa-clock"></i>
        <span class="caret"></span>
        </a>
        <ul class="dropdown-menu">
        <li>Other Data/Figures:</li>
        <li><a href="http://home.chpc.utah.edu/~u0553130/PhD/HRRR_fires/"""+F.replace(' ', '_')+"""">More Plots</a></li>
        <li><a href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_fires_alert.cgi?fire="""+F+"""">Past Wind Events</a></li>
        </ul>
        -->
        </div>
        </div>"""
        #OLD BUTTON# html_text += """<tr><td><a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/%s/photo_viewer_fire.php" class="btn btn-warning btn-block"><b>%s</b></a></td>""" % (location[F]['name'].replace(' ', '_'), location[F]['name'])
        html_text += """<tr><td>%s</td>""" % (button)
        html_text += """<td>%s</td> <td>%s</td><td>%s</td></tr>""" % (location[F]['state'], '{:,}'.format(location[F]['area']), location[F]['start date'])
    html_text += """
</table>
</div>
  <div class="col-md-6">
<center>
<br><br>
<img src='http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/firemap.png' style="width=100%;max-width:600px">
<br><hr><br>
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
    # Get a location dictionary of the active fires
    try:  
        location = get_fires()['FIRES']
        print 'Retrieved fires from Active Fire Mapping Program'
    except:  
        location = get_incidents(limit_num=10)
        print 'Retrieved fires from InciWeb'

    ## ---- Lat/Lons ----------------------------------------------------------
    ## ------------------------------------------------------------------------
    h = h5py.File('/uufs/chpc.utah.edu/common/home/horel-group7/Pando/GOES16/goes16_conus_latlon_east.h5', 'r')
    lons = h['longitude'][:]
    lats = h['latitude'][:]

    ABI = file_nearest(datetime.utcnow())

    ## ---- TRUE COLOR --------------------------------------------------------
    ## ------------------------------------------------------------------------
    TC = get_GOES16_truecolor(ABI, only_RGB=False, night_IR=True)
    print 'File date:', TC['DATE']

    ## ---- FIRE TEMPERATURE --------------------------------------------------
    ## ------------------------------------------------------------------------
    FT = get_GOES16_firetemperature(ABI, only_RGB=False)

    ## ---- Geostationary Lightning Mapper ------------------------------------
    ## ------------------------------------------------------------------------
    GLM = accumulate_GLM(get_GLM_files_for_ABI(ABI))

    ## ---- BLEND TRUE COLOR/FIRE TEMPERATURE ---------------------------------
    max_RGB = np.nanmax([FT['rgb_tuple'], TC['rgb_tuple']], axis=0)


    bot_left_lat  = np.min([location[i]['latitude'] for i in location.keys()])
    bot_left_lon  = np.min([location[i]['longitude'] for i in location.keys()])
    top_right_lat  = np.max([location[i]['latitude'] for i in location.keys()])
    top_right_lon  = np.max([location[i]['longitude'] for i in location.keys()])

    plt.figure(100)
    #m = draw_CONUS_cyl_map()
    bot_left_lat  -= 1.5
    bot_left_lon  -= 1.5
    top_right_lat += 1.5
    top_right_lon += 2.5
    print bot_left_lat, bot_left_lon, top_right_lat, top_right_lon
    m = Basemap(resolution='i', projection='cyl', area_thresh=1500,\
        llcrnrlon=bot_left_lon, llcrnrlat=bot_left_lat, \
        urcrnrlon=top_right_lon, urcrnrlat=top_right_lat)

    newmap = m.pcolormesh(lons, lats, TC['TrueColor'][:,:,1],
                          color=max_RGB,
                          zorder=1,
                          latlon=True)
    newmap.set_array(None)
    m.scatter(GLM['longitude'], GLM['latitude'],
              marker='+',
              color='yellow',
              zorder=10,
              latlon=True)

    m.drawmapboundary(fill_color='k', zorder=5)
    m.drawstates(linewidth=.2, zorder=5)
    m.drawcoastlines(linewidth=.25, zorder=5)
    m.drawcountries(linewidth=.2, zorder=5)
    
    for F in location:
        x, y = m(location[F]['longitude'], location[F]['latitude'])
        m.scatter(x, y, s=location[F]['area']/300, c='orangered',edgecolors='none', zorder=10)
        plt.text(x+.1, y+.1, F, fontsize=7, zorder=10)
    plt.xlabel('Updated: %s\nGOES Image: %s' % (datetime.now().strftime('%Y-%B-%d %H:%M MT'), TC['DATE'].strftime('%Y-%B-%d %H:%M UTC')), fontsize=7)
    plt.title('Active Fires Larger than 1000 Acres\n%s' % (date.today().strftime('%B %d, %Y')), fontsize=15)

    plt.savefig('/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/firemap.png', bbox_inches="tight")
    return location

if __name__ == '__main__':
    write_HRRR_fires_HTML()
    l = draw_fires_on_map()
    