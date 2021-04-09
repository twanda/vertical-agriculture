odoo.define('vertical_agriculture.GeoengineRenderer', function (require) {
    "use strict";
    
    
    var BasicRenderer = require('web.BasicRenderer');
    var utils = require('web.utils');
    var QWeb = require('web.QWeb');
    var session = require('web.session');

    var Record = require('base_geoengine.Record');
    var GeoengineRecord = Record.GeoengineRecord;
    var geoengine_common = require('base_geoengine.geoengine_common');
    var BackgroundLayers = require('base_geoengine.BackgroundLayers');
    
    var GeoEngineRenderer = require('base_geoengine.GeoengineRenderer');
    
    
    GeoEngineRenderer.include({
    	_renderVectorLayers: function () {
	        var data = this.state.data;
	
	        this.map.removeLayer(this.overlaysGroup);
	        this.ids = {};
	        
	        var vectorLayers = this._createVectorLayers(data);
	        this.overlaysGroup = new ol.layer.Group({
	            title: 'Overlays',
	            layers: vectorLayers,
	        });
	
	        this._createPopupOverlay();
	
	        _.each(vectorLayers, function (vlayer) {
	            // First vector always visible on startup
	            if (vlayer !== vectorLayers[0] &&
	                !vlayer.values_.active_on_startup) {
	                vlayer.setVisible(false);
	            }
	        });
	        this.map.addLayer(this.overlaysGroup);
	        this.map.addOverlay(this.overlayPopup);
	
	        // Zoom to data extent
	        if (data.length) {
	        	console.log("Vector Layers---",vectorLayers)
	        	if(vectorLayers.length > 0) {
	        		var extent = vectorLayers[0].getSource().getExtent();
	                this.zoomToExtentCtrl.extent_ = extent;
	                this.zoomToExtentCtrl.changed();
	
	                // When user quits fullscreen map, the size is set to undefined
	                // So we have to check this and recompute the size.
	                if (typeof this.map.getSize() === 'undefined' ) {
	                    this.map.updateSize();
	                }
	                if (!ol.extent.isEmpty(extent)) {
	                    this.map.getView().fit(extent);
	                }
	        	}
	        }
	    },
    })
    
    
});