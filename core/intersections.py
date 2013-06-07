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

from math import sqrt, fabs, pow, sin, cos, tan, pi
from qgis.core import QgsPoint


class TwoCirclesIntersection():
    def __init__(self, observations, initPoint):
        self.intersection = None
        # see http://www.mathpages.com/home/kmath396/kmath396.htm
        x1 = observations[0]["x"].toDouble()[0]
        y1 = observations[0]["y"].toDouble()[0]
        r1 = observations[0]["observation"].toDouble()[0]
        x2 = observations[1]["x"].toDouble()[0]
        y2 = observations[1]["y"].toDouble()[0]
        r2 = observations[1]["observation"].toDouble()[0]
        d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))
        if d < fabs(r1-r2):
            # circle is within the other
            return
        if d > r1+r2:
            # circles are not intersecting, scaling their radius to get intersection"
            s = d/(r1+r2)
            r1 *= s
            r2 *= s
        a = sqrt((d+r1+r2) * (d+r1-r2) * (d-r1+r2) * (-d+r1+r2)) / 4
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


class TwoDirectionIntersection():
    def __init__(self, observations):
        self.intersection = None
        # x = x1+k*cos(90-a1) = x2+l*cos(90-a2)
        # y = y1+k*sin(90-a1) = y2+l*sin(90-a2)
        #
        # [ x1 + k cos(90-a1) - x2 - l cos(90-a2) = 0
        # [ y1 + k sin(90-a1) - y2 - l sin(90-a2) = 0
        #
        # [ x1 + k sin(a1) - x2 - l sin(a2) = 0
        # [ y1 + k cos(a1) - y2 - l cos(a2) = 0
        #
        # k = ( x2 - x1 + l sin(a2) ) / sin(a2)
        # l = ( y1 - y2 + k cos(a1) ) / cos(a2)
        # => solve k
        x1 = observations[0]["x"].toDouble()[0]
        y1 = observations[0]["y"].toDouble()[0]
        a1 = pi/180 * observations[0]["observation"].toDouble()[0]
        x2 = observations[1]["x"].toDouble()[0]
        y2 = observations[1]["y"].toDouble()[0]
        a2 = pi/180 * observations[1]["observation"].toDouble()[0]

        if fabs(a1) == fabs(a2):
            # parralell
            return

        k = (x2-x1+(y1-y2)*tan(a2)) / (sin(a1)*(1-tan(a2)/tan(a1)))
        x = x1 + k * sin(a1)
        y = y1 + k * cos(a1)

        self.intersection = QgsPoint(x, y)


class CircleDirectionIntersection():
    def __init__(self, observations, initPoint):
        self.intersection = None
        if observations[0]["type"] == "distance":
            distance = observations[0]
            direction = observations[1]
        else:
            direction = observations[0]
            distance = observations[1]

        # distance:: (x1-x)^2 + (y1-y)^2 + d^2 = 0
        # direction:: y - x/tan(az) - y2 + x2/tan(az)
        #
        # => y = x/tan(az) + y2 - x2/tan(az)
        #
        # (1) becomes:
        # 0 = x1^2 -2x1x + x^2 + y1^2 -2y1(x/tan(az)+y2-x2/tan(az)) + x^2/tan^2(a)
        #   + 2x(y2-x2/tan(az))/tan(az) + (y2-x2/tan(az))^2
        #
        # 0 = x^2 (1+1/tan^2(az)) + x (-2x1-2y1/tan(az)+2(y2-x2/tan(az))/tan(az))
        #   + x1^2 + y1^2 - 2y1y2 + 2x2y1/tan(az) + (y2-x2/tan(az))^2 + d^2
        #
        # => quadratic equation

        x1 = distance["x"]
        y1 = distance["y"]
        d = distance["observation"]
        x2 = direction["x"]
        y2 = direction["y"]
        az = direction["observation"]

        a = 1 + 1/pow(tan(az), 2)
        b = -2*x1 - 2*y1/tan(az) + 2*(y2-x2/tan(az))/tan(az)
        c = pow(x1, 2) + pow(y1, 2) - 2*y1*y2 + 2*x2*y1/tan(az) + pow(y2-x2/tan(az), 2) + pow(d, 2)

        delta = pow(b, 2) - 4*a*c

        # no intersection
        if delta < 0:
            return

        x_1 = (-b + sqrt(delta)) / a
        x_2 = (-b - sqrt(delta)) / a
        y_1 = x_1/tan(az) + y2 - x2/tan(az)
        y_2 = x_2/tan(az) + y2 - x2/tan(az)

        P1 = QgsPoint(x_1, y_1)
        P2 = QgsPoint(x_2, y_2)





