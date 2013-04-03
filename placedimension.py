"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for placing dimension arcs
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import math
from intersectitsettings import IntersectItSettings
from ui.ui_place_dimension import Ui_placeDimension

class PlaceDimension(QDialog, Ui_placeDimension ):
	def __init__(self,iface,intersectedPoint,observations,distanceLayers):
		QDialog.__init__(self)
		self.setupUi(self)
		self.iface = iface
		self.distanceLayers = distanceLayers
		# load settings
		self.settings = IntersectItSettings()	
		self.layer = next( ( layer for layer in iface.mapCanvas().layers() if layer.id() == self.settings.value("dimensionLayer") ), None )
		self.rubber = QgsRubberBand(iface.mapCanvas())
		self.rubber.setWidth(2)
		defaultRadius = self.radiusSlider.value()
		QObject.connect(self , SIGNAL( "accepted()" ) , self.rubber.reset)
		QObject.connect(self , SIGNAL( "rejected()" ) , self.cancel)
		QObject.connect(self.radiusSpin,   SIGNAL("valueChanged(int)"),	self.radiusSlider, SLOT("setValue(int)"))
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"),	self.radiusSpin,   SLOT("setValue(int)"))
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"), self.radiusChanged)

		# init state for distance layer visibility
		QObject.connect( self.displayLayersBox , SIGNAL("stateChanged(int)") , self.toggleDistanceLayers )
		# create the observations
		self.observations = observations
		self.dimension = []
		self.dimensionCombo.clear()
		nn = len(observations)
		for i,obs in enumerate(observations):
			self.dimensionCombo.addItem( "%u/%u" % (i+1,nn) )
			self.dimension.append( Dimension(	iface,self.layer,
												intersectedPoint,
												QgsPoint( obs["x"] , obs["y"] ),
												obs["measure"],
												obs["precision"],
												defaultRadius) )
		# above line must be placed after the combobox population
		QObject.connect(self.dimensionCombo, SIGNAL("currentIndexChanged(int)") , self.dimensionSelected)
		self.dimensionSelected(0)
		
	def toggleDistanceLayers(self,i):
		self.displayLayersBox.setTristate(False)
		self.iface.legendInterface().setLayerVisible(self.distanceLayers[0],bool(i))
		self.iface.legendInterface().setLayerVisible(self.distanceLayers[1],bool(i))
			
	def currentDimension(self):
		return self.dimensionCombo.currentIndex()
		
	def dimensionSelected(self,i):
		dimension = self.dimension[self.currentDimension()]
		self.radiusSlider.setValue(dimension.radius)
		self.createBox.setChecked(dimension.isActive)
		self.updateRubber()
		
	def radiusChanged(self,radius):
		self.updateRubber()
		self.dimension[self.currentDimension()].setRadius(radius).draw()

	def cancel(self):
		self.rubber.reset()
		for a in self.dimension: a.delete()
	
	@pyqtSignature("on_prevButton_clicked()")
	def on_prevButton_clicked(self):
		i = max(0,self.currentDimension()-1)
		self.dimensionCombo.setCurrentIndex(i)
		
	@pyqtSignature("on_nextButton_clicked()")
	def on_nextButton_clicked(self):
		self.updateRubber()
		i = min(self.currentDimension()+1,len(self.dimension)-1)
		self.dimensionCombo.setCurrentIndex(i)
		
	@pyqtSignature("on_reverseButton_clicked()")
	def on_reverseButton_clicked(self):
		self.dimension[self.currentDimension()].reverse().draw()
		self.updateRubber()
		
	@pyqtSignature("on_createBox_stateChanged(int)")
	def on_createBox_stateChanged(self,i):
		if i == 0:
			self.dimension[self.currentDimension()].delete()
		else:
			self.dimension[self.currentDimension()].createFeature()
	
	def updateRubber(self):
		self.rubber.reset()
		if self.createBox.isChecked():
			geom = self.dimension[self.dimensionCombo.currentIndex()].geometry()
			self.rubber.addGeometry(geom,self.layer)


class Dimension():
	def __init__(self,iface,layer,intersectedPoint,distancePoint,distance,precision,radius):
		self.iface = iface
		self.layer = layer
		self.provider = layer.dataProvider()
		self.radius    = radius	
		self.distance  = distance
		self.precision = precision 
		self.length    = math.sqrt( intersectedPoint.sqrDist(distancePoint) )
		self.isActive  = True
		self.intersectedPoint = intersectedPoint
		self.distancePoint     = distancePoint
		self.anchorPoint       = [  (intersectedPoint.x()+distancePoint.x())/2 , (intersectedPoint.y()+distancePoint.y())/2 ]
		self.direction         = [ -(intersectedPoint.y()-distancePoint.y())   ,  intersectedPoint.x()-distancePoint.x()    ]
		self.way = 1
		self.settings = IntersectItSettings()
		self.createFeature()
		
	def setRadius(self,radius):
		self.radius = radius
		return self
		
	def reverse(self):
		self.way *= -1
		return self		

	def createFeature(self):
		self.isActive = True
		# create feature and geometry
		f = QgsFeature()
		f.initAttributes( self.provider.fields().count() )
		f.setGeometry(self.geometry())
		# look for dimension and precision fields
		if self.settings.value("dimenPlaceMeasure"):
			dimFieldName = self.settings.value("measureField")
			idx = self.provider.fieldNameIndex(dimFieldName)
			if idx == -1:
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "The field to save the measure could not be found. Would you like to continue?" % QMessageBox.Yes, QMessageBox.No )
				if reply == QMessageBox.No:	return				
			f.setAttribute(idx,QVariant("%.4f" % self.distance))
		if self.settings.value("dimenPlacePrecision"):
			preFieldName = self.settings.value("precisionField")
			idx = self.provider.fieldNameIndex(preFieldName)
			if idx == -1:
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "The field to save the measure could not be found. Would you like to continue?" % QMessageBox.Yes, QMessageBox.No )
				if reply == QMessageBox.No:	return	
			f.setAttribute(idx,QVariant("%.4f" % self.precision))
		print f.id()
		ans = self.provider.addFeatures( [f] )
		print "ok"
		self.f_id = f.id()
		print f.id()
		self.layer.updateExtents()
		self.iface.mapCanvas().refresh()
		
	def delete(self):
		self.isActive = False
		self.provider.deleteFeatures([self.f_id])
		self.layer.updateExtents()
		self.iface.mapCanvas().refresh()
		
	def draw(self):
		if self.isActive:
			# can also do on layer: startEditing, changeGeometry, rollBack, updateExtents
			self.provider.changeGeometryValues( { self.f_id : self.geometry() }) 
			self.iface.mapCanvas().refresh()
			
	def geometry(self):
		# http://www.vb-helper.com/howto_find_quadratic_curve.html
		curvePoint = QgsPoint(	self.anchorPoint[0] + self.way * self.direction[0] * self.radius/100 ,
								self.anchorPoint[1] + self.way * self.direction[1] * self.radius/100 )
		return  QgsGeometry().fromMultiPoint([self.intersectedPoint,curvePoint,self.distancePoint])  

	
