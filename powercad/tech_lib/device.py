'''
Created on Feb 22, 2013

@author: anizam
'''

import os
import pickle

from PySide import QtGui
from PySide.QtGui import QMessageBox
from PySide.QtGui import QFileDialog

from powercad.tech_lib.test_techlib import make_sub_dir
from powercad.design.library_structures import *
from powercad.save_and_load import *
class DevicePage(object):
    # Device type enum
    TRANSISTOR = 0
    DIODE = 1
    
    def __init__(self, parent):
        # Device root directory
        self.sub_dir = os.path.join(parent.tech_lib_dir, "Layout_Selection", "Device")
        
        # Set up device page GUI
        self.parent = parent
        self.ui = parent.ui
        
        # Disable the save or load buttons in device page at first (to prevent incomplete data entry)
        self.ui.VerilogFileLoad.setEnabled(False)
        self.ui.SaveDevice.setEnabled(False)
        self.ui.SavePosition.setEnabled(False)
        
        # Enable save or load buttons in device page (after data entry is complete)
        self.ui.BrowseVerilogDir.clicked.connect(self.check_verilog)
        self.ui.DeviceList.currentIndexChanged.connect(self.check)
        self.ui.XInput.textChanged.connect(self.check)
        self.ui.DeviceNameInput.textChanged.connect(self.check)
        
        # Push buttons in device section
        self.ui.SaveDevice.clicked.connect(self.save_device)
        self.ui.RemoveDevice.clicked.connect(self._remove_device_form)
        
        # Push buttons in bond wire position section
        self.ui.SavePosition.clicked.connect(self.save_position)
        self.ui.RemovePosition.clicked.connect (self._remove_position_form)
        
        # Push buttons in Verilog-A files load section
        self.ui.BrowseVerilogDir.pressed.connect(self.open_dir)
        self.ui.VerilogFileLoad.clicked.connect(self.load_verilog)
        
        # Lists in device page
        # All input fields are controlled primarily by the device list. The list of bond wire positions are dependent on a particular device.
        if self.ui.DeviceList.currentIndex() == 0:
            self.ui.DeviceList.currentIndexChanged.connect(self.load_device)
            self.ui.PositionList.currentIndexChanged.connect(self.load_single_position)
        else:
            self.ui.DeviceList.currentIndexChanged.connect(self._clear_device_form())
        
        # Project specific variables
        self.current_device = None
        self.wire_landings = []

# ------------------------------------------------------------------------------------------
# ------ Complete Entry Check --------------------------------------------------------------
       
    def check(self):
        if self.ui.DeviceList.currentIndex()<=0:
            if not ((len(self.ui.DeviceNameInput.text())==0)):
                self.ui.SaveDevice.setEnabled(True)
            else:
                pass
            
            if not len(self.ui.XInput.text()) == 0:
                self.ui.SavePosition.setEnabled(True)
            else:
                pass
        else:
            self.ui.SaveDevice.setEnabled(True)
            self.ui.SavePosition.setEnabled(True)      
        
    def check_verilog(self):
        if not len(self.ui.VerilogFileName.text())<=0:
            self.ui.VerilogFileLoad.setEnabled(True)


