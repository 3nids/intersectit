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
from qgis.core import QGis, QgsTolerance, QgsPointLocator, QgsSnappingUtils, QgsVectorLayer
from qgis.gui import QgsRubberBand, QgsMapTool

from ..core.orientation import Orientation
from ..core.mysettings import MySettings

from orientation_dialog import OrientationDialog


class OrientationMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.settings = MySettings()
        self.canvas = iface.mapCanvas()
        self.rubber = QgsRubberBand(self.canvas)
        QgsMapTool.__init__(self, self.canvas)

    def activate(self):
        QgsMapTool.activate(self)
        self.rubber.setWidth(self.settings.value("rubberWidth"))
        self.rubber.setColor(self.settings.value("rubberColor"))

    def deactivate(self):
        self.rubber.reset()
        QgsMapTool.deactivate(self)

    def canvasMoveEvent(self, mouseEvent):
        ori = self.get_orientation(mouseEvent.pos())
        if ori is None:
            self.rubber.reset()
        else:
            self.rubber.setToGeometry(ori.geometry(), None)

    def canvasPressEvent(self, mouseEvent):
        if mouseEvent.button() != Qt.LeftButton:
            self.rubber.reset()
            return
        ori = self.get_orientation(mouseEvent.pos())
        if ori is None:
            self.rubber.reset()
            return
        dlg = OrientationDialog(ori, self.rubber)
        if dlg.exec_():
            if ori.length != 0:
                ori.save()
        self.rubber.reset()

    def get_orientation(self, pos):
        match = self.snap_to_segment(pos)
        if not match.hasEdge():
            return None
        vertices = match.edgePoints()
        po = match.point()
        dist = (po.sqrDist(vertices[0]), po.sqrDist(vertices[1]))
        mindist = min(dist)
        if mindist == 0:
            return None
        i = dist.index(mindist)
        ve = vertices[i]
        az = po.azimuth(ve)
        return Orientation(self.iface, ve, az)

    def snap_to_segment(self, pos):
        """ Temporarily override snapping config and snap to vertices and edges
         of any editable vector layer, to allow selection of node for editing
         (if snapped to edge, it would offer creation of a new vertex there).
        """
        map_point = self.toMapCoordinates(pos)
        tol = QgsTolerance.vertexSearchRadius(self.canvas.mapSettings())
        snap_type = QgsPointLocator.Type(QgsPointLocator.Edge)

        snap_layers = []
        for layer in self.canvas.layers():
            if not isinstance(layer, QgsVectorLayer):
                continue
            snap_layers.append(QgsSnappingUtils.LayerConfig(
                layer, snap_type, tol, QgsTolerance.ProjectUnits))

        snap_util = self.canvas.snappingUtils()
        old_layers = snap_util.layers()
        old_mode = snap_util.snapToMapMode()
        old_inter = snap_util.snapOnIntersections()
        snap_util.setLayers(snap_layers)
        snap_util.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
        snap_util.setSnapOnIntersections(False)
        m = snap_util.snapToMap(map_point)
        snap_util.setLayers(old_layers)
        snap_util.setSnapToMapMode(old_mode)
        snap_util.setSnapOnIntersections(old_inter)
        return m



