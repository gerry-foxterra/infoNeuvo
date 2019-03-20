#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:         insert_layerInfo
# Modified:     09-Jan-2019
# Version:      1.0001
# Purpose:
#
# Author:       Gerald Perkins
#
# Created:      19/01/2019
# Copyright:    (c) Foxterra Systems Ltd. 2017
# Licence:      <your licence>
#-------------------------------------------------------------------------------

import sys, json, datetime
from classInfo import *

import logging
logging.basicConfig(filename='logs/insert_layerInfo.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

parms = json.load(sys.stdin)
#parms = {u'appName': u'Infosight', u'authCode': u'glp1553103419.68', u'userID': u'1', u'sortID': u'1200', u'objName': u'Topo:Historic', u'uniqueID': u'0', u'published': u'Y', u'metadata': u'{"color":"0,0,0,2","text":"Historic Topo","image":"","visible":"false","heatMap":false,"filters":false,"owner":"","locale":"","cssClass":"selectLine","open":false,"select":false,"pop_up":"","zindex":"105","source":"ESRI","minZoom":0,"type":"dynamic","opacity":1,"attribution":"","format":"tileLayer","URL":"https://services.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer","legend":"","geometry":"polygon","imagerySet":"","maxZoom":9999999}'}
logging.info(str(parms))

o = LayerInfo()
members = utilPublicMembers(o)
for mbr in members:
  logging.info(str(mbr[0]))
  if mbr[0] in parms:
    o.__dict__[mbr[0]] = parms[mbr[0]]
sMetadata = str(parms["metadata"])
sMetadata = sMetadata.replace("'", '"')
metadata = json.loads(sMetadata)
o.__dict__["metadata"] = metadata

if not o.insert():
  rtn = '{"status":"ERROR","reason":"Unable to insert layer info."}'
  print (utilJsonContentType())
  print rtn
  quit()

rtn = '{"status":"SUCCESS","message":"New layer info record added"}'
print (utilJsonContentType())
print( rtn )
logging.info(rtn)



