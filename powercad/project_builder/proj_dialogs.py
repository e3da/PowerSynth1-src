'''
Created on Oct 12, 2012

@author: Peter N. Tucker, qmle
'''
# IMPORT METHODS
import os
import traceback
import pandas as pd
from PySide import QtGui
import types
from PySide.QtGui import QFileDialog, QStandardItemModel,QStandardItem, QMessageBox,QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import powercad.sym_layout.plot as plot
from powercad.project_builder.dialogs.propertiesDeviceDialog import Ui_device_propeties
from powercad.Spice_handler.spice_import.NetlistImport import Netlist

plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'
from powercad.design.project_structures import *
from powercad.project_builder.dialogs.device_states import Ui_dev_state_dialog
from powercad.project_builder.dialogs.newProjectDialog import Ui_newProjectDialog
from powercad.project_builder.dialogs.openProjectDialog_ui import Ui_openProjectDialog
from powercad.project_builder.dialogs.edit_tech_lib_dir_ui import Ui_EditTechLibDirDialog
from powercad.project_builder.dialogs.solidwork_version_check_ui import Ui_checkversion_dialog
from powercad.project_builder.dialogs.genericDeviceDialog_ui import Ui_generic_device_builder
from powercad.project_builder.dialogs.device_setup_dialog import Ui_setup_device
from powercad.project_builder.dialogs.Env_setup import Ui_EnvSetup
from powercad.project_builder.dialogs.bondwire_setup import Ui_Bondwire_setup
from powercad.project_builder.dialogs.layoutEditor_ui import Ui_layouteditorDialog
from powercad.project_builder.project import Project
from powercad.sym_layout.symbolic_layout import SymbolicLayout
from powercad.general.settings.settings import DEFAULT_TECH_LIB_DIR,EXPORT_DATA_PATH,ANSYS_IPY64,FASTHENRY_FOLDER,GMSH_BIN_PATH,ELMER_BIN_PATH
from powercad.electro_thermal.ElectroThermal_toolbox import rdson_fit_transistor, list2float, csv_load_file,Vth_fit,fCRSS_fit
from powercad.general.settings.save_and_load import save_file, load_file
from powercad.project_builder.dialogs.ResponseSurface import Ui_ResponseSurface
from powercad.project_builder.dialogs.ModelSelection import Ui_ModelSelection
from powercad.layer_stack.layer_stack_import import *
from powercad.general.settings.Error_messages import *
from PySide import QtCore, QtGui
from powercad.sym_layout.symbolic_layout import SymPoint
from powercad.response_surface.Model_Formulation import form_trace_model_optimetric,form_fasthenry_trace_response_surface
import sys
import psidialogs
# CLASSES FOR DIALOG USAGE
class GenericDeviceDialog(QtGui.QDialog):   
    # Author: quang le
    # Date: 9-27-2016
    def __init__(self,parent, device_dir):
        '''Constructor for Generic Device Dialog'''
        '''Description: This is the constructor generic device dialog in PowerSynth. Libraries -> Generic Model ->triggered'''
        '''This dialog will load existed data_sheet information of a device (MosFet or Diode) or letting user modify such information'''
        '''Using the Electrothermal_toolbox in PowerSynth, curve fitting methods are used to find best fit parameters for each required datasheet curve '''
        '''Inputs: DataSheet Information Qrr, Ciss, Vpl, Vth vs Tj curve, Rds vs Tj curve, Crss vs Vds curve'''
        '''Outputs: Under tech_lib->Layout_selection->Device->Device_PModel-> *.pmdl files '''
        # Basic Constructor of any dialog connected a a Mianwindow
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_generic_device_builder()
        self.ui.setupUi(self)
        self.parent = parent
        self.dev_dir=device_dir
        #---------------------------------------------------------
        # Initially, the Build_Generic_Model button is disabled 
        self.ui.btn_buildgenericmdl.setEnabled(False)
        #---------------------------------------------------------
        # Connect method -- Read through to understand this is important to skim through each functions
        self.ui.btn_buildgenericmdl.pressed.connect(self.make_mdl) 
        self.ui.cmb_device_choice.currentIndexChanged.connect(self.change_page)
        self.ui.lst_device.clicked.connect(self.enable_inputs)
        self.ui.lst_device.clicked.connect(self.load_selected_inputs)
        self.ui.btn_rds_vs_tj.pressed.connect(self.load_data_rd_tJ)
        self.ui.btn_vth_vs_tj.pressed.connect(self.load_data_vth_tj)
        self.ui.btn_crss_vs_vds.pressed.connect(self.load_data_crss_vds)
        #----------------------------------------------------------------------------------------------
        # Disable Text if there is no Device Selected
        self.ui.ln_edit_qrr.setEnabled(False)
        self.ui.ln_edit_ciss.setEnabled(False)
        self.ui.ln_edit_vpl.setEnabled(False)
        #--------------------------------------------
        # Disable Buttons if there is no Device Selected
        self.ui.btn_vth_vs_tj.setEnabled(False)
        self.ui.btn_crss_vs_vds.setEnabled(False)
        self.ui.btn_rds_vs_tj.setEnabled(False)
        #-----------------------------------------------
        # Set up Device Field
        self.change_page()   
        #--------------------
        # Setup Directory for models  
        self.model_dir=os.path.join(self.dev_dir,'Device_PModel')
        #---------------------------
        
    def make_mdl(self):
        # When the build generic model button is clicked this method is triggered. Depending on the selected device from the list the name of the model is defined
        # if there are fields that are not filled up or filled up with wrong information e.g: numeric/ text the error window will pops up
        #---------------------------------------------------------------------------------------------------------------------------------------------------------
        # Collect Simple Numeric Data and check for data error at the same time
        try: # check for wrong data_type if they are not numeric type the float method wont work
            self.Qrr=float(self.ui.ln_edit_qrr.text())
            self.Ciss=float(self.ui.ln_edit_ciss.text())
            self.Vpl=float(self.ui.ln_edit_vpl.text())
        except:
            # Notify user for wrong data_type
            QtGui.QMessageBox.warning(self, "Build Model", "Wrong data inputs detected, please input numeric data only")
            #--------------------------------
        if self.Qrr=='' or self.Ciss=='' or self.Vpl=='':
            # Check for No Data Inputs
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(" please input numeric data in the blanks")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        #-----------------------------
        # Get the string of selected device from Qlistview
        index = self.ui.lst_device.currentIndex().row()  
        name= str(self.list_model.item(index).text()).split('.')[0]
        #-------------------------------------------------
        # The list data error check are already done in the load methods (connected to buttons) thus we can build a dictionary for the model here 
        try: # check if list data are inputed correctly
            self.mdl={'Qrr': self.Qrr,'Ciss': self.Ciss,'Vpl': self.Vpl,'VthvsTj': self.vth_tj_params,'Crssvsvds':self.crss_params,'RdsvsTj':self.rd_tj_params}
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(" please input all of datasheet csv data using the load data buttons")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        #----------------------------------------------------------------------------------------------------------------------------------------
        # Save the method in *.pmdl file type
        save_file(self.mdl,os.path.join(self.model_dir, name + '.pmdl'))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Datasheet information added")
        msg.setWindowTitle("Success!")
        msg.setStandardButtons(QMessageBox.Ok)
        if msg.exec_():
            return
        #------------------------------------
    def enable_inputs(self):   
        # Enable Text if there is Device Selected
        self.ui.ln_edit_qrr.setEnabled(True)
        self.ui.ln_edit_ciss.setEnabled(True)
        self.ui.ln_edit_vpl.setEnabled(True)
        # Enable Buttons if there is Device Selected
        self.ui.btn_vth_vs_tj.setEnabled(True)
        self.ui.btn_crss_vs_vds.setEnabled(True)
        self.ui.btn_rds_vs_tj.setEnabled(True)
        self.ui.btn_buildgenericmdl.setEnabled(True)
    def load_selected_inputs(self):
        # when there is existed datasheet information, load the information to the blank line_edit
        # Get the string of selected device from Qlistview
        index = self.ui.lst_device.currentIndex().row()  
        name= str(self.list_model.item(index).text()).split('.')[0]
        #-------------------------------------------------
        # Get file_path from selected file
        file_path=os.path.join(self.model_dir,name+'.pmdl')
        if os.path.isfile(file_path):
            self.mdl=load_file(file_path)
            self.Qrr=self.mdl['Qrr']
            self.Ciss=self.mdl['Ciss']
            self.Vpl=self.mdl['Vpl']
            self.vth_tj_params=self.mdl['VthvsTj']
            self.crss_params=self.mdl['Crssvsvds']
            self.rd_tj_params=self.mdl['RdsvsTj']
            self.ui.ln_edit_qrr.setText(str(self.Qrr))
            self.ui.ln_edit_ciss.setText(str(self.Ciss))
            self.ui.ln_edit_vpl.setText(str(self.Vpl))
            self.ui.btn_vth_vs_tj.setText('Params Existed')
            self.ui.btn_rds_vs_tj.setText('Params Existed')
            self.ui.btn_crss_vs_vds.setText('Params Existed')
        else:
            self.ui.ln_edit_qrr.setText('')
            self.ui.ln_edit_ciss.setText('')
            self.ui.ln_edit_vpl.setText('')
            self.ui.btn_vth_vs_tj.setText('Load CSV here')
            self.ui.btn_rds_vs_tj.setText('Load CSV here')
            self.ui.btn_crss_vs_vds.setText('Load CSV here')
        #----------------------------------
        #-------------------------------------------------------------------------------------------
    def load_data_rd_tJ(self):
        # Load the CSV file for rdson data, the left column should be Tj while the right should be Rds (in the csv file)
        csv_file = QFileDialog.getOpenFileName(caption=r"CSV file", filter="Comma-separated values (*.csv)")    
        filedir = csv_file[0]
        tuple = ['Tj', 'Rds']
        try:
            rds_data = csv_load_file(filedir, tuple)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("In your CSV file set the left column as Tj and right column as Rds value")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        btn_name=os.path.basename(filedir)
        self.ui.btn_rds_vs_tj.setText(btn_name)
        [alpha, Ro] = rdson_fit_transistor(list2float(rds_data[0]), list2float(rds_data[1]))
        self.rd_tj_params=[alpha,Ro]    
        #----------------------------------------------------------------------------------------------------------------
    def load_data_vth_tj(self):
        # load Vth vs Tj data, left column is Tj, right column is Vth
        csv_file = QFileDialog.getOpenFileName(caption=r"CSV file", filter="Comma-separated values (*.csv)")   
        filedir = csv_file[0]
        tuple = ['Tj', 'Vth']
        try:
            Vth_dat = csv_load_file(filedir, tuple)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("In your CSV file set the left column as Tj and right column as Vth")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        btn_name=os.path.basename(filedir)
        self.ui.btn_vth_vs_tj.setText(btn_name)
        [a, b] = Vth_fit(list2float(Vth_dat[0]), list2float(Vth_dat[1])) 
        self.vth_tj_params=[a,b]   
        #-----------------------------------------------------------------
    def load_data_crss_vds(self):
        # load Crss vs vds data, left column is Vds, right column is Cap
        csv_file = QFileDialog.getOpenFileName(caption=r"CSV file", filter="Comma-separated values (*.csv)")   
        filedir = csv_file[0]
        tuple = ['Vds', 'Cap']
        try:
            crss_data = csv_load_file(filedir, tuple)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("In your CSV file set the left column as 'Vds' and right column as 'Cap' value")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        btn_name=os.path.basename(filedir)
        self.ui.btn_crss_vs_vds.setText(btn_name)
        [a1, b1, c1, a2, b2, c2] = fCRSS_fit(list2float(crss_data[0]), list2float(crss_data[1]))
        self.crss_params=[a1, b1, c1, a2, b2, c2]
        #---------------------------------------------------------------
    def change_page(self):        
        # Depends on device choices, the page will change accordingly to ask user for correct input data
        self.list_model = QStandardItemModel(self.ui.lst_device)
        choice= self.ui.cmb_device_choice.currentText()
        if choice =='Transistor':
            self.ui.stackedWidget.setCurrentIndex(1)    
        elif choice =='Diode':
            self.ui.stackedWidget.setCurrentIndex(0) 
        for f in os.listdir(self.dev_dir):
            filename=os.path.join(self.dev_dir,f)
            if os.path.isfile(filename):
                self.current_device = load_file(filename)
                if self.current_device.device_type==1 and choice=='Transistor':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_model.appendRow(item)
                elif self.current_device.device_type==2 and choice=='Diode':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_model.appendRow(item)    
        self.ui.lst_device.setModel(self.list_model)
        #------------------------------------------------------------------------------------------------
