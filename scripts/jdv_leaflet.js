// ===================================
// Leaflet specific mapping interface
// ===================================

var gLayerCount = 0;
var gSelectLayerKey = "";
var gLayers;
var foxLayer
var leafletLayer;
var gLayerKey;

function createMap(mapInit, layers) {
  gLayerCount = 0;
  gLayers = layers;
  for (var l in layers)
    gLayerCount++;
  map = L.map('map');
  map.setView([mapInit.lat, mapInit.lon], mapInit.zoom);
  setupSelections();
  $('.leaflet-container').css('cursor','default');
}

// Select ======================================================================
//
var drawControl;
var gSelectLayers, gDrawLayers;
var currentlySelecting = false;
var selectLayer, drawLayer;
var selectedPolygonStyle;
var selectedIcon;
var selectedMarkerOptions;
var gMarkerLatLng;

function setupSelections() {
  gSelectLayers = new L.FeatureGroup();
  gDrawLayers = new L.FeatureGroup();

  map.addLayer(gSelectLayers);
  drawControl = new L.Control.Draw({
      draw: {
          marker   : true,
          polygon  : true,
          polyline : false,
          rectangle: true,
          circle   : {
              metric: 'metric'
          }
      },
      edit: {
         featureGroup: gSelectLayers,
         edit: false
      }
  });
  drawControl.addTo(map);

  L.Rectangle.include({
    contains: function (latLng) {
      return this.getBounds().contains(latLng);
    }
  });

  L.Polygon.include({
    contains: function (latLng) {
      return turf.inside(new L.Marker(latLng).toGeoJSON(), this.toGeoJSON());
    }
  });

  L.Circle.include({
    contains: function (latLng) {
      return this.getLatLng().distanceTo(latLng) < this.getRadius();
    }
  });

  L.Marker.include({
    contains: function (latLng) {
      return this.getLatLng().distanceTo(latLng) < 5000;
    }
  });

  // Styling
  var redCircle = L.divIcon({className: 'leaflet-div-icon-redCircle'});
  var defaultIcon = L.divIcon({className: 'leaflet-div-icon'});
  selectedIcon = redCircle;
  selectedPolygonStyle =  {  // Global
      weight: 2,
      opacity: 1,
      color: 'green',
      fillOpacity: 0.2,
      fillColor: 'yellow'
  };

  selectedMarkerOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
  };

  map.on(L.Draw.Event.CREATED, function (e) {
    if (gSelectLayerKey == "")
    {
      message("No layer currently set selectable", 5);
      return;
    }
    foxLayer = gLayers[gSelectLayerKey]
    leafletLayer = foxLayer.leafletLayer;
    selectLayer = new L.layerGroup();
    drawLayer = new L.layerGroup();
    e.layer.addTo(drawLayer);
    if (e.layerType == "marker") {
      gMarkerLatLng = e.layer.getLatLng();
      // return;
    }

    if (foxLayer.format === "geoJSON") {
      switch (foxLayer.geometry) {
        case "point":
          var marker;
          var latLng;
          var markerCount = 0;
          for (_layer in leafletLayer._layers) {
            latLng = leafletLayer._layers[_layer]._latlng;
            if (e.layer.contains(latLng)) {
              ++markerCount;
              marker = new L.marker(latLng, {icon: selectedIcon}); //.addTo(map);
              marker.bindPopup(leafletLayer._layers[_layer]._popup);
              marker.addTo(selectLayer);
            }
            if (markerCount > 0) {
              selectLayer.addTo(gSelectLayers);
              gSelectLayers.addTo(map);
            }
          };
          break;
        case "polygon":
          for (_layer in leafletLayer._layers) {
            latLng = leafletLayer._layers[_layer]._latlng;
          }
          break;
        case "linestring":
        case "multilinestring":
          break;
        default:
          break;
      };
    }
    else if (foxLayer.format == "WMS") {
      var radius = 0.0;
      var refPts;
      switch (e.layerType) {
        case "rectangle":
          refPts = [e.layer._bounds._northEast.lng, e.layer._bounds._northEast.lat,
                    e.layer._bounds._southWest.lng, e.layer._bounds._southWest.lat] ;
          break;
        case "circle":
          refPts = [e.layer._latlng.lng, e.layer._latlng.lat];
          radius = e.layer._mRadius;
          break;
        case "polygon":
          var ln = e.layer.editing.latlngs[0][0].length;
          refPts = new Array(ln*2+2);
          var j = 0;
          for (var i=0; i<ln; i++) {
            var lngLat = e.layer.editing.latlngs[0][0][i];
            refPts[j++] = lngLat.lng;
            refPts[j++] = lngLat.lat;
          }
          refPts[j++] = refPts[0];
          refPts[j] = refPts[1];
          break;
        case "marker":
          refPts = [gMarkerLatLng.lng, gMarkerLatLng.lat];
          radius = 5000;
          break;
      }
      buildGeoJsonSelectLayer(gSelectLayerKey, refPts, radius);
    }
  })
  // Remove all temporary layers when the garbage can is clicked
  map.on('draw:deletestart', function (e) {
    takeOutTrash();
  });

  map.on('draw:drawstart', function (e) {
    currentlySelecting = true;
  });

  map.on('draw:drawstop', function (e) {
    currentlySelecting = false;
    if (gSelectLayerKey == "")
      return;
    if (e.layerType == 'marker') {
      bullsEye(gMarkerLatLng);
    }
    drawLayer.addTo(gDrawLayers);
    gDrawLayers.addTo(map);
  });

  map.on('layerremove', function(event) {
    // If layer just turned off was the current select layer, set select layer to none.
    if (event.layer.hasOwnProperty("objName")) {
      var id = $('.leaflet-control-layers-selector-rt:checked').val();
      if (id == gSelectLayerKey) {
        $(".leaflet-control-layers-selector-rt").prop('checked', false);
        gSelectLayer = '';
      }
    }
  });
}
// end setup selections
// =============================================================================
// Selection utilities

