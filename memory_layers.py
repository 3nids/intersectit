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


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class memoryLayers():
	def __init__(self,iface):
		self.iface = iface
		
   	def lineLayerDeleted(self):
		QgsProject.instance().writeEntry("IntersectIt", "memory_line_layer", "")

	def pointLayerDeleted(self):
		QgsProject.instance().writeEntry("IntersectIt", "memory_point_layer", "")

	def lineLayer(self):
		layerID = QgsProject.instance().readEntry("IntersectIt", "memory_line_layer", "")[0]
		layer = next(    ( layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
			layer = QgsVectorLayer("LineString?crs=%s&field=id:string&field=type:string&field=x:double&field=y:double&field=measure:double&field=precision:double&index=yes" % epsg, "IntersectIt Lines", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.lineLayerDeleted )
			QgsProject.instance().writeEntry("IntersectIt", "memory_line_layer", layer.id())
		else: self.iface.legendInterface().setLayerVisible (layer,True)
		return layer			

	def pointLayer(self):
		layerID = QgsProject.instance().readEntry("IntersectIt", "memory_point_layer", "")[0]
		layer = next(    ( layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID ),  False ) 
		if layer is False:
			epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
			layer = QgsVectorLayer("Point?crs=%s&field=id:string&index=yes" % epsg, "IntersectIt Points", "memory") 
			QgsMapLayerRegistry.instance().addMapLayer(layer) 
			QObject.connect( layer, SIGNAL("layerDeleted()") , self.pointLayerDeleted )
			QgsProject.instance().writeEntry("IntersectIt", "memory_point_layer", layer.id())
		else: self.iface.legendInterface().setLayerVisible (layer,True)
		return layer			

