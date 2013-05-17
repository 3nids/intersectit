
from PyQt4.QtGui import QColor
from ..qgissettingmanager import *


pluginName = "intersectit"


class MySettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)
         
        # global settings
        self.addSetting("obsSnapping", "bool", "global", True)
        self.addSetting("obsDefaultPrecisionDistance", "double", "global", 25)
        self.addSetting("obsDefaultPrecisionOrientation", "double", "global", .01)
        self.addSetting("intersecResultConfirm", "bool", "global", True)
        self.addSetting("intersecSelectTolerance", "double", "global", 0.3)
        self.addSetting("intersecSelectUnits", "string", "global", "map")
        self.addSetting("intersectRubberColor", "Color", "global", QColor(0, 0, 255))
        self.addSetting("intersectRubberWidth", "double", "global", 2)
        self.addSetting("intersecLSmaxIter", "Integer", "global", 15)
        self.addSetting("intersecLSconvergeThreshold", "double", "global", .0005)

        # project settings
        self.addSetting("intersecResultPlacePoint", "bool", "project", False)
        self.addSetting("intersecResultPlaceReport", "bool", "project", False)
        self.addSetting("dimenPlaceDimension", "bool", "project", True)
        self.addSetting("dimenPlaceMeasure", "bool", "project", True)
        self.addSetting("dimenPlacePrecision", "bool", "project", False)
        # fields and layers
        self.addSetting("dimensionLayer", "string", "project", "")
        self.addSetting("measureField", "string", "project", "")
        self.addSetting("precisionField", "string", "project", "")
        self.addSetting("intersectionLayer", "string", "project", "")
        self.addSetting("reportField", "string", "project", "")
        self.addSetting("memoryLineLayer", "string", "project", "")
        self.addSetting("memoryPointLayer", "string", "project", "")
