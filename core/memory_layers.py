# -----------------------------------------------------------
#
# Intersect It is a QGIS plugin to place observations (distance or orientation)
# with their corresponding precision, intersect them using a least-squares solution
# and save dimensions in a dedicated layer to produce maps.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
# -----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ---------------------------------------------------------------------

from PyQt4.QtCore import Qt
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsProject
from mysettings import MySettings


class MemoryLayers():
    def __init__(self, iface):
        self.iface = iface
        self.settings = MySettings()

    def set_layer_visible(self, layer):
        root = QgsProject.instance().layerTreeRoot()
        node = root.findLayer(layer.id())
        node.setVisible(Qt.Checked)
        
    def remove_layers(self):
        try:
            QgsMapLayerRegistry.instance().removeMapLayer(self.settings.value("memoryLineLayer"))
            QgsMapLayerRegistry.instance().removeMapLayer(self.settings.value("memoryPointLayer"))
        except AttributeError:
            return
        
    def clean_layers(self):
        for layer_name in ('memoryLineLayer', 'memoryPointLayer'):
            layer_id = self.settings.value(layer_name)
            layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
            layer.selectAll()
            fids = layer.selectedFeaturesIds()
            layer.dataProvider().deleteFeatures(fids)
            layer.featuresDeleted.emit(fids)
        self.iface.mapCanvas().refresh()

    def line_layer(self):
        layer_id = self.settings.value("memoryLineLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        if layer is None:
            epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            layer = QgsVectorLayer("LineString?crs=%s&field=id:string&field=type:string&field=x:double&field=y:double&field=observation:double&field=precision:double&index=yes" % epsg, "IntersectIt Lines", "memory")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            layer.layerDeleted.connect(self.__line_layer_deleted)
            layer.featureDeleted.connect(self.__line_layer_feature_deleted)
            self.settings.setValue("memoryLineLayer", layer.id())
        else:
            self.set_layer_visible(layer)
        return layer

    def __line_layer_deleted(self):
        self.settings.setValue("memoryLineLayer", "")

    def __line_layer_feature_deleted(self, fid):
        # todo: delete corresponding feature in other layer
        print "hay"

    def point_layer(self):
        layer_id = self.settings.value("memoryPointLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        if layer is None:
            epsg = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
            layer = QgsVectorLayer("Point?crs=%s&field=id:string&index=yes" % epsg, "IntersectIt Points", "memory")
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            layer.layerDeleted.connect(self.__pointLayerDeleted)
            self.settings.setValue("memoryPointLayer", layer.id())
        else:
            self.set_layer_visible(layer)
        return layer

    def __pointLayerDeleted(self):
        self.settings.setValue("memoryPointLayer", "")