// geoJSON returned from server as a select overlay
function addPointSelectLayer(geoJSON) {
  L.geoJson(geoJSON, {
    pointToLayer: function (feature, latlng) {
      var marker = L.circleMarker(latlng, selectedMarkerOptions);
      if (feature.properties && feature.properties.popup)
        marker.bindPopup(feature.properties.popup);
      return marker;
    }
  }).addTo(gSelectLayers);
  gSelectLayers.addTo(map);
}

function addPolygonSelectLayer(geoJSON) {
  selectLayer = new L.geoJSON(geoJSON,{
    style: selectedPolygonStyle,
    onEachFeature: selectFeaturePopup
  });
  selectLayer.addTo(gSelectLayers);
  gSelectLayers.addTo(map);
}

function selectFeaturePopup(feature, layer) {
  if (feature.properties && feature.properties.popup) {
    layer.bindPopup(feature.properties.popup);
  }
}

function bullsEye(latLng) {
  L.circle([latLng.lat, latLng.lng], {radius: 1000}).addTo(drawLayer);
  L.circle([latLng.lat, latLng.lng], {radius: 2500}).addTo(drawLayer);
  L.circle([latLng.lat, latLng.lng], {radius: 5000}).addTo(drawLayer);
}

function buildGeoJsonSelectLayer(layerKey, refPts, radius, selectLayer) {
  var callBack;
  switch (gLayers[layerKey].geometry) {
    case "point":
      callBack = addPointSelectLayer;
      break;
    case "polygon":
      callBack = addPolygonSelectLayer;
      break;
    default:
      callBack = addPolygonSelectLayer;
      break;
  }
  retrieveGeoJSON(layerKey, refPts, radius, callBack);
}

function takeOutTrash() {
	gSelectLayers.eachLayer(function (oneLayer) {
		gSelectLayers.removeLayer(oneLayer);
	});
  map.removeLayer(gSelectLayers)
	gDrawLayers.eachLayer(function (oneLayer) {
		gDrawLayers.removeLayer(oneLayer);
	});
  map.removeLayer(gDrawLayers);
  waiting(false);
}
// end selection utilities
// =============================================================================
// Instantiate a layer

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
        opacity: layer.opacity,
        transparent: true,
        format: 'image/png'
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
      oneLayer.addTo(map);
    }
}

