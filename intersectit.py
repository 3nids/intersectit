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


from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QAction, QIcon, QDesktopServices

from core.memorylayers import MemoryLayers

from gui.mysettingsdialog import MySettingsDialog
from gui.dimensionmaptool import DimensionMapTool
from gui.distancemaptool import DistanceMapTool
from gui.directionmaptool import DirectionMapTool
from gui.intersectionmaptool import IntersectionMapTool

import resources


class IntersectIt ():
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        memLay = MemoryLayers(iface)
        self.lineLayer = memLay.lineLayer
        self.pointLayer = memLay.pointLayer

    def initGui(self):
        self.toolBar = self.iface.addToolBar("IntersectIt")
        self.toolBar.setObjectName("IntersectIt")

        # settings
        self.uisettingsAction = QAction(QIcon(":/plugins/quickfinder/icons/settings.svg"), "settings", self.iface.mainWindow())
        self.uisettingsAction.triggered.connect(self.showSettings)
        self.iface.addPluginToMenu("&Intersect It", self.uisettingsAction)
        # distance
        self.distanceAction = QAction(QIcon(":/plugins/intersectit/icons/distance.svg"), "place distance", self.iface.mainWindow())
        self.distanceAction.setCheckable(True)
        self.distanceMapTool = DistanceMapTool(self.iface)
        self.distanceMapTool.setAction(self.distanceAction)
        self.toolBar.addAction(self.distanceAction)
        self.iface.addPluginToMenu("&Intersect It", self.distanceAction)
        # prolongation
        self.directionAction = QAction(QIcon(":/plugins/intersectit/icons/prolongation.svg"), "place direction", self.iface.mainWindow())
        self.directionAction.setCheckable(True)
        self.directionMapTool = DirectionMapTool(self.iface)
        self.directionMapTool.setAction(self.directionAction)
        self.toolBar.addAction(self.directionAction)
        self.iface.addPluginToMenu("&Intersect It", self.directionAction)
        # intersection
        self.intersectionAction = QAction(QIcon(":/plugins/intersectit/icons/intersectit.svg"), "intersection", self.iface.mainWindow())
        self.intersectionAction.setCheckable(True)
        self.intersectionMapTool = IntersectionMapTool(self.iface)
        self.intersectionMapTool.setAction(self.intersectionAction)
        self.toolBar.addAction(self.intersectionAction)
        self.iface.addPluginToMenu("&Intersect It", self.intersectionAction)
        # dimension edit
        self.dimensionAction = QAction(QIcon(":/plugins/intersectit/icons/dimension.svg"), "dimension", self.iface.mainWindow())
        self.dimensionAction.setCheckable(True)
        self.dimensionMapTool = DimensionMapTool(self.iface)
        self.dimensionMapTool.setAction(self.dimensionAction)
        self.toolBar.addAction(self.dimensionAction)
        self.iface.addPluginToMenu("&Intersect It", self.dimensionAction)
        # cleaner
        self.cleanerAction = QAction(QIcon(":/plugins/intersectit/icons/eraser.svg"), "clean points and circles", self.iface.mainWindow())
        self.cleanerAction.triggered.connect(self.cleanMemoryLayers)
        self.toolBar.addAction(self.cleanerAction)
        self.iface.addPluginToMenu("&Intersect It", self.cleanerAction)
        # help
        self.helpAction = QAction(QIcon(":/plugins/quickfinder/icons/help.svg"), "help", self.iface.mainWindow())
        self.helpAction.triggered.connect(self.help)
        self.iface.addPluginToMenu("&Intersect It", self.helpAction)

        self.toolBar.actionTriggered.connect(self.setMapTool)

    def help(self):
        QDesktopServices().openUrl(QUrl("https://github.com/3nids/intersectit/wiki"))

    def unload(self):
        self.iface.removePluginMenu("&Intersect It", self.distanceAction)
        self.iface.removePluginMenu("&Intersect It", self.directionAction)
        self.iface.removePluginMenu("&Intersect It", self.intersectionAction)
        self.iface.removePluginMenu("&Intersect It", self.dimensionAction)
        self.iface.removePluginMenu("&Intersect It", self.uisettingsAction)
        self.iface.removePluginMenu("&Intersect It", self.cleanerAction)
        self.iface.removePluginMenu("&Intersect It", self.helpAction)
        self.iface.removeToolBarIcon(self.distanceAction)
        self.iface.removeToolBarIcon(self.directionAction)
        self.iface.removeToolBarIcon(self.intersectionAction)
        self.iface.removeToolBarIcon(self.dimensionAction)
        self.iface.removeToolBarIcon(self.cleanerAction)
        del self.toolBar
        try:
            print "IntersecIt :: Removing temporary layer"
            #QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer().id())
            #QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer().id())
        except AttributeError:
            return

    def setMapTool(self, action):
        if action == self.distanceAction:
            self.mapCanvas.setMapTool(self.distanceMapTool)
        if action == self.directionAction:
            self.mapCanvas.setMapTool(self.directionMapTool)
        if action == self.intersectionAction:
            self.mapCanvas.setMapTool(self.intersectionMapTool)
        if action == self.dimensionAction:
            self.mapCanvas.setMapTool(self.dimensionMapTool)

    def cleanMemoryLayers(self):
        for layer in (self.lineLayer(), self.pointLayer()):
            layer.selectAll()
            ids = layer.selectedFeaturesIds()
            layer.dataProvider().deleteFeatures(ids)
        self.mapCanvas.refresh()

    def showSettings(self):
        MySettingsDialog().exec_()
