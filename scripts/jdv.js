// Map functionality

var gAccessKeys;
var gMap;
var gMapInit = [];

// Get parms for initial map setup.  This could come from a cookie or a check
// of user location.
function mapSetup()
{
  gMapInit["lat"] = 51.0;
  gMapInit["lon"] = -114.0;
  gMapInit["zoom"] = 11;
  return gMapInit;
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
      gMapInit = mapSetup();
      createMap(gMapInit, layers);
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
    layersDialogue(layers);
  }, 1000)
}

function setVisibility(layers, layerKey) {
  if (!layers[layerKey].hasOwnProperty("instantiated")) {
    instantiateLayer(layers, layerKey);
    return;
  }
  if (layer.visible) {
    // Do  layer visible thing
  }
  else {
    // Do  layer hidden thing
  }
}

