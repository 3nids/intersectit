"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Settings dialog
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui_settings import Ui_Settings
from layer_field_combo import layerCombo,fieldCombo,layerFieldCombo

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class IntersectItSettings():
	def __init__(self):
		# load settings
		self.pluginName = "IntersectIt"
		self.settings = QSettings(self.pluginName,self.pluginName)
		
		self.globalDefaultValue = {	"rubberColorR"      : 0,
									"rubberColorG"      : 0,
									"rubberColorB"      : 255,
									"rubberWidth"       : 2,
									"placeDimension"    : 1,
									"placeMeasure"      : 1,
									"placePrecision"    : 0,
									"displayReport"     : 1,
									"placeIntersection" : 0,
									"placeReport"       : 0,
									"snapping"          : 1,
									"tolerance"         : 1,
									"units"             : "map",
									"defaultPrecisionDistance"    : 25,
									"defaultPrecisionOrientation" : .01
								}
								
		self.projectDefaultValue = {"dimensionLayer"   : "",
									"measureField"     : "",									
									"precisionField"   : "",									
									"intersectionLayer": "",									
									"reportField"      : "",								
									"memoryLineLayer"  : "",								
									"memoryPointLayer" : ""								
								}
	
	def value(self,setting):
		if setting in self.globalDefaultValue:
			return self.settings.value( setting, self.globalDefaultValue[setting] )
		elif setting in self.projectDefaultValue:
			return QgsProject.instance().readEntry( self.pluginName, setting , self.projectDefaultValue[setting] )[0]
		else:
			raise NameError('IntersectIt has no setting %s' % setting)
		
		
	def setValue(self,setting,value):
		if setting in self.globalDefaultValue:
			self.settings.setValue( setting, value )
		elif setting in self.projectDefaultValue:
			QgsProject.instance().writeEntry( self.pluginName, setting , value )
		else:
			raise NameError('IntersectIt has no setting %s' % setting)

		

