#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        logout.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     04/04/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from gisUser import *
import cgi

import logging
logging.basicConfig(filename='logs/logout.log', level=logging.INFO)
logging.info("Start")

print "Content-Type: text/html\r\n\r\n"

parms = cgi.FieldStorage()
authCode = parms["authCode"].value

logging.info("authCode: " + authCode)

o = GisUser()
o.isAuthorized(authCode)
o.logout()
print("LOGOUT")
