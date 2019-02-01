from classInfo import *

ci = ClassInfo()
more = ci.fetchNext()

# == Layers ====================
layerDelim = ''
attributeDelim = ''
reportDelim = ''
jsonLayers = '"layers":{'
jsonAttributes = '"attributes":{'
jsonReports = '"reports":{'
while more:
  for layer in ci.layers:
    jsonLayers += layerDelim + layer.encodeJSON()
    layerDelim = ','
  for attribute in ci.attributes:
    jsonAttributes += attributeDelim + attribute.encodeJSON()
    attributeDelim = ','
  for report in ci.reports:
    jsonReports += reportDelim + report.encodeJSON()
    reportDelim = ','
  more = ci.fetchNext()
print '[{' + jsonLayers + '}},'
print '{' + jsonAttributes + '}},'
print '{' + jsonReports + '}}]'
