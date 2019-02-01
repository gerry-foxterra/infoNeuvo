#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        update_layerInfo
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     19/01/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, json
from classInfo import *
from gisUser import *
import logging, datetime

timeNow = str(datetime.datetime.now())[0:19]
logging.basicConfig(filename='logs/update_layerInfo.log', level=logging.INFO)
logging.info("Start " + timeNow)

dataObj = json.load(sys.stdin)
#dataObj = {u'appName': u'Infosight', u'authCode': u'glp1547051798.23', u'userID': u'1', u'objName': u'Apartments:1 bedroom', u'uniqueID': u'2', u'metadata': u'{"color":[0,0,0,0.3],"text":"2 Bedroom","image":"images/blueDot12.png","visible":"true","heatMap":false,"filters":false,"owner":"","locale":"","cssClass":"selectLine","open":false,"id":"2Bedroom","select":false,"group":"Apartments","min":0,"source":"spatial/1Bedroom.json","type":"static","format":"GeoJSON","URL":"","max":"999","legend":"glp.jpg","geometry":"point","imagerySet":"GLP"}'}

logging.info(str(dataObj))
print 'Content-Type: application/json\n\n'

# Ensure the user is logged in
userID = dataObj['userID']
authCode = dataObj['authCode']
logging.info("userID: " + userID + ", authCode: " + authCode)
u = GisUser()
u.filterAuthCode(authCode)
loginOK = False
if u.fetch(userID):
  if u.isLoggedIn():
    loginOK = True
if not loginOK:
  logging.info("*** Error *** User not logged in, userID: " + str(userID))
  print '{"ERROR":"Not logged in"}'
  quit()

msg = ""
o = LayerInfo()
uniqueID = dataObj['uniqueID']
if not o.fetch(uniqueID):
  rtn = '{"status":"ERROR","reason":"Unable to fetch layer for update"}'
  print rtn
  quit()

count = 0
# Always update 'metadata'. Since it is a JSON object and Postgres doesn't handle
# that well when updating with parms the update_layer class must handle the update
# itself.
sMetadata = str(dataObj["metadata"])
sMetadata = sMetadata.replace("'", '"')
metadata = json.loads(sMetadata)
if o.update(uniqueID, "metadata", metadata):
  count += 1
else:
  rtn = '{"status":"ERROR","reason":' + o.errorMsg() + '"}'
  print rtn
  logging.info(o.errorMsg())
  quit()

# Now update everything that is not 'metadata'
if o.objName != dataObj["objName"]:
  if o.update(uniqueID, "objname", dataObj["objName"]):
    count += 1
if o.appName != dataObj["appName"]:
  if o.update(uniqueID, "appname", dataObj["appName"]):
    count += 1
if o.sortID != dataObj["sortID"]:
  if o.update(uniqueID, "sortid", dataObj["sortID"]):
    count += 1

msg = " fields updated"
if count == 1:
  msg = " field updated"
rtn = '{"status":"SUCCESS","message":"' + str(count) + msg + '"}'
print( rtn )
logging.info(rtn)
logging.info("Fields updated: " + str(count))

