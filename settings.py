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
from layer_field_combo import layer,field,layerFieldCombo

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class IntersectItSettings():
	def __init__(self):
		# load settings
		self.pluginName = "IntersectIt"
		self.settings = QSettings(self.pluginName,self.pluginName)
		
		self.globalDefaultValue = {	"rubber_colorR" : 0,
									"rubber_colorG" : 0,
									"rubber_colorB" : 255,
									"rubber_width"  : 2,
									"placeDimension": 1,
									"placeMeasure"  : 1,
									"placePrecision": 0,
									"snapping"      : 1,
									"tolerance"     : 1,
									"units"         : "map",
									"defaultPrecisionDistance"    : 25,
									"defaultPrecisionOrientation" : .01
								}
								
		self.projectDefaultValue = {"dimension_layer": "",
									"measure_field": "",									
									"precision_field": "",									
									"intersection_layer": ""									
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
			return self.settings.setValue( setting, value )
		elif setting in self.projectDefaultValue:
			return QgsProject.instance().writeEntry( self.pluginName, setting , value )
		else:
			raise NameError('IntersectIt has no setting %s' % setting)

		

# create the dialog to connect layers
class settingsDialog(QDialog, Ui_Settings):
	def __init__(self,iface):
		self.iface = iface
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		QObject.connect(self , SIGNAL( "accepted()" ) , self.applySettings)
		# load settings
		self.settings = IntersectItSettings()
		
		self.snapBox.setChecked( self.settings.value( "snapping").toInt()[0] ) 
		self.tolerance.setValue(self.settings.value("tolerance").toDouble()[0])
		if self.settings.value( "units" ).toString() == "map":
			self.mapUnits.setChecked(True)
			self.pixels.setChecked(False)
		else:
			self.mapUnits.setChecked(False)
			self.pixels.setChecked(True)
		self.rubberWidth.setValue(self.settings.value("rubber_width").toDouble()[0])
		self.colorR = self.settings.value("rubber_colorR").toInt()[0]
		self.colorG = self.settings.value("rubber_colorG").toInt()[0]
		self.colorB = self.settings.value("rubber_colorB").toInt()[0]
		self.color = QColor(self.colorR,self.colorG,self.colorB,255)
		self.applyColorStyle()
		self.placeDimensionBox.setChecked(       self.settings.value( "placeDimension"       ).toInt()[0] ) 
		self.placeMeasureBox.setChecked( self.settings.value( "placeMeasure" ).toInt()[0] ) 
		self.placePrecisionBox.setChecked( self.settings.value( "placePrecision" ).toInt()[0] ) 
		self.defaultPrecisionDistanceBox.setValue( self.settings.value( "defaultPrecisionDistance" ).toDouble()[0] ) 
		self.defaultPrecisionOrientationBox.setValue( self.settings.value( "defaultPrecisionOrientation" ).toDouble()[0] )
		
		# Management of layer/fields combos
		dimensionLayerCombo           = layer( self.dimensionLayerCombo, lambda: self.settings.value("dimension_layer") )
		dimensionMeasureFieldCombo    = field( self.measureFieldCombo,   lambda: self.settings.value("measure_field"),  QMetaType.QString )
		dimensionPrecisionFieldCombo  = field( self.precisionFieldCombo, lambda: self.settings.value("precision_field"), QMetaType.QString )
		intersectionLayerCombo        = layer( self.dimensionLayerCombo, lambda: self.settings.value("intersection_layer") )
		self.dimensionLayerManage     = layerFieldCombo(iface.mapCanvas(),  dimensionLayerCombo,     [dimensionMeasureFieldCombo, dimensionPrecisionFieldCombo])
		self.intersectionLayerManage  = layerFieldCombo(iface.mapCanvas(),  intersectionLayerCombo , [] )
		
	def showEvent(self, e):
		self.dimensionLayerManage.onDialogShow()
		self.intersectionLayerManage.onDialogShow()

			
	@pyqtSignature("on_placeDimensionBox_toggled(bool)")
	def on_placeDimensionBox_toggled(self,b):
		self.dimensionLayerCombo.setEnabled(b)
		self.placeMeasureBox.setEnabled(b)
		self.measureFieldCombo.setEnabled(b)
		self.placePrecisionBox.setEnabled(b)
		self.precisionFieldCombo.setEnabled(b)
		
	def applySettings(self):
		self.settings.setValue( "snapping" , int(self.snapBox.isChecked()) )
		self.settings.setValue( "defaultPrecisionOrientation" , self.defaultPrecisionOrientationBox.value()) 
		self.settings.setValue( "defaultPrecisionDistance"    , self.defaultPrecisionDistanceBox.value()) 
		self.settings.setValue( "tolerance" , self.tolerance.value() )
		if self.mapUnits.isChecked():
			self.settings.setValue( "units" , "map")
		else:
			self.settings.setValue( "units" , "pixels")		
		self.settings.setValue( "rubber_width"   , self.rubberWidth.value() )	
		self.settings.setValue( "rubber_colorR"  , self.color.red() )
		self.settings.setValue( "rubber_colorG"  , self.color.green() )
		self.settings.setValue( "rubber_colorB"  , self.color.blue() )
		self.settings.setValue( "placeDimension"       , int(self.placeDimensionBox.isChecked()) )
		self.settings.setValue( "placePrecision" , int(self.placePrecisionBox.isChecked()) )
		self.settings.setValue( "placeMeasure" , int(self.placeMeasureBox.isChecked()) )
		if self.dimensionLayer() is False: dimLayerId = ''
		else: dimLayerId = self.dimensionLayer().id()		
		QgsProject.instance().writeEntry("IntersectIt", "dimension_layer", dimLayerId)
		QgsProject.instance().writeEntry("IntersectIt", "dimension_field", self.measureFieldCombo.currentText() )
		QgsProject.instance().writeEntry("IntersectIt", "precision_field", self.precisionFieldCombo.currentText() )

	@pyqtSignature("on_rubberColor_clicked()")
	def on_rubberColor_clicked(self):
		self.color = QColorDialog.getColor(self.color)
		self.applyColorStyle()
		
	def applyColorStyle(self):
		self.rubberColor.setStyleSheet("background-color: rgb(%u,%u,%u)" % (self.color.red(),self.color.green(),self.color.blue()))	
