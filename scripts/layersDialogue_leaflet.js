// Build a layers dialogue using leaflet methods
//
function layersDialogue(layers) {
  var baseLayers = {};
  var overlays = {}
  for (layer in layers) {
    var oneLayer = layers[layer];
    oneLayer.leafletLayer["selectable"] = oneLayer.select;
    oneLayer.leafletLayer["objName"] = layer;
    if (layer.indexOf("Basemap") != 0)
      overlays[oneLayer.text] = oneLayer.leafletLayer;
    else
      baseLayers[oneLayer.text] = oneLayer.leafletLayer;
  }
  L.control.layers(baseLayers, overlays).addTo(map);
  setTimeout(function() {
    jQuery(".leaflet-control-layers-selector-rt").click(function(){
        gSelectLayerKey = this.id;
    });
  }, 100);
}
