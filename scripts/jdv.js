// Map functionality

var gAccessKeys;
var map;
var gExtent;  // current map extent (rectangle)
var gWmsMap;
var mapInit = [];

// Get parms for initial map setup.  This could come from a cookie or a check
// of user location.
function mapSetup()
{
  mapInit["lat"] = 51.0;
  mapInit["lon"] = -114.0;
  mapInit["zoom"] = 11;
  return mapInit;
}

function loadMap(layers, serviceUrl) {
  var fullUrl = serviceUrl + "accessKeys.py";
  $.ajax({
    url: fullUrl,
    data: '',
    dataType: 'text',
    type: 'POST',
    cache: false,
    success: function(bfr) {
      gAccessKeys = JSON.parse(bfr);
      mapInit = mapSetup();
      createMap(mapInit, layers);
      displayLayers(layers);
    },
      error: function(jqXHR, ajaxOptions, thrownError) {
        console.log(thrownError);
    },
  });
}

function displayLayers(layers) {
  for (var layerKey in layers) {
    setVisibility(layers, layerKey)
  }
  setTimeout(function() {
    doLayersDialogue(layers);
  }, 200);
}

function doLayersDialogue(layers) {
  if (!loadingLayers()) {
    gWmsMap = layersDialogue(layers);
  }
  else {
    setTimeout(function() {
      doLayersDialogue(layers);
    }, 200);
  }
}

var processingGeoJSON = false;
var jsonBfr = "";
var jsonlayerID;

function retrieveGeoJSON(layerKey, refPts, radius, callBack) {
  // If 4 pts in 'refPts', select features by a bounding rectangle.  If 2 pts, select
  // features by a center point and radius.  If greater than 4 pts, select
  // using a polygon. If 0 points, select the from the map extent.

  // Don't allow this AJAX retrieve method to have more than one current retrieval.
  if (processingGeoJSON) return;

  waiting(true);
  if (arguments.length <= 3)
    callBack = false;
  if (arguments.length <= 2)
    radius = 0.0;
  if (arguments.length <= 1 || refPts.length < 1)
    refPts = getMapExtent();
  if (refPts.length < 1)
    refPts = [0.0];

  var layerID = layerKey.split(':')[1];
  //var surrogate = gLayers[layerKey].surrogate;
  //if (surrogate != "") layerID = surrogateLayer(surrogate);
  jsonLayerID = layerID;

  var htmlContent = "";
  var theUrl = serviceUrl + "geoJSON_" + layerID + ".py";
  var formValues = $("#filterForm").serialize();
  $.ajax(
  {
      url: theUrl,
      data: {_refPts: JSON.stringify(refPts), _radius: JSON.stringify(radius),
             _form: JSON.stringify(formValues)},
      dataType: 'json',
      type: 'GET',
      cache: false,
      success: function(bfr) {
        jsonBfr = bfr;
        if (!callBack)
          return bfr.geoJSON;
        else
          callBack(bfr.geoJSON);
        waiting(false);
      },
      error: function (jqXHR, ajaxOptions, thrownError) {
          console.log(thrownError);
          processingGeoJSON = false;
          waiting(false);
          return false;
      }
  });
}

function setVisibility(layers, layerKey) {
  if (!layers[layerKey].hasOwnProperty("instantiated")) {
    instantiateLayer(layers, layerKey);
    return;
  }
}

/* =============================================================================
   Map interactions
*/

