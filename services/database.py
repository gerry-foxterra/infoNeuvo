#-------------------------------------------------------------------------------
# Name:        database
# Modified:    17-May-2017
# Version:     1.0002
# Purpose:     Postgres database connector
#
# Author:      Gerald Perkins
#
# Created:     16/11/2015
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import psycopg2
from globalVars import *
from decimal import Decimal
import logging

class Database(object):
    # Determine what computer we are running on and set the database login
    # parameters appropriately.

    # Connect to the appropriate database
    def __init__(self, admin=False, dbName=None):
        g = GlobalVars()
        self.errorLevel = 0
        self.errorMsg = ""
        self.results = None
        self.currentRow = 0
        self.cursorArraySize = 100000

        _user = g.user
        _pswd = g.password
        _host = g.server
        if admin:
          _user = g.admin
          _pswd = g.adminPassword
        _db = g.database
        if dbName is not None:
          _db = dbName
        try:
            if _host is None:
              self.db = psycopg2.connect(user=_user, password=_pswd, database=_db)
            else:
              self.db = psycopg2.connect(user=_user, password=_pswd, database=_db, host=_host)
            self.cursor = self.db.cursor()
            self.ok = True
        except psycopg2.Error as e:
            self.ok = False
            self.errorLevel = 1
            self.errorMsg = "Unable to connect to database: " + _db + \
                            "\n" + e.message + "\nuser: " + _user + "\nhost: " + \
                            str(_host)
    #
    # For SQL queries.  With parms, for INSERT or UPDATE
    # Strong encouragement, here: http://initd.org/psycopg/docs/usage.html#query-parameters
    # Suggesting the value of using parms.
    #
    def execute(self, sql, parms=None, isArray=False):
        if parms is not None:
            return self.executeParms(sql, parms, isArray)
        if self.ok:
            try:
                self.cursor.execute(sql)
            except psycopg2.Error as e:
                self.errorLevel = 1
                self.errorMsg = "Unable to execute query: " + sql + \
                                "\n" + str(e.pgerror)
                #print self.errorMsg
                return False
            if self.cursor.rowcount > 0:
                sqlUpper = sql.upper()
                if "SELECT " in sqlUpper or " RETURNING " in sqlUpper:
                    self.results = self.cursor.fetchall()
                    self.currentRow = -1
                    if "INSERT " in sqlUpper:
                      self.db.commit()
                    return True
                else:
                    self.db.commit()
                    return True
        self.errorLevel = 1
        self.errorMsg += "\nDB not open. Unable to execute query: " + sql
        return False

    def executeParms(self, sql, parms, isArray):
        if self.ok:
            try:
                if isArray:   # Array parms are incorrectly formatted by PostGRES - fix it up
                  mogrified = self.cursor.mogrify(sql, parms).replace('[', '{')
                  mogrified = mogrified.replace(']', '}')
                  self.cursor.execute(mogrified)
                else:
                  self.cursor.execute(sql, parms)
            except psycopg2.Error as e:
                self.errorLevel = 1
                errSql = self.cursor.mogrify(sql, parms)
                if isArray:
                  errSql = mogrified
                self.errorMsg = "Unable to execute query: " + errSql + \
                                "\n" + e.pgerror
                #print self.errorMsg
                logging.info(self.errorMsg)
                return False

            if self.cursor.rowcount > 0:
                sqlUpper = sql.upper()    # If a fetch, get all rows requested by 'sql'
                if "SELECT " in sqlUpper or " RETURNING " in sqlUpper:
                    self.results = self.cursor.fetchall()
                    self.currentRow = -1
                    if "INSERT " in sqlUpper:
                      self.db.commit()
                    return True
                else:                     # Not a fetch, commit the executed 'sql'
                    self.db.commit()
                    return True
            else:
                self.errorLevel = 1
                self.errorMsg = "Unable to execute query: " + self.cursor.mogrify(sql, parms)
                return False
        self.errorLevel = 1
        self.errorMsg += "\nDB not open. Unable to execute query: " + sql
        return False

    def errorLevel(self):
        return self.errorLevel

    def errorMsg(self):
        return self.errorMsg

    def getNextRow(self):
        self.currentRow += 1
        if self.currentRow >= self.cursor.rowcount:
            return None
        return self.results[self.currentRow]

    def getNumRows(self):
        return self.cursor.rowcount

    def close(self):
        self.db.close()

'''
Some useful utilities for populating class variables from a query
'''
def sNone(s, len=None):
    if s is None:
        return ''
    if len is None:
      return str(s)
    return str(s)[:len]

def dNone(d):   # Date
  return sNone(d, 10)

def bNone(b):
    if b is None:
        return False
    return b

def DNone(d):
    if d is None:
        return Decimal('0.0')
    try:
        dd = Decimal(d)
        return dd
    except:
        return Decimal('0.0')

def fNone(f):
    if f is None:
        return float(0.0)
    try:
        ff = float(f)
        return ff
    except:
        return float('0.0')

def iNone(i):
    if i is None:
        return int('0')
    try:
        ii = int(i)
        return ii
    except:
        return int('0')

def lNone(i):       # List
    if i is None:
        return []
    else:
        return i

def jNone(i):       # JSON
    if i is None:
        return {}
    else:
        return i