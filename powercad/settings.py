'''
Created on Feb 24, 2014

@author: anizam
'''

POWERSYNTH_RELEASE = False

if POWERSYNTH_RELEASE:
    DEFAULT_TECH_LIB_DIR = "tech_lib"
    LAST_ENTRIES_PATH = "app_data/last_entries.p"
    ELMER_BIN_PATH = "Elmer7/bin"
    GMSH_BIN_PATH = "gmsh-2.7.0"
else: # Debug
    DEFAULT_TECH_LIB_DIR = "../../../tech_lib"
    LAST_ENTRIES_PATH = "../../../export_data/app_data/last_entries.p"
    ELMER_BIN_PATH = ""
    GMSH_BIN_PATH = ""
    TEMP_DIR = r"../../../export_data/temp"