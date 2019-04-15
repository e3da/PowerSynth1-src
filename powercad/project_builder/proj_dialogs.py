'''
Created on Oct 12, 2012

@author: Peter N. Tucker, qmle, Imam Al Razi
'''
# IMPORT METHODS
import os
import traceback
import pandas as pd
import random
import types
import numpy as np
from PySide.QtGui import QFileDialog, QStandardItemModel, QStandardItem, QMessageBox, QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import powercad.sym_layout.plot as plot
from powercad.project_builder.dialogs.propertiesDeviceDialog import Ui_device_propeties
from powercad.Spice_handler.spice_import.NetlistImport import Netlist
import copy

# plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4'] = 'PySide'
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
from powercad.project_builder.dialogs.CS_design_up_ui import Ui_CornerStitch_Dialog  # CS_design_ui
from powercad.project_builder.dialogs.Fixed_loc_up_ui import Ui_Fixed_location_Dialog  # Fixed_loc_ui
from powercad.project_builder.project import Project
from powercad.sym_layout.symbolic_layout import SymbolicLayout, plot_layout
from powercad.general.settings.settings import DEFAULT_TECH_LIB_DIR, EXPORT_DATA_PATH, ANSYS_IPY64, FASTHENRY_FOLDER, \
    GMSH_BIN_PATH, ELMER_BIN_PATH
from powercad.electro_thermal.ElectroThermal_toolbox import rdson_fit_transistor, list2float, csv_load_file, Vth_fit, \
    fCRSS_fit
from powercad.general.settings.save_and_load import save_file, load_file
from powercad.project_builder.dialogs.ResponseSurface import Ui_ResponseSurface
from powercad.project_builder.dialogs.ModelSelection import Ui_ModelSelection
from powercad.project_builder.dialogs.ET_evaluate_up_ui import Ui_ET_Evaluation_Dialog  # ET_evaluate_ui
from powercad.project_builder.dialogs.waiting_ui import Ui_waiting_dialog
from powercad.layer_stack.layer_stack_import import *
from powercad.general.settings.Error_messages import *
from PySide import QtCore, QtGui
from powercad.sym_layout.symbolic_layout import SymPoint, ElectricalMeasure, ThermalMeasure, LayoutError
from powercad.project_builder.dialogs.cons_setup_ui import Ui_Constraint_setup
from powercad.response_surface.Model_Formulation import form_trace_model_optimetric, \
    form_fasthenry_trace_response_surface
from powercad.parasitics.analysis import parasitic_analysis
import psidialogs
from numpy.linalg.linalg import LinAlgError
from powercad.corner_stitch.optimization_setup import OptSetup
import networkx as nx
from powercad.design.module_data import *
from powercad.corner_stitch.CornerStitch import Rectangle
from powercad.general.data_struct.util import *
from powercad.sol_browser.solution import Solution
from powercad.interfaces.EMPro.EMProExport import EMProScript
from powercad.interfaces.FastHenry.fh_layers import output_fh_script
from powercad.interfaces.Q3D.Q3D import output_q3d_vbscript
from powercad.interfaces.Solidworks.solidworks import output_solidworks_vbscript
from powercad.design.module_design import ModuleDesign
from powercad.opt.optimizer import NSGAII_Optimizer, DesignVar


# CLASSES FOR DIALOG USAGE
class GenericDeviceDialog(QtGui.QDialog):
    # Author: quang le
    # Date: 9-27-2016
    def __init__(self, parent, device_dir):
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
        self.dev_dir = device_dir
        # ---------------------------------------------------------
        # Initially, the Build_Generic_Model button is disabled
        self.ui.btn_buildgenericmdl.setEnabled(False)
        # ---------------------------------------------------------
        # Connect method -- Read through to understand this is important to skim through each functions
        self.ui.btn_buildgenericmdl.pressed.connect(self.make_mdl)
        self.ui.cmb_device_choice.currentIndexChanged.connect(self.change_page)
        self.ui.lst_device.clicked.connect(self.enable_inputs)
        self.ui.lst_device.clicked.connect(self.load_selected_inputs)
        self.ui.btn_rds_vs_tj.pressed.connect(self.load_data_rd_tJ)
        self.ui.btn_vth_vs_tj.pressed.connect(self.load_data_vth_tj)
        self.ui.btn_crss_vs_vds.pressed.connect(self.load_data_crss_vds)
        # ----------------------------------------------------------------------------------------------
        # Disable Text if there is no Device Selected
        self.ui.ln_edit_qrr.setEnabled(False)
        self.ui.ln_edit_ciss.setEnabled(False)
        self.ui.ln_edit_vpl.setEnabled(False)
        # --------------------------------------------
        # Disable Buttons if there is no Device Selected
        self.ui.btn_vth_vs_tj.setEnabled(False)
        self.ui.btn_crss_vs_vds.setEnabled(False)
        self.ui.btn_rds_vs_tj.setEnabled(False)
        # -----------------------------------------------
        # Set up Device Field
        self.change_page()
        # --------------------
        # Setup Directory for models
        self.model_dir = os.path.join(self.dev_dir, 'Device_PModel')
        # ---------------------------

    def make_mdl(self):
        # When the build generic model button is clicked this method is triggered. Depending on the selected device from the list the name of the model is defined
        # if there are fields that are not filled up or filled up with wrong information e.g: numeric/ text the error window will pops up
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------
        # Collect Simple Numeric Data and check for data error at the same time
        try:  # check for wrong data_type if they are not numeric type the float method wont work
            self.Qrr = float(self.ui.ln_edit_qrr.text())
            self.Ciss = float(self.ui.ln_edit_ciss.text())
            self.Vpl = float(self.ui.ln_edit_vpl.text())
        except:
            # Notify user for wrong data_type
            QtGui.QMessageBox.warning(self, "Build Model", "Wrong data inputs detected, please input numeric data only")
            # --------------------------------
        if self.Qrr == '' or self.Ciss == '' or self.Vpl == '':
            # Check for No Data Inputs
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(" please input numeric data in the blanks")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        # -----------------------------
        # Get the string of selected device from Qlistview
        index = self.ui.lst_device.currentIndex().row()
        name = str(self.list_model.item(index).text()).split('.')[0]
        # -------------------------------------------------
        # The list data error check are already done in the load methods (connected to buttons) thus we can build a dictionary for the model here
        try:  # check if list data are inputed correctly
            self.mdl = {'Qrr': self.Qrr, 'Ciss': self.Ciss, 'Vpl': self.Vpl, 'VthvsTj': self.vth_tj_params,
                        'Crssvsvds': self.crss_params, 'RdsvsTj': self.rd_tj_params}
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(" please input all of datasheet csv data using the load data buttons")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            if msg.exec_():
                return
        # ----------------------------------------------------------------------------------------------------------------------------------------
        # Save the method in *.pmdl file type
        save_file(self.mdl, os.path.join(self.model_dir, name + '.pmdl'))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Datasheet information added")
        msg.setWindowTitle("Success!")
        msg.setStandardButtons(QMessageBox.Ok)
        if msg.exec_():
            return
        # ------------------------------------

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
        name = str(self.list_model.item(index).text()).split('.')[0]
        # -------------------------------------------------
        # Get file_path from selected file
        file_path = os.path.join(self.model_dir, name + '.pmdl')
        if os.path.isfile(file_path):
            self.mdl = load_file(file_path)
            self.Qrr = self.mdl['Qrr']
            self.Ciss = self.mdl['Ciss']
            self.Vpl = self.mdl['Vpl']
            self.vth_tj_params = self.mdl['VthvsTj']
            self.crss_params = self.mdl['Crssvsvds']
            self.rd_tj_params = self.mdl['RdsvsTj']
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
        # ----------------------------------
        # -------------------------------------------------------------------------------------------

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
        btn_name = os.path.basename(filedir)
        self.ui.btn_rds_vs_tj.setText(btn_name)
        [alpha, Ro] = rdson_fit_transistor(list2float(rds_data[0]), list2float(rds_data[1]))
        self.rd_tj_params = [alpha, Ro]
        # ----------------------------------------------------------------------------------------------------------------

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
        btn_name = os.path.basename(filedir)
        self.ui.btn_vth_vs_tj.setText(btn_name)
        [a, b] = Vth_fit(list2float(Vth_dat[0]), list2float(Vth_dat[1]))
        self.vth_tj_params = [a, b]
        # -----------------------------------------------------------------

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
        btn_name = os.path.basename(filedir)
        self.ui.btn_crss_vs_vds.setText(btn_name)
        [a1, b1, c1, a2, b2, c2] = fCRSS_fit(list2float(crss_data[0]), list2float(crss_data[1]))
        self.crss_params = [a1, b1, c1, a2, b2, c2]
        # ---------------------------------------------------------------

    def change_page(self):
        # Depends on device choices, the page will change accordingly to ask user for correct input data
        self.list_model = QStandardItemModel(self.ui.lst_device)
        choice = self.ui.cmb_device_choice.currentText()
        if choice == 'Transistor':
            self.ui.stackedWidget.setCurrentIndex(1)
        elif choice == 'Diode':
            self.ui.stackedWidget.setCurrentIndex(0)
        for f in os.listdir(self.dev_dir):
            filename = os.path.join(self.dev_dir, f)
            if os.path.isfile(filename):
                self.current_device = load_file(filename)
                if self.current_device.device_type == 1 and choice == 'Transistor':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_model.appendRow(item)
                elif self.current_device.device_type == 2 and choice == 'Diode':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_model.appendRow(item)
        self.ui.lst_device.setModel(self.list_model)
        # ------------------------------------------------------------------------------------------------


'''----------------------------------------End of GenericDeviceDialog ------------------------------------------'''


class DevicePropertiesDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, None)
        self.ui = Ui_device_propeties()
        self.ui.setupUi(self)
        self.parent = parent
        self.device_path = os.path.join(parent.project.tech_lib_dir, 'Layout_Selection', 'Device')
        self.device_att_path = os.path.join(parent.project.tech_lib_dir, "Die_Attaches")
        # Connect method -- Read through to understand this is important to skim through each functions
        self.ui.cmb_device_type.currentIndexChanged.connect(self.change_display)
        # self.ui.btn_add.pressed.connect(self.add_to_device_table())
        self.list_dv_model = QStandardItemModel(self.ui.lst_devices)
        self.list_dv_att_model = QStandardItemModel(self.ui.lst_devices_att)
        self.dev_choice = self.ui.cmb_device_type.currentText()
        self.load_init_page()

    def load_init_page(self):
        model_choice = self.parent.ui.cmb_thermal.currentIndex()
        if model_choice == 0 or model_choice == 1:
            self.ui.stackedWidget.setCurrentIndex(0)
            self.load_device_physics()
            self.load_device_att()
        elif model_choice == 2:
            self.ui.stackedWidget.setCurrentIndex(2)

    def load_device_physics(self):
        for f in os.listdir(self.device_path):
            filename = os.path.join(self.device_path, f)
            if os.path.isfile(filename):
                self.current_device = load_file(filename)
                if self.current_device.device_type == 1 and self.dev_choice == 'Transistor':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_dv_model.appendRow(item)
                elif self.current_device.device_type == 2 and self.dev_choice == 'Diode':
                    item = QStandardItem(f)
                    item.setEditable(False)
                    self.list_dv_model.appendRow(item)
        self.ui.lst_devices.setModel(self.list_dv_model)

    def load_device_model(self):
        print 1

    def load_device_att(self):
        for f in os.listdir(self.device_att_path):
            filename = os.path.join(self.device_att_path, f)
            if os.path.isfile(filename):
                item = QStandardItem(f)
                item.setEditable(False)
                self.list_dv_att_model.appendRow(item)
        self.ui.lst_devices_att.setModel(self.list_dv_att_model)

    def change_display(self):
        # Depends on device choices, the page will change accordingly to ask user for correct input data
        model_choice = self.parent.ui.cmb_thermal.currentIndex()
        if self.dev_choice == 'Transistor' and (model_choice == 0 or model_choice == 1):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif self.dev_choice == 'Transistor' and model_choice == 2:
            self.ui.stackedWidget.setCurrentIndex(2)
        elif self.dev_choice == 'Diode' and (model_choice == 0 or model_choice == 1):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif self.dev_choice == 'Diode' and model_choice == 2:
            self.ui.stackedWidget.setCurrentIndex(1)

        # self.ui.lst_devices_att.setRootIndex(self.attach_list_model.setRootPath(die_attach_path))


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

        # self.ui.txt_positive_source.textChanged.connect(self.check)
        # self.ui.txt_negative_source.textChanged.connect(self.check)
        # self.ui.txt_output.textChanged.connect(self.check)
        # self.ui.dropdown_filetype.currentIndexChanged.connect(self.check)

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
        self.filetype = 'script'
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
        if netlist == None:
            Notifier(msg='You did not import a netlist, you will need to assign netname in the UI !',
                     msg_name='Reminder')
        proj_dir = os.path.join(self.ui.txt_dir.text(), self.ui.txt_name.text())
        return Project(self.ui.txt_name.text(), proj_dir, DEFAULT_TECH_LIB_DIR, netlist, symb_layout)


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

    def open_dir(
            self):  # responds to button click by opening a file browser where the project directory can be selected
        prev_folder = 'C://'
        if not os.path.exists(prev_folder):  # check if the last entry file store a correct path
            prev_folder = 'C://'
        self.project_file = QFileDialog.getOpenFileName(self, "Select Project File", prev_folder, "Project Files (*.p)")
        self.ui.txt_projectLocation.setText(self.project_file[0])
        self.parent.layout_script_dir = os.path.dirname(self.project_file[0])

    def load_project(self):  # loads the project selected into the main view
        try:
            self.parent.project = load_file(self.project_file[0])

            # Add constraints field to any objects which lack it
            self.parent.project.symb_layout.add_constraints()

            # Check if project object contains tech_lib_dir field (if not add it)
            if not hasattr(self.parent.project, 'tech_lib_dir'):
                self.parent.project.tech_lib_dir = DEFAULT_TECH_LIB_DIR

        except:
            QtGui.QMessageBox.about(self, "Project Load Error", "Error loading project -- Contact developer.")
            self.reject()
            print traceback.format_exc()


