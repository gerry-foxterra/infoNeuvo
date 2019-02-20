#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        geoJSON_Optometrists.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     06/05/2016
# Modified:    06/05/2016
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from retrieveJSON import *
from businessDemographic import *

logging.basicConfig(filename='logs/geoJSON_Optometrists.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

parms = cgi.FieldStorage()

# For testing as a run-time exe
#parms = {}
#formValues = [(u'title_type', u'Condominium Plan')]

o = Optometrists()

if "_form" in parms:
  formValues = urlparse.parse_qsl(json.loads(parms["_form"].value))
  for key, val in formValues:
    logging.info( key + ": " + str(val))

retrieveJSON(o, parms)
