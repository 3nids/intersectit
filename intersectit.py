"""
Intersect It QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Main class
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from placeobservation import PlaceObservationOnMap
from placeintersection import placeIntersectionOnMap
from memorylayers import MemoryLayers
from mysettings import MySettings


# Initialize Qt resources from file resources.py
import resources


class IntersectIt ():
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # create rubber band to emphasis selected circles
        self.rubber = QgsRubberBand(self.iface.mapCanvas())
        # init memory layers
        memLay = MemoryLayers(iface)
        self.lineLayer  = memLay.lineLayer
        self.pointLayer = memLay.pointLayer

    def initGui(self):
        self.toolBar = self.iface.addToolBar("IntersectIt")
        self.toolBar.setObjectName("IntersectIt")
        # distance
        self.distanceAction = QAction(QIcon(":/plugins/intersectit/icons/distance.png"), "place distance", self.iface.mainWindow())
        self.distanceAction.setCheckable(True)
        QObject.connect(self.distanceAction, SIGNAL("triggered()"), self.distanceInitTool)
        self.toolBar.addAction(self.distanceAction)
        self.iface.addPluginToMenu("&Intersect It", self.distanceAction)
        # intersection
        self.intersectAction = QAction(QIcon(":/plugins/intersectit/icons/intersection.png"), "intersection", self.iface.mainWindow())
        self.intersectAction.setCheckable(True)
        QObject.connect(self.intersectAction, SIGNAL("triggered()"), self.intersectionInitTool)
        self.toolBar.addAction(self.intersectAction)
        self.iface.addPluginToMenu("&Intersect It", self.intersectAction)
        # cleaner
        self.cleanerAction = QAction(QIcon(":/plugins/intersectit/icons/cleaner.png"), "clean points and circles", self.iface.mainWindow())
        QObject.connect(self.cleanerAction, SIGNAL("triggered()"), self.cleanMemoryLayers)
        self.toolBar.addAction(self.cleanerAction)
        self.iface.addPluginToMenu("&Intersect It", self.cleanerAction)
        # settings
        self.uisettings = SettingsDialog(self.iface)
        self.uisettingsAction = QAction("settings", self.iface.mainWindow())
        QObject.connect(self.uisettingsAction, SIGNAL("triggered()"), self.uisettings.exec_)
        self.iface.addPluginToMenu("&Intersect It", self.uisettingsAction)
        # help
        self.helpAction = QAction("help", self.iface.mainWindow())
        QObject.connect(self.helpAction, SIGNAL("triggered()"), self.help)
        self.iface.addPluginToMenu("&Intersect It", self.helpAction)
          
    def help(self):
        QDesktopServices.openUrl(QUrl("https://github.com/3nids/intersectit/wiki"))

    def unload(self):
        self.iface.removePluginMenu("&Intersect It",self.distanceAction)
        self.iface.removePluginMenu("&Intersect It",self.intersectAction)
        self.iface.removePluginMenu("&Intersect It",self.uisettingsAction)
        self.iface.removePluginMenu("&Intersect It",self.cleanerAction)
        self.iface.removePluginMenu("&Intersect It",self.helpAction)
        self.iface.removeToolBarIcon(self.distanceAction)
        self.iface.removeToolBarIcon(self.intersectAction)
        self.iface.removeToolBarIcon(self.cleanerAction)
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("mapToolSet(QgsMapTool *)"), self.distanceToolChanged)
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("mapToolSet(QgsMapTool *)"), self.intersectionToolChanged)
        try:
            print "IntersecIt :: Removing temporary layer"
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
         self.iface.mapCanvas().refresh()

    def distanceInitTool(self):
        canvas = self.iface.mapCanvas()
        if self.distanceAction.isChecked() is False:
            canvas.unsetMapTool(self.placeDistancePoint)
            return
        self.distanceAction.setChecked(True)
        self.placeDistancePoint = PlaceObservationOnMap(self.iface, "distance")
        canvas.setMapTool(self.placeDistancePoint)
        QObject.connect(canvas, SIGNAL("mapToolSet(QgsMapTool *)"), self.distanceToolChanged)

    def distanceToolChanged(self, tool):
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("mapToolSet(QgsMapTool *)"), self.distanceToolChanged)
        self.distanceAction.setChecked(False)
        self.iface.mapCanvas().unsetMapTool(self.placeDistancePoint)

    def intersectionInitTool(self):
        canvas = self.iface.mapCanvas()
        if self.intersectAction.isChecked() is False:
            canvas.unsetMapTool(self.placeInitialIntersectionPoint)
            return
        self.intersectAction.setChecked(True)
        self.placeInitialIntersectionPoint = placeIntersectionOnMap(self.iface,self.rubber)
        canvas.setMapTool(self.placeInitialIntersectionPoint)
        QObject.connect(canvas, SIGNAL("mapToolSet(QgsMapTool *)"), self.intersectionToolChanged)

    def intersectionToolChanged(self, tool):
        self.rubber.reset()
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("mapToolSet(QgsMapTool *)"), self.intersectionToolChanged)
        self.intersectAction.setChecked(False)
        self.iface.mapCanvas().unsetMapTool(self.placeInitialIntersectionPoint)
