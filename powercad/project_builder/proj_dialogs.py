'''
Created on Oct 12, 2012

@author: Peter N. Tucker
'''

import os
import pickle
import traceback
from shutil import copyfile

from PySide import QtGui
from PySide.QtGui import QFileDialog

import powercad.sym_layout.plot as plot
plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'

from powercad.project_builder.newProjectDialog_ui import Ui_newProjectDialog
from powercad.project_builder.openProjectDialog_ui import Ui_openProjectDialog
from powercad.project_builder.edit_tech_lib_dir_ui import Ui_EditTechLibDirDialog
from powercad.project_builder.Solidworkversioncheck import Ui_checkversion_dialog
from powercad.project_builder.project import Project
from powercad.sym_layout.symbolic_layout import SymbolicLayout
from powercad.settings import LAST_ENTRIES_PATH, DEFAULT_TECH_LIB_DIR
from powercad.spice_import import Netlist_SVG_converter


class NewProjectDialog(QtGui.QDialog):
    """New Project Dialog"""
    def __init__(self, parent): #initializes the new project dialog box elements to default values before the dialog box is displayed to the user
        """Create a new Project Dialog"""
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_newProjectDialog()
        self.ui.setupUi(self)
        
        self.parent = parent
        
        self.project_path = None
        self.symb_path = None
        
        self.filetype = None
        self.net_to_svg_file = None
        
        self.adv_netlist_args = {}
        
        # read in last entries and place in text boxes to save time
