#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        accessKeys.py
# Purpose:
#
# Author:      Jim Vos
#
# Created:     25/01/2016
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import json


jsonS = "Content-Type: application/json\r\n\r\n"

data = {}
data['bing'] = 'AnxrVChMRCXFPFTzjTiVtWMrFepABVo5FeLCWkC4n6eBf40hnNS3aG4HhI0J7iCt'
data['mapq'] = 'ERceFL6NUECjcyuyPeBubNJZT9GEFYEC'
data['mapbox'] = 'sk.eyJ1IjoiZWFybmVzdGIiLCJhIjoiY2pwdm1xY3lvMDJsazN4cGhramEwZzY3dyJ9.Zy3yreQaFtn4UfjHZGxSsQ'
data['google'] = 'AIzaSyAEOPfvvXRv14SXNY74bI9JHekYfSjEx4s'
json_data = json.dumps(data)

print jsonS + json_data
