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

from qgis.core import QgsPoint, QgsGeometry, QgsFeature

from math import cos, sin, pi
from datetime import datetime

from memorylayers import MemoryLayers
from mysettings import MySettings


class Observation():
    def __init__(self, iface, obsType, point, observation, precision):
        memoryLayers = MemoryLayers(iface)
        self.lineLayer = memoryLayers.lineLayer()
        self.pointLayer = memoryLayers.pointLayer()
        self.settings = MySettings()

        # generate ID;
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        # obsservations are stored in the lineLayer layer attributes:
        #   0: id
        #   1: observation type
        #   2: x
        #   3: y
        #   4: observation
        #   5: precision

        self.obsType = obsType
        self.point = point
        self.observation = observation
        self.precision = precision

        print "kkkk", self.point.x()

    def geometry(self):
        if self.obsType == "distance":
            # trace circle at distance from point
            return QgsGeometry().fromPolyline([QgsPoint(self.point.x() + self.observation * cos(pi/180*a),
                                                        self.point.y() + self.observation * sin(pi/180*a))
                                               for a in range(0, 361, 3)])
        elif self.obsType == "prolongation":
            length = self.settings.value("obsProlongationLength")
            x = self.point.x() + length * cos((90-self.observation)*pi/180)
            y = self.point.y() + length * sin((90-self.observation)*pi/180)
            print "lol", x, y, self.point.x(), self.point.y()
            return QgsGeometry().fromPolyline([self.point, QgsPoint(x, y)])
        raise NameError("Unknown observation type")

    def save(self):
        # save info in feature
        f = QgsFeature()
        fields = self.lineLayer.dataProvider().fields()
        f.setFields(fields)
        f["id"] = self.id
        f["type"] = self.obsType
        f["x"] = self.point.x()
        f["y"] = self.point.y()
        f["observation"] = self.observation
        f["precision"] = self.precision
        f.setGeometry(self.geometry())
        self.lineLayer.dataProvider().addFeatures([f])
        self.lineLayer.updateExtents()
        self.lineLayer.setCacheImage(None)

        # draw center
        f = QgsFeature()
        f["id"] = self.id
        f.setGeometry(QgsGeometry().fromPoint(self.point))
        self.pointLayer.dataProvider().addFeatures([f])
        self.pointLayer.updateExtents()
        self.pointLayer.setCacheImage(None)


#     def delete(self):
#          self.pointLayer().dataProvider().deleteFeatures([self.point_id])
#          self.lineLayer().dataProvider().deleteFeatures([self.line_id])
#          self.canvas.refresh()
