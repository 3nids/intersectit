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

from settings import IntersectItSettings

class placeMeasureOnMap(QgsMapToolEmitPoint):
	def __init__(self, canvas, snapping=0):
		self.canvas = canvas
		self.snapping = snapping
		self.rubber = QgsRubberBand(canvas)
		QgsMapToolEmitPoint.__init__(self, canvas)

	def canvasMoveEvent(self, mouseEvent):
		#snap to layers	
		self.rubber.reset()
		if self.snapping == 1:
			pixPoint = mouseEvent.pos()
			result,snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint,[])
			if result == 0 and len(snappingResults)>0:
				snappedPoint = QgsPoint(snappingResults[0].snappedVertex)
				self.rubber.addGeometry(QgsGeometry.fromPoint(snappedPoint),None)

	def canvasPressEvent(self, mouseEvent):
		if mouseEvent.button() != Qt.LeftButton: return
		self.rubber.reset()
		pixpoint = mouseEvent.pos()
		mappoint = self.toMapCoordinates( mouseEvent.pos() )
		self.emit( SIGNAL( "distancePlaced" ), mappoint, pixpoint )

class placeIntersectionOnMap(QgsMapToolEmitPoint):
	def __init__(self, canvas, lineLayer, rubber):
		self.canvas = canvas
		self.rubber = rubber
		self.provider = lineLayer().dataProvider()
		QgsMapToolEmitPoint.__init__(self, canvas)
		self.settings = IntersectItSettings()

		self.tolerance = self.settings.value("tolerance").toDouble()[0]
		units = self.settings.value("units").toString()
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