#        try:
#            last_entries = pickle.load(open(LAST_ENTRIES_PATH,"rb"))
#            self.project_path = last_entries[0]
#            self.symb_path = last_entries[1]
#            self.ui.txt_dir.setText(self.project_path)
#            self.ui.txt_symbnet_address.setText(self.symb_path)
#        except:
#            print traceback.print_exc()
#       
        # Disable all buttons
        self.ui.btn_symbnetfile.setEnabled(False)
        self.ui.txt_symbnet_address.setEnabled(False)
        self.ui.groupBox_advnetlist.setEnabled(False)
        self.ui.txt_dir.setEnabled(False)
        
        # Check user input as it is entered
        self.ui.txt_name.textChanged.connect(self.check)
        self.ui.txt_dir.textChanged.connect(self.check)
        self.ui.txt_symbnet_address.textChanged.connect(self.check)
        self.ui.txt_positive_source.textChanged.connect(self.check)
        self.ui.txt_negative_source.textChanged.connect(self.check)
        self.ui.txt_output.textChanged.connect(self.check)
        self.ui.dropdown_filetype.currentIndexChanged.connect(self.check)
        
        self.ui.btn_openDirectory.pressed.connect(self.open_dir)   
        self.ui.btn_symbnetfile.pressed.connect(self.open_symbnet_file)
        self.ui.dropdown_filetype.currentIndexChanged.connect(self.select_filetype)    
        
        self.ui.btn_cancel.pressed.connect(self.reject)
        self.ui.btn_create.pressed.connect(self.accept)

    def check(self):
        # Check for valid netlist details
        valid_netlist_details = False
        if self.filetype == 'netlist' and self.ui.txt_symbnet_address.text() != '': # if netlist filetype is chosen and the "select file" text area is not empty, 
            valid_netlist_details = self.check_netlist_details() # check netlist details entered.
        
        # Enable/Disable 'Create Project' button
        # Disable if either of the three text areas is empty: Project Name, Project Directory, Select file
        if (len(self.ui.txt_name.text()) == 0) or (len(self.ui.txt_dir.text()) == 0) or (len(self.ui.txt_symbnet_address.text()) == 0):
            self.ui.btn_create.setEnabled(False)
        # Disable if either of the three node names are not provided when filetype has been chosen as netlist
        elif self.filetype == 'netlist' and ((len(self.ui.txt_positive_source.text()) == 0) or (len(self.ui.txt_negative_source.text()) == 0) or (len(self.ui.txt_output.text()) == 0)):
            self.ui.btn_create.setEnabled(False)
        # Disable if netlist details are not valid (as checked by the check_netlist_details() called above, when netlist has been chosen as the filetype
        elif self.filetype == 'netlist' and not valid_netlist_details:
            self.ui.btn_create.setEnabled(False)
        # Enable if none of the above is true, i.e. no issues are detected with input data.
        else:
            self.ui.btn_create.setEnabled(True)
    
    def check_netlist_details(self):    
        valid_netlist_dtls = False
        invalid_pos_src = True
        invalid_neg_src = True
        invalid_output_node = True
        
        # Check if positive src, negative src, and output node names exist in the netlist file. If yes, mark invalid flag as false. If not, keep invalid flag as true. 
        if self.ui.txt_positive_source.text() in open(self.ui.txt_symbnet_address.text()).read(): # check if the positive source node is included in the netlist file.
            invalid_pos_src = False
        if self.ui.txt_negative_source.text() in open(self.ui.txt_symbnet_address.text()).read(): # check if the negative source node is included in the netlist file.
            invalid_neg_src = False
        if self.ui.txt_output.text() in open(self.ui.txt_symbnet_address.text()).read(): # check if the output node is included in the netlist file.
            invalid_output_node = False
        
        if invalid_pos_src:
            self.ui.err_pos_src.setText('Source not found in netlist')
        elif self.ui.txt_positive_source.text() != '' and (self.ui.txt_positive_source.text() == self.ui.txt_negative_source.text() 
                                                           or self.ui.txt_positive_source.text() == self.ui.txt_output.text()):
            self.ui.err_pos_src.setText('Source name may only be used once')
        else:
            self.ui.err_pos_src.setText(' ')
            
        if invalid_neg_src:
            self.ui.err_neg_src.setText('Source not found in netlist')
        elif self.ui.txt_negative_source.text() != '' and (self.ui.txt_negative_source.text() == self.ui.txt_positive_source.text() 
                                                           or self.ui.txt_negative_source.text() == self.ui.txt_output.text()):
            self.ui.err_neg_src.setText('Source name may only be used once')
        else:
            self.ui.err_neg_src.setText(' ') 
            
        if invalid_output_node:
            self.ui.err_output_node.setText('Node not found in netlist')
        elif self.ui.txt_output.text() != '' and (self.ui.txt_output.text() == self.ui.txt_positive_source.text() 
                                                  or self.ui.txt_output.text() == self.ui.txt_negative_source.text()):
            self.ui.err_output_node.setText('Node name may only be used once')
        else:
            self.ui.err_output_node.setText(' ')
        
        if not (invalid_pos_src or invalid_neg_src or invalid_output_node):
            valid_netlist_dtls = True
        return valid_netlist_dtls
            
    def open_dir(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Project Directory", str(self.project_path)))
        if os.path.isdir(directory):
            self.ui.txt_dir.setText(directory)
    
    def select_filetype(self):
        self.ui.txt_symbnet_address.clear()                     # Clear "Open file" text area.
        if self.ui.dropdown_filetype.currentIndex() > 0:        # If something other than the default is selected from the filetype dropdown menu, 
            self.ui.btn_symbnetfile.setEnabled(True)            # Enable the "Open file" button.
            if self.ui.dropdown_filetype.currentIndex() == 1:   # If filetype has been selected as 'svg',
                self.filetype = 'svg'                           # set filetype to "svg", and 
                self.ui.groupBox_advnetlist.setEnabled(False)   # disable the "Netlist Details" section.
            elif self.ui.dropdown_filetype.currentIndex() == 2: # If filetype has been selected as 'netlist',
                self.filetype = 'netlist'                       # set filetype to "netlist", and 
                self.ui.groupBox_advnetlist.setEnabled(True)    # enable the "Netlist Details" section.
        else:                                                   # If nothing other than the default has been selected from the filetype dropdown menu,
            self.filetype = None                                # set filetype to "None",  
            self.ui.btn_symbnetfile.setEnabled(False)           # disable the "Open File" button, and 
            self.ui.groupBox_advnetlist.setEnabled(False)       # disable the "Netlist Details" section.
        
    def open_symbnet_file(self): # opens file browser and saves the selected file and its filepath (if file extension is correct).
        if self.filetype == 'svg':
            symbnet_file = QFileDialog.getOpenFileName(self, "Select Symbolic Layout", self.ui.txt_symbnet_address.text(), "SVG Files (*.svg)")
            file_name, file_extension = os.path.splitext(symbnet_file[0])
            if file_extension == '.svg':
                self.ui.txt_symbnet_address.setText(os.path.abspath(symbnet_file[0]))
                
        elif self.filetype == 'netlist':
            symbnet_file = QFileDialog.getOpenFileName(self, "Select Netlist File", self.ui.txt_symbnet_address.text(), "Netlist Files (*.net *.txt)")
            print "symbnet file:", symbnet_file
            file_name, file_extension = os.path.splitext(symbnet_file[0])
            if file_extension == '.txt' or file_extension == '.net':
                self.ui.txt_symbnet_address.setText(os.path.abspath(symbnet_file[0]))
    
    # Create an svg xml file from the netlist text file provided, and return the filepath of the svg file.
    def convert_netlist(self): 
        # Prepares for conversion
        # Converts datatype of positive, negative, and output nodes from object attributes into strings
        netlist_file_name, netlist_file_extension = os.path.splitext(self.ui.txt_symbnet_address.text()) # separates the file path and file name combination from the file extension (.txt or .net)        
        converter = Netlist_SVG_converter.Converter(self.ui.txt_symbnet_address.text(), netlist_file_name) # initializes the converter object with the specific source's file path and file name 
        # Converts from netlist to svg
        symbnet_file = converter.convert(vp=str(self.ui.txt_positive_source.text()), # the positive source node mentioned by the user is converted to string type and saved in variable vp
                                         vn=str(self.ui.txt_negative_source.text()), # the negative source node mentioned by the user is converted to string type and saved in variable vn
                                         output_node=str(self.ui.txt_output.text())) # the output node mentioned by the user is converted to string type and saved in variable output_node 
        
        return os.path.abspath(symbnet_file[0]) # Shilpi - return the converted file  

    def create(self):
        # Save most recent entries
        last_entries = [self.ui.txt_dir.text(),self.ui.txt_symbnet_address.text()]
        print "last_entries:", last_entries
        pickle.dump(last_entries,open(LAST_ENTRIES_PATH,"wb"))
        print "pickle dumped."
        
        # If netlist, create symbolic layout
        if self.filetype == 'netlist':
            self.net_to_svg_file = self.convert_netlist() # Shilpi- save the newly created svg file.
            print "netlist converted to svg."
        print "net_to_svg_file= ", self.net_to_svg_file
             
        # Read in symbolic layout
        symb_layout = SymbolicLayout()
        if self.filetype == 'netlist':
            symb_layout.load_layout(self.net_to_svg_file)  # Shilpi- convert the svg that was obtained from netlist to a symbolic layout.
        elif self.filetype == 'svg':
            symb_layout.load_layout(self.ui.txt_symbnet_address.text()) # Shilpi- convert the original svg to a symbolic layout.
        print "symbolic layout created."      
        '''        
        # sxm - copy the source (svg/net file) to the project directory
        copyfile(self.ui.txt_symbnet_address.text(), os.path.join(self.ui.txt_dir.text(), "source_file"))
        print "source file copied."
        '''
        # Create project
        return Project(self.ui.txt_name.text(), self.ui.txt_dir.text(), DEFAULT_TECH_LIB_DIR, symb_layout)
        
        
class OpenProjectDialog(QtGui.QDialog): #done
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
            
    def open_dir(self): # done - responds to button click by opening a file browser where the project directory can be selected
        try:
            last_entries = pickle.load(open(LAST_ENTRIES_PATH,"rb"))
            prev_folder = last_entries[0]
            
            self.project_file = QFileDialog.getOpenFileName(self, "Select Project File",prev_folder,"Project Files (*.p)")
            self.ui.txt_projectLocation.setText(self.project_file[0])
        except:
            print traceback.print_exc()
     
    def load_project(self): # done - loads the project selected into the main view
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

class SolidworkVersionCheckDialog(QtGui.QDialog):       

    def __init__(self,parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_checkversion_dialog()
        self.ui.setupUi(self)
        self.parent = parent 
        self.ui.buttonBox.accepted.connect(self.version_output)

    def version_output(self):
        return self.ui.SolidworkVersion.text()    

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