
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
        self.canvas.mapToolSet.disconnect(self.distanceToolChanged)
        self.canvas.mapToolSet.disconnect(self.intersectionToolChanged)
        try:
            print "IntersecIt :: Removing temporary layer"
            # todo
            QgsMapLayerRegistry.instance().removeMapLayer(self.lineLayer().id())
            QgsMapLayerRegistry.instance().removeMapLayer(self.pointLayer.id())
        except AttributeError:
            return

    def cleanMemoryLayers(self):
        self.rubber.reset()
        lineProv = self.lineLayer().dataProvider()
        pointProv = self.pointLayer().dataProvider()
        lineProv.select([])
        pointProv.select([])
        f = QgsFeature()
        f2del = []
        while lineProv.nextFeature(f):
            f2del.append(f.id())
        lineProv.deleteFeatures(f2del)
        f2del = []
        while pointProv.nextFeature(f):
            f2del.append(f.id())
        pointProv.deleteFeatures(f2del)
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
