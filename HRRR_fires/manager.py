# Brian Blaylock
# May 8, 2017                           Thunderstorms outside right now! :)

"""
This manager builds the webpage to select each fire and removes old fires
"""

from datetime import date, datetime
import numpy as np
import os
import shutil

# Fires file for current day
get_today = datetime.strftime(date.today(), "%Y-%m-%d")
fires_file = '/uufs/chpc.utah.edu/common/home/u0553130/oper/HRRR_fires/large_fire_'+get_today+'.txt' # Operational file: local version copied from the gl1 crontab
fires = np.genfromtxt(fires_file, names=True, dtype=None,delimiter='\t')

def write_HRRR_fires_HTML():

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
  
<h3>Active Large Fires</h3>"""

    for F in fires:
      html_text += """<a href="http://home.chpc.utah.edu/~u0553130/oper/HRRR_fires/%s/photo_viewer_fire.php" class="btn btn-primary btn-lg btn-block">%s, size: %s, start: %s</a>""" % (F[0].replace(' ', '_'), F[0], F[7], F[4])
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

def remove_old_fires():
    path = '/uufs/chpc.utah.edu/common/home/u0553130/public_html/oper/HRRR_fires/'
    dirs = os.listdir(path)
    for D in dirs:
        if D.replace('_', ' ') not in fires['INAME']:
            shutil.rmtree(path+D)

write_HRRR_fires_HTML()
remove_old_fires()