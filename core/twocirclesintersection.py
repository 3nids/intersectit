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

import math

from qgis.core import QgsPoint


class TwoCirclesIntersection():
    def __init__(self, observations, initPoint):
        # see http://www.mathpages.com/home/kmath396/kmath396.htm
        x1 = observations[0]["x"]
        y1 = observations[0]["y"]
        r1 = observations[0]["observation"]
        x2 = observations[1]["x"]
        y2 = observations[1]["y"]
        r2 = observations[1]["observation"]
        d = math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))
        if d < math.fabs(r1-r2):
            # circle is within the other
            return None
        if d > r1+r2:
            # circles are not intersecting, scaling their radius to get intersection"
            s = d/(r1+r2)
            r1 *= s
            r2 *= s
        a = math.sqrt((d+r1+r2) * (d+r1-r2) * (d-r1+r2) * (-d+r1+r2)) / 4
        xlt = (x1+x2)/2.0 - (x1-x2)*(r1*r1-r2*r2)/(2.0*d*d)
        ylt = (y1+y2)/2.0 - (y1-y2)*(r1*r1-r2*r2)/(2.0*d*d)
        xrt = 2.0*(y1-y2)*a/(d*d)
        yrt = 2.0*(x1-x2)*a/(d*d)
        xa = xlt + xrt
        ya = ylt - yrt
        xb = xlt - xrt
        yb = ylt + yrt
        pt1 = QgsPoint(xa, ya)
        pt2 = QgsPoint(xb, yb)
        # return unique point
        d1 = pt1.sqrDist(initPoint)
        d2 = pt2.sqrDist(initPoint)
        if d1 < d2:
            self.intersection = pt1
        else:
            self.intersection = pt2
