
from PyQt4.QtGui import QDialog

from ..qgissettingmanager import SettingDialog
from ..qgiscombomanager import VectorLayerCombo, FieldCombo

from ..core.mysettings import MySettings

from ..ui.ui_settings import Ui_Settings


class MySettingsDialog(QDialog, Ui_Settings, SettingDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = MySettings()
        SettingDialog.__init__(self, self.settings)

        self.dimensionLayerCombo = VectorLayerCombo(self.dimensionLayer,
                                                    lambda: self.settings.value("dimensionLayer"),
                                                    {"groupLayers": False, "hasGeometry": True})
        self.measureFieldCombo = FieldCombo(self.measureField, self.dimensionLayerCombo,
                                            lambda: self.settings.value("measureField"))
        self.precisionFieldCombo = FieldCombo(self.precisionField, self.dimensionLayerCombo,
                                              lambda: self.settings.value("precisionField"))

        self.intersectionLayerCombo = VectorLayerCombo(self.intersectionLayer,
                                                       lambda: self.settings.value("intersectionLayer"),
                                                       {"groupLayers": False, "hasGeometry": True})
        self.reportFieldCombo = FieldCombo(self.reportField, self.intersectionLayerCombo,
                                           lambda: self.settings.value("reportField"))
