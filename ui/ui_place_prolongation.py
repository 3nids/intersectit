# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_place_prolongation.ui'
#
# Created: Tue Jun 11 07:57:19 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PlaceProlongation(object):
    def setupUi(self, PlaceProlongation):
        PlaceProlongation.setObjectName(_fromUtf8("PlaceProlongation"))
        PlaceProlongation.resize(362, 129)
        self.gridLayout = QtGui.QGridLayout(PlaceProlongation)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_4 = QtGui.QLabel(PlaceProlongation)
        self.label_4.setEnabled(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PlaceProlongation)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)
        self.label_8 = QtGui.QLabel(PlaceProlongation)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 1, 1, 1)
        self.length = QtGui.QDoubleSpinBox(PlaceProlongation)
        self.length.setDecimals(1)
        self.length.setProperty("value", 8.0)
        self.length.setObjectName(_fromUtf8("length"))
        self.gridLayout.addWidget(self.length, 1, 2, 1, 3)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 0, 1, 1, 1)
        self.precision = QtGui.QDoubleSpinBox(PlaceProlongation)
        self.precision.setEnabled(True)
        self.precision.setDecimals(4)
        self.precision.setMaximum(10.0)
        self.precision.setSingleStep(0.05)
        self.precision.setProperty("value", 0.5)
        self.precision.setObjectName(_fromUtf8("precision"))
        self.gridLayout.addWidget(self.precision, 2, 4, 1, 1)

        self.retranslateUi(PlaceProlongation)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PlaceProlongation.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PlaceProlongation.reject)
        QtCore.QMetaObject.connectSlotsByName(PlaceProlongation)

    def retranslateUi(self, PlaceProlongation):
        PlaceProlongation.setWindowTitle(QtGui.QApplication.translate("PlaceProlongation", "Place prolongation", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("PlaceProlongation", "Precision of prolongation [°]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("PlaceProlongation", "Length of drawn line", None, QtGui.QApplication.UnicodeUTF8))

