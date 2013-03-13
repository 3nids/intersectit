"""
Plain Geometry Editor
QGIS plugin

Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2013
"""
from qgistools.pluginsettings.pluginsettings import PluginSettings

from PyQt4.QtGui import QColor,QDialog

from ui.ui_settings import Ui_Settings

class MySettings(PluginSettings):
	def __init__(self,uiObject=None):
		PluginSettings.__init__(self, "intersectit",uiObject)
		self.addSetting("obs_snapping", "global", "bool", True)
		self.addSetting("intresect_result_confirm", "global", "bool", True)
		
		self.addSetting("memoryLineLayer", "project", "string", "")
		self.addSetting("memoryPointLayer", "project", "string", "")
		
		
		#self.addSetting("rubberColor", "global", "color", QColor(0,0,255),True)
		

class MySettingsDialog(QDialog, Ui_Settings):
	def __init__(self):
		QDialog.__init__(self)
