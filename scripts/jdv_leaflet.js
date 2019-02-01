// ===================================
// Leaflet specific mapping interface
// ===================================

var gLayerCount;
function createMap(mapInit, layers) {
  var gLayerCount = 0;
  for (var l in layers)
    gLayerCount++;
  gMap = L.map('map');
  gMap.setView([mapInit.lat, mapInit.lon], mapInit.zoom);
}

function instantiateLayer(layers, layerKey) {
  // Do necessary leaflet instantiation
  var layer = layers[layerKey];
  var oneLayer;
  switch (layer.format) {
    case "OSM":
      if (layer.source == "BingMaps") {
        oneLayer = L.tileLayer.bing(gAccessKeys.bing, {type: layer.imagerySet});
        gLayerCount--;
      }
      break;
    case "WMS":
      oneLayer = L.tileLayer.betterWms(layer.URL, {
        layers: layer.imagerySet,
        opacity: layer.opacity
      });
      gLayerCount--;
      break;
    case "feedJSON":
      break;
    case "geoJSON":
      if (layer.geometry == "point") {
        $.getJSON(layer.URL, function(data){
          layers = pointLayer(data, layers, layerKey);
        });
      }
      break;
    case "tileLayer":
      var parms = layer.URL;
      oneLayer = L.tileLayer(parms);
      gLayerCount--;
      break;
    default:
      break;
  }
  if (layer.format != "geoJSON") {
    layer["instantiated"] = true;
    layer["leafletLayer"] = oneLayer;
    layers[layerKey] = layer;
    if (layer.visible)
      oneLayer.addTo(gMap);
    }
}

function pointLayer(data, layers, layerKey) {
  var layer = layers[layerKey];
  var oneIcon = L.icon({
    iconUrl: layer.image,
    iconSize: [12,12],
		iconAnchor: [6,6],
    popupAnchor: [0,-6],
    opacity: layer.opacity
  });
	var ptLayer = L.geoJSON(data, {
		pointToLayer: function (feature, latlng) {
			return L.marker(latlng, {icon: oneIcon});
		},
		onEachFeature: onEachPoint,
  });
  gLayerCount--;
  layer["instantiated"] = true;
  layer["leafletLayer"] = ptLayer;
  layers[layerKey] = layer;
  if (layer.visible)
    ptLayer.addTo(gMap);
  return layers;
}

function onEachPoint(feature, leafletLayer) {
	if (feature.properties) {
		var popupContent = "<p>" + feature.properties.Title + "<br>" +
      feature.properties.Address + "</p>";
	}
	leafletLayer.bindPopup(popupContent);
}

// =============================================================================
// BetterWMS - From: http://bl.ocks.org/rclark/6908938

L.TileLayer.BetterWMS = L.TileLayer.WMS.extend({

  onAdd: function (gMap) {
    // Triggered when the layer is added to a map.
    //   Register a click listener, then do all the upstream WMS things
    L.TileLayer.WMS.prototype.onAdd.call(this, gMap);
    gMap.on('click', this.getFeatureInfo, this);
  },

  onRemove: function (gMap) {
    // Triggered when the layer is removed from a map.
    //   Unregister a click listener, then do all the upstream WMS things
    L.TileLayer.WMS.prototype.onRemove.call(this, gMap);
    gMap.off('click', this.getFeatureInfo, this);
  },

  getFeatureInfo: function (evt) {
    // Make an AJAX request to the server and hope for the best
    var url = this.getFeatureInfoUrl(evt.latlng),
        showResults = L.Util.bind(this.showGetFeatureInfo, this);
    $.ajax({
      url: url,
      success: function (data, status, xhr) {
        var err = typeof data === 'string' ? null : data;
        showResults(err, evt.latlng, data);
      },
      error: function (xhr, status, error) {
        showResults(error);
      }
    });
  },

  getFeatureInfoUrl: function (latlng) {
    // Construct a GetFeatureInfo request URL given a point
    var point = this._map.latLngToContainerPoint(latlng, this._map.getZoom()),
        size = this._map.getSize(),

        params = {
          request: 'GetFeatureInfo',
          service: 'WMS',
          srs: 'EPSG:4326',
          styles: this.wmsParams.styles,
          transparent: this.wmsParams.transparent,
          version: this.wmsParams.version,
          format: this.wmsParams.format,
          bbox: this._map.getBounds().toBBoxString(),
          height: size.y,
          width: size.x,
          layers: this.wmsParams.layers,
          query_layers: this.wmsParams.layers,
          info_format: 'text/html'
        };

    params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
    params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

    return this._url + L.Util.getParamString(params, this._url, true);
  },

  showGetFeatureInfo: function (err, latlng, content) {
    if (err) { console.log(err); return; } // do nothing if there's an error

    // Otherwise show the content in a popup, or something.
    L.popup({ maxWidth: 800})
      .setLatLng(latlng)
      .setContent(content)
      .openOn(this._map);
  }
});

L.tileLayer.betterWms = function (url, options) {
  return new L.TileLayer.BetterWMS(url, options);
};

// End BetterWMS
// =============================================================================
