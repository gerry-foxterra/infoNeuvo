#-------------------------------------------------------------------------------
# Name:        util
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     12/12/2015
# Copyright:   (c) Entiro Systems Ltd. 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, inspect, copy
from decimal import Decimal

def utilPublicMembers(theClass):
    attributes = inspect.getmembers(theClass, \
        lambda a:not(inspect.isroutine(a)))
    return [a for a in attributes if \
        not(a[0].startswith('_')) and str(a[1]).find(" object ")<0 \
        and str(a[1]).find(" instance ")<0 and type(a[1]) is not dict]

def utilBaseURL():
  if "SCRIPT_NAME" in os.environ:
    parts = os.environ["SCRIPT_NAME"].split('/')
    directory = ""
    i = 0
    while i < (len(parts)-2):
      part = str(parts[i])
      if len(part) > 1:
        directory += '/' + part
      i += 1
    baseUrl = os.environ["REQUEST_SCHEME"] + '://' + \
             os.environ["HTTP_HOST"] + '/' + \
             directory + '/'
  else:
    baseUrl = "../"
  return baseUrl

def utilAppBaseURL():
  if "SCRIPT_NAME" in os.environ:
    parts = os.environ["SCRIPT_NAME"].split('/')
    directory = ""
    i = 0
    while i < (len(parts)-1):
      part = str(parts[i])
      if len(part) > 1:
        directory += '/' + part
      i += 1
    appUrl = os.environ["REQUEST_SCHEME"] + '://' + \
             os.environ["HTTP_HOST"] + '/' + \
             directory + '/'
  else:
    appUrl = "../"
  return appUrl

def utilJsonContentType():
    return 'Content-Type: application/json\r\n'

def utilJsonHeader():
    return '{"type":"FeatureCollection","features":['

def utilJsonFooter():
    return ']}\n'

def utilJsonFeatureSuffix():
    return '{"type":"Feature","properties":'

def utilJsonEncodeArray(arrayName, array):
    jsonBfr = '"' + arrayName + '":'
    jsonBfr += utilFmat(array)
    return jsonBfr

def utilFmat(value, strDelimiter='"'):
    theType = type(value)
    if theType is str:
        #return strDelimiter + "xyz" + strDelimiter
        if len(value) > 0 and value[0] == '[':
          return value
        return strDelimiter + value.replace("\\","/") + strDelimiter
    if theType is long or type is int:
        return "{0:d}".format(value)
    if theType is float:
        return "{0:.6f}".format(value)
    if theType is Decimal:
        return "{0:.6f}".format(value)
    if theType is bool:
        return strDelimiter + str(value) + strDelimiter
    if theType is list:
        comma = ''
        rtn = '['
        for val in value:
          rtn += comma + utilFmat(val)
          comma = ','
        return rtn + ']'
    try:
        return "{0:d}".format(value)
    except:
        pass
    return ""

def utilIntWithCommas(ix):
    x = int(ix+0.5)
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)

def utilPrettyDate(yyyymmdd):
    if len(yyyymmdd) == 8:      # Input in the form yyyymmdd
      return yyyymmdd[6:8] + '-' + yyyymmdd[4:6] + '-' + yyyymmdd[0:4]
    elif len(yyyymmdd) == 10:   # Input in the form yyyy-mm-dd
      return yyyymmdd[8:10] + '-' + yyyymmdd[5:7] + '-' + yyyymmdd[0:4]
    return yyyymmdd

# Based on the passed `date`, return the date `delta` months different
def utilMonthDelta(date, delta):
  m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
  if not m: m = 12
  d = min(date.day, [31,
    29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
  return date.replace(day=d, month=m, year=y)

# Convert the date to a string in the form yyyymmdd from a form where month 1
# is January to month 0 is January
def utilZeroBasedMonth(theDate):
  d = int(theDate.strftime('%Y%m%d'))
  return str(d-100)

def utilStripPassword(parms):
  try:
    cleanParms = copy.deepcopy(parms)
    if 'password' in cleanParms:
      cleanParms['password'] = "********"
    if 'retypePassword' in cleanParms:
      cleanParms['retypePassword'] = "********"
    return cleanParms
  except:
    return parms
