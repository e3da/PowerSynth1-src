'''
Created on Feb 17, 2013

@author: Andalib
'''

import os

from PySide.QtGui import QMessageBox

from powercad.design.library_structures import *
from powercad.general.settings.save_and_load import *
from powercad.tech_lib.test_techlib import make_sub_dir
class LeadPage(object):
    def __init__(self, parent):
        # Lead root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Layout_Selection", "Lead")
        
        # Set up lead page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in lead page at first (to prevent incomplete data entry)
        self.ui.SaveLead.setEnabled(False)
        
        # Enable the save button in lead page (after data entry is complete)
        self.ui.LeadList.currentIndexChanged.connect(self.check)
        self.ui.LeadNameInput.textChanged.connect(self.check)
        
        # Push buttons in lead page
        self.ui.RemoveLead.clicked.connect(self.remove)
        self.ui.SaveLead.clicked.connect(self.save)
        
        # Lists in lead page
        self.ui.LeadList.currentIndexChanged.connect(self.load)
        
        # Radio buttons in lead page
        self.ui.RoundLead.toggled.connect(self._set_round_form)
        self.ui.BusbarLead.toggled.connect(self._set_busbar_form)
        
        # Project specific variable
        self.current_lead = None
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.LeadList.clear()
        self.ui.LeadList.addItem('New Lead')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.LeadList.addItem(filename)
    
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrRoundLeadDiaLabel, self.ui.ErrRoundLeadHeightLabel, self.ui.ErrBusLeadHeightLabel, self.ui.ErrBusLeadLengthLabel, self.ui.ErrBusLeadThicknessLabel, self.ui.ErrBusLeadWidthLabel, self.ui.ErrRhoLeadlabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.RhoLeadInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrRhoLeadlabel.setText("Error: Must be a number")
            error = True
        
        if self.ui.RoundLead.isChecked():
            if(not self.ui.RoundLeadDiaInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrRoundLeadDiaLabel.setText("Error: Must be a number")
                error = True
            if(not self.ui.RoundLeadHeightInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrRoundLeadHeightLabel.setText("Error: Must be a number")
                error = True
        else:
            if(not self.ui.BusLeadLengthInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrBusLeadLengthLabel.setText("Error: Must be a number")
                error = True
            if(not self.ui.BusLeadWidthInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrBusLeadWidthLabel.setText("Error: Must be a number")
                error = True
            if(not self.ui.BusLeadHeightInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrBusLeadHeightLabel.setText("Error: Must be a number")
                error = True
            if(not self.ui.BusLeadThicknessInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrBusLeadThicknessLabel.setText("Error: Must be a number")
                error = True
                
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.LeadNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Lead name already exists. Please choose another name.')
                
        """Save all inputs""" 
        if not error:
            lead = Lead(None, None, None, None, None)
            lead.name = str(self.ui.LeadNameInput.text())
            if self.ui.PowerLead.isChecked():
                lead.lead_type = Lead.POWER
            else:
                lead.lead_type = Lead.SIGNAL
            
            if self.ui.RoundLead.isChecked():
                lead.shape = Lead.ROUND
                lead.dimensions = (float(self.ui.RoundLeadDiaInput.text()), float(self.ui.RoundLeadHeightInput.text()))
            else: 
                lead.shape = Lead.BUSBAR
                lead.dimensions = (float(self.ui.BusLeadLengthInput.text()), float(self.ui.BusLeadWidthInput.text()), 
                                   float(self.ui.BusLeadHeightInput.text()), float(self.ui.BusLeadThicknessInput.text()))
            
            lead.properties = MaterialProperties(None, None, None, None, float(self.ui.RhoLeadInput.text()), None, None)
            
            make_sub_dir(self.sub_dir)
            save_file(lead,os.path.join(self.sub_dir, lead.name+".p"))
            self.load_page()
        else:
            print "Error Creating Lead"
    
    def load(self):
        if self.ui.LeadList.currentIndex() >0:
            filename = os.path.join(self.sub_dir, self.ui.LeadList.currentText())
            self.current_lead = load_file(filename)
            
            self.ui.LeadNameInput.setText(str(self.current_lead.name))
            self.ui.RhoLeadInput.setText(str(self.current_lead.properties.electrical_res))
            if self.current_lead.shape == 2:
                self.ui.RoundLead.setChecked(True)
                if self.current_lead.lead_type == 1:
                    self.ui.PowerLead.setChecked(True)
                else:
                    self.ui.SignalLead.setChecked(True)
                self.ui.RoundLeadDiaInput.setText(str(self.current_lead.dimensions[0]))
                self.ui.RoundLeadHeightInput.setText(str(self.current_lead.dimensions[1]))
                self._clear_busbar_form()
                
            elif self.current_lead.shape == 1:
                self.ui.BusbarLead.setChecked(True)
                if self.current_lead.lead_type == 1:
                    self.ui.PowerLead.setChecked(True)
                else:
                    self.ui.SignalLead.setChecked(True)
                self.ui.BusLeadLengthInput.setText(str(self.current_lead.dimensions[0]))
                self.ui.BusLeadWidthInput.setText(str(self.current_lead.dimensions[1]))
                self.ui.BusLeadHeightInput.setText(str(self.current_lead.dimensions[2]))
                self.ui.BusLeadThicknessInput.setText(str(self.current_lead.dimensions[3]))
                self._clear_round_form()
        
        elif self.ui.LeadList.currentIndex() <=0:
            self._clear_busbar_form()
            self._clear_round_form()
            self._clear_form()
            
    
    def remove(self):
        if self.ui.RemoveLead.clicked:
            mb = QMessageBox()
            mb.addButton('Yes', QMessageBox.AcceptRole)
            mb.addButton('No', QMessageBox.RejectRole)
            mb.setText("Do you really want to delete the lead?")
            ret = mb.exec_()
            if ret == 0: #AcceptRole, file to be removed
                if self.ui.LeadList.currentIndex() >=0:
                    filename = os.path.join(self.sub_dir, self.ui.LeadList.currentText())
                    os.remove(filename)
                
                self.ui.LeadList.removeItem(self.ui.LeadList.currentIndex())
                self._clear_form()
                if self.ui.RoundLead.isChecked(): 
                    self._clear_round_form()
                elif self.ui.BusbarLead.isChecked():
                    self._clear_busbar_form()
            else:
                pass
        else:
            pass

# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------

    def check(self):
        if self.ui.LeadList.currentIndex()<=0:
            if self.ui.RoundLead.isChecked():
                if not ((len(self.ui.RoundLeadDiaInput.text()) == 0) or (len(self.ui.RoundLeadHeightInput.text()) == 0) or (len(self.ui.RhoLeadInput.text()) == 0) or (len(self.ui.LeadNameInput.text()) == 0)):
                    self.ui.SaveLead.setEnabled(True)
            else:
                if not ((len(self.ui.BusLeadLengthInput.text()) == 0) or (len(self.ui.BusLeadWidthInput.text()) == 0) or (len(self.ui.BusLeadHeightInput.text()) == 0) or (len(self.ui.BusLeadThicknessInput.text()) == 0) or (len(self.ui.RhoLeadInput.text()) == 0) or (len(self.ui.LeadNameInput.text()) == 0)):
                    self.ui.SaveLead.setEnabled(True)
        else:
            self.ui.SaveLead.setEnabled(True)
    
# ------------------------------------------------------------------------------------------
# ------ Enable/disable Specific Forms -----------------------------------------------------
        
    def _set_round_form(self, enabled):
        self.ui.RoundLeadDiaInput.setEnabled(enabled)
        self.ui.RoundLeadHeightInput.setEnabled(enabled)
        self.ui.RhoLeadInput.setEnabled(enabled)
        self.ui.LeadNameInput.setEnabled(enabled)
        
    def _set_busbar_form(self, enabled):
        self.ui.BusLeadLengthInput.setEnabled(enabled)
        self.ui.BusLeadWidthInput.setEnabled(enabled)
        self.ui.BusLeadHeightInput.setEnabled(enabled)
        self.ui.BusLeadThicknessInput.setEnabled(enabled)
        self.ui.RhoLeadInput.setEnabled(enabled)
        self.ui.LeadNameInput.setEnabled(enabled)

# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------
            
    def _clear_form(self):
        self.ui.RhoLeadInput.clear()
        self.ui.LeadNameInput.clear()
        
    def _clear_round_form(self):
        self.ui.RoundLeadDiaInput.clear()
        self.ui.RoundLeadHeightInput.clear()
    
    def _clear_busbar_form(self):
        self.ui.BusLeadLengthInput.clear()
        self.ui.BusLeadWidthInput.clear()
        self.ui.BusLeadHeightInput.clear()
        self.ui.BusLeadThicknessInput.clear()