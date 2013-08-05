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

from PyQt4.QtGui import QMessageBox
from qgis.core import QGis, QgsFeatureRequest, QgsFeature, QgsGeometry, QgsMapLayerRegistry, QgsMapLayer, QgsTolerance, QgsSnapper
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMessageBar

from ..core.mysettings import MySettings

from mysettingsdialog import MySettingsDialog


class SimpleIntersectionMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        QgsMapTool.__init__(self, self.mapCanvas)
        self.settings = MySettings()
        self.rubber = QgsRubberBand(self.mapCanvas)

    def deactivate(self):
        self.rubber.reset()
        QgsMapLayerRegistry.instance().layersAdded.disconnect(self.updateSnapperList)
        QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateSnapperList)
        QgsMapTool.deactivate(self)

    def activate(self):
        QgsMapTool.activate(self)
        self.rubber.setWidth(self.settings.value("rubberWidth"))
        self.rubber.setColor(self.settings.value("rubberColor"))
        self.updateSnapperList()
        QgsMapLayerRegistry.instance().layersAdded.connect(self.updateSnapperList)
        QgsMapLayerRegistry.instance().layersRemoved.connect(self.updateSnapperList)
        self.checkLayer()

    def updateSnapperList(self, dummy=None):
        # make a snapper list of all line and polygons layers
        self.snapperList = []
        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType() and layer.geometryType() in (QGis.Line, QGis.Polygon):
                snapLayer = QgsSnapper.SnapLayer()
                snapLayer.mLayer = layer
                snapLayer.mSnapTo = QgsSnapper.SnapToVertex
                snapLayer.mTolerance = self.settings.value("selectTolerance")
                if self.settings.value("selectUnits") == "map":
                    snapLayer.mUnitType = QgsTolerance.MapUnits
                else:
                    snapLayer.mUnitType = QgsTolerance.Pixels
                self.snapperList.append(snapLayer)

    def canvasMoveEvent(self, mouseEvent):
        # put the observations within tolerance in the rubber band
        self.rubber.reset()
        for f in self.getFeatures(mouseEvent.pos()):
            self.rubber.addGeometry(f.geometry(), None)

    def canvasPressEvent(self, mouseEvent):
        self.rubber.reset()
        features = self.getFeatures(mouseEvent.pos())
        print len(features)
        if len(features) != 2:
            self.iface.messageBar().pushMessage("Intersect It",
                                                "You need exactly 2 features to proceed a simple intersection.",
                                                QgsMessageBar.WARNING, 3)
            return
        intersection = features[0].geometry().intersection(features[1].geometry()).asPoint()
        if intersection is None:
            return
        layer = self.checkLayer()
        if layer is None:
            return
        f = QgsFeature()
        initFields = layer.dataProvider().fields()
        f.setFields(initFields)
        f.initAttributes(initFields.size())
        f.setGeometry(QgsGeometry().fromPoint(intersection))
        layer.editBuffer().addFeature(f)
        layer.triggerRepaint()

    def getFeatures(self, pixPoint):
        # do the snapping
        snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        snapper.setSnapLayers(self.snapperList)
        snapper.setSnapMode(QgsSnapper.SnapWithResultsWithinTolerances)
        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        # output snapped features
        features = []
        alreadyGot = []
        for result in snappingResults:
            featureId = result.snappedAtGeometry
            f = QgsFeature()
            if (result.layer.id(), featureId) not in alreadyGot:
                if result.layer.getFeatures(QgsFeatureRequest().setFilterFid(featureId)).nextFeature(f) is False:
                    continue
                features.append(QgsFeature(f))
                alreadyGot.append((result.layer.id(), featureId))
        return features

    def checkLayer(self):
        # check output layer is defined
        layerid = self.settings.value("simpleIntersectionLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if not self.settings.value("simpleIntersectionWritePoint") or layer is None:
            self.iface.messageBar().pushMessage("Intersect It",
                                                "You must define an output layer for simple intersections",
                                                QgsMessageBar.WARNING, 3)
            self.mapCanvas.unsetMapTool(self)
            return None
        if not layer.isEditable():
            self.iface.messageBar().pushMessage("Intersect It",
                                                "The output layer <b>%s must be editable</b>" % layer.name(),
                                                QgsMessageBar.WARNING, 3)
            self.mapCanvas.unsetMapTool(self)
            return None
        return layer
