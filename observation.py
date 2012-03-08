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
from datetime import datetime

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class observation():
	def __init__(self,canvas,lineLayer,pointLayer,type,point,observation,precision):
		# generate ID
		id = datetime.now().strftime("%Y%m%d%H%M%S%f")
		
		# creates features
		# obsservations are stored in the lineLayer layer
		# attributeMap: 
		#   0: otherid (the id of the feature in the other layer)
		#   1: type
		#   2: x
		#   3: y
		#   4: observation
		#   5: precision

		# draw observation and save info in feature
		f = QgsFeature()
		f.setAttributeMap( {0: QVariant(id),
							1: QVariant(type),
							2: QVariant(point.x()),
							3: QVariant(point.y()),
							4: QVariant(observation),
							5: QVariant(precision)} )
		if type == "distance":
			geom = QgsGeometry.fromPolyline( [QgsPoint(point.x()+observation*math.cos(math.pi/180*a),point.y()+observation*math.sin(math.pi/180*a)) for a in range(0,361,3)] )
		f.setGeometry(geom)
		lineLayer().dataProvider().addFeatures( [f] )
		lineLayer().updateExtents()

		# draw center
		f = QgsFeature()
		f.setAttributeMap( {0: QVariant(id)} )
		f.setGeometry(QgsGeometry.fromPoint(point))
		pointLayer().dataProvider().addFeatures( [f] )
		pointLayer().updateExtents()
		
		# refresh canvas
		canvas.refresh()
		
		
#	def delete(self):
#		self.pointLayer().dataProvider().deleteFeatures( [self.point_id] )
#		self.lineLayer().dataProvider().deleteFeatures(  [self.line_id]  )
#		self.canvas.refresh()
		
		
