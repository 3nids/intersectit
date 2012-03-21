# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_LSreport.ui'
#
# Created: Tue Mar 20 17:31:37 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LSreport(object):
    def setupUi(self, LSreport):
        LSreport.setObjectName(_fromUtf8("LSreport"))
        LSreport.resize(903, 349)
        LSreport.setWindowTitle(QtGui.QApplication.translate("LSreport", "IntersectIt :: Least Squares report", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(LSreport)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.reportBrowser = QtGui.QTextBrowser(LSreport)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        font.setPointSize(10)
        self.reportBrowser.setFont(font)
        self.reportBrowser.setObjectName(_fromUtf8("reportBrowser"))
        self.gridLayout.addWidget(self.reportBrowser, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(LSreport)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.label = QtGui.QLabel(LSreport)
        self.label.setText(QtGui.QApplication.translate("LSreport", "Use this solution?", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.retranslateUi(LSreport)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LSreport.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LSreport.reject)
        QtCore.QMetaObject.connectSlotsByName(LSreport)

    def retranslateUi(self, LSreport):
        pass

