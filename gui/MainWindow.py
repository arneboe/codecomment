__author__ = 'aboeckmann'

from PyQt4.QtGui import QMainWindow, QFileDialog, QFont, QListWidgetItem
from PyQt4 import uic
from Highlighter import Highlighter

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


        # Set up the user interface from Designer.
        self.ui = uic.loadUi('gui/ui_MainWindow.ui')


        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.ui.plainTextEditCode.setFont(font)
        self.highlighter = Highlighter(self.ui.plainTextEditCode.document())
        self.files = []

        self.ui.actionOpen.triggered.connect(self.open)

        self.ui.listWidgetFiles.currentItemChanged.connect(self.fileListSelectedItemChanged)


        self.ui.show();

    def open(self):
        '''
        is called when the user clicks file->open
        '''
        self.files = QFileDialog.getOpenFileNames(self, 'Open file', '.')
        for f in self.files:
            item = QListWidgetItem(f)
            self.ui.listWidgetFiles.addItem(item)
        if(len(self.files) > 0):
            self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))

    def fileListSelectedItemChanged(self, curr, prev):
        print(curr.text())
        pass