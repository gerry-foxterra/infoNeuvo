#-------------------------------------------------------------------------------
# Name:        gisUser
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     27/04/2016
# Last Update: 27/04/2016
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
from dataObj import *
import datetime, time, os
import bcrypt

class GisUser(DataObj):
    def __init__(self, admin=False, dbName=None):
        # Required by the parent class - DataObj
        _id = "uniqueID"
        _tableName = "gis_users"
        _baseSql = "SELECT uniqueid,name,password,email,status,statusdate," + \
          "mode,latestvalidtime,maxduration,authcode,ip,rightsto,branding, " + \
          "activationcode FROM " + _tableName
        super(GisUser, self).__init__(_id, _tableName, _baseSql, self.populate)

        _reason = ""
        self.resetFilters()

    #   ========================================================================
    #   Filters are local to the specific object based on application requirements
    #

    def resetFilters(self): #PRIVATE method
        self._firstTime = True
        self._nameFilter = None
        self._authCodeFilter = None
        self._rightsFilter = None

    def filterName(self, theName):
        self._nameFilter = theName

    def filterAuthCode(self, theAuthCode):
        self._authCodeFilter = theAuthCode

    def filterRightsTo(self, theRights):
        self._rightsFilter = theRights

    def applyFilters(self): #PRIVATE method
        if not self._firstTime:
            return
        if self._nameFilter is not None:
            where = "upper(name)=upper('" + (self._nameFilter) + "')"
            self.sqlFilters(where)
        if self._authCodeFilter is not None:
            where = "authcode='" + str(self._authCodeFilter) + "'"
            self.sqlFilters(where)
        if self._rightsFilter is not None:
            where = "'" + self._rightsFilter + "' = ANY (rightsto::text[])"
            self.sqlFilters(where)

    def populate(self, result, isCsv=False):
    #
    #   populate the class.  To ensure values read from database or csv are
    #   of the right data type, use iNone to force integer and dNone to force
    #   decimal.
    #
        i = 0;
        self.uniqueID = iNone(result[i])
        i += 1
        self.name = sNone(result[i])
        i += 1
        self.password = sNone(result[i])
        i += 1
        self.email = sNone(result[i])
        i += 1
        self.status = sNone(result[i])
        i += 1
        self.statusDate = sNone(result[i])
        i += 1
        self.mode = sNone(result[i])
        i += 1
        self.latestValidTime = sNone(result[i])
        i += 1
        self.maxDuration = iNone(result[i])
        i += 1
        self.authCode = sNone(result[i])
        i += 1
        self.ip = sNone(result[i])
        i += 1
        self.rightsTo = lNone(result[i])
        i += 1
        self.branding = sNone(result[i])
        i += 1
        self.activationCode = sNone(result[i])

        self._lastIndex = i

    def insert(self):
      self.uniqueID = self.nextUniqueID()
      sql = "INSERT INTO " + _tableName + " VALUES( (%s),(%s),(%s),(%s),(%s)," + \
            "(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s) )"
      data = (self.uniqueID, self.name, self.password, \
        self.email, self.status, self.statusDate, self.mode, self.latestValidTime, \
        self.maxDuration, self.ip, self.rightsTo, self.branding, self.activationCode )
      if self.db.execute(sql, data):
        return True
      return False

    #   ========================================================================
    #   User authorization
    #
    #   Usage:
    #     Initial call to this class must always be 'isValid'
    #     If the username / password combination is valid, the 'GisUser' object
    #     is instantiated and other methods can be used to:
    #       'login()', 'logout()', check if 'isLoggedIn()' and if 'isAdmin()'

    # ALWAYS call the 'isValid' or 'isAuthorized' method before any other

    def isValid(self, username, password):
      self.filterName(username)
      if self.fetchNext():
        hashed = bcrypt.hashpw(password, self.password)
        if hashed == self.password:
          if (self.status == "authenticated"):
            self.name = username
            self._reason = "Valid"
            return True
          else:
            self._reason = "User not authenticated. Current status: " + self.status
        else:
          self._reason = "Password incorrect"
      else:
        self._reason = "User does not exist"
        logging.info(self._sql)
      return False

    def isAuthorized(self, authCode):
      self.filterAuthCode(authCode)
      logging.info("isAuthorized, authCode:" + authCode)
      if self.fetchNext():
        logging.info("isAuthorized, fetchNext true")
        return True
      logging.info("isAuthorized, fetchNext false")
      return False

    def hasBranding(self, authCode):
      self.filterAuthCode(authCode)
      if self.fetchNext():
        if self.branding != '':
          return True
      return False

    def hasRightsTo(self, authCode, rightsTo):
      self.filterAuthCode(authCode)
      self.filterRightsTo(rightsTo)
      if self.fetchNext():
        return True
      return False
    def reason(self):
      return self._reason

    def login(self):
      dtNow = datetime.datetime.now()
      logoutTime = dtNow + datetime.timedelta(minutes=self.maxDuration)
      logging.info("Now: " + str(dtNow) + ", latestvalidtime: " + str(logoutTime))
      authCode = self.name + str(time.time())
      self.authCode = authCode.strip()
      if "REMOTE_ADDR" in os.environ:
        self.ip = os.environ["REMOTE_ADDR"]
      if self.update(self.uniqueID, "authcode", self.authCode):
        if self.update(self.uniqueID, "latestvalidtime", str(logoutTime)):
          if self.update(self.uniqueID, "ip", self.ip):
            return True
      self._reason = "Login error"
      return False

    def logout(self):
      logoutTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
      if self.update(self.uniqueID, "latestvalidtime", str(logoutTime)):
        return True
      self._reason = "Logout error"
      return False

    def isLoggedIn(self):
      # 2016-04-29 14:40:02.508000
      try:
        lastTime = datetime.datetime.strptime(self.latestValidTime, '%Y-%m-%d %H:%M:%S.%f')
      except:
        return False
      if lastTime > datetime.datetime.now():
        return True
      return False

    def isAdmin(self):
      if self.mode.lower() == "admin":
        return True
      return False

    def reason(self):
      return self._reason
