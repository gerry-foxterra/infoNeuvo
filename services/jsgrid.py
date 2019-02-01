#-------------------------------------------------------------------------------
# Name:        jsgrid.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     03/05/2017
# Copyright:   (c) Entiro Systems Ltd. 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from util import *
import sys, cgi, json, datetime, urlparse, logging

def jsgrid(o, parms, extraJSON=None):

# 'extraJSON' is optional. If present it is an array of JSON attributes of this
# object that will be returned.

# For testing as a run-time exe
  #refPts = [-114.10575612608396, 51.027146329165305, -114.0279935223242, 51.060603950046044]
  #radius = 1000.0

  refPts = None
  if "_refPts" in parms:
    refPts = json.loads(parms["_refPts"].value)
  radius = 1000.0
  if "_radius" in parms:
    radius = json.loads(parms["_radius"].value)

  logging.info("jsgrid, refPts: " + str(refPts))
  logging.info("jsgrid, radius: " + str(radius))

  polygon = False
  rectangle = False
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

  print (utilJsonContentType())
  print ('{' + o.formatJsonHeader() + ',')

  if not result:
    print( '<tr><td class="warning">No data matches filter criteria</td></tr>' )
    return
  else:
    count = 0

    delim = ''
    print(' "data":[')
    while result:
      count += 1
      print(delim + o.formatJsonRow())
      delim = ','
      if all:
        result = o.fetchNext()
      elif rectangle:
        result = o.withinRectangle(refPts, maxPt)
      elif polygon:
        result = o.withinPolygon(refPts)
      else:
        result = o.withinRadius(refPts, radius)
    print ']'

  if extraJSON is not None:
    for jsn in extraJSON:
      print ',"' + jsn + '":' + json.dumps(getattr(o, jsn))

  print '}'


