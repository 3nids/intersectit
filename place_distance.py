"""
IntersectIt QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for distance
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_place_distance import Ui_place_distance

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class place_distance(QDialog, Ui_place_distance ):
	def __init__(self,point):
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		
		self.x.setText("%.3f" % point.x())
		self.y.setText("%.3f" % point.y())
		
		self.distance.selectAll()
