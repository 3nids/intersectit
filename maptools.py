"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

mapTools
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from mysettings import MySettings
from observation import observation
from ui.ui_place_distance import Ui_place_distance

class PlaceDistanceDialog(QDialog, Ui_place_distance ):
	def __init__(self,point):
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)	
		self.x.setText("%.3f" % point.x())
		self.y.setText("%.3f" % point.y())
		self.distance.selectAll()

class PlaceDistanceOnMap(QgsMapToolEmitPoint):
	def __init__(self, canvas, snapping=0):
		self.canvas = canvas
		self.snapping = snapping
		self.rubber = QgsRubberBand(canvas)
		QgsMapToolEmitPoint.__init__(self, canvas)

	def canvasMoveEvent(self, mouseEvent):
		if self.snapping:
			snappedPoint = self.snapToLayers( mouseEvent.pos() )
			self.rubber.setToGeometry( QgsGeometry.fromPoint(snappedPoint), None )

	def canvasPressEvent(self, mouseEvent):
		if mouseEvent.button() != Qt.LeftButton: return
		self.rubber.reset()
		pixPoint = mouseEvent.pos()
		mapPoint = self.toMapCoordinates( pixPoint )
		#snap to layers
		if self.snapping:
			mapPoint = self.snapToLayers( pixPoint, mapPoint)
		# creates ditance with dialog
		dlg = PlaceDistanceDialog(mapPoint)
		if dlg.exec_():
			radius    = dlg.distance.value()
			precision = dlg.precision.value()
			if radius==0: return
			observation( canvas,self.lineLayer,self.pointLayer,"distance",point,radius,precision )
			
	def snapToLayers(self, pixPoint, dfltPoint=QgsPoint()):
		if not self.snapping:
			return None
		result,snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint,[])
		if result == 0 and len(snappingResults)>0:
			return QgsPoint(snappingResults[0].snappedVertex)
		else:
			return dfltPoint

class placeIntersectionOnMap(QgsMapToolEmitPoint):
	def __init__(self, canvas, lineLayer, rubber):
		self.canvas = canvas
		self.rubber = rubber
		self.provider = lineLayer().dataProvider()
		QgsMapToolEmitPoint.__init__(self, canvas)
		self.settings = IntersectItSettings()
		self.tolerance = self.settings.value("intersect_select_tolerance").toDouble()[0]
		units = self.settings.value("intersect_select_units").toString()
		if units == "pixels": self.tolerance *= self.iface.mapCanvas().mapUnitsPerPixel()

	def canvasMoveEvent(self, mouseEvent):
		# put the observations within tolerance in the rubber band
		self.rubber.reset()
		point = self.toMapCoordinates( mouseEvent.pos() )
		self.provider.select([], self.getBox(point) , True, True)
		f = QgsFeature()
		while (self.provider.nextFeature(f)):
			self.rubber.addGeometry( f.geometry() , None )

	def canvasPressEvent(self, mouseEvent):
		self.rubber.reset()
		observations = []
		point = self.toMapCoordinates( mouseEvent.pos() )
		it = self.provider.fieldNameIndex('type')
		ix = self.provider.fieldNameIndex('x')
		iy = self.provider.fieldNameIndex('y')
		io = self.provider.fieldNameIndex('measure')
		ip = self.provider.fieldNameIndex('precision')
		self.provider.select([it,ix,iy,io,ip], self.getBox(point) , True, True)
		f = QgsFeature()
		while (self.provider.nextFeature(f)):
			fm = f.attributeMap()
			observations.append({	"type": fm[it].toString(),
									"x": fm[ix].toDouble()[0],
									"y": fm[iy].toDouble()[0],
									"measure": fm[io].toDouble()[0],
									"precision": fm[ip].toDouble()[0] })
		self.emit( SIGNAL( "intersectionStarted" ), point, observations )

	def getBox(self,point):
		return QgsRectangle(point.x()-self.tolerance,point.y()-self.tolerance,point.x()+self.tolerance,point.y()+self.tolerance)
