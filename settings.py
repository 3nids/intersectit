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

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class IntersectItSettings():
	def __init__(self):
		# load settings
		self.settings = QSettings("IntersectIt","IntersectIt")
		
		self.defaultValue = {	"rubber_colorR" : 0,
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
	
	def value(self,setting):
		if setting not in self.defaultValue:
			raise NameError('IntersectIt has no setting %s' % setting)
		return self.settings.value(setting,self.defaultValue.get(setting))
		
	def setValue(self,setting,value):
		if setting not in self.defaultValue:
			raise NameError('IntersectIt has no setting %s' % setting)
		self.settings.setValue(setting,value)
		
		

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
		
	def showEvent(self, e):
		self.layers = self.iface.mapCanvas().layers()
		dimLayerId = QgsProject.instance().readEntry("IntersectIt", "dimension_layer", "")[0]
		intLayerId = QgsProject.instance().readEntry("IntersectIt", "intersection_layer", "")[0]
		self.dimensionLayerCombo.clear()
		self.intersectionLayerCombo.clear()
		self.dimensionLayerCombo.addItem(_fromUtf8(""))
		self.intersectionLayerCombo.addItem(_fromUtf8(""))
		for i,layer in enumerate(self.layers):
			self.dimensionLayerCombo.addItem(layer.name())
			self.intersectionLayerCombo.addItem(layer.name())
			if layer.id() == dimLayerId: self.dimensionLayerCombo.setCurrentIndex(i+1)
			if layer.id() == intLayerId: self.intersectionLayerCombo.setCurrentIndex(i+1)
		self.updateFieldsCombo()
			
	@pyqtSignature("on_placeDimensionBox_toggled(bool)")
	def on_placeDimensionBox_toggled(self,b):
		self.dimensionLayerCombo.setEnabled(b)
		self.placeMeasureBox.setEnabled(b)
		self.measureFieldCombo.setEnabled(b)
		self.placePrecisionBox.setEnabled(b)
		self.precisionFieldCombo.setEnabled(b)
			
	@pyqtSignature("on_dimensionLayerCombo_currentIndexChanged(int)")
	def on_dimensionLayerCombo_currentIndexChanged(self,i):
		error_msg = ''
		if i > 0:
			layer = self.layers[i-1]
			if layer.type() != QgsMapLayer.VectorLayer:
				error_msg = QApplication.translate("IntersectIt", "The dimension layer must be a vector layer.", None, QApplication.UnicodeUTF8) 
			elif layer.hasGeometryType() is False:
				error_msg = QApplication.translate("IntersectIt", "The dimension layer has no geometry.", None, QApplication.UnicodeUTF8) 
			else:
				# TODO CHECK GEOMETRY
				print layer.dataProvider().geometryType() , layer.geometryType()
		if error_msg != '':
			self.dimensionLayerCombo.setCurrentIndex(0)
			QMessageBox.warning( self , "IntersectIt", error_msg )
		# update field list
		self.updateFieldsCombo()
		
	@pyqtSignature("on_measureFieldCombo_currentIndexChanged(int)")
	def on_measureFieldCombo_currentIndexChanged(self,i):
		if self.dimensionLayer() is not False and i > 0:
			field = self.measureFieldCombo.currentText()
			i = self.dimensionLayer().dataProvider().fieldNameIndex(field)
			# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
			if self.dimensionLayer().dataProvider().fields()[i].type() != 10:
				QMessageBox.warning( self , "IntersectIt" ,  QApplication.translate("IntersectIt", "The dimension field must be a varchar or a text.", None, QApplication.UnicodeUTF8) )
				self.measureFieldCombo.setCurrentIndex(0)
				
	@pyqtSignature("on_precisionFieldCombo_currentIndexChanged(int)")
	def on_precisionFieldCombo_currentIndexChanged(self,i):
		if self.dimensionLayer() is not False and i > 0:
			field = self.precisionFieldCombo.currentText()
			i = self.dimensionLayer().dataProvider().fieldNameIndex(field)
			# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
			if self.dimensionLayer().dataProvider().fields()[i].type() != 10:
				QMessageBox.warning( self , "IntersectIt" ,  QApplication.translate("IntersectIt", "The precision field must be a varchar or a text.", None, QApplication.UnicodeUTF8) )
				self.precisionFieldCombo.setCurrentIndex(0)
			
	def dimensionLayer(self):
		i = self.dimensionLayerCombo.currentIndex()
		if i == 0: return False
		else: return self.layers[i-1]
				
	def updateFieldsCombo(self):
		self.measureFieldCombo.clear()
		self.precisionFieldCombo.clear()
		self.measureFieldCombo.addItem(_fromUtf8(""))
		self.precisionFieldCombo.addItem(_fromUtf8(""))
		if self.dimensionLayer() is False: return
		l = 1
		for field in self.dimensionLayer().dataProvider().fieldNameMap():
			self.measureFieldCombo.addItem(_fromUtf8("") )
			self.measureFieldCombo.setItemText( l, field )
			if field == QgsProject.instance().readEntry("IntersectIt", "dimension_field", "")[0]:
				self.measureFieldCombo.setCurrentIndex(l)	
			l += 1
		l = 1
		for field in self.dimensionLayer().dataProvider().fieldNameMap():
			self.precisionFieldCombo.addItem(_fromUtf8("") )
			self.precisionFieldCombo.setItemText( l, field )
			if field == QgsProject.instance().readEntry("IntersectIt", "precision_field", "")[0]:
				self.precisionFieldCombo.setCurrentIndex(l)	
			l += 1

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
