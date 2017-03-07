'''
Created on Feb 19, 2013

@author: Andalib
'''

import os
import pickle

from PySide import QtGui
from PySide.QtGui import QMessageBox

from powercad.tech_lib.test_techlib import make_sub_dir
from powercad.design.library_structures import Baseplate, MaterialProperties

class BaseplatePage(object):
    def __init__(self, parent):
        #Baseplate root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Baseplates")
        
        #Set up baseplate page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in baseplate page at first (to prevent incomplete data entry)
        self.ui.SaveBaseplate.setEnabled(False)
                                
        # Enable the save button in baseplate page (after data entry is complete)
        self.ui.BaseplateList.currentIndexChanged.connect(self.check)
        self.ui.BaseplateNameInput.textChanged.connect(self.check)
        
        # Push buttons in baseplate page
        self.ui.RemoveBaseplate.clicked.connect(self.remove)
        self.ui.SaveBaseplate.clicked.connect(self.save)
        
        # Lists in baseplate page
        self.ui.BaseplateList.currentIndexChanged.connect(self.load)
        
        # Project specific variable
        self.current_baseplate = None
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.BaseplateList.clear()
        self.ui.BaseplateList.addItem('New Baseplate')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.BaseplateList.addItem(filename)
                    
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrBaseplateThermalCondLabel, 
                      self.ui.ErrBaseplateSpHeatLabel, 
                      self.ui.ErrBaseplateDensityLabel, 
                      self.ui.ErrBaseplateRhoLabel, 
                      self.ui.ErrBaseplateMuLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.BaseplateThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBaseplateThermalCondLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.BaseplateSpHeatInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBaseplateSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.BaseplateDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBaseplateDensityLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.BaseplateRhoInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBaseplateRhoLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.BaseplateMuInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBaseplateMuLabel.setText("Error: Must be a number")
            error = True
        
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.BaseplateNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Baseplate name already exists. Please choose another.')
                
        """Save all inputs"""     
        if not error:    
            base = Baseplate(None)
            base.properties = MaterialProperties(str(self.ui.BaseplateNameInput.text()), 
                                                 float(self.ui.BaseplateThermalCondInput.text()), 
                                                 float(self.ui.BaseplateSpHeatInput.text()), 
                                                 float(self.ui.BaseplateDensityInput.text()),
                                                 float(self.ui.BaseplateRhoInput.text()), None,
                                                 float(self.ui.BaseplateMuInput.text()))
            
            make_sub_dir(self.sub_dir)
            pickle.dump(base,open(os.path.join(self.sub_dir, base.properties.name+".p"), "wb"))
            self.load_page()
        else:
            print "Error Creating Baseplate"
            
    def load(self):
        if self.ui.BaseplateList.currentIndex() > 0:
            filename = os.path.join(self.sub_dir, self.ui.BaseplateList.currentText())
            self.current_baseplate = pickle.load(open(filename, "rb"))
            
            self.ui.BaseplateNameInput.setText(str(self.current_baseplate.properties.name))
            self.ui.BaseplateThermalCondInput.setText(str(self.current_baseplate.properties.thermal_cond))
            self.ui.BaseplateSpHeatInput.setText(str(self.current_baseplate.properties.spec_heat_cap))
            self.ui.BaseplateDensityInput.setText(str(self.current_baseplate.properties.density))
            self.ui.BaseplateRhoInput.setText(str(self.current_baseplate.properties.electrical_res))
            self.ui.BaseplateMuInput.setText(str(self.current_baseplate.properties.rel_permeab))
        elif self.ui.BaseplateList.currentIndex() <= 0:
            self._clear_form()
            
    def remove(self):
        if self.ui.RemoveBaseplate.clicked:
            if self.ui.BaseplateList.currentIndex()>0:
                mb = QMessageBox()
                mb.addButton('Yes', QMessageBox.AcceptRole)
                mb.addButton('No', QMessageBox.RejectRole)
                mb.setText("Do you really want to delete the baseplate?")
                ret = mb.exec_()
                if ret == 0: #AcceptRole, file to be removed
                    filename = os.path.join(self.sub_dir, self.ui.BaseplateList.currentText())
                    os.remove(filename)
                
                    self.ui.BaseplateList.removeItem(self.ui.BaseplateList.currentIndex())
                    self._clear_form()
                else:
                    pass
            elif self.ui.BaseplateList.currentIndex()<=0:
                pass
                
        self.load_page()

# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------
        
    def check(self):
        if self.ui.BaseplateList.currentIndex()==0:
            if not ((len(self.ui.BaseplateThermalCondInput.text()) == 0) or 
                    (len(self.ui.BaseplateSpHeatInput.text()) == 0) or 
                    (len(self.ui.BaseplateDensityInput.text()) == 0) or 
                    (len(self.ui.BaseplateRhoInput.text()) == 0) or 
                    (len(self.ui.BaseplateMuInput.text()) == 0) or 
                    (len(self.ui.BaseplateNameInput.text()) == 0)):
                self.ui.SaveBaseplate.setEnabled(True)
        else:
            self.ui.SaveBaseplate.setEnabled(True)

# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------
    
    def _clear_form(self):
        self.ui.BaseplateNameInput.clear()
        self.ui.BaseplateThermalCondInput.clear()
        self.ui.BaseplateSpHeatInput.clear()
        self.ui.BaseplateDensityInput.clear()
        self.ui.BaseplateRhoInput.clear()
        self.ui.BaseplateMuInput.clear()      
        