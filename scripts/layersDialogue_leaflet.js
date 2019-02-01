// Build a layers dialogue using leaflet methods
//
function layersDialogue(layers) {
  var baseLayers = {};
  var overlays = {}
  for (layer in layers) {
    oneLayer = layers[layer];
    if (layer.indexOf("Basemap") == 0)
      baseLayers[oneLayer.text] = oneLayer.leafletLayer;
    else
      overlays[oneLayer.text] = oneLayer.leafletLayer;
  }
  L.control.layers(baseLayers, overlays).addTo(gMap);
}