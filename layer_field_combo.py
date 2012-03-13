"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Management class for layer / fields UI combos
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class layerCombo():
	def __init__(self,combo,settingIDLambda=lambda:"",checkType=None):
		self.combo = combo
		self.settingIDLambda = settingIDLambda
		self.checkType = checkType	

class fieldCombo():
	def __init__(self,combo,settingIDLambda=lambda:"",checkType=None):
		self.combo = combo
		self.settingIDLambda = settingIDLambda
		self.checkType = checkType

class layerFieldCombo():
	def __init__(self, canvas, dialog, layer, fields=[]):
		self.canvas = canvas
		self.layer = layer
		self.fields = fields
		self.layerList = []
		# connect combos
		self.layerChangedLambda = lambda(i): self.layerChanged(i)
		self.fieldChangedLambda = lambda(i): self.fieldChanged(i,dialog.sender())
		QObject.connect(self.layer.combo, SIGNAL("currentIndexChanged(int)"), self.layerChangedLambda)
		for field in fields:
			QObject.connect(field.combo, SIGNAL("currentIndexChanged(int)"), self.fieldChangedLambda)
		
	def getLayer(self):
		i = self.layer.combo.currentIndex()
		if i == 0 or len(self.layerList)==0: return False
		else: return self.layerList[i-1]

	def onDialogShow(self):
		self.layerList = self.canvas.layers()
		self.layer.combo.clear()
		self.layer.combo.addItem("")
		for i,layer in enumerate(self.layerList):
			self.layer.combo.addItem(layer.name())
			if layer.id() == self.layer.settingIDLambda(): self.layer.combo.setCurrentIndex(i+1)
		self.updateFieldsCombo()
		QObject.connect(self.layer.combo, SIGNAL("currentIndexChanged(int)"), self.layerChanged)

	def layerChanged(self,i):
		error_msg = ''
		if i > 0:
			layer = self.layerList[i-1]
			if layer.type() != QgsMapLayer.VectorLayer:
				error_msg = QApplication.translate("Layer Field Combo", "The layer must be a vector layer.", None, QApplication.UnicodeUTF8) 
			elif layer.hasGeometryType() is False:
				error_msg = QApplication.translate("Layer Field Combo", "The dimension layer has no geometry.", None, QApplication.UnicodeUTF8) 
			else:
				# TODO CHECK GEOMETRY
				print "TODO CHECK GEOMETRY",layer.dataProvider().geometryType() , layer.geometryType()
		if error_msg != '':
			self.dimensionLayerCombo.setCurrentIndex(0)
			QMessageBox.warning( self , "Bad Layer", error_msg )
		# update field list
		self.updateFieldsCombo()

	def fieldChanged(self,i,sender):
		field = None
		for testField in self.fields:
			if testField.combo == sender:
				 field = testField
				 break
		if field is None: raise NameError('LayerFieldCombo: cannot find field')
		if self.getLayer() is not False and i > 0:
			fieldName = field.combo.currentText()
			i = self.getLayer().dataProvider().fieldNameIndex(fieldName)
			# http://developer.qt.nokia.com/doc/qt-4.8/qmetatype.html#Type-enum
			if self.getLayer().dataProvider().fields()[i].type() != field.checkType:
				QMessageBox.warning( self , "Bad field" ,  QApplication.translate("Layer Field Combo", "The field must be a %s" % field.type, None, QApplication.UnicodeUTF8) )
				field.combo.setCurrentIndex(0)	

	def updateFieldsCombo(self):
		for field in self.fields:
			field.combo.clear()
			field.combo.addItem(_fromUtf8(""))
			if self.getLayer() is False: continue
			for i,fieldItem in enumerate( self.getLayer().dataProvider().fieldNameMap() ):
				field.combo.addItem( fieldItem )
				if fieldItem == field.settingIDLambda():
					field.combo.setCurrentIndex(i+1)
