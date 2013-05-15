
from PyQt4.QtGui import QDialog

from ..ui.ui_LSreport import Ui_LSreport


class LSreport(QDialog, Ui_LSreport ):
	def __init__(self,report):
		QDialog.__init__(self)
		self.setupUi(self)
		self.reportBrowser.setText(report)