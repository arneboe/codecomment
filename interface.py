__author__ = 'aboeckmann'

class Marker:
    def __init__(self, line, start_col, end_col):
        self.line = line
        self.start_col = start_col
        self.end_col = end_col

class Comment:
    def __init__(self, text="", markers=[]):
        self.text = text
        self.markers = markers

    def add_marker(self, marker):
        self.markers.append(marker)

    def set_text(self, text):
        self.text = text

    def get_text(self):
        return self.text

class File:
    def __init__(self, path="", comments=[]):
        self.path = path
        self.comments = comments

    def add_comment(self, comment):
        self.comments.append(comment)

    def set_path(self, path):
        self.path = path

    def get_comment(self, i):
        return self.comments[i]

class Data:
    def __init__(self, group_no, files = []):
        self.group_no = group_no
        self.files = files

    def add_file(self, file):
        self.files.append(file)

    def get_file_by_path(self, path):
        for f in self.files:
            if f.path == path:
                return f
        raise ValueError(path + "does not exist")