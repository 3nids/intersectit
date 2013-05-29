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

from PyQt4.QtCore import QVariant
from qgis.core import QgsPoint, QgsGeometry, QgsFeature

import math
from datetime import datetime
from memorylayers import MemoryLayers


class Observation():
    def __init__(self, iface, obsType, point, observation, precision):
        memoryLayers = MemoryLayers(iface)
        lineLayer = memoryLayers.lineLayer()
        pointLayer = memoryLayers.pointLayer()

        # generate ID
        id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        # obsservations are stored in the lineLayer layer attributes:
        #   0: id
        #   1: observation type
        #   2: x
        #   3: y
        #   4: observation
        #   5: precision

        # save info in feature
        f = QgsFeature()
        # todo: check this
        f.setAttributes([QVariant(id),
                         QVariant(obsType),
                         QVariant(point.x()),
                         QVariant(point.y()),
                         QVariant(observation),
                         QVariant(precision)])

        # draw observation
        if obsType == "distance":
            # trace circle at distance from point
            geom = QgsGeometry.fromPolyline([QgsPoint(point.x()+observation*math.cos(math.pi/180*a),point.y()+observation*math.sin(math.pi/180*a)) for a in range(0,361,3)])
        f.setGeometry(geom)
        lineLayer.dataProvider().addFeatures([f])
        lineLayer.updateExtents()
        lineLayer.setCacheImage(None)

        # draw center
        f = QgsFeature()
        f.setAttributes([QVariant(id)])
        f.setGeometry(QgsGeometry.fromPoint(point))
        pointLayer.dataProvider().addFeatures([f])
        pointLayer.updateExtents()
        pointLayer.setCacheImage(None)


#     def delete(self):
#          self.pointLayer().dataProvider().deleteFeatures([self.point_id])
#          self.lineLayer().dataProvider().deleteFeatures([self.line_id])
#          self.canvas.refresh()
          
          
