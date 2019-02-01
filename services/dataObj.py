#-------------------------------------------------------------------------------
# Name:        dataObj
# Modified:    15-May-2017
# Version:     1.0003
# Purpose:     Parent class for objects which require database fetch access for
#              both raw data and spatial data elements
#
# Author:      Gerald Perkins
#
# Created:     05/02/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
import string, re, json, functools
from database import *
from util import *

class DataObj(object):
    def __init__(self, id=None, tableName=None, baseSql=None, populate=None, \
                 db=None, admin=None, dbName=None, userName=None):
      if db is None:
        self.db = Database(admin, dbName)
      else:
        self.db = db
      self._id = id
      self._tableName = tableName
      self._baseSql = baseSql
      self._firstTime = True
      self._sqlFilter = ""
      self._sqlJoin = ""
      self._sqlExtension = ""
      self._sqlOrderBy = ""
      self._sqlAndOr = " AND "
      self._srid = None

    def sqlJoin(self, theJoin):
      self._sqlJoin = theJoin

    def baseSql(self, theBaseSql):
      self._baseSql = theBaseSql

    def sqlFilters(self, theFilter):
      if self._sqlFilter == "" and self._baseSql.upper().find("WHERE") < 0:
        self._sqlFilter += " WHERE " + theFilter
      else:
        self._sqlFilter += self._sqlAndOr + theFilter

    def sqlExtension(self, theExtension):
      self._sqlExtension = theExtension

    def sqlOrderBy(self, orderBy):
      self._sqlOrderBy = " ORDER BY " + orderBy

    def sqlAnd(self):
      self._sqlAndOr = " AND "

    def sqlOr(self):
      self._sqlAndOr = " OR "

    def sqlClear(self):
      self._firstTime = True
      self._sqlFilter = ""
      self._sqlExtension = ""
      self._sqlOrderBy = ""
      self._sqlAndOr = " AND "

    def errorLevel(self):
        return self.db.errorLevel

    def errorMsg(self):
        return self.db.errorMsg

    # In case the child class does not have this method
    def applyFilters(self):
        pass

    # In case the child class does not have this method
    def resetFilters(self):
        self._sqlFilter = ""
        pass

    # Get the Postgres data type for each column in a table
    def dataTypes(self, tableName=None):
      if tableName is None:
        tblName = self._tableName
      else:
        tblName = tableName
      sql = "SELECT COLUMN_NAME, data_type FROM information_schema.columns " + \
            "WHERE TABLE_NAME = '" + tblName + "'"
      result = self.db.execute(sql)
      if not result:
        return False
      result = self.db.getNextRow()
      dTypes = {}
      while result:
        dTypes[result[0]] = result[1]
        result = self.db.getNextRow()
      return dTypes

    # Does the object exist in the database for the specified unique id?
    def isLoaded(self, theFID):
        if type(theFID) is str:
          theKey = "'" + str(theFID) + "'"
        else:
          theKey = str(theFID)
        self.sqlFilters(self._id + "=" + theKey)
        filtered = self.filteredSql()
        self._sql = filtered
        result = self.db.execute(self.filteredSql())
        self.sqlClear() # isLoaded only returns a single record - reset for the next fetch
        if not result:
          return False
        return True

#
#   Fetch an object based on it's ID.  Either the exact: ltEqGt = '=',
#   previous: ltEqGt == '<' or the next: ltEqGt == '>'
#
    def fetch(self, theFID, ltEqGt='=', useFilters=False):
        if type(theFID) is str:
          theKey = "'" + str(theFID) + "'"
        else:
          theKey = str(theFID)
        self.sqlFilters(self._id + ltEqGt + theKey)
        if useFilters:
          self.applyFilters()
        if ltEqGt != '=':
          orderBy = self._id
          if ltEqGt == '<':
            orderBy += " DESC"
          self.sqlOrderBy(orderBy + " LIMIT 1")
        filtered = self.filteredSql()
        self._sql = filtered
        #print filtered
        result = self.db.execute(self.filteredSql())
        self.sqlClear() # fetch only returns a single record - reset for the next fetch
        if not result:
          return False
        result = self.db.getNextRow()
        if result:
          self.populate(result)
          return True
        return false

    def fetchNext(self):
    # Fetch all columns, including the spatial component
        if self._firstTime:
          self.applyFilters()
          filtered = self.filteredSql()
          #print filtered
          #logging.info(filtered)
          self._sql = filtered
          result = self.db.execute(filtered)
          if not result:
            return False
          self._firstTime = False

        result = self.db.getNextRow()
        if result:
          self.populate(result)
          return True
        self.sqlClear()
        return False
