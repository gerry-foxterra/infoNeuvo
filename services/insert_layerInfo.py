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
#parms = {u'appName': u'Infosight', u'authCode': u'glp1547068989.42', u'userID': u'1', u'sortID': u'3030', u'objName': u'Apartments:2 bedroom', u'uniqueID': u'0', u'metadata': u'{"color":[0,0,0,0.3],"text":"2 Bedroom","image":"images/blueDot12.png","visible":"true","heatMap":false,"filters":false,"owner":"","locale":"","cssClass":"selectLine","open":false,"id":"","select":false,"group":"Apartments","min":0,"source":"spatial/2Bedroom.json","type":"static","format":"GeoJSON","URL":"","max":"99","legend":"glp.jpg","geometry":"point","imagerySet":"GLP"}'}
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



