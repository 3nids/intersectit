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

import math
import numpy as np
from numpy import linalg as la

from qgis.core import QgsPoint

from mysettings import MySettings


class LeastSquares():
    def __init__(self, observations, initPoint):
        settings = MySettings()
        nObs = len(observations)
        threshold = settings.value("intersecLSconvergeThreshold")
        # initial parameters
        x0 = np.array([[initPoint.x()], [initPoint.y()]])  # brackets needed to create column and not row vector
        report = "Initial position: %13.3f %13.3f\n" % (x0[0], x0[1])
        dx = np.array([[2*threshold], [2*threshold]])
        it = 0
        # global observations vector
        l = np.array([[obs["measure"]] for obs in observations])  # brackets needed to create column and not row vector
        # adjustment main loop
        while max(np.abs(dx)) > threshold:
            it += 1
            if it > settings.value("intersecLSmaxIter"):
                x0 = [None, None]
                report += "\n!!! Maximum iterations reached (%u)" % (it-1)
                break
            # init matrices
            A = []
            B = []
            Qll = []
            w = []
            for i, obs in enumerate(observations):
                if obs["type"] == "distance":
                    # distance equation: (x - xc)^2 + (y-yc)^2 - l^2 = 0 (obs: r, param: xc,yc, fixed: x,y)
                    # jacobian for parameters
                    A.append([2*x0[0][0]-2*obs["x"], 2*x0[1][0]-2*obs["y"]])
                    # jacobian for observations
                    B.append(-2*obs["measure"])
                    # stochastic model
                    Qll.append(math.pow(obs["precision"]/1000, 2))
                    # misclosure
                    # brackets needed to create column and not row vector
                    w.append([math.pow(x0[0]-obs["x"], 2) + math.pow(x0[1]-obs["y"], 2) - math.pow(obs["measure"], 2)])
            # generate matrices
            A = np.array(A)
            B = np.diag(B)
            Qll = np.diag(Qll)
            w = np.array(w)
            # weight matrix
            Pm = np.dot(B, np.dot(Qll, B.T))
            P = la.inv(Pm)
            # normal matrix
            N = np.dot(A.T, np.dot(P, A))
            u = np.dot(A.T, np.dot(P, w))
            # QR decomposition
            q, r = la.qr(N)
            p = np.dot(q.T, u)
            dx = np.dot(la.inv(r), p)
            x0 -= dx
            report += "\nCorrection %u: %10.4f %10.4f" % (it, dx[0], dx[1])
        Qxx = la.inv(N)
        p1 = math.sqrt(Qxx[0][0])
        p2 = math.sqrt(Qxx[1][1])
        # residuals -Qll*B'*(P * (A* dx(iN)+w)) !!! ToBeChecked !!!
        v = np.dot(-Qll, np.dot(B.T, np.dot(P, np.dot(A, dx) + w)))
        report += "\n"
        report += "\nSolution:\t%13.3f\t%13.3f" % (x0[0], x0[1])
        report += "\nPrecision:\t%13.3f\t%13.3f" % (p1, p2)
        report += "\n\n Observation  |       x       |       y       |   Measure   | Precision | Residual"
        report += "  \n              |  [map units]  |  [map units]  | [map units] |  [1/1000] | [1/1000]"
        for i, obs in enumerate(observations):
            report += "\n%13s | %13.3f | %13.3f | %11.3f | %9.1f | %7.1f" % (obs["type"], obs["x"], obs["y"],
                                                                             obs["measure"], obs["precision"],
                                                                             1000*v[i][0])
        sigmapos = np.dot(v.T, np.dot(P, v)) / (nObs - 2)  # vTPv / r
        if sigmapos > 1.8:
            sigmapos_comment = "precision is too optimistic"
        elif sigmapos < .5:
            sigmapos_comment = "precision is too pessimistc"
        else:
            sigmapos_comment = "precision seems realistic"
        report += "\n\nSigma a posteriori: %5.2f \t (%s)" % (sigmapos, sigmapos_comment)

        self.solution = QgsPoint(x0[0], x0[1])
        self.report = report


