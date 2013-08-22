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
from ..core.orientationline import OrientationLine
from ..core.mysettings import MySettings


class DimensionMapTool(QgsMapTool):
    def __init__(self, iface, observationType):
        self.iface = iface
        self.observationType = observationType
        self.mapCanvas = iface.mapCanvas()
        self.settings = MySettings()
        self.lineRubber = QgsRubberBand(self.mapCanvas)
        self.editing = False
        self.snapLayer = None
        QgsMapTool.__init__(self, self.mapCanvas)

    def activate(self):
        QgsMapTool.activate(self)
        self.lineRubber.setWidth(self.settings.value("rubberWidth"))
        self.lineRubber.setColor(self.settings.value("rubberColor"))
        layerid = self.settings.value("dimensionLayer")
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
        self.checkType = self.settings.value("dimensionCheckType")
        self.fieldTypeIdx = layer.fieldNameIndex(self.settings.value("typeField"))
        if self.checkType and (self.fieldTypeIdx == -1 or not self.settings.value("dimensionWriteType")):
            self.checkType = False
            self.iface.messageBar().pushMessage("Intersect It",
                                                "Dimension type cannot be checked since field type could not be found.",
                                                QgsMessageBar.INFO, 3)
        # unset this tool if the layer is removed
        layer.layerDeleted.connect(self.unsetMapTool)
        # create snapper for this layer
        self.snapLayer = QgsSnapper.SnapLayer()
        self.snapLayer.mLayer = layer
        self.snapLayer.mSnapTo = QgsSnapper.SnapToVertexAndSegment
        self.snapLayer.mTolerance = self.settings.value("selectTolerance")
        if self.settings.value("selectUnits") == "map":
            self.snapLayer.mUnitType = QgsTolerance.MapUnits
        else:
            self.snapLayer.mUnitType = QgsTolerance.Pixels
        self.editing = False
        self.drawObject = None

    def unsetMapTool(self):
        self.mapCanvas.unsetMapTool(self)

    def deactivate(self):
        self.lineRubber.reset()
        layer = QgsMapLayerRegistry.instance().mapLayer(self.settings.value("dimensionLayer"))
        if layer is not None:
            try:
                layer.layerDeleted.disconnect(self.unsetMapTool)
            except TypeError:
                pass
        QgsMapTool.deactivate(self)

    def canvasPressEvent(self, mouseEvent):
        feature = self.snapToDimensionLayer(mouseEvent.pos())
        if feature is None:
            return
        line = feature.geometry().asPolyline()
        point = self.map2layer(mouseEvent.pos())
        if self.observationType == "distance":
            if len(line) == 0:
                return
            self.editing = True
            self.drawObject = Arc(line[0], point, line[len(line)-1])
        else:
            if len(line) != 2:
                return
            self.editing = True
            self.drawObject = OrientationLine(line, point)
        self.featureId = feature.id()


    def canvasReleaseEvent(self, mouseEvent):
        if not self.editing:
            return
        self.editing = False
        self.lineRubber.reset()
        point = self.map2layer(mouseEvent.pos())
        if point is None:
            return
        self.drawObject.setPoint(point)
        geom = self.drawObject.geometry()
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
            self.drawObject.setPoint(point)
            self.lineRubber.setToGeometry(self.drawObject.geometry(), self.snapLayer.mLayer)

    def map2layer(self, pos):
        point = self.toMapCoordinates(pos)
        return self.mapCanvas.mapRenderer().mapToLayerCoordinates(self.snapLayer.mLayer, point)

    def snapToDimensionLayer(self, pixPoint):
        snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        snapper.setSnapLayers([self.snapLayer])
        snapper.setSnapMode(QgsSnapper.SnapWithResultsWithinTolerances)

        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        for result in snappingResults:
            featureId = result.snappedAtGeometry
            f = QgsFeature()
            if self.snapLayer.mLayer.getFeatures(QgsFeatureRequest().setFilterFid(featureId)).nextFeature(f) is not False:
                if self.checkType:
                    if f[self.fieldTypeIdx] != self.observationType:
                        continue
                if self.observationType == "orientation":
                    line = f.geometry().asPolyline()
                    if len(line) != 2:
                        continue
                return f
        return None
