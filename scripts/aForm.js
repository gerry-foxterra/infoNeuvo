// =============================================================================
// The following entries are specific for the object being retrieved
//
var baseUrl;
var serviceUrl;
var dataObjName = "layerInfo";
var g_dataObj;  // Last edited dataObj. Used as a template for Insert
var layerMetadataDefaults = false;
var layerMetadataFormat = false;
var layerMetadataAttributes = false;
var layerMetadataOrder = false;
var metadata;
var userID = 0;
var authCode = 0;
var jsn;

jQuery(document).ready(function(){
  baseUrl = utilBaseUrl();
  serviceUrl = baseUrl + "/services/";
  userID = getCookie("meta_userID");
  authCode = getCookie("meta_authCode");
  if (authCode.length < 1) {
    $(".btnBar").html(" ");
    $("#theForm").html("<table><tr><td>You must first log in. <a href='/infoNeuvo/admin/index.html'>Click here</a> to continue.</td></tr><table>");
    return;
  }
  /* Grid */
  listClass('layerInfo',{_userID:userID})
  setTimeout(function() {           // Give the form time to build, then add
    $("#userID").val(userID);       // the current userID and authCode to
    $("#authCode").val(authCode);   // hidden fields in the form.
    $("#owner").change(function() {
      alert("Changed ");
    });
  }, 200);
  //  Add dragability to specific windows
  $(function() {
    $("#innerdiv").draggable({ handle: "#formHeader" });
    $(".confirm").draggable({ handle: ".confirmMsg" });
  });
});

var waitCount = 0
function waiting(on)
{
  if ( on ) {
    waitCount += 1;
    $("#waiting").slideDown(500);
  }
  else {
    waitCount -= 1;
    if (waitCount <= 0) {
      $("#waiting").hide(200);
      waitCount = 0;
    }
  }
}

function addNew()
{
  updateMode = "insert";
  g_dataObj.uniqueID = 0;   // Use the last displayed forms values as defaults
  populate(g_dataObj, jsn._attributes, jsn._attributes['_defaults']);
}
function insert() {
  $("#userID").val(userID);
  $("#authCode").val(authCode);
  updateMode = "insert";
  save();
}

var updateMode = "update";
function save()
{
  $("#userID").val(userID);
  $("#authCode").val(authCode);
  if (checkFormValues()) {
    var jsonData = encodeFormData();
    update(jsonData);
  }
}

function closeConfirm()
{
  $("#confirm").slideUp(500);
}

function closeConfirmMulti()
{
  $("#confirmMulti").slideUp(500);
}
function closeForm()
{
  $("#outerdiv").hide();
}
function drop()
{
  $("#confirm").slideDown(500);
}
function dropMulti()
{
  $("#confirmMulti").slideDown(500);
}

function deleteRecord()
{
  updateMode = "delete";
  $("#userID").val(userID);
  $("#authCode").val(authCode);
  var jsonData = encodeFormData();
  update(jsonData);
  closeConfirm();
}

function editLayerInfo(what)
{
  $("#outerdiv").show(200);
  populate(oneDataObjByKey("uniqueID", what.id), jsn._attributes, jsn._attributes['_defaults']);
}

function oneDataObjByKey(theKey, theValue) {
  for (var idx in jsn.data) {
    if (jsn.data[idx][theKey] == theValue)
      return jsn.data[idx];
  }
  return false
}

var removeIds = [];
function removeProperty(what)
{
  var idx = jQuery.inArray(what.id, removeIds);
  if (idx !== -1)
    removeIds.splice(idx, 1);
  else
    removeIds.push(what.id);
  if (removeIds.length == 1) $("#deleteBtn").fadeIn(500);
  if (removeIds.length == 0) $("#deleteBtn").fadeOut(500);
}

function update(jsonObj)
{
    var theUrl = serviceUrl + updateMode + "_" + dataObjName + ".py";
    console.log("update: " + jsonObj);
    $.ajax(
    {
        url: theUrl,
        data: jsonObj,
        dataType: 'json',
        type: 'POST',
        cache: false,
        success: function(rtn) {
          if ( rtn.hasOwnProperty("ERROR") ) {
            message(rtn.ERROR);
            if (rtn.ERROR.indexOf("logged") > 0) {
              setTimeout(function() {
                logout();
              }, 3000);
            }
            return;
          }
          message(rtn.message);
          updateMode = "update";
          closeForm();
          listClass('layerInfo',{_userID:userID});
        },
        error: function (jqXHR, ajaxOptions, thrownError) {
            console.log('jqXHR.status: ' + jqXHR.status);
            console.log('jqXHR.responseText: ' + jqXHR.responseText);
            console.log('thrownError: ' + thrownError);
        }
    });
}

function checkFormValues()
{
  var msg = "";
  if (msg == "")
    return true;
  message(msg, true);
  return false;
}

var tablesBuilt = "";
function populate(dataObj, attributes, defaults)
{
  tablesBuilt = "";
  dataObj = setDefaults(dataObj, defaults);
  g_dataObj = dataObj;
  for (var key in dataObj) {
    if (key in attributes) {
      if (key == "metadata") {
        formatOneEntry(dataObj[key], attributes[key], key);
        metadata = dataObj["metadata"]
        for (metaKey in metadata) {
          var metadataFormat = layerMetadataFormat[metaKey];
          metadataFormat = setDefaults(metadataFormat, jsn._attributes['_defaults']);
          formatOneEntry(metadata[metaKey], metadataFormat, metaKey);
        }
      }
      else
        formatOneEntry(dataObj[key], attributes[key], key);
    }
  }
}

