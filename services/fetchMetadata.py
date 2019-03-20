#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        fetchMetadata.py
# Purpose:     Retrieve layer and report metadata that is available for the
#              user whose credentials are supplied.
# Author:      Gerald Perkins
#
# Created:     26-Dec-2018
# Copyright:   (c) Foxterra Systems Ltd. 2018
# Licence:
#-------------------------------------------------------------------------------

from gisUser import *
from classInfo import *
from util import *
import sys, cgi, datetime, logging

logging.basicConfig(filename='logs/fetchMetadata.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

# ------------------------------------------------------------------------------
# Parameters:
# autocode - the authcode for the current logged in user
# OR
# username - the username for any user
# password - if present used to validate the user with 'username'.  If 'password'
#            is not present, only 'username' is validated
#
#parms = cgi.FieldStorage()
parms = {"_username":"glp"}
authCode = None
username = None
password = None
isValid = False

u = GisUser()
if "_authCode" in parms:
  authCode = json.loads(parms["_authCode"].value)
  logging.info("authCode: " + authCode)
  isValid = u.isAuthorized(authCode)
elif "_username" in parms:
  #username = json.loads(parms["_username"].value)
  username = "glp"
  logging.info("username: " + username)
  if "_password" in parms:
    logging.info("Password supplied")
    password = json.loads(parms["_password"])
    isValid = u.isValid(username, password)
  else:
    u.filterName(username)
    logging.info("filterName: " + username)
    isValid = u.fetchNext()

if isValid:
  delim = ''
  jsonLayers = '"layers":{'
  jsonReports = '"reports":{'

  delim = ''
  l = LayerInfo()
  l.sqlFilters("uniqueid>0")
  l.filterIsPublished("Y")
  l.sqlOrderBy("sortid")
  more = l.fetchNext()
  while more:
    if l.metadata["owner"] == "" or l.metadata["owner"] in u.rightsTo:
      jsonLayers += delim + l.encodeJSON()
      delim = ','
    more = l.fetchNext()

  delim = ''
  r = ReportInfo()
  i = 0
  for report in r.reports:
    if r.reports[report]['owner'] == "" or r.reports[report]['owner'] in u.rightsTo:
      j = json.dumps(r.reports[report])
      loaded_j = str(json.loads(j))
      loaded_j = loaded_j.replace("u'", '"')
      loaded_j = loaded_j.replace("'", '"')
      jsonReports += delim + '"' + report + '":' + loaded_j
      delim = ','
      i += 1

  print utilJsonContentType()
  print '[{"status":"VALID"},'
  print '{' + jsonLayers + '}},'
  print '{' + jsonReports + '}}]'

else:
  print utilJsonContentType()
  print '[{"status":"INVALID"}]'
