'''
Created on Feb 24, 2014

@author: anizam
changes made by sxm063: os.path.abspath(); added CACHED_CHAR_PATH since it changes between release/non-release modes  - Nov 23, 2015
'''
import os
POWERSYNTH_RELEASE = False

if POWERSYNTH_RELEASE:
    DEFAULT_TECH_LIB_DIR = os.path.abspath("tech_lib")
    LAST_ENTRIES_PATH = os.path.abspath("export_data/app_data/last_entries.p")
    ELMER_BIN_PATH = ""
    GMSH_BIN_PATH = ""
    TEMP_DIR = os.path.abspath("export_data/temp")
    CACHED_CHAR_PATH = os.path.abspath("export_data/cached_thermal") # sxm063
else: # Debug
    DEFAULT_TECH_LIB_DIR = os.path.abspath("../../../tech_lib")
    LAST_ENTRIES_PATH = os.path.abspath("../../../export_data/app_data/last_entries.p")
    #ELMER_BIN_PATH = ""
    #GMSH_BIN_PATH = ""
    ELMER_BIN_PATH = "C:\Program Files (x86)\Elmer 8.2-Release\\bin"
    GMSH_BIN_PATH = ""
    TEMP_DIR = os.path.abspath(r"../../../export_data/temp")
    CACHED_CHAR_PATH = os.path.abspath("../../../export_data/cached_thermal") # sxm063
    
if __name__ == '__main__':
    print GMSH_BIN_PATH