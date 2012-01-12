"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for distance
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
		self.settings = QSettings("Triangulation","Triangulation")
		
		self.tolerance.setValue(self.settings.value("tolerance",0.6).toDouble()[0])
		if self.settings.value( "units" , "map").toString() == "map":
			self.mapUnits.setChecked(True)
			self.pixels.setChecked(False)
		else:
			self.mapUnits.setChecked(False)
			self.pixels.setChecked(True)
		self.rubberWidth.setValue(self.settings.value("rubber_width",2).toDouble()[0])
		self.colorR = self.settings.value("rubber_colorR",255).toInt()[0]
		self.colorG = self.settings.value("rubber_colorG",0  ).toInt()[0]
		self.colorB = self.settings.value("rubber_colorB",0  ).toInt()[0]
		self.color = QColor(self.colorR,self.colorG,self.colorB,255)
		self.applyColorStyle()
		self.placeArc.setChecked( self.settings.value( "placeArc" , 1).toInt()[0] ) 
		
	def showEvent(self, e):
		self.layers = self.iface.mapCanvas().layers()
		dimLayerId = QgsProject.instance().readEntry("Translation", "dimension_layer", "")[0]
		self.layerList.clear()
		self.layerList.addItem(_fromUtf8(""))
		l = 1
		for layer in self.layers:
			self.layerList.addItem(_fromUtf8(""))
			self.layerList.setItemText(l, layer.name())
			if layer.id() == dimLayerId:
				self.layerList.setCurrentIndex(l)
			l+=1
			
	def applySettings(self):
		self.settings.setValue( "tolerance" , self.tolerance.value() )
		if self.mapUnits.isChecked():
			self.settings.setValue( "units" , "map")
		else:
			self.settings.setValue( "units" , "pixels")		
		self.settings.setValue( "rubber_width" , self.rubberWidth.value() )	
		self.settings.setValue( "rubber_colorR" , self.color.red() )
		self.settings.setValue( "rubber_colorG" , self.color.green() )
		self.settings.setValue( "rubber_colorB" , self.color.blue() )
		self.settings.setValue( "placeArc" , int(self.placeArc.isChecked()) )
		l = self.layerList.currentIndex()
		dimLayerId = ""
		if l > 0:
			dimLayerId = self.layers[l-1].id()
		QgsProject.instance().writeEntry("Translation", "dimension_layer", dimLayerId)

	@pyqtSignature("on_rubberColor_clicked()")
	def on_rubberColor_clicked(self):
		self.color = QColorDialog.getColor(self.color)
		self.applyColorStyle()
		
	def applyColorStyle(self):
		self.rubberColor.setStyleSheet("background-color: rgb(%u,%u,%u)" % (self.color.red(),self.color.green(),self.color.blue()))	
			



