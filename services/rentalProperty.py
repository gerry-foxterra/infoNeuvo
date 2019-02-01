#-------------------------------------------------------------------------------
# Name:        RentalProperty
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     18/06/2016
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import csv
from classInfo import *
from feature import *
from util import *
import logging
import datetime

class RentalProperty(DataObj):
    """
    Commercial Real Estate class
    """
    def __init__(self):
        self.uniqueID = None
        self.source = None
        self.foreignKey = None
        self.address = None
        self.country = "Canada"
        self.province = None
        self.city = None
        self.postalCode = None
        self.agency = None
        self.title = None
        self.description = None
        self.priceMin = None
        self.priceMax = None
        self.price = None
        self.bedroomDesc = None
        self.bedrooms = None
        self.bathroomDesc = None
        self.bathrooms = None
        self.parkingSpots = None
        self.parkingPrice = None
        self.furnished = None
        self.size = None
        self.petDesc = None
        self.pets = None
        self.status = None
        self.linkToAd = None
        self.linkToImage = None
        self.listingDate = None
        self.latitude = None
        self.longitude = None

        self.meta = ClassInfo()
        self.meta.fetchByClassName('rentalProperty')

        # Required by the parent class - DataObj
        self._id = "uniqueID"
        self._tableName = "rental_properties"
        self._baseSql = "SELECT uniqueID, source, foreignkey, address, country," + \
          "province, city, postalcode, agency, title, description, pricemin, pricemax, "+ \
          "price, bedroomdesc, bedrooms, bathroomdesc, bathrooms, parkingspots, parkingprice, furnished, size, " + \
          "petDesc, pets, status, linktoad, linktoimage, listingdate, latitude, longitude, " + \
          "geom FROM " + self._tableName
        db = Database(False, 'infosight')
        super(RentalProperty, self).__init__(self._id, self._tableName, self._baseSql, self.populate, db)
        properties = {"FID":None, "gid":None, "flyover":None}
        self.feature = Feature(self._id, db, self._tableName, self._baseSql, properties, Point())
        self.resetFilters()

    def db(self):
        return self.db

    def errorLevel(self):
        return self.db.errorLevel

    def errorMsg(self):
        return self.db.errorMsg

    def resetFilters(self): #PRIVATE method
        self._firstTime = True
        self._bedroomFilter = None
        self._furnishedFilter = None

    def filterBedrooms(self, bdrmCounts):         # "for use in an IN clause
        self._bedroomFilter = str(bdrmCounts)     # eg. '3,4'
        if '5' in self._bedroomFilter:            # '5 is 5 or more in dropdown
          self._bedroomFilter += ",6,7,8,9,10"

    def filterFurnished(self, isFurnished):
        self._furnishedFilter = isFurnished

    def applyFilters(self): #PRIVATE method
        if not self._firstTime:
            return
        if self._bedroomFilter is not None:
            where = "bedrooms IN (" + str(self._bedroomFilter) + ")"
            self.sqlFilters(where)
            self.feature.sqlFilters(where)
        if self._furnishedFilter is not None:
            where = "furnished = '" + str(self._furnishedFilter) + "'"
            self.sqlFilters(where)
            self.feature.sqlFilters(where)

    def populate(self, result):
      self.meta.populate(self, result)

    def populate(self, result, isCsv=False, geoCode=False):
    #
    #   populate the class.  To ensure values read from database or csv are
    #   of the right data type, use iNone to force integer and dNone to force
    #   decimal.
    #
        i = 0
        self.uniqueID = iNone(result[i])
        self.FID = self.uniqueID
        self.feature.properties['FID'] = self.FID
        self.feature.properties['gid'] = self.FID
        self.findID = self.uniqueID
        self.removeID = self.uniqueID
        i += 1
        self.source = lNone(result[i])
        i += 1
        self.foreignKey = sNone(result[i])
        i += 1
        self.address = sNone(result[i])
        i += 1
        self.country = sNone(result[i])
        i += 1
        self.province = sNone(result[i])
        i += 1
        self.city = sNone(result[i])
        i += 1
        self.postalCode = sNone(result[i])
        i += 1
        self.agency = sNone(result[i])
        i += 1
        self.title = sNone(result[i])
        i += 1
        self.description = sNone(result[i])
        i += 1
        self.priceMin = iNone(result[i])
        i += 1
        self.priceMax =  iNone(result[i])
        i += 1
        self.price =  iNone(result[i])
        i += 1
        self.bedroomDesc =  sNone(result[i])
        i += 1
        self.bedrooms =  iNone(result[i])
        i += 1
        self.bathroomDesc =  sNone(result[i])
        i += 1
        self.bathrooms =  fNone(result[i])
        i += 1
        self.parkingSpots =  iNone(result[i])
        i += 1
        self.parkingPrice =  iNone(result[i])
        i += 1
        self.furnished =  bNone(result[i])
        i += 1
        self.size =  iNone(result[i])
        i += 1
        self.petDesc =  sNone(result[i])
        i += 1
        self.pets =  bNone(result[i])
        i += 1
        self.status = sNone(result[i])
        i += 1
        self.linkToAd = sNone(result[i])
        i += 1
        self.linkToImage = sNone(result[i])
        i += 1
        self.listingDate = dNone(result[i])
        i += 1
        self.latitude = fNone(result[i])
        i += 1
        self.longitude = fNone(result[i])
        i += 1
        if isCsv:
          if geoCode: # geocode based on the address
            latLng = self.geoCode()
            self.feature.geometry.position.x = latLng['lng']
            self.feature.geometry.position.y = latLng['lat']
          else:       # if csv input and there can be x & y columns in the csv
            self.feature.geometry.position.y = dNone(result[i])
            i += 1
            self.feature.geometry.position.x = dNone(result[i])
        else:
        # if sql result, the result is a text version of the spatially encoded
        # value in the table. eg. POINT(-114.070941 51.047071)
          self.feature.geom = result[i]
        # Build the flyover based on available data
        self.feature.properties["flyover"] = self.title

        # This is returned if we ever use any "closestPoints..." methods in
        # the feature class
        self._lastIndex = i;
        self._distance = Decimal(0.0)

    def insert(self):
      sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT, (%s),(%s)," + \
          "(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s)," + \
          "(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s)," + \
          "ST_SetSRID(ST_GeomFromText('POINT(%s %s)'),4326) ) RETURNING uniqueID"
      data = (self.source, self.foreignKey, self.address, self.country, \
          self.province, self.city, self.postalCode, self.agency, self.title, \
          self.description, self.priceMin, self.priceMax, self.price, self.bedroomDesc, self.bedrooms, \
          self.bathroomDesc, self.bathrooms, self.parkingSpots, self.parkingPrice, self.furnished, self.size, \
          self.petDesc, self.pets, self.status, self.linkToAd, self.linkToImage, self.listingDate+" 00:00:00", \
          self.latitude, self.longitude, self.longitude, self.latitude)
      if self.db.execute(sql, data):
        self.uniqueID = self.db.results[0][0]
        return True
      return False

    # Does the object exist in the database for the specified unique id?
    def isInDb(self, theSource, theForeignKey):
        self.sqlFilters("source='" + theSource + "'")
        self.sqlFilters("foreignkey='" + theForeignKey + "'")
        filtered = self.filteredSql()
        self._sql = filtered
        result = self.db.execute(self.filteredSql())
        self.sqlClear() # isLoaded only returns a single record - reset for the next fetch
        if not result:
          return False
        return True

    def encodeJSON(self):
        members = utilPublicMembers(self) # members useful for json export
        return self.encodePointJSON(members)

    #===========================================================================
    # Data loading
    #
    def importCSV(self, fullPathName):
      f = open(fullPathName)
      reader = csv.reader(f)
      for row in reader:
        self.populate(row, True)
        self.insert()

    #===========================================================================
    # Spatial methods
    #

    # Returns a dictionary of {'lat': xx.x, 'lng': xxx.x}
    def geoCode(self):
      self.feature.setGeoCoder("Google")
      logging.info(".geoCode: " + str(self.address) + ',' + str(self.city) + ',' + str(self.province))
      latLng = self.feature.geoCode(self.address + ' ' + self.city + ' ' + self.province + ' ' + self.country)
      if latLng is None:
        logging.info("Google failed to geocode. Switching to MapQuest.")
        self.feature.setGeoCoder("MapQuest")
        latLng = self.feature.geoCode(self.address + ' ' + self.city + ' ' + self.province + ' ' + self.country)
      return latLng

    def closestPoints(self, refPoint, nPts=None):
      self.applyFilters()
      result = self.feature.closestPoints(refPoint, nPts)
      if result:
        self.populate(result)
        self._distance = dNone(result[self._lastIndex+1])
        return True
      return False

