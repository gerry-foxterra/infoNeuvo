#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        delete_layerInfo
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
logging.basicConfig(filename='logs/delete_layerInfo.log', level=logging.INFO)
logging.info("Start " + timeNow)

dataObj = json.load(sys.stdin)
logging.info(str(dataObj))
#dataObj = {'province': 'AB', 'city': 'Calgary', 'description': '', 'practiceType': 'DENTAL', 'authCode': 'glp1519165111.25', 'address': '1021 Maggie St SE', 'userID': '1', 'contactPerson': 'Gerald Perkins', 'saleOrLease': 'SALE', 'status': 'PENDING', 'FID': '2', 'country': 'Canada', 'pdf': '', 'size': '1111'}
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

theID = dataObj['uniqueID']
logging.info("Layer to delete: " + str(theID))
msg = ""
o = LayerInfo()
o.uniqueID = theID
if o.delete():
  msg = "Layer deleted"
else:
  errMsg = o.errorMsg()
  logging.info(errMsg)
  if "not logged in" in errMsg:
    print '{"ERROR":"Not logged in"}'
  else:
    print '{"ERROR":"' + errMsg + '"}';

logging.info(msg)
rtn = '{"status":"SUCCESS","message":"' + str(count) + msg + '"}'
print rtn