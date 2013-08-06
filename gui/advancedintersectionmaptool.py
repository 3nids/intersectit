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
from qgis.core import QgsFeatureRequest, QgsFeature, QgsGeometry, QgsMapLayerRegistry, QgsPoint, QgsSnapper, QgsTolerance
from qgis.gui import QgsMapTool, QgsRubberBand

from ..core.mysettings import MySettings
from ..core.memorylayers import MemoryLayers
from ..core.arc import Arc

from mysettingsdialog import MySettingsDialog
from intersectiondialog import IntersectionDialog


class AdvancedIntersectionMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        QgsMapTool.__init__(self, self.mapCanvas)
        self.settings = MySettings()
        self.rubber = QgsRubberBand(self.mapCanvas)

        self.tolerance = self.settings.value("selectTolerance")
        units = self.settings.value("selectUnits")
        if units == "pixels":
            self.tolerance *= self.mapCanvas.mapUnitsPerPixel()

    def activate(self):
        QgsMapTool.activate(self)
        self.rubber.setWidth(self.settings.value("rubberWidth"))
        self.rubber.setColor(self.settings.value("rubberColor"))
        lineLayer = MemoryLayers(self.iface).lineLayer()
        # unset this tool if the layer is removed
        lineLayer.layerDeleted.connect(self.unsetMapTool)
        self.layerId = lineLayer.id()
        # create snapper for this layer
        self.snapLayer = QgsSnapper.SnapLayer()
        self.snapLayer.mLayer = lineLayer
        self.snapLayer.mSnapTo = QgsSnapper.SnapToVertexAndSegment
        self.snapLayer.mTolerance = self.settings.value("selectTolerance")
        if self.settings.value("selectUnits") == "map":
            self.snapLayer.mUnitType = QgsTolerance.MapUnits
        else:
            self.snapLayer.mUnitType = QgsTolerance.Pixels

    def unsetMapTool(self):
        self.mapCanvas.unsetMapTool(self)

    def deactivate(self):
        self.rubber.reset()
        lineLayer = QgsMapLayerRegistry.instance().mapLayer(self.layerId)
        if lineLayer is not None:
            lineLayer.layerDeleted.disconnect(self.unsetMapTool)
        QgsMapTool.deactivate(self)

    def canvasMoveEvent(self, mouseEvent):
        # put the observations within tolerance in the rubber band
        self.rubber.reset()
        for f in self.getFeatures(mouseEvent.pos()):
            self.rubber.addGeometry(f.geometry(), None)

    def canvasPressEvent(self, mouseEvent):
        pos = mouseEvent.pos()
        observations = self.getFeatures(pos)
        point = self.toMapCoordinates(pos)
        #self.doIntersection(point, observations)

    def getFeatures(self, pixPoint):
        snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        snapper.setSnapLayers([self.snapLayer])
        snapper.setSnapMode(QgsSnapper.SnapWithResultsWithinTolerances)
        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        # output snapped features
        features = []
        alreadyGot = []
        for result in snappingResults:
            featureId = result.snappedAtGeometry
            print featureId
            print type(featureId)
            print result.layer.name()
            f = QgsFeature()
            if featureId not in alreadyGot:
                if result.layer.getFeatures(QgsFeatureRequest().setFilterFid(featureId)).nextFeature(f) is not False:
                    print f["precision"]
                    features.append(QgsFeature(f))
                    alreadyGot.append(featureId)
        return features

    def doIntersection(self, initPoint, observations):
        nObs = len(observations)
        # for o in observations:
        #     print o
        #     for a in o.attributes():
        #         print a
        #     print o["type"]
        if nObs < 2:
            return
        self.rubber.reset()
        self.dlg = IntersectionDialog(self.iface, observations, initPoint)
        if not self.dlg.exec_() or self.dlg.solution is None:
            return
        intersectedPoint = self.dlg.solution
        self.saveIntersectionResult(self.dlg.report, intersectedPoint)
        self.saveDimension(intersectedPoint, self.dlg.observations)

    def saveIntersectionResult(self, report, intersectedPoint):
        # save the intersection result (point) and its report
        # check first
        while True:
            if not self.settings.value("advancedIntersectionWritePoint"):
                break  # if we do not place any point, skip
            layerid = self.settings.value("advancedIntersectionLayer")
            message = "To place the intersection solution, you must select a layer in the settings."
            status, intLayer = self.checkLayerExists(layerid, message)
            if status == 2:
                continue
            if status == 3:
                return
            if self.settings.value("advancedIntersectionWriteReport"):
                reportField = self.settings.value("reportField")
                message = "To save the intersection report, please select a field for it."
                status = self.checkFieldExists(intLayer, reportField, message)
                if status == 2:
                    continue
                if status == 3:
                    return
            break
        # save the intersection results
        if self.settings.value("advancedIntersectionWritePoint"):
            f = QgsFeature()
            f.setGeometry(QgsGeometry().fromPoint(intersectedPoint))
            if self.settings.value("advancedIntersectionWriteReport"):
                irep = intLayer.dataProvider().fieldNameIndex(reportField)
                f.addAttribute(irep, report)
            intLayer.dataProvider().addFeatures([f])
            intLayer.updateExtents()
            self.mapCanvas.refresh()

    def saveDimension(self, intersectedPoint, observations):
         # check that dimension layer and fields have been set correctly
        while True:
            # check layer
            if not self.settings.value("dimenPlaceDimension"):
                return  # if we do not place any dimension, skip
            dimensionLayerId = self.settings.value("dimensionLayer")
            message = "To place dimension arcs, you must select a layer in the settings."
            status, dimLayer = self.checkLayerExists(dimensionLayerId, message)
            if status == 2:
                continue
            if status == 3:
                return
            # check fields
            if self.settings.value("dimenPlaceMeasure"):
                measureField = self.settings.value("observationField")
                message = "To save the observed distance, please select a field for it."
                status = self.checkFieldExists(dimLayer, measureField, message)
                if status == 2:
                    continue
                if status == 3:
                    return
            if self.settings.value("dimenPlaceType"):
                typeField = self.settings.value("typeField")
                message = "To save the type of observaton, please select a field for it."
                status = self.checkFieldExists(dimLayer, typeField, message)
                if status == 2:
                    continue
                if status == 3:
                    return
            if self.settings.value("dimenPlacePrecision"):
                precisionField = self.settings.value("precisionField")
                message = "To save the precision of observation, please select a field for it."
                status = self.checkFieldExists(dimLayer, precisionField, message)
                if status == 2:
                    continue
                if status == 3:
                    return
            break
        # save the intersection results
        if self.settings.value("dimenPlaceDimension"):
            layer = QgsMapLayerRegistry.instance().mapLayer(dimensionLayerId)
            initFields = layer.dataProvider().fields()
            features = []
            for obs in observations:
                f = QgsFeature()
                f.setFields(initFields)
                f.initAttributes(initFields.size())
                if self.settings.value("dimenPlaceMeasure"):
                    f[self.settings.value("observationField")] = obs["observation"]
                if self.settings.value("dimenPlaceType"):
                    f[self.settings.value("typeField")] = obs["type"]
                if self.settings.value("dimenPlacePrecision"):
                    f[self.settings.value("precisionField")] = obs["precision"]
                p0 = QgsPoint(obs["x"], obs["y"])
                p1 = intersectedPoint
                if obs["type"] == "distance":
                    geom = Arc(p0, p1).geometry()
                elif obs["type"] == "orientation":
                    geom = QgsGeometry().fromPolyline([p0, p1])
                else:
                    raise NameError("Invalid observation %s" % obs["type"])
                f.setGeometry(geom)
                features.append(f)
            print layer.id()
            print features
            print layer.dataProvider().addFeatures(features)
            layer.updateExtents()
            self.mapCanvas.refresh()

    def checkLayerExists(self, layerid, message):
        # returns:
        # 1: layer exists
        # 2: does not exist, settings has been open, so loop once more (i.e. continue)
        # 3: does not exist, settings not edited, so cancel
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        if layer is not None:
            return 1, layer

        reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                     message + " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if MySettingsDialog().exec_():
                return 2
        return 3

    def checkFieldExists(self, layer, field, message):
        # returns:
        # 1: field exists
        # 2: does not exist, settings has been open, so loop once more (i.e. continue)
        # 3: does not exist, settings not edited, so cancel
        if layer.dataProvider().fieldNameIndex(field) != -1:
            return 1

        reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                     message + " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if MySettingsDialog().exec_():
                return 2
        return 3
