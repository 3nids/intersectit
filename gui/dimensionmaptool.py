#-----------------------------------------------------------
#
# Intersect It is a QGIS plugin to place observations (distance or orientation)
# with their corresponding precision, intersect them using a least-squares solution
# and save dimensions in a dedicated layer to produce maps.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
#-----------------------------------------------------------
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
#---------------------------------------------------------------------

from qgis.core import QgsMapLayerRegistry, QgsTolerance, QgsSnapper, QgsFeature, QgsFeatureRequest
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMessageBar

from ..core.arc import Arc
from ..core.mysettings import MySettings


class DimensionMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.lineRubber = QgsRubberBand(self.mapCanvas)
        self.lineRubber.setWidth(4)
        self.editing = False
        self.snapLayer = None
        QgsMapTool.__init__(self, self.mapCanvas)

    def activate(self):
        QgsMapTool.activate(self)
        layerid = MySettings().value("dimensionLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if layer is None:
            self.iface.messageBar().pushMessage("Intersect It", "Dimension layer must defined.",
                                                QgsMessageBar.WARNING, 3)
            self.mapCanvas.unsetMapTool(self)
            return
        if not layer.isEditable():
            self.iface.messageBar().pushMessage("Intersect It", "Dimension layer must be editable to edit arcs.",
                                                QgsMessageBar.WARNING, 3)
            self.mapCanvas.unsetMapTool(self)
            return
        self.snapLayer = QgsSnapper.SnapLayer()
        self.snapLayer.mLayer = layer
        self.snapLayer.mSnapTo = QgsSnapper.SnapToVertexAndSegment
        self.snapLayer.mTolerance = 7
        self.snapLayer.mUnitType = QgsTolerance.Pixels
        self.editing = False
        self.arc = None

    def deactivate(self):
        self.lineRubber.reset()
        QgsMapTool.deactivate(self)

    def canvasPressEvent(self, mouseEvent):
        feature = self.snapToDimensionLayer(mouseEvent.pos())
        if feature is None:
            return
        self.editing = True
        line = feature.geometry().asPolyline()
        point = self.map2layer(mouseEvent.pos())
        self.arc = Arc(line[0], point, line[len(line)-1])
        self.featureId = feature.id()

    def canvasReleaseEvent(self, mouseEvent):
        if not self.editing:
            return
        self.editing = False
        self.lineRubber.reset()
        point = self.map2layer(mouseEvent.pos())
        if point is None:
            return
        self.arc.setPoint(point)
        geom = self.arc.geometry()
        layer = self.snapLayer.mLayer
        editBuffer = layer.editBuffer()
        editBuffer.changeGeometry(self.featureId, geom)
        layer.triggerRepaint()

    def canvasMoveEvent(self, mouseEvent):
        if not self.editing:
            feature = self.snapToDimensionLayer(mouseEvent.pos())
            if feature is None:
                self.lineRubber.reset()
                return
            self.lineRubber.setToGeometry(feature.geometry(), self.snapLayer.mLayer)
        else:
            point = self.map2layer(mouseEvent.pos())
            if point is None:
                return
            self.arc.setPoint(point)
            self.lineRubber.setToGeometry(self.arc.geometry(), self.snapLayer.mLayer)

    def map2layer(self, pos):
        point = self.toMapCoordinates(pos)
        return self.mapCanvas.mapRenderer().mapToLayerCoordinates(self.snapLayer.mLayer, point)

    def snapToDimensionLayer(self, pixPoint):
        snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        snapper.setSnapLayers([self.snapLayer])
        snapper.setSnapMode(QgsSnapper.SnapWithOneResult)

        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        if ok == 0 and len(snappingResults) > 0:
            featureId = snappingResults[0].snappedAtGeometry
            f = QgsFeature()
            if self.snapLayer.mLayer.getFeatures(QgsFeatureRequest().setFilterFid(featureId)).nextFeature(f) is False:
                return None
            return f
        else:
            return None
