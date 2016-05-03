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

from PyQt4.QtGui import QDialog
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox, QgsMapLayerProxyModel

from ..qgissettingmanager import SettingDialog

from ..core.mysettings import MySettings

from ..ui.ui_settings import Ui_Settings


class MySettingsDialog(QDialog, Ui_Settings, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()

        # distance combos
        self.dimensionDistanceLayer.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.dimensionDistanceLayer.layerChanged.connect(self.dimensionDistanceObservationField.setLayer)
        self.dimensionDistanceLayer.layerChanged.connect(self.dimensionDistancePrecisionField.setLayer)

        # orientation combos
        self.dimensionOrientationLayer.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.dimensionOrientationLayer.layerChanged.connect(self.dimensionOrientationObservationField.setLayer)
        self.dimensionOrientationLayer.layerChanged.connect(self.dimensionOrientationPrecisionField.setLayer)

        # other combos
        self.simpleIntersectionLayer.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.advancedIntersectionLayer.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.advancedIntersectionLayer.layerChanged.connect(self.reportField.setLayer)

        SettingDialog.__init__(self, self.settings)