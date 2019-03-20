#-------------------------------------------------------------------------------
# Name:        classInfo
# Purpose:
#
# Author:      GLP
#
# Created:     15-Nov-2018
# Copyright:   (c) Foxterra Systems Ltd 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from dataObj import *
from util import *
import logging
import datetime

class ClassInfoData(DataObj):
  """
  Shared methods for ClassInfo data holders
  """
  def __init__(self, db=None):
    self.uniqueID = None
    self.objName = ""
    self.group = ""
    self.id = ""
    self.appName = None
    self.metadata = {}            # information for handling a this object
    self.sortID = 0
    self.published = 'Y'

    self._id = "uniqueID"
    self._baseSql = "SELECT uniqueid, objname, appname, metadata, sortid, published FROM " + \
                    self._tableName
    if db is None:
      db = Database(False, "metadata")
    super(ClassInfoData, self).__init__(self._id, self._tableName, self._baseSql, self.populate, db)

    self._order = ('uniqueID','findID','objName','group','id','appName','sortID','metadata','published')
    self._grid = {}
    self._grid['uniqueID'] = {'title':'uniqueID','format':'{:d}','visible':'false','width':'20', 'csv':'true', 'quoted':'false'}
    self._grid['findID'] = {'title':'Find','format':'<img id=\'{}\' src=\'images/editMe.png\' onclick=\'editClassInfo(this)\'>',\
               'visible':'true','width':'20', 'css':'centerLink', 'csv':'false', 'quoted':'true'}
    self._grid['objName'] = {'title':'Object Name','format':'{}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
    self._grid['group'] = {'title':'Group','format':'{}','visible':'true','width':'30', 'csv':'true', 'quoted':'true'}
    self._grid['id'] = {'title':'ID','format':'{}','visible':'true','width':'30', 'csv':'true', 'quoted':'true'}
    self._grid['classID'] = {'title':'Class ID','format':'{:d}','visible':'true','width':'44', 'csv':'true', 'quoted':'false'}
    self._grid['appName'] = {'title':'Application Name','format':'{}','visible':'true','width':'40', 'csv':'true', 'quoted':'true'}
    self._grid['metadata'] = {'title':'Metadata','format':'{json}','visible':'false','width':'100', 'csv':'true', 'quoted':'true'}
    self._grid['sortID'] = {'title': 'Sort ID','format':'{:d}','visible':'true','width':'30', 'csv':'true', 'quoted':'false'}
    self._grid['published'] = {'title':'Published?','format':'{}','visible':'true','width':'20', 'csv':'true', 'quoted':'false'}
    self.resetFilters()

  def resetFilters(self):
      self._filterAppName = None
      self._filterPublished = None
      self._firstTime = True

  def filterAppName(self, theAppName):
    self._filterAppName = theClassID

  def filterIsPublished(self, isPublished):
    self._filterPublished = isPublished

  def applyFilters(self): #PRIVATE method
      if not self._firstTime:
          return
      if self._filterAppName is not None:
        where = "appname='" + str(self._filterAppName) + "'"
        self.sqlFilters(where)
      if self._filterPublished is not None:
        where = "published='" + self._filterPublished + "'"
        self.sqlFilters(where)

  def populate(self, result):
  #
  #   Populate this class.
  #
      i = 0;
      self.uniqueID = iNone(result[i])
      self.findID = self.uniqueID
      i += 1
      self.objName = sNone(result[i])  # in the form Group:Layer
      if ':' in self.objName:
        parts = self.objName.split(':')
        self.group = parts[0]
        self.id = parts[1]
      else:
        self.group = '';
        self.id = self.objName
      i += 1
      self.appName = sNone(result[i])
      i += 1
      self.metadata = self.setDefaultAttributes(self._defaults, jNone(result[i]))
      i += 1
      self.sortID = iNone(result[i])
      i += 1
      self.published = sNone(result[i])
      i += 1
      self._lastIndex = i

  def setDefaultAttributes(self, defaults, jsn):
    # Return all possible attributes whether in 'jsn' or not.  This means that
    # code which uses this metadata does not have to check for the existence of
    # an attribute. All valid attributes will always be present in the json
    # object returned.
    rtn = {}
    for key, val in defaults.items():
      if key in jsn:
        rtn[key] = jsn[key]
      else:
        rtn[key] = defaults[key]
    return rtn

  def encodeJSON(self):
    for key in self.metadata:
      if self.metadata[key] == "false":
        self.metadata[key] = False
      elif self.metadata[key] == "true":
        self.metadata[key] = True
    return re.sub('[^a-zA-Z0-9 {}"\'.!@#$%^&*()-_=+`]', '', \
                  '"' + self.objName + '":' + json.dumps(self.metadata))

  def update(self, theID, column, newValue, tableName=None, isArray=False):
    if column is not "metadata":
      return super(ClassInfoData, self).update(theID, column, newValue)
    if tableName is None:
      tblName = self._tableName
    else:
      tblName = tableName
    sql = "UPDATE " + tblName + " SET metadata='" + json.dumps(newValue) + \
          "' WHERE uniqueID=" + str(theID)
    if self.db.execute(sql):
      return True
    return False

  def insert(self):
    sql = "INSERT INTO " + self._tableName + " VALUES( DEFAULT,'" + self.objName + \
          "','" + self.appName +  "','" + json.dumps(self.metadata) + "'," + \
          str(self.sortID) + ",'" + self.published + "') RETURNING uniqueID"
    if self.db.execute(sql):
        self.uniqueID = self.db.results[0][0]
        return True
    return False

class LayerInfo(ClassInfoData):
  """
  Attributes for a single layer
  """
  def __init__(self, db=None):
    self._tableName = "layers"
    super(LayerInfo, self).__init__(db)

    # All attribute metadata for display and editing
    self._editOrder = [ 'uniqueID', 'objName', 'published', 'group', 'id', 'appName', \
                        'sortID', 'metadata', 'userID', 'authCode']
    self._attributes = {\
      '_defaults': { 'tagType':'input', 'dataType':'str', \
                  'maxLength':999, 'active':True, 'min':0, 'max':0, \
                  'cssClass':'iSmall', 'label':'', 'disabled':False, \
                  'inputClass':'f_input', 'labelClass':'f_label', 'disabled':False},
      'uniqueID': { 'dataType':"int", 'maxLength':12, 'label':'Unique ID (cannot be edited)', 'disabled':True},
      'userID': { 'dataType':'int', 'cssClass':'hidden', 'label':'UserID'},
      'authCode': { 'dataType':'int', 'cssClass':'hidden', 'label':'Auth Code'},
      'objName': { 'label':'Group:Layer'}, \
      'group': { 'label':'Group', 'disabled':True}, \
      'id': { 'label':'ID', 'disabled':True}, \
      'appName': { 'label':'App Name'}, \
      'metadata': { 'dataType':'json', 'label':'Metadata', 'disabled':True}, \
      'sortID': { 'label':'Legend Sort ID', 'dataType':'int'}, \
      "published":{"label":"Published?", "dataType":"str", "tagType":"select","options":[{"text":"Yes","value":"Y"},{"text":"No","value":"N"},{"text":"Testing","value":"T"}]}
    }

    # Metadata for grid retrieval and display
    self._defaults = {'type':'dynamic', 'format':'WMS', 'minZoom':0, 'maxZoom':9999999, 'text':'Unknown', \
                     'URL':'', 'pop_up':'','open':False, 'owner':'', 'cssClass':'selectLine', \
                     'visible':False, 'select':False, 'legend':'', 'heatMap':False, 'geometry':'point', \
                     'image':'', 'zindex':'', 'filters':False, 'source':'', 'locale':'', 'color':[0,0,0,1.0], \
                     'imagerySet':'','attribution':'','opacity':1.0}
    self._format = {'type':'str', 'id': 'str', 'format':'str', 'minZoom':'int', 'maxZoom':'int', 'text':'str', \
                     'URL':'str', 'pop_up':'str', 'open':'bool', 'group':'str', 'owner':'str', 'cssClass':'str', \
                     'visible':'bool', 'select':'bool', 'legend':'str', 'heatMap':'bool', 'geometry':'str', \
                     'image':'str', 'zindex':'int', 'filters':'bool', 'source':'str', 'locale':'str', 'color':'int[]', \
                     'imagerySet':'str','opacity':'int'}
    '''
    self._options = {'type':['dynamic','static','update','OSM'], 'format':['WMS','feedJSON','GeoJSON','OSM'], \
                    'geometry':['','point','polygon','linestring','multilinestring']}
    '''
    # Override base class
    self._grid['findID'] = {'title':'Find','format':'<img id=\'{}\' src=\'images/editMe.png\' onclick=\'editLayerInfo(this)\'>',\
               'visible':'true','width':'20', 'css':'centerLink', 'csv':'false', 'quoted':'true'}

    # objName is in the form "layerGroup:layer".  eg. "RentalProperties:CurrentListings"

class ReportInfo():
  """
  Attributes for a single report.
  """
  def __init__(self, db=None):
    self.reports = {
      #'major_projects_closest':{'text':'Closest Major Projects', 'owner':'', 'service':'report_closest_majorProjects.py', 'checked':''},
      #'overview': {'text':'Overview Report', 'owner':'', 'service':'report_overview.py', 'checked':''},
      'population': {'text':'Population Report', 'owner':'', 'service':'report_statscan_population.py', 'checked':''},
      'age_range': {'text':'Age Range Report', 'owner':'', 'service':'report_statscan_ageRange.py', 'checked':''}
    }
