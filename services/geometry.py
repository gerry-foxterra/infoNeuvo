#-------------------------------------------------------------------------------
# Name:        geometry
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     13/01/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

"""
This module is largely based upon the GeoJSON standard as defined at:
  http://geojson.org/geojson-spec.html
"""

class Position(object):
  """
  The Position class contains spatial

  Attributes:
        x - x coordinate
        y - y coordinate
  """
  def __init__(self, x=None, y=None):
    self.x = x
    self.y = y


class Crs(object):
  """
  The Crs class defines the coordinate reference system. The 3 parameters
  define one of the two possible CRS types: 'name' or 'link'.
  See: http://geojson.org/geojson-spec.html#coordinate-reference-system-objects

  Attributes:
        name - if not None, the name of the CRS of type 'name'
        href - if not None, the URI to the CRS
        type - if not None, hints at format options for 'href'
  """
  def __init__(self, name=None, href=None, type=None):
    self.name = name
    self.href = href
    self.type = type

class Point(object):
  def __init__(self, x=None, y=None):
    self.position = Position(x, y)
    self.text = None

#POINT(-114.070941 51.047071)

  def decode(self, text=None):
    if text is None:
      return None

    self.text = text
    bfr = self.text[6:len(self.text)-1]
    ll = bfr.split()
    self.position.x = float(ll[0])
    self.position.y = float(ll[1])
    return self

  def encode(self):
    if self.position is None:
      return ""
    return "POINT({0:.6f} {1:.6f})".format(self.position.x, self.position.y)

#"geometry":{"type":"Point","coordinates":[-114.070941,51.047071]}}
  def encodeJSON(self):
    xy = '{0:.6f},{1:.6f}'.format(self.position.x, self.position.y)
    return '"geometry":{"type":"Point","coordinates":[' + xy + ']}'

  def encodeCsv(self):
    xy = '{0:.6f},{1:.6f}'.format(self.position.x, self.position.y)
    return xy

class MultiPoint(object):
  def __init__(self, positions=None):
    self.positions = positions

class LineString(object):
  # LINESTRING(-118.013129387119 55.3816083250687,-118.115077668567 55.3816017312843)
  def __init__(self, positions=None):
    self.positions = positions

  def decode(self, text=None):
    if text is None:
      return None
    i = str.find(text,"(")
    if i < 0:
      return None
    i += 1
    j = str.find(text,')', i)
    self.positions = positionList(text[i:j-1])
    return self

#{ "type": "LineString",
#    "coordinates": [ [100.0, 0.0], [101.0, 1.0] ] }
  def encodeJSON(self, header=True):
    bfr = ''
    count = 0
    if self.positions is None or len(self.positions) == 0:
      return ""
    if header:
      bfr = '"geometry":{"type":"LineString","coordinates":['
    bfr += encodePoly(self.positions)
    if header:
      bfr += ']}'
    return bfr

class MultiLineString(object):
  # MULTILINESTRING((-118.013129387119 55.3816083250687,-118.115077668567 55.3816017312843))
  def __init__(self, lineStrings=None):
    self.lineStrings = lineStrings;

  def decode(self, text=None):
    if text is None:
      return None
    i = str.find(text, "((")
    if i < 0:
      return None
    i += 1  # Position i at the first LineString
    lineStrings = []
    while str.find(text,"(",i) >= 0:
      j = str.find(text,")", i)
      lineString = LineString()
      oneLineString = lineString.decode(text[i:j+1])
      lineStrings.append(oneLineString)
      i = j + 2
    self.lineStrings = lineStrings
    return self

#"geometry": { "type": "MultiLineString","coordinates": [
#        [ [100.0, 0.0], [101.0, 1.0] ],
#        [ [102.0, 2.0], [103.0, 3.0] ] ]}
  def encodeJSON(self):
    if self.lineStrings is None or len(self.lineStrings) == 0:
      return ""
    bfr = '"geometry":{"type":"MultiLineString","coordinates":['
    lineString = LineString()
    count = 0
    for lineString in self.lineStrings:
      if count > 0:
        bfr += ','
      bfr += lineString.encodeJSON(False)
      count += 1
    return bfr + ']}'

