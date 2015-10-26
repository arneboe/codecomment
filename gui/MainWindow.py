__author__ = 'aboeckmann'

from PyQt4.QtGui import QMainWindow, QFileDialog, QFont,\
                        QListWidgetItem, QTextCharFormat, QBrush, QColor, QTextCursor,\
                        QListWidget, QTextOption, QPixmap, QIcon, QPlainTextEdit, QLineEdit,\
                        QLabel, QPalette
from PyQt4 import uic
from Highlighter import Highlighter
from interface import *
from MetaData import CommentMetaData, MarkerMetaData
from yaml import load, dump
from os.path import dirname
from Exporter import Export


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


        self.data = Data(0)
        self.save_folder = "."
        self.load_yaml()

        # Set up the user interface from qt designer file
        self.ui = uic.loadUi('gui/ui_MainWindow.ui')

        #metadata about the comments, filled every time a comment is added
        self.commentMetaData = {}
        #maps from list widget items to comments
        self.comments = {}
        #maps from marker to marker meta data
        self.markerMetaData = {}

        self.reset_code_edit()

        self.labelGroup = QLabel("Group No.")
        self.ui.toolBar.addWidget(self.labelGroup)
        self.lineEditGroup = QLineEdit()
        self.lineEditGroup.setFixedWidth(60)
        self.lineEditGroup.setText(self.data.group_no)
        self.lineEditGroup.textChanged.connect(self.group_no_changed)
        self.ui.toolBar.addWidget(self.lineEditGroup)

        self.labelSheet = QLabel("Sheet No.")
        self.ui.toolBar.addWidget(self.labelSheet)
        self.lineEditSheet = QLineEdit()
        self.lineEditSheet.setFixedWidth(60)
        self.lineEditSheet.setText(self.data.sheet_no)
        self.lineEditSheet.textChanged.connect(self.sheet_no_changed)
        self.ui.toolBar.addWidget(self.lineEditSheet)

        self.labelTutor = QLabel("Tutor")
        self.ui.toolBar.addWidget(self.labelTutor)
        self.lineEditTutor = QLineEdit()
        self.lineEditTutor.setText(self.data.tutor_name)
        self.lineEditTutor.textChanged.connect(self.tutor_name_changed)
        self.ui.toolBar.addWidget(self.lineEditTutor)


        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionAdd_Selection.setEnabled(False)#is disbled initially because no comment is selected on startup
        self.ui.actionAdd_Comment.setEnabled(False)#will be enabeled as soon as  a file is added
        self.ui.actionAdd_Comment.triggered.connect(self.add_comment)
        self.ui.actionAdd_Selection.triggered.connect(self.add_selection)
        self.ui.actionRemove_Comment.setEnabled(False)
        self.ui.actionRemove_Comment.triggered.connect(self.remove_comment)
        self.ui.actionExport.triggered.connect(self.export)
        self.ui.actionExport.setEnabled(False)


        self.ui.listWidgetFiles.currentItemChanged.connect(self.selected_file_changed)
        self.ui.listWidgetComments.currentItemChanged.connect(self.selected_comment_changed)
        self.ui.plainTextEditComment.textChanged.connect(self.comment_text_changed)
        self.ui.plainTextEditComment.setReadOnly(True)
        self.next_comment_no = 0



        self.current_comment = None #the currently selected comment, if any

        self.color_names = ["coral", "cornflowerblue", "darksalmon", "darkseagreen",
                            "greenyellow", "plum", "rosybrown", "mistyrose"]

        self.default_color = self.ui.plainTextEditCode.palette().color(QPalette.Base)

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
            self.data.add_file(File(str(f)))
        if(len(files) > 0):
            self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))
            self.ui.actionAdd_Comment.setEnabled(True)


    def clear_comment_list(self):
        '''
        clear the comment list without deleting the items
        '''
        while self.ui.listWidgetComments.count() > 0:
            self.ui.listWidgetComments.takeItem(0)

    def selected_file_changed(self, curr, prev):
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

        if len(f.comments) > 0:
            self.ui.actionRemove_Comment.setEnabled(True)
        else:
            self.ui.actionRemove_Comment.setEnabled(False)


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

    def add_comment(self):
        #is called whenever the user clicks "add comment"
        color_name = self.color_names[self.next_comment_no % len(self.color_names)]
        initial_comment_text = "comment " + str(self.next_comment_no)
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

        self.ui.actionRemove_Comment.setEnabled(True)
        self.ui.actionExport.setEnabled(True)


        #as soon as we have one comment, we can enable the "add selection" button
        self.ui.actionAdd_Selection.setEnabled(True)

    def selected_comment_changed(self, curr, prev):
        #called whenever another comment is selected
        self.ui.plainTextEditComment.blockSignals(True) #otherwise it would cause a textChanged() event which would overwrite the data
        if not curr is None:
            self.current_comment = self.comments[curr]
            comment_text = self.current_comment.get_text()
            self.ui.plainTextEditComment.setPlainText(comment_text)
            self.ui.plainTextEditComment.setReadOnly(False)
            self.ui.actionAdd_Selection.setEnabled(True)
            #jump to first marker
            if len(self.current_comment.markers) > 0:
                first_marker = self.current_comment.markers[0]
                line = first_marker.start_line
                cursor = QTextCursor(self.ui.plainTextEditCode.document().findBlockByNumber(line)) #only works without word wrap
                self.ui.plainTextEditCode.setTextCursor(cursor)

        else:
            self.ui.plainTextEditComment.clear()
            self.ui.plainTextEditComment.setReadOnly(True)
            self.ui.actionAdd_Selection.setEnabled(False)
            self.ui.actionRemove_Comment.setEnabled(False)
            self.current_comment = None
        self.ui.plainTextEditComment.blockSignals(False)

    def comment_text_changed(self):
        new_text = self.ui.plainTextEditComment.document().toPlainText()
        unicoded = str(new_text.toUtf8()).decode("utf-8")
        self.current_comment.set_text(unicoded)
        self.ui.listWidgetComments.currentItem().setText(new_text[0:40])


    def highlight_marker(self, marker_meta_data, color=None):
        '''
        highlights text according to the marker and the color in the current file
        use metadata.color_name of color is Nnoe
        '''
        cursor = self.ui.plainTextEditCode.textCursor()
        cursor.setPosition(marker_meta_data.start_pos)
        cursor.setPosition(marker_meta_data.end_pos, QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        if color is None:
            color = QColor(marker_meta_data.color_name)
        brush = QBrush(color)
        format.setBackground(brush)
        cursor.mergeCharFormat(format)



    def add_selection(self):
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


    def remove_comment(self):
        if not self.current_comment is None:
            item = self.commentMetaData[self.current_comment].item
            del self.commentMetaData[self.current_comment]

            #remove from data
            file = self.data.get_file_by_path(self.get_current_file_path())
            file.comments.remove(self.current_comment)
            #remove markings from text
            for marker in self.current_comment.markers:
                meta_data = self.markerMetaData[marker]
                self.highlight_marker(meta_data, self.default_color)
                del self.markerMetaData[marker]

            #remove from gui
            self.ui.listWidgetComments.takeItem(self.ui.listWidgetComments.row(item)) #memory leak but I dont care


    def group_no_changed(self, new_value):
        self.data.group_no = unicode(new_value.toUtf8(), encoding="UTF-8")
        self.save_yaml()

    def sheet_no_changed(self, new_value):
        self.data.sheet_no = unicode(new_value.toUtf8(), encoding="UTF-8")
        self.save_yaml()

    def tutor_name_changed(self, new_value):
        #because names can contain lots of strange chars
        self.data.tutor_name = unicode(new_value.toUtf8(), encoding="UTF-8")
        self.save_yaml()

    def load_yaml(self):
        with open("settings.yaml", "r") as f:
            doc = load(f)
            self.data.group_no = doc["group"]
            self.data.sheet_no = doc["sheet"]
            self.data.tutor_name = doc["tutor"]
            self.save_folder = doc["folder"]

    def save_yaml(self):
        data = {"group" : self.data.group_no,
                "sheet" : self.data.sheet_no,
                "tutor" : self.data.tutor_name,
                "folder" : self.save_folder}

        with open('settings.yaml', 'w') as f:
            f.write(dump(data, default_flow_style=False))

    def set_save_path(self, path):
        self.save_folder = path
        self.save_yaml()

    def export(self):
        #is called whenever the user clicks on export

        output_name = "Code_Anmerkungen_" + self.data.group_no + "_" + self.data.sheet_no + ".tex"
        path = self.save_folder
        file_name = path + "/" + output_name

        save_name = QFileDialog.getSaveFileName(self, "Export to Tex", file_name, "Tex files (*.tex)");

        if save_name.length() > 0: #i.e. the user didnt cancel the dialog
            self.set_save_path(dirname(str(save_name)))
            ex = Export()
            ex.export(self.data, str(save_name))
