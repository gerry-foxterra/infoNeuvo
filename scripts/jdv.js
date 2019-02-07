// Map functionality

var gAccessKeys;
var map;
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
    layersDialogue(layers);
    addSelectability(layers);
  }
  else {
    setTimeout(function() {
      doLayersDialogue(layers);
    }, 200);
  }
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
/* =============================================================================
   Map interactions
*/
function selectBtnClick() {
  // Reveal out the various select options
  var selectOpen = $("#selectOptions").css('display') == "block" ? true : false;
  if (selectOpen) {
    $( "#selectOptions" ).animate({
      left: "-200px"
    }, 1000, function() {
      $("#selectOptions").css('display','none');
      $("#div_select_on").css("background-image", "url('css/images/select.png')");
    });
    selectOpen = false;
  }
  else {
    $("#selectOptions").css('display','block');
    $( "#selectOptions" ).animate({
      left: "0px"
    }, 1000, function() {
      $("#div_select_on").css("background-image", "url('css/images/hideLeft.png')");
    });
    selectOpen = true;
  }
}

function selectBtnOut(what) {
}

