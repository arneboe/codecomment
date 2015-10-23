__author__ = 'aboeckmann'



class CommentMetaData:

    def __init__(self, color_name, item):
        self.item = item #the QListWidgetItem
        self.color_name = color_name
        
class MarkerMetaData:
    def __init__(self, marker, color_name, start_pos, end_pos): 
        self.end_pos = end_pos
        self.start_pos = start_pos
        self.color_name = color_name
        self.marker = marker