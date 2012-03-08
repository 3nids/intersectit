"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Observation class for distances
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import math

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class distance():
	def __init__(self,canvas,lineLayer,pointLayer,center,radius,precision):
		self.type = "distance"
		self.center = center
		self.radius = radius
		self.precision = precision
		self.canvas = canvas
		self.lineLayer = lineLayer
		self.pointLayer = pointLayer
		self.draw()
		
	def draw(self):
		# add circle
		circleGeom = QgsGeometry.fromPolyline( [QgsPoint(self.center.x()+self.radius*math.cos(math.pi/180*a),self.center.y()+self.radius*math.sin(math.pi/180*a)) for a in range(0,361,3)] )
		f = QgsFeature()
		f.setGeometry(circleGeom)
		self.lineLayer().dataProvider().addFeatures( [f] )
		self.lineLayer().updateExtents()
		self.line_id = f.id()
		# add center
		f = QgsFeature()
		f.setGeometry(QgsGeometry.fromPoint(self.center))
		self.pointLayer().dataProvider().addFeatures( [f] )
		self.pointLayer().updateExtents()
		self.point_id = f.id()
		# refresh canvas
		self.canvas.refresh()
		
		
	def delete(self):
		self.pointLayer().dataProvider().deleteFeatures( [self.point_id] )
		self.lineLayer().dataProvider().deleteFeatures(  [self.line_id]  )
		self.canvas.refresh()
		
		
