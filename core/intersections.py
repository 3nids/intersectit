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


def closestPoint(point, pointList):
    distList = list(pointList)
    for i, distPoint in enumerate(pointList):
        distList[i] = point.sqrDist(distPoint)
    minDist = min(distList)
    idx = distList.index(minDist)
    return pointList[idx]


class TwoCirclesIntersection():
    def __init__(self, observations, initPoint):
        self.intersection = None
        # see http://www.mathpages.com/home/kmath396/kmath396.htm
        x1 = observations[0]["x"]
        y1 = observations[0]["y"]
        r1 = observations[0]["observation"]
        x2 = observations[1]["x"]
        y2 = observations[1]["y"]
        r2 = observations[1]["observation"]
        d = sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))
        if d < fabs(r1-r2):
            self.report = "No solution found using two distances intersection since circle are within each others."
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
        P1 = QgsPoint(xa, ya)
        P2 = QgsPoint(xb, yb)
        self.solution = closestPoint(initPoint, [P1, P2])
        self.report = "A solution using two distances has been found.\n\n"
        self.report += "         |       x       |       y       |   radius   |\n"
        self.report += "-------- | ------------- | ------------- | ---------- |\n"
        self.report += "Circle 1 | %13.3f | %13.3f | %10.3f |\n" % (x1, y1, r1)
        self.report += "Circle 2 | %13.3f | %13.3f | %10.3f |\n" % (x2, y2, r2)
        self.report += "-------- | ------------- | ------------- |\n"
        self.report += "Solution | %13.3f | %13.3f |\n" % (self.solution.x(), self.solution.y())


class TwoOrientationIntersection():
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
        x1 = observations[0]["x"]
        y1 = observations[0]["y"]
        a1 = pi/180 * observations[0]["observation"]
        x2 = observations[1]["x"]
        y2 = observations[1]["y"]
        a2 = pi/180 * observations[1]["observation"]
        if fabs(a1) == fabs(a2):
            self.report = "No solution found using two orientations intersection since orientations are parralell."
            return
        k = (x2-x1+(y1-y2)*tan(a2)) / (sin(a1)*(1-tan(a2)/tan(a1)))
        x = x1 + k * sin(a1)
        y = y1 + k * cos(a1)
        self.solution = QgsPoint(x, y)
        self.report = "A solution using two orientations has been found.\n\n"
        self.report += "              |       x       |       y       | azimut |\n"
        self.report += " ------------ | ------------- | ------------- | ------ |\n"
        self.report += "Orientation 1 | %13.3f | %13.3f | %8.3f |\n" % (x1, y1, a1)
        self.report += "Orientation 2 | %13.3f | %13.3f | %8.3f |\n" % (x2, y2, a2)
        self.report += "------------- | ------------- | ------------- |\n"
        self.report += "Solution      | %13.3f | %13.3f |\n" % (x, y)


class DistanceOrientationIntersection():
    def __init__(self, observations, initPoint):
        self.intersection = None
        if observations[0]["type"] == "distance":
            distance = observations[0]
            orientation = observations[1]
        else:
            orientation = observations[0]
            distance = observations[1]
        # obs 1: distance:: (x1-x)^2 + (y1-y)^2 - r^2 = 0
        # obs 2: line::   [ x = x2 + k . sin(az)
        #                 [ y = y2 + k . cos(az)
        #
        # dx = x1-x2, dy = y1-y2
        #
        # (dx-k.sin(az))^2 + (dy-k.cos(az))^2 - r^2 = 0
        #
        # k^2 + -2.k * (dx.sin(az)+dy.cos(az)) + dx^2 + dy^2 - r^2 = 0
        #
        # => quadratic equation for k
        x1 = distance["x"]
        y1 = distance["y"]
        r = distance["observation"]
        x2 = orientation["x"]
        y2 = orientation["y"]
        az = orientation["observation"]*pi/180
        dx = x1-x2
        dy = y1-y2
        # solve quadratic equation
        a = 1
        b = -2*(dx*sin(az)+dy*cos(az))
        c = pow(dx, 2) + pow(dy, 2) - pow(r, 2)
        delta = pow(b, 2) - 4*a*c
        # no intersection
        if delta < 0:
            self.report = "No solution found using an orientation and a distance intersection."
            return
        # compute solutions
        k_1 = (-b + sqrt(delta)) / (2*a)
        k_2 = (-b - sqrt(delta)) / (2*a)
        x_1 = x2 + k_1*sin(az)
        y_1 = y2 + k_1*cos(az)
        x_2 = x2 + k_2*sin(az)
        y_2 = y2 + k_2*cos(az)
        P1 = QgsPoint(x_1, y_1)
        P2 = QgsPoint(x_2, y_2)
        self.solution = closestPoint(initPoint, [P1, P2])
        self.report = "A solution using an orientation and a distance has been found.\n\n"
        self.report += "          |       x       |       y       | observation |\n"
        self.report += "--------- | ------------- | ------------- | ----------- |\n"
        self.report += "Orientation | %13.3f | %13.3f |   %9.3f |\n" % (x2, y2, az)
        self.report += "Circle    | %13.3f | %13.3f |   %9.3f |\n" % (x1, y1, r)
        self.report += "--------- | ------------- | ------------- |\n"
        self.report += "Solution  | %13.3f | %13.3f |\n" % (self.solution.x(), self.solution.y())