#
# Update a single parameter for the current object based upon it's ID and
# column name.
#
    def update(self, theID, column, newValue, tableName=None, isArray=False):
      if tableName is None:
        tblName = self._tableName
      else:
        tblName = tableName
      sql = "UPDATE " + tblName + " SET " + column.lower() + "=(%s)" + \
            " WHERE " + self._id + "=(%s)"
      data = (newValue,theID, )
      #logging.info(sql)
      if self.db.execute(sql, data, isArray):
        return True
      return False

#
# Update all changed members of the class.  Updated data passed to this method
# is JSON. The existing data is read from the database.
#
    def updateObj(self, jsonObj, tableName=None):
      if tableName is None:
        tblName = self._tableName
      else:
        tblName = tableName
      count = 0
      dTypes = self.dataTypes(tblName)
      try:
        theID = jsonObj[self._id]
      except:                               # Perhaps self._id is X.id (qualified) as
        self._id = self._id.split('.')[1]   # opposed to the data, which is not qualified
        theID = jsonObj[self._id]
      encoded = self.encodeJSON()
      #print(str(encoded))
      existingObj = json.loads(encoded)
      for key in existingObj:
        key = str(key)
        keyLower = key.lower()
        if keyLower in dTypes and key in jsonObj:
          if "timestamp" in dTypes[keyLower] and len(str(jsonObj[key])) < 16 and len(str(jsonObj[key])) > 9:
            jsonObj[key] += " 00:00:00"
          newVal = self.encodeToType(jsonObj[key], dTypes[keyLower])
          if str(newVal) != str(existingObj[key]):
            logging.info(str(key) + ": " + str(existingObj[key]) + " <> " + str(newVal))
            updateThis = True
            isArray = False
            if "ARRAY" in dTypes[keyLower]:
              updateThis = True
              isArray = True
            if updateThis:
              if self.update(theID, key, jsonObj[key], tblName, isArray):
                self.__dict__[key] = jsonObj[key]   # Update the object itself to the new value
                count += 1
      return count

    def encodeToType(self, val, theType): # Where theType is a database data type
      try:
        if "character" in theType:
          rtnVal = str(val)
        #elif "timestamp" in theType:
        #    rtnVal = val
        elif "int" in theType:
          rtnVal = int(val)
        elif "numeric" in theType:
          rtnVal = float(val)
        elif "bool" in theType:
          rtnVal = str(val)
        elif "ARRAY" in theType:
          # The passed JSON does not reflect the JSON returned from Python for the
          # object returned from the database.  A bit of fiddling around is required.
          # A mess - a better solution could be available but this too considerable
          # time to get running as is
          if str(val) == '':
            return '[]'
          bfr = str(val).replace('[','')
          bfr = bfr.replace(']','')
          bfr = bfr.replace("'","")
          bfr = bfr.replace('"','')
          bfr = bfr.split(',')
          i = 0
          rtnVal = []
          for i in range(len(bfr)):
            rtnVal.append(bfr[i])
        else:
          rtnVal = val
        return rtnVal
      except:
        return None
