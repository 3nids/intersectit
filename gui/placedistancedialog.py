

from PyQt4.QtGui import QDialog

from ui.ui_place_distance import Ui_place_distance


class PlaceDistanceDialog(QDialog, Ui_place_distance):
    def __init__(self, point):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.x.setText("%.3f" % point.x())
        self.y.setText("%.3f" % point.y())
        self.distance.selectAll()