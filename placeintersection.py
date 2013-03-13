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
from observation import Observation
from ui.ui_place_distance import Ui_place_distance

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