# create the dialog to connect layers
class settingsDialog(QDialog, Ui_Settings):
	def __init__(self,iface):
		self.iface = iface
		QDialog.__init__(self)
		self.setupUi(self)
		QObject.connect(self , SIGNAL( "accepted()" ) , self.applySettings)
		# load settings
		self.settings = IntersectItSettings()
				
		# Management of layer/fields combos
		dimensionLayerCombo           = layerCombo( self.dimensionLayerCombo,    lambda: self.settings.value("dimensionLayer") )
		dimensionMeasureFieldCombo    = fieldCombo( self.measureFieldCombo,      lambda: self.settings.value("measureField"),  QMetaType.QString )
		dimensionPrecisionFieldCombo  = fieldCombo( self.precisionFieldCombo,    lambda: self.settings.value("precisionField"), QMetaType.QString )
		intersectionLayerCombo        = layerCombo( self.intersectionLayerCombo, lambda: self.settings.value("intersectionLayer") )
		intersectionReportFieldCombo  = fieldCombo( self.reportFieldCombo,       lambda: self.settings.value("reportField"), QMetaType.QString )
		self.dimensionLayerManage     = layerFieldCombo(iface.mapCanvas(), self, dimensionLayerCombo,     [dimensionMeasureFieldCombo, dimensionPrecisionFieldCombo])
		self.intersectionLayerManage  = layerFieldCombo(iface.mapCanvas(), self, intersectionLayerCombo , [intersectionReportFieldCombo] )
		
	def showEvent(self, e):
		# observations
		self.snapBox.setChecked( self.settings.value( "snapping").toInt()[0] ) 
		self.defaultPrecisionDistanceBox.setValue(    self.settings.value( "defaultPrecisionDistance" ).toDouble()[0] ) 
		self.defaultPrecisionOrientationBox.setValue( self.settings.value( "defaultPrecisionOrientation" ).toDouble()[0] )
		# intersection - selection
		self.tolerance.setValue( self.settings.value("tolerance").toDouble()[0])
		if self.settings.value( "units" ).toString() == "map":
			self.mapUnits.setChecked(True)
			self.pixels.setChecked(False)
		else:
			self.mapUnits.setChecked(False)
			self.pixels.setChecked(True)
		self.rubberWidth.setValue(self.settings.value("rubberWidth").toDouble()[0])
		self.colorR = self.settings.value("rubberColorR").toInt()[0]
		self.colorG = self.settings.value("rubberColorG").toInt()[0]
		self.colorB = self.settings.value("rubberColorB").toInt()[0]
		self.color = QColor(self.colorR,self.colorG,self.colorB,255)
		self.applyColorStyle()
		# intersection - intersection
		self.intersectionLayerManage.onDialogShow()
		self.placeDimensionBox.setChecked(self.settings.value( "displayReport"    ).toInt()[0] ) 
		self.placeMeasureBox.setChecked(  self.settings.value( "placeIntersection").toInt()[0] ) 
		self.placePrecisionBox.setChecked(self.settings.value( "placeReport"      ).toInt()[0] ) 
		# dimensions
		self.dimensionLayerManage.onDialogShow()
		self.placeDimensionBox.setChecked(self.settings.value( "placeDimension").toInt()[0] ) 
		self.placeMeasureBox.setChecked(  self.settings.value( "placeMeasure"  ).toInt()[0] ) 
		self.placePrecisionBox.setChecked(self.settings.value( "placePrecision").toInt()[0] ) 

	@pyqtSignature("on_placeDimensionBox_toggled(bool)")
	def on_placeDimensionBox_toggled(self,b):
		self.dimensionLayerCombo.setEnabled(b)
		self.placeMeasureBox.setEnabled(b)
		self.measureFieldCombo.setEnabled(b)
		self.placePrecisionBox.setEnabled(b)
		self.precisionFieldCombo.setEnabled(b)
		
	def applySettings(self):
		# observations
		self.settings.setValue( "snapping" , int(self.snapBox.isChecked()) )
		self.settings.setValue( "defaultPrecisionDistance"    , self.defaultPrecisionDistanceBox.value()) 
		self.settings.setValue( "defaultPrecisionOrientation" , self.defaultPrecisionOrientationBox.value()) 
		# intersection - selection
		self.settings.setValue( "tolerance" , self.tolerance.value() )
		if self.mapUnits.isChecked():
			self.settings.setValue( "units" , "map")
		else:
			self.settings.setValue( "units" , "pixels")		
		self.settings.setValue( "rubberWidth"   , self.rubberWidth.value() )	
		self.settings.setValue( "rubberColorR"  , self.color.red() )
		self.settings.setValue( "rubberColorG"  , self.color.green() )
		self.settings.setValue( "rubberColorB"  , self.color.blue() )
		# intersection - result
		self.settings.setValue( "displayReport"     , int(self.displayReportBox.isChecked()) )
		self.settings.setValue( "placeIntersection" , int(self.placeIntersectionBox.isChecked()) )
		self.settings.setValue( "placeReport"       , int(self.placeReportBox.isChecked()) )
		if self.intersectionLayerManage.getLayer() is False: intLayerId = ''
		else: intLayerId = self.intersectionLayerManage.getLayer().id()
		self.settings.setValue("intersectionLayer" , intLayerId )
		self.settings.setValue("reportField"       , self.measureFieldCombo.currentText()   )
		# dimensions
		self.settings.setValue( "placeDimension" , int(self.placeDimensionBox.isChecked()) )
		self.settings.setValue( "placePrecision" , int(self.placePrecisionBox.isChecked()) )
		self.settings.setValue( "placeMeasure"   , int(self.placeMeasureBox.isChecked()) )
		if self.dimensionLayerManage.getLayer() is False: dimLayerId = ''
		else: dimLayerId = self.dimensionLayerManage.getLayer().id()
		self.settings.setValue("dimensionLayer", dimLayerId )
		self.settings.setValue("measureField"  , self.measureFieldCombo.currentText()   )
		self.settings.setValue("precisionField", self.precisionFieldCombo.currentText() )

	@pyqtSignature("on_rubberColor_clicked()")
	def on_rubberColor_clicked(self):
		self.color = QColorDialog.getColor(self.color)
		self.applyColorStyle()
		
	def applyColorStyle(self):
		self.rubberColor.setStyleSheet("background-color: rgb(%u,%u,%u)" % (self.color.red(),self.color.green(),self.color.blue()))	
