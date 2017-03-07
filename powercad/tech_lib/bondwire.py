'''
Created on Feb 18, 2013

@author: anizam
'''

import os
import pickle

from PySide import QtGui
from PySide.QtGui import QMessageBox

from powercad.tech_lib.test_techlib import make_sub_dir
from powercad.design.library_structures import *

class BondwirePage(object):
    def __init__(self, parent):
        # Bond wire root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Layout_Selection", "Bond Wire")
        
        #Set up bond wire page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save button in bond wire page at first (to prevent incomplete data entry)
        self.ui.SaveBondwire.setEnabled(False)
        
        # Enable the save button in bond wire page (after data entry is complete)
        self.ui.BondwireList.currentIndexChanged.connect(self.check)
        self.ui.BondwireNameInput.textChanged.connect(self.check)
        
        # Push buttons in bond wire page
        self.ui.RemoveBondwire.clicked.connect(self.remove)
        self.ui.SaveBondwire.clicked.connect(self.save)
        
        # Lists in bond wire page
        self.ui.BondwireList.currentIndexChanged.connect(self.load)
       
        # Radio buttons in bond wire page
        self.ui.RoundWire.toggled.connect(self._set_round_form)
        self.ui.RibbonWire.toggled.connect(self._set_ribbon_form)
        
        # Project specific variable
        self.current_bondwire = None
        
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.BondwireList.clear()
        self.ui.BondwireList.addItem('New Bond Wire')
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.BondwireList.addItem(filename)
    
    def save(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrRoundDiaWireLabel, self.ui.ErrRibbonWidthWireLabel, self.ui.ErrRibbonHeightWireLabel, self.ui.ErrBondwireHeightLabel, self.ui.ErrBondwireFractionLabel, self.ui.ErrRhoBondwireLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.BondwireHeightInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBondwireHeightLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.BondwireFractionInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrBondwireFractionLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.RhoBondwireInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrRhoBondwireLabel.setText("Error: Must be a number")
            error = True
            
        if self.ui.RoundWire.isChecked():
            if(not self.ui.RoundDiaWireInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrRoundDiaWireLabel.setText("Error: Must be a number")
                error = True
        else:
            if(not self.ui.RibbonWidthWireInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrRibbonWidthWireLabel.setText("Error: Must be a number")
                error = True
            if(not self.ui.RibbonHeightWireInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
                self.ui.ErrRibbonHeightWireLabel.setText("Error: Must be a number")
                error = True
                
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.BondwireNameInput.text()+'.p':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Bondwire name already exists. Please choose another name.')
                
        """Save all inputs"""            
        if not error:
            wire = BondWire(None, None, None, None, None, None, None)
            wire.name = str(self.ui.BondwireNameInput.text())
            if self.ui.PowerWire.isChecked():
                wire.wire_type = BondWire.POWER
            else:
                wire.wire_type = BondWire.SIGNAL
            
            if self.ui.RoundWire.isChecked():
                wire.shape = BondWire.ROUND
                wire.dimensions = float(self.ui.RoundDiaWireInput.text())
            else: 
                wire.shape = BondWire.RIBBON
                wire.dimensions = (float(self.ui.RibbonWidthWireInput.text()), 
                                   float(self.ui.RibbonHeightWireInput.text()))
            
            wire.a = float(self.ui.BondwireHeightInput.text())
            wire.b = float(self.ui.BondwireFractionInput.text())
            wire.properties = MaterialProperties(None, None, None, None, 
                                                 float(self.ui.RhoBondwireInput.text()), None, None)
            
            make_sub_dir(self.sub_dir)
            pickle.dump(wire,open(os.path.join(self.sub_dir, wire.name+".p"), "wb"))
            self.load_page()
        else:
            print "Error Creating Bond Wire"
        
    def load(self):
        if self.ui.BondwireList.currentIndex()>0:
            filename = os.path.join(self.sub_dir, self.ui.BondwireList.currentText())
            self.current_bondwire = pickle.load(open(filename, "rb"))
            
            self.ui.BondwireNameInput.setText(str(self.current_bondwire.name))
            
            if self.current_bondwire.shape == 1:
                
                if self.current_bondwire.wire_type == 1:
                    self.ui.PowerWire.setChecked(True)
                elif self.current_bondwire.wire_type == 2:
                    self.ui.SignalWire.setChecked(True)
                self.ui.RoundWire.setChecked(True)
                self.ui.RoundDiaWireInput.setText(str(self.current_bondwire.dimensions))
                self.ui.RibbonWidthWireInput.clear()
                self.ui.RibbonHeightWireInput.clear()
                self._set_ribbon_form(False)
            
            elif self.current_bondwire.shape == 2:
                if self.current_bondwire.wire_type == 1:
                    self.ui.PowerWire.setChecked(True)
                elif self.current_bondwire.wire_type == 2:
                    self.ui.SignalWire.setChecked(True)
                self.ui.RibbonWire.setChecked(True)
                self.ui.RibbonWidthWireInput.setText(str(self.current_bondwire.dimensions[0]))
                self.ui.RibbonHeightWireInput.setText(str(self.current_bondwire.dimensions[1]))
                self.ui.RoundDiaWireInput.clear()
                
            self.ui.BondwireHeightInput.setText(str(self.current_bondwire.a))
            self.ui.BondwireFractionInput.setText(str(self.current_bondwire.b))
            self.ui.RhoBondwireInput.setText(str(self.current_bondwire.properties.electrical_res))
        elif self.ui.BondwireList.currentIndex()<=0:
            self._clear_form()
    
    def remove(self):
        if self.ui.RemoveBondwire.clicked:
            mb = QMessageBox()
            mb.addButton('Yes', QMessageBox.AcceptRole)
            mb.addButton('No', QMessageBox.RejectRole)
            mb.setText("Do you really want to delete the bond wire?")
            ret = mb.exec_()
            if ret == 0: #AcceptRole, file to be removed
                if self.ui.BondwireList.currentIndex() >=0:
                    filename = os.path.join(self.sub_dir, self.ui.BondwireList.currentText())
                    os.remove(filename)
                
                self.ui.BondwireList.removeItem(self.ui.BondwireList.currentIndex())
                self.ui.BondwireHeightInput.clear()
                self.ui.BondwireFractionInput.clear()
                self.ui.RhoBondwireInput.clear()
                self.ui.BondwireNameInput.clear()
        
                if self.ui.RoundWire.isChecked(): 
                    self.ui.RoundDiaWireInput.clear()
                            
                if self.ui.RibbonWire.isChecked():
                    self.ui.RibbonWidthWireInput.clear()
                    self.ui.RibbonHeightWireInput.clear()
            else:
                pass
        else:
            pass
        self.load_page()

# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------

    def check(self):
        if self.ui.BondwireList.currentIndex()<=0:
            if self.ui.RoundWire.isChecked():
                if not ((len(self.ui.RoundDiaWireInput.text()) == 0) or (len(self.ui.BondwireHeightInput.text()) == 0) or (len(self.ui.BondwireFractionInput.text()) == 0) or (len(self.ui.RhoBondwireInput.text()) == 0) or (len(self.ui.BondwireNameInput.text()) == 0)):
                    self.ui.SaveBondwire.setEnabled(True)
            else:
                if not ((len(self.ui.RibbonWidthWireInput.text()) == 0) or (len(self.ui.RibbonHeightWireInput.text()) == 0) or (len(self.ui.BondwireHeightInput.text()) == 0) or (len(self.ui.BondwireFractionInput.text()) == 0) or (len(self.ui.RhoBondwireInput.text()) == 0) or (len(self.ui.BondwireNameInput.text()) == 0)):
                    self.ui.SaveBondwire.setEnabled(True)
        else:
            self.ui.SaveBondwire.setEnabled(True)

# ------------------------------------------------------------------------------------------
# ------ Enable/disable Specific Forms -----------------------------------------------------
                        
    def _set_round_form(self, enabled):
        self.ui.RoundDiaWireInput.setEnabled(enabled)
    
    def _set_ribbon_form(self, enabled):
        self.ui.RibbonWidthWireInput.setEnabled(enabled)
        self.ui.RibbonHeightWireInput.setEnabled(enabled)

# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------
        
    def _clear_form(self):
        self.ui.RhoBondwireInput.clear()
        self.ui.BondwireHeightInput.clear()
        self.ui.BondwireFractionInput.clear()
        self.ui.BondwireNameInput.clear()
        self.ui.RoundDiaWireInput.clear()
        self.ui.RibbonWidthWireInput.clear()
        self.ui.RibbonHeightWireInput.clear()        
    
    
