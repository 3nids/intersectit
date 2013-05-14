"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

mapTools
"""

from PyQt4.QtCore import Qt
from qgis.core import QgsGeometry, QgsPoint
from qgis.gui import QgsRubberBand, QgsMapToolEmitPoint, QgsMapCanvasSnapper

from ..core.mysettings import MySettings
from ..core.observation import Observation

from placedistancedialog import PlaceDistanceDialog


class PlaceObservationOnMap(QgsMapToolEmitPoint):
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
                radius    = dlg.distance.value()
                precision = dlg.precision.value()
                if radius == 0:
                    return
            else:
                return
        Observation(self.iface, self.obsType, mapPoint, radius, precision)

    def snapToLayers(self, pixPoint, dfltPoint=None):
        if not self.snapping:
            return None
        result, snappingResults = QgsMapCanvasSnapper(self.canvas).snapToBackgroundLayers(pixPoint, [])
        if result == 0 and len(snappingResults) > 0:
            return QgsPoint(snappingResults[0].snappedVertex)
        else:
            return dfltPoint
