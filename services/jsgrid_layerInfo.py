#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        jsgrid_layerInfo.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     09/12/2015
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from classInfo import *
from jsgrid import *
import sys, cgi, json, datetime, urlparse

import logging
logging.basicConfig(filename='logs/jsgrid_layerInfo.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

parms = cgi.FieldStorage()
#parms = {"_userID":"glp"}
logging.info(str(parms))

o = LayerInfo()
o.sqlOrderBy("sortid")
jsgrid(o, parms, ["_editOrder","_attributes"])

