__author__ = 'aboeckmann'

from PyQt4.QtGui import QMainWindow, QFileDialog, QFont,\
                        QListWidgetItem, QTextCharFormat, QBrush, QColor, QTextCursor,\
                        QListWidget, QTextOption, QPixmap, QIcon, QPlainTextEdit
from PyQt4 import uic
from Highlighter import Highlighter
from interface import *
from MetaData import CommentMetaData, MarkerMetaData

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


        # Set up the user interface from qt designer file
        self.ui = uic.loadUi('gui/ui_MainWindow.ui')

        #metadata about the comments, filled every time a comment is added
        self.commentMetaData = {}
        #maps from list widget items to comments
        self.comments = {}
        #maps from marker to marker meta data
        self.markerMetaData = {}

        self.reset_code_edit()

        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionAdd_Selection.setEnabled(False)#is disbled initially because no comment is selected on startup
        self.ui.actionAdd_Comment.setEnabled(False)#will be enabeled as soon as  a file is added
        self.ui.actionAdd_Comment.triggered.connect(self.addComment)
        self.ui.actionAdd_Selection.triggered.connect(self.addSelection)

        self.ui.listWidgetFiles.currentItemChanged.connect(self.fileListSelectedItemChanged)
        self.ui.listWidgetComments.currentItemChanged.connect(self.selectedCommentChanged)
        self.ui.plainTextEditComment.textChanged.connect(self.commentTextChanged)
        self.ui.plainTextEditComment.setReadOnly(True)
        self.next_comment_no = 0
        self.data = Data(0)
        self.current_comment = None #the currently selected comment, if any

        self.color_names = ["coral", "cornflowerblue", "darksalmon", "darkseagreen",
                            "greenyellow", "plum", "rosybrown", "mistyrose"]

        self.ui.show();

    def reset_code_edit(self):
        #this method exists because the highlighting sometimes breaks the formatting of the
        #plain text edit, re creating it is far easier than figuring out what is wrong :D

        self.ui.gridLayout.removeWidget(self.ui.plainTextEditCode)
        self.ui.plainTextEditCode.hide()
        self.ui.plainTextEditCode = QPlainTextEdit()
        self.ui.gridLayout.addWidget(self.ui.plainTextEditCode, 0, 1)

        #initialize the highlighter
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.ui.plainTextEditCode.setFont(font)
        self.highlighter = Highlighter(self.ui.plainTextEditCode.document())
        #important because otherwise the mapping from block to line breaks
        self.ui.plainTextEditCode.setWordWrapMode(QTextOption.NoWrap)
        #make sure that the cursor is always in the center (improves readability when clickig on comments)
        self.ui.plainTextEditCode.setCenterOnScroll(True)
        self.ui.plainTextEditCode.setReadOnly(True)

    def open(self):
        #is called when the user clicks open
        files = QFileDialog.getOpenFileNames(self, 'Open file', '.')
        for f in files:
            item = QListWidgetItem(f)
            self.ui.listWidgetFiles.addItem(item)
            self.data.add_file(File(f))
        if(len(files) > 0):
            self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))
            self.ui.actionAdd_Comment.setEnabled(True)


    def clear_comment_list(self):
        '''
        clear the comment list without deleting the items
        '''
        while self.ui.listWidgetComments.count() > 0:
            self.ui.listWidgetComments.takeItem(0)

    def fileListSelectedItemChanged(self, curr, prev):
        #is called whenever an item is selecetd in the file list
        f = open(curr.text(), 'r')

        self.reset_code_edit()
        self.ui.plainTextEditCode.setPlainText(f.read())
        # update comment list if file changed
        f = self.data.get_file_by_path(curr.text())
        self.clear_comment_list()
        for comment in f.comments:
            item = self.commentMetaData[comment].item
            self.ui.listWidgetComments.addItem(item)
            self.ui.listWidgetComments.setCurrentItem(item)
            self.highlight_all_markers(comment)


    def highlight_all_markers(self, comment):
        '''
        applies all markers of the specified comment to the text
        '''
        for marker in comment.markers:
            meta_data = self.markerMetaData[marker]
            self.highlight_marker(meta_data)

    def get_current_file_path(self):
        return self.ui.listWidgetFiles.currentItem().text()

    def get_current_comment_color_name(self):
        item = self.ui.listWidgetComments.currentItem()
        comment = self.comments[item]
        return self.commentMetaData[comment].color_name

    def addComment(self):
        #is called whenever the user clicks "add comment"
        color_name = self.color_names[self.next_comment_no % len(self.color_names)]
        initial_comment_text = "comment #" + str(self.next_comment_no)
        file = self.data.get_file_by_path(self.get_current_file_path())
        comment = Comment(initial_comment_text, [])
        file.add_comment(comment)
        self.next_comment_no += 1

        item = QListWidgetItem(initial_comment_text)

        #has to happen before listWidgetComments.addItem
        #because event handlers need to access the meta data
        self.commentMetaData[comment] = CommentMetaData(color_name, item)
        self.comments[item] = comment

        self.ui.listWidgetComments.addItem(item)
        self.ui.listWidgetComments.setCurrentItem(item)
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(color_name))
        icon = QIcon(pixmap)
        item.setIcon(icon)


        #as soon as we have one comment, we can enable the "add selection" button
        self.ui.actionAdd_Selection.setEnabled(True)

    def selectedCommentChanged(self, curr, prev):
        #called whenever another comment is selected
        self.ui.plainTextEditComment.blockSignals(True) #otherwise it would cause a textChanged() event which would overwrite the data
        if not curr is None:
            self.current_comment = self.comments[curr]
            comment_text = self.current_comment.get_text()
            self.ui.plainTextEditComment.setPlainText(comment_text)
            self.ui.plainTextEditComment.setReadOnly(False)
            #jump to first marker
            if len(self.current_comment.markers) > 0:
                first_marker = self.current_comment.markers[0]
                line = first_marker.start_line
                cursor = QTextCursor(self.ui.plainTextEditCode.document().findBlockByNumber(line)) #only works without word wrap
                self.ui.plainTextEditCode.setTextCursor(cursor)

        else:
            self.ui.plainTextEditComment.clear()
            self.ui.plainTextEditComment.setReadOnly(True)
            self.current_comment = None
        self.ui.plainTextEditComment.blockSignals(False)

    def commentTextChanged(self):
        new_text = self.ui.plainTextEditComment.document().toPlainText()
        self.current_comment.set_text(new_text)
        self.ui.listWidgetComments.currentItem().setText(new_text[0:40])


    def highlight_marker(self, marker_meta_data):
        '''
        highlights text according to the marker and the color in the current file
        '''
        cursor = self.ui.plainTextEditCode.textCursor()
        cursor.setPosition(marker_meta_data.start_pos)
        cursor.setPosition(marker_meta_data.end_pos, QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        brush = QBrush(QColor(marker_meta_data.color_name))
        format.setBackground(brush)
        cursor.mergeCharFormat(format)



    def addSelection(self):
        #is called whenever the user wants to add a new selection
        cursor = self.ui.plainTextEditCode.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.clearSelection()
            cursor.setPosition(start)
            start_line = cursor.blockNumber()
            start_column = cursor.columnNumber()
            cursor.setPosition(end)
            end_line = cursor.blockNumber()
            end_column = cursor.columnNumber()
            marker = Marker(start_line, end_line, start_column, end_column)
            self.current_comment.add_marker(marker)
            color_name = self.get_current_comment_color_name()
            metaData = MarkerMetaData(marker, color_name, start, end)
            self.markerMetaData[marker] = metaData
            self.highlight_marker(metaData)

            #clear selection and reset color
            cursor.clearSelection()
            self.ui.plainTextEditCode.setTextCursor(cursor)



