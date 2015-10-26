# coding: utf8
__author__ = 'aboeckmann'

from interface import *
import Exporter

#just for testing



group_no = u"D02"
d = Data(group_no)
d.tutor_name=u"Master und Hellfire Berghöfer"
d.sheet_no = u"01"

file_1 = File(u"./test_code/ConfigurationHelper.hpp")
file_2 = File(u"./test_code/test_transform_graph.cpp")
d.add_file(file_1)
d.add_file(file_2)

f1_comment_1 = Comment(u"test 123 hallo bla bla")
f1_comment_2 = Comment(u"aaaaaaaaaa wdew qdwq dwqd wqd frtg ftghf th fth gzhvgz h fh")
file_1.add_comment(f1_comment_1)
file_1.add_comment(f1_comment_2)

f2_comment_1 = Comment(u"bla blablab blabla blablab blabla blablab blabla blablab bla")
f2_comment_2 = Comment(u"aaaaa bbbb cccc ddd eee fff ggg")
file_2.add_comment(f2_comment_1)
file_2.add_comment(f2_comment_2)

f1_c1_marker_1 = Marker(0, 0, 3, 12)
f1_c1_marker_2 = Marker(2, 3, 0, 5)
f1_comment_1.add_marker(f1_c1_marker_1)
f1_comment_1.add_marker(f1_c1_marker_2)

f1_c2_marker_1 = Marker(21, 21, 3, 20)
f1_comment_2.add_marker(f1_c2_marker_1)

f2_c1_marker_1 = Marker(58, 58, 10, 30)
f2_comment_1.add_marker(f2_c1_marker_1)

f2_c2_marker_1 = Marker(268, 268, 0, 10)
f2_comment_2.add_marker(f2_c2_marker_1)

print("bla")

ex = Exporter.Export();
ex.export(d, "./texout/testfile.tex")

'''
class Marker:
    def __init__(self, start_line, end_line, start_col, end_col):
'''
