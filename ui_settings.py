# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_settings.ui'
#
# Created: Thu Jan 12 09:12:30 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(284, 209)
        Settings.setWindowTitle(QtGui.QApplication.translate("Settings", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(Settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Settings)
        self.label.setText(QtGui.QApplication.translate("Settings", "Tolerance", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 2, 1)
        self.tolerance = QtGui.QDoubleSpinBox(Settings)
        self.tolerance.setProperty("value", 0.6)
        self.tolerance.setObjectName(_fromUtf8("tolerance"))
        self.gridLayout.addWidget(self.tolerance, 0, 1, 2, 1)
        self.label_2 = QtGui.QLabel(Settings)
        self.label_2.setText(QtGui.QApplication.translate("Settings", "Selected circles", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.rubberStyle = QtGui.QPushButton(Settings)
        self.rubberStyle.setText(_fromUtf8(""))
        self.rubberStyle.setObjectName(_fromUtf8("rubberStyle"))
        self.gridLayout.addWidget(self.rubberStyle, 2, 3, 1, 1)
        self.label_3 = QtGui.QLabel(Settings)
        self.label_3.setText(QtGui.QApplication.translate("Settings", "Export points to", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 2)
        self.layerList = QtGui.QComboBox(Settings)
        self.layerList.setObjectName(_fromUtf8("layerList"))
        self.gridLayout.addWidget(self.layerList, 3, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.groupBox = QtGui.QGroupBox(Settings)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.mapUnits = QtGui.QRadioButton(self.groupBox)
        self.mapUnits.setText(QtGui.QApplication.translate("Settings", "map units", None, QtGui.QApplication.UnicodeUTF8))
        self.mapUnits.setChecked(True)
        self.mapUnits.setObjectName(_fromUtf8("mapUnits"))
        self.gridLayout_2.addWidget(self.mapUnits, 0, 0, 1, 1)
        self.pixels = QtGui.QRadioButton(self.groupBox)
        self.pixels.setText(QtGui.QApplication.translate("Settings", "pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.pixels.setObjectName(_fromUtf8("pixels"))
        self.gridLayout_2.addWidget(self.pixels, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 2, 1, 2)

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        pass

