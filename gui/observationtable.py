#-----------------------------------------------------------
#
# Intersect It is a QGIS plugin to place observations (distance or orientation)
# with their corresponding precision, intersect them using a least-squares solution
# and save dimensions in a dedicated layer to produce maps.
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTableWidget, QTableWidgetItem, QAbstractItemView, QDoubleSpinBox, QItemDelegate


class ObservationTable(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(25)

        headersText = ("Type", "Observation", "Precision")
        for c, headerText in enumerate(headersText):
            self.insertColumn(c)
            item = QTableWidgetItem(headerText)
            self.setHorizontalHeaderItem(c, item)

        spinDelegate = SpinBoxDelegate()
        self.setItemDelegateForColumn(2, spinDelegate)

    def displayRows(self, observations):
        self.clearContents()
        for r in range(self.rowCount() - 1, -1, -1):
            self.removeRow(r)
        for r, obs in enumerate(observations):
            # obs is a QgsFeature, translate it to a dict
            dataDict = {"type": obs["type"], "x": obs["x"], "y": obs["y"],
                        "observation": obs["observation"], "precision": obs["precision"]}
            self.insertRow(r)
            # type
            item = QTableWidgetItem(obs["type"])
            item.setData(Qt.UserRole, dataDict)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.setItem(r, 0, item)
            # observation
            item = QTableWidgetItem("%.4f" % obs["observation"])
            item.setFlags(Qt.ItemIsEnabled)
            self.setItem(r, 1, item)
            # precision
            item = QTableWidgetItem("%.4f" % obs["precision"])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.setItem(r, 2, item)
        self.adjustSize()

    def getObservations(self):
        observations = []
        for r in range(self.rowCount()):
            item = self.item(r, 0)
            if item.checkState() == Qt.Checked:
                obs = item.data(Qt.UserRole)
                obs["precision"] = float(self.item(r, 2).text())
                observations.append(obs)
        return observations


class SpinBoxDelegate(QItemDelegate):
    def __init__(self):
        QItemDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(4)
        editor.setSingleStep(0.005)
        return editor

    def setEditorData(self, spinBox, index):
        value = index.model().data(index, Qt.EditRole)
        spinBox.setValue(float(value or 0))

    def setModelData(self, spinBox, model, index):
        #spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
