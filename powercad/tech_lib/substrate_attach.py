'''
Created on Feb 19, 2013

@author: Andalib
'''

import os
import pickle

from PySide import QtGui
from PySide.QtGui import QMessageBox

from powercad.tech_lib.test_techlib import make_sub_dir
from powercad.design.library_structures import *
from powercad.save_and_load import *
class SubAttachPage(object):
    def __init__(self, parent):
        # Substrate attach root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Substrate_Attaches")
        
        #Set up substrate attach page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in substrate attach page at first (to prevent incomplete data entry)
        self.ui.SaveSubAttach.setEnabled(False)
        
        # Enable the save button in substrate attach page (after data entry is complete)
        self.ui.SubAttachList.currentIndexChanged.connect(self.check)
        self.ui.SubAttachNameInput.textChanged.connect(self.check)
        
        # Push buttons for substrate attach page 
        self.ui.RemoveSubAttach.clicked.connect(self.remove)
        self.ui.SaveSubAttach.clicked.connect(self.save)
        
        # Lists in substrate attach page
        self.ui.SubAttachList.currentIndexChanged.connect(self.load)
        
        # Project specific variable
        self.current_subattach = None
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.SubAttachList.clear()
        self.ui.SubAttachList.addItem('New Substrate Attach')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.SubAttachList.addItem(filename)
 
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrSubAttachThermalCondLabel, self.ui.ErrSubAttachSpHeatLabel, self.ui.ErrSubAttachDensityLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.SubAttachThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubAttachThermalCondLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubAttachSpHeatCapInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubAttachSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubAttachDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubAttachDensityLabel.setText("Error: Must be a number")
            error = True
            
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.SubAttachNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Substrate attach name already exists. Please choose another name.')
                
        """Save all inputs"""       
        if not error:
            sub_attach = SubstrateAttach(None)
            sub_attach.properties = MaterialProperties(str(self.ui.SubAttachNameInput.text()), 
                                                       float(self.ui.SubAttachThermalCondInput.text()), 
                                                       float(self.ui.SubAttachSpHeatCapInput.text()), 
                                                       float(self.ui.SubAttachDensityInput.text()), None, None, None) 
            
            make_sub_dir(self.sub_dir)
            save_file(sub_attach,os.path.join(self.sub_dir, sub_attach.properties.name+".p"))
            self.load_page()
        else:
            print "Error Creating Substrate Attach"
        
    def load(self):
        if self.ui.SubAttachList.currentIndex() > 0:
            filename = os.path.join(self.sub_dir, self.ui.SubAttachList.currentText())
            self.current_subattach = load_file(filename)
            
            self.ui.SubAttachNameInput.setText(str(self.current_subattach.properties.name))
            self.ui.SubAttachThermalCondInput.setText(str(self.current_subattach.properties.thermal_cond))
            self.ui.SubAttachSpHeatCapInput.setText(str(self.current_subattach.properties.spec_heat_cap))
            self.ui.SubAttachDensityInput.setText(str(self.current_subattach.properties.density))
        elif self.ui.SubAttachList.currentIndex() <= 0:
            self._clear_form()
    
    def remove(self):
        if self.ui.RemoveSubAttach.clicked:
            if self.ui.SubAttachList.currentIndex()>0:
                mb = QMessageBox()
                mb.addButton('Yes', QMessageBox.AcceptRole)
                mb.addButton('No', QMessageBox.RejectRole)
                mb.setText("Do you really want to delete the substrate attach?")
                ret = mb.exec_()
                if ret == 0: #AcceptRole, file to be removed
                    if self.ui.SubAttachList.currentIndex() >=0:
                        filename = os.path.join(self.sub_dir, self.ui.SubAttachList.currentText())
                        os.remove(filename)
                    self.ui.SubAttachList.removeItem(self.ui.SubAttachList.currentIndex())
                    self._clear_form()
                else:
                    pass
            elif self.ui.SubAttachList.currentIndex()<=0:
                pass
        self.load_page()

# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------
    
    def check(self):
        if self.ui.SubAttachList.currentIndex()<=0:
            if not ((len(self.ui.SubAttachThermalCondInput.text()) == 0) or (len(self.ui.SubAttachSpHeatCapInput.text()) == 0) or (len(self.ui.SubAttachDensityInput.text()) == 0) or (len(self.ui.SubAttachNameInput.text()) == 0)):
                self.ui.SaveSubAttach.setEnabled(True)
        else:
            self.ui.SaveSubAttach.setEnabled(True)
            
# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------
    
    def _clear_form(self):
        self.ui.SubAttachNameInput.clear()
        self.ui.SubAttachThermalCondInput.clear()
        self.ui.SubAttachSpHeatCapInput.clear()
        self.ui.SubAttachDensityInput.clear()
        