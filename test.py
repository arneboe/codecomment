__author__ = 'aboeckmann'
import sys
from PyQt4.QtGui import QApplication
from gui import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
sys.exit(app.exec_())