class Polygon(object):
  '''
  POLYGON((-114.187805991 51.0615063440001,-114.187805319 51.0609384110001,-114.187660748 51.0609452010001,-114.18765716 51.0605030640001,-114.187655567
  51.0597846420001,-114.18765537 51.0596958500001,-114.187803687 51.0596956120001,-114.188301872 51.0596953490001,-114.188511079 51.059695068,-114.188818402
  . . .
  51.0647377160001,-114.187809764 51.0647094090001,-114.187805991 51.0615063440001))
  '''
  # A Polygon is made up of a list of outer Positions and zero or more inner Positions which
  # are holes in the polygon
  def __init__(self, outerPosition=None, innerPositions=None):
    self.outerPosition = outerPosition
    self.innerPositions = innerPositions

  def decode(self, text=None):
    if text is None:
      return None
    i = str.find(text,"((")
    if i < 0:
      return None
    i += 2
    j = str.find(text,')', i)
    self.outerPosition = positionList(text[i:j-1])
    # Check for inner positions, ie. a hole
    while text[j:j+1] == "),":    # we have a hole
        i = j + 2
        j = str.find(text,')')
        self.innerPositions.append(positionList(text[i:j-1]))
    return self

  def vertices(self):
    if self.outerPosition is None or len(self.outerPosition) == 0:
      return None
    v = []
    posn = Point()
    firstX = None
    firstY = None
    for posn in self.outerPosition:
      v.append(posn.x)
      v.append(posn.y)
      if firstX is None:
        firstX = posn.x
        firstY = posn.y
    ln = len(v)
    if v[ln-2] != firstX or v[ln-1] != firstY:  # Make sure the polygon is closed
      v.append(firstX)
      v.append(firstY)
    return v

#"geometry": {"type": "Polygon","coordinates": [
# [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ]
  def encodeJSON(self, header=True):
    bfr = ''
    if header:
      bfr = '"geometry":{"type":"Polygon","coordinates":'
    if self.outerPosition is None or len(self.outerPosition) == 0:
      return ""
    bfr += '[' + encodePoly(self.outerPosition)
    if self.innerPositions is not None:
      position = Position()
      count = 0
      for position in self.innerPositions:
        if count > 0:
          bfr += ','
        bfr += '[' + encodePoly(position) + ']'
    bfr += ']'
    if header:
      bfr += '}'
    return bfr

class MultiPolygon(object):
  '''
  MULTIPOLYGON(((-114.187805991 51.0615063440001,-114.187805319 51.0609384110001,-114.187660748 51.0609452010001,-114.18765716 51.0605030640001,-114.187655567
  51.0597846420001,-114.18765537 51.0596958500001,-114.187803687 51.0596956120001,-114.188301872 51.0596953490001,-114.188511079 51.059695068,-114.188818402
  51.0596946550001,-114.189208294 51.059694129,-114.18923981 51.0596940860001,-114.189240832 51.0594016360001,-114.189240559 51.0592436450001,-114.18924034
  . . .
  51.0647377160001,-114.187809764 51.0647094090001,-114.187805991 51.0615063440001)))
  '''
  # A MultiPolygon is a list of one or more Polygons
  def __init__(self, polygons=None):
    self.polygons = polygons

  def decode(self, text=None):
    if text is None:
      return None
    i = str.find(text, "(((")
    if i < 0:
      return None
    i += 1  # Position i at the first Polygon
    polygons = []
    while str.find(text,"((",i) >= 0:
      j = str.find(text,"))", i)
      polygon = Polygon()
      onePolygon = polygon.decode(text[i:j+2])
      polygons.append(onePolygon)
      i = j + 2
    self.polygons = polygons
    return self

#"geometry": {"type": "MultiPolygon","coordinates": [ [
# [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],
# [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ] ]
  def encodeJSON(self):
    if self.polygons is None or len(self.polygons) == 0:
      return ""
    bfr = '"geometry":{"type":"MultiPolygon","coordinates":['
    polygon = Polygon()
    count = 0
    for polygon in self.polygons:
      if count > 0:
        bfr += ','
      bfr += polygon.encodeJSON(False)
      count += 1
    return bfr + ']}'

# =============================================================================
# Utility functions

# Given a buffer containing lon-lat pairs separated by commas, return a list of
# Positions
def positionList(llBfr):
  lls = llBfr.split(',')
  positions = []
  for idx in range(len(lls)):
    ll = lls[idx].split()
    position = Position()
    position.x = float(ll[0])
    position.y = float(ll[1])
    positions.append(position)
  return positions

def encodePoly(llList):
  bfr = '['
  count = 0
  position = Position()
  for position in llList:
    if count > 0:
      bfr += ','
    bfr += '[{0:.6f},{1:.6f}]'.format(position.x, position.y)
    count += 1
  return bfr + ']'



