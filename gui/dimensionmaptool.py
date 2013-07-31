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
from qgis.core import QGis, QgsMapLayerRegistry, QgsTolerance, QgsSnapper
from qgis.gui import QgsRubberBand, QgsMapTool

from ..core.observation import Direction
from ..core.mysettings import MySettings

from directiondialog import DirectionDialog


class DimensionMapTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)

    def activate(self):
        layerid = MySettings().value("dimensionLayer")
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)

        snapLayer = QgsSnapper.SnapLayer()
        snapLayer.mLayer = layer
        snapLayer.mSnapTo = QgsSnapper.SnapToVertex
        snapLayer.mTolerance = 7
        snapLayer.mUnitType = QgsTolerance.Pixels

        QgsMapTool.activate(self)


    def canvasMoveEvent(self, e):
        pass

