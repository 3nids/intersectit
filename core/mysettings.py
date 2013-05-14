
from PyQt4.QtGui import QColor
from ..qgissettingmanager import *


pluginName = "intersectit"


class MySettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)
         
        # global settings
        self.addSetting("obsSnapping", "Bool", "global", True)
        self.addSetting("obsDefaultPrecisionDistance", "Double", "global", 25)
        self.addSetting("obsDefaultPrecisionOrientation", "Double", "global", .01)
        self.addSetting("intersecResultConfirm", "Bool", "global", True)
        self.addSetting("intersecSelectTolerance", "Double", "global", 0.3)
        self.addSetting("intersecSelectUnits", "String", "global", "map")
        self.addSetting("intersectRubberColor", "Color ", "global", QColor(0, 0, 255))
        self.addSetting("intersectRubberWidth", "Double", "global", 2)
        self.addSetting("intersecLSmaxIter", "Integer", "global", 15)
        self.addSetting("intersecLSconvergeThreshold", "Double", "global", .0005)

        # project settings
        self.addSetting("Bool", "intersecResultPlacePoint", "project", False)
        self.addSetting("Bool", "intersecResultPlaceReport", "project", False)
        self.addSetting("Bool", "dimenPlaceDimension", "project", True)
        self.addSetting("Bool", "dimenPlaceMeasure", "project", True)
        self.addSetting("Bool", "dimenPlacePrecision", "project", False)
        # fields and layers
        self.addSetting("dimensionLayer", "String", "project", "")
        self.addSetting("measureField", "String", "project", "")
        self.addSetting("precisionField", "String", "project", "")
        self.addSetting("intersectionLayer", "String", "project", "")
        self.addSetting("reportField", "String", "project", "")
        self.addSetting("memoryLineLayer", "String", "project", "")
        self.addSetting("memoryPointLayer", "String", "project", "")

