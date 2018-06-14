'''
Created on Feb 24, 2014

@author: anizam
changes made by sxm063: os.path.abspath(); added CACHED_CHAR_PATH since it changes between release/non-release modes  - Nov 23, 2015
Updated Jmain changelog - Aug 10, 2016; 
'''
import os
POWERSYNTH_RELEASE = False


if POWERSYNTH_RELEASE:  # For packaged versions
    DEFAULT_TECH_LIB_DIR = os.path.abspath("tech_lib")
    LAST_ENTRIES_PATH = os.path.abspath("export_data/app_data/last_entries.p")
    TEMP_DIR = os.path.abspath("export_data/temp")
    CACHED_CHAR_PATH = os.path.abspath("export_data/cached_thermal") # sxm063
    MATERIAL_LIB_PATH = '..//..//..//tech_lib//Material//Materials.csv'
    EXPORT_DATA_PATH = os.path.abspath("../../../export_data/")
    SETTINGS_TXT = os.path.abspath("../../../Settings.txt")
    GMSH_BIN_PATH = ''
    ELMER_BIN_PATH = ''
    ANSYS_IPY64 = ''
    FASTHENRY_FOLDER = ''
else:   # For debugging and running PowerSynth from Eclipse
    DEFAULT_TECH_LIB_DIR = os.path.abspath("../../../tech_lib")
    LAST_ENTRIES_PATH = os.path.abspath("../../../export_data/app_data/last_entries.p")
    TEMP_DIR = os.path.abspath(r"../../../export_data/temp")
    CACHED_CHAR_PATH = os.path.abspath("../../../export_data/cached_thermal") # sxm063
    MATERIAL_LIB_PATH='..//..//..//tech_lib//Material//Materials.csv'
    EXPORT_DATA_PATH=os.path.abspath("../../../export_data/")
    SETTINGS_TXT=os.path.abspath("../../../Settings.txt")

    GMSH_BIN_PATH = 'C:\PowerSynth\gmsh-2.7.0-Windows'
    ELMER_BIN_PATH = 'C:\PowerSynth\Elmer 8.2-Release/bin'
    ANSYS_IPY64 = os.path.abspath('C:\Program Files\AnsysEM\AnsysEM18.2\Win64\common\IronPython')
    FASTHENRY_FOLDER = 'C:\Users\qmle\Desktop\FastHenry'


if __name__ == '__main__':  # Module test
    print DEFAULT_TECH_LIB_DIR
    print LAST_ENTRIES_PATH
    print ELMER_BIN_PATH
    print GMSH_BIN_PATH
    print TEMP_DIR
    print CACHED_CHAR_PATH