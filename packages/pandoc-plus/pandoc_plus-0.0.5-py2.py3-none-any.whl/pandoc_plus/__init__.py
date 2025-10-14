# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:21:15 2020

@author: danaukes
"""
import os
import sys

if hasattr(sys, 'frozen'):
    localpath = os.path.normpath(os.path.join(os.path.dirname(sys.executable),''))
else:
    localpath = sys.modules['pandoc_plus'].__path__[0]

support_dir = os.path.normpath(os.path.join(localpath, 'support'))
