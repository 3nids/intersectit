"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Memory layers class
"""

from PyQt4.QtCore import SIGNAL, QObject
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer

from mysettings import MySettings


class MemoryLayers():
    def __init__(self, iface):
        self.iface = iface
        self.settings = MySettings()

    def lineLayer(self):
        layerID = self.settings.value("memoryLineLayer")
        layer = next((layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID),  None)
        if layer is None:
            epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            layer = QgsVectorLayer("LineString?crs=%s&field=id:string&field=type:string&field=x:double&field=y:double&field=measure:double&field=precision:double&index=yes" % epsg, "IntersectIt Lines", "memory")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            QObject.connect(layer, SIGNAL("layerDeleted()"), self.__lineLayerDeleted)
            QObject.connect(layer, SIGNAL("featureDeleted(int)"), self.__lineLayerFeatureDeleted)
            self.settings.setValue("memoryLineLayer", layer.id())
        else:
            self.iface.legendInterface().setLayerVisible(layer, True)
        return layer

    def __lineLayerDeleted(self):
        self.settings.setValue("memoryLineLayer", "")

    def __lineLayerFeatureDeleted(self, fid):
        print "hay"

    def pointLayer(self):
        layerID = self.settings.value("memoryPointLayer")
        layer = next((layer for layer in self.iface.legendInterface().layers() if layer.id() == layerID),  None)
        if layer is None:
            epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            layer = QgsVectorLayer("Point?crs=%s&field=id:string&index=yes" % epsg, "IntersectIt Points", "memory")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            QObject.connect(layer, SIGNAL("layerDeleted()"), self.__pointLayerDeleted)
            self.settings.setValue("memoryPointLayer", layer.id())
        else:
            self.iface.legendInterface().setLayerVisible(layer, True)
        return layer

    def __pointLayerDeleted(self):
        self.settings.setValue("memoryPointLayer", "")

