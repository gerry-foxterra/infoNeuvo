#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        retrieveJSON_1 bedroom.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     04/04/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from classInfo import *
import sys, cgi, json, datetime, urlparse, logging

import logging
logging.basicConfig(filename='logs/retrieveJSON_1 bedroom.log', level=logging.INFO)
timeNow = str(datetime.datetime.now())[0:19]
logging.info("Start " + timeNow + " =====================================")

parms = cgi.FieldStorage()
logging.info(str(parms))
formValues = None
if "_form" in parms:
  formValues = urlparse.parse_qsl(json.loads(parms["_form"].value))
  logging.info(str(formValues))

refPts = [0]
if "_refPts" in parms:
  refPts = json.loads(parms["_refPts"].value)
radius = 0
if "_radius" in parms:
  radius = json.loads(parms["_radius"].value)

# For testing as a run-time exe
#formValues = [(u'sar_category', u'235'), (u'sar_category', u'237'), (u'selDisplayMode', u'mothertongue_hotSpots')]
#refPts = [-114.16811014570926,51.03861253172468,-114.14742494978643,51.05113188875475]
#refPts = [-114.056269,51.067446,-114.056117,51.067892,-114.059072,51.091692,-114.071496,51.095704,-114.072785,51.096083,-114.077416,51.096927,-114.088243,51.092254,-114.089638,51.091014,-114.093187,51.087035,-114.094722,51.08689,-114.101803,51.09168,-114.10388,51.092245,-114.106304,51.092801,-114.114556,51.095736,-114.094284,51.099624,-114.091554,51.121703,-114.098743,51.125696,-114.101489,51.127258,-114.104518,51.12833,-114.108076,51.131477,-114.110023,51.134572,-114.106904,51.140881,-114.1067,51.141342,-114.097869,51.148597,-114.097298,51.148809,-114.083917,51.146066,-114.075382,51.150734,-114.070185,51.156563,-114.069774,51.157092,-114.06963,51.157106,-114.069577,51.157111,-114.065804,51.155283,-114.060853,51.154465,-114.055738,51.151676,-114.033333,51.154382,-114.024941,51.158003,-114.010307,51.15903,-114.000759,51.17371,-114.00074,51.174183,-114.000724,51.175483,-114.000729,51.176226,-114.000509,51.176221,-114.000488,51.175472,-114.000502,51.174142,-114.000511,51.173678,-114.001028,51.168115,-113.998,51.154329,-113.995426,51.139531,-114.001663,51.137502,-114.007652,51.136561,-114.015524,51.133851,-114.015741,51.133743,-114.026244,51.11843,-114.013743,51.100955,-114.000625,51.102395,-114.000311,51.102176,-113.989953,51.096024,-113.98657,51.095349,-113.988544,51.081455,-113.988667,51.081131,-113.990277,51.066812,-114.001317,51.045023,-114.007477,51.037215,-114.017553,51.047124,-114.026207,51.047481,-114.027879,51.047275,-114.03186,51.047489,-114.031989,51.047482,-114.036303,51.048015,-114.038826,51.048831,-114.050806,51.06462,-114.053335,51.065523,-114.056332,51.066999,-114.056269,51.067445]
#radius = float(0)

print "Content-Type: application/json\r\n\r\n"

# ==============================================================================
# What age categories do we filter on. The val in the list of categories is the
# index in the total array field from postGres
bedroomCount = 0
displayMode = "hotSpots"
for key, val in formValues:
  logging.info( key + ": " + str(val))
  if key == "bedrooms":
    bedroomCount = val

o = LayerInfo()

# ==============================================================================
# Go thru all the intersected geographies

circle = False
polygon = False
rectangle = False
all = False
if len(refPts) == 2:
  circle = True
  result = o.fractionIntersectRadius(refPts, radius)
elif len(refPts) == 4:
  rectangle = True
  result = o.fractionIntersectRectangle(refPts)
elif len(refPts) > 4:
  polygon = True
  result = o.fractionIntersectPolygon(refPts)
else:
  all = True
  result = o.fetchNext()

print utilJsonHeader()
while result:
  # Do our business here
  pass
  if all:
    result = o.fetchNext()
  elif polygon:
    result = o.fractionIntersectPolygon(refPts)
  elif rectangle:
    result = o.fractionIntersectRectangle(refPts)
  else:
    result = o.fractionIntersectRadius(refPts, radius)

print utilJsonFooter()