// geoJSON points
function pointLayer(data, layers, layerKey) {
  var layer = layers[layerKey];
  gLayerKey = layerKey;
  var oneIcon = L.icon({
    iconUrl: layer.image,
    iconSize: [12,12],
		iconAnchor: [6,6],
    popupAnchor: [0,-6],
    opacity: layer.opacity
  });
	var ptLayer = L.geoJSON(data, {
		pointToLayer: function (feature, latlng) {
			var oneMarker = L.marker(latlng, {icon: oneIcon});
      oneMarker["objName"] = layerKey;
      return oneMarker;
		},
		onEachFeature: onEachPoint,
  });
  gLayerCount--;
  layer["instantiated"] = true;
  layer["leafletLayer"] = ptLayer;
  layers[layerKey] = layer;
  if (layer.visible)
    ptLayer.addTo(map);
  return layers;
}

function onEachPoint(feature, leafletLayer) {
	if (feature.properties) {
    var bfr = buildFeaturePopup(feature);
    if ( bfr )
	   leafletLayer.bindPopup(bfr);
	}
}

function loadingLayers() {
  return gLayerCount > 0 ? true : false;
}

function getMapExtent() {
  var latLng = map.getBounds();
  return [latLng[0][0], latLng[0][1], latLng[1][0], latLng[1][1]];
}

function buildFeaturePopup(feature) {
    var elList = gLayers[gLayerKey].pop_up;
    if (elList.length < 2) return false;
    var elements = elList.split(',');
    var bfr = "<table class='pTbl'><tr class='pTr0'><td class='pTd0' colspan='2'>" + feature.properties[elements[0]] +
      "</td></tr>";
    for (var i=1; i<elements.length; i++) {
      var parts = elements[i].split(':');    // element is name:description or simply name
      var desc = parts.length == 1 ? elements[i] : parts[1];
      bfr += "<tr class='pTr'><td class='pTdL'>" + desc + "</td>" +
             "<td class='pTdR'>" + feature.properties[parts[0]] + "</td></tr>";
    }
    return bfr += "</table>";
}

// =============================================================================
// BetterWMS - From: http://bl.ocks.org/rclark/6908938
// GLP - Modified

L.TileLayer.BetterWMS = L.TileLayer.WMS.extend({

  onAdd: function (map) {
    // Triggered when the layer is added to a map.
    //   Register a click listener, then do all the upstream WMS things
    L.TileLayer.WMS.prototype.onAdd.call(this, map);
    map.on('click', this.getFeatureInfo, this);
  },

  onRemove: function (map) {
    // Triggered when the layer is removed from a map.
    //   Unregister a click listener, then do all the upstream WMS things
    L.TileLayer.WMS.prototype.onRemove.call(this, map);
    map.off('click', this.getFeatureInfo, this);
  },

  getFeatureInfo: function (evt) {
    // GLP
    if (currentlySelecting) return;
    var url = this.getFeatureInfoUrl(evt.latlng),
        showResults = L.Util.bind(this.showGetFeatureInfo, this);
    $.ajax({
      url: url,
      success: function (data, status, xhr) {
        var err = typeof data === 'object' ? null : data;
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
          info_format: 'application/json'       //GLP - We can process the JSON
        };

    params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
    params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;

    return this._url + L.Util.getParamString(params, this._url, true);
  },

  showGetFeatureInfo: function (err, latlng, content) {
    // GLP - New formatting, using json object
    if (err) return; // do nothing if there's an error
    if (!content.features) return;
    if (content.features.length < 1) return;
    var leafletID = content.features[0].id.split('.')[0];
    gLayerKey = gWmsMap[leafletID];
    var bfr = buildFeaturePopup(content.features[0]);
    if ( !bfr ) return;

    L.popup({ maxWidth: 800})
      .setLatLng(latlng)
      .setContent(bfr)
      .openOn(this._map);
  }
});

L.tileLayer.betterWms = function (url, options) {
  return new L.TileLayer.BetterWMS(url, options);
};

// End BetterWMS
// =============================================================================
