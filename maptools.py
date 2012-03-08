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
		self.rubber.reset()
		pixpoint = mouseEvent.pos()
		mappoint = self.toMapCoordinates( mouseEvent.pos() )
		self.emit( SIGNAL( "canvasClickedWithModifiers" ), mappoint, pixpoint , mouseEvent.button(), mouseEvent.modifiers() )
		
		
class placeIntersectionOnMap(QgsMapToolEmitPoint):
	def __init__(self, canvas, lineLayer):
		self.canvas = canvas
		self.rubber = QgsRubberBand(canvas)
		self.provider = lineLayer().dataProvider()
		QgsMapToolEmitPoint.__init__(self, canvas)
		self.settings = QSettings("IntersectIt","IntersectIt")

		self.tolerance = self.settings.value("tolerance",0.3).toDouble()[0]
		units = self.settings.value("units","map").toString()
		if units == "pixels": self.tolerance *= self.iface.mapCanvas().mapUnitsPerPixel()
		
	def canvasMoveEvent(self, mouseEvent):
		# put the observations within tolerance in the rubber band
		point = self.toMapCoordinates( mouseEvent.pos() )
		rect = QgsRectangle(point.x()-self.tolerance,point.y()-self.tolerance,point.x()+self.tolerance,point.y()+self.tolerance)
		self.provider.select([], rect, True, True)
		f = QgsFeature()
		self.rubber.reset()
		while (self.provider.nextFeature(f)):
			self.rubber.addGeometry( f.geometry() , None )
		
	def canvasPressEvent(self, mouseEvent):
		self.rubber.reset()
		pixpoint = mouseEvent.pos()
		mappoint = self.toMapCoordinates( mouseEvent.pos() )
		self.emit( SIGNAL( "canvasClickedWithModifiers" ), mappoint, pixpoint , mouseEvent.button(), mouseEvent.modifiers() )	
