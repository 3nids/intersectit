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

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QMessageBox
from qgis.core import QgsFeatureRequest, QgsFeature, QgsGeometry, QgsMapLayerRegistry, QgsPoint, QgsTolerance, QgsSnapper, QgsSnappingUtils, QgsPointLocator
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMessageBar

from ..core.mysettings import MySettings
from ..core.memory_layers import MemoryLayers
from ..core.arc import Arc

from my_settings_dialog import MySettingsDialog
from intersection_dialog import IntersectionDialog


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
        line_layer = MemoryLayers(self.iface).line_layer()
        # unset this tool if the layer is removed
        line_layer.layerDeleted.connect(self.unsetMapTool)
        self.layerId = line_layer.id()
        # create snapper for this layer
        self.snapLayer = QgsSnapper.SnapLayer()
        self.snapLayer.mLayer = line_layer
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
        line_layer = QgsMapLayerRegistry.instance().mapLayer(self.layerId)
        if line_layer is not None:
            line_layer.layerDeleted.disconnect(self.unsetMapTool)
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
        self.doIntersection(point, observations)

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
            f = QgsFeature()
            if featureId not in alreadyGot:
                if result.layer.getFeatures(QgsFeatureRequest().setFilterFid(featureId)).nextFeature(f) is not False:
                    features.append(QgsFeature(f))
                    alreadyGot.append(featureId)
        return features

    def doIntersection(self, initPoint, observations):
        nObs = len(observations)
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
            message = QCoreApplication.translate("IntersectIt",
                                                 "To place the intersection solution,"
                                                 " you must select a layer in the settings.")
            status, intLayer = self.checkLayerExists(layerid, message)
            if status == 2:
                continue
            if status == 3:
                return
            if self.settings.value("advancedIntersectionWriteReport"):
                reportField = self.settings.value("reportField")
                message = QCoreApplication.translate("IntersectIt",
                                                     "To save the intersection report, please select a field for it.")
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
        if not self.settings.value("dimensionDistanceWrite") and not self.settings.value("dimensionOrientationWrite"):
            return  # if we do not place any dimension, skip
        obsTypes = ("Distance", "Orientation")
        recheck = True
        while recheck:
            # settings might change during checking,
            # so recheck both observation types whenever the settings dialog is shown
            recheck = False
            for obsType in obsTypes:
                while True:
                    if not self.settings.value("dimension"+obsType+"Write"):
                        break
                    # check layer
                    layerId = self.settings.value("dimension"+obsType+"Layer")
                    message = QCoreApplication.translate("IntersectIt",
                                                         "To place dimensions, "
                                                         "you must define a layer in the settings.")
                    status, dimLayer = self.checkLayerExists(layerId, message)
                    if status == 2:
                        recheck = True
                        continue
                    if status == 3:
                        return
                    # check fields
                    if self.settings.value("dimension"+obsType+"ObservationWrite"):
                        obsField = self.settings.value("dimension"+obsType+"ObservationField")
                        message = QCoreApplication.translate("IntersectIt",
                                                             "To save the observation in the layer,"
                                                             " please select a field for it.")
                        status = self.checkFieldExists(dimLayer, obsField, message)
                        if status == 2:
                            recheck = True
                            continue
                        if status == 3:
                            return
                    if self.settings.value("dimension"+obsType+"PrecisionWrite"):
                        precisionField = self.settings.value("dimension"+obsType+"PrecisionField")
                        message = QCoreApplication.translate("IntersectIt",
                                                             "To save the precision of observation,"
                                                             " please select a field for it.")
                        status = self.checkFieldExists(dimLayer, precisionField, message)
                        if status == 2:
                            recheck = True
                            continue
                        if status == 3:
                            return
                    break
        # save the intersection results
        for obsType in obsTypes:
            if self.settings.value("dimension"+obsType+"Write"):
                layerid = self.settings.value("dimension"+obsType+"Layer")
                layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
                if layer is None:
                    continue
                initFields = layer.dataProvider().fields()
                features = []
                for obs in observations:
                    if obs["type"] != obsType.lower():
                        continue
                    f = QgsFeature()
                    f.setFields(initFields)
                    f.initAttributes(initFields.size())
                    if self.settings.value("dimension"+obsType+"ObservationWrite"):
                        f[self.settings.value("dimension"+obsType+"ObservationField")] = obs["observation"]
                    if self.settings.value("dimension"+obsType+"PrecisionWrite"):
                        f[self.settings.value("dimension"+obsType+"PrecisionField")] = obs["precision"]
                    p0 = QgsPoint(obs["x"], obs["y"])
                    p1 = intersectedPoint
                    if obs["type"] == "distance":
                        geom = Arc(p0, p1).geometry()
                    elif obs["type"] == "orientation":
                        geom = QgsGeometry().fromPolyline([p0, p1])
                    else:
                        raise NameError("Invalid observation %s" % obs["type"])
                    f.setGeometry(geom)
                    features.append(QgsFeature(f))
                if not layer.dataProvider().addFeatures(features):
                    self.iface.messageBar().pushMessage("Could not commit %s observations" % obsType,
                                                        QgsMessageBar.CRITICAL)
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

        reply = QMessageBox.question(self.iface.mainWindow(), "Intersect It",
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

        reply = QMessageBox.question(self.iface.mainWindow(), "Intersect It",
                                     message + " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if MySettingsDialog().exec_():
                return 2
        return 3
