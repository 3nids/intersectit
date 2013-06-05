#-----------------------------------------------------------
#
# Intersect It is a QGIS plugin to place measures (distance or orientation)
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
from qgis.core import QgsGeometry, QgsPoint
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapCanvasSnapper

from ..core.mysettings import MySettings
from ..core.observation import Observation

from placedistancedialog import PlaceDistanceDialog


class PlaceDistanceOnMap(QgsMapToolEmitPoint):
    def __init__(self, iface, obsType):
        self.iface = iface
        self.obsType = obsType
        self.canvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.canvas)
        self.snapping = MySettings().value("obsSnapping")
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasMoveEvent(self, mouseEvent):
        if self.snapping:
            snappedPoint = self.snapToLayers(mouseEvent.pos())
            if snappedPoint is None:
                self.rubber.reset()
            else:
                self.rubber.setToGeometry(QgsGeometry.fromPoint(snappedPoint), None)

    def canvasPressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            return
        self.rubber.reset()
        pixPoint = mouseEvent.pos()
        mapPoint = self.toMapCoordinates(pixPoint)
        #snap to layers
        if self.snapping:
            mapPoint = self.snapToLayers(pixPoint, mapPoint)
        if self.obsType == "distance":
            # creates ditance with dialog
            dlg = PlaceDistanceDialog(mapPoint)
            if dlg.exec_():
                radius = dlg.distance.value()
                precision = dlg.precision.value()
                if radius == 0:
                    return
            else:
                return
        Observation(self.iface, self.obsType, mapPoint, radius, precision)
        self.iface.mapCanvas().refresh()

    def snapToLayers(self, pixPoint, dfltPoint=None):
        if not self.snapping:
            return None
        result, snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint, [])
        if result == 0 and len(snappingResults) > 0:
            return QgsPoint(snappingResults[0].snappedVertex)
        else:
            return dfltPoint
