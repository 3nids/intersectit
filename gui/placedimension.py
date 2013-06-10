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

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QDialog, QMessageBox
from qgis.core import QgsPoint, QgsMapLayerRegistry
from qgis.gui import QgsRubberBand

from ..core.mysettings import MySettings
from ..core.dimension import Dimension
from ..core.memorylayers import MemoryLayers

from mysettingsdialog import MySettingsDialog

from ..ui.ui_place_dimension import Ui_placeDimension


class PlaceDimension(QDialog, Ui_placeDimension):
    def __init__(self, iface, intersectedPoint, observations):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.lineLayer = MemoryLayers(iface).lineLayer
        self.pointLayer = MemoryLayers(iface).pointLayer
        self.settings = MySettings()
        self.layer = QgsMapLayerRegistry.instance().mapLayer(self.settings.value("dimensionLayer"))
        self.rubber = QgsRubberBand(iface.mapCanvas())
        self.rubber.setWidth(2)
        defaultRadius = self.radiusSlider.value()
        self.accepted.connect(self.rubber.reset)
        self.rejected.connect(self.cancel)
        self.radiusSpin.valueChanged.connect(self.radiusSlider.setValue)
        self.radiusSlider.valueChanged.connect(self.radiusSpin.setValue)
        self.radiusSlider.valueChanged.connect(self.radiusChanged)

        # init state for observation layers visibility
        self.displayLayersBox.stateChanged.connect(self.toggleMemoryLayerVisibility)

        # check dimension and precision fields
        if self.settings.value("dimenPlaceMeasure"):
            dimFieldName = self.settings.value("observationField")
            idx = self.layer.dataProvider().fieldNameIndex(dimFieldName)
            if idx == -1:
                if QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                        "The field to save the observation could not be found."
                                        " Would you like to open settings?" % QMessageBox.Yes, QMessageBox.No
                                        ) == QMessageBox.Yes:
                    MySettingsDialog().exec_()

        if self.settings.value("dimenPlacePrecision"):
            preFieldName = self.settings.value("precisionField")
            idx = self.layer.dataProvider().fieldNameIndex(preFieldName)
            if idx == -1:
                if QMessageBox.question(self.iface.mainWindow(), "IntersectIt",
                                        "The field to save the precision could not be found."
                                        " Would you like to open settings?" % QMessageBox.Yes, QMessageBox.No
                                        ) == QMessageBox.Yes:
                    MySettingsDialog().exec_()

        # create the observations
        self.observations = observations
        self.dimension = []
        self.dimensionCombo.clear()
        nn = len(observations)
        for i, obs in enumerate(observations):
            self.dimensionCombo.addItem("%u/%u" % (i+1, nn))
            self.dimension.append(Dimension(self.layer,
                                            intersectedPoint,
                                            QgsPoint(obs["x"], obs["y"]),
                                            obs["observation"],
                                            obs["precision"],
                                            defaultRadius))
        # above line must be placed after the combobox population
        self.dimensionCombo.currentIndexChanged.connect(self.dimensionSelected)
        self.dimensionSelected(0)

    def toggleMemoryLayerVisibility(self, i):
        self.displayLayersBox.setTristate(False)
        self.iface.legendInterface().setLayerVisible(self.lineLayer(), bool(i))
        self.iface.legendInterface().setLayerVisible(self.pointLayer(), bool(i))

    def currentDimension(self):
        return self.dimension[self.dimensionCombo.currentIndex()]

    def dimensionSelected(self, i):
        dimension = self.currentDimension()
        self.radiusSlider.setValue(dimension.radius)
        self.createBox.setChecked(dimension.isActive)
        self.updateRubber()

    def radiusChanged(self, radius):
        self.currentDimension().setRadius(radius)
        self.currentDimension().draw()
        self.updateRubber()

    def cancel(self):
        self.rubber.reset()
        for d in self.dimension:
            d.delete()

    @pyqtSignature("on_prevButton_clicked()")
    def on_prevButton_clicked(self):
        i = max(0, self.dimensionCombo.currentIndex()-1)
        self.dimensionCombo.setCurrentIndex(i)

    @pyqtSignature("on_nextButton_clicked()")
    def on_nextButton_clicked(self):
        self.updateRubber()
        i = min(self.dimensionCombo.currentIndex()+1, len(self.dimension)-1)
        self.dimensionCombo.setCurrentIndex(i)

    @pyqtSignature("on_reverseButton_clicked()")
    def on_reverseButton_clicked(self):
        self.currentDimension().reverse().draw()
        self.updateRubber()

    @pyqtSignature("on_createBox_stateChanged(int)")
    def on_createBox_stateChanged(self, i):
        if i == 0:
            self.currentDimension().delete()
        else:
            self.currentDimension().createFeature()

    def updateRubber(self):
        self.rubber.reset()
        if self.createBox.isChecked():
            geom = self.currentDimension().geometry()
            self.rubber.addGeometry(geom, self.layer)
