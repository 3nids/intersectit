"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for placing dimension arcs
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ui_place_arc import Ui_placeArc

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class placeArc(QDialog, Ui_placeArc ):
	def __init__(self,iface,xyrp):
		self.iface = iface
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)
		QObject.connect(self , SIGNAL( "accepted()" ) , self.addArcToLayer)
		QObject.connect(self.radiusSpin,   SIGNAL("valueChanged(int)"),	self.radiusSlider, SLOT("setValue(int)"));
		QObject.connect(self.radiusSlider, SIGNAL("valueChanged(int)"),	self.radiusSpin,   SLOT("setValue(int)"));

		self.settings = QSettings("Triangulation","Triangulation")
		
		


	def addArcToLayer(self):
		print 1