'''----------------------------------------End of GenericDeviceDialog ------------------------------------------'''
class DevicePropertiesDialog(QtGui.QDialog):
    def __init__(self,parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_device_propeties()
        self.ui.setupUi(self)
        self.parent = parent
        self.device_path=os.path.join(parent.project.tech_lib_dir,'Layout_Selection','Device')
        self.device_att_path=os.path.join(parent.project.tech_lib_dir, "Die_Attaches")
        # Connect method -- Read through to understand this is important to skim through each functions
        self.ui.cmb_device_type.currentIndexChanged.connect(self.change_display)
        #self.ui.btn_add.pressed.connect(self.add_to_device_table())
        self.list_dv_model = QStandardItemModel(self.ui.lst_devices)
        self.list_dv_att_model=QStandardItemModel(self.ui.lst_devices_att)
        self.dev_choice= self.ui.cmb_device_type.currentText()
        self.load_init_page()
    def load_init_page(self):
        model_choice= self.parent.ui.cmb_thermal.currentIndex()
        if model_choice==0 or model_choice==1:
            self.ui.stackedWidget.setCurrentIndex(0)
            self.load_device_physics()
            self.load_device_att()
        elif model_choice==2:
            self.ui.stackedWidget.setCurrentIndex(2)   
    def load_device_physics(self):
        for f in os.listdir(self.device_path):
            filename=os.path.join(self.device_path,f)
            if os.path.isfile(filename):
                self.current_device = load_file(filename)
                if self.current_device.device_type==1 and self.dev_choice=='Transistor':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_dv_model.appendRow(item)
                elif self.current_device.device_type==2 and self.dev_choice=='Diode':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_dv_model.appendRow(item)    
        self.ui.lst_devices.setModel(self.list_dv_model)
    def load_device_model(self): 
        print 1   
    def load_device_att(self):
        for f in os.listdir(self.device_att_path):
            filename=os.path.join(self.device_att_path,f)
            if os.path.isfile(filename):
                item = QStandardItem(f)
                item.setEditable(False)
                self.list_dv_att_model.appendRow(item)
        self.ui.lst_devices_att.setModel(self.list_dv_att_model)             
    def change_display(self):        
        # Depends on device choices, the page will change accordingly to ask user for correct input data 
        model_choice= self.parent.ui.cmb_thermal.currentIndex()
        if self.dev_choice =='Transistor' and (model_choice==0 or model_choice==1):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif self.dev_choice =='Transistor' and model_choice==2 :
            self.ui.stackedWidget.setCurrentIndex(2)
        elif self.dev_choice =='Diode' and (model_choice==0 or model_choice==1):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif self.dev_choice =='Diode' and model_choice==2:
            self.ui.stackedWidget.setCurrentIndex(1)
               
        #self.ui.lst_devices_att.setRootIndex(self.attach_list_model.setRootPath(die_attach_path))
'''----------------------------------------End of DevicePropertiesDialog ------------------------------------------'''
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

        self.filetype = None

        self.adv_netlist_args = {}
        self.ui.btn_symbnetfile.setEnabled(True)
        self.ui.txt_symbnet_address.setEnabled(True)
        self.ui.groupBox_advnetlist.setEnabled(True)
        self.ui.txt_dir.setEnabled(True)

        # Check user input as it is entered
        self.ui.txt_name.textChanged.connect(self.check)
        self.ui.txt_dir.textChanged.connect(self.check)
        self.ui.txt_symbnet_address.textChanged.connect(self.check)

        #self.ui.txt_positive_source.textChanged.connect(self.check)
        #self.ui.txt_negative_source.textChanged.connect(self.check)
        #self.ui.txt_output.textChanged.connect(self.check)
        #self.ui.dropdown_filetype.currentIndexChanged.connect(self.check)


        self.ui.btn_openDirectory.pressed.connect(self.open_dir)
        self.ui.btn_symbnetfile.pressed.connect(self.open_symbnet_file)
        self.ui.btn_net_import.pressed.connect(self.import_netlist)
        self.ui.btn_cancel.pressed.connect(self.reject)
        self.ui.btn_create.pressed.connect(self.accept)
    def import_netlist(self):

        file_dir = QFileDialog.getOpenFileName(self, "Select Netlist",
                                                   self.ui.txt_symbnet_address.text(),
                                                   "Script Files (*.txt *.net)")
        self.ui.txt_symbnet_address_2.setText(file_dir[0])


    def check(self):
        # Check for valid netlist details
        valid_netlist_details = False
        if self.filetype == 'netlist' and self.ui.txt_symbnet_address.text() != '':  # if netlist filetype is chosen and the "select file" text area is not empty,
            valid_netlist_details = self.check_netlist_details()  # check netlist details entered.

        # Enable/Disable 'Create Project' button
        # Disable if either of the three text areas is empty: Project Name, Project Directory, Select file
        if (len(self.ui.txt_name.text()) == 0) or (len(self.ui.txt_dir.text()) == 0) or (
                    len(self.ui.txt_symbnet_address.text()) == 0):
            self.ui.btn_create.setEnabled(False)
        # Disable if either of the three node names are not provided when filetype has been chosen as netlist
        elif self.filetype == 'netlist' and (
                        (len(self.ui.txt_positive_source.text()) == 0) or (
                        len(self.ui.txt_negative_source.text()) == 0) or (
                            len(self.ui.txt_output.text()) == 0)):
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
        if self.ui.txt_positive_source.text() in open(
                self.ui.txt_symbnet_address.text()).read():  # check if the positive source node is included in the netlist file.
            invalid_pos_src = False
        if self.ui.txt_negative_source.text() in open(
                self.ui.txt_symbnet_address.text()).read():  # check if the negative source node is included in the netlist file.
            invalid_neg_src = False
        if self.ui.txt_output.text() in open(
                self.ui.txt_symbnet_address.text()).read():  # check if the output node is included in the netlist file.
            invalid_output_node = False

        if invalid_pos_src:
            self.ui.err_pos_src.setText('Source not found in netlist')
        elif self.ui.txt_positive_source.text() != '' and (
                        self.ui.txt_positive_source.text() == self.ui.txt_negative_source.text()
                or self.ui.txt_positive_source.text() == self.ui.txt_output.text()):
            self.ui.err_pos_src.setText('Source name may only be used once')
        else:
            self.ui.err_pos_src.setText(' ')

        if invalid_neg_src:
            self.ui.err_neg_src.setText('Source not found in netlist')
        elif self.ui.txt_negative_source.text() != '' and (
                        self.ui.txt_negative_source.text() == self.ui.txt_positive_source.text()
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
        self.parent.layout_script_dir = directory

    def open_symbnet_file(self):
        self.filetype='script'
        if self.filetype == 'svg' or self.filetype == 'script':
            if self.filetype == 'svg':
                symbnet_file = QFileDialog.getOpenFileName(self, "Select Symbolic Layout",
                                                           self.ui.txt_symbnet_address.text(), "SVG Files (*.svg)")
            if self.filetype == 'script':
                symbnet_file = QFileDialog.getOpenFileName(self, "Select Symbolic Layout",
                                                           self.ui.txt_symbnet_address.text(),
                                                           "Script Files (*.txt *.psc)")
            file_name, file_extension = os.path.splitext(symbnet_file[0])
            if file_extension == '.svg':
                self.ui.txt_symbnet_address.setText(os.path.abspath(symbnet_file[0]))
            elif file_extension == '.txt' or file_extension == '.psc':
                self.ui.txt_symbnet_address.setText(os.path.abspath(symbnet_file[0]))
    '''
    def convert_netlist(self):
        # Prepares for conversion
        # Converts datatype of positive, negative, and output nodes from object attributes into strings
        netlist_file_name, netlist_file_extension = os.path.splitext(
            self.ui.txt_symbnet_address.text())  # separates the file path and file name combination from the file extension (.txt or .net)
        converter = Netlist_SVG_converter.Converter(self.ui.txt_symbnet_address.text(),
                                                    netlist_file_name)  # initializes the converter object with the specific source's file path and file name
        # Converts from netlist to svg
        symbnet_file = converter.convert(vp=str(self.ui.txt_positive_source.text()),
                                         # the positive source node mentioned by the user is converted to string type and saved in variable vp
                                         vn=str(self.ui.txt_negative_source.text()),
                                         # the negative source node mentioned by the user is converted to string type and saved in variable vn
                                         output_node=str(
                                             self.ui.txt_output.text()))  # the output node mentioned by the user is converted to string type and saved in variable output_node

        NetlistConverter = Netlist_SVG_converter.Converter(self.ui.txt_symbnet_address.text(), netlist_file_name)
        symbnet_file = NetlistConverter.convert(vp=str(self.ui.txt_positive_source.text()),
                                                vn=str(self.ui.txt_negative_source.text()),
                                                output_node=str(self.ui.txt_output.text()))

        return os.path.abspath(symbnet_file[0])  # Shilpi - return the converted file
    '''
    def create(self):
        # Save most recent entries
        # If netlist, create symbolic layout
        if self.filetype == 'netlist':
            self.net_to_svg_file = self.convert_netlist()  # sxm- save the newly created svg file.
            print "netlist converted to svg."
        # print "net_to_svg_file= ", self.net_to_svg_file

        # Read in symbolic layout
        symb_layout = SymbolicLayout()
        if self.filetype == 'netlist':
            symb_layout.load_layout(self.net_to_svg_file,
                                    'svg')  # sxm- convert the svg that was obtained from netlist to a symbolic layout.
        elif self.filetype == 'svg':
            symb_layout.load_layout(self.ui.txt_symbnet_address.text(),
                                    'svg')  # sxm- convert the original svg to a symbolic layout.
        elif self.filetype == 'script':
            symb_layout.load_layout(self.ui.txt_symbnet_address.text(),
                                    'script')  # qmle-- read the script and directly build the layout
        print "symbolic layout created."
        try:
            netlist = Netlist(netlist_file=self.ui.txt_symbnet_address_2.text())
        except:
            netlist = None
        # Create project
        if netlist==None:
            Notifier(msg='You did not import a netlist, you will need to assign netname in the UI !',msg_name='Reminder')
        proj_dir =os.path.join(self.ui.txt_dir.text(),self.ui.txt_name.text())
        return Project(self.ui.txt_name.text(), proj_dir, DEFAULT_TECH_LIB_DIR, netlist,symb_layout)


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
            
    def open_dir(self): # responds to button click by opening a file browser where the project directory can be selected
        prev_folder = 'C://'
        if not os.path.exists(prev_folder):  # check if the last entry file store a correct path
            prev_folder = 'C://'
        self.project_file = QFileDialog.getOpenFileName(self, "Select Project File",prev_folder,"Project Files (*.p)")
        self.ui.txt_projectLocation.setText(self.project_file[0])
        self.parent.layout_script_dir=os.path.dirname(self.project_file[0])


    def load_project(self): # loads the project selected into the main view
        try:
            self.parent.project = load_file(self.project_file[0])
            
            # Add constraints field to any objects which lack it
            self.parent.project.symb_layout.add_constraints()
            
            # Check if project object contains tech_lib_dir field (if not add it)
            if not hasattr(self.parent.project, 'tech_lib_dir'):
                self.parent.project.tech_lib_dir = DEFAULT_TECH_LIB_DIR

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
        
        '''Edit the Tech lib path should reload the combo boxes on the moudle stacks'''# Quang
          
        self.parent.fill_material_cmbBoxes()    # Quang
        self.parent.load_moduleStack()          # Quang

class LayoutEditorDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_layouteditorDialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.load_layout_script()
        self.ui.btn_reload.pressed.connect(self.reload_sym)
    def load_layout_script(self):
        self.ui.text_layout_script.setFont(QFont("Courier", 12))
        self.ui.text_layout_script.setText(self.parent.layout_script)
    def reload_sym(self): 
        self.parent.layout_script=self.ui.text_layout_script.toPlainText()
        path=os.path.join(self.parent.layout_script_dir,'layout.psc')
        f=open(path,'wb')
        f.write(self.parent.layout_script)
        self.close()

class ResponseSurfaceDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ResponseSurface()
        self.ui.setupUi(self)
        self.parent = parent
        self.layer_stack_import = None
        self.DOE = 'mesh'
        # Suggested Min Max ranges
        self.ui.lineEdit_maxL.setText('40')
        self.ui.lineEdit_maxW.setText('40')
        self.ui.lineEdit_fmin.setText('10')
        self.ui.lineEdit_fmax.setText('1000')
        # Initialization, only load layer stack button is enabled
        # 1 buttons:
        self.ui.btn_build.setEnabled(False)
        # 2 text_edit:
        self.ui.lineEdit_maxL.setEnabled(False)
        self.ui.lineEdit_maxW.setEnabled(False)
        self.ui.lineEdit_fmin.setEnabled(False)
        self.ui.lineEdit_fmax.setEnabled(False)
        # 3 cmb list
        #self.ui.cmb_DOE.setEnabled(False)
        self.ui.cmb_sims.setEnabled(False)

        # 4 connecting signals
        self.ui.btn_add_layer_stack.pressed.connect(self.importlayerstack)
        self.ui.btn_build.pressed.connect(self.build)
        self.ui.list_mdl_lib.clicked.connect(self.show_mdl_info)
        #self.ui.cmb_DOE.currentIndexChanged.connect(self.set_up_DOE)

        # populate model files
        self.model_dir = os.path.join(DEFAULT_TECH_LIB_DIR, 'Model', 'Trace')
        self.rs_model = QtGui.QFileSystemModel()
        self.rs_model.setRootPath(self.model_dir)
        self.rs_model.setFilter(QtCore.QDir.Files)
        self.ui.list_mdl_lib.setModel(self.rs_model)
        self.ui.list_mdl_lib.setRootIndex(self.rs_model.setRootPath(self.model_dir))
        self.wp_dir = os.path.join(EXPORT_DATA_PATH, 'workspace', 'RS')

    def importlayerstack(self):
        prev_folder = 'C://'
        layer_stack_csv_file = QFileDialog.getOpenFileName(self, "Select Layer Stack File", prev_folder,
                                                           "CSV Files (*.csv)")
        layer_stack_csv_file = layer_stack_csv_file[0]
        self.layer_stack_import = LayerStackImport(layer_stack_csv_file)
        self.layer_stack_import.import_csv()
        if self.layer_stack_import.compatible:
            Notifier(msg="Sucessfully Imported Layer Stack File", msg_name="Success!!!")
            # 1 buttons:
            self.ui.btn_build.setEnabled(True)
            # 2 text_edit:
            self.ui.lineEdit_maxL.setEnabled(True)
            self.ui.lineEdit_maxW.setEnabled(True)
            self.ui.lineEdit_fmin.setEnabled(True)
            self.ui.lineEdit_fmax.setEnabled(True)
            # 3 cmb list
            self.ui.cmb_sims.setEnabled(True)
        else:
            InputError(msg="Layer Stack format is not compatible")

    def refresh_mdl_list(self):
        self.rs_model.setRootPath(self.model_dir)
        self.rs_model.setFilter(QtCore.QDir.Files)
        self.ui.list_mdl_lib.setModel(self.rs_model)
        self.ui.list_mdl_lib.setRootIndex(self.rs_model.setRootPath(self.model_dir))

    def build(self):
        # check all input types:
        minL = self.parent.project.module_data.design_rules.min_trace_width
        maxL = self.ui.lineEdit_maxL.text()
        minW = self.parent.project.module_data.design_rules.min_trace_width
        maxW = self.ui.lineEdit_maxW.text()
        fmin = self.ui.lineEdit_fmin.text()
        fmax = self.ui.lineEdit_fmax.text()

        mdl_name = self.ui.lineEdit_name.text()
        checknum = maxL.isdigit()  or maxW.isdigit() or fmin.isdigit() or fmax.isdigit()
        self.DOE='mesh'
        self.sims = str(self.ui.cmb_sims.currentText())
        options = [self.sims, self.DOE, False]
        if not (checknum):
            InputError(msg="not all inputs for width length and frequency are numeric, double check please")
            return
        else:

            all_num = [minL, maxL, minW, maxW]
            minL, maxL, minW, maxW = [float(x) for x in all_num]
            fmin,fmax=[int(x) for x in [fmin,fmax]]
            w_range=[minW, maxW]
            l_range=[minL, maxL]

            if self.ui.cmb_sims.currentText()=="Q3D":
                fstep = 10
                f_range = [fmin, fmax, fstep]

                env_dir = os.path.join(ANSYS_IPY64, 'ipy164.exe')
                if os.path.isfile(env_dir):
                    form_trace_model_optimetric(layer_stack=self.layer_stack_import, Width=w_range, Length=l_range,
                                                freq=f_range, wdir=self.wp_dir, savedir=self.model_dir,
                                                mdl_name=mdl_name
                                                , env=env_dir, options=options)
                else:
                    env_dir=QFileDialog.getOpenFileName(caption=r"Find ANSYS Q3D IPY dir", filter="(*.exe)")
                    print env_dir[0]
                    env_dir=os.path.abspath(env_dir[0])
                    version=psidialogs.ask_string("what is the ANSYS version (folder name ANSYSEM...)")
                    print version
                    form_trace_model_optimetric(layer_stack=self.layer_stack_import, Width=w_range, Length=l_range,
                                                freq=f_range, wdir=self.wp_dir, savedir=self.model_dir,
                                                mdl_name=mdl_name
                                                , env=env_dir, options=options,version=version)
            elif self.ui.cmb_sims.currentText()=="FastHenry":
                fstep = 100
                f_range = [fmin, fmax, fstep]
                exe=['fasthenry.exe','ReadOutput.exe']
                env_dir=[os.path.join(FASTHENRY_FOLDER,x) for x in exe]
                form_fasthenry_trace_response_surface(layer_stack=self.layer_stack_import,Width=w_range,Length=l_range,
                                                      freq=f_range,wdir=self.wp_dir, savedir=self.model_dir,mdl_name=mdl_name,
                                                      env=env_dir)
            self.refresh_mdl_list()

    def set_up_DOE(self):
        if self.ui.cmb_DOE.currentText() == "Mesh":
            self.DOE = "mesh"  # add DOE option later fix for now
        elif self.ui.cmb_DOE.currentText() == "Center Composite":
            self.DOE = "cc"  # add DOE option later fix for now

    def show_mdl_info(self):
        selected = str(self.rs_model.fileName(self.ui.list_mdl_lib.currentIndex()))
        mdl = load_file(os.path.join(self.model_dir, selected))
        text = mdl['info']
        self.ui.text_edt_model_info.setText(text)
        self.ui.list_mdl_lib.currentIndex()


class ModelSelectionDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ModelSelection()
        self.ui.setupUi(self)
        self.parent = parent
        # populate model files
        self.model_dir = os.path.join(DEFAULT_TECH_LIB_DIR, 'Model', 'Trace')
        self.rs_model = QtGui.QFileSystemModel()
        self.rs_model.setRootPath(self.model_dir)
        self.rs_model.setFilter(QtCore.QDir.Files)
        self.ui.list_mdl_choices.setModel(self.rs_model)
        self.ui.list_mdl_choices.setRootIndex(self.rs_model.setRootPath(self.model_dir))
        self.ui.buttonBox.accepted.connect(self.select_mdl)

    def show_mdl_info(self):
        selected=str(self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex()))
        mdl = load_file(os.path.join(self.model_dir,selected))
        text=mdl['info']
        self.ui.textEdit.setText(text)
        self.ui.list_mdl_choices.currentIndex()

    def select_mdl(self):
        try:
            self.model=load_file(os.path.join(self.model_dir,self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex())))
            self.parent.project.symb_layout.set_RS_model(self.model)
            Notifier(msg="model is set to: "+str(self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex())),msg_name="model selected")
        except:
            InputError(msg="Unexpected error:"+str(sys.exc_info()[0]))

class EnvironmentSetupDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_EnvSetup()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.cmb_env.currentIndexChanged.connect(self.show_path)
        self.ui.btn_selectdir.pressed.connect(self.open_dir)
        self.ui.btn_update.pressed.connect(self.update)
        self.ui.txt_dir.setText(GMSH_BIN_PATH)

    def show_path(self):
        with open(SETTINGS_TXT) as f:
            data=f.readlines()
            self.ui.txt_dir.setText(data[self.ui.cmb_env.currentIndex()])

    def open_dir(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select BIN folder", "C://"))
        if os.path.isdir(folder):
            self.ui.txt_dir.setText(folder)

    def update(self):
        with open(SETTINGS_TXT,'r') as f:
            data = f.readlines()
            data[self.ui.cmb_env.currentIndex()]=self.ui.txt_dir.text()
        f.close()

        with open(SETTINGS_TXT,'w') as f:
            for i in range(len(data)):
                data[i]=data[i].strip('\n')
                f.write(data[i]+'\n')
        Notifier(msg="Update Binary complete",msg_name="Complete!")

class SetupDeviceDialogs(QtGui.QDialog):
    def __init__(self, parent,mode=1):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_setup_device()
        self.ui.setupUi(self)
        self.ui.lst_devices_att.setEnabled(True)
        self.parent = parent
        self.device=None
        # SETUP DIE ATTACH
        self.mode=mode
        self.attach_path=os.path.join(self.parent.project.tech_lib_dir, "Device_Selection","Die_Attaches")
        self.attach_list_model=QtGui.QFileSystemModel()
        self.attach_list_model.setRootPath(self.attach_path)
        self.attach_list_model.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self.ui.lst_devices_att.setModel(self.attach_list_model)
        self.ui.lst_devices_att.setRootIndex(self.attach_list_model.setRootPath(self.attach_path))

        # UNABLE BUTTONS AND TEXT EDIT
        self.ui.txt_devAttchThickness.setEnabled(False)
        self.ui.txt_device_heat_flow.setEnabled(False)
        # SETUP EVENTS
        self.ui.lst_devices_att.clicked.connect(self.input_heat_flow)
        self.ui.btn_update_dev_setup.pressed.connect(self.return_device_setup)

    def _check_field(self, field, func, error_title, error_msg):
        try:
            func(field.text())
            return False
        except:
            QtGui.QMessageBox.warning(self, error_title, error_msg)
            return True
    def input_heat_flow(self):
        self.ui.txt_device_heat_flow.setEnabled(True)
        self.ui.txt_devAttchThickness.setEnabled(True)

    def _check_device_fields(self):
        error1 = self._check_field(self.ui.txt_devAttchThickness, float, "Component", "Must enter a numeric value for Attach Thickness")
        error2 = self._check_field(self.ui.txt_device_heat_flow, float, "Component", "Must enter a numeric value for Device Heat Flow")
        return error1 or error2

    def check_device_error(self):
        error = False
        if self.ui.lst_devices_att.selectionModel().selectedIndexes() == []:
            error = True
            QtGui.QMessageBox.warning(self, "Add Component", "No Attach Material selected for device")
        if self._check_device_fields():
            error=True
        return  error

    def return_device_setup(self,mode="ADD"):
        if not (self.check_device_error()):
            if self.mode ==1:
                item = self.parent.ui.lst_devices.selectionModel().selectedIndexes()[0]
                tech_obj = load_file(self.parent.device_list_model.rootPath() + '/' + item.model().data(item))
                heat_flow = float(self.ui.txt_device_heat_flow.text())
                item2 = self.ui.lst_devices_att.selectionModel().selectedIndexes()[0]
                # Load attach tech lib object
                attch_tech_obj = load_file(self.attach_list_model.rootPath() + '/' + item2.model().data(item2))
                attch_thick = float(self.ui.txt_devAttchThickness.text())
                self.parent.ui.btn_addDevice.setEnabled(True)
                # ADD NEW DEVICE TO TABLE
                row_count = self.parent.ui.tbl_projDevices.rowCount()
                self.parent.ui.tbl_projDevices.insertRow(row_count)
                self.parent.ui.tbl_projDevices.setItem(row_count, 0, QtGui.QTableWidgetItem())
                self.parent.ui.tbl_projDevices.item(row_count, 0).setBackground(QtGui.QBrush(self.parent.color_wheel[self.parent.cw1 - 1]))
                self.parent.ui.tbl_projDevices.setItem(row_count, 1, QtGui.QTableWidgetItem())
                self.parent.ui.tbl_projDevices.item(row_count, 1).setText('  ' + item.model().data(item))
                self.parent.ui.tbl_projDevices.item(row_count, 1).tech = DeviceInstance(attch_thick, heat_flow, tech_obj, attch_tech_obj)
                self.close()
            elif self.mode ==2:
                """Save updated device heat flow and attach thickness by reading in the current values from the text entered by the user."""
                selected_row = self.parent.ui.tbl_projDevices.currentRow()
                row_item = self.parent.ui.tbl_projDevices.item(selected_row, 1)
                if isinstance(row_item.tech, DeviceInstance):
                    error = self._check_device_fields()
                    if not error:
                        row_item.tech.heat_flow = float(self.ui.txt_device_heat_flow.text())
                        row_item.tech.attach_thickness = float(self.ui.txt_devAttchThickness.text())
                self.close()
            print "return device and wires"

class WireConnectionDialogs(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Bondwire_setup()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.btn_add.setEnabled(False)

        #SAVE PARENT SYMB CANVAS
        parent_canvas=self.parent.symb_canvas[0]
        parent_axis=self.parent.symb_axis[0]
        parent_fig=self.parent.symb_fig[0]
        self.parent_data=[parent_canvas,parent_axis,parent_fig]
        # BUTTON EVENTs
        self.ui.btn_add.pressed.connect(self.add_item)
        self.ui.btn_remove.pressed.connect(self.remove_item)

        self.parent.symb_canvas[0].mpl_disconnect(self.parent.select_comp)
        self.select = self.parent.symb_canvas[0].mpl_connect('pick_event', self.device_pick)
        self.load_table()
        self.bond_conn=[]
        self.event_list=[]

    def load_table(self):
        table_df=self.parent.project.tbl_bondwire_connect
        if isinstance(table_df, types.NoneType) == False:
            total_rows = len(table_df.axes[0])
            for r in range(total_rows):
                self.ui.tbl_bw_connection.insertRow(r)
                self.ui.tbl_bw_connection.setItem(r, 0, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 1, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 2, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 3, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.item(r, 0).setText(table_df.loc[r,0])
                self.ui.tbl_bw_connection.item(r, 1).setText(str(table_df.loc[r,1]))
                self.ui.tbl_bw_connection.item(r, 2).setText(str(table_df.loc[r,2]))
                self.ui.tbl_bw_connection.item(r, 3).setText(table_df.loc[r,3])
                self.ui.tbl_bw_connection.item(r, 3).tech=table_df.loc[r, 4]


    def device_pick(self,event):
        layout_obj = self.parent.patch_dict.get_layout_obj(event.artist)
        if event.artist.get_hatch() == '///':
            event.artist.set_hatch('')
            self.bond_conn.remove(layout_obj)
            self.event_list.remove(event.artist)
        elif len(self.bond_conn)<=1:
            event.artist.set_hatch('///')
            self.event_list.append(event.artist)
            self.bond_conn.append(layout_obj)
        self.parent.symb_canvas[0].draw()
        if len(self.bond_conn)==2:
            self.ui.btn_add.setEnabled(True)
        else:
            self.ui.btn_add.setEnabled(False)

    def closeEvent(self,event):
        self.parent.symb_canvas[0].mpl_disconnect(self.select)
        self.parent.select_comp=self.parent.symb_canvas[0].mpl_connect('pick_event',self.parent.device_pick)
        table_df=pd.DataFrame(columns=['bw_type','start','stop','obj'])
        for row in range(self.ui.tbl_bw_connection.rowCount()):
            for col in range(self.ui.tbl_bw_connection.columnCount()):
                table_df.loc[row, col] = self.ui.tbl_bw_connection.item(row, col).text()
            table_df.loc[row, 4]=self.ui.tbl_bw_connection.item(row, 3).tech # Fir
        self.parent.project.tbl_bondwire_connect=table_df
        for patch in self.event_list:
            patch.set_hatch('')
        self.event_list = []
        self.bond_conn = []
        self.parent.symb_canvas[0].draw()
    def add_item(self):
        row_count = self.ui.tbl_bw_connection.rowCount()
        self.ui.tbl_bw_connection.insertRow(row_count)
        self.ui.tbl_bw_connection.setItem(row_count, 0, QtGui.QTableWidgetItem())
        self.ui.tbl_bw_connection.setItem(row_count, 1, QtGui.QTableWidgetItem())
        self.ui.tbl_bw_connection.setItem(row_count, 2, QtGui.QTableWidgetItem())
        self.ui.tbl_bw_connection.setItem(row_count, 3, QtGui.QTableWidgetItem())
        try:
            item = self.parent.ui.lst_devices.selectionModel().selectedIndexes()[0]
            tech_obj = load_file(self.parent.device_list_model.rootPath() + '/' + item.model().data(item))
        except:
            InputError(msg="Please select a bondwire object on from the list")
            # clear everything to select again
            for patch in self.event_list:
                patch.set_hatch('')
            self.event_list = []
            self.bond_conn = []
            self.parent.symb_canvas[0].draw()
            return
        if tech_obj.wire_type==1:
            type='POWER'
        elif tech_obj.wire_type==2:
            type='SIGNAL'

        self.ui.tbl_bw_connection.item(row_count, 0).setText(type)
        self.ui.tbl_bw_connection.item(row_count, 1).setText(str(self.bond_conn[0].name))
        self.ui.tbl_bw_connection.item(row_count, 2).setText(str(self.bond_conn[1].name))
        self.ui.tbl_bw_connection.item(row_count, 3).setText(' '+item.model().data(item))
        self.ui.tbl_bw_connection.item(row_count, 3).tech = tech_obj
        for patch in self.event_list:
            patch.set_hatch('')
        self.ui.btn_add.setEnabled(False)
        self.event_list=[]
        self.bond_conn=[]
        self.parent.symb_canvas[0].draw()
    def remove_item(self):
        print "ITEM REMOVED"
        selected_row = self.ui.tbl_bw_connection.currentRow()
        self.ui.tbl_bw_connection.selectionModel().selectedIndexes()[0].row()
        self.ui.tbl_bw_connection.removeRow(selected_row)

class Device_states_dialog(QtGui.QDialog):
    def __init__(self,parent,per_ui):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_dev_state_dialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.per_ui=per_ui
        self.ui.btn_ok.pressed.connect(self.Ok)
        self.dv_df=pd.DataFrame()
        self.group=QtGui.QButtonGroup()

        self.load_table()

    def closeEvent(self,event):
        self.Ok()

    def load_table(self):
        for dv in self.parent.project.symb_layout.all_sym:
            if isinstance(dv, SymPoint):
                if dv.tech == None:
                    Notifier("Not all devices have technology file, please go to the previous page to select", "Error")
                    return
                elif isinstance(dv.tech, DeviceInstance):
                    row_count = self.ui.tbl_states.rowCount()
                    self.ui.tbl_states.insertRow(row_count)
                    self.ui.tbl_states.setItem(row_count, 0, QtGui.QTableWidgetItem())
                    if dv.name!=None:
                        self.ui.tbl_states.item(row_count, 0).setText(dv.name)
                    else:
                        self.ui.tbl_states.item(row_count, 0).setText(dv.element.path_id)



                    if dv.is_transistor():
                        # add 3 collumns:

                        btn_state1 = QtGui.QCheckBox(self.ui.tbl_states)
                        btn_state1.setText('D-S')

                        self.ui.tbl_states.setCellWidget(row_count, 1, btn_state1)  # Drain to source
                        btn_state2 = QtGui.QCheckBox(self.ui.tbl_states)
                        btn_state2.setText('G-S')
                        self.ui.tbl_states.setCellWidget(row_count, 2, btn_state2)
                        btn_state3 = QtGui.QCheckBox(self.ui.tbl_states)
                        btn_state3.setText('G-D')
                        self.ui.tbl_states.setCellWidget(row_count, 3, btn_state3)
                        self.group.addButton(btn_state1)
                        self.group.addButton(btn_state2)
                        self.group.addButton(btn_state3)
                    elif dv.is_diode():
                        btn_state = QtGui.QCheckBox(self.ui.tbl_states)
                        btn_state.setText('A-C')
                        self.ui.tbl_states.setCellWidget(row_count, 1, btn_state) # Drain to source
                        self.group.addButton(btn_state)


        self.group.setExclusive(False)
    def Ok(self):
        for row in range(self.ui.tbl_states.rowCount()):
            for col in range(self.ui.tbl_states.columnCount()):
                if col ==0:
                    self.dv_df.loc[row,col]=self.ui.tbl_states.item(row, col).text()
                else:
                    if self.ui.tbl_states.cellWidget(row, col)!=None:
                        self.dv_df.loc[row, col]= int(self.ui.tbl_states.cellWidget(row, col).isChecked()*1)
        self.per_ui.device_states_df=self.dv_df

        self.close()
