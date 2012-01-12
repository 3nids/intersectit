"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Main class
"""

import math

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from distance import distance
from triangulation_process import triangulationProcess


# Initialize Qt resources from file resources.py
import resources


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class triangulation ():
	def __init__(self, iface):
		# Save reference to the QGIS interface
		self.iface = iface
		self.lineLayer = False
		self.pointLayer = False
		# create rubber band to emphasis selected circles
		self.rubber = QgsRubberBand(self.iface.mapCanvas())

	def initGui(self):
		# DISTANCE
		self.distanceAction = QAction(QIcon(":/plugins/triangulation/icons/distance.png"), "distance tool", self.iface.mainWindow())
		self.distanceAction.setCheckable(True)
		# connect the action to the run method
		QObject.connect(self.distanceAction, SIGNAL("triggered()"), self.distanceStart)
		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.distanceAction)
		self.iface.addPluginToMenu("&Triangulation", self.distanceAction)	
		# TRIANGULATION
		self.triangulAction = QAction(QIcon(":/plugins/triangulation/icons/intersect.png"), "distance tool", self.iface.mainWindow())
		self.triangulAction.setCheckable(True)
		# connect the action to the run method
		QObject.connect(self.triangulAction, SIGNAL("triggered()"), self.triangulationStart)
		# Add toolbar button and menu item
		self.iface.addToolBarIcon(self.triangulAction)
		self.iface.addPluginToMenu("&Triangulation", self.triangulAction)	
		
	def unload(self):
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)
		print "TODO: instersect unload"
		try:
			print "Triangulation :: Removing temporary layer"
			QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer.id()) 
			QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer.id()) 
		except AttributeError:
			return

	def lineLayerDeleted(self):
		self.lineLayer = False

	def pointLayerDeleted(self):
		self.pointLayer = False

	def createLineMemoryLayer(self):	
		self.lineLayer = QgsVectorLayer("LineString?crs=EPSG:21781&field=x:double&field=y:double&field=radius:double&field=precision:double&index=yes", "Triangulation", "memory") 
		QgsMapLayerRegistry.instance().addMapLayer(self.lineLayer) 
		QObject.connect( self.lineLayer, SIGNAL("layerDeleted()") , self.lineLayerDeleted )

	def createPointMemoryLayer(self):	
		self.pointLayer = QgsVectorLayer("Point?crs=EPSG:21781&index=yes", "Triangulation", "memory") 
		QgsMapLayerRegistry.instance().addMapLayer(self.pointLayer) 
		QObject.connect( self.pointLayer, SIGNAL("layerDeleted()") , self.pointLayerDeleted )
		
	def distanceStart(self):
		canvas = self.iface.mapCanvas()
		if self.distanceAction.isChecked() is False:
			canvas.unsetMapTool(self.getDistancePoint)
			return
		self.distanceAction.setChecked( True )
		if self.lineLayer is False:
			self.createLineMemoryLayer()
		if self.pointLayer is False:
			self.createPointMemoryLayer()
		self.getDistancePoint = getPoint(canvas)
		QObject.connect(self.getDistancePoint , SIGNAL("canvasClickedWithModifiers") , self.distanceOnCanvasClicked ) 
		canvas.setMapTool(self.getDistancePoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		
	def distanceOnCanvasClicked(self, point, button, modifiers):
		if button != Qt.LeftButton:
			return
		canvas = self.iface.mapCanvas()
		point = canvas.mapRenderer().mapToLayerCoordinates(self.lineLayer, point)
		dlg = distance(point)
		if dlg.exec_():
			radius    = dlg.distance.value()
			if radius==0:
				return
			precision = dlg.precision.value()
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPolyline( [QgsPoint(point.x()+radius*math.cos(math.pi/180*a),point.y()+radius*math.sin(math.pi/180*a)) for a in range(0,360,1)] ))
			f.setAttributeMap( {0: QVariant(point.x()),
								1: QVariant(point.y()),
								2: QVariant(radius),
								3: QVariant(precision)} )
			self.lineLayer.dataProvider().addFeatures( [f] )
			self.lineLayer.updateExtents()
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPoint(point))
			self.pointLayer.dataProvider().addFeatures( [f] )
			self.pointLayer.updateExtents()
			canvas.refresh()
		
	def distanceToolChanged(self, tool):
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		self.distanceAction.setChecked( False )
		self.iface.mapCanvas().unsetMapTool(self.getDistancePoint)
		
	def triangulationStart(self):
		canvas = self.iface.mapCanvas()
		if self.triangulAction.isChecked() is False:
			canvas.unsetMapTool(self.getInitialTriangulationPoint)
			return
		if self.lineLayer is False or self.pointLayer is False:
			self.triangulAction.setChecked(False)
			return
		self.triangulAction.setChecked( True )
		self.getInitialTriangulationPoint = getPoint(canvas)
		QObject.connect(self.getInitialTriangulationPoint , SIGNAL("canvasClickedWithModifiers") , self.triangulationOnCanvasClicked ) 
		canvas.setMapTool(self.getInitialTriangulationPoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)

	def triangulationOnCanvasClicked(self, point, button, modifiers):
		if button != Qt.LeftButton:
			return
		canvas = self.iface.mapCanvas()
		point = canvas.mapRenderer().mapToLayerCoordinates(self.lineLayer, point)
		xyrp = self.getCircles(point)
		self.triangulationProcess = triangulationProcess(point,xyrp)		
		try:
			triangulatedPoint =  self.triangulationProcess.getSolution()
		except NameError as detail:
				QMessageBox.warning( self.iface , "Triangulation", detail )
		f = QgsFeature()
		f.setGeometry(QgsGeometry.fromPoint(triangulatedPoint))
		self.pointLayer.dataProvider().addFeatures( [f] )
		self.pointLayer.updateExtents()
		canvas.refresh()


	def triangulationToolChanged(self, tool):
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)
		self.triangulAction.setChecked( False )
		self.iface.mapCanvas().unsetMapTool(self.getInitialTriangulationPoint)
		
	def getCircles(self,point):
		mapTolerance = 0.6 # in meters
		rect = QgsRectangle(point.x()-mapTolerance,point.y()-mapTolerance,point.x()+mapTolerance,point.y()+mapTolerance)
		provider = self.lineLayer.dataProvider()
		ix = provider.fieldNameIndex('x')
		iy = provider.fieldNameIndex('y')
		ir = provider.fieldNameIndex('radius')
		ip = provider.fieldNameIndex('precision')
		provider.select([ix,iy,ir,ip], rect, True, True)
		xyrp = []
		f = QgsFeature()
		self.rubber.reset()
		while (provider.nextFeature(f)):
			fm = f.attributeMap()
			x = fm[ix].toDouble()
			y = fm[iy].toDouble()
			r = fm[ir].toDouble()
			p = fm[ip].toDouble()
			xyrp.append([QgsPoint(x[0],y[0]),r[0],p[0]])
			self.rubber.addGeometry(f.geometry(),self.lineLayer)
		return xyrp
		
class getPoint(QgsMapToolEmitPoint):
	def __init__(self, canvas):
		QgsMapToolEmitPoint.__init__(self, canvas)

	def canvasPressEvent(self, mouseEvent):
		point = self.toMapCoordinates( mouseEvent.pos() )
		self.emit( SIGNAL( "canvasClickedWithModifiers" ), point, mouseEvent.button(), mouseEvent.modifiers() )	
		
		
	
		

