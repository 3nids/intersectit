"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for distance
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_distance import Ui_distanceDialog

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class distance(QDialog, Ui_distanceDialog ):
	def __init__(self,canvas,center,radius,precision):
		self.type = "distance"
		self.center = center
		self.radius = radius
		self.precision = precision
		self.rubber = QgsRubberBand(canvas)
		
	def drawCircle(self):
		self.rubber.addGeometry( QgsGeometry.fromPolyline( [QgsPoint(self.center.x()+self.radius*math.cos(math.pi/180*a),self.center.y()+self.radius*math.sin(math.pi/180*a)) for a in range(0,361,3)] ) )
		self.rubber.addGeometry( QgsGeometry.fromPoint( self.center ) )
		
	def delete(self):
		self.rubber.reset()
		
		
