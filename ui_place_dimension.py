# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_place_dimension.ui'
#
# Created: Tue Mar 13 07:35:29 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_placeDimension(object):
    def setupUi(self, placeDimension):
        placeDimension.setObjectName(_fromUtf8("placeDimension"))
        placeDimension.resize(380, 211)
        placeDimension.setWindowTitle(QtGui.QApplication.translate("placeDimension", "IntersectIt :: place dimension", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(placeDimension)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.dimensionCombo = QtGui.QComboBox(placeDimension)
        self.dimensionCombo.setObjectName(_fromUtf8("dimensionCombo"))
        self.gridLayout.addWidget(self.dimensionCombo, 2, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(placeDimension)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 1, 1, 4)
        self.prevButton = QtGui.QToolButton(placeDimension)
        self.prevButton.setText(QtGui.QApplication.translate("placeDimension", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.prevButton.setObjectName(_fromUtf8("prevButton"))
        self.gridLayout.addWidget(self.prevButton, 2, 0, 1, 1)
        self.nextButton = QtGui.QToolButton(placeDimension)
        self.nextButton.setText(QtGui.QApplication.translate("placeDimension", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.gridLayout.addWidget(self.nextButton, 2, 5, 1, 1)
        self.label = QtGui.QLabel(placeDimension)
        self.label.setText(QtGui.QApplication.translate("placeDimension", "Radius [%]", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 5, 1, 1, 2)
        self.createBox = QtGui.QCheckBox(placeDimension)
        self.createBox.setText(QtGui.QApplication.translate("placeDimension", "Create arc for this distance", None, QtGui.QApplication.UnicodeUTF8))
        self.createBox.setChecked(True)
        self.createBox.setObjectName(_fromUtf8("createBox"))
        self.gridLayout.addWidget(self.createBox, 3, 1, 1, 4)
        self.radiusSlider = QtGui.QSlider(placeDimension)
        self.radiusSlider.setMaximum(200)
        self.radiusSlider.setPageStep(10)
        self.radiusSlider.setProperty("value", 15)
        self.radiusSlider.setSliderPosition(15)
        self.radiusSlider.setOrientation(QtCore.Qt.Horizontal)
        self.radiusSlider.setInvertedAppearance(False)
        self.radiusSlider.setInvertedControls(False)
        self.radiusSlider.setTickInterval(0)
        self.radiusSlider.setObjectName(_fromUtf8("radiusSlider"))
        self.gridLayout.addWidget(self.radiusSlider, 4, 1, 1, 4)
        self.radiusSpin = QtGui.QSpinBox(placeDimension)
        self.radiusSpin.setMaximum(200)
        self.radiusSpin.setProperty("value", 15)
        self.radiusSpin.setObjectName(_fromUtf8("radiusSpin"))
        self.gridLayout.addWidget(self.radiusSpin, 5, 3, 1, 1)
        self.reverseButton = QtGui.QPushButton(placeDimension)
        self.reverseButton.setText(QtGui.QApplication.translate("placeDimension", "Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.reverseButton.setObjectName(_fromUtf8("reverseButton"))
        self.gridLayout.addWidget(self.reverseButton, 5, 4, 1, 1)
        self.line = QtGui.QFrame(placeDimension)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 6)
        self.displayLayersBox = QtGui.QCheckBox(placeDimension)
        self.displayLayersBox.setText(QtGui.QApplication.translate("placeDimension", "Display distances", None, QtGui.QApplication.UnicodeUTF8))
        self.displayLayersBox.setChecked(True)
        self.displayLayersBox.setTristate(False)
        self.displayLayersBox.setObjectName(_fromUtf8("displayLayersBox"))
        self.gridLayout.addWidget(self.displayLayersBox, 0, 1, 1, 1)

        self.retranslateUi(placeDimension)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), placeDimension.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), placeDimension.reject)
        QtCore.QMetaObject.connectSlotsByName(placeDimension)
        placeDimension.setTabOrder(self.buttonBox, self.dimensionCombo)
        placeDimension.setTabOrder(self.dimensionCombo, self.nextButton)
        placeDimension.setTabOrder(self.nextButton, self.createBox)
        placeDimension.setTabOrder(self.createBox, self.radiusSlider)
        placeDimension.setTabOrder(self.radiusSlider, self.radiusSpin)
        placeDimension.setTabOrder(self.radiusSpin, self.reverseButton)
        placeDimension.setTabOrder(self.reverseButton, self.prevButton)

    def retranslateUi(self, placeDimension):
        pass

