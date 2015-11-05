__author__ = 'aboeckmann'

from PyQt4.QtGui import QMainWindow, QFileDialog, QFont,\
                        QListWidgetItem, QTextCharFormat, QBrush, QColor, QTextCursor,\
                        QListWidget, QTextOption, QPixmap, QIcon, QPlainTextEdit, QLineEdit,\
                        QLabel, QPalette, QWidget
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
        self.ui.actionAdd_Comment.setEnabled(False)#will be enabeled as soon as  a file is added
        self.ui.actionAdd_Comment.triggered.connect(self.add_comment)
        self.ui.actionAdd_Comment_radius_0.setEnabled(False)
        self.ui.actionAdd_Comment_radius_0.triggered.connect(self.add_comment_0_radius)
        self.ui.actionRemove_Comment.setEnabled(False)
        self.ui.actionRemove_Comment.triggered.connect(self.remove_comment)
        self.ui.actionExport.triggered.connect(self.export)
        self.ui.actionExport.setEnabled(False)
        self.ui.actionSave.setEnabled(False)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionLoad.triggered.connect(self.load)

        self.ui.listWidgetFiles.currentItemChanged.connect(self.selected_file_changed)
        self.ui.listWidgetComments.currentItemChanged.connect(self.selected_comment_changed)
        self.ui.plainTextEditComment.textChanged.connect(self.comment_text_changed)
        self.ui.plainTextEditComment.setReadOnly(True)
        self.next_comment_no = 0

        self.ui.spinBoxEndLine.setEnabled(False)
        self.ui.spinBoxStartLine.setEnabled(False)
        self.ui.spinBoxStartLine.valueChanged.connect(self.start_line_changed)
        self.ui.spinBoxEndLine.valueChanged.connect(self.end_line_changed)

        self.current_comment = None #the currently selected comment, if any

        self.color_names = ["coral", "cornflowerblue", "darksalmon", "darkseagreen",
                            "greenyellow", "plum", "rosybrown", "mistyrose"]

        self.default_color = self.ui.plainTextEditCode.palette().color(QPalette.Base)

        self.save_name = "" #file name used for saving
        self.ui.show();

    def save(self):
        if len(self.save_name) <= 0:
            self.save_name = QFileDialog.getSaveFileName(self, "Save State", "save.yaml" , "Yaml files (*.yaml)")
        if len(self.save_name) > 0:
            with open(self.save_name, 'w') as f:
                f.write(dump(self.data, default_flow_style=False))
                self.ui.statusBar.showMessage("Saved " + self.save_name, 2000)


    def load(self):
        file_name = QFileDialog.getOpenFileName(parent=self, caption="Load State", filter="Yaml files (*.yaml)")
        if len(file_name) > 0:
            with open(file_name, "r") as f:
                self.data = load(f)
                for file in self.data.files:
                    self.add_file(file.path)
                    #we need to load the file content into the ui,otherwise the marker creation
                    #does not work because it needs to move the cursor inside the text.
                    #The user never acutally sees this
                    with open(file.path, 'r') as f:
                        self.ui.plainTextEditCode.setPlainText(f.read())
                    for comment in file.comments:
                        self.add_comment_to_gui(comment)
                        for marker in comment.markers:
                            color = self.commentMetaData[comment].color_name
                            self.load_marker(marker, color, comment.start_line, comment.end_line)
                if(len(self.data.files) > 0):
                    self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))


    def load_marker(self, marker, color_name, start_block, end_block):
        start_cursor = self.ui.plainTextEditCode.textCursor()
        start_cursor.setPosition(0, QTextCursor.MoveAnchor); #Moves the cursor to the beginning of the document
        #Now moves the cursor to the line "line" and in the column "index"
        start_cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, marker.line_index);
        start_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, marker.start_col);
        start_pos = start_cursor.position()

        end_cursor = self.ui.plainTextEditCode.textCursor()
        end_cursor.setPosition(0,QTextCursor.MoveAnchor); #Moves the cursor to the beginning of the document
        #Now moves the cursor to the line "line" and in the column "index"
        end_cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, marker.line_index);
        end_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, marker.end_col);
        end_pos = end_cursor.position()

        metadata = MarkerMetaData(marker, color_name, start_pos, end_pos, start_block, end_block)
        self.markerMetaData[marker] = metadata


    def reset_code_edit(self):
        #this method exists because the highlighting sometimes breaks the formatting of the
        #plain text edit, re creating it is far easier than figuring out what is wrong :D
        self.ui.plainTextEditCode.hide()
        self.ui.plainTextEditCode.setParent(None)#remove from ui
        self.ui.plainTextEditCode.deleteLater()
        self.ui.plainTextEditCode = QPlainTextEdit()
        self.ui.splitter.addWidget(self.ui.plainTextEditCode)

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
            self.data.add_file(File(str(f)))
            self.add_file(f)
        if(len(files) > 0):
            self.ui.actionLoad.setEnabled(False)#loading does not work after opening because it overwrites self.data
            self.ui.listWidgetFiles.setCurrentItem(self.ui.listWidgetFiles.item(0))

    def add_file(self, f):
        item = QListWidgetItem(f)
        self.ui.listWidgetFiles.addItem(item)


        #the following happens multiple times if you open multiple files, but who cares
        self.ui.actionAdd_Comment.setEnabled(True)
        self.ui.actionAdd_Comment_radius_0.setEnabled(True)
        self.ui.actionSave.setEnabled(True)


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

    def redraw_all_markers(self):
        self.clear_markers()
        path = self.get_current_file_path()
        f = self.data.get_file_by_path(path)
        for comment in f.comments:
            self.highlight_all_markers(comment)

    def clear_markers(self):
        cursor = self.ui.plainTextEditCode.textCursor()
        cursor.setPosition(0, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        color = QColor()
        color.setAlpha(0) #nice trick to get the original background color back
        brush = QBrush(color)
        format.setBackground(brush)
        cursor.mergeCharFormat(format)

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

    def add_comment_0_radius(self):
        #is called whenever the user clicks "add comment (radius=0)
        self.add_comment()
        #at this point there should only be one marker
        assert(len(self.current_comment.markers) == 1)
        #use line number of first marker
        line = self.current_comment.markers[0].line_index
        self.ui.spinBoxEndLine.setValue(line)
        self.ui.spinBoxStartLine.setValue(line)

    def add_comment_to_gui(self, comment):
        #is called whenever the user clicks "add comment"
        color_name = self.color_names[self.next_comment_no % len(self.color_names)]
        self.next_comment_no += 1
        comment_text_short = comment.text[0:40]
        item = QListWidgetItem(comment_text_short)

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

        #add the initial selection
        self.add_selection()

    def add_comment(self):
        if self.ui.plainTextEditCode.textCursor().hasSelection():
            current_line = self.ui.plainTextEditCode.textCursor().blockNumber()
            initial_comment_text = "comment " + str(self.next_comment_no)
            comment = Comment(initial_comment_text, [], current_line - 4, current_line + 4) #0, 0 will be changed after the selection has been added
            file = self.data.get_file_by_path(self.get_current_file_path())
            file.add_comment(comment)
            self.add_comment_to_gui(comment)

    def selected_comment_changed(self, curr, prev):
        #called whenever another comment is selected
        self.ui.plainTextEditComment.blockSignals(True) #otherwise it would cause a textChanged() event which would overwrite the data
        if not curr is None:
            self.current_comment = self.comments[curr]
            comment_text = self.current_comment.get_text()
            self.ui.plainTextEditComment.setPlainText(comment_text)
            self.ui.plainTextEditComment.setReadOnly(False)
            self.ui.spinBoxStartLine.setEnabled(True)
            self.ui.spinBoxEndLine.setEnabled(True)

            self.ui.spinBoxStartLine.blockSignals(True)
            self.ui.spinBoxStartLine.setValue(self.current_comment.start_line)
            self.ui.spinBoxStartLine.blockSignals(False)

            self.ui.spinBoxEndLine.blockSignals(True)
            self.ui.spinBoxEndLine.setValue(self.current_comment.end_line)
            self.ui.spinBoxEndLine.blockSignals(False)

            #jump to first marker
            if len(self.current_comment.markers) > 0:
                first_marker = self.current_comment.markers[0]
                line = first_marker.line_index
                cursor = QTextCursor(self.ui.plainTextEditCode.document().findBlockByNumber(line)) #only works without word wrap
                self.ui.plainTextEditCode.setTextCursor(cursor)

        else:
            self.ui.plainTextEditComment.clear()
            self.ui.plainTextEditComment.setReadOnly(True)
            self.ui.actionRemove_Comment.setEnabled(False)
            self.ui.spinBoxStartLine.setEnabled(False)
            self.ui.spinBoxEndLine.setEnabled(False)
            self.current_comment = None
        self.ui.plainTextEditComment.blockSignals(False)

    def comment_text_changed(self):
        new_text = self.ui.plainTextEditComment.document().toPlainText()
        unicoded = unicode(new_text.toUtf8(), encoding="UTF-8")
        self.current_comment.set_text(unicoded)
        self.ui.listWidgetComments.currentItem().setText(new_text[0:40])


    def highlight_marker(self, marker_meta_data, color=None):
        '''
        highlights text according to the marker and the color in the current file
        use metadata.color_name if color is None
        '''

        #first highlight the area
        cursor = self.ui.plainTextEditCode.textCursor()
        cursor.setPosition(0, QTextCursor.MoveAnchor); #Moves the cursor to the beginning of the document
        #Now moves the cursor to the start_line
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, marker_meta_data.start_block)
        #select everything till the end line
        assert(marker_meta_data.end_block >= marker_meta_data.start_block)
        move_dist = marker_meta_data.end_block - marker_meta_data.start_block
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, move_dist)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        format = QTextCharFormat()
        background_color = color
        if background_color is None:
            background_color = QColor(marker_meta_data.color_name)
        background_color.setAlpha(70)
        brush = QBrush(background_color)
        format.setBackground(brush)
        cursor.mergeCharFormat(format)

        #now highlight the marker
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

            #selections may only be one line long
            #multi line does not work well in latex
            if(end_line != start_line):
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.EndOfBlock)
                end = cursor.position()

            end_column = cursor.columnNumber()
            marker = Marker(start_line, start_column, end_column)
            self.current_comment.add_marker(marker)
            color_name = self.get_current_comment_color_name()
            metaData = MarkerMetaData(marker, color_name, start, end, self.current_comment.start_line,
                                      self.current_comment.end_line)
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

    def start_line_changed(self, newValue):
        if newValue > self.current_comment.end_line:
            newValue = self.current_comment.end_line
            self.ui.spinBoxStartLine.setValue(newValue)
        self.current_comment.start_line = newValue

        #update metadata of all markers in this comment
        #yes I know that this sucks :D
        for marker in self.current_comment.markers:
            metadata = self.markerMetaData[marker]
            metadata.start_block = newValue

        self.redraw_all_markers()


    def end_line_changed(self, newValue):
        if newValue < self.current_comment.start_line:
            newValue = self.current_comment.start_line
            self.ui.spinBoxEndLine.setValue(newValue)
        self.current_comment.end_line = newValue

        #update metadata of all markers in this comment
        #yes I know that this sucks :D
        for marker in self.current_comment.markers:
            metadata = self.markerMetaData[marker]
            metadata.end_block = newValue
        self.redraw_all_markers()