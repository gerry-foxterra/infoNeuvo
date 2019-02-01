#-------------------------------------------------------------------------------
# Name:        feature
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     13/01/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
# Last Update: 01-Mar-2016
#-------------------------------------------------------------------------------

import urllib
import urllib2
import json
from dataObj import *
from geometry import  *
from util import *
from gisKeys import *

import logging

class Feature(DataObj):
  """
  The Feature class defines a single spatial feature

  Attributes:
        FID -        feature id
        properties - list of properties attached to this feature
        geometry -   geometry object locating this feature
        geom -       raw data from the geom column
  """

  def __init__(self, id=None, db=None, tableName=None, baseSql=None, properties=None, \
               geometry=None, geom=None):
    self._id = id
    self.db = db
    self._tableName = tableName
    self._baseSql = baseSql
    self.properties = properties
    self.geometry = geometry      # geometry object, eg. Point()
    self.geom = geom              # geom value from PostGIS
    self._firstTime = True;
    self._sqlFilter = ""
    self._sqlExtension = ""
    self._sqlOrderBy = ""
    self._sqlJoin = ""
    self._sqlAndOr = " AND "
    self._srid = None
    self._gid = "gid"

  """
  PUBLIC method. Called by classes that have a 'feature'.
    This method requires the `childGeom` for the current instantiation of the
    object. This should be available as object.feature.geom after an object.fetch()
  """
  def centroid(self, childGeom):
    sql = "SELECT ST_AsText(ST_Centroid('" + childGeom + "'))"
    result = self.db.execute(sql)
    if not result:
      return False
    result = self.db.getNextRow()
    if result:
      return result[0];
    return false

  def pointWithin(self, childGeom):
    sql = "SELECT ST_AsText(ST_PointOnSurface('" + childGeom + "'))"
    result = self.db.execute(sql)
    # print sql
    if not result:
      return False
    result = self.db.getNextRow()
    if result:
      return result[0];
    return false

  """
  PUBLIC method. Called by classes that have a 'feature'.
    This method requires the Point `childGeom` for the current instantiation of the
    object. This should be available as object.feature.geom after an object.fetch()
  """
  def offset(self, childGeom, meters, degrees):
    sql = "SELECT ST_AsText(ST_Project('" + childGeom + "'," + str(meters) + "," + \
          "radians(" + str(degrees) + ")))"
    result = self.db.execute(sql)
    if not result:
      return False
    result = self.db.getNextRow()
    if result:
      return result[0];
    return false

  """
  PRIVATE method. Called by classes that have a 'feature'.
  """
  def closestPoints(self, refPoint, nPts=None):
    if self._firstTime:
      if nPts is not None:
        limit = " LIMIT " + str(nPts)
      else:
        limit = " LIMIT 1"
      pt = Point(refPoint[0], refPoint[1])

      distanceClause = "ST_Distance(ST_Transform(ST_GeomFromText('" + pt.encode() + \
                       "',4326),2163),ST_Transform(geom,2163))"
      self.sqlExtension("," + distanceClause)
      self.sqlOrderBy(distanceClause)
      filtered = super(Feature,self).filteredSql()
      sql = filtered + limit
      self._sql = sql
      #print sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False

    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    self.sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
    Returns a single polygon that contains 'refPoint'
    (ST_GeomFromText('POINT(1 2)')
  """
  def containsPoint(self, refPoint):
    sqlFilter = "ST_Contains(geom, ST_GeomFromText('POINT(" + \
                str(refPoint[0]) +  " " + str(refPoint[1]) + ")',4326))"
    self.sqlFilters(sqlFilter)
    filtered = super(Feature,self).filteredSql()
    #print filtered
    self._sql = filtered
    result = self.db.execute(filtered)
    if not result:
      #print "feature.py: " + filtered
      return False
    dbRow = self.db.getNextRow()
    if dbRow:
      super(Feature,self).sqlClear()
      return dbRow;
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
    Returns a single polygon that contains 'theText'
  """
  def containsText(self, theText):
    sqlFilter = "ST_Contains(geom, ST_GeomFromText('" + theText + "',4326))"
    self.sqlFilters(sqlFilter)
    filtered = super(Feature,self).filteredSql()
    #print filtered
    self._sql = filtered
    result = self.db.execute(filtered)
    if not result:
      #print "feature.py: " + filtered
      self.sqlClear()
      return False
    dbRow = self.db.getNextRow()
    if dbRow:
      super(Feature,self).sqlClear()
      return dbRow;
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  """
  def withinRadius(self, refPoint, radius, maxRtn=None):
    if self._firstTime:
      if maxRtn is not None:
        limit = " LIMIT " + str(maxRtn)
      else:
        limit = ""
      self.sqlFilters("ST_Distance_Sphere(geom, ST_MakePoint(" + \
                      str(refPoint[0]) +  "," + str(refPoint[1]) + ")) < " + \
                      str(radius))
      filtered = super(Feature,self).filteredSql()
      #print filtered
      sql = filtered + limit
      self._sql = sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    super(Feature,self).sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  """
  def withinRectangle(self, minCorner, maxCorner, maxRtn=None):
    if (self._firstTime):
      if maxRtn is not None:
        limit = " LIMIT " + str(maxRtn)
      else:
        limit = ""
      self.sqlFilters("geom && ST_MakeEnvelope(" + \
                      str(minCorner[0]) +  "," + str(minCorner[1]) + "," + \
                      str(maxCorner[0]) +  "," + str(maxCorner[1]) + ",4326)")
      filtered = super(Feature,self).filteredSql()
      sql = filtered + limit
      self._sql = sql
      #print sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    self.sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  """
  def withinPolygon(self, vertices, maxRtn=None):
    if (self._firstTime):
      if maxRtn is not None:
        limit = " LIMIT " + str(maxRtn)
      else:
        limit = ""
      filter = "ST_Intersects((ST_GeomFromText('POLYGON(("
      n = len(vertices)
      i = 0
      while i < n:
        if i > 0:
          filter += ','
        filter += str(vertices[i]) + " " + str(vertices[i+1])
        i += 2
      filter += "))',4326)),geom)"
      self.sqlFilters(filter)
      filtered = super(Feature,self).filteredSql()
      sql = filtered + limit
      self._sql = sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    self.sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Polygon method.
  """
  # Return each feature which intersects the circle described by the refPoint
  # and radius and the fraction of the feature which is intersected.

  def fractionIntersectRadius(self, refPoint, radius=None, nPts=None):
    #logging.info("fractionIntersectRadius")
    if (self._firstTime):
      limit = ""
      if nPts is not None:
        limit = " LIMIT " + str(nPts)
      # Limit the extent of the query to the radius
      self.sqlFilters("ST_Distance_Sphere(geom, ST_MakePoint(" + \
                      str(refPoint[0]) +  "," + str(refPoint[1]) + ")) < " + \
                      str(radius))
      # Return the fraction of the retrieved polygon which is within the radius
      extension = ",ST_Area(ST_intersection(geom, ST_Buffer(ST_MakePoint(" + \
                  str(refPoint[0]) + "," + str(refPoint[1]) + ")::geography," + \
                  str(radius) + ")))/ST_Area(ST_Transform(geom, utmzone(ST_Centroid(geom)))) as _x"
      self.sqlExtension(extension)
      filtered = super(Feature,self).filteredSql()
      sql = filtered + limit
      self._sql = sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    super(Feature,self).sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Polygon method.
  """
  # Return each feature which intersects the rectangle described by the refPoints
  # and the fraction of the feature which is intersected.

  def fractionIntersectRectangle(self, refPoints, nPts=None):
    if self._firstTime:
      #
      # If refPoints is length 4, the two corners of a rectangle have been
      # passed.  Convert to a line string and build the linestring sql
      #
      if len(refPoints) == 4:
        refPts = [refPoints[0], refPoints[1], refPoints[0], refPoints[3], \
                  refPoints[2], refPoints[3], refPoints[2], refPoints[1], \
                  refPoints[0], refPoints[1]]
      else:
        refPts = refPoints
    else:           # after the first call to fractionIntersectPolygon, everthing
      refPts = []   # has been set up properly for the query.
    return self.fractionIntersectPolygon(refPts, nPts)

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Polygon method.
  """
  # Return each feature which intersects the polygon described by the refPoints
  # and the fraction of the feature which is intersected.

  def fractionIntersectPolygon(self, refPoints, nPts=None):
    #logging.info("fractionIntersectRadius")
    if (self._firstTime):
      limit = ""
      if nPts is not None:
        limit = " LIMIT " + str(nPts)

      #Filter selection area to the polygon
      filter = "ST_Intersects((ST_GeomFromText('POLYGON(("
      n = len(refPoints)
      i = 0
      while i < n:
        if i > 0:
          filter += ','
        filter += str(refPoints[i]) + " " + str(refPoints[i+1])
        i += 2
      filter += "))',4326)),geom)"
      self.sqlFilters(filter)

      # Add clause to return the fraction of the returned object within the selection polygon
      extension = self.sqlExtensionString(refPoints)
      self.sqlExtension(extension)
      filtered = super(Feature,self).filteredSql()
      sql = filtered + limit
      self._sql = sql
      # print sql
      result = self.db.execute(sql)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    super(Feature,self).sqlClear()
    return False

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Build the extension to SQL to return the fraction geometry which is intersected
  by 'refPoints'
  """
  def sqlExtensionString(self, refPoints):
    if len(refPoints) == 2:     # Radius
      extension = ",ST_Area(ST_intersection(geom, ST_Buffer(ST_MakePoint(" + \
                  str(refPoints[0]) + "," + str(refPoints[1]) + ")::geography," + \
                  str(radius) + ")))/ST_Area(ST_Transform(geom, utmzone(ST_Centroid(geom)))) as _x"
      return extension
    elif len(refPoints) == 4:   # Rectangle corners, convert to polygon
      refPts = [refPoints[0], refPoints[1], refPoints[0], refPoints[3], \
                refPoints[2], refPoints[3], refPoints[2], refPoints[1], \
                refPoints[0], refPoints[1]]
    else:                       # Polygon
      refPts = refPoints

    lineString = "LINESTRING("
    delimiter = ','
    count = 0
    for refPt in refPts:
      if count > 0:
        lineString += delimiter
      count += 1
      lineString += str(refPt)
      if delimiter == ',':
        delimiter = ' '
      else:
        delimiter = ','
    lineString += ')'
    extension = ",ST_Area(ST_intersection(ST_Transform(geom, utmzone(ST_Centroid(geom)))," + \
                "ST_Transform(ST_MakePolygon(ST_GeomFromText('" + lineString + \
                "', 4326)), utmzone(ST_Centroid(geom))))) /" + \
                "ST_Area(ST_Transform(geom, utmzone(ST_Centroid(geom)))) AS _x"
    return extension

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Polygon method.
  """
  # Return each feature which intersects the polygon described by the refPoints
  # and the fraction of the feature which is intersected.
  # gidList is a string in the form 123,456,789 which is suitable to concatenate
  # into an INCLUDE( clause.

  def fractionIntersectList(self, gidList, refPts, gidColumnName=None):
    if (self._firstTime):
      if gidColumnName is not None:
        self._gid = gidColumnName
      #Filter selection area to the list of gids
      filter = self._gid + " IN (" + gidList + ")"
      self.sqlFilters(filter)

      # Determine from the number of reference points passed whether the geometry of
      # the select area is a rectangle, polygon or circle
      polygon = False
      rectangle = False
      if len(refPts) == 2:
        radius = True
      elif len(refPts) == 4:
        rectangle = True
      else:
        polygon = True

      # Add clause to return the fraction of the returned object within the selection polygon
      extension = self.sqlExtensionString(refPts)
      self.sqlExtension(extension)
      filtered = super(Feature,self).filteredSql()
      self._sql = filtered
      #print filtered
      result = self.db.execute(filtered)
      self._firstTime = False
      if not result:
        self._firstTime = True
        return False
    dbRow = self.db.getNextRow()
    if dbRow:
      return dbRow;
    self._firstTime = True
    super(Feature,self).sqlClear()
    return False

  """
  Set the geocode engine to either "MapQuest" or "Google"
  """
  def setGeoCoder(self, geoCodeEngine):
    if geoCodeEngine in "MapQuest:Google":
      self._geoCoder = geoCodeEngine
    else:
      self._geoCoder = "Google"

  """
  Called by classes that have a 'feature'.
  Returns a dictionary of {'lat': xx.x, 'lng': xxx.x}
  """
  def geoCode(self, address):
    if self._geoCoder == "MapQuest":
      return self.geoCodeMapQuest(address)
    return self.geoCodeGoogle(address)

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Returns a dictionary of {'lat': xx.x, 'lng': xxx.x}
  """
  def geoCodeGoogle(self, address):
    fullR  = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
             urllib.quote(address) + "&key=" + accessKeys['google']
    logging.info("feature.geoCode Google, fullR: " + fullR)
    r = urllib2.urlopen(fullR)
    data = json.load(r)
    if data['status'] != "ZERO_RESULTS":
      lat = data['results'][0]['geometry']['location']['lat']
      lng = data['results'][0]['geometry']['location']['lng']
    else:
      return None
    latLng = {}
    latLng['lat'] = lat
    latLng['lng'] = lng
    return latLng

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Returns a dictionary of {'lat': xx.x, 'lng': xxx.x}
  """
  def geoCodeMapQuest(self, address):
    fullR = "https://www.mapquestapi.com/geocoding/v1/address?key=" + \
            accessKeys["mapq"] + "&location=" + \
            urllib.quote(address) + "&thumbMaps=false&maxResults=1"
    logging.info("feature.geoCode Mapquest, fullR: " + fullR)
    r = urllib2.urlopen(fullR)
    try:
      data = json.load(r)
      latLng = data["results"][0]["locations"][0]["displayLatLng"]
    except:
      latLng = None
    return latLng

  """
  PRIVATE method. Called by classes that have a 'feature'.
  Returns an address as a string
  """
  def geoCodeFromLL(self, lonLat):
    #http://maps.googleapis.com/maps/api/geocode/json?latlng=44.4647452,7.3553838&sensor=true
    fullR = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + \
            str(lonLat[1]) + "," + str(lonLat[0]) + "&sensor=true"+ "&key=" + accessKeys['google']
    #print fullR
    r = urllib2.urlopen(fullR)
    data = json.load(r)
    address = data["results"][0]["formatted_address"]
    return address

  """
  PUBLIC method. Called by classes that have a 'feature' that wants to generate
  geometry JSON for use by a mapping application
  """
  def encodeJSON(self, returnGeom=True):
    comma = ''
    bfr = '{"type":"Feature","properties":{'
    for key, value in self.properties.iteritems():
      bfr += comma + '"' + key + '":' + str(utilFormat(value))
      comma = ','
    bfr = bfr + '}'
    if returnGeom:
      bfr += ',' + self.geometry.encodeJSON()
    return bfr + '}'

  def geomFromVertices(self, vertices):
    geomType = "POLYGON"
    n = len(vertices)
    if n == 4:  # box
      v = polygonVerticesFromRectangle(vertices)
      n = len(v)
    elif n == 2:
      v = vertices
      geomType = "POINT"
    else:
      v = vertices
    sql = "SELECT ST_GeomFromText('" + geomType + "(("
    i = 0
    while i < n:
      if i > 0:
        sql += ','
      sql += str(v[i]) + " " + str(v[i+1])
      i += 2
    sql += "))',4326)"
    return self.oneFeatureResult(sql)

  def geomFromText(self, text):
    sql = "SELECT ST_GeomFromText('" + text + "')"
    return self.oneFeatureResult(sql)

  def geomFromTextTransformed(self, text, fromSRID, toSRID):
    sql = "SELECT ST_Transform(ST_SetSRID(ST_GeomFromText('" + text + "')," + \
          str(fromSRID) + ")," + str(toSRID) + ")"
    return self.oneFeatureResult(sql)

  def textFromGeom(self, geom=None):
    if geom is None:
      geom = self.geom
    sql = "SELECT ST_AsText('" + geom + "')"
    return self.oneFeatureResult(sql)

  def jsonFromGeom(self, geom=None):
    if geom is None:
      geom = self.geom
    sql = "SELECT ST_AsGeoJSON('" + geom + "')"
    return self.oneFeatureResult(sql)

  def ptFromGeom(self, geom=None):
    # POINT(-12030019.6312391 6454427.02253853)
    ptStr = self.textFromGeom(geom)
    if ptStr:
      return ptStr[7:len(ptStr)-1].split(' ')

  def geomTransform(self, geom, fromSRID, toSRID):
    sql = "SELECT ST_Transform(ST_SetSRID('" + geom + "'," + \
          str(fromSRID) + ")," + str(toSRID) + ")"
    return self.oneFeatureResult(sql)

  def oneFeatureResult(self, sql):
    result = self.db.execute(sql)
    if not result:
      return False
    dbRow = self.db.getNextRow()
    return sNone(dbRow[0])

  def utmZoneFromTextPt(self, textGeom, inputSRID):
    sql = "SELECT utmzone(ST_GeomFromText('" + textGeom + "'," + str(inputSRID) + "))"
    result = self.db.execute(sql)
    if not result:
      return False
    dbRow = self.db.getNextRow()
    return dbRow[0]

# ==============================================================================
# Utilities


def polygonVerticesFromRectangle(refPoints):
  return [refPoints[0], refPoints[1], refPoints[0], refPoints[3], \
          refPoints[2], refPoints[3], refPoints[2], refPoints[1], \
          refPoints[0], refPoints[1]]

def polygonTextFromVertices(vertices):
  n = len(vertices)
  i = 0
  bfr = "POLYGON(("
  while i < n:
    if i > 0:
      bfr += ","
    bfr += str(vertices[i]) + " " + str(vertices[i+1])
    i += 2
  bfr += "))"
  return bfr

def polygonVerticesFromText(theText):
  vertices = []
  text = theText[9:len(theText)-2]
  parts = text.split(',')
  for part in parts:
    xy = part.split(' ')
    vertices.append(float(xy[0]))
    vertices.append(float(xy[1]))
  return vertices

def utilFormat(value, strDelimiter='"'):
    theType = type(value)
    if theType is str:
        if len(value) > 0 and value[0] == '[':
          return value
        return strDelimiter + value.replace("\\","/") + strDelimiter
    if theType is long or type is int:
        return "{0:d}".format(value)
    if theType is float:
        return "{0:.6f}".format(value)
    if theType is Decimal:
        return "{0:.6f}".format(value)
    try:
        return "{0:d}".format(value)
    except:
        pass
    return ""
