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
	def __init__(self,iface,layer,triangulatedPoint,xyrpi):
		self.layer = layer
		defaultRadius = 40
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		QObject.connect(self , SIGNAL( "accepted()" ) , self.addArcToLayer)
		QObject.connect(self.radiusSpin,   SIGNAL("valueChanged(int)"),	self.radiusSlider, SLOT("setValue(int)"))
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"),	self.radiusSpin,   SLOT("setValue(int)"))
		QObject.connect(self.radiusSpin,   SIGNAL("valueChanged(int)"), self.radiusChanged)

		self.settings = QSettings("Triangulation","Triangulation")
		
		self.xyrpi = xyrpi
		self.arc = []
		self.arcCombo.clear()
		ii = 0
		nn = len(xyrpi)
		for c in xyrpi:
			self.arcCombo.addItem(_fromUtf8(""))
			self.arcCombo.setItemText( ii , "%u/%u" % (ii,nn) )
			
			point = c[0]
			self.arc.append(arc(iface,layer,triangulatedPoint,point,defaultRadius))
			ii += 1
			
	def currentArc(self):
		return self.arcCombo.currentIndex()
		
	def radius(self):
		return self.radiusSlider.value()
	
	
	@pyqtSignature("on_createBox_stateChanged(int)")
	def on_createBox_stateChanged(self,i):
		if i == 0:
			print i,self.currentArc()
			self.arc[self.currentArc()].delete()
		else:
			self.arc[self.currentArc()].createFeature(self.radius())
	
		
	def radiusChanged(self,radius):
		self.arc[0].draw(radius)


	def addArcToLayer(self):
		print 1
		
		
		
class arc():
	def __init__(self,iface,layer,triangulatedPoint,distancePoint,radius):
		self.iface = iface
		self.layer = layer
		self.provider = layer.dataProvider()
		self.rubber = QgsRubberBand(iface.mapCanvas())
		self.rubber.setWidth(2)
		
		self.length = math.sqrt( triangulatedPoint.sqrDist(distancePoint) )
		
		self.triangulatedPoint = triangulatedPoint
		self.distancePoint     = distancePoint
		self.anchorPoint       = [  (triangulatedPoint.x()+distancePoint.x())/2 , (triangulatedPoint.y()+distancePoint.y())/2 ]
		self.direction         = [ -(triangulatedPoint.y()-distancePoint.y())   ,  triangulatedPoint.x()-distancePoint.x()    ]
		self.way = 1
		
		self.createFeature(radius)


	def createFeature(self,radius):
		# create feature and geometry
		f = QgsFeature()
		f.setGeometry(self.geometry(radius))
		# look for dimension label
		dimFieldName = QgsProject.instance().readEntry("Triangulation", "dimension_field", "")[0]
		ilbl = self.provider.fieldNameIndex(dimFieldName)
		if ilbl != -1:
			f.addAttribute(ilbl,QVariant("%.2f" % self.length))
		# look for primary key
		iid  = self.provider.fieldNameIndex('id')
		if iid != -1:
			self.fid = self.provider.maximumValue(iid).toInt()[0]+1
			f.addAttribute(iid,self.fid)
		# add feature to layer	
		self.provider.addFeatures( [f] )
		self.layer.updateExtents()
		self.iface.mapCanvas().refresh()
		
	def delete(self):
		self.provider.deleteFeatures([self.fid])
		
	def reverse(self):
		self.way *= 1	
		
	
	def draw(self,radius):
		f = QgsFeature()
		self.provider.featureAtId(self.fid,f)
		f.setGeometry(self.geometry(radius))
		
		
		
	def geometry(self,radius):
		# http://www.vb-helper.com/howto_find_quadratic_curve.html
		"""
		self.rubber.reset()
		self.rubber.addGeometry(QgsGeometry.fromPoint(self.triangulatedPoint),self.layer)
		self.rubber.addGeometry(QgsGeometry.fromPoint(self.distancePoint),self.layer)
		"""
		curvePoint = QgsPoint(   self.anchorPoint[0] + self.way * self.direction[0] * radius/100    ,   self.anchorPoint[1] + self.way * self.direction[1] * radius/100    )
		return  QgsGeometry().fromMultiPoint([self.triangulatedPoint,curvePoint,self.distancePoint])  

		
		
				
		#self.rubber.addGeometry(QgsGeometry.fromPoint(curvePoint),self.layer)
		
	
		
		
		
		
		
		
		

		
