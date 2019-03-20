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
var currentFormValues = "";

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
        loadMap(g_obj[1].layers, g_obj[2].reports, serviceUrl);
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

function doReport(reportKey, selectMode, refPts, radius) {
  waiting(true);
  var htmlContent = "";
  var theUrl = serviceUrl + g_obj[2].reports[reportKey].service;

  $.ajax(
  {
      url: theUrl,
      data: {_geography: JSON.stringify(selectMode), _refPts:JSON.stringify(refPts),
             _radius: JSON.stringify(radius), _form: JSON.stringify(currentFormValues),
             _authCode: JSON.stringify(authCode)},
      dataType: 'html',
      type: 'POST',
      cache: false,
      success: function(bfr) {
        $("#reportContainer").html(bfr);
        openReportInNewWindow('landscape');
        waiting(false);
      },
      error: function (jqXHR, ajaxOptions, thrownError) {
        console.log(jqXHR.responseText);
        waiting(false);
      }
  });
}

function openReportInNewWindow(orientation) {
  var width = 695;
  var height = 860
  if ( orientation == 'landscape' ) {
    height = 695;
    width = 940;
  }
  var wInfoRep = window.open("reportEnvelope.html", "_blank",
      "toolbar=no, scrollbars=yes,resizable=yes, width=" + width + ", height=" + height + ", top=100, left=100'");
}
function waiting(on) {
  if ( on ) {
    if (++waitCount == 1)
      $("#waiting").slideDown(0.5);
  }
  else {
    if (--waitCount < 1) {
      $("#waiting").hide(0.2);
      waitCount = 0;
    }
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
