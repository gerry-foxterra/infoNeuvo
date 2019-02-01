// glp.js
// JavaScript interfaces for any non-map related interactions

var baseUrl;
var serviceUrl;
var wName = "wGis";
var busy = true;
var waitCount = 0;
var username = "anonymous";
var loggedIn = false;
var loginDiv;
var userObj = {};
var userID = 0;
var authCode = "";
var g_obj = "";

function loadAll() {
  var isMobile = false;
  if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
    isMobile = true;
  }
  if (!isMobile) {
  }
  baseUrl = utilBaseUrl();
  serviceUrl = baseUrl + "/services/";
  loadObjects();
}

function loadObjects() {
  // Testing
  username = 'glp'
  // Load all object information from AJAX service
  var theUrl = serviceUrl + "fetchMetadata.py";
  $.ajax(
  {
    url: theUrl,
    data: {_username: JSON.stringify(username)},
    dataType: 'json',
    type: 'GET',
    cache: false,
    success: function(bfr) {
      g_obj = eval(bfr);
      if (g_obj[0].status == "VALID") {
        loadMap(g_obj[1].layers, serviceUrl);
      }
      else {
        message("Unable to load map");
      }
      waiting(false);
      return;
    },
    error: function (jqXHR, ajaxOptions, thrownError) {
      console.log(thrownError);
      waiting(false);
    }
  });
}

function waiting(on) {
  if ( on ) {
    waitCount++;
    $("#waiting").slideDown(0.5);
  }
  else {
    waitCount--;
    if (!waitCount)
      $("#waiting").hide(0.2);
  }
}

function findAddress(inputID) {
  var address = $('#'+inputID).val();
  jdv_resolve_address(address, jdv_centerPoint_zoom);
}

function findOnMap(theID) {
  jdv_zoom_to_highlite_id(theID);
}

var dialogueHt, dialogueWd, dialogueTop, dialogueLeft;
var dialogueOpen = true;
function collapseDialogue(theID) {
  var p = $(theID).position();
  dialogueTop = p.top;
  dialogueLeft = p.left;
  dialogueHt = $(theID).height();
  dialogueWd = $(theID).width();
  dialogueOpen = false;
  $(theID).animate({
    height: 30,
    width: 30
  }, 1000, function(){
    $("#expandContainer").css({top: dialogueTop, left: dialogueLeft});
    $("#expandContainer").show(200);
    $(theID).hide(200);
  });
}

function expandDialogue(theID) {
  var p = $("#expandContainer").position();
  dialogueTop = p.top;
  dialogueLeft = p.left;
  $("#expandContainer").hide(200);
  $(theID).show(200);
  $(theID).css({top: dialogueTop, left: dialogueLeft});
  $(theID).animate({
    height: dialogueHt,
    width: dialogueWd }, 1000 );
  dialogueOpen = true;
}

function openDialogue() {
  var rowCount = $('#tableContainer tr').length;
  var maxHt = rowCount * 30;
  var ht = maxHt > 600 ? 600 : maxHt;
  if (ht < 200)
    ht = 200;
  $("#tableContainer").height(ht);
  $("#tableContainer").slideDown(600);
}

function closeDialogue(theID) {
  $(theID).slideUp(400);
  layersMnuOpen = false;
  imageOpen = false;
}

var processingGeoJSON = false;
var jsonBfr = "";
var jsonlayerID;

function retrieveGeoJSON(layerID, hiliteMode, refPts, radius, extra)
{
  // If 4 pts in 'refPts', select features by a bounding rectangle.  If 2 pts, select
  // features by a center point and radius.  If greater than 4 pts, select
  // using a polygon. If 0 points, select the from the map extent.
  //
  // hiliteMode: 'hilite' - draw features to user select layer
  //             'redraw' - draw features to user layer
  //             'reuse'  - use last retrieve 'jsonBfr' if redrawing same layer
  //             'both'   - draw features to user and select layer

  // Don't allow this AJAX retrieve method to have more than one current retrieval.
  if (processingGeoJSON) return;

  waiting(true);
  if (arguments.length <= 4)
    extra = '';
  if (arguments.length <= 3)
    radius = 0.0;
  if (arguments.length <= 2 || refPts.length < 1)
    refPts = glpExtent;
  if (arguments.length <= 1)
    hiliteMode = 'hilite';
  if (refPts.length < 1)
    refPts = [0.0];

  if (hiliteMode == "reuse" && layerID == jsonLayerID) {
    jdv_update_layerID_with_new_json_string(layerID, jsonBfr);
    waiting(false);
    return;
  }

  var hilite = "/both/hilite".indexOf(hiliteMode) > 0 ? true : false;
  var redraw = "/both/redraw".indexOf(hiliteMode) > 0 ? true : false;
  jsonLayerID = layerID;

  var htmlContent = "";
  var theUrl = serviceUrl("retrieveJSON_", layerID);
  var formValues = $("#filterForm").serialize();
  $.ajax(
  {
    url: theUrl,
    data: {_refPts: JSON.stringify(refPts), _radius: JSON.stringify(radius),
           _form: JSON.stringify(formValues), _extra: JSON.stringify(extra)},
    dataType: 'json',
    type: 'GET',
    cache: false,
    success: function(bfr) {
      if (hilite) {
          jdv_populate_selection(layerID, bfr, false);  // this layer is drawn (highlighted) to
      }                                                 // to the user draw layer
      if (redraw) {
        jdv_layerChanged(layerID, true);                // this layer is drawn to its own layer
        jdv_update_layerID_with_new_json_string(layerID, bfr);
      }
      jsonBfr = bfr;
      waiting(false);
      selectOff();
      processingGeoJSON = false;
      return;
    },
    error: function (jqXHR, ajaxOptions, thrownError) {
      console.log(thrownError);
      processingGeoJSON = false;
      waiting(false);
    }
  });
}

// ============================== etc =========================================
// Opens AND closes the datagrid table

var dataGridOpen = false;
function dataGrid()
{
  topPosn = 0;
  ht = 400;
  $("#tableContainer").css({'height':ht, 'display':'block'});

  var tm = Math.sqrt(ht * 1000)
  dataGridOpen = !dataGridOpen;
  $( "#tableContainer" ).animate({
    top: topPosn
  }, tm, function() {
    if (!dataGridOpen)
      $("#tableContainer").css('display','none');
    });
}
