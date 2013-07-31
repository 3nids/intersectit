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
from PyQt4.QtGui import QTextEdit
from qgis.core import QGis, QgsGeometry, QgsPoint, QgsMapLayer, QgsTolerance, QgsSnapper
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapCanvasSnapper

from ..core.mysettings import MySettings
from ..core.observation import Distance

from distancedialog import DistanceDialog


class DistanceOnMap(QgsMapToolEmitPoint):
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.canvas)
        self.rubber.setIconSize(8)
        self.snapping = MySettings().value("obsDistanceSnapping")
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.snapperList = []
        if self.snapping == "all":
            for layer in self.iface.mapCanvas().layers():
                if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType():
                    snapLayer = QgsSnapper.SnapLayer()
                    snapLayer.mLayer = layer
                    snapLayer.mSnapTo = QgsSnapper.SnapToVertex
                    snapLayer.mTolerance = 7
                    snapLayer.mUnitType = QgsTolerance.Pixels
                    self.snapperList.append(snapLayer)

        self.messageWidget = self.iface.messageBar().createMessage("Not snapped.")
        self.messageWidgetExist = True
        self.messageWidget.destroyed.connect(self.messageWidgetRemoved)
        if self.snapping != "no":
            self.iface.messageBar().pushWidget(self.messageWidget)

    def deactivate(self):
        self.iface.messageBar().popWidget(self.messageWidget)
        self.rubber.reset()

    def messageWidgetRemoved(self):
        self.messageWidgetExist = False

    def displaySnapInfo(self, snappingResults):
        if not self.messageWidgetExist:
            return
        nSnappingResults = len(snappingResults)
        if nSnappingResults == 0:
            message = "No snap"
        else:
            message = "<b>Snapped to: %s" % snappingResults[0].layer.name() + "</b>"
            if nSnappingResults > 1:
                message += "<br>Other layers: "
                for res in snappingResults[1:]:
                    message += res.layer.name() + ", "
                message = message[:-2]
        messageTextEdit = self.messageWidget.findChild(QTextEdit, "mMsgText")
        if messageTextEdit is not None:
            messageTextEdit.setText(message)

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
        dlg = DistanceDialog(distance, self.canvas)
        if dlg.exec_():
            distance.save()
        self.rubber.reset()

    def snapToLayers(self, pixPoint, initPoint=None):
        if self.snapping == "no":
            return initPoint

        if self.snapping == "project":
            ok, snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint, [])
            self.displaySnapInfo(snappingResults)
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
            self.displaySnapInfo(snappingResults)
            if ok == 0 and len(snappingResults) > 0:
                return QgsPoint(snappingResults[0].snappedVertex)
            else:
                return initPoint
