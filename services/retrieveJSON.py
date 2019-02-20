#-------------------------------------------------------------------------------
# Name:        retrieveJSON.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     06/05/2016
# Modified:    06/05/2016
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from util import *
import sys, cgi, json, datetime, urlparse, logging

# Given a spatial object and it's bounding rectangle, polygon or radius,
# print to stdout the JSON formatted features for the passed object

def retrieveJSON(o, parms, includeAttributes=True):

  # For testing as a run-time exe
  #refPts = []
  #refPts = [-113.95978925982492, 51.02191191032259, -113.98553846636788, 51.01003270117797]
  #refPts = [float(-114.07), float(51.046), float(-114.04), float(51.046), float(-113.04), \
  #         float(51.006), float(-114.07), float(51.006), float(-114.07), float(51.046)]
  #refPts = [float(-114.105978), float(51.04313)]
  #radius = float(1000)

  print utilJsonContentType()
  refPts = json.loads(parms["_refPts"].value)
  radius = 0.0
  if "_radius" in parms:
    radius = json.loads(parms["_radius"].value)

  # Assumes logging turned on in calling method
  logging.info("len(refPts): " + str(len(refPts)))
  logging.info("refPts: " + str(refPts))
  logging.info("radius: " + str(radius))

  polygon = False
  rectangle = False
  result = False
  all = False

  ln = 0
  if refPts != None:
    ln = len(refPts)
  if ln < 2:
    result = o.fetchNext()
    all = True
  elif len(refPts) == 2:
    result = o.withinRadius(refPts, radius)
  elif len(refPts) == 4:
    rectangle = True
    maxPt = [float(refPts[2]),float(refPts[3])]
    result = o.withinRectangle(refPts, maxPt)
  else:
    polygon = True
    result = o.withinPolygon(refPts)

  lineCount = 0
  comma = ''
  parent = None
  if includeAttributes:
    parent = o
  if result:
    # GLP Test
    print ('{"formatting":{' + o.formatJsonHeader())
    print ('}, "geoJSON":')
    print utilJsonHeader()
    while result:
      lineCount += 1
      bfr = o.feature.encodeJSON(parent)
      print comma + o.feature.encodeJSON(parent)
      comma = ','
      if all:
        result = o.fetchNext()
      elif rectangle:
        result = o.withinRectangle(refPts, maxPt)
      elif polygon:
        result = o.withinPolygon(refPts)
      else:
        result = o.withinRadius(refPts, radius)
    print utilJsonFooter()
    print '}'
  logging.info("Result count: " + str(lineCount))
  return lineCount
