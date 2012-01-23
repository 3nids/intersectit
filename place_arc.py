"""
Triangulation QGIS plugin
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
from ui_place_arc import Ui_placeArc

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class placeArc(QDialog, Ui_placeArc ):
	def __init__(self,iface,triangulatedPoint,xyrpi,distanceLayers):
		QDialog.__init__(self)
		self.setupUi(self)
		self.iface = iface
		self.distanceLayers = distanceLayers
		self.layer = next( ( layer for layer in iface.mapCanvas().layers() if layer.id() == QgsProject.instance().readEntry("Triangulation", "dimension_layer", "")[0] ), False )
		self.rubber = QgsRubberBand(iface.mapCanvas())
		self.rubber.setWidth(2)
		defaultRadius = self.radiusSlider.value()
		QObject.connect(self , SIGNAL( "accepted()" ) , self.rubber.reset)
		QObject.connect(self , SIGNAL( "rejected()" ) , self.cancel)
		QObject.connect(self.radiusSpin,   SIGNAL("valueChanged(int)"),	self.radiusSlider, SLOT("setValue(int)"))
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"),	self.radiusSpin,   SLOT("setValue(int)"))
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"), self.radiusChanged)
		# load settings
		self.settings = QSettings("Triangulation","Triangulation")
		# init state for distance layer visibility
		self.displayLayersBox.setCheckState(Qt.PartiallyChecked)
		QObject.connect( self.displayLayersBox , SIGNAL("stateChanged(int)") , self.toggleDistanceLayers )
		# create the arcs
		self.xyrpi = xyrpi
		self.arc = []
		self.arcCombo.clear()
		ii = 0
		nn = len(xyrpi)
		for c in xyrpi:
			self.arcCombo.addItem(_fromUtf8(""))
			self.arcCombo.setItemText( ii , "%u/%u" % (ii+1,nn) )
			point = c[0]
			distance  = c[1] # this is the measure
			precision = c[2]
			self.arc.append(arc(iface,self.layer,triangulatedPoint,point,distance,precision,defaultRadius))
			ii += 1
		QObject.connect(self.arcCombo, SIGNAL("currentIndexChanged(int)") , self.arcSelected) # this must be placed after the combobox population
		self.arcSelected(0)
		
	def toggleDistanceLayers(self,i):
		self.displayLayersBox.setTristate(False)
		self.iface.legendInterface().setLayerVisible(self.distanceLayers[0],bool(i))
		self.iface.legendInterface().setLayerVisible(self.distanceLayers[1],bool(i))
			
	def currentArc(self):
		return self.arcCombo.currentIndex()
		
	def arcSelected(self,i):
		arc = self.arc[self.currentArc()]
		self.radiusSlider.setValue(arc.radius)
		self.createBox.setChecked(arc.isActive)
		self.updateRubber()
		
	def radiusChanged(self,radius):
		self.updateRubber()
		self.arc[self.currentArc()].setRadius(radius).draw()

	def cancel(self):
		self.rubber.reset()
		for a in self.arc: a.delete()
	
	@pyqtSignature("on_prevButton_clicked()")
	def on_prevButton_clicked(self):
		i = max(0,self.currentArc()-1)
		self.arcCombo.setCurrentIndex(i)
		
	@pyqtSignature("on_nextButton_clicked()")
	def on_nextButton_clicked(self):
		self.updateRubber()
		i = min(self.currentArc()+1,len(self.arc)-1)
		self.arcCombo.setCurrentIndex(i)
		
	@pyqtSignature("on_reverseButton_clicked()")
	def on_reverseButton_clicked(self):
		self.arc[self.currentArc()].reverse().draw()
		
	@pyqtSignature("on_createBox_stateChanged(int)")
	def on_createBox_stateChanged(self,i):
		if i == 0:
			self.arc[self.currentArc()].delete()
		else:
			self.arc[self.currentArc()].createFeature()
	
	def updateRubber(self):
		self.rubber.reset()
		if self.createBox.isChecked():
			geom = self.arc[self.arcCombo.currentIndex()].geometry()
			self.rubber.addGeometry(geom,self.layer)


class arc():
	def __init__(self,iface,layer,triangulatedPoint,distancePoint,distance,precision,radius):
		self.iface = iface
		self.layer = layer
		self.provider = layer.dataProvider()
		self.radius    = radius	
		self.distance  = distance
		self.precision = precision 
		self.length    = math.sqrt( triangulatedPoint.sqrDist(distancePoint) )
		self.isActive  = True
		self.triangulatedPoint = triangulatedPoint
		self.distancePoint     = distancePoint
		self.anchorPoint       = [  (triangulatedPoint.x()+distancePoint.x())/2 , (triangulatedPoint.y()+distancePoint.y())/2 ]
		self.direction         = [ -(triangulatedPoint.y()-distancePoint.y())   ,  triangulatedPoint.x()-distancePoint.x()    ]
		self.way = 1
		self.settings = QSettings("Triangulation","Triangulation")
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
		f.setGeometry(self.geometry())
		# look for dimension and precision fields
		if self.settings.value("placeDimension",1).toInt()[0] == 1:
			dimFieldName = QgsProject.instance().readEntry("Triangulation", "dimension_field", "")[0]
			ilbl = self.provider.fieldNameIndex(dimFieldName)
			f.addAttribute(ilbl,QVariant("%.2f" % self.distance))
		if self.settings.value("placePrecision",1).toInt()[0] == 1:
			preFieldName = QgsProject.instance().readEntry("Triangulation", "precision_field", "")[0]
			ilbl = self.provider.fieldNameIndex(preFieldName)
			f.addAttribute(ilbl,QVariant("%.2f" % self.precision))
		# look for primary key
		iid = self.provider.fieldNameIndex('id')
		#iid = -1
		if iid != -1:
			self.db_id = self.provider.maximumValue(iid).toInt()[0]+1
			f.addAttribute(iid,self.db_id)
		# add feature to layer	
		ans,f = self.provider.addFeatures( [f] )
		self.f_id = f[0].id()
		self.layer.updateExtents()
		self.iface.mapCanvas().refresh()
		
	def delete(self):
		self.isActive = False
		self.provider.deleteFeatures([self.f_id])
		self.layer.updateExtents()
		self.iface.mapCanvas().refresh()
		
	def draw(self):
		if self.isActive:
			self.layer.startEditing()
			self.layer.changeGeometry( self.f_id , self.geometry() )
			self.layer.commitChanges()
			self.layer.rollBack()
			#self.layer.updateExtents()
			self.iface.mapCanvas().refresh()
			#self.provider.changeGeometryValues( { self.f_id : self.geometry() }) #not working as it expects a QMap. Asked to developer list. Waiting.
			
	def geometry(self):
		# http://www.vb-helper.com/howto_find_quadratic_curve.html
		curvePoint = QgsPoint(   self.anchorPoint[0] + self.way * self.direction[0] * self.radius/100    ,   self.anchorPoint[1] + self.way * self.direction[1] * self.radius/100    )
		return  QgsGeometry().fromMultiPoint([self.triangulatedPoint,curvePoint,self.distancePoint])  

	
