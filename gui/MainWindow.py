__author__ = 'aboeckmann'

from PyQt4.QtGui import QMainWindow, QFileDialog, QFont, QListWidgetItem
from PyQt4 import uic
from Highlighter import Highlighter
from interface import *

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


        # Set up the user interface from qt designer file
        self.ui = uic.loadUi('gui/ui_MainWindow.ui')

        #initialize the highlighter
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.ui.plainTextEditCode.setFont(font)
        self.highlighter = Highlighter(self.ui.plainTextEditCode.document())

        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionAdd_Selection.setEnabled(False)#is disbled initially because no comment is selected on startup
        self.ui.actionAdd_Comment.triggered.connect(self.addComment)

        self.ui.listWidgetFiles.currentItemChanged.connect(self.fileListSelectedItemChanged)
        self.ui.listWidgetComments.currentItemChanged.connect(self.selectedCommentChanged)
        self.ui.plainTextEditComment.textChanged.connect(self.commentTextChanged)

        self.next_comment_no = 0
        self.data = Data(0)
        self.current_comment = None #the currently selected comment, if any

        self.ui.show();

    def open(self):
        #is called when the user clicks open
        files = QFileDialog.getOpenFileNames(self, 'Open file', '.')
        for f in files:
            item = QListWidgetItem(f)
            self.ui.listWidgetFiles.addItem(item)
            self.data.add_file(File(f))
        if(len(files) > 0):
            self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))

    def fileListSelectedItemChanged(self, curr, prev):
        #is called whenever tan item is selecetd in the file list
        f = open(curr.text(), 'r')
        self.ui.plainTextEditCode.setPlainText(f.read())

    def get_current_file_path(self):
        return self.ui.listWidgetFiles.currentItem().text()

    def get_current_comment_index(self):
        return self.ui.listWidgetComments.currentRow()

    def addComment(self):
        #is called whenever the user clicks "add comment"
        initial_comment_text = "comment #" + str(self.next_comment_no)
        self.next_comment_no += 1
        file = self.data.get_file_by_path(self.get_current_file_path())
        file.add_comment(Comment(initial_comment_text))
        item = QListWidgetItem(initial_comment_text)
        self.ui.listWidgetComments.addItem(item)
        self.ui.listWidgetComments.setCurrentItem(item)

        #as soon as we have one comment, we can enable the "add selection" button
        self.ui.actionAdd_Selection.setEnabled(True)

    def selectedCommentChanged(self, curr, prev):
        #called whenever another comment is selected
        current_file = self.data.get_file_by_path(self.get_current_file_path())
        self.current_comment = current_file.get_comment(self.get_current_comment_index())
        comment_text = self.current_comment.get_text()
        self.ui.plainTextEditComment.blockSignals(True) #otherwise it would cause a textChanged() event which would overwrite the data
        self.ui.plainTextEditComment.setPlainText(comment_text)
        self.ui.plainTextEditComment.blockSignals(False)

    def commentTextChanged(self):
        new_text = self.ui.plainTextEditComment.document().toPlainText()
        self.current_comment.set_text(new_text)
