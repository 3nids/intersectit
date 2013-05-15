
import math

from PyQt4.QtCore import QVariant
from qgis.core import QgsFeature, QgsGeometry, QgsPoint

from mysettings import MySettings


class Dimension():
    def __init__(self, iface, layer, intersectedPoint, distancePoint, distance, precision, radius):
        self.iface = iface
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
        return self

    def reverse(self):
        self.way *= -1
        return self

    def createFeature(self):
        self.isActive = True
        # create feature and geometry
        f = QgsFeature()
        f.setFields(self.provider.fields())
        f.setGeometry(self.geometry())
        # dimension and precision fields
        if self.settings.value("dimenPlaceMeasure"):
            dimFieldName = self.settings.value("measureField")
            idx = self.provider.fieldNameIndex(dimFieldName)
            if idx != -1:
                f[idx] = QVariant("%.4f" % self.distance)
        if self.settings.value("dimenPlacePrecision"):
            preFieldName = self.settings.value("precisionField")
            idx = self.provider.fieldNameIndex(preFieldName)
            if idx != -1:
                f[idx] = QVariant("%.4f" % self.precision)
        ans, f = self.provider.addFeatures([f])
        self.f_id = f[0].id()
        self.layer.updateExtents()
        self.iface.mapCanvas().refresh()

    def delete(self):
        self.isActive = False
        self.provider.deleteFeatures([self.f_id])
        self.layer.updateExtents()
        self.iface.mapCanvas().refresh()

    def draw(self):
        if self.isActive:
            # can also do on layer: startEditing, changeGeometry, rollBack, updateExtents
            self.provider.changeGeometryValues({self.f_id: self.geometry()})
            self.iface.mapCanvas().refresh()

    def geometry(self):
        # http://www.vb-helper.com/howto_find_quadratic_curve.html
        curvePoint = QgsPoint(self.anchorPoint[0] + self.way * self.direction[0] * self.radius/100,
                              self.anchorPoint[1] + self.way * self.direction[1] * self.radius/100)
        return QgsGeometry().fromMultiPoint([self.intersectedPoint, curvePoint, self.distancePoint])