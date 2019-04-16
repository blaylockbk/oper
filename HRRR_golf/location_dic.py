# Brian Blaylock
# February 15, 2018

"""
Return a dictionary of the locations of interest
"""

import time
daylight = time.daylight # If daylight is on (1) then subtract from timezone.

location = {'Oaks': {'latitude':40.084,
                    'longitude':-111.598,
                    'name':'Spanish Oaks Golf Course',
                    'timezone': 7-daylight,        # Timezone offset from UTC
                    'is MesoWest': False},         # Is the Key a MesoWest ID?
            'UKBKB': {'latitude':40.09867,
                    'longitude':-111.62767,
                    'name':'Spanish Fork Bench',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'KSLC':{'latitude':40.77069,
                    'longitude':-111.96503,
                    'name':'Salt Lake International Airport',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'WBB':{'latitude':40.76623,
                'longitude':-111.84755,
                'name':'William Browning Building',
                'timezone': 7-daylight,
                'is MesoWest': True},
            'FREUT':{'latitude':41.15461,
                    'longitude':-112.32998,
                    'name':'Fremont Island - Miller Hill',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'HATUT':{'latitude':41.07073,
                     'longitude':-112.58621 ,
                     'name':'Hat Island',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'GNI':{'latitude':41.33216,
                'longitude':-112.85432,
                'name':'Gunnison Island',
                'timezone': 7-daylight,
                'is MesoWest': True},
            'NAA':{'latitude':40.71152,
                'longitude':-112.01448,
                'name':'Neil Armstrong Academy',
                'timezone': 7-daylight,
                'is MesoWest': True},
            'UtahLake':{'latitude':40.159,
                        'longitude':-111.778,
                        'name':'Utah Lake',
                        'timezone': 7-daylight,
                        'is MesoWest': False},
            'UTPKL':{'latitude':40.98985,
                    'longitude':-111.90130,
                    'name':'Lagoon (UTPKL)',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'Orderville':{'latitude':37.276,
                        'longitude':-112.638,
                        'name':'Orderville',
                        'timezone': 7-daylight,
                        'is MesoWest': False},
            'BFLAT':{'latitude':40.784,
                    'longitude':-113.829,
                    'name':'Bonneville Salt Flats',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'UFD09':{'latitude':40.925,
                    'longitude':-112.159,
                    'name':'Antelope Island',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'C8635':{'latitude':41.11112,
                    'longitude':-111.96229,
                    'name':'Hill Air Force Base (CW8635)',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'FPS':{'latitude':40.45689,
                'longitude':-111.90483,
                'name':'Flight Park South',
                'timezone': 7-daylight,
                'is MesoWest': True},
            'EYSC':{'latitude':40.24715,
                    'longitude':-111.65001,
                    'name':'Brigham Young University',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            'UCC23':{'latitude':41.7665,
                    'longitude':-111.8105,
                    'name':'North Logan',
                    'timezone': 7-daylight,
                    'is MesoWest': True},
            #'KIDA':{'latitude':43.52083,
            #        'longitude':-112.06611,
            #        'name':'Idaho Falls',
            #        'timezone': 7-daylight,
            #        'is MesoWest': True},
            'ALT':{'latitude':40.571,
                'longitude':-111.631,
                'name':'Alta Top',
                'timezone': 7-daylight,
                'is MesoWest': True},
            'SND':{'latitude':40.368386,
                'longitude':-111.593964,
                'name':'Sundance Summit',
                'timezone': 7-daylight,
                'is MesoWest': True},
            #'RACM4':{'latitude':46.358056,
            #         'longitude':-84.803889,
            #         'name':'Raco, Michigan',
            #         'timezone': 5-daylight,
            #         'is MesoWest': True},
            'EPMU1':{'latitude':39.36798,
                     'longitude':-111.57803,
                     'name':'Ephraim',
                     'timezone': 7-daylight,
                     'is MesoWest': True},
            'KCNY':{'latitude':38.760,
                    'longitude':-109.745 ,
                    'name':'Moab, Canyonlands Field',
                    'timezone': 7-daylight,
                    'is MesoWest': True},    
        } 

def get_all():
   return location
