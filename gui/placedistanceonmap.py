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

from PyQt4.QtCore import Qt
from qgis.core import QGis, QgsGeometry, QgsPoint, QgsMapLayer, QgsTolerance, QgsSnapper
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapCanvasSnapper

from ..core.mysettings import MySettings
from ..core.observation import Distance

from placedistancedialog import PlaceDistanceDialog


class PlaceDistanceOnMap(QgsMapToolEmitPoint):
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.canvas)
        self.rubber.setIconSize(8)
        self.snapping = MySettings().value("obsDistanceSnapping")
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.snapperList = []
        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType():
                snapLayer = QgsSnapper.SnapLayer()
                snapLayer.mLayer = layer
                snapLayer.mSnapTo = QgsSnapper.SnapToVertex
                snapLayer.mTolerance = 7
                snapLayer.mUnitType = QgsTolerance.Pixels
                self.snapperList.append(snapLayer)

    def canvasMoveEvent(self, mouseEvent):
        if self.snapping:
            snappedPoint = self.snapToLayers(mouseEvent.pos())
            if snappedPoint is None:
                self.rubber.reset()
            else:
                self.rubber.setToGeometry(QgsGeometry().fromPoint(snappedPoint), None)

    def canvasPressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            return
        pixPoint = mouseEvent.pos()
        mapPoint = self.toMapCoordinates(pixPoint)
        #snap to layers
        mapPoint = self.snapToLayers(pixPoint, mapPoint)
        self.rubber.setToGeometry(QgsGeometry().fromPoint(mapPoint), None)
        distance = Distance(self.iface, mapPoint, 1)
        dlg = PlaceDistanceDialog(distance, self.canvas)
        if dlg.exec_():
            distance.save()
        self.rubber.reset()

    def snapToLayers(self, pixPoint, initPoint=None):
        if self.snapping == "no":
            return initPoint

        if self.snapping == "project":
            ok, snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint, [])
            if ok == 0 and len(snappingResults) > 0:
                return QgsPoint(snappingResults[0].snappedVertex)
            else:
                return initPoint

        if self.snapping == "all":
            if len(self.snapperList) == 0:
                return initPoint
            snapper = QgsSnapper(self.canvas.mapRenderer())
            snapper.setSnapLayers(self.snapperList)
            snapper.setSnapMode(QgsSnapper.SnapWithOneResult)

            ok, snappingResults = snapper.snapPoint(pixPoint, [])
            if ok == 0 and len(snappingResults) > 0:
                return QgsPoint(snappingResults[0].snappedVertex)
            else:
                return initPoint
