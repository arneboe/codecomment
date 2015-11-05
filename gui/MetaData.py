__author__ = 'aboeckmann'



class CommentMetaData:

    def __init__(self, color_name, item):
        self.item = item #the QListWidgetItem
        self.color_name = color_name
        
class MarkerMetaData:
    def __init__(self, marker, color_name, start_pos, end_pos, start_block, end_block):
        self.end_pos = end_pos #start cursor position of the marker
        self.start_pos = start_pos #end cursor position of the marker
        self.color_name = color_name
        self.marker = marker
        self.start_block = start_block #start of the area surrounding the selection
        self.end_block = end_block# end of the area surrounding the selection