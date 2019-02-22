// Build a layers dialogue using leaflet methods
//
function layersDialogue(layers) {
  var baseLayers = {};
  var overlays = {}
  var wmsMap = {};
  for (layerKey in layers) {
    var oneLayer = layers[layerKey];
    oneLayer.leafletLayer["selectable"] = oneLayer.select;
    oneLayer.leafletLayer["objName"] = layerKey;
    if (oneLayer.format == "WMS" && oneLayer.imagerySet != "") {
      var setParts = oneLayer.imagerySet.split(':');
      wmsMap[setParts.length == 2 ? setParts[1] : setParts[0]] = layerKey;
    }
    if (layerKey.indexOf("Basemap") != 0)
      overlays[oneLayer.text] = oneLayer.leafletLayer;
    else
      baseLayers[oneLayer.text] = oneLayer.leafletLayer;
  }
  L.control.layers(baseLayers, overlays, {collapsed:true}).addTo(map);
  setTimeout(function() {
    jQuery(".leaflet-control-layers-selector-rt").click(function(){
      gSelectLayerKey = this.id;
      if (!map.hasLayer(layers[gSelectLayerKey].leafletLayer)) {
        $("#msg").css({top: "15%", left: "82%"});
        message("You must turn the layer on before<br> making it the current select layer");
        $(".leaflet-control-layers-selector-rt").prop('checked', false);
      }
    });
    jQuery("span.openGroup").click(function(){
      openCloseGroup(this);
    });
    initializeGroups()
  }, 100);
  return wmsMap;
}

function openCloseGroup(what) {
  var bgPosn = $(what).css("background-position");
  var isOpen = bgPosn.indexOf("-3px") > 0 ? true : false;
  var newBgPosn = isOpen ? "left -38px" : "left -3px";
  $(what).css("background-position", newBgPosn);
  var firstDiv = $(what).parent();
  var firstChild = $(firstDiv[0]).children("div")[0];
  var delta = 200;
  $(firstChild).slideToggle(delta);
  $(firstDiv).nextUntil("div.openGroup").slideToggle(delta+=200);
}

function initializeGroups() {
  // Close all groups that don't have visible layers
  var isOpened = {};
  var i=0;
  $("div.foxgroup").each(function() {
    var checkVal = $(this).find("input:checkbox").attr("checked");
    var isChecked = checkVal === "checked" ? true : false;
    var id = $(this).find("input:checkbox").attr("id");
    var group = id.split(':')[1];
    if (isOpened.hasOwnProperty(group)) {
      if (isChecked)
        isOpened[group] = true;
    }
    else
      isOpened[group] = isChecked;
    i += 1;
  });
  for (key in isOpened) {
    if (!isOpened[key]) {
      var what = document.getElementById("spn:" + key);
      openCloseGroup(what);
    }
  }
}