#
# Delete one record based upon it's id.  If theID is not passed, we assume the object
# is instantiated and use the id of the object.
#
    def delete(self, theID=None):
      if theID is None:
        theID = getattr(self, self._id)
      data = (theID, )
      sql = "DELETE FROM " + self._tableName + " WHERE " + self._id + "=(%s)"
      # logging.info(sql)
      if self.db.execute(sql, data):
        return True
      return False

    def commit(self):
      self.db.execute("COMMIT");

    def filteredSql(self):
      baseSql = self._baseSql
      if self._sqlJoin != "":
        self.sqlFilters(self._sqlJoin)
      if len(self._sqlExtension) > 1:
        # Add one or more retrieval columns to the sql
        baseSql = self._baseSql.replace(" from ", " FROM " )
        baseSql = baseSql.replace(" FROM ", self._sqlExtension + " FROM ")
      if self._srid is None:
        sql = baseSql + self._sqlFilter + self._sqlOrderBy
        return sql
      else:
        # Retrieve a transformed geometry based on the SRID set by transformSRID
        #   ST_AsText(geom)
        #   ST_AsText(ST_Transform(geom,3857))
        i = string.find(baseSql, "ST_AsText(")
        j = string.find(baseSql, ')', i)
        colName = baseSql[i+10:j]
        sql = baseSql[0:i] + "ST_AsText(ST_Transform(" + colName + "," + \
              str(self._srid) + ")" + baseSql[j:] + self._sqlExtension + \
              self._sqlFilter + self._sqlOrderBy
        return sql

    def nextUniqueID(self):
      sql = "SELECT MAX(" + self._id + ")+1 FROM " + self._tableName
      if self.db.execute(sql):
        result = self.db.getNextRow()
      if result:
        return iNone(result[0])
      return 1

    #===========================================================================
    # Spatial queries
    #   Even though these queries are performed in .feature they  are required
    #   in dataObj in order to populate the results and ensure
    #   fields added via _sqlExtension are populated for fields such as
    #   _distance and _intersectFraction
    #
    def closestPoints(self, refPoint, nPts=1):
      self.applyFilters()
      result = self.feature.closestPoints(refPoint, nPts)
      if self.populateResult(result):
        # A distance clause has been added to the base query in the feature class
        # Populate the self._distance attribute for use in reporting
        self._distance = dNone(result[self._lastIndex+1])
        return True
      return False

    def containsPoint(self, refPoint):
      self.applyFilters()
      result = self.feature.containsPoint(refPoint)
      return self.populateResult(result)

    def containsPointGeom(self, childGeom):
      self.applyFilters()
      result = self.feature.containsPointGeom(childGeom)
      return self.populateResult(result)

    def withinRadius(self, refPoint, radius=None, nPts=None):
      self.applyFilters()
      result = self.feature.withinRadius(refPoint, radius, nPts)
      return self.populateResult(result)

    def withinRectangle(self, minCorner, maxCorner, nPts=None):
      self.applyFilters()
      result = self.feature.withinRectangle(minCorner, maxCorner, nPts)
      return self.populateResult(result)

    def withinPolygon(self, vertices, nPts=None):
      self.applyFilters()
      result = self.feature.withinPolygon(vertices, nPts)
      return self.populateResult(result)

    def transformSRID(self, srid):
      self._srid = srid

    def populateResult(self, result):
      if result:
        self.populate(result)
        return True
      return False

    def fractionIntersectRadius(self, refPoint, radius=None, nPts=None):
      self.applyFilters()
      result = self.feature.fractionIntersectRadius(refPoint, radius, nPts)
      return self.returnFraction(result)

    def fractionIntersectRectangle(self, refPoints, nPts=None):
      self.applyFilters()
      result = self.feature.fractionIntersectRectangle(refPoints, nPts)
      return self.returnFraction(result)

    def fractionIntersectPolygon(self, refPoints, nPts=None):
      self.applyFilters()
      result = self.feature.fractionIntersectPolygon(refPoints, nPts)
      return self.returnFraction(result)

    def fractionIntersectList(self, gidList, gidColumnName=None):
      self.applyFilters()
      result = self.feature.fractionIntersectList(gidList, gidColumnName)
      return self.returnFraction(result)

    def returnFraction(self, result):
      if result:
        self.populate(result)
        frac = dNone(result[self._lastIndex+1])
        self._intersectFraction = frac
        return True
      return False

    #===========================================================================
    # Encoding / formatting
    #
    def encodeJSON(self, members=None, braces=True):
        if members is None:
          mbrs = utilPublicMembers(self)
        else:
          mbrs = members
        bfr = ''
        if braces:
          bfr = '{'
        comma = ''
        for mbr in mbrs:
            bfr += comma + '"' + mbr[0] + '":' + str(utilFmat(mbr[1]))
            comma = ','
        if braces:
          bfr += '}'
        return re.sub('[^a-zA-Z0-9 {}"\'.!@#$%^&*()-_=+`]', '', bfr)

    def encodePointJSON(self, members):
        bfr = '{'
        firstOne = True
        for mbr in members:
            if not firstOne:
                bfr += ','
            firstOne = False
            bfr += '"' + mbr[0] + '":' + str(utilFmat(mbr[1]))
        # add the geography, in this case a Point
        bfr += ',"' + 'latitude' + '":' + \
               str(utilFmat(self.feature.geometry.position.y))
        bfr += ',"' + 'longitude' + '":' + \
               str(utilFmat(self.feature.geometry.position.x))
        bfr += '}'
        return re.sub('[^a-zA-Z0-9 {}"\'.!@#$%^&*()-_=+`]', '', bfr)

    def encodeMultiPolyJSON(self, members):
        bfr = '{'
        firstOne = True
        for mbr in members:
            if not firstOne:
                bfr += ','
            firstOne = False
            bfr += '"' + mbr[0] + '":' + str(utilFmat(mbr[1]))
        bfr += '}'
        return re.sub('[^a-zA-Z0-9 {}"\'.!@#$%^&*()-_=+`]', '', bfr)

    def formatTableHeader(self):
        bfr = '<thead><tr>'
        for key in self._order:
          bfr += '<th>' + self._header[key] + '</th>'
        return bfr + '</tr></thead>'

    def formatTableRow(self):
        bfr = '<tr>'
        for key in self._order:
          td = '<td>'
          f = self._format[key]
          val = self.rgetattr(self, key)
          if f == "{}":
            x = f.format(val)
          elif '.' in f:
            x = f.format(float(val))
            if key in self._totals:
              self._totals[key] += float(val)
          elif 'date' in f:
            x = val[0:10]
          elif 'find' in f:
            td = '<td id="f_' + str(val) + '" class="td1" onclick="findOnMap(\'' + str(val) + '\')">'
            x = ''
          elif 'link' in f:
            if len(str(val)) > 0:
              lnk = "Link"
            else:
              lnk = ""
            theLink = str(val)
            if "http:" not in theLink:
              theLink = "http://" + theLink
            td = '<td><a href="' + str(theLink) + '" target="_blank">' + lnk + '</a>'
            x = ''
          bfr += td + str(x) + '</td>'
        return bfr + '</tr>'

    # Allow for dotted (child) objects
    def rgetattr(self, obj, attr):
      return functools.reduce(getattr, [obj]+attr.split('.'))

    def formatTableTotals(self):
        bfr = '<tr>'
        for key in self._order:
          td = '<td>'
          x = ''
          if key in self._totals:
            f = self._format[key]
            if '.' in f:
              x = f.format(float(self._totals[key]))
            else:
              x = f.format(self._totals[key])
          bfr += td + str(x) + '</td>'
        return bfr + '</tr>'

    # Returned contents are compatable with the jsgrid.js jquery plugin
    def formatJsonHeader(self, isMobile=False):
        bfr = '"fields":['
        delim = ''
        for key in self._order:
          name = str(key)
          row = self._grid[name]
          #jsgrid doesn't like dotted names
          bfr += delim + '{"name":"' + name.replace('.','_x_') + '"'
          for rowKey in row:
            if rowKey == 'mobileTitle':
              if isMobile:
                row['title'] = row[rowKey]
                continue
            quote = '"'
            if "~visible~width~csv~quoted".find(rowKey) > 0:
              quote = ''
            # Set 'visible' attribute false if this is a mobile device request
            # and 'not_mobile' is set for this column
            if rowKey == 'visible':
              if row[rowKey] == 'not_mobile':
                if isMobile:
                  row[rowKey] = 'false'
                else:
                  row[rowKey] = 'true'
            bfr += ',"' + rowKey + '":' + quote + row[rowKey] + quote
          #bfr += ',"title":"' + row["title"] + '"'
          bfr += '}'
          delim = ','
        bfr += ']'
        return bfr

    def formatJsonRow(self):
        bfr = '{'
        delim = ''
        for key in self._order:
          row = self._grid[str(key)]
          f = row['format']
          val = self.rgetattr(self, key)
          if type(val) is list:
            x = self.formatOneList(key, val, f)
          else:
            x = self.formatOneValue(key, val, f)
          bfr += delim + '"' + key.replace('.','_x_') + '":' + x
          delim = ','
        return bfr + '}'

    def formatOneValue(self, key, val, f):
          if f == "{}":
            x = '"' + f.format(str(val)) + '"'
          elif 'f}' in f:
            x = '"' + f.format(float(val)) + '"'
            if key in self._totals:
              self._totals[key] += float(val)
          elif 'bool' in f:
            x = str(val).lower()
          elif 'date' in f:
            x = '"' + val[0:10] + '"'
          elif 'json' in f:
            x = json.dumps(val)
          elif 'link' in f:
            if len(str(val)) > 0:
              x = '"<a href=' + str(val) + ' target=_blank>Open</a>"'
            else:
              x = '""'
          elif 'find' in f:
            x = '"' + f.format(val) + '"'
          elif 'remove' in f:
            x = '"' + f.format(val) + '"'
          else:
            x = '"' + f.format(val) + '"'
          return x

    def formatOneList(self, key, val, f):
        lst = '['
        delim = ''
        for v in val:
          lst += delim + self.formatOneValue(key, v, f)
          delim = ','
        return lst + ']'

    # Allow for dotted (child) objects
    def rgetattr(self, obj, attr):
      return functools.reduce(getattr, [obj]+attr.split('.'))

    #===========================================================================
    # Utilities
    #
    def publicMembers(self):
      return utilPublicMembers(self)

    def isCalledBy(self, theCaller):
      stack = inspect.stack()
      if "self" in stack[2][0].f_locals:
        sClass = str(stack[2][0].f_locals["self"].__class__)
        if theCaller in sClass:
          return True
      return False
