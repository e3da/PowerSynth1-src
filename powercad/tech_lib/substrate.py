'''
Created on Feb 18, 2013

@author: anizam
'''

import os

from PySide.QtGui import QMessageBox

from powercad.design.library_structures import *
from powercad.general.settings.save_and_load import *
from powercad.tech_lib.test_techlib import make_sub_dir
class SubstratePage(object):
    def __init__(self, parent):
        #Substrate root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Substrates")
        
        #Set up substrate page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in substrate page at first (to prevent incomplete data entry)
        self.ui.SaveSubstrate.setEnabled(False)
        
        # Enable the save button in substrate page (after data entry is complete)
        self.ui.SubstrateList.currentIndexChanged.connect(self.check)
        self.ui.SubstrateNameInput.textChanged.connect(self.check)
        
        # Push buttons in substrate page
        self.ui.RemoveSubstrate.clicked.connect(self.remove)
        self.ui.SaveSubstrate.clicked.connect(self.save)
        
        # Lists in substrate page
        self.ui.SubstrateList.currentIndexChanged.connect(self.load)
        
        # Project specific variable
        self.current_substrate = None
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.SubstrateList.clear()
        self.ui.SubstrateList.addItem('New Substrate')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.SubstrateList.addItem(filename)
    
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrSubDieThicknessLabel, self.ui.ErrSubMetalThicknessLabel, self.ui.ErrSubMetalThermalCondLabel, self.ui.ErrSubMetalSpHeatLabel, self.ui.ErrSubMetalRhoLabel, self.ui.ErrSubMetalDensityLabel, 
                      self.ui.ErrSubIsolationThermalCondLabel, self.ui.ErrSubIsolationSpHeatLabel, self.ui.ErrSubIsolationDensityLabel, self.ui.ErrSubIsolationEpsilonLabel, self.ui.ErrSubIsolationMuLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.SubDieThicknessInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubDieThicknessLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubMetalThicknessInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubMetalThicknessLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubMetalThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubMetalThermalCondLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubMetalSpHeatInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubMetalSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubMetalRhoInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubMetalRhoLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubMetalDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubMetalDensityLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubIsolationThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubIsolationThermalCondLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubIsolationSpHeatInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubIsolationSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubIsolationDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubIsolationDensityLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubIsolationEpsilonInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubIsolationEpsilonLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.SubIsolationMuInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrSubIsolationMuLabel.setText("Error: Must be a number")
            error = True
        
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.SubstrateNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Substrate name already exists. Please choose another name.')
                
        """Save all inputs"""            
        if not error:
            sub = Substrate(None, None, None, None, None)
            sub.name = str(self.ui.SubstrateNameInput.text())
            sub.isolation_properties = MaterialProperties(None, float(self.ui.SubIsolationThermalCondInput.text()), 
                                                                float(self.ui.SubIsolationSpHeatInput.text()), 
                                                                float(self.ui.SubIsolationDensityInput.text()), None, 
                                                                float(self.ui.SubIsolationEpsilonInput.text()), 
                                                                float(self.ui.SubIsolationMuInput.text()))
            sub.metal_properties = MaterialProperties(None, float(self.ui.SubMetalThermalCondInput.text()), 
                                                            float(self.ui.SubMetalSpHeatInput.text()), 
                                                            float(self.ui.SubMetalDensityInput.text()), 
                                                            float(self.ui.SubMetalRhoInput.text()), None, None)
            
            sub.isolation_thickness = float(self.ui.SubDieThicknessInput.text())
            sub.metal_thickness = float(self.ui.SubMetalThicknessInput.text())
            
            make_sub_dir(self.sub_dir)
            save_file(sub,os.path.join(self.sub_dir, sub.name+".p"))
            self.load_page()
        else:
            print "Error Creating Substrate"
        
    def load(self):
        if self.ui.SubstrateList.currentIndex() > 0:
            filename = os.path.join(self.sub_dir, self.ui.SubstrateList.currentText())
            self.current_substrate = load_file(filename)
            
            self.ui.SubstrateNameInput.setText(str(self.current_substrate.name))
            self.ui.SubIsolationThermalCondInput.setText(str(self.current_substrate.isolation_properties.thermal_cond))
            self.ui.SubIsolationSpHeatInput.setText(str(self.current_substrate.isolation_properties.spec_heat_cap))
            self.ui.SubIsolationDensityInput.setText(str(self.current_substrate.isolation_properties.density))
            self.ui.SubIsolationEpsilonInput.setText(str(self.current_substrate.isolation_properties.rel_permit))
            self.ui.SubIsolationMuInput.setText(str(self.current_substrate.isolation_properties.rel_permeab))
            self.ui.SubMetalThermalCondInput.setText(str(self.current_substrate.metal_properties.thermal_cond))
            self.ui.SubMetalSpHeatInput.setText(str(self.current_substrate.metal_properties.spec_heat_cap))
            self.ui.SubMetalDensityInput.setText(str(self.current_substrate.metal_properties.density))
            self.ui.SubMetalRhoInput.setText(str(self.current_substrate.metal_properties.electrical_res))
            self.ui.SubDieThicknessInput.setText(str(self.current_substrate.isolation_thickness))
            self.ui.SubMetalThicknessInput.setText(str(self.current_substrate.metal_thickness))
        elif self.ui.SubstrateList.currentIndex() <= 0:
            self._clear_form()
            
    def remove(self):
        if self.ui.RemoveSubstrate.clicked:
            mb = QMessageBox()
            mb.addButton('Yes', QMessageBox.AcceptRole)
            mb.addButton('No', QMessageBox.RejectRole)
            mb.setText("Do you really want to delete the substrate?")
            ret = mb.exec_()
            if ret == 0: #AcceptRole, file to be removed
                if self.ui.SubstrateList.currentIndex() >=0:
                    filename = os.path.join(self.sub_dir, self.ui.SubstrateList.currentText())
                    os.remove(filename)
                
                self.ui.SubstrateList.removeItem(self.ui.SubstrateList.currentIndex())
                self._clear_form()
            else:
                pass
        else:
            pass
        self.load_page()
        
# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------
    
    def check(self):
        if self.ui.SubstrateList.currentIndex()<=0:
            if not ((len(self.ui.SubDieThicknessInput.text()) == 0) or (len(self.ui.SubMetalThicknessInput.text()) == 0) or (len(self.ui.SubMetalThermalCondInput.text()) == 0) or (len(self.ui.SubMetalSpHeatInput.text()) == 0) or (len(self.ui.SubMetalRhoInput.text()) == 0) or (len(self.ui.SubMetalDensityInput.text()) == 0) or (len(self.ui.SubIsolationThermalCondInput.text()) == 0) or (len(self.ui.SubIsolationSpHeatInput.text()) == 0) or (len(self.ui.SubIsolationDensityInput.text()) == 0) or (len(self.ui.SubIsolationEpsilonInput.text()) == 0) or (len(self.ui.SubIsolationMuInput.text()) == 0) or (len(self.ui.SubstrateNameInput.text()) == 0)):
                self.ui.SaveSubstrate.setEnabled(True)
        else:
            self.ui.SaveSubstrate.setEnabled(True)

# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------
    
    def _clear_form(self):
        self.ui.SubstrateNameInput.clear()
        self.ui.SubIsolationThermalCondInput.clear()
        self.ui.SubIsolationSpHeatInput.clear()
        self.ui.SubIsolationDensityInput.clear()
        self.ui.SubIsolationEpsilonInput.clear()
        self.ui.SubIsolationMuInput.clear()
        self.ui.SubMetalThermalCondInput.clear()
        self.ui.SubMetalSpHeatInput.clear()
        self.ui.SubMetalDensityInput.clear()
        self.ui.SubMetalRhoInput.clear()
        self.ui.SubDieThicknessInput.clear()
        self.ui.SubMetalThicknessInput.clear()
