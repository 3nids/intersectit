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
from PyQt4.QtGui import QMessageBox
from qgis.core import QgsRectangle, QgsFeatureRequest, QgsFeature, QgsGeometry
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand

from ..core.mysettings import MySettings
from ..core.memorylayers import MemoryLayers
from ..core.leastsquares import LeastSquares
from ..core.twocirclesintersection import TwoCirclesIntersection

from placedimension import PlaceDimension
from lsreport import LSreport


class placeIntersectionOnMap(QgsMapToolEmitPoint):
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.settings = MySettings()
        self.lineLayer = MemoryLayers(iface).lineLayer
        self.pointLayer = MemoryLayers(iface).pointLayer
        self.rubber = QgsRubberBand(self.canvas)
        self.rubber.setWidth(self.settings.value("intersectRubberWidth"))
        self.rubber.setColor(self.settings.value("intersectRubberColor"))
        self.tolerance = self.settings.value("intersecSelectTolerance")
        units = self.settings.value("intersecSelectUnits")
        if units == "pixels":
            self.tolerance *= self.canvas.mapUnitsPerPixel()

    def deactivate(self):
        self.rubber.reset()

    def canvasMoveEvent(self, mouseEvent):
        # put the observations within tolerance in the rubber band
        self.rubber.reset()
        point = self.toMapCoordinates(mouseEvent.pos())
        for f in self.getFeatures(point):
            self.rubber.addGeometry(f.geometry(), None)

    def canvasPressEvent(self, mouseEvent):
        self.rubber.reset()
        observations = []
        point = self.toMapCoordinates(mouseEvent.pos())
        for f in self.getFeatures(point):
            # todo: new API
            observations.append({"type": f.attribute("type").toString(),
                                 "x": f.attribute("x").toDouble()[0],
                                 "y": f.attribute("y").toDouble()[0],
                                 "measure": f.attribute("measure").toDouble()[0],
                                 "precision": f.attribute("precision").toDouble()[0]})
        self.doIntersection(point, observations)

    def getFeatures(self, point):
        features = []
        featReq = QgsFeatureRequest()
        box = QgsRectangle(point.x()-self.tolerance,
                           point.y()-self.tolerance,
                           point.x()+self.tolerance,
                           point.y()+self.tolerance)
        featReq.setFilterRect(box)
        f = QgsFeature()
        iter = self.lineLayer().getFeatures(featReq)
        while iter.nextFeature(f):
            features.append(QgsFeature(f))
        return features

    def doIntersection(self, initPoint, observations):
        nObs = len(observations)
        report = ""
        if nObs < 2:
            return
        if nObs == 2:
            intersectedPoint = TwoCirclesIntersection(observations, initPoint).intersection
            if intersectedPoint is None:
                return
            if self.settings.value("intersecResultConfirm"):
                reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                             "A perfect intersection has been found using two circles."
                                             " Use this solution?", QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
        else:
            LS = LeastSquares(observations, initPoint)
            intersectedPoint = LS.solution
            report = LS.report
            if self.settings.value("intersecResultConfirm"):
                if not LSreport(report).exec_():
                    return

        # save the intersection result (point) and its report
        while True:
            if not self.settings.value("intersecResultPlacePoint"):
                break  # if we do not place any point, skip
            intLayer = next((layer for layer in self.iface.mapCanvas().layers() if layer.id() == self.settings.value("intersectionLayer")), None)
            if intLayer is None:
                reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                             "To place the intersection solution, "
                                             "you must select a layer in the settings. "
                                             "Would you like to open settings?",
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                if self.uisettings.exec_() == 0:
                    return
                continue
            if self.settings.value("intersecResultPlaceReport"):
                reportField = next((field for field in intLayer.dataProvider().fieldNameMap() if field == self.settings.value("reportField")), None)
                if reportField is None:
                    reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                                 "To save the intersection report, please select a field for tit."
                                                 " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                    if self.uisettings.exec_() == 0:
                        return
                    continue
            break
        if self.settings.value("intersecResultPlacePoint"):
            f = QgsFeature()
            f.setGeometry(QgsGeometry.fromPoint(intersectedPoint))
            if self.settings.value("intersecResultPlaceReport"):
                irep = intLayer.dataProvider().fieldNameIndex(reportField)
                f.addAttribute(irep, QVariant(report))
            intLayer.dataProvider().addFeatures([f])
            intLayer.updateExtents()
            self.canvas.refresh()

         # check that dimension layer and fields have been set correctly
        while True:
            if not self.settings.value("dimenPlaceDimension"):
                return  # if we do not place any dimension, skip
            dimLayer = next((layer for layer in self.iface.mapCanvas().layers() if layer.id() == self.settings.value("dimensionLayer")), None)
            if dimLayer is None:
                reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                             "To place dimension arcs, you must select a layer in the settings."
                                             " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                if self.uisettings.exec_() == 0:
                    return
                continue
            if self.settings.value("dimenPlaceMeasure"):
                measureField = next((True for field in dimLayer.dataProvider().fieldNameMap() if field == self.settings.value("measureField")), None)
                if measureField is None:
                    ok = False
                    reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                                 "To save the measured distance, please select a field for tit."
                                                 " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                    if self.uisettings.exec_() == 0:
                        return
                    continue
            if self.settings.value("dimenPlacePrecision"):
                precisionField = next((True for field in dimLayer.dataProvider().fieldNameMap() if field == self.settings.value("precisionField")), None)
                if precisionField is None:
                    ok = False
                    reply = QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                                 "To save the measure precision, please select a field for it."
                                                 " Would you like to open settings?", QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                    if self.uisettings.exec_() == 0:
                        return
                    continue
            break
        dlg = PlaceDimension(self.iface, intersectedPoint, observations, [self.lineLayer(), self.pointLayer()])
        dlg.exec_()
