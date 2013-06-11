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

from ..qgissettingmanager import SettingDialog

from ..core.mysettings import MySettings
from ..core.leastsquares import LeastSquares
from ..core.intersections import TwoCirclesIntersection, TwoDirectionIntersection, CircleDirectionIntersection

from ..ui.ui_intersection import Ui_Intersection


class IntersectionDialog(QDialog, Ui_Intersection, SettingDialog):
    def __init__(self, observations, initPoint):
        QDialog.__init__(self)
        self.setupUi(self)
        SettingDialog.__init__(self, MySettings(), False, False)
        self.processButton.clicked.connect(self.doIntersection)
        self.okButton.clicked.connect(self.accept)
        self.initPoint = initPoint

        self.observations = []
        self.solution = None
        self.report = ""

        self.observationTableWidget.displayRows(observations)
        self.observationTableWidget.itemChanged.connect(self.disbaleOKbutton)
        self.doIntersection()

    def disbaleOKbutton(self):
        self.okButton.setDisabled(True)

    def doIntersection(self):
        self.observations = []
        self.solution = None
        self.report = ""

        observations = self.observationTableWidget.getObservations()
        nObs = len(observations)
        if nObs == 2:
            if observations[0]["type"] == "distance" and observations[1]["type"] == "distance":
                intersection = TwoCirclesIntersection(observations, self.initPoint)
            elif observations[0]["type"] == "prolongation" and observations[1]["type"] == "prolongation":
                intersection = TwoDirectionIntersection(observations)
            else:
                intersection = CircleDirectionIntersection(observations, self.initPoint)
        else:
            maxIter = self.intersecLSmaxIteration.value()
            threshold = self.intersecLSconvergeThreshold.value()
            intersection = LeastSquares(observations, self.initPoint, maxIter, threshold)

        self.reportBrowser.setText(intersection.report)

        if intersection.solution is not None:
            self.solution = intersection.solution
            self.observations = observations
            self.report = intersection.report
            self.okButton.setEnabled(True)








