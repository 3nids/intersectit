"""
Triangulation QGIS plugin
Denis Rouzaud
denis.rouzaud@gmail.com
Jan. 2012

Init dialog for distance
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_settings import Ui_Settings

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# create the dialog to connect layers
class settings(QDialog, Ui_Settings ):
	def __init__(self):
		QDialog.__init__(self)
		# Set up the user interface from Designer.
		self.setupUi(self)

		
			
