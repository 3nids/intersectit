# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_intersection.ui'
#
# Created: Tue Jun 11 16:53:47 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Intersection(object):
    def setupUi(self, Intersection):
        Intersection.setObjectName(_fromUtf8("Intersection"))
        Intersection.resize(616, 456)
        self.gridLayout_3 = QtGui.QGridLayout(Intersection)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter = QtGui.QSplitter(Intersection)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.intersecLSconvergeThreshold = QtGui.QDoubleSpinBox(self.widget)
        self.intersecLSconvergeThreshold.setDecimals(4)
        self.intersecLSconvergeThreshold.setProperty("value", 0.0005)
        self.intersecLSconvergeThreshold.setObjectName(_fromUtf8("intersecLSconvergeThreshold"))
        self.gridLayout.addWidget(self.intersecLSconvergeThreshold, 1, 1, 1, 1)
        self.observationTableWidget = ObservationTable(self.widget)
        self.observationTableWidget.setColumnCount(3)
        self.observationTableWidget.setObjectName(_fromUtf8("observationTableWidget"))
        self.observationTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.observationTableWidget, 2, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.intersecLSmaxIteration = QtGui.QSpinBox(self.widget)
        self.intersecLSmaxIteration.setProperty("value", 15)
        self.intersecLSmaxIteration.setObjectName(_fromUtf8("intersecLSmaxIteration"))
        self.gridLayout.addWidget(self.intersecLSmaxIteration, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.widget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.processButton = QtGui.QPushButton(self.widget)
        self.processButton.setCheckable(False)
        self.processButton.setObjectName(_fromUtf8("processButton"))
        self.gridLayout.addWidget(self.processButton, 3, 2, 1, 2)
        self.widget_2 = QtGui.QWidget(self.splitter)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widget_2)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.okButton = QtGui.QPushButton(self.widget_2)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.gridLayout_2.addWidget(self.okButton, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 0, 1, 1)
        self.reportBrowser = QtGui.QTextBrowser(self.widget_2)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier New"))
        font.setPointSize(10)
        self.reportBrowser.setFont(font)
        self.reportBrowser.setObjectName(_fromUtf8("reportBrowser"))
        self.gridLayout_2.addWidget(self.reportBrowser, 0, 0, 1, 2)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Intersection)
        QtCore.QMetaObject.connectSlotsByName(Intersection)

    def retranslateUi(self, Intersection):
        Intersection.setWindowTitle(QtGui.QApplication.translate("Intersection", "IntersectIt :: Least Squares report", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Intersection", "Convergence", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Intersection", "Max iteration", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Intersection", "mm", None, QtGui.QApplication.UnicodeUTF8))
        self.processButton.setText(QtGui.QApplication.translate("Intersection", "process", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("Intersection", "Use this solution", None, QtGui.QApplication.UnicodeUTF8))

from ..gui.observationtable import ObservationTable
