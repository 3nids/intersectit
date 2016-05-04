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
from qgis.core import QGis, QgsGeometry, QgsPoint, QgsTolerance, QgsPointLocator, QgsVectorLayer, QgsSnappingUtils
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMapCanvasSnapper, QgsMessageBar

from ..core.mysettings import MySettings
from ..core.distance import Distance
from ..core.memory_layers import MemoryLayers

from distance_dialog import DistanceDialog


class DistanceMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.line_layer = None
        self.settings = MySettings()
        QgsMapTool.__init__(self, iface.mapCanvas())

    def activate(self):
        QgsMapTool.activate(self)
        self.line_layer = MemoryLayers(self.iface).line_layer
        self.rubber = QgsRubberBand(self.canvas(), QGis.Point)
        self.rubber.setColor(self.settings.value("rubberColor"))
        self.rubber.setIcon(self.settings.value("rubberIcon"))
        self.rubber.setIconSize(self.settings.value("rubberSize"))
        self.messageWidget = self.iface.messageBar().createMessage("Intersect It", "Not snapped.")
        self.messageWidgetExist = True
        self.messageWidget.destroyed.connect(self.messageWidgetRemoved)

    def deactivate(self):
        self.iface.messageBar().popWidget(self.messageWidget)
        self.rubber.reset()
        QgsMapTool.deactivate(self)

    def messageWidgetRemoved(self):
        self.messageWidgetExist = False

    def displaySnapInfo(self, match=None):
        if not self.messageWidgetExist:
            return
        if match is None:
            message = "No snap"
        else:
            message = 'Snapped to: <b>{}</b>'.format(match.layer())
        self.messageWidget.setText(message)

    def canvasMoveEvent(self, mouseEvent):
        match = self.snap_to_vertex(mouseEvent.pos())
        self.rubber.reset(QGis.Point)
        if match.type() == QgsPointLocator.Vertex and match.layer() != self.line_layer:
            self.rubber.addPoint(match.point())
        self.displaySnapInfo(match)

    def canvasPressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            return
        match = self.snap_to_vertex(mouseEvent.pos())
        if match.type() != QgsPointLocator.Vertex and match.layer() != self.line_layer:
            point = self.toMapCoordinates(mouseEvent.pos())
        else:
            point = match.point()
        self.rubber.addPoint(point)
        distance = Distance(self.iface, point, 1)
        dlg = DistanceDialog(distance, self.canvas())
        if dlg.exec_():
            distance.save()
        self.rubber.reset()

    def snap_to_vertex(self, pos):
        """ Temporarily override snapping config and snap to vertices and edges
         of any editable vector layer, to allow selection of node for editing
         (if snapped to edge, it would offer creation of a new vertex there).
        """
        map_point = self.toMapCoordinates(pos)
        tol = QgsTolerance.vertexSearchRadius(self.canvas().mapSettings())
        snap_type = QgsPointLocator.Type(QgsPointLocator.Vertex)

        snap_layers = []
        for layer in self.canvas().layers():
            if not isinstance(layer, QgsVectorLayer):
                continue
            snap_layers.append(QgsSnappingUtils.LayerConfig(
                layer, snap_type, tol, QgsTolerance.ProjectUnits))

        snap_util = self.canvas().snappingUtils()
        old_layers = snap_util.layers()
        old_mode = snap_util.snapToMapMode()
        old_inter = snap_util.snapOnIntersections()
        snap_util.setLayers(snap_layers)
        snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
        snap_util.setSnapOnIntersections(True)
        m = snap_util.snapToMap(map_point)
        snap_util.setLayers(old_layers)
        snap_util.setSnapToMapMode(old_mode)
        snap_util.setSnapOnIntersections(old_inter)
        return m

