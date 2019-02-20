#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        geoJSON_Landuse.py
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
from landUse import *

logging.basicConfig(filename='logs/geoJSON_Landuse.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

parms = cgi.FieldStorage()

# For testing as a run-time exe
#parms = {}
#formValues = [(u'title_type', u'Condominium Plan')]
#logging.info("formValues: " + str(formValues))

o = LandUse()

if "_form" in parms:
  formValues = urlparse.parse_qsl(json.loads(parms["_form"].value))
  landuseCategories = ""
  for key, val in formValues:
    logging.info( key + ": " + str(val))
    if key == "landuse_category":
      if landuseCategories != "":
        landuseCategories += ','
      landuseCategories += "'" + val + "'"

  if landuseCategories != '':
    o.filterCategory(landuseCategories)

retrieveJSON(o, parms)