function formatOneEntry(val, formatParms, key)
{
  if (formatParms.dataType.indexOf("[]") > 0) // this element is an array - wrapped by a table
    formatTable(val, formatParms)
  else if (formatParms.tagType == "multiselect")
    $('#'+key).val(eval(val)).trigger('chosen:updated');
  else if (formatParms.tagType == "select")
    $('#'+key).val(val).trigger('chosen:updated');
  else
    $('#'+key).val(frmat(val.toString().trim(), formatParms));
}

function setDefaults(oneEntry, defaults) {
  for (var key in defaults) {
    if (!oneEntry.hasOwnProperty(key))
      oneEntry[key] = defaults[key];
  }
  return oneEntry;
}

function formatTable(theArray, formatParms)
{
  if (tablesBuilt.indexOf(formatParms.parent) > 0)
    return;
  tablesBuilt += '~' + formatParms.parent;
  var tableObj = formObj(formatParms.parent);
  var tableCols = tableObj.columns;
  var bfr = "";

  for (var r=0; r<theArray.length; r++) {
    var theValues = [];
    for (var c=0; c<tableCols.length; c++) {
      if (tableCols[c].id in dataObj)
        var val = dataObj[tableCols[c].id][r];
      else
        var val = ""
      theValues.push(frmat(val, tableCols[c]));
    }
    bfr += oneTableRow(formatParms.parent, r, tableCols, theValues);
  }
  var tag = '#tbody_' + formatParms.parent;
  $(tag).html(bfr);
  $('#'+formatParms.parent).show();
}

// formatParms are from the metadata db
function frmat(theValue, formatParms)
{
//alert(formatParms.id + ": " + theValue.toString() + ", " + formatParms.dataType);
  switch (formatParms.dataType)
  {
    case "str":
    case "str[]":
    case "bool":
      return theValue;
      break;
    case "int":
    case "int[]":
    case "json":
      return theValue.toString();
    case "dec":
      return utilFixDecimal(theValue, formatParms.decPts);
    case "date":
      return theValue.substr(0,10);
    case "intDate":
    case "intDate[]":
      var sVal = theValue.toString();
      return sVal.substr(0,4) + '-' + sVal.substr(4,2) + '-' + sVal.substr(6,2);
    default:
      return theValue;
  }
}

// Use jsgrid to list the contents of a class, retrieved from the db
// parms - javascript object - eg. {_username:"Bob"}
function listClass(theClass, parms)
{
    waiting(true);
    currentClass = theClass;
    var htmlContent = "";
    var theUrl = serviceUrl + "jsgrid_" + theClass + ".py";
    $.ajax(
    {
        url: theUrl,
        data: parms,
        dataType: 'json',
        type: 'GET',
        cache: false,
        success: function(bfr) {
          jsn = eval(bfr);
          layerMetadataDefaults = oneDataObjByKey("uniqueID", -1)["metadata"];
          layerMetadataFormat = oneDataObjByKey("uniqueID", -2)["metadata"];
          layerMetadataAttributes = oneDataObjByKey("uniqueID", -3)["metadata"];
          layerMetadataOrder = sortThese(oneDataObjByKey("uniqueID", -4)["metadata"]);
          loadJsGrid(theClass, jsn);
          buildForm(jsn._attributes, jsn._editOrder, layerMetadataOrder, layerMetadataAttributes);
          waiting(false);
        },
        error: function (jqXHR, ajaxOptions, thrownError) {
            $("#tableWrapper").jsGrid("destroy");
            $("#tableWrapper").html("<div class='noResults'>No results available</div>");
            //console.log(jqXHR.responseText);
            waiting(false);
        }
    });
}

function sortThese(dict)
{
  // Create items array
  var items = Object.keys(dict).map(function(key) {
    return [key, dict[key]];
  });
  // Sort the array based on the second element
  items.sort(function(first, second) {
    return first[1] - second[1];
  });
  return items;
}

function loadJsGrid(theClass, jsn)
{
    currentClass = theClass;
    jsGrid.sortStrategies.commaSepNbr = function(val1, val2) {
        if (val1 == null || val2 == null) return 0;
        comp1 = Number(utilReplaceAll(val1, ',', ''));
        comp1 = isNaN(comp1) ? 0.0 : comp1;
        comp2 = Number(utilReplaceAll(val2, ',', ''));
        comp2 = isNaN(comp2) ? 0.0 : comp2;
        return comp1 - comp2;
    };
    $("#tableWrapper").jsGrid("destroy");
    $("#tableWrapper").jsGrid({
        height: "100%",
        width: "100%",
        sorting: true,
        paging: false,
        selecting: false,
        data: jsn.data,
        fields: jsn.fields,
        rowClass: function (item, itemIndex) {
          if (item.uniqueID < 0 )
            return "hidden";
        }
    });



    g_fields = jsn.fields;
    $(".jsgrid-grid-body").css("height","100%");
    $("#tableWrapper").fadeIn(200);
}