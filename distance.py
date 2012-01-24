"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for distance
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_distance import Ui_distanceDialog

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class distance(QDialog, Ui_distanceDialog ):
	def __init__(self,point):
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		
		self.x.setText("%.3f" % point.x())
		self.y.setText("%.3f" % point.y())
		
		self.distance.selectAll()
