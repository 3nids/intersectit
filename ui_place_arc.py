# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_place_arc.ui'
#
# Created: Tue Jan 17 17:24:30 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_placeArc(object):
    def setupUi(self, placeArc):
        placeArc.setObjectName(_fromUtf8("placeArc"))
        placeArc.resize(379, 174)
        placeArc.setWindowTitle(QtGui.QApplication.translate("placeArc", "Triangulation :: place arc", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(placeArc)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.arcCombo = QtGui.QComboBox(placeArc)
        self.arcCombo.setObjectName(_fromUtf8("arcCombo"))
        self.gridLayout.addWidget(self.arcCombo, 0, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(placeArc)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 4)
        self.prevButton = QtGui.QToolButton(placeArc)
        self.prevButton.setText(QtGui.QApplication.translate("placeArc", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.prevButton.setObjectName(_fromUtf8("prevButton"))
        self.gridLayout.addWidget(self.prevButton, 0, 0, 1, 1)
        self.nextButton = QtGui.QToolButton(placeArc)
        self.nextButton.setText(QtGui.QApplication.translate("placeArc", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.gridLayout.addWidget(self.nextButton, 0, 5, 1, 1)
        self.label = QtGui.QLabel(placeArc)
        self.label.setText(QtGui.QApplication.translate("placeArc", "Radius [%]", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 1, 1, 2)
        self.createBox = QtGui.QCheckBox(placeArc)
        self.createBox.setText(QtGui.QApplication.translate("placeArc", "Create arc for this distance", None, QtGui.QApplication.UnicodeUTF8))
        self.createBox.setChecked(True)
        self.createBox.setObjectName(_fromUtf8("createBox"))
        self.gridLayout.addWidget(self.createBox, 1, 1, 1, 4)
        self.radiusSlider = QtGui.QSlider(placeArc)
        self.radiusSlider.setMaximum(200)
        self.radiusSlider.setPageStep(10)
        self.radiusSlider.setProperty("value", 15)
        self.radiusSlider.setSliderPosition(15)
        self.radiusSlider.setOrientation(QtCore.Qt.Horizontal)
        self.radiusSlider.setInvertedAppearance(False)
        self.radiusSlider.setInvertedControls(False)
        self.radiusSlider.setTickInterval(0)
        self.radiusSlider.setObjectName(_fromUtf8("radiusSlider"))
        self.gridLayout.addWidget(self.radiusSlider, 2, 1, 1, 4)
        self.radiusSpin = QtGui.QSpinBox(placeArc)
        self.radiusSpin.setMaximum(200)
        self.radiusSpin.setProperty("value", 15)
        self.radiusSpin.setObjectName(_fromUtf8("radiusSpin"))
        self.gridLayout.addWidget(self.radiusSpin, 3, 3, 1, 1)
        self.reverseButton = QtGui.QPushButton(placeArc)
        self.reverseButton.setText(QtGui.QApplication.translate("placeArc", "Reverse", None, QtGui.QApplication.UnicodeUTF8))
        self.reverseButton.setObjectName(_fromUtf8("reverseButton"))
        self.gridLayout.addWidget(self.reverseButton, 3, 4, 1, 1)

        self.retranslateUi(placeArc)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), placeArc.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), placeArc.reject)
        QtCore.QMetaObject.connectSlotsByName(placeArc)
        placeArc.setTabOrder(self.buttonBox, self.arcCombo)
        placeArc.setTabOrder(self.arcCombo, self.nextButton)
        placeArc.setTabOrder(self.nextButton, self.createBox)
        placeArc.setTabOrder(self.createBox, self.radiusSlider)
        placeArc.setTabOrder(self.radiusSlider, self.radiusSpin)
        placeArc.setTabOrder(self.radiusSpin, self.reverseButton)
        placeArc.setTabOrder(self.reverseButton, self.prevButton)

    def retranslateUi(self, placeArc):
        pass

