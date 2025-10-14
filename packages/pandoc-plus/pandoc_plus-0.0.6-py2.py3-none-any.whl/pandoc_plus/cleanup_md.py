#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 09:39:54 2020

@author: danaukes
"""
import re
import glob

def repl(in1):
    # print(in1.group(0))
    # s = in1.group(0)+'1.'
    # print(in1.groups())
    if not not in1.groups()[0]:
        s = '\n'+in1.groups()[0]+'1.'
    else:
        s='\n1.'
    return s

def cleanup(s):
    pattern = '\n((?:  )*)([0-9]+)\.'        
    s2 = re.sub(pattern,repl,s)
    return s2    
    
def cleanup_file(file_exp):
    
    files = glob.glob(file_exp)    
    for file in files:
        with open(file,'r') as f:
            s = f.read()
        s2 = cleanup(s)
            # f.seek(0)
        with open(file,'w') as f:
            f.write(s2)
    
        
# prog = re.compile(pattern)
# result0=prog.search('\n        2.')
# result = prog.findall(s)
# s2 = re.sub(pattern,'\n\2',s)

if __name__=='__main__':
    import sys
    # input_exp = sys.argv[1]
    cleanup_file('*.md')