# ------------------------------------------------------------------------------------------        
# ------ Device Section --------------------------------------------------------------------
    
    def load_page(self):
        dir_list = os.listdir(self.sub_dir)
        self.ui.DeviceList.clear()
        self.ui.DeviceList.addItem('New Device')
        self.ui.PositionList.clear()
        self.ui.PositionList.addItem('New Position')
        self.wire_landings = []
        
        for filename in dir_list:
            file_path = os.path.join(self.sub_dir, filename)
            if os.path.isfile(file_path):
                length = len(filename)
                if filename[length-2:] == '.p':
                    self.ui.DeviceList.addItem(filename)
       
    def save_device(self):
        """Validation of input data"""
        error = False
        
        #reset all error messages
        for label in [self.ui.ErrDeviceLengthLabel, self.ui.ErrDeviceWidthLabel, self.ui.ErrDeviceHeightLabel, self.ui.ErrDeviceThermalCondLabel, self.ui.ErrDeviceSpHeatLabel, self.ui.ErrDeviceDensityLabel]:
            label.setText("")
        
        # check all textbox inputs for correct type
        if(not self.ui.DeviceLengthInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceLengthLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DeviceWidthInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceWidthLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DeviceHeightInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceHeightLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DeviceThermalCondInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceThermalCondLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DeviceSpHeatInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceSpHeatLabel.setText("Error: Must be a number")
            error = True
        if(not self.ui.DeviceDensityInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.ErrDeviceDensityLabel.setText("Error: Must be a number")
            error = True
        
        # Check that there are some device landing positions (otherwise device cannot function)
        power_pt = False
        signal_pt = False
        for landing in self.wire_landings:
            if landing.bond_type == BondwireLanding.POWER:
                power_pt = True
            elif  landing.bond_type == BondwireLanding.SIGNAL:
                signal_pt = True
        if self.ui.DeviceType.currentIndex() == self.TRANSISTOR:
            if (not power_pt) or (not signal_pt):
                error = True
                QMessageBox.warning(self.parent, 'Bondwire Landing Error', 'Device is a Transistor: Must have at least one power and signal bondwire landing.')
        elif self.ui.DeviceType.currentIndex() == self.DIODE:
            if not power_pt:
                error = True
                QMessageBox.warning(self.parent, 'Bondwire Landing Error', 'Device is a Diode: Must have at least one power bondwire landing.')
        
        # Check if the device filename is unique (if not, don't save the device, ask user to rename)
        dir_list = os.listdir(self.sub_dir)
        for filename in dir_list:
            if filename==self.ui.DeviceNameInput.text()+'.dv':
                error = True
                QMessageBox.warning(self.parent, 'File Name Error', 'Device name already exists. Please choose another.')
        
        """Save all inputs"""    
        if not error:
            dev = Device(None, None, None, None, None, None, None)
            dev.name = str(self.ui.DeviceNameInput.text())
            dev.dimensions = (float(self.ui.DeviceLengthInput.text()), float(self.ui.DeviceWidthInput.text()), float(self.ui.DeviceHeightInput.text()))
            dev.properties = MaterialProperties(None, float(self.ui.DeviceThermalCondInput.text()),
                                                 float(self.ui.DeviceSpHeatInput.text()), 
                                                 float(self.ui.DeviceDensityInput.text()), 
                                                 None, None, None)
    
            dev.device_model = None
            
            if self.ui.DeviceType.currentIndex() == self.TRANSISTOR:
                dev.device_type = Device.TRANSISTOR
            elif self.ui.DeviceType.currentIndex() == self.DIODE:
                dev.device_type = Device.DIODE
                
            self.save_position()
            dev.wire_landings = self.save_position()
            dev.power_side = self.find_device_power_side(dev)
            save_file(dev,os.path.join(self.sub_dir, dev.name+".p"))
            self.load_page()
        else:
            print "Error Creating Device"
            
    def find_device_power_side(self, device):
        """Finds which side the power bondwires are connected on a device (left or right)"""
        # Loop through power bondwire landings and take average X landing position
        # Determine which side that average landing position falls on (left or right side of device)
        sum_x = 0.0
        for landing in device.wire_landings:
            sum_x += landing.position[0]
        avg_x = sum_x/len(device.wire_landings)
        
        if avg_x <= float(self.ui.DeviceWidthInput.text())*0.5:
            return Device.LEFT_SIDE
            print 'left side'
        else:
            return Device.RIGHT_SIDE
            print 'right side'
   
    def load_device(self):
        if self.ui.DeviceList.currentIndex() > 0:
            filename = os.path.join(self.sub_dir, self.ui.DeviceList.currentText())
            self.current_device = load_file(filename)
            self.ui.DeviceNameInput.setText(str(self.current_device.name))
            self.ui.DeviceLengthInput.setText(str(self.current_device.dimensions[0]))
            self.ui.DeviceWidthInput.setText(str(self.current_device.dimensions[1]))
            self.ui.DeviceHeightInput.setText(str(self.current_device.dimensions[2]))
            self.ui.DeviceThermalCondInput.setText(str(self.current_device.properties.thermal_cond)) 
            self.ui.DeviceSpHeatInput.setText(str(self.current_device.properties.spec_heat_cap))
            self.ui.DeviceDensityInput.setText(str(self.current_device.properties.density))
            self.load_positions()
            self.load_device_type()
            
        elif self.ui.DeviceList.currentIndex() == 0:
            self._clear_device_form()
            self.ui.PositionList.clear()
            self.ui.PositionList.addItem('New Position')
            self._clear_position_form()
                    
    def load_device_type(self):
        if self.current_device.device_type == 1:
            self.ui.DeviceType.setCurrentIndex(0)
        elif self.current_device.device_type == 2:
            self.ui.DeviceType.setCurrentIndex(1)
     
    def _remove_device_form(self):
        mb = QMessageBox()
        mb.addButton('Yes', QMessageBox.AcceptRole)
        mb.addButton('No', QMessageBox.RejectRole)
        mb.setText("Do you really want to delete the device?")
        ret = mb.exec_()
        
        if ret == 0: #AcceptRole, file to be removed
            if self.ui.DeviceList.currentIndex() >=0:
                filename = os.path.join(self.sub_dir, self.ui.DeviceList.currentText())
                if self.current_device.wire_landings is not None:
                    for landing in self.current_device.wire_landings:
                        self.ui.PositionList.removeItem(self.ui.PositionList.currentIndex())
                os.remove(filename)
            self.ui.DeviceList.removeItem(self.ui.DeviceList.currentIndex())
            self._clear_device_form()
        else:
            pass
        
        self.load_page()

# ------------------------------------------------------------------------------------------
# ------ Bondwire Position Section ---------------------------------------------------------
           
    def save_position(self):
        """Validation of input data"""
        error = False
        
        # check all textbox inputs for correct type
        if(not self.ui.XInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            QMessageBox.warning(self.parent, 'Bondwire Position Error', 'X-Position must be a number.')
            error = True
        if(not self.ui.YInput.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            QMessageBox.warning(self.parent, 'Bondwire Position Error', 'Y-Position must be a number.')
            error = True
        # check if power or signal is selected
        if (not self.ui.PowerButton.isChecked() and not self.ui.SignalButton.isChecked()):
            QMessageBox.warning(self.parent, 'Bond wire type is not selected!', 'Bond wire must be power or signal.')
            error = True
        
        """Save all the inputs"""    
        if not error:
            self.wire_landings=self.get_point_data()
            self.ui.PositionList.clear()
            for landing in self.wire_landings:
                if landing.bond_type == 1:
                    type = 'power'
                elif landing.bond_type == 2:
                    type = 'signal'
                self.ui.PositionList.addItem(str(type+':'+str(landing.position)))

            return self.wire_landings 
    
    def load_positions(self):
        if self.current_device.wire_landings is not None:
            self.wire_landings = self.current_device.wire_landings
            self.ui.PositionList.clear()
            
            for landing in self.wire_landings:
                if not landing.bond_type is None:
                    if landing.bond_type == BondwireLanding.POWER:
                        type = 'power'
                    elif landing.bond_type == BondwireLanding.SIGNAL:
                        type = 'signal'
                    self.ui.PositionList.addItem(str(type+':'+str(landing.position)))
                    
                else:
                    print 'bond type is None'

        else:
            print 'wire landing is none'
            self.wire_landings = []
            self.ui.PositionList.clear()
            self._clear_position_form()
                 
    def load_single_position(self):
        if self.ui.DeviceList.currentIndex()<0:
            self._clear_position_form()
            
        elif self.ui.DeviceList.currentIndex()>0:
            self.wire_landings = self.current_device.wire_landings
            sel_landing = self.wire_landings[self.ui.PositionList.currentIndex()]
            self.ui.XInput.setText(str(sel_landing.position[0]))
            self.ui.YInput.setText(str(sel_landing.position[1]))
            
            if sel_landing.bond_type == 1:
                self.ui.PowerButton.setChecked(True)
                self.ui.SignalButton.setChecked(False)
            elif sel_landing.bond_type == 2:
                self.ui.SignalButton.setChecked(True)
                self.ui.PowerButton.setChecked(False)
                
        elif (self.ui.DeviceList.currentIndex()==0 and self.ui.PositionList.currentIndex()>0):
            print 'current list index:', self.ui.PositionList.currentIndex()
            print 'current wire landing list index:', str(self.wire_landings)
#            self.ui.XInput.setText(str(self.wire_landings[self.ui.PositionList.currentIndex()].position[0]))
#            self.ui.YInput.setText(str(self.wire_landings[self.ui.PositionList.currentIndex()].position[1]))
                
    def get_point_data(self):
        if self.ui.PowerButton.isChecked():
            bond_type = BondwireLanding.POWER
        elif self.ui.SignalButton.isChecked():
            bond_type = BondwireLanding.SIGNAL
        position = (float(self.ui.XInput.text()), float(self.ui.YInput.text()))
        
        return BondwireLanding(position, bond_type)
    
    def _remove_position_form(self):
        mb = QMessageBox()
        mb.addButton('Yes', QMessageBox.AcceptRole)
        mb.addButton('No', QMessageBox.RejectRole)
        mb.setText("Do you really want to delete the bond wire landing position?")
        ret = mb.exec_()

        if ret == 0: #AcceptRole, file to be removed      
            if self.ui.PositionList.currentIndex()>=0:
                id=self.ui.PositionList.currentIndex()
                self.ui.PositionList.removeItem(id)
                self.wire_landings.remove(self.wire_landings[id])
            elif self.ui.PositionList.currentIndex()<0:
                mb = QMessageBox()
                mb.addButton('OK', QMessageBox.AcceptRole)
                mb.setText("The position list is empty")
                mb.exec_()        
        else:
            pass
        
        
# ------------------------------------------------------------------------------------------        
# ------ Verilog-A Section -----------------------------------------------------------------        

    def open_dir(self):
        vafile = QFileDialog.getOpenFileName(caption=r"Open file", filter="Verilog-A (*.va)")
        if vafile[0][-3:] == '.va':
            file = open(vafile[0], 'rb')
            file_name = vafile[0][57:]
            self.ui.VerilogFileName.setText(file_name) 
            self.check_verilog()
            
    def load_verilog(self):
        path = r"..\..\..\device_models"
        filename = os.path.join(path, self.ui.VerilogFileName.text())
        f = open(filename, 'r')
        va= str(f.read())
        f.close()

    

# ------------------------------------------------------------------------------------------
# ------ Clear Forms -----------------------------------------------------------------------

    def _clear_device_form(self):
        self.ui.DeviceNameInput.clear()
        self.ui.DeviceLengthInput.clear()
        self.ui.DeviceWidthInput.clear()
        self.ui.DeviceHeightInput.clear()
        self.ui.DeviceThermalCondInput.clear()
        self.ui.DeviceSpHeatInput.clear()
        self.ui.DeviceDensityInput.clear()

    def _set_position_form(self, enabled):
        self.ui.XInput.setEnabled(enabled)
        self.ui.YInput.setEnabled(enabled)
    
    def _clear_position_form(self):
        self.ui.XInput.clear()
        self.ui.YInput.clear()
        