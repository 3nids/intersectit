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
from settings import settings
from place_arc import placeArc
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
		# create rubber band to emphasis selected circles
		self.rubber = QgsRubberBand(self.iface.mapCanvas())
		# settings
		self.settings = QSettings("Triangulation","Triangulation")

	def initGui(self):
		self.toolBar = self.iface.addToolBar("Triangulation")
		self.toolBar.setObjectName("Triangulation")
		# distance
		self.distanceAction = QAction(QIcon(":/plugins/triangulation/icons/distance.png"), "insert distance", self.iface.mainWindow())
		self.distanceAction.setCheckable(True)
		QObject.connect(self.distanceAction, SIGNAL("triggered()"), self.distanceStart)
		self.toolBar.addAction(self.distanceAction)
		self.iface.addPluginToMenu("&Triangulation", self.distanceAction)	
		# triangulation
		self.triangulAction = QAction(QIcon(":/plugins/triangulation/icons/intersect.png"), "triangulate", self.iface.mainWindow())
		self.triangulAction.setCheckable(True)
		QObject.connect(self.triangulAction, SIGNAL("triggered()"), self.triangulationStart)
		self.toolBar.addAction(self.triangulAction)
		self.iface.addPluginToMenu("&Triangulation", self.triangulAction)	
		# settings
		self.uisettings = settings(self.iface)
		QObject.connect(self.uisettings , SIGNAL( "accepted()" ) , self.applySettings)
		self.uisettingsAction = QAction("settings", self.iface.mainWindow())
		QObject.connect(self.uisettingsAction, SIGNAL("triggered()"), self.uisettings.exec_)
		self.iface.addPluginToMenu("&Triangulation", self.uisettingsAction)	
		
				
	def unload(self):
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)
		print "TODO: instersect unload"
		try:
			print "Triangulation :: Removing temporary layer"
			QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer().id()) 
			QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer.id()) 
		except AttributeError:
			return
			
	def applySettings(self):
		self.rubber.setWidth( self.settings.value("rubber_width",2).toDouble()[0] )
		R = self.settings.value("rubber_colorR",255).toInt()[0]
		G = self.settings.value("rubber_colorG",0  ).toInt()[0]
		B = self.settings.value("rubber_colorB",0  ).toInt()[0]
		self.rubber.setColor(QColor(R,G,B,255))		
			
	def lineLayerDeleted(self):
		QgsProject.instance().writeEntry("Triangulation", "memory_line_layer", "")

	def pointLayerDeleted(self):
		QgsProject.instance().writeEntry("Triangulation", "memory_point_layer", "")
		
	def lineLayer(self):
		layerID = QgsProject.instance().readEntry("Triangulation", "memory_line_layer", "")[0]
		layer = next(    ( layer for layer in self.iface.mapCanvas().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			layer = QgsVectorLayer("LineString?crs=EPSG:21781&field=x:double&field=y:double&field=radius:double&field=precision:double&index=yes", "Triangulation Lines", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.lineLayerDeleted )
			QgsProject.instance().writeEntry("Triangulation", "memory_line_layer", layer.id())
		return layer			

	def pointLayer(self):
		layerID = QgsProject.instance().readEntry("Triangulation", "memory_point_layer", "")[0]
		layer = next(    ( layer for layer in self.iface.mapCanvas().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			layer = QgsVectorLayer("Point?crs=EPSG:21781&index=yes", "Triangulation Points", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.pointLayerDeleted )
			QgsProject.instance().writeEntry("Triangulation", "memory_point_layer", layer.id())
		return layer			

	def distanceStart(self):
		canvas = self.iface.mapCanvas()
		if self.distanceAction.isChecked() is False:
			canvas.unsetMapTool(self.getDistancePoint)
			return
		self.distanceAction.setChecked( True )
		self.getDistancePoint = getPoint(canvas)
		QObject.connect(self.getDistancePoint , SIGNAL("canvasClickedWithModifiers") , self.distanceOnCanvasClicked ) 
		canvas.setMapTool(self.getDistancePoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		
	def distanceOnCanvasClicked(self, point, button, modifiers):
		if button != Qt.LeftButton:
			return
		canvas = self.iface.mapCanvas()
		point = canvas.mapRenderer().mapToLayerCoordinates(self.lineLayer(), point)
		dlg = distance(point)
		if dlg.exec_():
			radius    = dlg.distance.value()
			if radius==0:
				return
			precision = dlg.precision.value()
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPolyline( [QgsPoint(point.x()+radius*math.cos(math.pi/180*a),point.y()+radius*math.sin(math.pi/180*a)) for a in range(0,361,3)] ))
			f.setAttributeMap( {0: QVariant(point.x()),
								1: QVariant(point.y()),
								2: QVariant(radius),
								3: QVariant(precision)} )
			self.lineLayer().dataProvider().addFeatures( [f] )
			self.lineLayer().updateExtents()
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPoint(point))
			self.pointLayer().dataProvider().addFeatures( [f] )
			self.pointLayer().updateExtents()
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
		self.triangulAction.setChecked( True )
		self.getInitialTriangulationPoint = getPoint(canvas)
		QObject.connect(self.getInitialTriangulationPoint , SIGNAL("canvasClickedWithModifiers") , self.triangulationOnCanvasClicked ) 
		canvas.setMapTool(self.getInitialTriangulationPoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)

	def triangulationOnCanvasClicked(self, point, button, modifiers):
		if button != Qt.LeftButton:
			return
		canvas = self.iface.mapCanvas()
		point = canvas.mapRenderer().mapToLayerCoordinates(self.lineLayer(), point)
		xyrpi = self.getCircles(point)
		self.triangulationProcess = triangulationProcess(point,xyrpi)		
		try:
			triangulatedPoint =  self.triangulationProcess.getSolution()
		except NameError as detail:
				QMessageBox.warning( self.iface.mainWindow() , "Triangulation", "%s" % detail )
				return
		f = QgsFeature()
		f.setGeometry(QgsGeometry.fromPoint(triangulatedPoint))
		self.pointLayer().dataProvider().addFeatures( [f] )
		self.pointLayer().updateExtents()
		canvas.refresh()
		if self.settings.value("placeArc",1).toInt()[0] == 1:
			# check that dimension layer and field have been set
			dimLayer                               = next(    ( layer for layer in self.iface.mapCanvas().layers()        if layer.id() == QgsProject.instance().readEntry("Triangulation", "dimension_layer", "")[0] ),  False )
			if dimLayer is not False: dimFieldName = next(    ( field for field in dimLayer.dataProvider().fieldNameMap() if field      == QgsProject.instance().readEntry("Triangulation", "dimension_field", "")[0] ),  False )
			while dimLayer is False or dimFieldName is False:
				if dimLayer is False:
					reply = QMessageBox.question( self.iface.mainWindow() , "Triangulation", "To place dimension arcs, you must select a dimension layer in the preferences. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No:	 return
					if self.uisettings.exec_() ==	 0: return
				elif dimFieldName is False:
					reply = QMessageBox.question( self.iface.mainWindow() , "Triangulation", "To place dimension arcs, please select a field for the label. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No:	 return
					if self.uisettings.exec_() == 0: return
				dimLayer                               = next(    ( layer for layer in self.iface.mapCanvas().layers()        if layer.id() == QgsProject.instance().readEntry("Triangulation", "dimension_layer", "")[0] ),  False )
				if dimLayer is not False: dimFieldName = next(    ( field for field in dimLayer.dataProvider().fieldNameMap() if field      == QgsProject.instance().readEntry("Triangulation", "dimension_field", "")[0] ),  False )
			dlg = placeArc(self.iface,dimLayer,triangulatedPoint,xyrpi)
			if dlg.exec_():
				print 1
		

	def triangulationToolChanged(self, tool):
		self.rubber.reset()
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.triangulationToolChanged)
		self.triangulAction.setChecked( False )
		self.iface.mapCanvas().unsetMapTool(self.getInitialTriangulationPoint)
		
	def getCircles(self,point):
		tolerance = self.settings.value("tolerance",0.6).toDouble()[0]
		units = self.settings.value("units","map").toString()
		if units == "pixels":
			tolerance *= self.iface.mapCanvas().mapUnitsPerPixel()
		rect = QgsRectangle(point.x()-tolerance,point.y()-tolerance,point.x()+tolerance,point.y()+tolerance)
		provider = self.lineLayer().dataProvider()
		ix = provider.fieldNameIndex('x')
		iy = provider.fieldNameIndex('y')
		ir = provider.fieldNameIndex('radius')
		ip = provider.fieldNameIndex('precision')
		provider.select([ix,iy,ir,ip], rect, True, True)
		xyrpi = []
		f = QgsFeature()
		self.rubber.reset()
		while (provider.nextFeature(f)):
			fm = f.attributeMap()
			x = fm[ix].toDouble()[0]
			y = fm[iy].toDouble()[0]
			r = fm[ir].toDouble()[0]
			p = fm[ip].toDouble()[0]
			xyrpi.append([QgsPoint(x,y),r,p,f.id()])
			self.rubber.addGeometry(f.geometry(),self.lineLayer())
		return xyrpi
		
class getPoint(QgsMapToolEmitPoint):
	def __init__(self, canvas):
		QgsMapToolEmitPoint.__init__(self, canvas)

	def canvasPressEvent(self, mouseEvent):
		point = self.toMapCoordinates( mouseEvent.pos() )
		self.emit( SIGNAL( "canvasClickedWithModifiers" ), point, mouseEvent.button(), mouseEvent.modifiers() )	
		
		
	
		

