# coding: utf8
'''
Created on 23.10.2015

@author: Elmar Berghöfer
'''
from interface import *
from os.path import basename



class Export(object):
    '''
    This Class handles the file export.
    '''


    def __init__(self, windowsize=4):
        '''
        Constructor
        '''
        self.fileList = [];
        self.mainTemplate = None;
        self.commentTemplate = None;
        self.commentList = [];
        self.output = "";
        print("Export");
        self.load_templates();
        self.window = windowsize; #defines the lines snipped out before and after the marker.
    
    
    def load(self, path):
        fi = open(path,'r');
        retVal = fi.read().split("\n");
        fi.close(); 
        #print("Length of file: "+str(len(retVal)))
        return retVal;
            
            
    def load_templates(self):
        '''
        This method loads the template files.
        '''
        fp = open('./tex_templates/main.tex', 'r');
        self.mainTemplate = fp.read();
        fp.close();
        fp = open('./tex_templates/comment.tex','r');
        self.commentTemplate = fp.read();
        fp.close();
        
    def export(self, data, path):
        '''
        This function performs the export to the target file:
        '''
        
        # add comments for each file in data object:
        for f in data.files:
            self.commentList.append("\\section{" + basename(self.tex_escape(f.path)) + "}");
            inhalt = self.load(f.path);
            
            # for each comment:
            for com in f.comments:
                #get code snippet
                snip_start = max(com.markers[0].start_line - self.window, 0);
                snip_end = min(com.markers[0].end_line + self.window, len(inhalt));
                snippet = inhalt[snip_start:(snip_end + 1)];
                
                index = min(self.window,com.markers[0].start_line);
                #generate new string with highlighting from to col index.
                newline = "";
                newline += snippet[index][0:com.markers[0].start_col];
                newline +="@*\colorbox{BurntOrange}{";
                newline += self.tex_escape(snippet[index][com.markers[0].start_col:com.markers[0].end_col + 1]);
                newline += "}*@" + snippet[index][com.markers[0].end_col + 1 :];
                snippet[index] = newline;
                codestr = "\n".join(snippet);
                
                #generate comment for snippet:
                comment = self.commentTemplate;
                comment = comment.replace("<startline>",str(snip_start + 1)); #line numbers start with 1 instead of 0!
                comment = comment.replace("<code>",codestr);
                comment = comment.replace("<comment>", com.text);
                comment += "\\\\";
                
                self.commentList.append(comment);
        
            #at the end clearpage for next section:
            self.commentList.append("\\clearpage");
        
        #build output string:
        self.output = self.mainTemplate.replace("<comments>", "\n".join(self.commentList));
        
        #add general fields:
        self.output = self.output.replace("<gruppe>", data.group_no);
        self.output = self.output.replace("<nummer>", data.sheet_no);
        self.output = self.output.replace("<tutor>", data.tutor_name);
        
        fo = open(path,'w');
        fo.write(self.output);
        fo.close();
        
        
    def tex_escape(self, text):
        """
            :param text: a plain text message
            :return: the message escaped to appear correctly in LaTeX
        """
        conv = {
            '\\': r'\textbackslash ',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde ',
            '^': r'\^{}',
            '<': r'\textless ',
            '>': r'\textgreater ',
            ' ': r'\ '
        }
        for char in "\\ ^{}&%$#_~<>":
            text = text.replace(char, conv.get(char,char));
        return text;