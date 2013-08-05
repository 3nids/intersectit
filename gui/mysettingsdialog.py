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

        self.dimensionLayerCombo = VectorLayerCombo(self.dimensionLayer,
                                                    lambda: self.settings.value("dimensionLayer"),
                                                    {"groupLayers": False, "hasGeometry": True})
        self.observationFieldCombo = FieldCombo(self.observationField, self.dimensionLayerCombo,
                                                lambda: self.settings.value("observationField"))
        self.typeFieldCombo = FieldCombo(self.typeField, self.dimensionLayerCombo,
                                         lambda: self.settings.value("typeField"))
        self.precisionFieldCombo = FieldCombo(self.precisionField, self.dimensionLayerCombo,
                                              lambda: self.settings.value("precisionField"))
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
