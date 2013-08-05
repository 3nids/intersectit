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

from math import sqrt, acos, atan2, pi, ceil, fabs, cos, sin
from qgis.core import QgsGeometry, QgsPoint


class Arc():
    def __init__(self, p1, p2, p3=None):
        if p3 is None:
            p3 = QgsPoint(p2)
            p2 = self.createMiddlePoint(p1, p3)
        self.p1 = QgsPoint(p1)
        self.p2 = QgsPoint(p2)
        self.p3 = QgsPoint(p3)

    def setPoint(self, point):
        self.p2 = point

    def createMiddlePoint(self, p1, p3):
        direction = [-(p1.y()-p3.y()),  p1.x()-p3.x()]
        length = sqrt(p1.sqrDist(p3))
        return QgsPoint((p1.x()+p3.x())/2 + direction[0] * .2 * length,
                        (p1.y()+p3.y())/2 + direction[1] * .2 * length)

    def geometry(self):
        # code taken from cadtools/circulararc.py
        # credits to Stefan Ziegler
        coords = [self.p1]
        featurePitch = 2
        featureAngle = 5
        center = self.getArcCenter(self.p1, self.p2, self.p3)
        if center is None:
            coords.append(self.p3)
            return QgsGeometry().fromPolyline(coords)
        cx = center.x()
        cy = center.y()
        px = self.p2.x()
        py = self.p2.y()
        r = ((cx-px) * (cx-px) + (cy-py) * (cy-py)) ** 0.5

        arcIncr = 2.0 * acos(1.0 - (featurePitch / 1000) / r)
        arcIncr = featureAngle * pi / 180

        a1 = atan2(self.p1.y() - center.y(), self.p1.x() - center.x())
        a2 = atan2(self.p2.y() - center.y(), self.p2.x() - center.x())
        a3 = atan2(self.p3.y() - center.y(), self.p3.x() - center.x())
        # Clockwise
        if a1 > a2 > a3:
            sweep = a3 - a1
        # Counter-clockwise
        elif a1 < a2 < a3:
            sweep = a3 - a1
        # Clockwise, wrap
        elif a3 < a1 < a2 or a2 < a3 < a1:
            sweep = a3 - a1 + 2*pi
        # Counter-clockwise, wrap
        elif a3 > a1 > a2 or a2 > a3 > a1:
            sweep = a3 - a1 - 2*pi
        else:
            sweep = 0.0
        ptcount = int(ceil(fabs(sweep / arcIncr)))
        if sweep < 0:
            arcIncr *= -1.0
        angle = a1
        for i in range(0, ptcount-1):
            angle += arcIncr
            if arcIncr > 0.0 and angle > pi:
                angle -= 2*pi
            if arcIncr < 0.0 and angle < -1*pi:
                angle -= 2*pi
            x = cx + r * cos(angle)
            y = cy + r * sin(angle)
            coords.append(QgsPoint(x, y))
            if angle < a2 < angle+arcIncr:
                coords.append(self.p2)
            if angle > a2 > angle+arcIncr:
                coords.append(self.p2)
        coords.append(self.p3)
        return QgsGeometry().fromPolyline(coords)

    def getArcCenter(self, p1, p2, p3):
        bx = p1.x()
        by = p1.y()
        cx = p2.x()
        cy = p2.y()
        dx = p3.x()
        dy = p3.y()
        temp = cx * cx + cy * cy
        bc = (bx * bx + by * by - temp) / 2.0
        cd = (temp - dx * dx - dy * dy) / 2.0
        det = (bx - cx) * (cy - dy) - (cx - dx) * (by - cy)
        try:
            det = 1 / det
            x = (bc * (cy - dy) - cd * (by - cy)) * det
            y = ((bx - cx) * cd - (cx - dx) * bc) * det
            return QgsPoint(x, y)
        except ZeroDivisionError:
            return None
