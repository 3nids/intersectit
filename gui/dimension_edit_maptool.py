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

from qgis.core import QgsMapLayerRegistry, QgsTolerance, QgsPointLocator, QgsSnappingUtils, QgsFeature, QgsFeatureRequest
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMessageBar

from ..core.arc import Arc
from ..core.orientation_line import OrientationLine
from ..core.mysettings import MySettings


class DimensionEditMapTool(QgsMapTool):
    def __init__(self, iface, observationType):
        self.iface = iface
        QgsMapTool.__init__(self, iface.mapCanvas())
        self.observationType = observationType  # distance or orientation
        self.settings = MySettings()
        self.lineRubber = QgsRubberBand(self.canvas())
        self.editing = False
        self.layer = None
        self.observationType = self.observationType.lower().title()
        if self.observationType not in ("Orientation", "Distance"):
            raise NameError("Wrong observation type")

    def activate(self):
        QgsMapTool.activate(self)
        self.lineRubber.setWidth(self.settings.value("rubberWidth"))
        self.lineRubber.setColor(self.settings.value("rubberColor"))
        layer_id = self.settings.value("dimension"+self.observationType+"Layer")
        self.layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        if self.layer is None:
            self.iface.messageBar().pushMessage("Intersect It", "Dimension layer must defined.",
                                                QgsMessageBar.WARNING, 3)
            self.canvas().unsetMapTool(self)
            return
        if not self.layer.isEditable():
            self.iface.messageBar().pushMessage("Intersect It", "Dimension layer must be editable.",
                                                QgsMessageBar.WARNING, 3)
            self.canvas().unsetMapTool(self)
            return
        # unset this tool if the layer is removed
        self.layer.layerDeleted.connect(self.unsetMapTool)
        
        self.editing = False
        self.drawObject = None

    def unsetMapTool(self):
        self.canvas().unsetMapTool(self)

    def deactivate(self):
        self.lineRubber.reset()
        if self.layer is not None:
            try:
                self.layer.layerDeleted.disconnect(self.unsetMapTool)
            except TypeError:
                pass
        QgsMapTool.deactivate(self)

    def canvasPressEvent(self, mouseEvent):
        feature = self.snap_to_dimension_layer(mouseEvent.pos())
        if not feature.isValid():
            return
        line = feature.geometry().asPolyline()
        point = self.map2layer(mouseEvent.pos())
        if self.observationType == "Distance":
            if len(line) == 0:
                return
            self.editing = True
            self.drawObject = Arc(line[0], point, line[len(line)-1])
        else:
            if len(line) != 2:
                return
            self.editing = True
            self.drawObject = OrientationLine(line, point)
        self.featureId = feature.id()

    def canvasReleaseEvent(self, mouseEvent):
        if not self.editing:
            return
        self.editing = False
        self.lineRubber.reset()
        point = self.map2layer(mouseEvent.pos())
        if point is None:
            return
        self.drawObject.setPoint(point)
        geom = self.drawObject.geometry()

        editBuffer = self.layer.editBuffer()
        editBuffer.changeGeometry(self.featureId, geom)
        self.layer.triggerRepaint()

    def canvasMoveEvent(self, mouseEvent):
        if not self.editing:
            feature = self.snap_to_dimension_layer(mouseEvent.pos())
            if not feature.isValid():
                self.lineRubber.reset()
                return
            self.lineRubber.setToGeometry(feature.geometry(), self.layer)
        else:
            point = self.map2layer(mouseEvent.pos())
            if point is None:
                return
            self.drawObject.setPoint(point)
            self.lineRubber.setToGeometry(self.drawObject.geometry(), self.layer)

    def map2layer(self, pos):
        point = self.toMapCoordinates(pos)
        return self.canvas().mapRenderer().mapToLayerCoordinates(self.layer, point)

    def snap_to_dimension_layer(self, pos):
        """ Temporarily override snapping config and snap to vertices and edges
            of any editable vector layer, to allow selection of node for editing
            (if snapped to edge, it would offer creation of a new vertex there).
           """
        map_point = self.toMapCoordinates(pos)
        tol = QgsTolerance.vertexSearchRadius(self.canvas().mapSettings())
        snap_type = QgsPointLocator.Type(QgsPointLocator.Edge)

        snap_layers = [QgsSnappingUtils.LayerConfig(self.layer, snap_type, tol, QgsTolerance.ProjectUnits)]

        snap_util = self.canvas().snappingUtils()
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

        f = QgsFeature()
        if m.featureId() is not None:
            self.layer.getFeatures(QgsFeatureRequest().setFilterFid(m.featureId())).nextFeature(f)
        return f
