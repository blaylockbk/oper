# Brian Blaylock
# May 8, 2017                           Thunderstorms outside right now! :)

"""
This manager builds the webpage to select each fire and removes old fires
"""

from datetime import date, datetime
import numpy as np
import os
import shutil

def remove_old_fires(fires):
    """
    fires is a dictionary. Each key is a fire name.
    We want to remove the directories that are no longer active
    """
    path = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
    dirs = os.listdir(path)
    for D in dirs:
        if D.replace('_', ' ') not in fires.keys():
            # Looks like the fire isn't active anymore
            shutil.rmtree(path+D)

def write_HRRR_fires_HTML(fires):
    """
    fires is a dictionary. Each key is a fire name.
    """

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

<h1 align="center"><i class="fa fa-map-marker" aria-hidden="true"></i> HRRR Point Forecasts</h1>
<center>
<div id="container" style="max-width:450px">
  
<h3>Active Large Fires >1000 Acres</h3>"""

    for F in sorted(fires, key=fires.get(0)):
        html_text += """<a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/%s/photo_viewer_fire.php" class="btn btn-primary btn-lg btn-block">%s, size: %s, start: %s</a>""" % (fires[F]['name'].replace(' ', '_'), fires[F]['name'], fires[F]['area'], fires[F]['start date'])
    html_text += """
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
