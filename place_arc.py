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
from ui_place_arc import Ui_placeArc

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class placeArc(QDialog, Ui_placeArc ):
	def __init__(self,iface,layer,triangulatedPoint,xyrpi):
		self.layer = layer
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
		for c in xyrpi:
			self.arc.append(arc(iface,layer,triangulatedPoint,c[0]))
		
		self.arc[0].draw(40)
		
	def radiusChanged(self,radius):
		self.arc[0].draw(radius)


	def addArcToLayer(self):
		print 1
		
		
		
class arc():
	def __init__(self,iface,layer,triangulatedPoint,distancePoint):
		self.layer = layer
		self.rubber = QgsRubberBand(iface.mapCanvas())
		self.rubber.setWidth(2)
		
		self.triangulatedPoint = triangulatedPoint
		self.distancePoint     = distancePoint
		self.anchorPoint       = [  (triangulatedPoint.x()+distancePoint.x())/2 , (triangulatedPoint.y()+distancePoint.y())/2 ]
		self.direction         = [ -(triangulatedPoint.y()-distancePoint.y())   ,  triangulatedPoint.x()-distancePoint.x()    ]
		self.way = 1
		
		
	def reverse(self):
		self.way *= 1	
		
		
	def draw(self,radius):
		# http://www.vb-helper.com/howto_find_quadratic_curve.html
		self.rubber.reset()
		self.rubber.addGeometry(QgsGeometry.fromPoint(self.triangulatedPoint),self.layer)
		self.rubber.addGeometry(QgsGeometry.fromPoint(self.distancePoint),self.layer)

		curvePoint = QgsPoint(   self.anchorPoint[0] + self.way * self.direction[0] * radius/100    ,   self.anchorPoint[1] + self.way * self.direction[1] * radius/100    )
		
		self.rubber.addGeometry(QgsGeometry.fromPoint(curvePoint),self.layer)
		
		
		
		
		
		
		

		
