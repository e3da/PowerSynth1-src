'''
Created on Mar 22, 2014

@author: shook

Release Build Script for PowerSynth

REMEMBER TO SET THE PYTHONPATH ENV. VARIABLE!
'''

import os
import subprocess

PYTHON_PATH = r"C:\Python27"
NUITKA_PATH = r"C:\Python27\Scripts"

MODULE_PATH = r"C:\Users\qmle\workspace\PowerCAD\src\powercad\project_builder\proj_builder.py"
OUTPUT_PATH = r"C:\Users\qmle\Desktop\PowerSynth_build"

if __name__ == '__main__':
    python_call = os.path.join(PYTHON_PATH, "python")
    nuitka_call = os.path.join(NUITKA_PATH, "nuitka")
    full_call = [python_call, nuitka_call, "--mingw", "--standalone", "--nofreeze-stdlib", MODULE_PATH]
    print full_call
    
    p = subprocess.Popen(full_call, stdout=subprocess.PIPE, cwd=OUTPUT_PATH)
    stdout, stderr = p.communicate()
    
    if stdout is not None:
        print stdout
        
    if stderr is not None:
        print stderr

