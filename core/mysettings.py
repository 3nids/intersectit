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

from PyQt4.QtGui import QColor
from ..qgissettingmanager import *

pluginName = 'intersectit'


class MySettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, pluginName)
         
        # Global settings
        self.add_setting( Double( 'obsDefaultPrecisionDistance', Scope.Global, .025) )
        self.add_setting( Double( 'obsDefaultPrecisionOrientation', Scope.Global, .5) )
        self.add_setting( Double( 'obsOrientationLength', Scope.Global, 4) )
        self.add_setting( Double( 'selectTolerance', Scope.Global, 7) )
        self.add_setting( String( 'selectUnits', Scope.Global, 'pixels') )
        self.add_setting( Color( 'rubberColor', Scope.Global, QColor(0, 0, 255, 150), {'alpha': True}) )
        self.add_setting( Double( 'rubberWidth', Scope.Global, 2) )
        self.add_setting( Integer( 'rubberSize', Scope.Global, 12) )
        self.add_setting( Integer( 'rubberIcon', Scope.Global, 4) )
        self.add_setting( Integer( 'advancedIntersecLSmaxIteration', Scope.Global, 15) )
        self.add_setting( Double( 'advancedIntersecLSconvergeThreshold', Scope.Global, .0005) )

        # Project settings
        self.add_setting( Bool( 'simpleIntersectionWritePoint', Scope.Project, False) )
        self.add_setting( Bool( 'advancedIntersectionWritePoint', Scope.Project, False) )
        self.add_setting( Bool( 'advancedIntersectionWriteReport', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionDistanceWrite', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionDistanceObservationWrite', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionDistancePrecisionWrite', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionOrientationWrite', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionOrientationObservationWrite', Scope.Project, False) )
        self.add_setting( Bool( 'dimensionOrientationPrecisionWrite', Scope.Project, False) )
        # fields and layers
        self.add_setting( String( 'dimensionDistanceLayer', Scope.Project, '') )
        self.add_setting( String( 'dimensionDistancePrecisionField', Scope.Project, '') )
        self.add_setting( String( 'dimensionDistanceObservationField', Scope.Project, '') )
        self.add_setting( String( 'dimensionOrientationLayer', Scope.Project, '') )
        self.add_setting( String( 'dimensionOrientationPrecisionField', Scope.Project, '') )
        self.add_setting( String( 'dimensionOrientationObservationField', Scope.Project, '') )

        self.add_setting( String( 'simpleIntersectionLayer', Scope.Project, '') )
        self.add_setting( String( 'advancedIntersectionLayer', Scope.Project, '') )
        self.add_setting( String( 'reportField', Scope.Project, '') )
        self.add_setting( String( 'memoryLineLayer', Scope.Project, '') )
        self.add_setting( String( 'memoryPointLayer', Scope.Project, '') )