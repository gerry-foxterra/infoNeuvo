#-------------------------------------------------------------------------------
# Name:        landUse
# Purpose:
#
# Author:      GLP
#
# Created:     05-11-2017
# Copyright:   (c) entiro systems 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from feature import *

class LandUse(DataObj):
    def __init__(self):

        self._id = "gid"
        self._tableName = 'landuse'
        self._baseSql = "SELECT gid, locale, idx, lucode, description, short_description," + \
                   "extra_1, extra_2, extra_3, ST_AsText(geom) FROM " + self._tableName
        server = "realestate.resolutefox.com"
        super(LandUse, self).__init__(self._id, self._tableName, self._baseSql, self.populate,
          None, None, None, None, server)
        properties = {"gid":None, "flyover":None, "popup":None}
        self.feature = Feature(self._id, self.db, self._tableName, self._baseSql, properties, MultiPolygon())

        self._order = ( 'luCode', 'shortDescription', 'description', 'extra1', 'extra2', 'extra3'  )
        self._grid = {}
        self._grid['gid'] = {'title': 'gid', 'key':'true','format':'{:.0f}','visible':'false','width':'20', 'csv':'true', 'quoted':'false'}
        self._grid['luCode'] = {'title': 'Lookup Code', 'key':'false','format':'{}','visible':'true','width':'20', 'csv':'true', 'quoted':'true'}
        self._grid['shortDescription'] = {'title': 'Short Desc', 'key':'false','format':'{}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['description'] = {'title': 'Description', 'key':'false','format':'{}','visible':'true','width':'80', 'csv':'true', 'quoted':'true'}
        self._grid['extra1'] = {'title': 'Extra 1', 'key':'false','format':'{}','visible':'false','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['extra2'] = {'title': 'Extra 2', 'key':'false','format':'{}','visible':'false','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['extra3'] = {'title': 'Extra 3', 'key':'false','format':'{}','visible':'false','width':'40', 'csv':'true', 'quoted':'true'}
        self._totals = {}

        self._intersectFraction = None
        self.resetFilters()

    def resetFilters(self): #PRIVATE method
        self._firstTime = True
        self._locale = None
        self._luCode = None
        self._idx = None
        self._categories = None

    def filterLocale(self, theLocale):
      self._locale = theLocale

    def filterLuCodes(self, theLuCodes):
      self._luCode = theLuCodes

    def filterIndices(self, theIndices):
      self._idx = theIndices

    def filterCategory(self, theCategories):
      self._categories = theCategories

    def applyFilters(self):
      if not self._firstTime:
          return
      if self._luCode is not None:
          where = "lucode IN (" + self._luCode + ")"
          self.sqlFilters(where)
          self.feature.sqlFilters(where)
      if self._idx is not None:
          where = "idx IN " + self._idx
          self.sqlFilters(where)
          self.feature.sqlFilters(where)
      if self._locale is not None:
          where = "locale = '" + self._locale + "'"
          self.sqlFilters(where)
          self.feature.sqlFilters(where)
      if self._categories is not None:
          where = "short_description IN (" + self._categories + ")"
          self.sqlFilters(where)
          self.feature.sqlFilters(where)

    def populate(self, result, startIndex=0):
    #
    #   Populate the class.
    #
        i = startIndex;
        self.gid = iNone(result[i])
        self.findID = self.gid
        self.removeID = self.gid
        i += 1
        self.locale = sNone(result[i])
        i += 1
        self.idx = iNone(result[i])
        i += 1
        self.luCode = sNone(result[i])
        i += 1
        self.description = sNone(result[i])
        i += 1
        self.shortDescription = sNone(result[i])
        i += 1
        self.extra1 = sNone(result[i])
        i += 1
        self.extra2 = sNone(result[i])
        i += 1
        self.extra3 = sNone(result[i])
        i += 1

        self.geom = result[i]
        self.feature.geometry = self.feature.geometry.decode(result[i])

        self._lastIndex = i
        self._intersectFraction = Decimal(0.0)

        self.feature.properties['popup'] = "<b>Landuse</b><p>Code: " + str(self.luCode) + \
          "<br>Description: " + self.description
        self.feature.properties['gid'] = self.gid
        self.feature.properties['flyover'] = "LandUse - Code: " + str(self.luCode) + \
          " . . Description: " + self.description

    def insert(self):
        sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT,(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s) )" + \
              "RETURNING gid"
        data = (self.locale, self.idx, self.luCode, self.description, self.shortDescription, self.extra1, \
                self.extra2, self.extra3, self.geom)
        if self.db.execute(sql, data):
            self.uniqueID = self.db.results[0][0]
            return True
        return False

    def deleteByLocale(self, locale):
      sql = "DELETE FROM " + self._tableName + " WHERE locale='" + str(locale) + "'"
      self._sql = sql
      return self.db.execute(sql)

    def encodeJSON(self):
        members = utilPublicMembers(self) # members useful for json export
        return self.encodePointJSON(members)

class LandUsePoint(LandUse):
    def __init__(self):

        super(LandUse, self).__init__()
        properties = {"gid":None, "flyover":None, "popup":None}
        self.feature = Feature(self._id, self.db, self._tableName, self._baseSql, properties, Point())

class LandUseLookup(DataObj):
    def __init__(self, locale=None):

        self._locale = locale
        self._id = "gid"
        self._tableName = 'lu_landuse'

        self._baseSql = "SELECT uniqueid, locale, idx, description, short_description " + \
                   "FROM " + self._tableName
        super(LandUseLookup, self).__init__(self._id, self._tableName, self._baseSql, self.populate)
        properties = {"gid":None, "flyover":None, "popup":None}

        self.sridMaps = { 'NewWest':3157, 'Vancouver':3157, 'Calgary':4326, 'NorthVan':3157, 'WhiteRock':4176,
                          'Surrey':26910 }
        self.recordMaps = {'NewWest': {
          'luCode':1, 'description':0, 'shortDescription':0, 'extra1':-1, 'extra2':-1, 'extra3':-1 },
                           'Calgary': {
          'luCode':6, 'description':10, 'shortDescription':0, 'extra1':7, 'extra2':3, 'extra3':9 },
                           'NorthVan': {
          'luCode':3, 'description':2, 'shortDescription':4, 'extra1':1, 'extra2':-1, 'extra3':-1 },
                           'WhiteRock': {
          'luCode':9, 'description':6, 'shortDescription':10, 'extra1':6, 'extra2':2, 'extra3':7 },
                           'Surrey': {
          'luCode':0, 'description':1, 'shortDescription':1, 'extra1':2, 'extra2':3, 'extra3':7 },
                           'Vancouver': {
          'luCode':0, 'description':1, 'shortDescription':1, 'extra1':-1, 'extra2':-1, 'extra3':-1 }
        }
        self.resetFilters()

    def resetFilters(self): #PRIVATE method
        self._firstTime = True
        self._selectLocale = None

    def filterLocale(self, theLocale):
      self._selectLocale = theLocale

    def applyFilters(self):
      if not self._firstTime:
          return
      if self._selectLocale is not None:
          where = "locale = '" + self._selectLocale + "'"
          self.sqlFilters(where)

    def populate(self, result, startIndex=0):
    #
    #   Populate the class.
    #
        i = startIndex;
        self.uniqueID = iNone(result[i])
        i += 1
        self.locale = sNone(result[i])
        i += 1
        self.idx = iNone(result[i])
        i += 1
        self.description = sNone(result[i])
        i += 1
        self.shortDescription = sNone(result[i])

        self._lastIndex = i
        self._intersectFraction = Decimal(0.0)

    def insert(self):
        sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT,(%s),(%s),(%s),(%s))" + \
                " RETURNING uniqueid"
        data = (self.locale, self.idx, self.description, self.shortDescription)
        if self.db.execute(sql, data):
            self.uniqueID = self.db.results[0][0]
            return True
        return False

    def deleteByLocale(self, locale):
      sql = "DELETE FROM " + self._tableName + " WHERE locale='" + str(locale) + "'"
      self._sql = sql
      return self.db.execute(sql)

# ==============================================================================
# === Locale Mappings ==========================================================
# ==============================================================================

    def recordMap(self, locale):
      return self.recordMaps[locale]

    def sridMap(self, locale):
      return self.sridMaps[locale]

