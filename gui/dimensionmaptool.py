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
from qgis.core import QGis, QgsMapLayerRegistry, QgsTolerance, QgsSnapper, QgsFeature, QgsFeatureRequest
from qgis.gui import QgsRubberBand, QgsMapTool

from ..core.arc import Arc
from ..core.mysettings import MySettings




class DimensionMapTool(QgsMapTool):
    def __init__(self, canvas):
        self.mapCanvas = canvas
        QgsMapTool.__init__(self, canvas)

    def activate(self):
        layerid = MySettings().value("dimensionLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        self.snapLayer = QgsSnapper.SnapLayer()
        self.snapLayer.mLayer = layer
        self.snapLayer.mSnapTo = QgsSnapper.SnapToVertex
        self.snapLayer.mTolerance = 7
        self.snapLayer.mUnitType = QgsTolerance.Pixels
        self.rubber = QgsRubberBand(self.mapCanvas)
        QgsMapTool.activate(self)

    def canvasMoveEvent(self, mouseEvent):
        featureId = self.snapToDimension(mouseEvent.pos())
        if featureId is None:
            self.rubber.reset()
            return
        f = QgsFeature()
        if self.snapLayer.mLayer.getFeatures(QgsFeatureRequest().setFilterFid(featureId).setFlags(QgsFeatureRequest.NoGeometry)).nextFeature(f) is False:
            self.rubber.reset()
            return
        print 123
        self.rubber.setToGeometry(f.geometry(), self.snapLayer.mLayer)

    def snapToDimension(self, pixPoint):
        snapper = QgsSnapper(self.mapCanvas.mapRenderer())
        snapper.setSnapLayers([self.snapLayer])
        snapper.setSnapMode(QgsSnapper.SnapWithOneResult)

        ok, snappingResults = snapper.snapPoint(pixPoint, [])
        if ok == 0 and len(snappingResults) > 0:
            return snappingResults[0].snappedAtGeometry
        else:
            return None
