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

from PyQt4.QtCore import QVariant
from qgis.core import QgsFeature, QgsGeometry, QgsPoint

from mysettings import MySettings


class Dimension():
    def __init__(self, layer, intersectedPoint, distancePoint, distance, precision, radius):
        self.layer = layer
        self.provider = layer.dataProvider()
        self.radius = radius
        self.distance = distance
        self.precision = precision
        self.length = math.sqrt(intersectedPoint.sqrDist(distancePoint))
        self.isActive = True
        self.intersectedPoint = intersectedPoint
        self.distancePoint = distancePoint
        self.anchorPoint = [(intersectedPoint.x()+distancePoint.x())/2, (intersectedPoint.y()+distancePoint.y())/2]
        self.direction = [-(intersectedPoint.y()-distancePoint.y()),  intersectedPoint.x()-distancePoint.x()]
        self.way = 1
        self.settings = MySettings()
        self.createFeature()

    def setRadius(self, radius):
        self.radius = radius

    def reverse(self):
        self.way *= -1
        return self

    def createFeature(self):
        self.isActive = True
        # create feature and geometry
        f = QgsFeature()
        fields = self.provider.fields()
        f.setFields(fields)
        f.initAttributes(fields.count())
        f.setGeometry(self.geometry())
        # dimension and precision fields
        if self.settings.value("dimenPlaceMeasure"):
            dimFieldName = self.settings.value("observationField")
            idx = self.provider.fieldNameIndex(dimFieldName)
            if idx != -1:
                f[dimFieldName] = QVariant("%.4f" % self.distance)
        if self.settings.value("dimenPlacePrecision"):
            preFieldName = self.settings.value("precisionField")
            idx = self.provider.fieldNameIndex(preFieldName)
            if idx != -1:
                f[preFieldName] = QVariant("%.4f" % self.precision)
        ans, fz = self.provider.addFeatures([f])
        self.f_id = fz[0].id()
        self.layer.updateExtents()
        self.layer.setCacheImage(None)
        self.layer.triggerRepaint()

    def delete(self):
        self.isActive = False
        self.provider.deleteFeatures([self.f_id])
        self.layer.updateExtents()
        self.layer.setCacheImage(None)
        self.layer.triggerRepaint()

    def draw(self):
        if self.isActive:
            # can also do on layer: startEditing, changeGeometry, rollBack, updateExtents
            print self.f_id
            self.provider.changeGeometryValues({self.f_id: self.geometry()})
            self.layer.setCacheImage(None)
            self.layer.triggerRepaint()

    def geometry(self):
        # http://www.vb-helper.com/howto_find_quadratic_curve.html
        curvePoint = QgsPoint(self.anchorPoint[0] + self.way * self.direction[0] * self.radius/100,
                              self.anchorPoint[1] + self.way * self.direction[1] * self.radius/100)
        return QgsGeometry().fromMultiPoint([self.intersectedPoint, curvePoint, self.distancePoint])
