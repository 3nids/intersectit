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
from qgis.core import QGis

from ..qgissettingmanager import SettingDialog
from ..qgiscombomanager import VectorLayerCombo, FieldCombo

from ..core.mysettings import MySettings

from ..ui.ui_settings import Ui_Settings


class MySettingsDialog(QDialog, Ui_Settings, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        self.obsDistanceSnapping.setItemData(0, "no")
        self.obsDistanceSnapping.setItemData(1, "project")
        self.obsDistanceSnapping.setItemData(2, "all")

        SettingDialog.__init__(self, self.settings)

        # distance combos
        self.distanceLayerCombo = VectorLayerCombo(self.dimensionDistanceLayer,
                                                   lambda: self.settings.value("dimensionDistanceLayer"),
                                                   {"groupLayers": False, "hasGeometry": True,
                                                    "geomType": QGis.Line})

        self.distanceObservationFieldCombo = FieldCombo(self.dimensionDistanceObservationField, self.distanceLayerCombo,
                                                        lambda: self.settings.value("dimensionDistanceObservationField"))
        self.distancePrecisionFieldCombo = FieldCombo(self.dimensionDistancePrecisionField, self.distanceLayerCombo,
                                                      lambda: self.settings.value("dimensionDistancePrecisionField"))

        # orientation combos
        self.orientationLayerCombo = VectorLayerCombo(self.dimensionOrientationLayer,
                                                      lambda: self.settings.value("dimensionOrientationLayer"),
                                                      {"groupLayers": False, "hasGeometry": True,
                                                       "geomType": QGis.Line})

        self.orientationObservationFieldCombo = FieldCombo(self.dimensionOrientationObservationField,
                                                           self.orientationLayerCombo,
                                                           lambda: self.settings.value("dimensionOrientationObservationField"))
        self.orientationPrecisionFieldCombo = FieldCombo(self.dimensionOrientationPrecisionField,
                                                         self.orientationLayerCombo,
                                                         lambda: self.settings.value("dimensionOrientationPrecisionField"))

        # other combos
        self.simpleIntersectionLayerCombo = VectorLayerCombo(self.simpleIntersectionLayer,
                                                             lambda: self.settings.value("simpleIntersectionLayer"),
                                                             {"groupLayers": False, "hasGeometry": True,
                                                              "geomType": QGis.Point})
        self.advancedIntersectionLayerCombo = VectorLayerCombo(self.advancedIntersectionLayer,
                                                               lambda: self.settings.value("advancedIntersectionLayer"),
                                                               {"groupLayers": False, "hasGeometry": True,
                                                                "geomType": QGis.Point})
        self.reportFieldCombo = FieldCombo(self.reportField, self.advancedIntersectionLayerCombo,
                                           lambda: self.settings.value("reportField"))
