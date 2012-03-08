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

# create the dialog to connect layers
class settings(QDialog, Ui_Settings ):
	def __init__(self,iface):
		self.iface = iface
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		QObject.connect(self , SIGNAL( "accepted()" ) , self.applySettings)
		# load settings
		self.settings = QSettings("IntersectIt","IntersectIt")
		
		self.snapBox.setChecked( self.settings.value( "snapping" , 1).toInt()[0] ) 
		self.tolerance.setValue(self.settings.value("tolerance",0.3).toDouble()[0])
		if self.settings.value( "units" , "map").toString() == "map":
			self.mapUnits.setChecked(True)
			self.pixels.setChecked(False)
		else:
			self.mapUnits.setChecked(False)
			self.pixels.setChecked(True)
		self.rubberWidth.setValue(self.settings.value("rubber_width",2).toDouble()[0])
		self.colorR = self.settings.value("rubber_colorR",0  ).toInt()[0]
		self.colorB = self.settings.value("rubber_colorG",0  ).toInt()[0]
		self.colorG = self.settings.value("rubber_colorB",255).toInt()[0]
		self.color = QColor(self.colorR,self.colorG,self.colorB,255)
		self.applyColorStyle()
		self.placeArcBox.setChecked(       self.settings.value( "placeArc"       , 1).toInt()[0] ) 
		self.placeDimensionBox.setChecked( self.settings.value( "placeDimension" , 1).toInt()[0] ) 
		self.placePrecisionBox.setChecked( self.settings.value( "placePrecision" , 0).toInt()[0] ) 
		
	def showEvent(self, e):
		self.layers = self.iface.mapCanvas().layers()
		dimLayerId = QgsProject.instance().readEntry("IntersectIt", "dimension_layer", "")[0]
		self.layerCombo.clear()
		self.layerCombo.addItem(_fromUtf8(""))
		l = 1
		for layer in self.layers:
			self.layerCombo.addItem(_fromUtf8("") )
			self.layerCombo.setItemText(l, layer.name())
			if layer.id() == dimLayerId:
				self.layerCombo.setCurrentIndex(l)
			l+=1
		self.updateFieldsCombo()
			
	@pyqtSignature("on_placeArcBox_toggled(bool)")
	def on_placeArcBox_toggled(self,b):
		self.layerCombo.setEnabled(b)
		self.placeDimensionBox.setEnabled(b)
		self.dimensionFieldCombo.setEnabled(b)
		self.placePrecisionBox.setEnabled(b)
		self.precisionFieldCombo.setEnabled(b)
			
	@pyqtSignature("on_layerCombo_currentIndexChanged(int)")
	def on_layerCombo_currentIndexChanged(self,i):
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
			self.layerCombo.setCurrentIndex(0)
			QMessageBox.warning( self , "IntersectIt", error_msg )
		# update field list
		self.updateFieldsCombo()
		
	@pyqtSignature("on_dimensionFieldCombo_currentIndexChanged(int)")
	def on_dimensionFieldCombo_currentIndexChanged(self,i):
		if self.dimLayer() is not False and i > 0:
			field = self.dimensionFieldCombo.currentText()
			i = self.dimLayer().dataProvider().fieldNameIndex(field)
			# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
			if self.dimLayer().dataProvider().fields()[i].type() != 10:
				QMessageBox.warning( self , "IntersectIt" ,  QApplication.translate("IntersectIt", "The dimension field must be a varchar or a text.", None, QApplication.UnicodeUTF8) )
				self.dimensionFieldCombo.setCurrentIndex(0)
				
	@pyqtSignature("on_precisionFieldCombo_currentIndexChanged(int)")
	def on_precisionFieldCombo_currentIndexChanged(self,i):
		if self.dimLayer() is not False and i > 0:
			field = self.precisionFieldCombo.currentText()
			i = self.dimLayer().dataProvider().fieldNameIndex(field)
			# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
			if self.dimLayer().dataProvider().fields()[i].type() != 10:
				QMessageBox.warning( self , "IntersectIt" ,  QApplication.translate("IntersectIt", "The precision field must be a varchar or a text.", None, QApplication.UnicodeUTF8) )
				self.precisionFieldCombo.setCurrentIndex(0)
			
	def dimLayer(self):
		i = self.layerCombo.currentIndex()
		if i == 0: return False
		else: return self.layers[i-1]
				
	def updateFieldsCombo(self):
		self.dimensionFieldCombo.clear()
		self.precisionFieldCombo.clear()
		self.dimensionFieldCombo.addItem(_fromUtf8(""))
		self.precisionFieldCombo.addItem(_fromUtf8(""))
		if self.dimLayer() is False: return
		l = 1
		for field in self.dimLayer().dataProvider().fieldNameMap():
			self.dimensionFieldCombo.addItem(_fromUtf8("") )
			self.dimensionFieldCombo.setItemText( l, field )
			if field == QgsProject.instance().readEntry("IntersectIt", "dimension_field", "")[0]:
				self.dimensionFieldCombo.setCurrentIndex(l)	
			l += 1
		l = 1
		for field in self.dimLayer().dataProvider().fieldNameMap():
			self.precisionFieldCombo.addItem(_fromUtf8("") )
			self.precisionFieldCombo.setItemText( l, field )
			if field == QgsProject.instance().readEntry("IntersectIt", "precision_field", "")[0]:
				self.precisionFieldCombo.setCurrentIndex(l)	
			l += 1

	def applySettings(self):
		self.settings.setValue( "snapping " , int(self.snapBox.isChecked()) )
		self.settings.setValue( "tolerance" , self.tolerance.value() )
		if self.mapUnits.isChecked():
			self.settings.setValue( "units" , "map")
		else:
			self.settings.setValue( "units" , "pixels")		
		self.settings.setValue( "rubber_width"   , self.rubberWidth.value() )	
		self.settings.setValue( "rubber_colorR"  , self.color.red() )
		self.settings.setValue( "rubber_colorG"  , self.color.green() )
		self.settings.setValue( "rubber_colorB"  , self.color.blue() )
		self.settings.setValue( "placeArc"       , int(self.placeArcBox.isChecked()) )
		self.settings.setValue( "placePrecision" , int(self.placePrecisionBox.isChecked()) )
		self.settings.setValue( "placeDimension" , int(self.placeDimensionBox.isChecked()) )
		if self.dimLayer() is False: dimLayerId = ''
		else: dimLayerId = self.dimLayer().id()		
		QgsProject.instance().writeEntry("IntersectIt", "dimension_layer", dimLayerId)
		QgsProject.instance().writeEntry("IntersectIt", "dimension_field", self.dimensionFieldCombo.currentText() )
		QgsProject.instance().writeEntry("IntersectIt", "precision_field", self.precisionFieldCombo.currentText() )

	@pyqtSignature("on_rubberColor_clicked()")
	def on_rubberColor_clicked(self):
		self.color = QColorDialog.getColor(self.color)
		self.applyColorStyle()
		
	def applyColorStyle(self):
		self.rubberColor.setStyleSheet("background-color: rgb(%u,%u,%u)" % (self.color.red(),self.color.green(),self.color.blue()))	
