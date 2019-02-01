#!/usr/local/bin/python
#-------------------------------------------------------------------------------
# Name:        dropdown_classes.py
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     04/04/2016
# Beta:        05-Sep-2017
# Copyright:   (c) Entiro Systems Ltd. 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from classInfo import *
import cgi
import json
import time

import logging
logging.basicConfig(filename='logs/dropdown_classes.log', level=logging.INFO)
logging.info("Start")

print "Content-Type: text/html\r\n\r\n"
print "<option id='0'> Choose a class </option>"

o = ClassInfo()
while o.fetchNext(False):
  print "<option id='" + str(o.uniqueID) + "'>" + o.name + "</option>"

