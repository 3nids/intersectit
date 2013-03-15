"""
Plain Geometry Editor
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2013
"""
from PyQt4.QtGui import QColor,QDialog

from qgistools.pluginsettings.pluginsettings import PluginSettings
from qgistools.layerfieldcombomanager import LayerCombo, FieldCombo

from ui.ui_settings import Ui_Settings

pluginName = "intersectit"


class MySettings(PluginSettings):
	def __init__(self, uiObject=None, setValuesOnDialogAccepted=True):
		PluginSettings.__init__(self, pluginName, uiObject, setValuesOnDialogAccepted)
		# global settings
		self.addSetting("obsSnapping"                   , "global", "bool"  , True )
		self.addSetting("obsDefaultPrecisionDistance"   , "global", "double", 25   )
		self.addSetting("obsDefaultPrecisionOrientation", "global", "double", .01  )
		self.addSetting("intersecResultConfirm"         , "global", "bool"  , True )
		self.addSetting("intersecSelectTolerance"       , "global", "double", 0.3  )
		self.addSetting("intersecSelectUnits"           , "global", "string", "map")
		self.addSetting("intersectRubberColor"          , "global", "color" , QColor(0,0,255) )
		self.addSetting("intersectRubberWidth"          , "global", "double", 2    )
		self.addSetting("intersecLSmaxIter"             , "global", "int"   , 15   )
		self.addSetting("intersecLSconvergeThreshold"   , "global", "double", .0005)
        
		# project settings
		self.addSetting("intersecResultPlacePoint" , "project", "bool", False)
		self.addSetting("intersecResultPlaceReport", "project", "bool", False)
		self.addSetting("dimenPlaceDimension"      , "project", "bool", True )
		self.addSetting("dimenPlaceMeasure"        , "project", "bool", True )
		self.addSetting("dimenPlacePrecision"      , "project", "bool", False)
		# fields and layers
		self.addSetting("dimensionLayer", "project", "string", "")
		self.addSetting("measureField", "project", "string", "")
		self.addSetting("precisionField", "project", "string", "")
		self.addSetting("intersectionLayer", "project", "string", "")
		self.addSetting("reportField", "project", "string", "")
		self.addSetting("memoryLineLayer", "project", "string", "")
		self.addSetting("memoryPointLayer", "project", "string", "")


class MySettingsDialog( QDialog, Ui_Settings):
	def __init__(self, iface):
		QDialog.__init__(self)
		self.setupUi(self)
		
		self.settings = MySettings(self)

		self.dimensionLayerCombo = LayerCombo(iface, self.dimensionLayer, lambda: self.settings.value("dimensionLayer"), True)
		self.measureFieldCombo   = FieldCombo(self.measureField,   self.dimensionLayerCombo, lambda: self.settings.value("measureField"))
		self.precisionFieldCombo = FieldCombo(self.precisionField, self.dimensionLayerCombo, lambda: self.settings.value("precisionField"))
        
		self.intersectionLayerCombo = LayerCombo(iface, self.intersectionLayer, lambda: self.settings.value("intersectionLayer"), True)
		self.reportFieldCombo       = FieldCombo(self.reportField, self.intersectionLayerCombo, lambda: self.settings.value("reportField"))

	def showEvent(self, e):
		self.settings.setWidgetsFromValues()
