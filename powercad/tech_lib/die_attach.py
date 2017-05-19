'''
Created on Feb 13, 2013

@author: anizam
'''

import os

from PySide.QtGui import QMessageBox

from powercad.design.library_structures import *
from powercad.general.settings.save_and_load import *
from powercad.tech_lib.test_techlib import make_sub_dir
class DieAttachPage(object):
    def __init__(self, parent):
        # Die attach root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Die_Attaches")
        
        # Set up device page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in die attach page at first (to prevent incomplete data entry)
        self.ui.SaveDieAttach.setEnabled(False)
        
        # Enable the save button in die attach page (after data entry is complete)
        self.ui.DieAttachList.currentIndexChanged.connect(self.check)
        self.ui.DieAttNameInput.textChanged.connect(self.check)
        
        # Push buttons in die attach page
        self.ui.RemoveDieAttach.clicked.connect(self.remove)
        self.ui.SaveDieAttach.clicked.connect(self.save)
        
        # Lists in die attach page
        self.ui.DieAttachList.currentIndexChanged.connect(self.load)
        
        # Project specific variable
        self.current_dattach = None
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.DieAttachList.clear()
        self.ui.DieAttachList.addItem('New Die Attach')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.DieAttachList.addItem(filename)
                
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrDieAttThermLabel, self.ui.ErrDieAttSpHeatLabel, self.ui.ErrDieAttDensityLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.DieAttThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDieAttThermLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DieAttSpHeatInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDieAttSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DieAttDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDieAttDensityLabel.setText("Error: Must be a number")
            error = True
        
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.DieAttNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Die attach name already exists. Please choose another name.')
        
        """Save all inputs""" 
        if not error:
            dattach = DieAttach(None)
            dattach.properties = MaterialProperties(str(self.ui.DieAttNameInput.text()), 
                                                    float(self.ui.DieAttThermalCondInput.text()),
                                                    float(self.ui.DieAttSpHeatInput.text()),
                                                    float(self.ui.DieAttDensityInput.text()), None, None, None)
            
            make_sub_dir(self.sub_dir)
            save_file(dattach,os.path.join(self.sub_dir, dattach.properties.name+".p"))
            self.load_page()
        else:
            print "Error Creating Die Attach"
        
    def load(self):
        if self.ui.DieAttachList.currentIndex()>0:
            filename = os.path.join(self.sub_dir, self.ui.DieAttachList.currentText())
            self.current_dattach = load_file(filename)
            
            self.ui.DieAttNameInput.setText(str(self.current_dattach.properties.name))
            self.ui.DieAttThermalCondInput.setText(str(self.current_dattach.properties.thermal_cond))
            self.ui.DieAttSpHeatInput.setText(str(self.current_dattach.properties.spec_heat_cap))
            self.ui.DieAttDensityInput.setText(str(self.current_dattach.properties.density))
        elif self.ui.DieAttachList.currentIndex() <= 0:
            self._clear_form()
            
    # Complete Entry Check            
    def check(self):
        if self.ui.DieAttachList.currentIndex()<=0:
            if not ((len(self.ui.DieAttThermalCondInput.text()) == 0) or (len(self.ui.DieAttSpHeatInput.text()) == 0) or (len(self.ui.DieAttDensityInput.text()) == 0) or (len(self.ui.DieAttNameInput.text()) == 0)):
                self.ui.SaveDieAttach.setEnabled(True)
        else:
            self.ui.SaveDieAttach.setEnabled(True)
            
                        
    def remove(self):
        if self.ui.RemoveDieAttach.clicked:
            mb = QMessageBox()
            mb.addButton('Yes', QMessageBox.AcceptRole)
            mb.addButton('No', QMessageBox.RejectRole)
            mb.setText("Do you really want to delete the die attach?")
            ret = mb.exec_()
            if ret == 0: #AcceptRole, file to be removed
                if self.ui.DieAttachList.currentIndex() >=0:
                    filename = os.path.join(self.sub_dir, self.ui.DieAttachList.currentText())
                    os.remove(filename)
                
                self.ui.DieAttachList.removeItem(self.ui.DieAttachList.currentIndex())
                self._clear_form()
            else:
                pass
        else:
            pass
        
        self.load_page()

    def _clear_form(self):
        self.ui.DieAttNameInput.clear()
        self.ui.DieAttThermalCondInput.clear()
        self.ui.DieAttSpHeatInput.clear()
        self.ui.DieAttDensityInput.clear()