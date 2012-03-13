"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Memory layers class
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from settings import IntersectItSettings

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class memoryLayers():
	def __init__(self,iface):
		self.iface = iface
		self.settings = IntersectItSettings()	

	def lineLayer(self):
		layerID = self.settings.value("memoryLineLayer")
		layer = next(    ( layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
			layer = QgsVectorLayer("LineString?crs=%s&field=id:string&field=type:string&field=x:double&field=y:double&field=measure:double&field=precision:double&index=yes" % epsg, "IntersectIt Lines", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.lineLayerDeleted )
			QObject.connect( layer, SIGNAL("featureDeleted(int)") , self.lineLayerFeatureDeleted )
			self.settings.setValue("memoryLineLayer", layer.id())
		else: self.iface.legendInterface().setLayerVisible(layer,True)
		return layer
		
   	def lineLayerDeleted(self):
		self.settings.setValue("memoryLineLayer", "")

	def lineLayerFeatureDeleted(fid):
		print "hay"



	def pointLayer(self):
		layerID = self.settings.value("memoryPointLayer")
		layer = next(    ( layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
			layer = QgsVectorLayer("Point?crs=%s&field=id:string&index=yes" % epsg, "IntersectIt Points", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.pointLayerDeleted )
			self.settings.setValue("memoryPointLayer", layer.id())
		else: self.iface.legendInterface().setLayerVisible(layer,True)
		return layer
	
	def pointLayerDeleted(self):
		self.settings.setValue("memoryPointLayer", "")

