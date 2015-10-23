# coding: utf8
'''
Created on 23.10.2015

@author: Elmar Berghöfer
'''
from interface import *



class Export(object):
    '''
    This Class handles the file export.
    '''


    def __init__(self):
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
    
    
    def load(self, path):
        fi = open(path,'r');
        retVal = fi.read().split("\n");
        fi.close(); 
        print("Length of file: "+str(len(retVal)))
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
            self.commentList.append("\\section{" + self.tex_escape(f.path) + "}");
            inhalt = self.load(f.path);
            
            # for each comment:
            for com in f.comments:
                #get code snippet
                snip_start = max(com.markers[0].start_line - 5, 0);
                snip_end = min(com.markers[0].end_line + 5, len(inhalt));
                snippet = inhalt[snip_start:snip_end + 1];
                print("Laenge: " + str(len(snippet)))
                index = min(5,snip_start);
                snippet[index] = self.tex_escape(snippet[index])
                snippet[index] = "%\colorbox{BurntOrange}{" + snippet[index] + "}%";
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
        
        #add group number:
        self.output = self.output.replace("<gruppe>", data.group_no);
        
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