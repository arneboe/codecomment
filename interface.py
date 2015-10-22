__author__ = 'aboeckmann'

class Marker:
    def __init__(self, start_line, end_line, start_col, end_col):
        self.start_line = start_line
        self.end_line = end_line
        self.start_col = start_col
        self.end_col = end_col

class Comment:
    def __init__(self, text="", markers=None):
        self.text = text
        if markers is None:
            self.markers = []
        else:
            self.markers = markers

    def add_marker(self, marker):
        self.markers.append(marker)

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

class File:
    def __init__(self, path="", comments=None):
        self.path = path
        if(comments is None):
            self.comments = []
        else:
            self.comments = comments

    def add_comment(self, comment):
        self.comments.append(comment)

    def set_path(self, path):
        self.path = path

    def get_comment(self, i):
        return self.comments[i]

class Data:
    def __init__(self, group_no, files = None):
        self.group_no = group_no
        if(files is None):
            self.files = []
        else:
            self.files = files

    def add_file(self, path):
        self.files.append(path)

    def get_file_by_path(self, path):
        for f in self.files:
            if f.path == path:
                return f
        raise ValueError(path + "does not exist")