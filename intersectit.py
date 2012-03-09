"""
Intersect It QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Main class
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from maptools import placeMeasureOnMap, placeIntersectionOnMap
from place_distance import place_distance
from observation import observation
from settings import settingsDialog, IntersectItSettings
from place_dimension import placeDimension
from intersection import intersection
from memory_layers import memoryLayers

# Initialize Qt resources from file resources.py
import resources

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class intersectit ():
	def __init__(self, iface):
		# Save reference to the QGIS interface
		self.iface = iface
		# create rubber band to emphasis selected circles
		self.rubber = QgsRubberBand(self.iface.mapCanvas())
		# init memory layers
		memLay = memoryLayers(iface)
		self.lineLayer  = memLay.lineLayer
		self.pointLayer = memLay.pointLayer
		# settings
		self.settings = IntersectItSettings()
		# apply settings at first launch
		self.applySettings()

	def initGui(self):
		self.toolBar = self.iface.addToolBar("IntersectIt")
		self.toolBar.setObjectName("IntersectIt")
		# distance
		self.distanceAction = QAction(QIcon(":/plugins/intersectit/icons/distance.png"), "place distance", self.iface.mainWindow())
		self.distanceAction.setCheckable(True)
		QObject.connect(self.distanceAction, SIGNAL("triggered()"), self.distanceInitTool)
		self.toolBar.addAction(self.distanceAction)
		self.iface.addPluginToMenu("&Intersect It", self.distanceAction)	
		# intersection
		self.intersectAction = QAction(QIcon(":/plugins/intersectit/icons/intersection.png"), "intersection", self.iface.mainWindow())
		self.intersectAction.setCheckable(True)
		QObject.connect(self.intersectAction, SIGNAL("triggered()"), self.intersectionInitTool)
		self.toolBar.addAction(self.intersectAction)
		self.iface.addPluginToMenu("&Intersect It", self.intersectAction)
		# settings
		self.uisettings = settingsDialog(self.iface)	
		QObject.connect(self.uisettings , SIGNAL( "accepted()" ) , self.applySettings)
		self.uisettingsAction = QAction("settings", self.iface.mainWindow())
		QObject.connect(self.uisettingsAction, SIGNAL("triggered()"), self.uisettings.exec_)
		self.iface.addPluginToMenu("&Intersect It", self.uisettingsAction)	
		# cleaner
		self.cleanerAction = QAction(QIcon(":/plugins/intersectit/icons/cleaner.png"), "clean points and circles", self.iface.mainWindow())
		QObject.connect(self.cleanerAction, SIGNAL("triggered()"), self.cleanMemoryLayers)
		self.toolBar.addAction(self.cleanerAction)
		self.iface.addPluginToMenu("&Intersect It", self.cleanerAction)	

	def unload(self):
		self.iface.removePluginMenu("&Intersect It",self.distanceAction)
		self.iface.removePluginMenu("&Intersect It",self.intersectAction)
		self.iface.removePluginMenu("&Intersect It",self.uisettingsAction)
		self.iface.removePluginMenu("&Intersect It",self.cleanerAction)
		self.iface.removeToolBarIcon(self.distanceAction)
		self.iface.removeToolBarIcon(self.intersectAction)	
		self.iface.removeToolBarIcon(self.cleanerAction)	
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.intersectionToolChanged)
		try:
			print "IntersecIt :: Removing temporary layer"
			QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer().id()) 
			QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer.id()) 
		except AttributeError:
			return

	def applySettings(self):
		self.rubber.setWidth( self.settings.value("rubber_width").toDouble()[0] )
		R = self.settings.value("rubber_colorR").toInt()[0]
		G = self.settings.value("rubber_colorG").toInt()[0]
		B = self.settings.value("rubber_colorB").toInt()[0]
		self.rubber.setColor(QColor(R,G,B,255))		

	def cleanMemoryLayers(self):
		self.rubber.reset()
		lineProv = self.lineLayer().dataProvider()
		pointProv = self.pointLayer().dataProvider()
		lineProv.select([])
		pointProv.select([])
		f = QgsFeature()
		f2del = []
		while lineProv.nextFeature(f):
			f2del.append(f.id())
		lineProv.deleteFeatures(f2del)
		f2del = []
		while pointProv.nextFeature(f):
			f2del.append(f.id())
		pointProv.deleteFeatures(f2del)
		self.iface.mapCanvas().refresh()

	def distanceInitTool(self):
		canvas = self.iface.mapCanvas()
		if self.distanceAction.isChecked() is False:
			canvas.unsetMapTool(self.placeDistancePoint)
			return
		self.distanceAction.setChecked( True )
		snapping = self.settings.value( "snapping").toInt()[0]
		self.placeDistancePoint = placeMeasureOnMap(canvas,snapping)
		QObject.connect(self.placeDistancePoint , SIGNAL("distancePlaced") , self.distancePlaceIt ) 
		canvas.setMapTool(self.placeDistancePoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)

	def distancePlaceIt(self, point, pixpoint):
		canvas = self.iface.mapCanvas()
		#snap to layers
		if self.settings.value( "snapping").toInt()[0] == 1:
			result,snappingResults = QgsMapCanvasSnapper(canvas).snapToBackgroundLayers(pixpoint,[])
			if result == 0 and len(snappingResults)>0:
				point = QgsPoint(snappingResults[0].snappedVertex)
		# creates ditance with dialog
		dlg = place_distance(point)
		if dlg.exec_():
			radius    = dlg.distance.value()
			precision = dlg.precision.value()
			if radius==0: return
			observation( canvas,self.lineLayer,self.pointLayer,"distance",point,radius,precision )

	def distanceToolChanged(self, tool):
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.distanceToolChanged)
		self.distanceAction.setChecked( False )
		self.iface.mapCanvas().unsetMapTool(self.placeDistancePoint)

	def intersectionInitTool(self):
		canvas = self.iface.mapCanvas()
		if self.intersectAction.isChecked() is False:
			canvas.unsetMapTool(self.placeInitialIntersectionPoint)
			return
		self.intersectAction.setChecked( True )
		self.placeInitialIntersectionPoint = placeIntersectionOnMap(canvas,self.lineLayer,self.rubber)
		QObject.connect(self.placeInitialIntersectionPoint , SIGNAL("intersectionStarted") , self.intersectionStarted ) 
		canvas.setMapTool(self.placeInitialIntersectionPoint)
		QObject.connect( canvas, SIGNAL( "mapToolSet(QgsMapTool *)" ), self.intersectionToolChanged)

	def intersectionStarted(self, point, observations):
		canvas = self.iface.mapCanvas()
	
		self.intersectionProcess = intersection(point,observations)		
		try:
			intersectedPoint =  self.intersectionProcess.getSolution()
		except NameError as detail:
				QMessageBox.warning( self.iface.mainWindow() , "IntersectIt", "%s" % detail )
				return
		# if we do not place any dimension, place the intersected point in layer
		if self.settings.value("placeDimension").toInt()[0] == 0:
			f = QgsFeature()
			f.setGeometry(QgsGeometry.fromPoint(intersectedPoint))
			self.pointLayer().dataProvider().addFeatures( [f] )
			self.pointLayer().updateExtents()
			canvas.refresh()
		# check that dimension layer and fields have been set correctly
		while True:
			if self.settings.value("placeDimension").toInt()[0] == 0: return # if we do not place any dimension, skip
			dimLayer = next( ( layer for layer in self.iface.mapCanvas().layers() if layer.id() == QgsProject.instance().readEntry("IntersectIt", "dimension_layer", "")[0] ), False )
			if dimLayer is False:
				reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To place dimension arcs, you must select a dimension layer in the preferences. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
				if reply == QMessageBox.No:	        return
				if self.uisettings.exec_() ==	 0: return
				continue
			if self.settings.value("placeMeasure").toInt()[0] == 1: 
				dimensionField = next( ( True for field in dimLayer.dataProvider().fieldNameMap() if field == QgsProject.instance().readEntry("IntersectIt", "dimension_field", "")[0] ), False )
				if dimensionField is False:
					ok = False
					reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To place dimension arcs, please select a field for the dimension. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No:  	 return
					if self.uisettings.exec_() == 0: return
					continue
			if self.settings.value("placePrecision").toInt()[0] == 1: 
				precisionField = next( ( True for field in dimLayer.dataProvider().fieldNameMap() if field == QgsProject.instance().readEntry("IntersectIt", "precision_field", "")[0] ), False )
				if precisionField is False:
					ok = False
					reply = QMessageBox.question( self.iface.mainWindow() , "IntersectIt", "To place dimension arcs, please select a field for the precision. Would you like to open settings?" , QMessageBox.Yes, QMessageBox.No )			
					if reply == QMessageBox.No: 	 return
					if self.uisettings.exec_() == 0: return
					continue
			break
		dlg = placeDimension(self.iface,intersectedPoint,xyrpi,[self.lineLayer(),self.pointLayer()])
		dlg.exec_()		

	def intersectionToolChanged(self, tool):
		self.rubber.reset()
		QObject.disconnect( self.iface.mapCanvas(), SIGNAL( "mapToolSet(QgsMapTool *)" ), self.intersectionToolChanged)
		self.intersectAction.setChecked( False )
		self.iface.mapCanvas().unsetMapTool(self.placeInitialIntersectionPoint)
