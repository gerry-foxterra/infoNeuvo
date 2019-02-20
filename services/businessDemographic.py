#-------------------------------------------------------------------------------
# Name:        businessDemographic.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     20/11/2017
# Copyright:   (c) Entiro Systems Ltd. 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from feature import *

class Popup(object):
  pass

class Business(DataObj):
    def __init__(self, tableName=None, theBusinessType=""):
        self._id = "gid"
        if tableName is None:
          self._tableName = "business"
        else:
          self._tableName = tableName
        self._baseSql = "SELECT gid, businessid, businesstype, licensenbr, " + \
          "name, unit, address, city, province, postalcode, employeeCount, practionercount, " + \
          "salesvol, yrestab, telephone, email, officesize, longitude, latitude, url, " + \
          "ST_AsText(geom) FROM " + self._tableName

        self.gid = None
        self.businessID = None
        self.businessType = None
        self.licenseNbr = None
        self.name = None
        self.unit = None
        self.address = None
        self.city = None
        self.province = None
        self.postalCode = None
        self.employeeCount = None
        self.practionerCount = None
        self.salesVol = None
        self.yrEstab = None
        self.telephone = None
        self.email = None
        self.officeSize = None
        self.url = None

        self.resetFilters()
        super(Business, self).__init__(self._id, self._tableName, self._baseSql, self.populate)
        properties = {"gid":None, "flyover":None}
        self.feature = Feature(self._id, self.db, self._tableName, self._baseSql, properties, Point())

        self._employeeCount = None
        self.businessType= theBusinessType

        self._order = ( 'gid', 'findID', 'removeID', 'businessType', 'name', \
                        'address', 'city', 'province', 'postalCode', 'practionerCount', 'email', 'url'  )
        self._grid = {}
        self._grid['gid'] = {'title': 'ID','format':'{:.0f}','visible':'false','width':'20', 'csv':'true', 'quoted':'false'}
        self._grid['findID'] = {'title':'Find','format':'<img id=\'{:.0f}\' src=\'images/findMe.png\' onclick=\'mapFind(this)\'>',\
               'visible':'true','width':'12', 'css':'jsfind', 'csv':'false', 'quoted':'true'}
        self._grid['removeID'] = {'title':' X ','format':'<img id=\'{:.0f}\' src=\'images/removeMe.png\' onclick=\'jsRemove(this)\'>',\
               'visible':'true','width':'12', 'css':'jsremove', 'csv':'false', 'quoted':'true'}
        self._grid['businessType'] = {'title': 'Biz Type','format':'{}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['name'] = {'title': 'Biz Name','format':'{}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['address'] = {'title': 'Address','format':'{}','visible':'true','width':'60', 'csv':'true', 'quoted':'true'}
        self._grid['city'] = {'title': 'City','format':'{}','visible':'false','width':'30', 'csv':'true', 'quoted':'true'}
        self._grid['province'] = {'title': 'Prov','format':'{}','visible':'false','width':'20', 'csv':'true', 'quoted':'true'}
        self._grid['postalCode'] = {'title': 'Postal','format':'{}','visible':'true','width':'20', 'csv':'true', 'quoted':'true'}
        self._grid['practionerCount'] = {'title': 'Practioner count','format':'{:.0f}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['email'] = {'title': 'Email','format':'{}','visible':'false','width':'40', 'csv':'true', 'quoted':'true'}
        self._grid['url'] = {'title': 'Link','format':'{link}','visible':'true','width':'20', 'csv':'true', 'quoted':'true'}
        self._totals = {}

    #   ========================================================================
    #   Filters are local to the specific object based on application requirements
    #
    def resetFilters(self): #PRIVATE method
        self._firstTime = True
        self._employeeCount = None
        self._businessName = None
        self._postalCode = None

    def filterEmployeeCount(self, theEmployeeCount):
        self._employeeCount = theEmployeeCount

    def filterBusinessName(self, theBusinessName):
        self._businessName = theBusinessName

    def filterPostalCode(self, thePostalCode):
        self._postalCode = thePostalCode

    def applyFilters(self): #PRIVATE method
        if not self._firstTime:
            return
        if self._employeeCount is not None:
            where = "employeeCount >= " + str(self._employeeCount)
            self.sqlFilters(where)
            self.feature.sqlFilters(where)
        if self._postalCode is not None:
            where = "postalcode='" + self._postalCode + "'"
            self.sqlFilters(where)
            self.feature.sqlFilters(where)
        if self._businessName is not None:
            where = "name='" + self._businessName + "'"
            self.sqlFilters(where)
            self.feature.sqlFilters(where)

    def populate(self, result):
    #
    #   Populate the class.  To ensure values read from database or csv are
    #   of the right data type, use iNone to force integer and dNone to force
    #   decimal.
    #
        i = 0;
        self.gid = iNone(result[i])
        self.findID = self.gid
        self.removeID = self.gid
        self.feature.properties['gid'] = self.gid
        i += 1
        self.businessID = sNone(result[i]).strip()
        i += 1
        self.businessType = sNone(result[i]).strip()
        i += 1
        self.licenseNbr = sNone(result[i]).strip()
        i += 1
        self.name = sNone(result[i]).strip()
        i += 1
        self.unit = sNone(result[i]).strip()
        i += 1
        self.address = sNone(result[i]).strip()
        i += 1
        self.city = sNone(result[i]).strip()
        i += 1
        self.province = sNone(result[i]).strip()
        i += 1
        self.postalCode = sNone(result[i]).strip()
        i += 1
        self.employeeCount = iNone(result[i])
        i += 1
        self.practionerCount = iNone(result[i])
        i += 1
        self.salesVol = fNone(result[i])
        i += 1;
        self.yrEstab = iNone(result[i])
        i += 1;
        self.telephone = sNone(result[i]).strip()
        i += 1
        self.email = sNone(result[i]).strip()
        i += 1
        self.officeSize = iNone(result[i])
        i += 1;
        self.longitude = fNone(result[i])
        i += 1;
        self.latitude = fNone(result[i])
        i += 1;
        self.url = sNone(result[i]).strip()
        i += 1;
        self.feature.geometry = self.feature.geometry.decode(result[i])
        self._lastIndex = i

        if len(self.name) > 1:
          self.feature.properties['flyover'] = self.name

        popup = "<p>" + self.name + "</p>Address: " + self.address + "<br>City: " + \
          self.city + "<br>Practioners: " + str(self.practionerCount)
        #if len(self.url) > 1:
        #  popup += '<br><a href="' + self.url + '" target="blank">' + self.url + '</a>'
        self.feature.properties['popup'] = popup

    def fetchByBusinessID(self, theID=None):
        if theID is None:
          _theID = self.businessID
        else:
          _theID = theID
        sql = self._baseSql + " WHERE businessid='" + _theID + "'"
        result = self.db.execute(sql)
        if not result:
          return False
        result = self.db.getNextRow()
        if result:
          self.populate(result)
          return True
        return false

    def insert(self):
      sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT,(%s),(%s),(%s)," + \
              "(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s)," + \
              "(%s),(%s),ST_SetSRID(ST_GeomFromText('POINT(%s %s)'),4326) )" + \
              " RETURNING gid"
      data = (self.businessID, self.businessType, self.licenseNbr, self.name, \
              self.unit, self.address, self.city, self.province, self.postalCode, \
              self.employeeCount, self.practionerCount, self.salesVol, self.yrEstab, \
              self.telephone, self.email, self.officeSize, self.url,
              self.longitude, self.latitude, self.longitude, self.latitude )
      if self.db.execute(sql, data):
        self.gid = self.db.results[0][0]
        return True
      else:
        print sql
      return False

    def deleteByCity(self, theCity):
      sql = "DELETE FROM " + self._tableName + " WHERE city='" + str(theCity) + "'"
      self._sql = sql
      return self.db.execute(sql)

    def bizID(self):
      bizID = ""
      for c in self.name.upper() + self.postalCode:
        ordC = ord(c)
        if (ordC > 47 and ordC < 58) or (ordC > 64 and ordC < 91):
          bizID += c
      return bizID

    def encodeJSON(self):
        members = utilPublicMembers(self) # members useful for json export
        return self.encodePointJSON(members)

class Optometrists(Business):

    def __init__(self):

        tableName = "optometrist_business"
        super(Optometrists, self).__init__(tableName, "Optometrist")

class Veterinarians(Business):

    def __init__(self):

        tableName = "veterinarian_business"
        super(Veterinarians, self).__init__(tableName, "Veterinarian")

class OptometristDensity(DataObj):

  def __init__(self, db=None):
    self._tableName = "optometrist_density"

    if db is not None:
      self.db = db
    else:
      self.db = Database()

    self._id = "gid"
    self._baseSql = "SELECT gid, geocode, totalpop, practionercount, " + \
                    "practionerperpop, ST_AsText(geom) FROM " + self._tableName

    super(OptometristDensity, self).__init__(self._id, self._tableName, self._baseSql, self.populate)

    properties = {"gid":None, "flyover":None, "popup":None}
    self.feature = Feature(self._id, self.db, self._tableName, self._baseSql, properties, Point())
    self.resetFilters()

    self._intersectFraction = None

    self._order = ( 'gid', 'findID', 'removeID', 'geocode', 'totalPop', 'practionerCount', 'practionerperpop' )
    self._grid = {}
    self._grid['gid'] = {'title': 'ID','format':'{:.0f}','visible':'false','width':'20', 'csv':'true', 'quoted':'false'}
    self._grid['findID'] = {'title':'Find','format':'<img id=\'{:.0f}\' src=\'images/findMe.png\' onclick=\'mapFind(this)\'>',\
           'visible':'true','width':'12', 'css':'jsfind', 'csv':'false', 'quoted':'true'}
    self._grid['removeID'] = {'title':' X ','format':'<img id=\'{:.0f}\' src=\'images/removeMe.png\' onclick=\'jsRemove(this)\'>',\
           'visible':'true','width':'12', 'css':'jsremove', 'csv':'false', 'quoted':'true'}
    self._grid['geocode'] = {'title': 'Geocode','format':'{}','visible':'false','width':'30', 'csv':'true', 'quoted':'true'}
    self._grid['totalPop'] = {'title': 'Population','format':'{:,.0f}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
    self._grid['practionerCount'] = {'title': 'Practioners','format':'{:.0f}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
    self._grid['practionerperpop'] = {'title': 'Density / 1,000 pop','format':'{:.2f}','visible':'true','width':'60', 'csv':'true', 'quoted':'true'}
    self._totals = {}

  def fetchByGeoCode(self, thegeocode=None):
      if thegeocode is None:
        _thegeocode = self.geocode
      else:
        _thegeocode = thegeocode
      sql = self._baseSql + " WHERE geocode='" + _thegeocode + "'"
      result = self.db.execute(sql)
      if not result:
        return False
      result = self.db.getNextRow()
      if result:
        self.populate(result)
        return True
      return false

  def populate(self, result, startIndex=0):
  #
  #   Populate the class.
  #
    i = startIndex;
    self.gid = iNone(result[i])
    self.findID = self.gid
    self.removeID = self.gid
    i += 1
    self.geocode = sNone(result[i])
    i += 1
    self.totalPop = fNone(result[i])
    i += 1
    self.practionerCount = iNone(result[i])
    i += 1
    self.practionerperpop = fNone(result[i])
    i += 1
    self.geom = result[i]
    self.feature.geometry = self.feature.geometry.decode(result[i])

    self._lastIndex = i
    self._intersectFraction = Decimal(0.0)

    p = Popup()
    p.Population = '{:,.0f}'.format(self.totalPop)
    p.Practioners = self.practionerCount
    p.Density = '{:.2f}'.format(self.practionerperpop)
    self.feature.properties['popup'] = '[' + json.dumps(p, default=lambda o: o.__dict__) + ']'
    self.feature.properties['gid'] = self.gid
    self.feature.properties['flyover'] = "Practioner Density: " + "{:.2f}".format(self.practionerperpop)

  def insert(self):
      sql = "INSERT INTO optometrist_density VALUES( DEFAULT,'" + self.geocode + "'," + str(self.totalPop) + \
              "," + str(self.practionerCount) + "," + str(self.practionerperpop) + "," + \
              "ST_GeomFromText('" + str(self.geom) + "',4326)) RETURNING gid"
      if self.db.execute(sql):
        self.uniqueID = self.db.results[0][0]
        return True
      return False

class Individual(DataObj):

  def __init__(self, tableName=None, theBusinessType="",  db=None):

    self.uniqueID = None            #
    self.businessID = None          # Foreign key to business table
    self.businessType = None        # 'Optometrist', 'Jeweller'
    self.lastName = None            # Last name
    self.firstName = None           #
    self.middleInitial = None       #
    self.middleName = None          #
    self.courtesyTitle = None       # Mr, Mrs, Dr ...
    self.telephone = None           #
    self.telephoneType = None       # Cell, home, office ...
    self.email = None               # Email address
    self.city = None
    self.province = None
    self.flags = None               # Special characteristics of this person:

    self._fullName = ""

    self._tableName = tableName
    if tableName is None:
      self._tableName = "individual"

    self.businessType = theBusinessType

    if db is not None:
      self.db = db
    else:
      self.db = Database()

    self._id = "uniqueID"
    self._baseSql = "SELECT uniqueID, businessid, businesstype, lastname, firstname, " + \
               "middleinitial, middlename, courtesytitle, telephone, " + \
               "telephonetype, email, city, province, flags " + \
               "FROM " + self._tableName
    super(Individual, self).__init__(self._id, self._tableName, self._baseSql, self.populate)
    self.resetFilters()

  def resetFilters(self): #PRIVATE method
    self._firstTime = True
    self._uniqueID = None
    self._email = None
    self._lastNameLike = None
    self._businessType = None

  def filterUniqueID(self, theUniqueID):
    self._uniqueID = theUniqueID

  def filterEmail(self, theEmail):
    self._email = theEmail

  def filterLastNameLike(self, theLastName):
    self._lastNameLike = theLastName

  def filterBusinessType(self, theBusinessType):
    self._businessType = theBusinessType

  def applyFilters(self): #PRIVATE method
    if not self._firstTime:
      return
    if self._uniqueID is not None:
      where = "uniqueid=" + str(self._uniqueID)
      self.sqlFilters(where)
    if self._email is not None:
      where = "UPPER(email)='" + self._email.upper() + "'"
      self.sqlFilters(where)
    if self._lastNameLike  is not None:
      where = "UPPER(lastname) LIKE '" + self._lastNameLike.upper() + "%'"
      self.sqlFilters(where)
    if self._businessType is not None:
      where = "UPPER(businesstype)='" + self._businessType.upper() + "'"
      self.sqlFilters(where)

  def populate(self, result, startIndex=0):
  #
  #   Populate the class.
  #
    i = startIndex;
    self.uniqueID = iNone(result[i])
    i += 1;
    self.businessID = sNone(result[i])
    i += 1;
    self.businessType = sNone(result[i])
    i += 1;
    self.lastName = sNone(result[i])
    i += 1;
    self.firstName = sNone(result[i])
    i += 1;
    self.middleInitial = sNone(result[i])
    i += 1;
    self._fullName = self.firstName + " "
    if self.middleInitial != "":
      self._fullName += self.middleInitial + " "
    self._fullName += self.lastName
    self.middleName = sNone(result[i])
    i += 1;
    self.courtesyTitle = sNone(result[i])
    i += 1;
    self.telephone = lNone(result[i])
    i += 1;
    self.telephoneType = lNone(result[i])
    i += 1;
    self.email = sNone(result[i])
    i += 1;
    self.city = sNone(result[i])
    i += 1;
    self.province = sNone(result[i])
    i += 1;
    self.flags = sNone(result[i])

    self._lastIndex = i

  def insert(self):
    sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT,(%s),(%s)," + \
            "(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s)) RETURNING uniqueid"
    data = (self.businessID, self.businessType, self.lastName, self.firstName, \
            self.middleInitial, self.middleName, self.courtesyTitle, \
            self.telephone, self.telephoneType, self.email, self.city, self.province, self.flags )
    if self.db.execute(sql, data):
      self.uniqueID = self.db.results[0][0]
      return True
    else:
      print sql
    return False

  def deleteByCity(self, theCity):
      sql = "DELETE FROM " + self._tableName + " WHERE city='" + str(theCity) + "'"
      self._sql = sql
      return self.db.execute(sql)

  def fullName(self):
    self._fullName = self.firstName + " "
    if self.middleName != "":
      self._fullName += self.middleName + " "
    elif self.middleInitial != "":
      self._fullName += self.middleInitial + " "
    self._fullName += self.lastName
    return self._fullName

  def textPhoneNumber(self):
    phoneBfr = self.telephone[0]
    i = 0
    for phoneType in self.telephoneType:
      if phoneType.upper() == 'CELL' or phoneType.upper == 'TEXT':
        phoneBfr = self.telephone[i]
        break
      i += 1
    textPhone = ""
    for c in phoneBfr:
      if c.isdigit():
        textPhone += c
    return "+1" + textPhone

class IndividualOptometrists(Individual):
    def __init__(self):
        super(IndividualOptometrists, self).__init__("optometrist_individuals", "Optometrist")