class SolidworkVersionCheckDialog(QtGui.QDialog):

    def __init__(self, parent):
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

        '''Edit the Tech lib path should reload the combo boxes on the moudle stacks'''  # Quang

        self.parent.fill_material_cmbBoxes()  # Quang
        self.parent.load_moduleStack()  # Quang


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
        self.parent.layout_script = self.ui.text_layout_script.toPlainText()
        path = os.path.join(self.parent.layout_script_dir, 'layout.psc')
        f = open(path, 'wb')
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
        # self.ui.cmb_DOE.setEnabled(False)
        self.ui.cmb_sims.setEnabled(False)

        # 4 connecting signals
        self.ui.btn_add_layer_stack.pressed.connect(self.importlayerstack)
        self.ui.btn_build.pressed.connect(self.build)
        self.ui.list_mdl_lib.clicked.connect(self.show_mdl_info)
        # self.ui.cmb_DOE.currentIndexChanged.connect(self.set_up_DOE)

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
        checknum = maxL.isdigit() or maxW.isdigit() or fmin.isdigit() or fmax.isdigit()
        self.DOE = 'mesh'
        self.sims = str(self.ui.cmb_sims.currentText())
        options = [self.sims, self.DOE, False]
        if not (checknum):
            InputError(msg="not all inputs for width length and frequency are numeric, double check please")
            return
        else:

            all_num = [minL, maxL, minW, maxW]
            minL, maxL, minW, maxW = [float(x) for x in all_num]
            fmin, fmax = [int(x) for x in [fmin, fmax]]
            w_range = [minW, maxW]
            l_range = [minL, maxL]

            if self.ui.cmb_sims.currentText() == "Q3D":
                fstep = 10
                f_range = [fmin, fmax, fstep]

                env_dir = os.path.join(ANSYS_IPY64, 'ipy164.exe')
                if os.path.isfile(env_dir):
                    form_trace_model_optimetric(layer_stack=self.layer_stack_import, Width=w_range, Length=l_range,
                                                freq=f_range, wdir=self.wp_dir, savedir=self.model_dir,
                                                mdl_name=mdl_name
                                                , env=env_dir, options=options)
                else:
                    env_dir = QFileDialog.getOpenFileName(caption=r"Find ANSYS Q3D IPY dir", filter="(*.exe)")
                    print env_dir[0]
                    env_dir = os.path.abspath(env_dir[0])
                    version = psidialogs.ask_string("what is the ANSYS version (folder name ANSYSEM...)")
                    print version
                    form_trace_model_optimetric(layer_stack=self.layer_stack_import, Width=w_range, Length=l_range,
                                                freq=f_range, wdir=self.wp_dir, savedir=self.model_dir,
                                                mdl_name=mdl_name
                                                , env=env_dir, options=options, version=version)
            elif self.ui.cmb_sims.currentText() == "FastHenry":
                fstep = 100
                f_range = [fmin, fmax, fstep]
                exe = ['fasthenry.exe', 'ReadOutput.exe']
                env_dir = [os.path.join(FASTHENRY_FOLDER, x) for x in exe]
                form_fasthenry_trace_response_surface(layer_stack=self.layer_stack_import, Width=w_range,
                                                      Length=l_range,
                                                      freq=f_range, wdir=self.wp_dir, savedir=self.model_dir,
                                                      mdl_name=mdl_name,
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
    def __init__(self, parent, techlib_dir=DEFAULT_TECH_LIB_DIR, mode=1):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ModelSelection()
        self.ui.setupUi(self)
        self.parent = parent
        # populate model files
        self.model_dir = os.path.join(techlib_dir, 'Model', 'Trace')
        self.rs_model = QtGui.QFileSystemModel()
        self.rs_model.setRootPath(self.model_dir)
        self.rs_model.setFilter(QtCore.QDir.Files)
        self.ui.list_mdl_choices.setModel(self.rs_model)
        self.ui.list_mdl_choices.setRootIndex(self.rs_model.setRootPath(self.model_dir))
        self.ui.buttonBox.accepted.connect(self.select_mdl)
        self.mode = mode

    def show_mdl_info(self):
        selected = str(self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex()))
        mdl = load_file(os.path.join(self.model_dir, selected))
        text = mdl['info']
        self.ui.textEdit.setText(text)
        self.ui.list_mdl_choices.currentIndex()

    def select_mdl(self):
        try:
            self.model = load_file(
                os.path.join(self.model_dir, self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex())))
            if self.mode == 1:
                self.parent.project.symb_layout.set_RS_model(self.model)
            elif self.mode == 2:
                self.parent.parent.engine.sym_layout.set_RS_model(self.model)

            Notifier(msg="model is set to: " + str(self.rs_model.fileName(self.ui.list_mdl_choices.currentIndex())),
                     msg_name="model selected")
        except:
            InputError(msg="Unexpected error:" + str(sys.exc_info()[0]))


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
            data = f.readlines()
            self.ui.txt_dir.setText(data[self.ui.cmb_env.currentIndex()])

    def open_dir(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select BIN folder", "C://"))
        if os.path.isdir(folder):
            self.ui.txt_dir.setText(folder)

    def update(self):
        with open(SETTINGS_TXT, 'r') as f:
            data = f.readlines()
            data[self.ui.cmb_env.currentIndex()] = self.ui.txt_dir.text()
        f.close()

        with open(SETTINGS_TXT, 'w') as f:
            for i in range(len(data)):
                data[i] = data[i].strip('\n')
                f.write(data[i] + '\n')
        Notifier(msg="Update Binary complete", msg_name="Complete!")


class SetupDeviceDialogs(QtGui.QDialog):
    def __init__(self, parent, mode=1):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_setup_device()
        self.ui.setupUi(self)
        self.ui.lst_devices_att.setEnabled(True)
        self.parent = parent
        self.device = None
        # SETUP DIE ATTACH
        self.mode = mode
        self.attach_path = os.path.join(self.parent.project.tech_lib_dir, "Device_Selection", "Die_Attaches")
        self.attach_list_model = QtGui.QFileSystemModel()
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
        error1 = self._check_field(self.ui.txt_devAttchThickness, float, "Component",
                                   "Must enter a numeric value for Attach Thickness")
        error2 = self._check_field(self.ui.txt_device_heat_flow, float, "Component",
                                   "Must enter a numeric value for Device Heat Flow")
        return error1 or error2

    def check_device_error(self):
        error = False
        if self.ui.lst_devices_att.selectionModel().selectedIndexes() == []:
            error = True
            QtGui.QMessageBox.warning(self, "Add Component", "No Attach Material selected for device")
        if self._check_device_fields():
            error = True
        return error

    def return_device_setup(self, mode="ADD"):
        if not (self.check_device_error()):
            if self.mode == 1:
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
                self.parent.ui.tbl_projDevices.item(row_count, 0).setBackground(
                    QtGui.QBrush(self.parent.color_wheel[self.parent.cw1 - 1]))
                self.parent.ui.tbl_projDevices.setItem(row_count, 1, QtGui.QTableWidgetItem())
                self.parent.ui.tbl_projDevices.item(row_count, 1).setText('  ' + item.model().data(item))
                self.parent.ui.tbl_projDevices.item(row_count, 1).tech = DeviceInstance(attch_thick, heat_flow,
                                                                                        tech_obj, attch_tech_obj)
                self.close()
            elif self.mode == 2:
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

        # SAVE PARENT SYMB CANVAS
        parent_canvas = self.parent.symb_canvas[0]
        parent_axis = self.parent.symb_axis[0]
        parent_fig = self.parent.symb_fig[0]
        self.parent_data = [parent_canvas, parent_axis, parent_fig]
        # BUTTON EVENTs
        self.ui.btn_add.pressed.connect(self.add_item)
        self.ui.btn_remove.pressed.connect(self.remove_item)

        self.parent.symb_canvas[0].mpl_disconnect(self.parent.select_comp)
        self.select = self.parent.symb_canvas[0].mpl_connect('pick_event', self.device_pick)
        self.load_table()
        self.bond_conn = []
        self.event_list = []

    def load_table(self):
        table_df = self.parent.project.tbl_bondwire_connect
        if isinstance(table_df, types.NoneType) == False:
            total_rows = len(table_df.axes[0])
            for r in range(total_rows):
                self.ui.tbl_bw_connection.insertRow(r)
                self.ui.tbl_bw_connection.setItem(r, 0, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 1, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 2, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.setItem(r, 3, QtGui.QTableWidgetItem())
                self.ui.tbl_bw_connection.item(r, 0).setText(table_df.loc[r, 0])
                self.ui.tbl_bw_connection.item(r, 1).setText(str(table_df.loc[r, 1]))
                self.ui.tbl_bw_connection.item(r, 2).setText(str(table_df.loc[r, 2]))
                self.ui.tbl_bw_connection.item(r, 3).setText(table_df.loc[r, 3])
                self.ui.tbl_bw_connection.item(r, 3).tech = table_df.loc[r, 4]

    def device_pick(self, event):
        layout_obj = self.parent.patch_dict.get_layout_obj(event.artist)
        if event.artist.get_hatch() == '///':
            event.artist.set_hatch('')
            self.bond_conn.remove(layout_obj)
            self.event_list.remove(event.artist)
        elif len(self.bond_conn) <= 1:
            event.artist.set_hatch('///')
            self.event_list.append(event.artist)
            self.bond_conn.append(layout_obj)
        self.parent.symb_canvas[0].draw()
        if len(self.bond_conn) == 2:
            self.ui.btn_add.setEnabled(True)
        else:
            self.ui.btn_add.setEnabled(False)

    def closeEvent(self, event):
        self.parent.symb_canvas[0].mpl_disconnect(self.select)
        self.parent.select_comp = self.parent.symb_canvas[0].mpl_connect('pick_event', self.parent.device_pick)
        table_df = pd.DataFrame(columns=['bw_type', 'start', 'stop', 'obj'])
        for row in range(self.ui.tbl_bw_connection.rowCount()):
            for col in range(self.ui.tbl_bw_connection.columnCount()):
                table_df.loc[row, col] = self.ui.tbl_bw_connection.item(row, col).text()
            table_df.loc[row, 4] = self.ui.tbl_bw_connection.item(row, 3).tech  # Fir
        self.parent.project.tbl_bondwire_connect = table_df
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
        if tech_obj.wire_type == 1:
            type = 'POWER'
        elif tech_obj.wire_type == 2:
            type = 'SIGNAL'

        self.ui.tbl_bw_connection.item(row_count, 0).setText(type)
        self.ui.tbl_bw_connection.item(row_count, 1).setText(str(self.bond_conn[0].name))
        self.ui.tbl_bw_connection.item(row_count, 2).setText(str(self.bond_conn[1].name))
        self.ui.tbl_bw_connection.item(row_count, 3).setText(' ' + item.model().data(item))
        self.ui.tbl_bw_connection.item(row_count, 3).tech = tech_obj
        for patch in self.event_list:
            patch.set_hatch('')
        self.ui.btn_add.setEnabled(False)
        self.event_list = []
        self.bond_conn = []
        self.parent.symb_canvas[0].draw()

    def remove_item(self):
        print "ITEM REMOVED"
        selected_row = self.ui.tbl_bw_connection.currentRow()
        self.ui.tbl_bw_connection.selectionModel().selectedIndexes()[0].row()
        self.ui.tbl_bw_connection.removeRow(selected_row)


class Device_states_dialog(QtGui.QDialog):
    def __init__(self, parent, per_ui=None, mode=1):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_dev_state_dialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.per_ui = per_ui
        self.ui.btn_ok.pressed.connect(self.Ok)
        self.dv_df = pd.DataFrame()
        self.group = QtGui.QButtonGroup()
        self.mode = mode
        self.load_table()

    def closeEvent(self, event):
        self.Ok()

    def load_table(self):
        if self.mode == 1:
            all_sym = self.parent.project.symb_layout.all_sym  # Called from old PS
        elif self.mode == 2:
            all_sym = self.parent.parent.engine.sym_layout.all_sym  # Called from new engine

        for dv in all_sym:
            if isinstance(dv, SymPoint):
                if dv.tech == None:
                    Notifier("Not all devices have technology file, please go to the previous page to select", "Error")
                    return
                elif isinstance(dv.tech, DeviceInstance):
                    row_count = self.ui.tbl_states.rowCount()
                    self.ui.tbl_states.insertRow(row_count)
                    self.ui.tbl_states.setItem(row_count, 0, QtGui.QTableWidgetItem())
                    if dv.name != None:
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
                        self.ui.tbl_states.setCellWidget(row_count, 1, btn_state)  # Drain to source
                        self.group.addButton(btn_state)

        self.group.setExclusive(False)

    def Ok(self):
        for row in range(self.ui.tbl_states.rowCount()):
            for col in range(self.ui.tbl_states.columnCount()):
                if col == 0:
                    self.dv_df.loc[row, col] = self.ui.tbl_states.item(row, col).text()
                else:
                    if self.ui.tbl_states.cellWidget(row, col) != None:
                        self.dv_df.loc[row, col] = int(self.ui.tbl_states.cellWidget(row, col).isChecked() * 1)
        # print self.dv_df
        if self.mode == 1:
            self.per_ui.device_states_df = self.dv_df
        if self.mode == 2:
            self.parent.dev_df = self.dv_df
        self.close()


class ConsDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Constraint_setup()
        self.ui.setupUi(self)
        self.parent = parent
        self.cons_df = pd.DataFrame()
        self.cons_dims = pd.DataFrame()
        self.cons_sp = pd.DataFrame()
        self.cons_encl = pd.DataFrame()
        self.num_types = 0  # number of tile's types
        self.ui.btn_load.pressed.connect(self.load_table)
        self.ui.btn_apply.pressed.connect(self.apply_changes)
        self.ui.btn_save.pressed.connect(self.save_cons)
        self.load_table(mode=0)

    def load_table(self, mode=1):
        if mode == 1:  # from csv
            cons_file = QFileDialog.getOpenFileName(self, "Select Constraint File", 'C://', "Constraints Files (*.csv)")
            self.cons_df = pd.read_csv(cons_file[0])
        elif mode == 0:

            cons_file = 'out.csv'
            if cons_file is not None:
                self.cons_df = pd.read_csv(cons_file)
                # self.cons_df = self.parent.cons_df
            # else:
            # return
        # print"con", self.cons_df
        table_df = self.cons_df
        # print table_df
        total_cols = len(table_df.axes[1])
        r_sp = 4  # row of min spacing
        r_encl = r_sp + total_cols  # row of min encl
        self.ui.tbl_cons_dims.setRowCount(4)
        self.ui.tbl_cons_dims.setColumnCount(total_cols)
        self.ui.tbl_cons_gaps.setRowCount(total_cols)
        self.ui.tbl_cons_gaps.setColumnCount(total_cols)
        self.ui.tbl_cons_encl.setRowCount(total_cols)
        self.ui.tbl_cons_encl.setColumnCount(total_cols)
        # First table for dimensions
        cols_name = list(table_df.columns.values)
        self.cons_dims = pd.DataFrame(columns=cols_name)
        self.cons_sp = pd.DataFrame(columns=["Min Spacing"] + cols_name[1:-1])
        self.cons_encl = pd.DataFrame(columns=["Min Enclosure"] + cols_name[1:-1])
        for c in range(total_cols):
            self.ui.tbl_cons_dims.setItem(0, c, QtGui.QTableWidgetItem())
            self.ui.tbl_cons_dims.item(0, c).setText(cols_name[c])
            if c == 0:
                self.ui.tbl_cons_encl.setItem(0, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_encl.item(0, c).setText("Min Enclosure")
                self.ui.tbl_cons_gaps.setItem(0, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_gaps.item(0, c).setText("Min Spacing")
            else:
                self.ui.tbl_cons_encl.setItem(0, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_encl.item(0, c).setText(cols_name[c])
                self.ui.tbl_cons_gaps.setItem(0, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_gaps.item(0, c).setText(cols_name[c])

        for r in range(3):
            for c in range(total_cols):
                self.ui.tbl_cons_dims.setItem(r + 1, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_dims.item(r + 1, c).setText(str(table_df.iloc[r, c]))

        for r in range(total_cols - 1):
            for c in range(total_cols):
                self.ui.tbl_cons_gaps.setItem(r + 1, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_gaps.item(r + 1, c).setText(str(table_df.iloc[r + r_sp, c]))
                self.ui.tbl_cons_encl.setItem(r + 1, c, QtGui.QTableWidgetItem())
                self.ui.tbl_cons_encl.item(r + 1, c).setText(str(table_df.iloc[r + r_encl, c]))

    def apply_changes(self):
        loc_id = 0
        for row in range(self.ui.tbl_cons_dims.rowCount() - 1):

            for col in range(len(self.cons_dims.columns)):
                colid = self.cons_dims.columns[col]
                self.cons_dims.loc[row, colid] = self.ui.tbl_cons_dims.item(row + 1, col).text()
                self.cons_df.loc[loc_id, colid] = self.ui.tbl_cons_dims.item(row + 1, col).text()

            loc_id += 1
        for row in range(self.ui.tbl_cons_gaps.rowCount()):
            for col in range(len(self.cons_sp.columns)):
                colid = self.cons_sp.columns[col]
                colid1 = self.cons_dims.columns[col]
                if row != 0:
                    self.cons_sp.loc[row, colid] = self.ui.tbl_cons_gaps.item(row, col).text()
                    self.cons_df.loc[loc_id, colid1] = self.ui.tbl_cons_gaps.item(row, col).text()
                else:
                    self.cons_df.loc[loc_id, colid1] = colid

            loc_id += 1
        for row in range(self.ui.tbl_cons_encl.rowCount()):
            for col in range(len(self.cons_encl.columns)):
                colid = self.cons_encl.columns[col]
                colid1 = self.cons_dims.columns[col]
                if row != 0:
                    self.cons_encl.loc[row, colid] = self.ui.tbl_cons_encl.item(row, col).text()
                    self.cons_df.loc[loc_id, colid1] = self.ui.tbl_cons_encl.item(row, col).text()
                else:
                    self.cons_df.loc[loc_id, colid1] = colid
            loc_id += 1

        self.parent.cons_df = self.cons_df
        # print "DFs",self.parent.cons_df
        self.close()

    def save_cons(self):
        self.apply_changes()
        save_path = QtGui.QFileDialog.getSaveFileName(self, "Save constraint file", 'C://',
                                                      "Constraints Files (*.csv)")
        self.cons_df.to_csv(save_path[0], index_label=False)


class Fixed_locations_Dialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Fixed_location_Dialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.node_dict = None
        self.Nodes = []
        self.current_node = None
        self.X = None
        self.Y = None
        self.x_space = None  # horizontal room
        self.y_space = None  # vertical room
        self.init_table()
        self.new_node_dict = {}

        self.Min_X, self.Min_Y = self.parent.engine.mode_zero()
        self.initial_range_x = {}  # finding each node's initial range of x  coordinate {Node ID:(xmin,xmax)}
        self.initial_range_y = {}  # finding each node's initial range of y  coordinate {Node ID:(ymin,ymax)}
        self.dynamic_range_x = {}  # finding each node's dynamic range of x  coordinate {Node ID:(xmin,xmax)}
        self.dynamic_range_y = {}  # finding each node's dynamic range of y  coordinate {Node ID:(ymin,ymax)}
        self.x_init_range = {}  # initial x range mapped to each x coordinate{x_coord:(x_min,x_max)}
        self.y_init_range = {}  # initial y range mapped to each y coordinate{y_coord:(y_min,y_max)}
        self.x_dynamic_range = {}  # dynamic x range mapped to each x coordinate{x_coord:(x_min,x_max)}
        self.y_dynamic_range = {}  # dynamic y range mapped to each y coordinate{y_coord:(y_min,y_max)}
        # print self.Min_X,self.Min_Y
        self.current_range = {}  # to check if the input coordinate is within the valid range

        # print "L", len(self.parent.input_node_info.keys())
        if len(self.parent.input_node_info.keys()) == 0:
            self.setup_initial_range()
            self.inserted_order = []

        else:
            self.new_node_dict = dict(self.parent.input_node_info)
            self.inserted_order = [i for i in self.parent.inserted_order]
            self.setup_initial_range()
            self.x_dynamic_range = dict(self.parent.x_dynamic_range)
            self.y_dynamic_range = dict(self.parent.y_dynamic_range)
            self.dynamic_range_x = dict(self.parent.dynamic_range_x)
            self.dynamic_range_y = dict(self.parent.dynamic_range_y)

        self.ui.cmb_nodes.currentIndexChanged.connect(self.node_handler)
        self.ui.txt_inputx.setEnabled(False)
        self.ui.txt_inputy.setEnabled(False)

        self.ui.btn_addnode.pressed.connect(self.add_row)
        self.ui.btn_rmvnode.pressed.connect(self.remove_row)
        self.ui.btn_save.pressed.connect(self.finished)

    # def show_nodeID(self,Nodelist):
    def setup_initial_range(self):
        x_values = self.Min_X[1].values()
        x_values.sort()
        max_x = x_values[-1]
        if self.parent.mode3_width != None and self.parent.mode3_width >= max_x:
            self.x_space = self.parent.mode3_width - max_x
        else:
            print "Please enter floorplan width greater or equal to minimum width ", float(max_x) / 1000
        y_values = self.Min_Y[1].values()
        y_values.sort()
        max_y = y_values[-1]
        if self.parent.mode3_height != None and self.parent.mode3_height >= max_y:
            self.y_space = self.parent.mode3_height - max_y
        else:
            print "Please enter floorplan height greater or equal to minimum height ", float(max_y) / 1000
        # print x_values, max_x, self.parent.fp_width, self.parent.fp_length
        for k, v in self.parent.graph[1].items():
            for k1, v1 in self.Min_X.items():
                for k2, v2 in v1.items():
                    if k2 == v[0]:
                        x_min = v2

                        if self.x_space != None:
                            x_max = v2 + self.x_space
                        else:
                            print "No horizontal space is allocated"
                        self.initial_range_x[k] = (x_min, x_max)
                        self.x_init_range[k2] = (x_min, x_max)
                        self.dynamic_range_x[k] = (x_min, x_max)
                        self.x_dynamic_range[k2] = (x_min, x_max)
                for k1, v1 in self.Min_Y.items():
                    for k2, v2 in v1.items():
                        if k2 == v[1]:
                            y_min = v2
                            if self.y_space != None:
                                y_max = v2 + self.y_space
                            else:
                                print "No vertical space is allocated"
                            self.initial_range_y[k] = (y_min, y_max)
                            self.y_init_range[k2] = (y_min, y_max)
                            self.dynamic_range_y[k] = (y_min, y_max)
                            self.y_dynamic_range[k2] = (y_min, y_max)

        '''
        #print self.Min_X
        #print self.Min_Y
        #print self.parent.graph[1]
        print "init"
        print self.initial_range_x
        print self.initial_range_y
        print "init_x",self.x_init_range
        print "init_y",self.y_init_range
        '''

    def dynamic_update(self):

        x_fixed = []
        y_fixed = []
        if len(self.new_node_dict.keys()) > 0:
            for k, v in self.new_node_dict.items():
                if v[0] != None:
                    for k1, v1 in self.node_dict.items():
                        if k1 == k:
                            x_fixed.append(v1[0])

                if v[1] != None:
                    for k1, v1 in self.node_dict.items():
                        if k1 == k:
                            y_fixed.append(v1[1])

        x_fixed.sort()
        y_fixed.sort()
        # print "init",x_fixed,y_fixed
        if len(x_fixed) > 0:
            for k, v in self.node_dict.items():
                if k == self.current_node:
                    x_fixed.append(v[0])
                    current_x = v[0]
                else:
                    continue
                    # y_fixed.append(v[1])
            x_fixed.sort()
            # print "app_cur", x_fixed,current_x
            if x_fixed.index(current_x) == 0:
                start = x_fixed[1]
                for k1, v1 in self.node_dict.items():
                    if v1[0] > start:
                        x_fixed.append(v1[0])
            elif x_fixed.index(current_x) == len(x_fixed) - 1:
                start = x_fixed[-2]
                for k1, v1 in self.node_dict.items():
                    if v1[0] < start:
                        x_fixed.append(v1[0])

                    else:
                        continue
            else:
                start = x_fixed.index(current_x) - 1
                end = x_fixed.index(current_x) + 1
                for k1, v1 in self.node_dict.items():
                    if v1[0] < x_fixed[start] or v1[0] > x_fixed[end]:
                        x_fixed.append(v1[0])
                    else:
                        continue
        if len(y_fixed) > 0:
            for k, v in self.node_dict.items():
                if k == self.current_node:
                    y_fixed.append(v[1])
                    current_y = v[1]
                else:
                    continue
                    # y_fixed.append(v[1])
            y_fixed.sort()
            # print"Y", y_fixed
            if y_fixed.index(current_y) == 0:
                for k1, v1 in self.node_dict.items():
                    if v1[1] > y_fixed[1]:
                        y_fixed.append(v1[1])
                    else:
                        continue
            elif y_fixed.index(current_y) == len(y_fixed) - 1:
                for k1, v1 in self.node_dict.items():
                    if v1[1] < y_fixed[-2]:
                        y_fixed.append(v1[1])
                    else:
                        continue
            else:
                start = y_fixed.index(current_y) - 1
                end = y_fixed.index(current_y) + 1
                for k1, v1 in self.node_dict.items():
                    if v1[1] < y_fixed[start] or v1[1] > y_fixed[end]:
                        y_fixed.append(v1[1])
                    else:
                        continue

        x_fixed = list(set(x_fixed))
        y_fixed = list(set(y_fixed))

        # print "Fixed", x_fixed
        # print y_fixed
        x0 = self.X
        y0 = self.Y
        # y0=self.new_node_dict[self.current_node][1]
        min_x_change = []
        max_x_change = []
        x_unchange = []
        min_y_change = []
        max_y_change = []
        y_unchange = []
        for k, v in self.node_dict.items():
            if x0 != None:
                if v[0] > self.node_dict[self.current_node][0] and v[0] not in x_fixed:
                    min_x_change.append(v[0])
                elif v[0] < self.node_dict[self.current_node][0] and v[0] not in x_fixed:
                    max_x_change.append(v[0])
                elif v[0] == self.node_dict[self.current_node][0]:
                    x_unchange.append(v[0])
            if y0 != None:
                if v[1] > self.node_dict[self.current_node][1] and v[1] not in y_fixed:
                    min_y_change.append(v[1])
                elif v[1] < self.node_dict[self.current_node][1] and v[1] not in y_fixed:
                    max_y_change.append(v[1])
                elif v[1] == self.node_dict[self.current_node][1]:
                    y_unchange.append(v[1])

        # print self.current_node
        min_x_change = list(set(min_x_change))
        max_x_change = list(set(max_x_change))
        x_unchange = list(set(x_unchange))
        min_y_change = list(set(min_y_change))
        max_y_change = list(set(max_y_change))
        y_unchange = list(set(y_unchange))
        # print min_x_change,max_x_change,x_unchange
        # print min_y_change,max_y_change,y_unchange
        if x0 != None:
            if len(min_x_change) > 0:
                for x in min_x_change:

                    x_min = self.x_dynamic_range[x][0] + (
                            x0 - self.x_dynamic_range[self.node_dict[self.current_node][0]][0])
                    x_max = self.x_dynamic_range[x][1]
                    for k, v in self.node_dict.items():
                        if v[0] == x:
                            self.dynamic_range_x[k] = (x_min, x_max)
                            self.x_dynamic_range[x] = (x_min, x_max)
                        else:
                            continue
            if len(max_x_change) > 0:
                for x in max_x_change:
                    x_min = self.x_dynamic_range[x][0]
                    x_max = (x0 - (self.x_dynamic_range[self.node_dict[self.current_node][0]][0] - x_min))
                    for k, v in self.node_dict.items():
                        if v[0] == x:
                            self.dynamic_range_x[k] = (x_min, x_max)
                            self.x_dynamic_range[x] = (x_min, x_max)
                        else:
                            continue
            if len(x_unchange) > 0:
                for x in x_unchange:
                    x_min = x_max = x0
                    for k, v in self.node_dict.items():
                        if v[0] == x:
                            self.dynamic_range_x[k] = (x_min, x_max)
                            self.x_dynamic_range[x] = (x_min, x_max)
                        else:
                            continue
        # print self.dynamic_range_x
        # print"x_dynamic" ,self.x_dynamic_range
        if y0 != None:
            if len(min_y_change) > 0:
                for y in min_y_change:
                    y_min = self.y_dynamic_range[y][0] + (
                            y0 - self.y_dynamic_range[self.node_dict[self.current_node][1]][0])
                    y_max = self.y_dynamic_range[y][1]
                    for k, v in self.node_dict.items():
                        if v[1] == y:
                            self.dynamic_range_y[k] = (y_min, y_max)
                            self.y_dynamic_range[y] = (y_min, y_max)
                        else:
                            continue
            if len(max_y_change) > 0:
                for y in max_y_change:
                    y_min = self.y_dynamic_range[y][0]
                    y_max = (y0 - abs(self.y_dynamic_range[self.node_dict[self.current_node][1]][0] - y_min))
                    for k, v in self.node_dict.items():
                        if v[1] == y:
                            self.dynamic_range_y[k] = (y_min, y_max)
                            self.y_dynamic_range[y] = (y_min, y_max)
                        else:
                            continue
            if len(y_unchange) > 0:
                for y in y_unchange:
                    y_min = y_max = y0
                    for k, v in self.node_dict.items():
                        if v[1] == y:
                            self.dynamic_range_y[k] = (y_min, y_max)
                            self.y_dynamic_range[y] = (y_min, y_max)
                        else:
                            continue
        # print self.y_dynamic_range

    def dynamic_remove(self):
        # print len(self.new_node_dict.keys()),self.new_node_dict.keys()
        if len(self.new_node_dict.keys()) == 0:
            for k, v in self.x_init_range.items():
                self.x_dynamic_range[k] = v
            for k, v in self.y_init_range.items():
                self.y_dynamic_range[k] = v
            for k, v in self.initial_range_x.items():
                self.dynamic_range_x[k] = v
            for k, v in self.initial_range_y.items():
                self.dynamic_range_y[k] = v
            # print"IN Remove x_dynamic", self.x_dynamic_range
            # print "IN Remove", self.y_dynamic_range
        else:

            for k, v in self.x_init_range.items():
                self.x_dynamic_range[k] = v
            for k, v in self.y_init_range.items():
                self.y_dynamic_range[k] = v
            for k, v in self.initial_range_x.items():
                self.dynamic_range_x[k] = v
            for k, v in self.initial_range_y.items():
                self.dynamic_range_y[k] = v

            Keys = [i for i in self.inserted_order]

            x_fixed = []
            y_fixed = []

            for i in range(len(Keys)):
                x0 = self.new_node_dict[Keys[i]][0]
                y0 = self.new_node_dict[Keys[i]][1]

                # print "Removed_node", Keys[i],x_fixed,y_fixed
                # if len(x_fixed) > 0:

                for k, v in self.node_dict.items():
                    if k == Keys[i]:
                        x_fixed.append(v[0])
                        current_x = v[0]
                    else:
                        continue
                x_fixed.sort()

                # print "IN Remove app_cur", x_fixed, current_x
                if len(x_fixed) > 1:
                    if x_fixed.index(current_x) == 0:
                        start = x_fixed[1]
                        for k1, v1 in self.node_dict.items():
                            if v1[0] > start:
                                x_fixed.append(v1[0])
                    elif x_fixed.index(current_x) == len(x_fixed) - 1:
                        start = x_fixed[-2]
                        for k1, v1 in self.node_dict.items():
                            if v1[0] < start:
                                x_fixed.append(v1[0])

                            else:
                                continue
                    else:

                        start = x_fixed.index(current_x) - 1
                        end = x_fixed.index(current_x) + 1
                        for k1, v1 in self.node_dict.items():
                            if v1[0] < x_fixed[start] or v1[0] > x_fixed[end]:
                                x_fixed.append(v1[0])
                            else:
                                continue
                # if len(y_fixed) > 0:
                for k, v in self.node_dict.items():
                    if k == Keys[i]:
                        y_fixed.append(v[1])
                        current_y = v[1]
                    else:
                        continue
                        # y_fixed.append(v[1])
                y_fixed.sort()
                if len(y_fixed) > 1:
                    if y_fixed.index(current_y) == 0:
                        for k1, v1 in self.node_dict.items():
                            if v1[1] > y_fixed[1]:
                                y_fixed.append(v1[1])
                            else:
                                continue
                    elif y_fixed.index(current_y) == len(y_fixed) - 1:
                        for k1, v1 in self.node_dict.items():
                            if v1[1] < y_fixed[-2]:
                                y_fixed.append(v1[1])
                            else:
                                continue
                    else:
                        start = y_fixed.index(current_y) - 1
                        end = y_fixed.index(current_y) + 1
                        for k1, v1 in self.node_dict.items():
                            if v1[1] < y_fixed[start] or v1[1] > y_fixed[end]:
                                y_fixed.append(v1[1])
                            else:
                                continue

                '''
                if len(x_fixed) > 0:

                    #for i in range(len(x_fixed)-1):
                    for k1, v1 in self.node_dict.items():
                        if v1[0]<x_fixed[0]:
                            x_fixed.append(v1[0])

                if len(y_fixed) > 0:
                    #for i in y_fixed:
                    for k1, v1 in self.node_dict.items():
                        if v1[1] < y_fixed[0]:
                            y_fixed.append(v1[0])
                '''
                x_fixed = list(set(x_fixed))
                y_fixed = list(set(y_fixed))

                # print "IN Remove Fixed", x_fixed
                # print y_fixed
                # y0=self.new_node_dict[self.current_node][1]
                min_x_change = []
                max_x_change = []
                x_unchange = []
                min_y_change = []
                max_y_change = []
                y_unchange = []
                for k, v in self.node_dict.items():
                    if x0 != None:
                        if v[0] > self.node_dict[Keys[i]][0] and v[0] not in x_fixed:
                            min_x_change.append(v[0])
                        elif v[0] < self.node_dict[Keys[i]][0] and v[0] not in x_fixed:
                            max_x_change.append(v[0])
                        elif v[0] == self.node_dict[Keys[i]][0]:
                            x_unchange.append(v[0])
                    if y0 != None:
                        if v[1] > self.node_dict[Keys[i]][1] and v[1] not in y_fixed:
                            min_y_change.append(v[1])
                        elif v[1] < self.node_dict[Keys[i]][1] and v[1] not in y_fixed:
                            max_y_change.append(v[1])
                        elif v[1] == self.node_dict[Keys[i]][1]:
                            y_unchange.append(v[1])

                # print self.current_node
                min_x_change = list(set(min_x_change))
                max_x_change = list(set(max_x_change))
                x_unchange = list(set(x_unchange))
                min_y_change = list(set(min_y_change))
                max_y_change = list(set(max_y_change))
                y_unchange = list(set(y_unchange))
                # print "IN Remove",min_x_change, max_x_change, x_unchange
                # print "IN Remove",min_y_change, max_y_change, y_unchange
                if x0 != None:
                    if len(min_x_change) > 0:
                        for x in min_x_change:

                            x_min = self.x_dynamic_range[x][0] + (
                                    x0 - self.x_dynamic_range[self.node_dict[Keys[i]][0]][0])
                            x_max = self.x_dynamic_range[x][1]
                            for k, v in self.node_dict.items():
                                if v[0] == x:
                                    self.dynamic_range_x[k] = (x_min, x_max)
                                    self.x_dynamic_range[x] = (x_min, x_max)
                                else:
                                    continue
                    if len(max_x_change) > 0:
                        for x in max_x_change:
                            x_min = self.x_dynamic_range[x][0]
                            x_max = (x0 - (self.x_dynamic_range[self.node_dict[Keys[i]][0]][0] - x_min))
                            for k, v in self.node_dict.items():
                                if v[0] == x:
                                    self.dynamic_range_x[k] = (x_min, x_max)
                                    self.x_dynamic_range[x] = (x_min, x_max)
                                else:
                                    continue
                    if len(x_unchange) > 0:
                        for x in x_unchange:
                            x_min = x_max = x0
                            for k, v in self.node_dict.items():
                                if v[0] == x:
                                    self.dynamic_range_x[k] = (x_min, x_max)
                                    self.x_dynamic_range[x] = (x_min, x_max)
                                else:
                                    continue
                # print self.dynamic_range_x

                if y0 != None:
                    if len(min_y_change) > 0:
                        for y in min_y_change:
                            y_min = self.y_dynamic_range[y][0] + (
                                    y0 - self.y_dynamic_range[self.node_dict[Keys[i]][1]][0])
                            y_max = self.y_dynamic_range[y][1]
                            for k, v in self.node_dict.items():
                                if v[1] == y:
                                    self.dynamic_range_y[k] = (y_min, y_max)
                                    self.y_dynamic_range[y] = (y_min, y_max)
                                else:
                                    continue
                    if len(max_y_change) > 0:
                        for y in max_y_change:
                            y_min = self.y_dynamic_range[y][0]
                            y_max = (y0 - abs(self.y_dynamic_range[self.node_dict[Keys[i]][1]][0] - y_min))
                            for k, v in self.node_dict.items():
                                if v[1] == y:
                                    self.dynamic_range_y[k] = (y_min, y_max)
                                    self.y_dynamic_range[y] = (y_min, y_max)
                                else:
                                    continue
                    if len(y_unchange) > 0:
                        for y in y_unchange:
                            y_min = y_max = y0
                            for k, v in self.node_dict.items():
                                if v[1] == y:
                                    self.dynamic_range_y[k] = (y_min, y_max)
                                    self.y_dynamic_range[y] = (y_min, y_max)
                                else:
                                    continue
                # print"IN Remove x_dynamic", self.x_dynamic_range
                # print "IN Remove", self.y_dynamic_range
            # print"IN Remove_end x_dynamic", self.x_dynamic_range
            # print "IN Remove", self.y_dynamic_range

    def init_table(self):

        if self.parent.input_node_info != None:
            self.new_node_dict = self.parent.input_node_info
        # print"P", self.parent.input_node_info
        row_id = self.ui.table_Fixedloc.rowCount()

        # print"R", row_id
        if len(self.parent.input_node_info.keys()) > 0:
            for k, v in self.parent.input_node_info.items():

                self.ui.table_Fixedloc.insertRow(row_id)
                self.ui.table_Fixedloc.setItem(row_id, 0, QtGui.QTableWidgetItem())
                self.ui.table_Fixedloc.setItem(row_id, 1, QtGui.QTableWidgetItem())
                self.ui.table_Fixedloc.setItem(row_id, 2, QtGui.QTableWidgetItem())
                if k != None:
                    self.ui.table_Fixedloc.item(row_id, 0).setText(str(k))
                if v[0] != None:
                    self.ui.table_Fixedloc.item(row_id, 1).setText(str(float(v[0]) / 1000))
                else:
                    self.ui.table_Fixedloc.item(row_id, 1).setText("None")
                if v[1] != None:
                    self.ui.table_Fixedloc.item(row_id, 2).setText(str(float(v[1]) / 1000))
                else:
                    self.ui.table_Fixedloc.item(row_id, 2).setText("None")
                row_id += 1

    def set_node_id(self, node_dict):
        self.node_dict = node_dict

        self.ui.cmb_nodes.clear()
        for i in node_dict.keys():
            item = 'Node ' + str(i)
            self.ui.cmb_nodes.addItem(item)
            self.Nodes.append(item)

    def set_label(self, x, y, div=1000):
        # updated version (showing dynamic range)
        label = "Node location range  X:" + "(" + str((float(x[0]) / div)) + "," + str(
            float(x[1]) / div) + ")  " + "Y:(" + str((float(y[0]) / div)) + "," + str(float(y[1]) / div) + ")"
        self.ui.lbl_minxy.setText(label)
        self.ui.txt_inputx.setEnabled(True)
        self.ui.txt_inputy.setEnabled(True)

        # old version
        '''
        label="Node min location X:"+str(float(x)/div)+"   "+"Y:"+str(float(y)/div)
        self.ui.lbl_minxy.setText(label)
        self.ui.txt_inputx.setEnabled(True)
        self.ui.txt_inputy.setEnabled(True)
        '''

    def node_handler(self):
        # self.ui.txt_inputx.clear()
        # self.ui.txt_inputy.clear()

        choice = self.ui.cmb_nodes.currentText()

        for i in self.Nodes:
            if choice == i:

                self.X = None
                self.Y = None
                node_id = int(i.split()[1])
                self.current_node = node_id
                # print self.current_node

                # updated version (showing dynamic range)
                # print self.new_node_dict

                if len(self.new_node_dict.keys()) == 0:
                    xrange = self.initial_range_x[self.current_node]
                    yrange = self.initial_range_y[self.current_node]
                else:
                    xrange = self.dynamic_range_x[self.current_node]
                    yrange = self.dynamic_range_y[self.current_node]

                self.set_label(xrange, yrange)
                self.current_range[self.current_node] = (xrange, yrange)
                # old version
                '''
                for k,v in self.node_dict.items():
                    #print "node_dict",k,v[0],v[1]
                    if k==node_id:
                        x=v[0]
                        y=v[1]
                    else:
                        continue


                for k,v in self.Min_X.items():

                    for k1,v1 in v.items():
                        if k1==x:
                            x_min=v1
                            #self.ui.lbl_minxy.setText(str(v1))

                        else:
                            continue
                for k,v in self.Min_Y.items():
                    for k1,v1 in v.items():
                        if k1==y:
                            y_min=v1
                            #self.ui.lbl_minxy.setText(str(v1))

                        else:
                            continue
                self.set_label(x_min,y_min)
                '''

    def valid_check(self):
        invalid_x = 0
        invalid_y = 0
        for k, v in self.current_range.items():
            if k == self.current_node:
                if self.X != None:
                    if self.X < v[0][0] or self.X > v[0][1]:

                        invalid_x = 1
                    else:
                        invalid_x = 0
                if self.Y != None:
                    if self.Y < v[1][0] or self.Y > v[1][1]:

                        invalid_y = 1
                    else:
                        invalid_y = 0
        return invalid_x, invalid_y

    def add_row(self):

        row_id = self.ui.table_Fixedloc.rowCount()
        # self.ui.table_Fixedloc.insertRow(rowPosition)
        # self.ui.table_Fixedloc.setItem(rowPosition, self.current_node, self.X, self.Y)
        self.ui.table_Fixedloc.insertRow(row_id)
        self.ui.table_Fixedloc.setItem(row_id, 0, QtGui.QTableWidgetItem())
        self.ui.table_Fixedloc.setItem(row_id, 1, QtGui.QTableWidgetItem())
        self.ui.table_Fixedloc.setItem(row_id, 2, QtGui.QTableWidgetItem())
        self.ui.table_Fixedloc.item(row_id, 0).setText(str(self.current_node))
        if str(self.ui.txt_inputx.text()) != '':
            self.X = float(self.ui.txt_inputx.text()) * 1000
            x_check, y_check = self.valid_check()
            if x_check == 0:
                self.ui.table_Fixedloc.item(row_id, 1).setText(str(float(self.X) / 1000))
            else:
                self.ui.table_Fixedloc.item(row_id, 1).setText('Invalid')
                print" X value is out of valid range"
                print "Please remove the row and try again"
        else:
            self.ui.table_Fixedloc.item(row_id, 1).setText('None')

        if str(self.ui.txt_inputy.text()) != '':
            self.Y = float(self.ui.txt_inputy.text()) * 1000
            x_check, y_check = self.valid_check()
            if y_check == 0:
                self.ui.table_Fixedloc.item(row_id, 2).setText(str(float(self.Y) / 1000))
            else:
                self.ui.table_Fixedloc.item(row_id, 2).setText('Invalid')
                print" Y value is out of valid range"
                print "Please remove the row and try again"

        else:
            self.ui.table_Fixedloc.item(row_id, 2).setText('None')

        # if x_check == 0 and y_check == 0:
        self.dynamic_update()
        self.inserted_order.append(self.current_node)
        self.new_node_dict[self.current_node] = (self.X, self.Y)

    def remove_row(self):
        selected_row = self.ui.table_Fixedloc.currentRow()
        row_id = self.ui.table_Fixedloc.selectionModel().selectedIndexes()[0].row()
        node_id = str(self.ui.table_Fixedloc.item(row_id, 0).text())
        self.ui.table_Fixedloc.removeRow(selected_row)
        for k1, v1 in self.parent.input_node_info.items():
            if k1 == int(node_id):
                del self.parent.input_node_info[k1]

        for k, v in self.new_node_dict.items():
            if k == int(node_id):
                del self.new_node_dict[k]
                self.inserted_order.remove(k)

        self.dynamic_remove()

        # print "RP", self.parent.input_node_info,self.new_node_dict,self.node_dict

    # def set_locations(self):
    def finished(self):
        # self.parent.input_node_info = self.new_node_dict
        self.parent.fixed_x_locations = {}
        self.parent.fixed_y_locations = {}
        Xloc = {}
        for k, v in self.Min_X.items():
            Xloc = v.keys()
        Yloc = {}
        for k, v in self.Min_Y.items():
            Yloc = v.keys()

        for k1, v1 in self.new_node_dict.items():
            self.parent.input_node_info[k1] = v1
        for k1, v1 in self.parent.input_node_info.items():
            # self.parent.input_node_info[k1] = v1
            for k, v in self.node_dict.items():
                if k1 == k:

                    if v1[0] != None and v1[1] != None:
                        ind = Xloc.index(v[0])

                        self.parent.fixed_x_locations[ind] = v1[0]
                        ind2 = Yloc.index(v[1])

                        self.parent.fixed_y_locations[ind2] = v1[1]
                    elif v1[0] == None and v1[1] != None:
                        ind2 = Yloc.index(v[1])

                        self.parent.fixed_y_locations[ind2] = v1[1]
                    elif v1[0] != None and v1[1] == None:
                        ind = Xloc.index(v[0])

                        self.parent.fixed_x_locations[ind] = v1[0]
                    else:
                        continue
                else:
                    continue
        self.parent.x_dynamic_range = dict(self.x_dynamic_range)
        self.parent.y_dynamic_range = dict(self.y_dynamic_range)
        self.parent.dynamic_range_x = dict(self.dynamic_range_x)
        self.parent.dynamic_range_y = dict(self.dynamic_range_y)
        self.parent.inserted_order = [i for i in self.inserted_order]

        # self.parent.input_node_info=self.new_node_dict
        # print"XY", self.parent.fixed_x_locations,self.parent.fixed_y_locations

        self.close()


class New_layout_engine_dialog(QtGui.QDialog):
    # Test New LAyout Engine
    def __init__(self, parent, fig, W, H, engine=None, graph=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_CornerStitch_Dialog()
        self.ui.setupUi(self)
        self.engine = engine
        self.parent = parent
        self.cornerstitch = None
        self.constraint = False
        self.num_layouts = 0
        self.mainwindow_fig = fig  ##Temporary addition
        self.graph = graph
        self.fp_width = W
        self.fp_length = H
        self.cons_df = None
        self.current_mode = 0
        self.generated_layouts = {}
        self.layout_data = {}
        self.perf_dict = {}
        self.Patches = None
        self.input_node_info = {}
        self.selected_ind = None
        self.fixed_x_locations = {}
        self.fixed_y_locations = {}
        self.opt_algo = None  # optimization algorithm
        self.individual = None  # for NSGAII
        self.W = None  # for NSGAII cost_func
        self.H = None  # for NSGAII cost_func
        self.solutions = []  # for NSGAII cost_func
        self.seed = None
        self.default_save_dir = "C:\\"
        # add buttons
        self.ui.cmb_modes.setEnabled(False)
        self.ui.btn_fixed_locs.setEnabled(False)
        self.ui.btn_fixed_locs.pressed.connect(self.assign_fixed_locations)
        self.ui.btn_constraints.pressed.connect(self.add_constraints)
        self.ui.cmb_modes.currentIndexChanged.connect(self.mode_handler)
        self.initialize_layout(self.mainwindow_fig, self.graph)
        self.ui.btn_eval_setup.pressed.connect(self.eval_setup)
        self.ui.btn_gen_layouts.pressed.connect(self.gen_layouts)
        self.ui.btn_export.pressed.connect(self.export_layout)
        self.ui.btn_sel_sol.pressed.connect(self.save_solution)
        self.ui.btn_save_all.pressed.connect(self.save_solution_set)

        # initialize for mode 0
        self.ui.txt_num_layouts.setEnabled(False)
        self.ui.txt_width.setEnabled(False)
        self.ui.txt_height.setEnabled(False)
        self.ui.btn_fixed_locs.setEnabled(False)
        self.ui.btn_gen_layouts.setEnabled(False)
        self.ui.btn_eval_setup.setEnabled(False)
        self.ui.txt_seed.setEnabled(False)

        self.mode3_width = None  # To update mode3 floorplan size
        self.mode3_height = None  # To update mode3 floorplan size
        self.x_dynamic_range = None  # To store saved information from the fixed location table
        self.y_dynamic_range = None  # To store saved information from the fixed location table
        self.dynamic_range_x = None  # To store saved information from the fixed location table
        self.dynamic_range_y = None  # To store saved information from the fixed location table
        self.inserted_order = None
        self.sol_count = 0
        self.sol_params = None

    def save_solution(self):
        if self.parent is not None:
            self.sol_count += 1
            sol_name = QtGui.QInputDialog.getText(self, "Solution Name", "Enter a name for this solution:",
                                                  QtGui.QLineEdit.Normal, "Solution " + str(self.sol_count))
            solution = Solution()
            if sol_name[1]:
                if sol_name[0] == "":
                    solution.name = "Solution " + str(self.sol_count)
                else:
                    solution.name = sol_name[0]
                # ----> what if the name already exists?
                sym_layout = copy.deepcopy(self.engine.sym_layout)
                sym_layout.layout_ready =True
                solution.index = self.selected_ind
                solution.params = self.sol_params
                self.parent.add_solution(solution=solution, flag=1, sym_layout=sym_layout)
            else:
                self.sol_count -= 1

    def save_solution_set(self):
        print "implement later"

    def export_layout(self):
        if self.current_mode != 0:
            choice = 'Layout ' + str(self.selected_ind)
        selected = str(self.ui.cmbox_export_option.currentText())
        # select and convert layout
        sym_info = self.form_sym_obj_rect_dict()
        self.sym_layout = self.engine.sym_layout
        symb_rect_dict = sym_info[choice]['sym_info']
        dims = sym_info[choice]['Dims']
        # print dims,symb_rect_dict
        bp_dims = [dims[0] + 4, dims[1] + 4]
        self._sym_update_layout(sym_info=symb_rect_dict)
        update_sym_baseplate_dims(sym_layout=self.sym_layout, dims=bp_dims)
        update_substrate_dims(sym_layout=self.sym_layout, dims=dims)
        self.sym_layout.layout_ready = True

        self.canvas_sols.draw()
        if selected == 'Q3D':
            self.export_q3d()
        elif selected == 'Solidworks':
            self.export_solidworks()
        elif selected == 'Electrical netlist ':
            print "add later"
        elif selected == 'Thermal netlist':
            print "add later"
        elif selected == 'FastHenry':
            self.export_FH()
        elif selected == 'EMPro':
            self.export_empro()

    def export_FH(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        if len(outname) > 0:
            try:
                md = ModuleDesign(self.sym_layout)
                # output_fh_script_mesh(md,outname)
                output_fh_script(self.sym_layout, outname)
                QtGui.QMessageBox.about(None, "FH Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "FH Script", "Failed to export FH script! Check log/console.")
                print traceback.format_exc()

    def export_empro(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        print fn
        outname = fn[0]

        if len(outname) > 0:
            try:
                md = ModuleDesign(self.sym_layout)
                empro_script = EMProScript(md, outname + ".py")
                empro_script.generate()
                QtGui.QMessageBox.about(None, "EMPro Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "EMPro Script", "Failed to export script! Check log/console.")
                print traceback.format_exc()

    def export_q3d(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        print fn
        outname = fn[0]

        if len(outname) > 0:
            try:
                md = ModuleDesign(self.sym_layout)
                output_q3d_vbscript(md, outname)
                QtGui.QMessageBox.about(None, "Q3D VB Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "Q3D VB Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()

    def export_solidworks(self):
        version = SolidworkVersionCheckDialog(self)
        if version.exec_():
            version = version.version_output()
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]

        if len(outname) > 0:
            print 'exporting solidworks file'
            try:
                md = ModuleDesign(self.sym_layout)

                data_dir = 'C:/ProgramData/SolidWorks/SolidWorks ' + version
                output_solidworks_vbscript(md, os.path.basename(outname), data_dir, os.path.dirname(outname))
                QtGui.QMessageBox.about(None, "SolidWorks Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SolidWorks Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()

    def getPatches(self, Patches):
        if self.Patches == None:
            self.Patches = Patches
            print "self.Patches"
        return

    def setPatches(self):
        return self.Patches

        self.ui.btn_gen_layouts.pressed.connect(self.gen_layouts)
        self.ui.cmb_sols.currentIndexChanged.connect(self.layout_plot)

    def width_edit_text_changed(self):
        try:
            W = float(self.ui.txt_width.text()) * 1000
        except ValueError:
            W = None
        if W != None:
            self.mode3_width = W

    def height_edit_text_changed(self):
        try:
            H = float(self.ui.txt_height.text()) * 1000
        except ValueError:
            H = None
        if H != None:
            self.mode3_height = H

    def mode_handler(self):  # Modes combobox
        choice = str(self.ui.cmb_modes.currentText())

        if choice == 'Minimum Size Layout':
            self.current_mode = 0
            self.ui.txt_num_layouts.setEnabled(False)
            self.ui.txt_width.setEnabled(False)
            self.ui.txt_height.setEnabled(False)
            self.ui.btn_fixed_locs.setEnabled(False)
            self.ui.txt_seed.setEnabled(False)
            self.refresh_layout()

        elif choice == 'Variable Size Layout':
            QtGui.QMessageBox.warning(self, "Varied Baseplate Size",
                                      "Thermal model is set to analytical for fast evaluation")

            self.current_mode = 1
            self.ui.txt_num_layouts.setEnabled(True)
            self.ui.txt_seed.setEnabled(True)
            self.ui.txt_width.setEnabled(False)
            self.ui.txt_height.setEnabled(False)
            self.ui.btn_fixed_locs.setEnabled(False)
            self.refresh_layout()

        elif choice == 'Fixed Size Layout':
            self.current_mode = 2
            self.ui.txt_num_layouts.setEnabled(True)
            self.ui.txt_seed.setEnabled(True)
            self.ui.txt_width.setEnabled(True)
            self.ui.txt_height.setEnabled(True)
            self.ui.btn_fixed_locs.setEnabled(False)
            self.refresh_layout()

        elif choice == 'Fixed Size with Fixed Loactions':
            self.current_mode = 3
            self.ui.txt_num_layouts.setEnabled(True)
            self.ui.txt_seed.setEnabled(True)
            self.ui.txt_width.setEnabled(True)
            self.ui.txt_height.setEnabled(True)
            self.ui.btn_fixed_locs.setEnabled(True)
            self.refresh_layout_mode3()
            # print self.fp_width
            self.mode3_width = float(self.ui.txt_width.text()) * 1000
            self.mode3_height = float(self.ui.txt_height.text()) * 1000
            self.ui.txt_width.textChanged.connect(self.width_edit_text_changed)
            self.ui.txt_height.textChanged.connect(self.height_edit_text_changed)

        return

    def assign_fixed_locations(self):  # Fixed Locations (for mode-3)

        fixed_locations = Fixed_locations_Dialog(self)
        fixed_locations.set_node_id(self.graph[1])
        fixed_locations.show()
        fixed_locations.exec_()

    def add_constraints(self):

        constraints = ConsDialog(self)
        self.constraint = True

        self.cons_df = self.engine.cons_df

        constraints.exec_()

        self.constraint = True

        self.engine.cons_df = self.cons_df

        self.ui.btn_eval_setup.setEnabled(True)
        self.ui.btn_gen_layouts.setEnabled(True)
        self.ui.cmb_modes.setEnabled(True)

    def update_sol_browser(self):
        self.ax3.clear()
        print "plot sol browser"
        if self.perf_dict == {}:
            self.perf1 = {"label": 'layout index', 'data': []}
            self.perf2 = {"label": 'layout index', 'data': []}

            for layout in self.generated_layouts.keys():
                id = self.generated_layouts.keys().index(layout)
                self.perf1['data'].append(id)
                self.perf2['data'].append(id)

        self.ax3.plot(self.perf1['data'], self.perf2['data'], 'o', picker=5)
        self.ax3.set_xlabel(self.perf1['label'])
        self.ax3.set_ylabel(self.perf2['label'])
        self.canvas_sol_browser.draw()
        self.canvas_sol_browser.callbacks.connect('pick_event', self.on_pick)

    def on_pick(self, event):
        self.update_sol_browser()
        self.selected_ind = event.ind[0]
        self.ax3.plot(self.perf1['data'][self.selected_ind], self.perf2['data'][self.selected_ind], 'o', c='red')
        self.layout_plot(layout_ind=self.selected_ind)
        self.canvas_sols.draw()
        self.canvas_sol_browser.draw()
        self.sol_params = [[self.perf1['type'], self.perf1['data'][self.selected_ind], self.perf1['unit']],
                           [self.perf2['type'], self.perf2['data'][self.selected_ind], self.perf2['unit']]]

    def cost_func_NSGAII(self, individual):
        self.count += 1
        if not (isinstance(individual, list)):
            individual = np.asarray(individual).tolist()
        # print"inside cost",individual
        Patches, cs_sym_data = self.engine.generate_solutions(self.current_mode, num_layouts=1, W=self.W, H=self.H,
                                                              fixed_x_location=self.fixed_x_locations,
                                                              fixed_y_location=self.fixed_y_locations, seed=self.seed,
                                                              individual=individual)
        # print "P",Patches
        # print cs_sym_data
        if self.engine.sym_layout != None:
            layout_data = self.form_sym_obj_rect_dict_opt(layout_data=cs_sym_data)
            for k, v in layout_data.items():
                sym_info = v
            self._sym_update_layout(sym_info=sym_info)
            dims = layout_data.keys()[0]
            bp_dims = [dims[0] + 4, dims[1] + 4]
            self._sym_update_layout(sym_info=sym_info)
            update_sym_baseplate_dims(sym_layout=self.engine.sym_layout, dims=bp_dims)
            update_substrate_dims(sym_layout=self.engine.sym_layout, dims=dims)
            plot = False  # Change this flag
            if plot == True and self.count > 100:
                fig, ax = plt.subplots()
                plot_layout(sym_layout=self.engine.sym_layout, ax=ax)
                plt.show

            '''
            # Evaluate performace for all all layouts
            for p in self.perf_dict.keys():
                perf = self.perf_dict[p]
                measure = perf['measure']
                if perf['type'] == 'Thermal' and measure.mdl == 1 and self.current_mode != 1:
                    self.engine.sym_layout.thermal_characterize()
            '''
            ret = self.one_measure(sym_info=sym_info)
            print ret, Patches
            solution = [ret, Patches, cs_sym_data]
            self.solutions.append(solution)
            return ret

    def gen_layouts(self):
        self.parent.project.layout_engine = "CS"
        if not (self.constraint):
            print "cant generate layouts"
            return
        else:
            print "generate layout"

            if self.current_mode != 0:
                # if self.opt_algo=="NG-RANDOM":
                try:
                    N = int(self.ui.txt_num_layouts.text())
                    self.seed = int(self.ui.txt_seed.text())
                except:
                    print "Please enter Num of Layouts greater than 0"
                    print "ERROR: Invalid Information"
                    return

                W = float(self.ui.txt_width.text()) * 1000
                H = float(self.ui.txt_height.text()) * 1000
                if self.opt_algo == "NSGAII" and self.current_mode == 2:
                    X, Y = self.engine.mode_zero()
                    x_nodes = [i for i in range(len(X[1]))]
                    y_nodes = [i for i in range(len(Y[1]))]
                    Random = []
                    for i in range((len(x_nodes) + len(y_nodes)) - 1):
                        r = random.uniform(0, 1)
                        Random.append(r)
                    Design_Vars = []
                    for i in range(len(Random)):
                        prange = [0, 1]
                        Design_Vars.append(DesignVar((prange[0], prange[1]), (prange[0], prange[1])))
                    self.W = W
                    self.H = H
                    self.count = 0
                    opt = NSGAII_Optimizer(design_vars=Design_Vars, eval_fn=self.cost_func_NSGAII, num_measures=2,
                                           seed=self.seed, num_gen=N)
                    opt.run()
                    Num_sols = len(self.solutions)
                    Patches = []
                    cs_sym_data = []
                    Meausrements = []
                    for i in range(Num_sols):
                        Patch = self.solutions[i][1]
                        Patches.append(Patch[0])
                        cs_sym = self.solutions[i][2]
                        cs_sym_data.append(cs_sym[0])
                        Meausrements.append(self.solutions[i][0])
                    Layouts = []
                    for i in range(int(Num_sols)):
                        item = 'Layout ' + str(i)
                        Layouts.append(item)

                    if Patches != None:

                        # UPDATE layout sols for plotting
                        for i in range(int(Num_sols)):

                            '''
                            Plot real Layout here
                            '''

                            if self.engine.sym_layout != None:
                                self.layout_data[Layouts[i]] = {'Rects': cs_sym_data[i]}

                                self.generated_layouts[Layouts[i]] = {'Patches': Patches[i]}
                    else:
                        print"Patches not found"
                    self.perf1 = {"label": None, 'data': [], 'unit': '', 'type': ''}
                    self.perf2 = {"label": None, 'data': [], 'unit': '', 'type': ''}
                    perf_plot = [self.perf1, self.perf2]
                    for p, pdraw in zip(self.perf_dict.keys(), perf_plot):
                        perf = self.perf_dict[p]
                        measure = perf['measure']
                        for i in range(Num_sols):
                            ax = plt.subplot('111', adjustable='box', aspect=1.0)

                            if perf['type'] == 'Thermal':
                                lbl = measure.name + '(K)'
                                pdraw["label"] = (lbl)
                                pdraw['data'].append(Meausrements[i][0])
                                pdraw['unit'] = 'K'
                                pdraw['type'] = 'Temperature'
                            elif perf['type'] == 'Electrical':
                                type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                                             ElectricalMeasure.MEASURE_IND: 'ind',
                                             ElectricalMeasure.MEASURE_CAP: 'cap'}
                                measure_type = type_dict[measure.measure]

                                if measure_type == 'res':
                                    lbl = measure.name + ' (mOhm)'
                                    pdraw['unit'] = '(mOhm)'
                                    pdraw['type'] = 'R'
                                if measure_type == 'ind':
                                    lbl = measure.name + ' (nH)'
                                    pdraw['unit'] = '(nH)'
                                    pdraw['type'] = 'L'

                                if measure_type == 'cap':
                                    lbl = measure.name + ' (pF)'
                                    pdraw['unit'] = '(pF)'
                                    pdraw['type'] = 'C'

                                pdraw["label"] = (lbl)
                                pdraw['data'].append(Meausrements[i][1])

                    self.update_sol_browser()






                else:

                    Patches, cs_sym_data = self.engine.generate_solutions(self.current_mode, num_layouts=N, W=W, H=H,
                                                                          fixed_x_location=self.fixed_x_locations,
                                                                          fixed_y_location=self.fixed_y_locations,
                                                                          seed=self.seed)

                if Patches == None or cs_sym_data == None:
                    print "ERROR: Invalid Information"
                    return
            else:
                N = 1
                Patches, cs_sym_data = self.engine.generate_solutions(self.current_mode, num_layouts=N)

            Layouts = []
            for i in range(int(N)):
                item = 'Layout ' + str(i)
                Layouts.append(item)

            if Patches != None:

                # UPDATE layout sols for plotting
                for i in range(int(N)):

                    '''
                    Plot real Layout here
                    '''

                    if self.engine.sym_layout != None:
                        self.layout_data[Layouts[i]] = {'Rects': cs_sym_data[i]}

                        self.generated_layouts[Layouts[i]] = {'Patches': Patches[i]}
            else:
                print"Patches not found"

        # Convert Data info to Symb object for evaluation
        if self.opt_algo == "NG-RANDOM":
            if self.engine.sym_layout != None:
                sym_info = self.form_sym_obj_rect_dict()

                # Evaluate performace for all all layouts
                for p in self.perf_dict.keys():
                    perf = self.perf_dict[p]
                    measure = perf['measure']
                    if perf['type'] == 'Thermal' and measure.mdl == 1 and self.current_mode != 1:
                        self.engine.sym_layout.thermal_characterize()
                self._sym_eval_perf(sym_info=sym_info)

            # Update the solution browser
            self.update_sol_browser()

            if self.current_mode == 0:
                self.layout_plot()
        return

    def eval_setup(self):
        eval = ET_standalone_Dialog(self)
        eval.exec_()

    def layout_plot(self, layout_ind=0, mode='cs'):
        self.ax1.clear()
        if self.current_mode != 0:
            choice = 'Layout ' + str(layout_ind)
        else:

            choice = 'Layout 0'
            for k, v in self.generated_layouts.items():
                if choice == k:
                    for k1, v1 in v['Patches'].items():
                        W = (float(k1[0]) / 1000)
                        H = (float(k1[1]) / 1000)

                        self.ui.txt_width.setText(str(W))
                        self.ui.txt_height.setText(str(H))

        if mode == 'cs':  # corner stitch plotting engine (has some issues)
            '''
            if self.current_mode==2:
                for k,v in self.generated_layouts.items():
                    if choice==k:
                        for k1,v1 in v['Patches'].items():
                            for p in v1:

                                self.ax1.add_patch(p)
                            self.ax1.set_xlim(-2, k1[0])
                            self.ax1.set_ylim(-2, k1[1])
                            self.ui.txt_width.setText(str(k1[0]-2))
                            self.ui.txt_height.setText(str(k1[1]-2))
                        self.canvas_sols.draw()
            #else:
            '''
            for k, v in self.generated_layouts.items():
                if choice == k:
                    for k1, v1 in v['Patches'].items():
                        for p in v1:
                            self.ax1.add_patch(p)
                        self.ax1.set_xlim(0, k1[0])
                        self.ax1.set_ylim(0, k1[1])
                        self.ui.txt_width.setText(str(k1[0]))
                        self.ui.txt_height.setText(str(k1[1]))
                    self.canvas_sols.draw()
        elif mode == 'ps':
            sym_info = self.form_sym_obj_rect_dict()
            sym_layout = self.engine.sym_layout
            symb_rect_dict = sym_info[choice]['sym_info']
            dims = sym_info[choice]['Dims']
            # print dims,symb_rect_dict
            bp_dims = [dims[0] + 4, dims[1] + 4]
            self._sym_update_layout(sym_info=symb_rect_dict)
            update_sym_baseplate_dims(sym_layout=sym_layout, dims=bp_dims)
            update_substrate_dims(sym_layout=sym_layout, dims=dims)
            plot_layout(sym_layout, ax=self.ax1, new_window=False)
            self.canvas_sols.draw()

    def refresh_layout(self):
        self.ax2.clear()
        self.ax2.set_position([0.07, 0.07, 0.9, 0.9])

        Names = self.init_fig.keys()
        Names.sort()
        for k, p in self.init_fig.items():

            if k[0] == 'T':
                x = p.get_x()
                y = p.get_y()
                self.ax2.text(x + 1, y + 1, k)
                self.ax2.add_patch(p)
        for k, p in self.init_fig.items():

            if k[0] != 'T':
                x = p.get_x()
                y = p.get_y()
                self.ax2.text(x + 1, y + 1, k, weight='bold')
                self.ax2.add_patch(p)
        if self.init_graph != None and self.current_mode == 3:
            G = self.init_graph[0]
            pos = self.init_graph[1]
            lbls = self.init_graph[2]
            nx.draw_networkx_nodes(G, pos, node_size=80, label=True, ax=self.ax2, zorder=6)

            nx.draw_networkx_labels(G, pos, lbls, font_size=6, ax=self.ax2)

        self.ax2.set_xlim(0, self.fp_width)
        self.ax2.set_ylim(0, self.fp_length)
        self.canvas_init.draw()

    def refresh_layout_mode3(self):
        self.ax2.clear()
        Names = self.init_fig.keys()
        Names.sort()
        for k, p in self.init_fig.items():

            if k[0] == 'T':
                x = p.get_x()
                y = p.get_y()
                self.ax2.text(x + 1, y + 1, k)
                self.ax2.add_patch(p)
        for k, p in self.init_fig.items():

            if k[0] != 'T':
                x = p.get_x()
                y = p.get_y()
                self.ax2.text(x + 1, y + 1, k, weight='bold')
                self.ax2.add_patch(p)

        data = {"x": [], "y": [], "label": []}
        for label, coord in self.init_graph[1].items():
            data["x"].append(coord[0])
            data["y"].append(coord[1])
            data["label"].append(label)

        self.ax2.plot(data['x'], data['y'], 'o', picker=5)
        self.ax2.set_xlim(0, self.fp_width)
        self.ax2.set_ylim(0, self.fp_length)
        self.canvas_init.draw()
        self.canvas_init.callbacks.connect('pick_event', self.on_click)

    def on_click(self, event):
        # self.ax3.plot(self.perf1['data'][self.selected_ind], self.perf2['data'][self.selected_ind], 'o', c='red')

        x = round(event.mouseevent.xdata, 2)
        y = round(event.mouseevent.ydata, 2)
        self.ax2.plot(x, y, 'o', c='red')
        for k, v in self.init_graph[1].items():
            if ((abs(x - v[0]) <= 0.99 and abs(y - v[1]) <= 0.99)):
                self.show_node_id(k)

    def show_node_id(self, id):
        label = "Node ID: " + str(id)
        self.ui.Node_ID.setText(label)

    def initialize_layout(self, fig, graph=None):
        '''
        plot main window figure
        Returns:

        '''
        self.init_fig = fig
        self.init_graph = graph
        self.ui.txt_width.setText(str(self.fp_width))
        self.ui.txt_height.setText(str(self.fp_length))
        fig2 = Figure()
        fig1 = Figure()
        fig3 = Figure()
        self.ax1 = fig1.add_subplot(111)  # Generated Layout
        self.ax2 = fig2.add_subplot(111)  # Initial Layout
        self.ax3 = fig3.add_subplot(111)  # Initial Layout

        self.canvas_init = FigureCanvas(fig2)
        self.canvas_sols = FigureCanvas(fig1)
        self.canvas_sol_browser = FigureCanvas(fig3)
        grid_layout = QtGui.QGridLayout(self.ui.grview_init_layout)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.canvas_init, 0, 0, 1, 1)

        grid_layout = QtGui.QGridLayout(self.ui.grview_layout_sols)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.canvas_sols, 0, 0, 1, 1)

        grid_layout = QtGui.QGridLayout(self.ui.grview_sols_browser)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.canvas_sol_browser, 0, 0, 1, 1)

        self.ax1.set_position([0.07, 0.07, 0.9, 0.9])
        self.ax2.set_position([0.07, 0.07, 0.9, 0.9])
        self.ax3.set_position([0.2, 0.2, 0.7, 0.7])

        if fig == None:
            self.ax2 = fig2.add_subplot(111, aspect=1.0)
            self.ax2.plot([0, 1, 2], [1, 2, 3])
        else:
            Names = fig.keys()
            Names.sort()
            for k, p in fig.items():

                if k[0] == 'T':
                    x = p.get_x()
                    y = p.get_y()
                    self.ax2.text(x + 1, y + 1, k)
                    self.ax2.add_patch(p)
            for k, p in fig.items():

                if k[0] != 'T':
                    x = p.get_x()
                    y = p.get_y()
                    self.ax2.text(x + 1, y + 1, k, weight='bold')
                    self.ax2.add_patch(p)
            self.ax2.set_xlim(0, self.fp_width)
            self.ax2.set_ylim(0, self.fp_length)
            if self.init_graph != None and self.current_mode == 3:
                G = graph[0]
                pos = graph[1]
                lbls = graph[2]
                nx.draw_networkx_nodes(G, pos, node_size=100, label=True, ax=self.ax2, zorder=6)
                nx.draw_networkx_labels(G, pos, lbls, font_size=8, ax=self.ax2)
        self.ax3.ticklabel_format(axis='both', style='sci')
        self.canvas_init.draw()
        return

    def run_mode(self):
        return self.current_mode

    def form_sym_obj_rect_dict_opt(self, layout_data, div=1000):
        layout_info = {}
        symb_rect_dict = {}
        p_data = layout_data[0]
        # print "p_data",p_data
        W, H = p_data.keys()[0]
        W = float(W) / div
        H = float(H) / div
        rect_dict = p_data.values()[0]
        for r_id in rect_dict.keys():
            left = 1e32
            bottom = 1e32
            right = 0
            top = 0
            for rect in rect_dict[r_id]:
                type = rect.type
                min_x = float(rect.left) / div
                max_x = float(rect.right) / div
                min_y = float(rect.bottom) / div
                max_y = float(rect.top) / div
                if min_x <= left:
                    left = float(min_x)
                if min_y <= bottom:
                    bottom = float(min_y)
                if max_x >= right:
                    right = float(max_x)
                if max_y >= top:
                    top = float(max_y)
            symb_rect_dict[r_id] = Rectangle(x=left, y=bottom, width=right - left, height=top - bottom, type=type)
        layout_info[(W, H)] = symb_rect_dict
        # return symb_rect_dict
        return layout_info

    def form_sym_obj_rect_dict(self, div=1000):
        '''
        From group of CornerStitch Rectangles, form a single rectangle for each trace
        Output type : {"Layout id": {'Sym_info': symb_rect_dict,'Dims': [W,H]} --- Dims is the dimension of the baseplate
        where symb_rect_dict= {'Symbolic ID': [R1,R2 ... Ri]} where Ri is a Rectangle object
        '''
        layout_symb_dict = {}
        for layout in self.layout_data.keys():
            symb_rect_dict = {}
            p_data = self.layout_data[layout]['Rects']
            # print "p_data",p_data
            W, H = p_data.keys()[0]
            W = float(W) / div
            H = float(H) / div
            rect_dict = p_data.values()[0]
            for r_id in rect_dict.keys():
                # print 'rect id',r_id
                left = 1e32
                bottom = 1e32
                right = 0
                top = 0
                for rect in rect_dict[r_id]:
                    type = rect.type
                    min_x = float(rect.left) / div
                    max_x = float(rect.right) / div
                    min_y = float(rect.bottom) / div
                    max_y = float(rect.top) / div
                    if min_x <= left:
                        left = float(min_x)
                    if min_y <= bottom:
                        bottom = float(min_y)
                    if max_x >= right:
                        right = float(max_x)
                    if max_y >= top:
                        top = float(max_y)
                symb_rect_dict[r_id] = Rectangle(x=left, y=bottom, width=right - left, height=top - bottom, type=type)
            layout_symb_dict[layout] = {'sym_info': symb_rect_dict, 'Dims': [W, H]}
        return layout_symb_dict

    def one_measure(self, sym_info=None):
        ret = []
        sym_layout = self.engine.sym_layout
        # print"PER", self.perf_dict
        for p in (self.perf_dict.keys()):
            perf = self.perf_dict[p]
            measure = perf['measure']

            if perf['type'] == 'Thermal':
                for layout in sym_info.keys():
                    if self.current_mode == 1:
                        mdl = 2
                    else:
                        mdl = measure.mdl
                val = sym_layout._thermal_analysis(measure, mdl)
                ret.append(val)
            elif perf['type'] == 'Electrical':

                type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                             ElectricalMeasure.MEASURE_IND: 'ind',
                             ElectricalMeasure.MEASURE_CAP: 'cap'}
                measure_type = type_dict[measure.measure]
                if measure.measure == ElectricalMeasure.MEASURE_CAP:
                    val = sym_layout._measure_capacitance(measure)
                else:

                    # load device states table
                    tbl_states = measure.dev_state
                    for row in range(len(tbl_states.axes[0])):
                        dev_name = tbl_states.loc[row, 0]
                        for dev in sym_layout.devices:
                            if (dev.name == dev_name) or dev.element.path_id == dev_name:
                                if dev.is_transistor():
                                    dev.states = [tbl_states.loc[row, 1], tbl_states.loc[row, 2],
                                                  tbl_states.loc[row, 3]]
                                if dev.is_diode():
                                    dev.states = [tbl_states.loc[row, 1]]
                    sym_layout.mdl_type['E'] = measure.mdl

                    sym_layout._build_lumped_graph()  # Rebuild the lumped graph for different device state.

                    # plot_lumped_graph(sym_layout)
                    # Measure res. or ind. from src node to sink node
                    source_terminal = measure.src_term
                    sink_terminal = measure.sink_term

                    src = measure.pt1.lumped_node
                    sink = measure.pt2.lumped_node

                    if source_terminal != None:
                        if source_terminal == 'S' or source_terminal == 'Anode':
                            src = src * 1000 + 1
                        elif source_terminal == 'G':
                            src = src * 1000 + 2

                    if sink_terminal != None:
                        if sink_terminal == 'S' or source_terminal == 'Anode':
                            sink = sink * 1000 + 1
                        elif sink_terminal == 'G':
                            sink = sink * 1000 + 2

                    node_dict = {}
                    index = 0
                    for n in sym_layout.lumped_graph.nodes():
                        node_dict[n] = index
                        index += 1

                    val = parasitic_analysis(sym_layout.lumped_graph, src, sink, measure_type, node_dict)
                    # print 'ind',val

                ret.append(val)

        return ret

    def _sym_eval_perf(self, sym_info=None):
        self.perf1 = {"label": None, 'data': [], 'unit': '', 'type': ''}
        self.perf2 = {"label": None, 'data': [], 'unit': '', 'type': ''}
        sym_layout = self.engine.sym_layout
        perf_plot = [self.perf1, self.perf2]
        for p, pdraw in zip(self.perf_dict.keys(), perf_plot):
            perf = self.perf_dict[p]
            measure = perf['measure']
            for layout in sym_info.keys():
                ax = plt.subplot('111', adjustable='box', aspect=1.0)
                symb_rect_dict = sym_info[layout]['sym_info']
                dims = sym_info[layout]['Dims']
                bp_dims = [dims[0] + 4, dims[1] + 4]
                self._sym_update_layout(sym_info=symb_rect_dict)
                update_sym_baseplate_dims(sym_layout=sym_layout, dims=bp_dims)
                update_substrate_dims(sym_layout=sym_layout, dims=dims)

                if perf['type'] == 'Thermal':
                    lbl = measure.name + '(K)'
                    pdraw["label"] = (lbl)
                    pdraw["unit"] = '(K)'
                    pdraw["type"] = 'Temperature'
                    if self.current_mode == 1:
                        mdl = 2
                    else:
                        mdl = measure.mdl

                    val = sym_layout._thermal_analysis(measure, mdl)
                    pdraw['data'].append(val)
                elif perf['type'] == 'Electrical':
                    type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                                 ElectricalMeasure.MEASURE_IND: 'ind',
                                 ElectricalMeasure.MEASURE_CAP: 'cap'}
                    measure_type = type_dict[measure.measure]

                    if measure_type == 'res':
                        lbl = measure.name + ' (mOhm)'
                        pdraw["unit"] = '(mOhm)'
                        pdraw["type"] = 'R'

                    if measure_type == 'ind':
                        lbl = measure.name + ' (nH)'
                        pdraw["unit"] = '(nH)'
                        pdraw["type"] = 'L'

                    if measure_type == 'cap':
                        lbl = measure.name + ' (pF)'
                        pdraw["unit"] = '(pF)'
                        pdraw["type"] = 'C'

                    pdraw["label"] = (lbl)
                    if measure.measure == ElectricalMeasure.MEASURE_CAP:
                        val = sym_layout._measure_capacitance(measure)
                    else:

                        # load device states table
                        tbl_states = measure.dev_state
                        for row in range(len(tbl_states.axes[0])):
                            dev_name = tbl_states.loc[row, 0]
                            for dev in sym_layout.devices:
                                if (dev.name == dev_name) or dev.element.path_id == dev_name:
                                    if dev.is_transistor():
                                        dev.states = [tbl_states.loc[row, 1], tbl_states.loc[row, 2],
                                                      tbl_states.loc[row, 3]]
                                    if dev.is_diode():
                                        dev.states = [tbl_states.loc[row, 1]]
                        sym_layout.mdl_type['E'] = measure.mdl

                        sym_layout._build_lumped_graph()  # Rebuild the lumped graph for different device state.

                        # Measure res. or ind. from src node to sink node
                        source_terminal = measure.src_term
                        sink_terminal = measure.sink_term

                        src = measure.pt1.lumped_node
                        sink = measure.pt2.lumped_node

                        if source_terminal != None:
                            if source_terminal == 'S' or source_terminal == 'Anode':
                                src = src * 1000 + 1
                            elif source_terminal == 'G':
                                src = src * 1000 + 2

                        if sink_terminal != None:
                            if sink_terminal == 'S' or source_terminal == 'Anode':
                                sink = sink * 1000 + 1
                            elif sink_terminal == 'G':
                                sink = sink * 1000 + 2

                        node_dict = {}
                        index = 0
                        for n in sym_layout.lumped_graph.nodes():
                            node_dict[n] = index
                            index += 1
                        try:
                            val = parasitic_analysis(sym_layout.lumped_graph, src, sink, measure_type, node_dict)
                        except LinAlgError:
                            val = 1e6
                    pdraw['data'].append(val)

    def _sym_update_layout(self, sym_info=None):
        # ToDo:Here we can add the automate symbolic layout - Corner Stitch interface to update thermal
        self._sym_update_trace_lines(sym_info=sym_info)
        self._sym_place_devices(sym_info=sym_info)
        self._sym_place_leads(sym_info=sym_info)
        self._sym_place_bondwires()

    def _sym_update_trace_lines(self, sym_info=None):
        '''
        *Only used when a symbolic layout is introduced
        Use the rectangles built from corner stitch to make trace rectangles in sym layout
        '''
        # Handle traces
        sym_layout = self.engine.sym_layout
        sym_layout.trace_rects = []

        for tr in self.engine.sym_layout.all_trace_lines:
            rect = sym_info[tr.element.path_id]
            sym_layout.trace_rects.append(rect)
            tr.trace_rect = rect

    def _sym_place_devices(self, sym_info=None):
        '''
        *Only used when a symbolic layout is introduced
        Use the rectangles built from corner stitch to update device locations in sym layout
        '''
        sym_layout = self.engine.sym_layout

        for dev in sym_layout.devices:

            dev_region = sym_info[dev.name]
            width, height, thickness = dev.tech.device_tech.dimensions

            line = dev.parent_line
            trace_rect = line.trace_rect
            if line.element.vertical:
                dev.orientation = 1
                dev.footprint_rect = Rect(dev_region.bottom + height, dev_region.bottom, dev_region.left,
                                          dev_region.left + width)
                xpos = trace_rect.center_x()
                ypos = dev_region.bottom + height / 2
            else:
                dev.footprint_rect = Rect(dev_region.bottom + width, dev_region.bottom, dev_region.left,
                                          dev_region.left + height)

                xpos = dev_region.left + height / 2
                ypos = trace_rect.center_y()
                dev.orientation = 3
            dev.center_position = (xpos, ypos)
            if len(dev.sym_bondwires) > 0:
                powerbond = None
                for bw in dev.sym_bondwires:
                    if bw.tech.wire_type == BondWire.POWER:
                        powerbond = bw
                        break

                if powerbond is None:
                    raise LayoutError('No connected power bondwire!')

                if dev.orientation == 1:

                    # On vertical trace
                    # orient device by power bonds
                    if powerbond.trace.trace_rect.left < trace_rect.left:
                        dev.orientation = 2  # 180 degrees from ref.
                    else:
                        dev.orientation = 1  # 0 degrees from ref.
                elif dev.orientation == 3:
                    if powerbond.trace.trace_rect.top < trace_rect.top:
                        dev.orientation = 3  # 180 degrees from ref.
                    else:
                        dev.orientation = 4  # 0 degrees from ref.

    def _sym_place_leads(self, sym_info=None):
        sym_layout = self.engine.sym_layout

        for lead in sym_layout.leads:
            if lead.tech.shape == Lead.BUSBAR:
                line = lead.parent_line
                trace_rect = line.trace_rect

                if line.element.vertical:
                    hwidth = 0.5 * lead.tech.dimensions[1]
                    hlength = 0.5 * lead.tech.dimensions[0]
                    lead.orientation = 3

                    # find if near left or right (decide orientation)
                    # for power leads only right now
                    edge_dist = sym_layout.sub_dim[0] - 0.5 * (trace_rect.left + trace_rect.right)
                    if edge_dist < 0.5 * sym_layout.sub_dim[0]:
                        # right
                        xpos = trace_rect.right - hwidth
                        lead.orientation = 3
                    else:
                        # left
                        xpos = trace_rect.left + hwidth
                        lead.orientation = 4

                    ypos = 0.5 * (trace_rect.bottom + trace_rect.top)
                    lead.footprint_rect = Rect(ypos + hlength, ypos - hlength, xpos - hwidth, xpos + hwidth)
                else:
                    # find if near top or bottom (decide orientation)
                    hwidth = 0.5 * lead.tech.dimensions[0]
                    hlength = 0.5 * lead.tech.dimensions[1]
                    lead.orientation = 1

                    edge_dist = sym_layout.sub_dim[1] - 0.5 * (trace_rect.top + trace_rect.bottom)
                    if edge_dist < 0.5 * sym_layout.sub_dim[1]:
                        # top
                        ypos = trace_rect.top - hlength
                        lead.orientation = 1
                    else:
                        # bottom
                        ypos = trace_rect.bottom + hlength
                        lead.orientation = 2

                    xpos = 0.5 * (trace_rect.left + trace_rect.right)
                    lead.footprint_rect = Rect(ypos + hlength, ypos - hlength, xpos - hwidth, xpos + hwidth)

                lead.center_position = (xpos, ypos)
            elif lead.tech.shape == Lead.ROUND:
                lead_region = sym_info[lead.element.path_id]
                radius = 0.5 * lead.tech.dimensions[0]
                center = [lead_region.left + radius, lead_region.bottom]
                lead.footprint_rect = Rect(center[1] + radius, center[1] - radius,
                                           center[0] - radius, center[0] + radius)
                lead.center_position = center

    def _sym_place_bondwires(self):
        sym_layout = self.engine.sym_layout
        for wire in sym_layout.bondwires:
            if wire.dev_pt is not None:
                sym_layout._place_device_bondwire(wire)


class ET_standalone_Dialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ET_Evaluation_Dialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.tbl_thermal = None
        self.tbl_elec = None
        self.dev_df = None
        self.method = "NSGAII"
        self.parent.opt_algo = "NSGAII"
        self.ui.cmb_opt_algo.currentIndexChanged.connect(self.opt_algo_handler)
        self.perf_dict = self.parent.perf_dict
        self.ui.Tab_model_select.setEnabled(False)
        self.ui.txt_perfname.textChanged.connect(self.perf_name)
        self.ui.btn_thermal_perf.pressed.connect(self.add_perf)
        self.ui.btn_add_elec_perf.pressed.connect(self.add_perf)
        # buttons
        self.ui.btn_done.pressed.connect(self.finished)
        self.ui.btn_remove.pressed.connect(self.remove_row)
        self.ui.btn_dv_states.pressed.connect(self.open_dv_state)
        self.ui.btn_select_mdl.pressed.connect(self.select_RS_model)
        self.ui.btn_save_setup.pressed.connect(self.save_opt_setup)
        self.ui.btn_load_setup.pressed.connect(self.load_opt_setup)

        # others
        self.ui.cmb_electrical_mdl.currentIndexChanged.connect(self.current_model)
        self.init_table()
        self.reload_table()
        self.load_src_sink()

    def opt_algo_handler(self):
        choice = str(self.ui.cmb_opt_algo.currentText())
        print "A", choice
        if choice == "NSGAII":
            self.method = "NSGAII"
            self.parent.opt_algo = "NSGAII"
        else:
            self.method = "NG-RANDOM"
            self.parent.opt_algo = "NG-RANDOM"

    def current_model(self):
        if str(self.ui.cmb_electrical_mdl.currentText()) == "Response Surface Model":
            self.ui.btn_select_mdl.setEnabled(True)

    def select_RS_model(self):
        rs_settings = ModelSelectionDialog(self,
                                           techlib_dir="C:\PowerSynth_git\CornerStitch_fixed\PowerCAD-full\\tech_lib",
                                           mode=2)
        rs_settings.exec_()

    def load_src_sink(self):
        self.ui.cmb_src_select.clear()
        self.ui.cmb_sink_select.clear()
        net_id = []
        for sym in self.parent.engine.sym_layout.all_sym:
            if isinstance(sym, SymPoint):
                if sym.name[0] == 'M':
                    net_id.append(sym.name + '_D')
                    net_id.append(sym.name + '_S')
                    net_id.append(sym.name + '_G')
                else:
                    net_id.append(sym.name)
        self.ui.cmb_src_select.addItems(net_id)
        self.ui.cmb_sink_select.addItems(net_id)

    def perf_name(self):
        if self.ui.txt_perfname != '':
            self.ui.Tab_model_select.setEnabled(True)
        else:
            self.ui.Tab_model_select.setEnabled(False)

    def reload_table(self):
        self.ui.tbl_perf_list.clearContents()
        self.ui.tbl_perf_list.setRowCount(0)
        row_id = 0
        for p_k in self.perf_dict.keys():
            perf = self.perf_dict[p_k]
            self.ui.tbl_perf_list.insertRow(row_id)
            self.ui.tbl_perf_list.setItem(row_id, 0, QtGui.QTableWidgetItem())
            self.ui.tbl_perf_list.setItem(row_id, 1, QtGui.QTableWidgetItem())
            self.ui.tbl_perf_list.setItem(row_id, 2, QtGui.QTableWidgetItem())
            self.ui.tbl_perf_list.item(row_id, 0).setText(p_k)
            self.ui.tbl_perf_list.item(row_id, 1).setText(perf['type'])
            self.ui.tbl_perf_list.item(row_id, 2).setText(perf['Eval'])

    def _sym_find_pt_obj(self, symlayout, name):
        for sym in symlayout.all_sym:
            if sym.name in name:
                return sym

    def add_perf(self):

        if len(self.perf_dict.keys()) < 2:
            if self.ui.Tab_model_select.currentIndex() == 0:
                print "Add thermal performance"
                perf_name = str(self.ui.txt_perfname.text())
                type = 'Thermal'
                mdl_str = str(self.ui.cmb_thermal_mdl.currentText())
                eval_type = str(self.ui.cmb_thermal_type.currentText())
                self.thermal_dev_sel = []
                for row in range(self.ui.tbl_thermal_data.rowCount()):
                    if int(self.ui.tbl_thermal_data.cellWidget(row, 2).isChecked() * 1) == 1:
                        dev_key = str(self.ui.tbl_thermal_data.item(row, 0).text())
                        for dev in self.parent.engine.sym_layout.devices:
                            if dev.name == dev_key:
                                self.thermal_dev_sel.append(dev)
                if mdl_str == "Fast Approximation with FEM":
                    mdl = 1
                elif mdl_str == "Analytical Rectangular Flux":
                    mdl = 2

                if eval_type == "Maximum":
                    stat_func = 1
                elif eval_type == "Average":
                    stat_func = 2
                elif eval_type == "Std Deviation":
                    stat_func = 3
                measure = ThermalMeasure(stat_fn=stat_func, devices=self.thermal_dev_sel, name=perf_name, mdl=mdl)
                self.perf_dict[perf_name] = {'type': type, 'measure': measure, 'Eval': eval_type}
                row_id = self.ui.tbl_perf_list.rowCount()
                if self.thermal_dev_sel != []:
                    self.ui.tbl_perf_list.insertRow(row_id)
                    self.ui.tbl_perf_list.setItem(row_id, 0, QtGui.QTableWidgetItem())
                    self.ui.tbl_perf_list.setItem(row_id, 1, QtGui.QTableWidgetItem())
                    self.ui.tbl_perf_list.setItem(row_id, 2, QtGui.QTableWidgetItem())
                    self.ui.tbl_perf_list.item(row_id, 0).setText(perf_name)
                    self.ui.tbl_perf_list.item(row_id, 1).setText(type)
                    self.ui.tbl_perf_list.item(row_id, 2).setText(eval_type)
                else:
                    QtGui.QMessageBox.about(self, "Reminder", "Please select devices for measurement")
            if self.ui.Tab_model_select.currentIndex() == 1:
                print "Add electrical performance"
                perf_name = str(self.ui.txt_perfname.text())
                type = 'Electrical'
                mdl_str = str(self.ui.cmb_electrical_mdl.currentText())
                eval_type = str(self.ui.cmb_electrical_type.currentText())
                src_type = None
                sink_type = None
                src = str(self.ui.cmb_src_select.currentText())
                if 'S' in src:
                    src_type = 'S'
                elif 'G' in src:
                    src_type = 'G'
                pt1 = self._sym_find_pt_obj(self.parent.engine.sym_layout, src)
                sink = str(self.ui.cmb_sink_select.currentText())
                if 'S' in sink:
                    sink_type = 'S'
                elif 'G' in sink:
                    sink_type = 'G'

                pt2 = self._sym_find_pt_obj(self.parent.engine.sym_layout, sink)
                if mdl_str == "Response Surface Model":
                    mdl = "RS"
                else:
                    mdl = "MS"
                if eval_type != "Capacitance":
                    if eval_type == "Inductance":
                        measure_type = 2
                    if eval_type == "Resistance":
                        measure_type = 1
                    measure = ElectricalMeasure(pt1=pt1, pt2=pt2, name=perf_name, mdl=mdl,
                                                src_sink_type=[src_type, sink_type],
                                                device_state=self.dev_df, measure=measure_type)
                self.perf_dict[perf_name] = {'type': type, 'measure': measure, 'Eval': eval_type}
                row_id = self.ui.tbl_perf_list.rowCount()

                self.ui.tbl_perf_list.insertRow(row_id)
                self.ui.tbl_perf_list.setItem(row_id, 0, QtGui.QTableWidgetItem())
                self.ui.tbl_perf_list.setItem(row_id, 1, QtGui.QTableWidgetItem())
                self.ui.tbl_perf_list.setItem(row_id, 2, QtGui.QTableWidgetItem())
                self.ui.tbl_perf_list.item(row_id, 0).setText(perf_name)
                self.ui.tbl_perf_list.item(row_id, 1).setText(type)
                self.ui.tbl_perf_list.item(row_id, 2).setText(eval_type)
        else:
            QtGui.QMessageBox.about(self, "Limitation", "We only support 2 objectives right now")
        self.ui.txt_perfname.setText(" ")

    def open_dv_state(self):
        dv_state = Device_states_dialog(parent=self, mode=2)
        dv_state.exec_()

    def finished(self):
        self.parent.perf_dict = self.perf_dict
        self.close()

    def init_table(self):
        row_id = self.ui.tbl_thermal_data.rowCount()
        if self.parent.engine.sym_layout != None:
            for symb_obj in self.parent.engine.sym_layout.all_sym:
                if isinstance(symb_obj, SymPoint):
                    if symb_obj.name[0] == 'M':
                        self.ui.tbl_thermal_data.insertRow(row_id)
                        self.ui.tbl_thermal_data.setItem(row_id, 0, QtGui.QTableWidgetItem())
                        self.ui.tbl_thermal_data.setItem(row_id, 1, QtGui.QTableWidgetItem())
                        self.ui.tbl_thermal_data.setItem(row_id, 2, QtGui.QTableWidgetItem())
                        self.ui.tbl_thermal_data.item(row_id, 0).setText(str(symb_obj.name))
                        self.ui.tbl_thermal_data.item(row_id, 1).setText(str(symb_obj.tech.heat_flow))
                        btn_sel = QtGui.QCheckBox(self.ui.tbl_thermal_data)
                        self.ui.tbl_thermal_data.setCellWidget(row_id, 2, btn_sel)  # Drain to source
                        row_id += 1

    def remove_row(self):
        selected_row = self.ui.tbl_perf_list.currentRow()
        row_id = self.ui.tbl_perf_list.selectionModel().selectedIndexes()[0].row()
        perf_name = str(self.ui.tbl_perf_list.item(row_id, 0).text())
        del self.perf_dict[perf_name]
        self.ui.tbl_perf_list.removeRow(selected_row)


    def load_opt_setup(self):
        filename = QFileDialog.getOpenFileName(caption=r"Optimization log file", filter="log file (*.log)")

        opt_setup = load_file(filename[0])
        # thermal
        self.ui.cmb_thermal_mdl.setCurrentIndex(opt_setup.thermal_mode)
        self.ui.cmb_thermal_type.setCurrentIndex(opt_setup.thermal_func)
        try:
            self.thermal_dev_sel= opt_setup.thermal_dev_tbl
            for dev in self.thermal_dev_sel:
                for row in range(self.ui.tbl_thermal_data.rowCount()):
                    dev_key = str(self.ui.tbl_thermal_data.item(row, 0).text())
                    if dev.name == dev_key:
                        self.ui.tbl_thermal_data.cellWidget(row, 2).setChecked(1)
        except:
            print "WRONG SETUP"
        # electrical

        self.ui.cmb_electrical_mdl.setCurrentIndex(opt_setup.electrical_mode)
        self.ui.cmb_electrical_type.setCurrentIndex(opt_setup.electrical_func)
        try:
            index1 = self.ui.cmb_src_select.findText(opt_setup.e_src, QtCore.Qt.MatchFixedString)
            self.ui.cmb_src_select.setCurrentIndex(index1)
            index2=self.ui.cmb_src_select.findText(opt_setup.e_sink, QtCore.Qt.MatchFixedString)
            self.ui.cmb_sink_select.setCurrentIndex(index2)
        except:
            print "WRONG SETUP"

        #print type(opt_setup.electrical_dev_state)
        self.dev_df=opt_setup.electrical_dev_state
        dv_state = Device_states_dialog(parent=self, mode=2)
        for row in range(dv_state.ui.tbl_states.rowCount()):
            for col in range(dv_state.ui.tbl_states.columnCount()):
                if self.dev_df.iat[row,col]==1:
                    print "Here"
                    dv_state.ui.tbl_states.cellWidget(row, col).setChecked(1)
        # Performances
        self.perf_dict= opt_setup.perf_table

        # Optimization Options
        if opt_setup.plot_pareto ==1:
            self.ui.rb_plot_pareto.setChecked(1)
        self.ui.cmb_opt_algo.setCurrentIndex(opt_setup.algorithm)




    def save_opt_setup(self):
        print "save setup"

        filename = QFileDialog.getSaveFileName(self,"Select Image to Save", "C://", "Opt Setup (*.log)")

        opt_setup = OptSetup()
        # Thermal
        opt_setup.thermal_dev_tbl = self.thermal_dev_sel
        mdl_str = str(self.ui.cmb_thermal_mdl.currentText())
        eval_type = str(self.ui.cmb_thermal_type.currentText())

        if mdl_str == "Fast Approximation with FEM":
            opt_setup.thermal_mode = 0  # 0 for FEM approximate 1 for analytical
        elif mdl_str == "Analytical Rectangular Flux":
            opt_setup.thermal_mode = 1  # 0 for FEM approximate 1 for analytical
        if eval_type == "Maximum":
            opt_setup.thermal_func = 0  # 0 for maximum, 1 for avg, 2 for std dev
        elif eval_type == "Average":
            opt_setup.thermal_func = 1  # 0 for maximum, 1 for avg, 2 for std dev
        elif eval_type == "Std Deviation":
            opt_setup.thermal_func = 2  # 0 for maximum, 1 for avg, 2 for std dev


        # Electrical
        opt_setup.electrical_dev_state = self.dev_df

        mdl_str = str(self.ui.cmb_electrical_mdl.currentText())
        eval_type = str(self.ui.cmb_electrical_type.currentText())

        if mdl_str == "Response Surface Model":
            opt_setup.electrical_mode = 0  # 0 for RS, 1 for MS, 2 for PEEC
        elif mdl_str == "Microstrip Equations":
            opt_setup.electrical_mode = 2 # 0 for RS, 1 for MS, 2 for PEEC
        elif mdl_str == "3D Hierarchical PEEC":
            opt_setup.electrical_mode = 1  # 0 for RS, 1 for MS, 2 for PEEC

        if eval_type == "Capacitance":
            opt_setup.electrical_func = 2  # 1 R, 0 L, 2 C
        elif eval_type == "Inductance":
            opt_setup.electrical_func = 0  # 1 R, 0 L, 2 C
        elif eval_type == "Resistance":
            opt_setup.electrical_func = 1  # 1 R, 0 L, 2 C

        opt_setup.e_src = str(self.ui.cmb_src_select.currentText())
        opt_setup.e_sink = str(self.ui.cmb_sink_select.currentText())
        # Performances
        opt_setup.perf_table = self.perf_dict

        # Optimization Options
        opt_setup.plot_pareto = self.ui.rb_plot_pareto.isChecked()
        algorithm = str(self.ui.cmb_opt_algo.currentText())
        if algorithm=="NSGAII":
            opt_setup.algorithm = 0  # 0: NSGAII , 1: NG-RANDOM
        elif algorithm=="Non-Guided Randomization":
            opt_setup.algorithm = 1  # 0: NSGAII , 1: NG-RANDOM
        save_file(opt_setup,filename[0])
class Waiting_dialog(QtGui.QDialog):
    def __init__(self, parent, txt_msg="none"):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_waiting_dialog()
        self.ui.setupUi(self)
        self.parent = parent
        self.ui.txt_wait_msg.setText(txt_msg)

    def run_process(self, code):
        self.show()
        exec (code)
        self.close()