#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        login.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     04/04/2016
# Beta:        05-Sep-2017
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from gisUser import *
import cgi
import json
import time

import logging
logging.basicConfig(filename='logs/login.log', level=logging.INFO)
logging.info("Start")

print "Content-Type: text/html\r\n\r\n"

parms = cgi.FieldStorage()
username = parms["username"].value
password = parms["password"].value
logging.info("username: " + username)

#debug
#username = "glp"
#password = "..."

o = GisUser()
if o.isValid(username, password):
  if o.isAdmin():
    if o.login():
      authCode = username + str(time.time())
      o.authCode = authCode.strip()
      o.update(o.uniqueID, "authcode", o.authCode)
      members = o.publicMembers()
      jsn = o.encodeJSON(members)
      print( str(jsn) )
      logging.info(jsn)
      logging.info("SUCCESS:" + o.authCode)
    else:
      jsn = '{"error":"ERROR","reason":"' + o.reason() + '"}'
      print( jsn )
      logging.info( "ERROR: " + o.reason())
  else:
    reason = "ADMIN privileges required for this application."
    jsn = '{"error":"ERROR","reason":"' + reason + '"}'
    print( jsn )
    logging.info( "ERROR: " + reason)
else:
  jsn = '{"error":"ERROR","reason":"' + o.reason() + '"}'
  print( jsn )
  logging.info( "ERROR: " + o.reason())
