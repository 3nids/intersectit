"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Observation class for distances
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import math
from datetime import datetime
from memorylayers import MemoryLayers


class Observation():
    def __init__(self, iface, obsType, point, observation, precision):
        memoryLayers = MemoryLayers(iface)
        lineLayer = memoryLayers.lineLayer()
        pointLayer = memoryLayers.pointLayer()

        # generate ID
        id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        # obsservations are stored in the lineLayer layer attributes:
        #   0: id
        #   1: observation type
        #   2: x
        #   3: y
        #   4: observation
        #   5: precision

        # save info in feature
        f = QgsFeature()
        f.setAttributes([QVariant(id),
                         QVariant(obsType),
                         QVariant(point.x()),
                         QVariant(point.y()),
                         QVariant(observation),
                         QVariant(precision)])

        # draw observation
        if obsType == "distance":
             # trace circle at distance from point
             geom = QgsGeometry.fromPolyline([QgsPoint(point.x()+observation*math.cos(math.pi/180*a),point.y()+observation*math.sin(math.pi/180*a)) for a in range(0,361,3)])
        f.setGeometry(geom)
        lineLayer.dataProvider().addFeatures([f])
        lineLayer.updateExtents()

        # draw center
        f = QgsFeature()
        f.setAttributes([QVariant(id)])
        f.setGeometry(QgsGeometry.fromPoint(point))
        pointLayer.dataProvider().addFeatures([f])
        pointLayer.updateExtents()

        # refresh canvas
        iface.mapCanvas().refresh()
        iface.mapCanvas().zoomOut()

          
#     def delete(self):
#          self.pointLayer().dataProvider().deleteFeatures([self.point_id])
#          self.lineLayer().dataProvider().deleteFeatures([self.line_id])
#          self.canvas.refresh()
          
          
