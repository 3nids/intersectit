"""
Plain Geometry Editor
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2013
"""
from PyQt4.QtGui import QColor,QDialog

from qgistools.pluginsettings import *
from qgistools.gui import VectorLayerCombo, FieldCombo

from ui.ui_settings import Ui_Settings

pluginName = "intersectit"

intersectItSettings = [
	# global settings
	Bool(   pluginName, "obsSnapping"                   , "global",  True )           ,
	Double( pluginName, "obsDefaultPrecisionDistance"   , "global",  25   )           ,
	Double( pluginName, "obsDefaultPrecisionOrientation", "global",  .01  )           ,
	Bool(   pluginName, "intersecResultConfirm"         , "global",  True )           ,
	Double( pluginName, "intersecSelectTolerance"       , "global",  0.3  )           ,
	String( pluginName, "intersecSelectUnits"           , "global",  "map")           ,
	Color(  pluginName, "intersectRubberColor"          , "global",  QColor(0,0,255) ),
	Double( pluginName, "intersectRubberWidth"          , "global",  2    )           ,
	Integer(pluginName, "intersecLSmaxIter"             , "global",  15   )           ,
	Double( pluginName, "intersecLSconvergeThreshold"   , "global",  .0005)           ,
	
	# project settings
	Bool(pluginName, "intersecResultPlacePoint" , "project", False),
	Bool(pluginName, "intersecResultPlaceReport", "project", False),
	Bool(pluginName, "dimenPlaceDimension"      , "project", True ),
	Bool(pluginName, "dimenPlaceMeasure"        , "project", True ),
	Bool(pluginName, "dimenPlacePrecision"      , "project", False),
	# fields and layers
	String(pluginName, "dimensionLayer", "project", "")   ,
	String(pluginName, "measureField", "project", "")     ,
	String(pluginName, "precisionField", "project", "")   ,
	String(pluginName, "intersectionLayer", "project", ""),
	String(pluginName, "reportField", "project", "")      ,
	String(pluginName, "memoryLineLayer", "project", "")  ,
	String(pluginName, "memoryPointLayer", "project", "") 
]

class IntersectItSettings(PluginSettings):
	def __init__(self):
		PluginSettings.__init__(self, pluginName, intersectItSettings)

class SettingsDialog( QDialog, Ui_Settings, PluginSettings):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.setupUi(self)
		PluginSettings.__init__(self, pluginName, intersectItSettings)
		
		self.dimensionLayerCombo = VectorLayerCombo(iface, self.dimensionLayer, lambda: self.value("dimensionLayer"), {"groupLayers":False,"hasGeometry":True})
		self.measureFieldCombo   = FieldCombo(self.measureField,   self.dimensionLayerCombo, lambda: self.value("measureField"))
		self.precisionFieldCombo = FieldCombo(self.precisionField, self.dimensionLayerCombo, lambda: self.value("precisionField"))
        
		self.intersectionLayerCombo = VectorLayerCombo(iface, self.intersectionLayer, lambda: self.value("intersectionLayer"), {"groupLayers":True,"hasGeometry":True})
		self.reportFieldCombo       = FieldCombo(self.reportField, self.intersectionLayerCombo, lambda: self.value("reportField"))
