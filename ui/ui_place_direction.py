# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_place_direction.ui'
#
# Created: Wed Jun 12 08:27:53 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PlaceDirection(object):
    def setupUi(self, PlaceDirection):
        PlaceDirection.setObjectName(_fromUtf8("PlaceDirection"))
        PlaceDirection.resize(321, 162)
        self.gridLayout = QtGui.QGridLayout(PlaceDirection)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_4 = QtGui.QLabel(PlaceDirection)
        self.label_4.setEnabled(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PlaceDirection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 5)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 3, 1, 1)
        self.label_8 = QtGui.QLabel(PlaceDirection)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 1)
        self.precision = QtGui.QDoubleSpinBox(PlaceDirection)
        self.precision.setEnabled(True)
        self.precision.setDecimals(4)
        self.precision.setMaximum(10.0)
        self.precision.setSingleStep(0.05)
        self.precision.setProperty("value", 0.5)
        self.precision.setObjectName(_fromUtf8("precision"))
        self.gridLayout.addWidget(self.precision, 4, 4, 1, 1)
        self.label = QtGui.QLabel(PlaceDirection)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.length = QtGui.QDoubleSpinBox(PlaceDirection)
        self.length.setDecimals(1)
        self.length.setProperty("value", 8.0)
        self.length.setObjectName(_fromUtf8("length"))
        self.gridLayout.addWidget(self.length, 3, 4, 1, 1)
        self.observation = QtGui.QDoubleSpinBox(PlaceDirection)
        self.observation.setDecimals(4)
        self.observation.setMaximum(360.0)
        self.observation.setObjectName(_fromUtf8("observation"))
        self.gridLayout.addWidget(self.observation, 1, 4, 1, 1)

        self.retranslateUi(PlaceDirection)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PlaceDirection.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PlaceDirection.reject)
        QtCore.QMetaObject.connectSlotsByName(PlaceDirection)

    def retranslateUi(self, PlaceDirection):
        PlaceDirection.setWindowTitle(QtGui.QApplication.translate("PlaceDirection", "Place direction", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("PlaceDirection", "Precision of prolongation [°]", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("PlaceDirection", "Length of drawn line", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PlaceDirection", "Angle [°]", None, QtGui.QApplication.UnicodeUTF8))

