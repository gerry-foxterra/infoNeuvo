#-------------------------------------------------------------------------------
# Name:        globalVars
# Purpose:
#
# Author:      Gerald Perkins
#
# Created:     16/11/2015
# Copyright:   (c) Entiro Systems Ltd. 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import socket

# Determine what computer we are running on and set the database login
# parameters appropriately

class GlobalVars:

    def __init__(self):
        self.fqdn = socket.getfqdn() # fully qualified domain name
        hostComp = self.fqdn.upper()
        if "GLP" in hostComp:         # GLP notebook
            self.server = None
            #self.server = "realestate.resolutefox.com"
            self.database = "infosight"
            self.user = "gisuser"
            self.password = "gis1sCool"
            self.admin = "gisAdmin"
            self.adminPassword = "gisAdmin1sCool"
            self.imageFileDirectory = 'http://localhost/infoNeuvo/services/'
        else:
            self.server = 'localhost'
            self.database = "infosight"
            self.user = "gisuser"
            self.password = "gis1sCool"
            self.admin = "gisuser"
            self.adminPassword = "gisUser"
            self.imageFileDirectory = 'https://realestate.resolutefox.com/infoNeuvo/services/'

    def Print(self):
        print self.fqdn
