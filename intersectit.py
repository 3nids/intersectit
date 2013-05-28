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


from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QAction, QIcon, QDesktopServices
from qgis.core import QgsFeature, QgsMapLayerRegistry

from core.memorylayers import MemoryLayers

from gui.mysettingsdialog import MySettingsDialog
from gui.placeobservationonmap import PlaceObservationOnMap
from gui.placeintersectiononmap import placeIntersectionOnMap

import resources


class IntersectIt ():
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        memLay = MemoryLayers(iface)
        self.lineLayer = memLay.lineLayer
        self.pointLayer = memLay.pointLayer

    def initGui(self):
        self.toolBar = self.iface.addToolBar("IntersectIt")
        self.toolBar.setObjectName("IntersectIt")
        # distance
        self.distanceAction = QAction(QIcon(":/plugins/intersectit/icons/distance.png"), "place distance", self.iface.mainWindow())
        self.distanceAction.setCheckable(True)
        self.distanceAction.triggered.connect(self.distanceInitTool)
        self.toolBar.addAction(self.distanceAction)
        self.iface.addPluginToMenu("&Intersect It", self.distanceAction)
        # intersection
        self.intersectAction = QAction(QIcon(":/plugins/intersectit/icons/intersection.png"), "intersection", self.iface.mainWindow())
        self.intersectAction.setCheckable(True)
        self.intersectAction.triggered.connect(self.intersectionInitTool)
        self.toolBar.addAction(self.intersectAction)
        self.iface.addPluginToMenu("&Intersect It", self.intersectAction)
        # cleaner
        self.cleanerAction = QAction(QIcon(":/plugins/intersectit/icons/cleaner.png"), "clean points and circles", self.iface.mainWindow())
        self.cleanerAction.triggered.connect(self.cleanMemoryLayers)
        self.toolBar.addAction(self.cleanerAction)
        self.iface.addPluginToMenu("&Intersect It", self.cleanerAction)
        # settings
        self.uisettingsAction = QAction("settings", self.iface.mainWindow())
        self.uisettingsAction.triggered.connect(self.showSettings)
        self.iface.addPluginToMenu("&Intersect It", self.uisettingsAction)
        # help
        self.helpAction = QAction("help", self.iface.mainWindow())
        self.helpAction.triggered.connect(self.help)
        self.iface.addPluginToMenu("&Intersect It", self.helpAction)
          
    def help(self):
        QDesktopServices.openUrl(QUrl("https://github.com/3nids/intersectit/wiki"))

    def unload(self):
        self.iface.removePluginMenu("&Intersect It", self.distanceAction)
        self.iface.removePluginMenu("&Intersect It", self.intersectAction)
        self.iface.removePluginMenu("&Intersect It", self.uisettingsAction)
        self.iface.removePluginMenu("&Intersect It", self.cleanerAction)
        self.iface.removePluginMenu("&Intersect It", self.helpAction)
        self.iface.removeToolBarIcon(self.distanceAction)
        self.iface.removeToolBarIcon(self.intersectAction)
        self.iface.removeToolBarIcon(self.cleanerAction)
        try:
            print "IntersecIt :: Removing temporary layer"
            QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer().id())
            QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer().id())
        except AttributeError:
            return

    def cleanMemoryLayers(self):
        for layer in (self.lineLayer(), self.pointLayer()):
            layer.selectAll()
            ids = layer.selectedFeaturesIds()
            layer.dataProvider().deleteFeatures(ids)
        self.canvas.refresh()

    def distanceInitTool(self):
        canvas = self.canvas
        if self.distanceAction.isChecked() is False:
            canvas.unsetMapTool(self.placeDistancePoint)
            return
        self.distanceAction.setChecked(True)
        self.placeDistancePoint = PlaceObservationOnMap(self.iface, "distance")
        canvas.setMapTool(self.placeDistancePoint)
        canvas.mapToolSet.connect(self.distanceToolChanged)

    def distanceToolChanged(self, tool):
        self.canvas.mapToolSet.disconnect(self.distanceToolChanged)
        self.distanceAction.setChecked(False)
        self.canvas.unsetMapTool(self.placeDistancePoint)

    def intersectionInitTool(self):
        canvas = self.canvas
        if self.intersectAction.isChecked() is False:
            canvas.unsetMapTool(self.placeInitialIntersectionPoint)
            return
        self.intersectAction.setChecked(True)
        self.placeInitialIntersectionPoint = placeIntersectionOnMap(self.iface)
        canvas.setMapTool(self.placeInitialIntersectionPoint)
        canvas.mapToolSet.connect(self.intersectionToolChanged)

    def intersectionToolChanged(self, tool):
        self.canvas.mapToolSet.disconnect(self.intersectionToolChanged)
        self.intersectAction.setChecked(False)
        self.canvas.unsetMapTool(self.placeInitialIntersectionPoint)

    def showSettings(self):
        MySettingsDialog().exec_()
