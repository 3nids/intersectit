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

from qgis.core import QGis, QgsFeature, QgsGeometry, QgsMapLayerRegistry, QgsTolerance, QgsPointLocator, QgsVectorLayer, QgsSnappingUtils
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMessageBar

from ..core.mysettings import MySettings


class SimpleIntersectionMapTool(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        QgsMapTool.__init__(self, self.mapCanvas)
        self.settings = MySettings()
        self.rubber = QgsRubberBand(self.mapCanvas, QGis.Point)

    def deactivate(self):
        self.rubber.reset()
        QgsMapTool.deactivate(self)

    def activate(self):
        QgsMapTool.activate(self)
        self.rubber.setWidth(self.settings.value("rubberWidth"))
        self.rubber.setColor(self.settings.value("rubberColor"))
        self.checkLayer()

    def canvasMoveEvent(self, mouseEvent):
        # put the observations within tolerance in the rubber band
        self.rubber.reset(QGis.Point)
        match = self.snap_to_intersection(mouseEvent.pos())
        if match.type() == QgsPointLocator.Vertex and match.layer() is None:
            self.rubber.addPoint(match.point())

    def canvasPressEvent(self, mouseEvent):
        self.rubber.reset()
        match = self.snap_to_intersection(mouseEvent.pos())
        if match.type() != QgsPointLocator.Vertex or match.layer() is not None:
            return

        layer = self.checkLayer()
        if layer is None:
            return
        f = QgsFeature()
        initFields = layer.dataProvider().fields()
        f.setFields(initFields)
        f.initAttributes(initFields.size())
        f.setGeometry(QgsGeometry().fromPoint(match.point()))
        layer.editBuffer().addFeature(f)
        layer.triggerRepaint()

    def snap_to_intersection(self, pos):
        """ Temporarily override snapping config and snap to vertices and edges
         of any editable vector layer, to allow selection of node for editing
         (if snapped to edge, it would offer creation of a new vertex there).
        """
        map_point = self.toMapCoordinates(pos)
        tol = QgsTolerance.vertexSearchRadius(self.canvas().mapSettings())
        snap_type = QgsPointLocator.Type(QgsPointLocator.Edge)

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
