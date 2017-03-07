'''
Created on Oct 12, 2012

@author: Peter N. Tucker
'''

import os
import pickle
import traceback

from PySide import QtGui
from PySide.QtGui import QFileDialog

import powercad.sym_layout.plot as plot
plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'

from powercad.project_builder.newProjectDialog_ui import Ui_newProjectDialog
from powercad.project_builder.openProjectDialog_ui import Ui_openProjectDialog
from powercad.project_builder.edit_tech_lib_dir_ui import Ui_EditTechLibDirDialog
from powercad.project_builder.project import Project
from powercad.sym_layout.symbolic_layout import SymbolicLayout
from powercad.settings import LAST_ENTRIES_PATH, DEFAULT_TECH_LIB_DIR

class NewProjectDialog(QtGui.QDialog):
    """New Project Dialog"""
    def __init__(self, parent):
        """Create a new Project Dialog"""
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_newProjectDialog()
        self.ui.setupUi(self)
        
        self.parent = parent
        
        self.project_path = None
        self.symb_path = None
        
        # read in last entries and place in text boxes to save time
#        try:
#            last_entries = pickle.load(open(LAST_ENTRIES_PATH,"rb"))
#            self.project_path = last_entries[0]
#            self.symb_path = last_entries[1]
#            self.ui.txt_dir.setText(self.project_path)
#            self.ui.txt_sym_address.setText(self.symb_path)
#        except:
#            print traceback.print_exc()
#        
        self.ui.txt_name.textChanged.connect(self.check)
        self.ui.txt_dir.textChanged.connect(self.check)
        self.ui.btn_openDirectory.pressed.connect(self.open_dir)
        self.ui.btn_symbLayout.pressed.connect(self.open_symb)
        self.ui.btn_cancel.pressed.connect(self.reject)
        self.ui.btn_create.pressed.connect(self.accept)

    def check(self):
    #  ----> need to check that directory is valid path
        if (len(self.ui.txt_name.text()) == 0) or (len(self.ui.txt_dir.text()) == 0) or (len(self.ui.txt_sym_address.text()) == 0):
            self.ui.btn_create.setEnabled(False)
        else:
            self.ui.btn_create.setEnabled(True)
            
    def open_dir(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Project Directory", str(self.project_path)))
        self.ui.txt_dir.setText(directory)
        
    def open_symb(self):
        symbolic_file = QFileDialog.getOpenFileName(self, "Select Symbolic Layout",
                                                    self.ui.txt_sym_address.text(),
                                                    "SVG Files (*.svg)","SVG Files (*.svg)")
        self.ui.txt_sym_address.setText(os.path.abspath(symbolic_file[0]))
        
    def create(self):
        # save most recent entries
        last_entries = [self.ui.txt_dir.text(),self.ui.txt_sym_address.text()]
        pickle.dump(last_entries,open(LAST_ENTRIES_PATH,"wb"))
        # read in symbolic layout
        symb_layout = SymbolicLayout()
        symb_layout.load_layout(self.ui.txt_sym_address.text())
        # create project
        return Project(self.ui.txt_name.text(), self.ui.txt_dir.text(), DEFAULT_TECH_LIB_DIR, symb_layout)
        
        
class OpenProjectDialog(QtGui.QDialog):
    """Open Project Dialog"""
    def __init__(self, parent):
        """Create an Open Project Dialog"""
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_openProjectDialog()
        self.ui.setupUi(self) 
        
        self.parent = parent
        
        self.ui.txt_projectLocation.selectionChanged.connect(self.open_dir)
        self.ui.btn_selectFile.pressed.connect(self.open_dir)
        self.ui.buttonBox.accepted.connect(self.load_project)
            
    def open_dir(self):
        try:
            last_entries = pickle.load(open(LAST_ENTRIES_PATH,"rb"))
            prev_folder = last_entries[0]
            
            self.project_file = QFileDialog.getOpenFileName(self, "Select Project File",prev_folder,"Project Files (*.p)")
            self.ui.txt_projectLocation.setText(self.project_file[0])
        except:
            print traceback.print_exc()
     
    def load_project(self):
        try:
            self.parent.project = pickle.load(open(self.project_file[0],'rb'))
            
            # Add constraints field to any objects which lack it
            self.parent.project.symb_layout.add_constraints()
            
            # Check if project object contains tech_lib_dir field (if not add it)
            if not hasattr(self.parent.project, 'tech_lib_dir'):
                self.parent.project.tech_lib_dir = DEFAULT_TECH_LIB_DIR
                
            # update project directory
            self.parent.project.directory = os.path.split(os.path.split(self.project_file[0])[0])[0]
        except:
            QtGui.QMessageBox.about(self,"Project Load Error","Error loading project -- Contact developer.")
            self.reject()
            print traceback.format_exc()
            
class EditTechLibPathDialog(QtGui.QDialog):
    """Edit Tech. Lib. Path Dialog"""
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_EditTechLibDirDialog()
        self.ui.setupUi(self)
        self.parent = parent
        
        self.ui.select_dir.pressed.connect(self.select_dir)
        self.ui.buttonBox.accepted.connect(self.update_path)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.txt_library_path.setText(self.parent.project.tech_lib_dir)
        
    def select_dir(self):
        try:
            prev_dir = self.parent.project.tech_lib_dir
            tech_dir = str(QFileDialog.getExistingDirectory(self, "Select Tech. Lib. Directory", dir=prev_dir))
            self.ui.txt_library_path.setText(tech_dir)
        except:
            print traceback.print_exc()
        
    def update_path(self):
        path = self.ui.txt_library_path.text()
        # Check that new path exists
        if os.path.exists(path):
            self.parent.project.tech_lib_dir = path
            print self.parent.project.tech_lib_dir
            self.accept()
        else:
            QtGui.QMessageBox.warning(self, "Tech. Lib. Path", "Directory selected doesn't exist!")
        