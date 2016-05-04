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

from qgis.core import QgsPoint, QgsGeometry
from math import pi, cos, sin, sqrt


class OrientationLine():
    def __init__(self, line, point):
        if len(line) != 2:
            raise NameError("line must be a vector of 2 QgsPoint")
        self.orientation = line[0].azimuth(line[1]) * pi/180
        self.origin = line[0]
        self.point = point

    def setPoint(self, point):
        self.point = point

    def geometry(self):
        a = -self.orientation + pi/180*self.origin.azimuth(self.point)
        d = sqrt(self.origin.sqrDist(self.point)) * cos(a)
        if d == 0:
            d = 1
        P = QgsPoint(self.origin.x() + d * sin(self.orientation),
                     self.origin.y() + d * cos(self.orientation))
        return QgsGeometry().fromPolyline([self.origin, P])



