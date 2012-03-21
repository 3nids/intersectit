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
		
		self.globalDefaultValue = {	"obs_snapping"                   : 1,
									"obs_defaultPrecisionDistance"   : 25,
									"obs_defaultPrecisionOrientation": .01,
									"intersect_select_tolerance"     : 0.3,
									"intersect_select_units"         : "map",
									"intersect_select_rubberColorR"  : 0,
									"intersect_select_rubberColorG"  : 0,
									"intersect_select_rubberColorB"  : 255,
									"intersect_select_rubberWidth"   : 2,
									"intersect_LS_convergeThreshold" : 0.0005,
									"intersect_LS_maxIter"           : 15,
									"intresect_result_confirm"       : 1,
									"intresect_result_placePoint"    : 0,
									"intresect_result_placeReport"   : 0,
									"dim_placeDimension"             : 1,
									"dim_placeMeasure"               : 1,
									"dim_placePrecision"             : 0									
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
		self.snapBox.setChecked( self.settings.value( "obs_snapping").toInt()[0] ) 
		self.defaultPrecisionDistanceBox.setValue(    self.settings.value( "obs_defaultPrecisionDistance" ).toDouble()[0] ) 
		self.defaultPrecisionOrientationBox.setValue( self.settings.value( "obs_defaultPrecisionOrientation" ).toDouble()[0] )
		# intersection - selection
		self.tolerance.setValue( self.settings.value("intersect_select_tolerance").toDouble()[0])
		if self.settings.value( "intersect_select_units" ).toString() == "map":
			self.mapUnits.setChecked(True)
			self.pixels.setChecked(False)
		else:
			self.mapUnits.setChecked(False)
			self.pixels.setChecked(True)
		self.rubberWidth.setValue(self.settings.value("intersect_select_rubberWidth").toDouble()[0])
		self.colorR = self.settings.value("intersect_select_rubberColorR").toInt()[0]
		self.colorG = self.settings.value("intersect_select_rubberColorG").toInt()[0]
		self.colorB = self.settings.value("intersect_select_rubberColorB").toInt()[0]
		self.color = QColor(self.colorR,self.colorG,self.colorB,255)
		self.applyColorStyle()
		# intersection - LeastSquares
		self.threshBox.setValue(  self.settings.value("intersect_LS_convergeThreshold").toDouble()[0])
		self.maxIterBox.setValue( self.settings.value("intersect_LS_maxIter"          ).toInt()[0])	
		# intersection - intersection
		self.intersectionLayerManage.onDialogShow()
		self.confirmResultBox.setChecked(self.settings.value( "intresect_result_confirm"     ).toInt()[0] ) 
		self.placeIntersectionBox.setChecked(  self.settings.value( "intresect_result_placePoint"  ).toInt()[0] ) 
		self.placeReportBox.setChecked(self.settings.value( "intresect_result_placeReport" ).toInt()[0] ) 
		# dimensions
		self.dimensionLayerManage.onDialogShow()
		self.placeDimensionBox.setChecked(self.settings.value( "dim_placeDimension" ).toInt()[0] ) 
		self.placeMeasureBox.setChecked(  self.settings.value( "dim_placeMeasure"   ).toInt()[0] ) 
		self.placePrecisionBox.setChecked(self.settings.value( "dim_placePrecision" ).toInt()[0] ) 

	@pyqtSignature("on_placeDimensionBox_toggled(bool)")
	def on_placeDimensionBox_toggled(self,b):
		self.dimensionLayerCombo.setEnabled(b)
		self.placeMeasureBox.setEnabled(b)
		self.measureFieldCombo.setEnabled(b)
		self.placePrecisionBox.setEnabled(b)
		self.precisionFieldCombo.setEnabled(b)
		
	def applySettings(self):
		# observations
		self.settings.setValue( "obs_snapping" , int(self.snapBox.isChecked()) )
		self.settings.setValue( "obs_defaultPrecisionDistance"    , self.defaultPrecisionDistanceBox.value()) 
		self.settings.setValue( "obs_defaultPrecisionOrientation" , self.defaultPrecisionOrientationBox.value()) 
		# intersection - selection
		self.settings.setValue( "intersect_select_tolerance" , self.tolerance.value() )
		if self.mapUnits.isChecked():
			self.settings.setValue( "intersect_select_units" , "map")
		else:
			self.settings.setValue( "intersect_select_units" , "pixels")		
		self.settings.setValue( "intersect_select_rubberWidth"   , self.rubberWidth.value() )	
		self.settings.setValue( "intersect_select_rubberColorR"  , self.color.red() )
		self.settings.setValue( "intersect_select_rubberColorG"  , self.color.green() )
		self.settings.setValue( "intersect_select_rubberColorB"  , self.color.blue() )
		# intersection - LeastSquares
		self.settings.setValue( "intersect_LS_convergeThreshold" , self.threshBox.value()) 
		self.settings.setValue( "intersect_LS_maxIter"           , self.maxIterBox.value()) 
		# intersection - result
		self.settings.setValue( "intresect_result_confirm"       , int(self.confirmResultBox.isChecked()) )
		self.settings.setValue( "intresect_result_placePoint"    , int(self.placeIntersectionBox.isChecked()) )
		self.settings.setValue( "intresect_result_placeReport"   , int(self.placeReportBox.isChecked()) )
		if self.intersectionLayerManage.getLayer() is False: intLayerId = ''
		else: intLayerId = self.intersectionLayerManage.getLayer().id()
		self.settings.setValue("intersectionLayer" , intLayerId )
		self.settings.setValue("reportField"       , self.reportFieldCombo.currentText()   )
		# dimensions
		self.settings.setValue( "dim_placeDimension" , int(self.placeDimensionBox.isChecked()) )
		self.settings.setValue( "dim_placeMeasure"   , int(self.placeMeasureBox.isChecked()) )
		self.settings.setValue( "dim_placePrecision" , int(self.placePrecisionBox.isChecked()) )
		if self.dimensionLayerManage.getLayer() is False: dimLayerId = ''
		else: dimLayerId = self.dimensionLayerManage.getLayer().id()
		self.settings.setValue( "dimensionLayer" , dimLayerId )
		self.settings.setValue( "measureField"   , self.measureFieldCombo.currentText()   )
		self.settings.setValue( "precisionField" , self.precisionFieldCombo.currentText() )

	@pyqtSignature("on_rubberColor_clicked()")
	def on_rubberColor_clicked(self):
		self.color = QColorDialog.getColor(self.color)
		self.applyColorStyle()
		
	def applyColorStyle(self):
		self.rubberColor.setStyleSheet("background-color: rgb(%u,%u,%u)" % (self.color.red(),self.color.green(),self.color.blue()))	
