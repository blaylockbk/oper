## HRRR Forecast Display - Project Golf

My neighborhood friend Dallin Naulu, now the superintendant over grounds at Spanish Oaks Golf Course, inspired me to make a golf weather product using the raw HRRR weather data. Ryan Thurston, another friend and avid wakeboarder, also inspired this project from a earlier project I called "HRRR Wake Finder." These plots displays the point forecast for temperature, humidity, wind, and precipitation from the HRRR model with a pannel showing the simulated radar reflectivity and 10 m wind field for the surrounding area. This product can be used for any location, not just a golf course. I added Utah Lake, Lagoon,and some MesoWest locations of interest.

You can run this code yourself. You'll need some functions from 
my pyKBKB_v2 repository to download HRRR files from NOMADS: https://github.com/blaylockbk/pyBKB_v2

The `./run_this.csh` script is a CRON job set to run 30 minutes after the hour.

Since all the HRRR forecast hours are not avaialble until about 1.5 hours after the analysis time, observed wind data from stations avaiable through MesoWest are shown on the map for analysis hour and forecast hour 1 (f00 and f01). If the location is a MesoWest station, then the observed temperature, dew point, and wind speed is shown as a dashed black line for the first 1.5 hours of the 18 hour time series.

More information about the HRRR model here: https://rapidrefresh.noaa.gov/hrrr/

---------
##### Related Project: HRRR Fires
Same idea, but creates HRRR forecasts figures for point at the current large fires (fires greater than 1000 acres) http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_fires.html
