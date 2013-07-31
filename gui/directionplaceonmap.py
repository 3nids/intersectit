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
from qgis.core import QGis, QgsMapLayer, QgsTolerance, QgsSnapper
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint

from ..core.observation import Direction
from ..core.mysettings import MySettings

from directiondialog import DirectionDialog


class DirectionOnMap(QgsMapToolEmitPoint):
    def __init__(self, iface):
        self.iface = iface
        self.settings = MySettings()
        self.canvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.canvas)
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def deactivate(self):
        self.rubber.reset()

    def canvasMoveEvent(self, mouseEvent):
        direction = self.getDirection(mouseEvent.pos())
        if direction is None:
            self.rubber.reset()
        else:
            self.rubber.setToGeometry(direction.geometry(), None)

    def canvasPressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            self.rubber.reset()
            return
        direction = self.getDirection(mouseEvent.pos())
        if direction is None:
            self.rubber.reset()
            return
        dlg = DirectionDialog(direction, self.rubber)
        if dlg.exec_():
            if direction.length != 0:
                print direction.precision
                direction.save()
        self.rubber.reset()

    def getDirection(self, pixPoint):
        snapperList = []
        for layer in self.iface.mapCanvas().layers():
            if layer.type() == QgsMapLayer.VectorLayer and layer.hasGeometryType():
                if layer.geometryType() in (QGis.Line, QGis.Polygon):
                    snapLayer = QgsSnapper.SnapLayer()
                    snapLayer.mLayer = layer
                    snapLayer.mSnapTo = QgsSnapper.SnapToSegment
                    snapLayer.mTolerance = 7
                    snapLayer.mUnitType = QgsTolerance.Pixels
                    snapperList.append(snapLayer)
        if len(snapperList) == 0:
            return None
        snapper = QgsSnapper(self.canvas.mapRenderer())
        snapper.setSnapLayers(snapperList)
        snapper.setSnapMode(QgsSnapper.SnapWithOneResult)

        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        if ok == 0:
            for result in snappingResults:
                vertices = (result.afterVertex, result.beforeVertex)
                po = result.snappedVertex
                dist = (po.sqrDist(vertices[0]), po.sqrDist(vertices[1]))
                mindist = min(dist)
                if mindist == 0:
                    return None
                i = dist.index(mindist)
                ve = vertices[i]
                az = po.azimuth(ve)
                return Direction(self.iface, ve, az)
        else:
            return None



