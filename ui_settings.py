# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_settings.ui'
#
# Created: Mon Jan 16 09:56:03 2012
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
        Settings.resize(366, 251)
        Settings.setWindowTitle(QtGui.QApplication.translate("Settings", "Triangulation :: settings", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(Settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Settings)
        self.label.setText(QtGui.QApplication.translate("Settings", "Tolerance", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 2, 1)
        self.label_2 = QtGui.QLabel(Settings)
        self.label_2.setText(QtGui.QApplication.translate("Settings", "Selected circles", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.rubberColor = QtGui.QPushButton(Settings)
        self.rubberColor.setToolTip(_fromUtf8(""))
        self.rubberColor.setText(_fromUtf8(""))
        self.rubberColor.setObjectName(_fromUtf8("rubberColor"))
        self.gridLayout.addWidget(self.rubberColor, 2, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 4)
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
        self.rubberWidth = QtGui.QDoubleSpinBox(Settings)
        self.rubberWidth.setToolTip(_fromUtf8(""))
        self.rubberWidth.setDecimals(1)
        self.rubberWidth.setSingleStep(1.0)
        self.rubberWidth.setProperty("value", 2.0)
        self.rubberWidth.setObjectName(_fromUtf8("rubberWidth"))
        self.gridLayout.addWidget(self.rubberWidth, 2, 2, 1, 1)
        self.tolerance = QtGui.QDoubleSpinBox(Settings)
        self.tolerance.setSingleStep(0.1)
        self.tolerance.setProperty("value", 0.6)
        self.tolerance.setObjectName(_fromUtf8("tolerance"))
        self.gridLayout.addWidget(self.tolerance, 0, 1, 2, 1)
        self.placeArc = QtGui.QCheckBox(Settings)
        self.placeArc.setText(QtGui.QApplication.translate("Settings", "Place dimension arc in layer", None, QtGui.QApplication.UnicodeUTF8))
        self.placeArc.setChecked(True)
        self.placeArc.setObjectName(_fromUtf8("placeArc"))
        self.gridLayout.addWidget(self.placeArc, 4, 0, 1, 2)
        self.layerCombo = QtGui.QComboBox(Settings)
        self.layerCombo.setObjectName(_fromUtf8("layerCombo"))
        self.gridLayout.addWidget(self.layerCombo, 4, 2, 1, 2)
        self.line = QtGui.QFrame(Settings)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 3, 0, 1, 4)
        self.placeLabel = QtGui.QCheckBox(Settings)
        self.placeLabel.setText(QtGui.QApplication.translate("Settings", "and place label in field", None, QtGui.QApplication.UnicodeUTF8))
        self.placeLabel.setChecked(True)
        self.placeLabel.setObjectName(_fromUtf8("placeLabel"))
        self.gridLayout.addWidget(self.placeLabel, 6, 0, 1, 2)
        self.fieldCombo = QtGui.QComboBox(Settings)
        self.fieldCombo.setObjectName(_fromUtf8("fieldCombo"))
        self.gridLayout.addWidget(self.fieldCombo, 6, 2, 1, 2)

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)
        Settings.setTabOrder(self.tolerance, self.mapUnits)
        Settings.setTabOrder(self.mapUnits, self.pixels)
        Settings.setTabOrder(self.pixels, self.rubberWidth)
        Settings.setTabOrder(self.rubberWidth, self.rubberColor)
        Settings.setTabOrder(self.rubberColor, self.buttonBox)

    def retranslateUi(self, Settings):
        pass

