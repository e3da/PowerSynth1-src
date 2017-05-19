'''
@author: Peter N. Tucker, Brett Shook,Quang Le
Major Changes:
Brett Shook - Added separate Performance Measure List system 4/29/2013
Brett Shook - Added separate Component Selection system 3/21/2014
            - 
'''
# add for packaging
#import six

#import packaging

#import packaging.version

#import packaging.specifiers
'''----------------------------------'''
import os
import shutil
import sys
import time
import traceback

from PySide import QtCore, QtGui
from PySide.QtGui import QFileDialog

import powercad.sym_layout.plot as plot

plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.patches import Rectangle, Circle
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from powercad.project_builder.symmetry_list import SymmetryListUI
from powercad.project_builder.performance_list import PerformanceListUI
from powercad.project_builder.windows.mainWindow import Ui_MainWindow
from powercad.project_builder.windows.sol_window import SolutionWindow
from powercad.project_builder.proj_dialogs import NewProjectDialog, OpenProjectDialog, EditTechLibPathDialog, \
    GenericDeviceDialog,LayoutEditorDialog, ResponseSurfaceWizard


from powercad.drc.process_design_rules_editor import ProcessDesignRulesEditor
from powercad.tech_lib.tech_lib_wiz import TechLibWizDialog

from powercad.layer_stack.layer_stack_import import LayerStackImport

from powercad.sym_layout.symbolic_layout import SymLine
from powercad.design.library_structures import BondWire, Lead
from powercad.sol_browser.graph_app import GrapheneWindow
from powercad.design.project_structures import *
from powercad.sym_layout.svg import LayoutLine, LayoutPoint
from powercad.general.settings.save_and_load import save_file, load_file
from powercad.general.settings.settings import *
class ProjectBuilder(QtGui.QMainWindow):
    
    # Relative paths -> use forward slashes for platform independence
    TEMP_DIR = os.path.abspath(TEMP_DIR)
    
    LAYOUT_SELECTION_PLOT = 0
    SYMMETRY_PLOT = 1
    CONSTRAINT_PLOT = 2 
    MEASURES_PLOT = 3
    
    STACK_PAGE = 0
    LAYOUT_PAGE = 1
    SYMMETRY_PAGE = 2
    CONSTRAINT_PAGE = 3
    MEASURE_PAGE = 4
    RESULTS_PAGE = 5
    
    """Main Window"""
    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)
        # current project
        self.project = None
        self.init()
        
    def init(self):
        """Set up the main window"""
        # set up main window GUI 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # display logo
#        self.ui.label_4.setPixmap(self.LOGO_PATH)
        
        # display module stack image
#        self.ui.lbl_modStackImg.setPixmap(self.STACK_IMG_PATH) 
        # connect actions
        self.ui.navigation.currentChanged.connect(self.change_stacked)
        self.ui.btn_newProject.pressed.connect(self.new_project)
        self.ui.btn_addDevice.pressed.connect(self.add_to_device_table)
        self.ui.btn_runSim.pressed.connect(self.start_optimization)
        self.ui.btn_open_sol_browser.pressed.connect(self.open_sol_browser)
        self.ui.lst_categories.clicked.connect(self.display_categ_items)
        self.ui.lst_solution.itemDoubleClicked.connect(self.show_sol_doc)
        
        self.ui.btn_previous.pressed.connect(self.previous)
        self.ui.btn_next.pressed.connect(self.next)
        self.ui.tbl_projDevices.cellPressed.connect(self.component_pressed)
        self.ui.btn_modify_component.pressed.connect(self.modify_component)
        self.ui.btn_removeDevice.pressed.connect(self.remove_component)
        
        # Module stack page
        self.ui.btn_import_layer_stack.pressed.connect(self.import_layer_stack)

        # Constraints page
        self.ui.txt_minWidth.textEdited.connect(self.constraint_min_edit)
        self.ui.txt_maxWidth.textEdited.connect(self.constraint_max_edit)
        self.ui.txt_fixedWidth.textEdited.connect(self.constraint_fixed_edit)
        self.ui.btn_remove_constraint.pressed.connect(self.constraint_remove)
        
        # Menu bar items
        self.ui.actionNew_Project.triggered.connect(self.new_project)
        self.ui.actionSave_Project.triggered.connect(self.save_project)
        self.ui.action_save_project_as.triggered.connect(self.save_project_as)
        self.ui.actionOpen_Project.triggered.connect(self.open_project)
        self.ui.btn_openProject.pressed.connect(self.open_project)
        self.ui.action_edit_design_rules.triggered.connect(self.open_design_rule_editor)
        self.ui.action_open_tech_lib_editor.triggered.connect(self.open_tech_lib_editor)
        self.ui.action_edit_tech_path.triggered.connect(self.edit_tech_lib_path)
        self.ui.action_load_symbolic_layout.triggered.connect(self.load_symbolic_layout)
        self.ui.actionExport_Layout_Script.triggered.connect(self.export_layout_script) # export layout to script action
        self.ui.actionOpen_Layout_Editor.triggered.connect(self.open_layout_editor) # Open script
        self.ui.actionResponse_Surface_Setup.triggered.connect(self.open_response_surface_wiz)
        # Disable project interfaces until a project is loaded or created
        self.enable_project_interfaces(False)
        # This is the current color wheel.
        # This is a temporary fix for something that should probably be more dynamic later. 
        self.color_wheel = [QtGui.QColor(255, 0, 0),
                            QtGui.QColor(0, 255, 0),
                            QtGui.QColor(0, 0, 255),
                            QtGui.QColor(255, 255, 0),
                            QtGui.QColor(255, 0, 255),
                            QtGui.QColor(0,255,255),
                            QtGui.QColor(128,0,0),
                            QtGui.QColor(0,128,0),
                            QtGui.QColor(0,0,128),
                            QtGui.QColor(255,255,255),
                            QtGui.QColor(128, 128, 0),
                            QtGui.QColor(128, 0, 128),
                            QtGui.QColor(0,128,128)]

        self.default_color = '#454545'
        
        # setup widgets used for plotting symbolic layouts
        self.setup_layout_plots()
        
        # set up table that displays added devices
        self.ui.tbl_projDevices.setColumnCount(2)
        self.ui.tbl_projDevices.setColumnWidth(0,50)
        self.ui.tbl_projDevices.horizontalHeader().setStretchLastSection(True)     
    def enable_project_interfaces(self, enable):
        # Navigation menu
        self.ui.navigation.setEnabled(enable)
        
        # Menu bar
        self.ui.action_edit_design_rules.setEnabled(enable)
        self.ui.actionSave_Project.setEnabled(enable)
        self.ui.action_save_project_as.setEnabled(enable)
        self.ui.action_edit_design_rules.setEnabled(enable)
        self.ui.actionExport_Layout_Script.setEnabled(enable)
        self.ui.action_open_tech_lib_editor.setEnabled(enable)
        self.ui.action_edit_tech_path.setEnabled(enable)
        self.ui.action_load_symbolic_layout.setEnabled(enable)
    def refresh_ui(self): #Quang: clear all the old project  data when new project is loaded
        self.ui.tbl_projDevices.clear()
        self.ui.tbl_projDevices.setRowCount(0)
        self.ui.tbl_symmetry.clear()
        self.ui.tbl_symmetry.setRowCount(0)
        self.ui.tbl_performance.clear()
        self.ui.tbl_performance.setRowCount(0)
        
        
    def reload_ui(self):
        # setup fields in subsections
        #self.add_page_quick_fix()
        self.refresh_ui()
        self.setup_dev_select_fields()
        self.ui.txt_numGenerations.setText(str(100)) # default number of generations to 100
        # the color wheel is not that long, so these are used in different sections to just loop back to the beginning once the end is reached
        self.cw1 = 0
        
        # used for error checking constraints
        self.constraint_error = False
        self.constraint_select = None
        
        self.fill_material_cmbBoxes() # sxm- initialize dropdown menus of items in module stack
        
        # Used to store which artist object is bound to which component row
        self.component_row_dict = {}
        
        self.sol_browser = None
        
        self.perf_list = PerformanceListUI(self)
        self.symmetry_ui = SymmetryListUI(self)
        
    def change_stacked(self, index):
        """Keep stacked widget current with navigation"""
        # the stacked widget is what shows everything like the symbolic layouts.  Different pages in the stacked widget show different things
        # "navigation" is the main bar on the left
        
        if index == self.CONSTRAINT_PAGE:
            self.enter_constraint_page()
        
        if self.constraint_error:
            # don't move on if error in constraints
            self.ui.navigation.setCurrentIndex(self.CONSTRAINT_PAGE)

        self.ui.stackedWidget.setCurrentIndex(self.ui.navigation.currentIndex()) # Ensure the content on the right frame of the window corresponds to the content on the selected tab on the left pane. 
        
        
    def new_project(self):
        """Create new project. Display prompt for necessary information"""
        # bring up new project dialog
        new_dialog = NewProjectDialog(self)
        if(new_dialog.exec_()):
            # create new project
            self.project = new_dialog.create()
            self.export_layout_script()           # Export layout script to project directory
            self.reload_ui()
            # set navigation to first step
            self.ui.navigation.setCurrentIndex(0)
            self.ui.stackedWidget.setCurrentIndex(0)
            self.enable_project_interfaces(True)
            # draws all symbolic layouts
            self.load_layout_plots()


    def open_project(self):
        """Open project. Display prompt for necessary information"""
        # bring up open project dialog
        self.layout_script_dir=None
        open_dialog = OpenProjectDialog(self)
        if(open_dialog.exec_()):
            self.project.tech_lib_dir=DEFAULT_TECH_LIB_DIR#Quang
            
            self.export_layout_script()           # Export layout script to project directory
            self.reload_ui()
            
            # set navigation to first step
            self.ui.navigation.setCurrentIndex(0)
            self.ui.stackedWidget.setCurrentIndex(0)
              
            self.enable_project_interfaces(True)
            self.load_layout_plots()
            self.load_moduleStack()
            self.load_deviceTable()
            self.symmetry_ui.load_symmetries()
            self.perf_list.load_measures()
            self.load_saved_solutions_list()
            
            self.fill_material_cmbBoxes() #Quang 
            
    def open_design_rule_editor(self):
        # Check if a project has been opened/created
        if self.ui.navigation.isEnabled():
            design_rule_dialog = ProcessDesignRulesEditor(self)
            design_rule_dialog.exec_()
        else:
            QtGui.QMessageBox.warning(self, "Project Needed", "A project needs to be loaded into the program first.")

    def open_response_surface_wiz(self):
        if self.ui.navigation.isEnabled():
            rs_settings=ResponseSurfaceWizard(self)
            rs_settings.show() # change this to a dialog
            print "code me"

    def open_tech_lib_editor(self):
        techlib = TechLibWizDialog(self, self.project.tech_lib_dir)
        techlib.show()
        
    def generic_device_dialog(self):
        print 'here'
        device_path = os.path.join(self.project.tech_lib_dir,'Layout_Selection\Device' )
        dev_dialog=GenericDeviceDialog(self,device_path)
        if(dev_dialog.exec_()):
            print 1
    def export_layout_script(self):
        # qmle 10-18-2016
        # This method will export the current layout (of the project) to script code
        save_path= self.layout_script_dir                    # choosing the directory for the script 
        path=os.path.join(save_path,'layout.psc')            # script name = project name + extemsopn
        print self.layout_script_dir
        lines=[]                                             # list of lines to write in txt 
        id=0                                                 # set a counter id
        for obj in self.project.symb_layout.layout:          # list out obj in symbolic layout  
            if isinstance(obj,LayoutLine):                   # check if it is a line  
                line_str =str(id).zfill(4)+' l '+'('+str(obj.pt1[0])+','+str(obj.pt1[1])+') '+'('+str(obj.pt2[0])+','+str(obj.pt2[1])+')' # write the line into string
                lines.append(line_str)                       # append to final list
            elif isinstance(obj, LayoutPoint):               # check if it is a point
                line_str =str(id).zfill(4)+' p '+'('+str(obj.pt[0])+','+str(obj.pt[1])+')'  # write the line into string  
                lines.append(line_str)                       # append to final list 
            id+=1                                            # increase id count
        f = open(path, 'w')                                  # open text file
        self.layout_script="\n".join(lines)                  
        f.write(self.layout_script)                          # write text to text file
        QtGui.QMessageBox.about(self, "Layout Script Saved", "Layoyt Script Saved")
    def open_layout_editor(self):
        # qmle 1-11-2016
        # This will open a LayoutEditor Window, which allow user to change the symbolic layout in real time
        layout_editor=LayoutEditorDialog(self)
        layout_editor.exec_()
        path=os.path.join(self.layout_script_dir,'layout.psc')
        self.project.symb_layout.load_layout(path,'script')
        self.load_layout_plots()
    def edit_tech_lib_path(self):
        # Check if a project has been opened/created
        if self.ui.navigation.isEnabled():
            tech_path_dialog = EditTechLibPathDialog(self)
            tech_path_dialog.exec_()
            
    def previous(self):
        """Selects previous navigation section"""
        if self.ui.navigation.isEnabled():
            index = self.ui.navigation.currentIndex()
            if index > 0:
                self.ui.navigation.setCurrentIndex(index-1)
        
    def next(self):
        """Selects next navigation section"""
        if self.ui.navigation.isEnabled():
            index = self.ui.navigation.currentIndex()
            if index < (self.ui.navigation.count()-1):
                self.ui.navigation.setCurrentIndex(index+1)
        
    def setup_layout_plots(self):
        """ Create figures, canvases, axes, and layout for each stacked widget page. 
        Connect all symbolic layouts to their respective pick events. """
        # create figures, canvases, axes, and layout for each stacked widget page
        self.symb_fig = [Figure(),Figure(),Figure(),Figure(),Figure()]
        self.symb_canvas = []
        self.symb_axis = []
        
        for window in xrange(4):
            # make canvas and axis
            self.symb_canvas.append(FigureCanvas(self.symb_fig[window]))
           
            self.symb_axis.append(self.symb_fig[window].add_subplot(111, aspect=1.0))
            # hide the axes
            self.symb_fig[window].patch.set_facecolor('#F0F0F0')
            self.symb_axis[window].set_frame_on(False)
            self.symb_axis[window].set_axis_off()
            # apply layout to make matplotlib fill window dynamically
            grid_layout = QtGui.QGridLayout(self.ui.stackedWidget.widget(window+1))
            grid_layout.setContentsMargins(0,0,0,0)
            grid_layout.addWidget(self.symb_canvas[window],0,0,1,1)
        
        # connect all symbolic layouts to their respective pick events
        self.symb_canvas[0].mpl_connect('pick_event', self.device_pick)
        self.symb_canvas[2].mpl_connect('pick_event', self.constraint_pick)
    def save_layout_plots(self):
        count=0
        for figure in self.symb_fig:
            count+=1
            name='fig'+str(count)+'.svg'
            figure.savefig(name)   
    def load_layout_plots(self):
        """Load symbolic layout from svg file and draw all necessary symbolic layouts in stacked widget"""
        symlayout = self.project.symb_layout
        layout = symlayout.all_sym
        self.patch_dict = PatchDictionary()  # Dictionary to map layout objects to patches
        
        # populate each matplotlib with rectangles and circles from symbolic layout
        for window in range(4):
            # only plot device circles in Device Selection and Performance identification
            # now include symmetries
            if window == 0 or window == 1 or window == 3:
                plt_devices = True
            else:
                plt_devices = False
                
            # plot everything
            self.plot_sym_objects(layout, symlayout.xlen,symlayout.ylen,
                                  self.symb_fig[window],self.symb_axis[window],
                                  window, plt_devices)
            self.symb_canvas[window].draw() # sxm - displayes the symbolic layout to the user. (Until this point most of the work was happening in the backend). 
            #self.save_layout_plots()
            
    def plot_sym_objects(self, layout_objs, xlen, ylen, figure, axis, window, plt_circles=True):
        """Plot symbolic layout rectangles and circles in matplotlib objects"""
        # used to temporarily hold horizontal lines and circles to plot them later
        temp_horz_objs = []
        temp_circ_objs = []
        
        axis.clear()
        axis.set_frame_on(True) #sxm originally false
        #axis.set_axis_off()#sxm commented -- uncomment this to remove axis from symbolic layout
        # go through each object and plot all vertical lines
        for obj in layout_objs:
            if isinstance(obj, SymLine): 
                lw=0.2 # width of lines
                
                if obj.element.pt1[0]==obj.element.pt2[0]: # vertical rectangle
                    # create rectangle patch
                    patch = Rectangle((obj.element.pt1[0]-lw/2.0,obj.element.pt1[1]-lw/2.0),lw,obj.element.pt2[1]-obj.element.pt1[1]+lw,facecolor=self.default_color,alpha=0.5,picker=True)
                    # used for constraint section
                    patch.symmetry = None
                    patch.window = window
                    # link to object
                    self.patch_dict[patch] = obj
#                    tech_elem_dict[obj] = patch
                    # add patch to axis
                    axis.add_patch(patch)
                    
                else: # horizontal rectangle
                    temp_horz_objs.append(obj) # save for later
                    
            else: # circle
                temp_circ_objs.append(obj) # save for later
        # next plot all horizontal lines        
        for obj in temp_horz_objs:
            patch = Rectangle((obj.element.pt1[0]-lw/2.0,obj.element.pt1[1]-lw/2.0),obj.element.pt2[0]-obj.element.pt1[0]+lw,lw,facecolor=self.default_color,alpha=0.5,picker=True)
            # used for constraint section
            patch.symmetry = None
            patch.window = window
            self.patch_dict[patch] = obj
#            tech_elem_dict[obj] = patch
            axis.add_patch(patch)
            
        # then plot all circles
        if plt_circles:
            for obj in temp_circ_objs:
                patch = Circle(obj.element.pt, facecolor=self.default_color, radius=0.25, alpha=0.5,picker=1)
                # used for constraint section
                patch.symmetry = None
                patch.window = window
                self.patch_dict[patch] = obj
#                tech_elem_dict[obj] = patch
                axis.add_patch(patch)
        
        # set up axis limits
        axis.axis([-1, xlen, -1, ylen])
        
        self.symb_axis[0].axis([-1,xlen,-1,ylen])

# ------------------------------------------------------------------------------------------        
# ------ Module Stack ----------------------------------------------------------------------

    def import_layer_stack(self):   # Import layer stack from CSV file
        try:
            last_entries = load_file(LAST_ENTRIES_PATH)
            prev_folder = last_entries[0]
        except:
            prev_folder = 'C://'
        # Open a layer stack CSV file and extract the layer stack data from it
        try:
            layer_stack_csv_file = QFileDialog.getOpenFileName(self, "Select Layer Stack File", prev_folder, "CSV Files (*.csv)")
            layer_stack_csv_file=layer_stack_csv_file[0]
            layer_stack_import = LayerStackImport(layer_stack_csv_file)
            layer_stack_import.import_csv()
        except:
            QtGui.QMessageBox.warning(self, "Layer Stack Import Failed", "ERROR: Could not import layer stack from CSV.")

        if layer_stack_import.compatible:
            # Layer stack compatible - fill module stack UI fields with imported values
            self.ui.txt_baseWidth.setText(str(layer_stack_import.baseplate.dimensions[0]))
            self.ui.txt_baseLength.setText(str(layer_stack_import.baseplate.dimensions[1]))
            self.ui.txt_baseThickness.setText(str(layer_stack_import.baseplate.dimensions[2]))
            self.ui.txt_baseConvection.setText(str(layer_stack_import.baseplate.eff_conv_coeff))
            self.ui.txt_subAttchThickness.setText(str(layer_stack_import.substrate_attach.thickness))
            self.ui.txt_subWidth.setText(str(layer_stack_import.substrate.dimensions[0]))
            self.ui.txt_subLength.setText(str(layer_stack_import.substrate.dimensions[1]))
            self.ui.txt_subLedge.setText(str(layer_stack_import.substrate.ledge_width))

            # Notify user of import success and any warnings
            if layer_stack_import.warnings == []:
                QtGui.QMessageBox.about(self, "Layer Stack Imported", "Layer Stack import successful (No warnings).")
            else:
                if len(layer_stack_import.warnings) == 1:
                    QtGui.QMessageBox.about(self, "Layer Stack Imported", "Layer Stack import successful with " + str(len(layer_stack_import.warnings)) + ' warning.')
                    QtGui.QMessageBox.warning(self, "Layer Stack Import Warning", "WARNING: " + layer_stack_import.warnings[0])
                else:
                    QtGui.QMessageBox.about(self, "Layer Stack Imported", "Layer Stack import successful with " + str(len(layer_stack_import.warnings)) + ' warnings.')
                    warnings_msg = ""
                    for warning in layer_stack_import.warnings:
                        warnings_msg += ("WARNING: " + warning + "\n")
                    QtGui.QMessageBox.warning(self, "Layer Stack Import Warnings", warnings_msg)

        else:
            # Layer stack not compatible - notify the user of import failure
            QtGui.QMessageBox.warning(self, "Layer Stack Import Failed", "ERROR: " + layer_stack_import.error_msg)


    def fill_material_cmbBoxes(self):
        """Fill combo boxes in module stack with materials from Tech Library"""
        # Add materials to substrate combobox
        substrate_dir = os.path.join(self.project.tech_lib_dir, "Substrates")
        self.substrate_model = QtGui.QFileSystemModel()
        self.substrate_model.setRootPath(substrate_dir)
        self.ui.cmb_subMaterial.setModel(self.substrate_model)
        self.ui.cmb_subMaterial.setRootModelIndex(self.substrate_model.setRootPath(substrate_dir))
        self.substrate_model.setFilter(QtCore.QDir.Files)
        self.ui.cmb_subMaterial.clearEditText()
        # Add materials to substrate attach combobox
        substrateAttch_dir = os.path.join(self.project.tech_lib_dir, "Substrate_Attaches")
        self.substrateAttch_model = QtGui.QFileSystemModel()
        self.substrateAttch_model.setRootPath(substrateAttch_dir)
        self.ui.cmb_subAttchMaterial.setModel(self.substrateAttch_model)
        self.ui.cmb_subAttchMaterial.setRootModelIndex(self.substrateAttch_model.setRootPath(substrateAttch_dir))
        self.substrateAttch_model.setFilter(QtCore.QDir.Files)
        self.ui.cmb_subAttchMaterial.clearEditText()
        # Add materials to baseplate combobox
        baseplate_dir = os.path.join(self.project.tech_lib_dir, "Baseplates")
        self.baseplate_model = QtGui.QFileSystemModel()
        self.baseplate_model.setRootPath(baseplate_dir)
        self.ui.cmb_baseMaterial.setModel(self.baseplate_model)
        self.ui.cmb_baseMaterial.setRootModelIndex(self.baseplate_model.setRootPath(baseplate_dir))
        self.baseplate_model.setFilter(QtCore.QDir.Files)
        self.ui.cmb_baseMaterial.clearEditText()
        
    def create_baseplate(self):
        error = False
        
        # reset all error messages
        for lbl in [self.ui.lbl_err_baseConvection, self.ui.lbl_err_baseLength, self.ui.lbl_err_baseMaterial, self.ui.lbl_err_baseThickness, self.ui.lbl_err_baseWidth]:
            lbl.setText("")
            
        # check all textbox inputs for correct type
        if(not self.ui.txt_baseConvection.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_baseConvection.setText("Error: Must be a number")
            error = True
        if(not self.ui.txt_baseLength.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_baseLength.setText("Error: Must be a number")
            error = True 
        if(not self.ui.txt_baseThickness.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_baseThickness.setText("Error: Must be a number")
            error = True
        if(not self.ui.txt_baseWidth.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_baseWidth.setText("Error: Must be a number")
            error = True
        
        # check material properties input  
        try:
            dims = (float(self.ui.txt_baseWidth.text()),float(self.ui.txt_baseLength.text()),float(self.ui.txt_baseThickness.text()))
            eff_conv_coeff = float(self.ui.txt_baseConvection.text())
            tech_path = os.path.join(self.project.tech_lib_dir, "Baseplates", self.ui.cmb_baseMaterial.currentText())
            tech_lib_obj = load_file(tech_path)
            self.project.module_data.baseplate = BaseplateInstance(dims,eff_conv_coeff,tech_lib_obj)
        except:
            self.ui.lbl_err_baseMaterial.setText("Error")
            error = True
            print traceback.print_exc()
            
        if error:
            print "Error Creating Baseplate"
       
        return error
        
    def create_substrate(self):
        error = False
        
        # reset all error messages
        for lbl in [self.ui.lbl_err_subMaterial, self.ui.lbl_err_subWidth, self.ui.lbl_err_subLength, self.ui.lbl_err_subLedge]:
            lbl.setText("")
            
        # check all textbox inputs for correct type
        if(not self.ui.txt_subWidth.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_subWidth.setText("Error: Must be a number")
            error = True
        if(not self.ui.txt_subLength.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_subLength.setText("Error: Must be a number")
            error = True
        if(not self.ui.txt_subLedge.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_subLedge.setText("Error: Must be a number")
            error = True
        
        # check material properties input    
        try:            
            dims = (float(self.ui.txt_subWidth.text()),float(self.ui.txt_subLength.text()))
            # Make sure baseplate dimensions are larger than substrate
            bp_dims = self.project.module_data.baseplate.dimensions
            if dims[0] > bp_dims[0]:
                error = True
                self.ui.lbl_err_subWidth.setText("Error: Must be smaller than baseplate") 
            if dims[1] > bp_dims[1]:
                error = True
                self.ui.lbl_err_subLength.setText("Error: Must be smaller than baseplate")
                
            ledge_width = float(self.ui.txt_subLedge.text())
            tech_path = os.path.join(self.project.tech_lib_dir, "Substrates", self.ui.cmb_subMaterial.currentText())
            tech_lib_obj = load_file(tech_path)
            self.project.module_data.substrate = SubstrateInstance(dims,ledge_width,tech_lib_obj)
        except:
            self.ui.lbl_err_subMaterial.setText("Error")
            error = True
            print traceback.print_exc()
            
        if error:
            print "Error Creating Substrate"
       
        return error
        
    def create_substrate_attach(self):
        error = False
        
        # reset all error messages
        for lbl in [self.ui.lbl_err_subAttchMaterial, self.ui.lbl_err_subAttchThickness]:
            lbl.setText("")
            
        # check all textbox inputs for correct type
        if(not self.ui.txt_subAttchThickness.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.ui.lbl_err_subAttchThickness.setText("Error: Must be a number")
            error = True
        
        # check material properties input  
        try:
            thickness = float(self.ui.txt_subAttchThickness.text())
            tech_path = os.path.join(self.project.tech_lib_dir, "Substrate_Attaches", self.ui.cmb_subAttchMaterial.currentText())
            tech_lib_obj = load_file(tech_path)
            self.project.module_data.substrate_attach = SubstrateAttachInstance(thickness,tech_lib_obj)
        except:
            self.ui.lbl_err_subAttchMaterial.setText("Error")
            error = True
            print traceback.print_exc()

        if error:
            print "Error Creating Substrate Attach"

        return error

    def create_system_properties(self):
        # Reset all error messages
        for lbl in [self.ui.lbl_err_switchFreq, self.ui.lbl_err_ambTemp]:
            lbl.setText("")

        # check switching frequency for errors
        switch_check = not (self.ui.txt_switchFreq.text().replace(".", "", 1).replace("e", "", 1).isdigit())
        if switch_check:
            self.ui.lbl_err_switchFreq.setText("Error: Must be a number")
            print "Error with Switching Frequency input"
        else:
            self.ui.lbl_err_switchFreq.setText("")
            self.project.module_data.frequency = float(self.ui.txt_switchFreq.text())

        # check ambient temp for errors
        temp_check = not (self.ui.txt_ambTemp.text().replace(".", "", 1).replace("e", "", 1).isdigit())
        if temp_check:
            self.ui.lbl_err_ambTemp.setText("Error: Must be a number")
            print "Error with ambient temperature input"
        else:
            self.ui.lbl_err_ambTemp.setText("")
            self.project.module_data.ambient_temp = float(self.ui.txt_ambTemp.text())

        return (switch_check or temp_check)

    def build_module_stack(self):
        """Build baseplate, substrate, and substrate attach for module stack and error check user input"""
        '''Quang: This method will check if the inputs of all materials properties in the Module stack are valid'''
        # create module stack and check for errors
        base_check = self.create_baseplate()
        sub_check = self.create_substrate()
        attach_check = self.create_substrate_attach()
        sys_prop_check = self.create_system_properties()

        if (base_check) or (sub_check) or (attach_check) or (sys_prop_check): #error
            self.ui.navigation.setItemText(0, "Module Stack  *** Error ***")
            return False
        else:
            self.ui.navigation.setItemText(0, "Module Stack")
            return True

    def save_moduleStack(self):
        self.project.module_stack_edit = [self.ui.cmb_subMaterial.currentText(),
                                          self.ui.txt_subWidth.text(),
                                          self.ui.txt_subLength.text(),
                                          self.ui.txt_subLedge.text(),
                                          self.ui.cmb_subAttchMaterial.currentText(),
                                          self.ui.txt_subAttchThickness.text(),
                                          self.ui.cmb_baseMaterial.currentText(),
                                          self.ui.txt_baseWidth.text(),
                                          self.ui.txt_baseLength.text(),
                                          self.ui.txt_baseThickness.text(),
                                          self.ui.txt_baseConvection.text(),
                                          self.ui.txt_switchFreq.text(),
                                          self.ui.txt_ambTemp.text()]

    def load_moduleStack(self):
        self.ui.cmb_subMaterial.setEditText(self.project.module_stack_edit[0])
        self.ui.txt_subWidth.setText(self.project.module_stack_edit[1])
        self.ui.txt_subLength.setText(self.project.module_stack_edit[2])
        self.ui.txt_subLedge.setText(self.project.module_stack_edit[3])
        self.ui.cmb_subAttchMaterial.setEditText(self.project.module_stack_edit[4])
        self.ui.txt_subAttchThickness.setText(self.project.module_stack_edit[5])
        self.ui.cmb_baseMaterial.setEditText(self.project.module_stack_edit[6])
        self.ui.txt_baseWidth.setText(self.project.module_stack_edit[7])
        self.ui.txt_baseLength.setText(self.project.module_stack_edit[8])
        self.ui.txt_baseThickness.setText(self.project.module_stack_edit[9])
        self.ui.txt_baseConvection.setText(self.project.module_stack_edit[10])
        self.ui.txt_switchFreq.setText(self.project.module_stack_edit[11])
        self.ui.txt_ambTemp.setText(self.project.module_stack_edit[12])


# ------------------------------------------------------------------------------------------
# ------ Component Selection ------------------------------------------------------------------

    def setup_dev_select_fields(self):
        # set up device categories
        self.tech_lib_path = os.path.join(self.project.tech_lib_dir, "Layout_Selection")
        self.categ_list_model = QtGui.QFileSystemModel()
        self.categ_list_model.setRootPath(self.tech_lib_path)
        self.ui.lst_categories.setModel(self.categ_list_model)
        self.ui.lst_categories.setRootIndex(self.categ_list_model.setRootPath(self.tech_lib_path))
        self.categ_list_model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)

        # used later to setup device category items
        self.device_list_model = QtGui.QFileSystemModel()
        self.attach_list_model = QtGui.QFileSystemModel()
        self.attach_list_model.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)

    def _clear_component_fields(self):
        self.ui.txt_device_heat_flow.setEnabled(False); self.ui.txt_device_heat_flow.setText("")
        self.ui.txt_devAttchThickness.setEnabled(False); self.ui.txt_devAttchThickness.setText("")
        self.ui.txt_bondwire_count.setEnabled(False); self.ui.txt_bondwire_count.setText("")
        self.ui.txt_bondwire_separation.setEnabled(False); self.ui.txt_bondwire_separation.setText("")

    def display_categ_items(self,dir):
        """Display library items inside library category

            Keyword Arguments:
            dir -- directory in which to find library items
        """
        sPath = self.categ_list_model.fileInfo(dir).absoluteFilePath()
        self.device_list_model.setRootPath(sPath)
        self.ui.lst_devices.setModel(self.device_list_model)
        self.ui.lst_devices.setRootIndex(self.device_list_model.setRootPath(sPath))
        self.device_list_model.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self._clear_component_fields()
        self.ui.lst_devices_att.setEnabled(False)
        self.ui.lst_devices_att.setModel(None)

        categ = self.categ_list_model.fileName(self.ui.lst_categories.selectedIndexes()[0])
        if categ == 'Device':
            self.ui.lst_devices_att.setEnabled(True)
            self.ui.lst_devices_att.setModel(self.attach_list_model)
            die_attach_path = os.path.join(self.project.tech_lib_dir, "Die_Attaches")
            self.ui.lst_devices_att.setRootIndex(self.attach_list_model.setRootPath(die_attach_path))
            self.ui.txt_devAttchThickness.setEnabled(True)
            self.ui.txt_device_heat_flow.setEnabled(True)
        elif categ == 'Bond Wire':
            self.ui.txt_bondwire_count.setEnabled(True)
            self.ui.txt_bondwire_separation.setEnabled(True)

    def add_device_error_check(self):
        error = False
        categ = self.ui.lst_categories.selectedIndexes()

        if categ == []:
            error = True
            QtGui.QMessageBox.warning(self, "Add Component", "No category selected")
        else:
            item = self.ui.lst_devices.selectionModel().selectedIndexes()
            if item == []:
                error = True
                QtGui.QMessageBox.warning(self, "Add Component", "Nothing selected to add")
            else:
                categ_name = self.categ_list_model.fileName(categ[0])
                if categ_name == 'Device':
                    if self.ui.lst_devices_att.selectionModel().selectedIndexes() == []:
                        error = True
                        QtGui.QMessageBox.warning(self, "Add Component", "No Attach Material selected for device")
                    if self._check_device_fields():
                        error = True
                elif categ_name == 'Bond Wire':
                    if len(self.ui.txt_bondwire_count.text()) > 0:
                        if self._check_bondwire_fields():
                            error = True

        return error

    def _check_device_fields(self):
        error1 = self._check_field(self.ui.txt_devAttchThickness, float, "Component", "Must enter a numeric value for Attach Thickness")
        error2 = self._check_field(self.ui.txt_device_heat_flow, float, "Component", "Must enter a numeric value for Device Heat Flow")
        return error1 or error2

    def _check_bondwire_fields(self):
        error1 = self._check_field(self.ui.txt_bondwire_count, int, "Component", "Must enter an integer value for Number of Wires")
        error2 = self._check_field(self.ui.txt_bondwire_separation, float, "Component", "Must enter a numeric value for Wire Separation")
        return error1 or error2

    def _check_field(self, field, func, error_title, error_msg):
        try:
            func(field.text())
            return False
        except:
            QtGui.QMessageBox.warning(self, error_title, error_msg)
            return True
    def get_color_index(self):
        '''Quang: this method get the real color from the bar'''
        selected_row = self.ui.tbl_projDevices.currentRow()
        color= self.ui.tbl_projDevices.item(selected_row,0).background()
        color=color.color()
        return color
    def add_to_device_table(self):
        """Add device from lst_devices to tbl_projectDevices"""
        # make sure no errors
        if not self.add_device_error_check():
            item = self.ui.lst_devices.selectionModel().selectedIndexes()[0]
            if self.cw1 == len(self.color_wheel)-1:
                self.cw1 = 0
            else:
                self.cw1 += 1
            row_count = self.ui.tbl_projDevices.rowCount()
            print row_count
            self.ui.tbl_projDevices.insertRow(row_count)
            self.ui.tbl_projDevices.setItem(row_count,0,QtGui.QTableWidgetItem())
            self.ui.tbl_projDevices.item(row_count,0).setBackground(QtGui.QBrush(self.color_wheel[self.cw1-1]))
            self.ui.tbl_projDevices.setItem(row_count,1,QtGui.QTableWidgetItem())
            self.ui.tbl_projDevices.item(row_count,1).setText('  ' + item.model().data(item))

            # link to tech_lib obj
            try:
                categ = self.categ_list_model.fileName(self.ui.lst_categories.selectedIndexes()[0])
                tech_obj = load_file(self.device_list_model.rootPath() + '/' + item.model().data(item))
                if categ == 'Device':
                    item2 = self.ui.lst_devices_att.selectionModel().selectedIndexes()[0]
                    # Load attach tech lib object
                    attch_tech_obj = load_file(self.attach_list_model.rootPath() + '/' + item2.model().data(item2))
                    attch_thick = float(self.ui.txt_devAttchThickness.text())
                    thermal_model_choice=1
                    if thermal_model_choice==1:
                        heat_flow = float(self.ui.txt_device_heat_flow.text())
                    self.ui.tbl_projDevices.item(row_count,1).tech = DeviceInstance(attch_thick, heat_flow, tech_obj, attch_tech_obj)
                elif categ == 'Bond Wire':
                    if len(self.ui.txt_bondwire_count.text()) > 0:
                        num_wires = int(self.ui.txt_bondwire_count.text())
                        wire_sep = float(self.ui.txt_bondwire_separation.text())
                    else:
                        # Default values
                        num_wires = 1
                        wire_sep = 0.0
                    self.ui.tbl_projDevices.item(row_count,1).tech = tech_obj
                    self.ui.tbl_projDevices.item(row_count,1).num_wires = num_wires
                    self.ui.tbl_projDevices.item(row_count,1).wire_sep = wire_sep
                else:
                    self.ui.tbl_projDevices.item(row_count,1).tech = tech_obj
            except:
                QtGui.QMessageBox.warning(self, "Add Component", "Error: Technology not found in Technology Library")
                print traceback.print_exc()
            # clear selections
            self.ui.lst_devices.selectionModel().clear()
            self.ui.lst_devices_att.selectionModel().clear()
            self.ui.txt_device_heat_flow.setEnabled(False); self.ui.txt_device_heat_flow.setText("")
            self.ui.txt_devAttchThickness.setEnabled(False); self.ui.txt_devAttchThickness.setText("")
            self.ui.txt_bondwire_count.setEnabled(False); self.ui.txt_bondwire_count.setText("")
            self.ui.txt_bondwire_separation.setEnabled(False); self.ui.txt_bondwire_separation.setText("")

    def device_pick(self, event):
        """Pick event called when device selection symbolic layout is clicked"""
        # get technology from table
        try:
            selected_row = self.ui.tbl_projDevices.selectionModel().selectedIndexes()[0].row()
            row_item = self.ui.tbl_projDevices.item(selected_row,1)
            selected_tech = row_item.tech
        # only work with rectangles or circles depending on what technology is selected
            if (isinstance(event.artist, Rectangle) and isinstance(selected_tech, BondWire)) \
               or (isinstance(event.artist, Circle)\
               and (isinstance(selected_tech, DeviceInstance) or isinstance(selected_tech, Lead))):
                # get color from table
                color=self.get_color_index().getRgbF() #Quang
                color = (color[0],color[1],color[2],0.5)

                # Check if patch is already chosen and if it matches the current component selection, clear the object
                if event.artist in self.component_row_dict and self.component_row_dict[event.artist] == selected_row:
                        # set back to default color
                        self.component_row_dict[event.artist]=None
                        event.artist.set_facecolor(self.default_color)
                        # Reset layout object back to nothing
                        layout_obj = self.patch_dict.get_layout_obj(event.artist)
                        if isinstance(layout_obj.tech, BondWire):
                            layout_obj.wire = False
                            layout_obj.num_wires = None
                            layout_obj.wire_sep = None
                        layout_obj.tech = None
                else:
                    # color object
                    event.artist.set_facecolor(color)
                    self.component_row_dict[event.artist] = selected_row
                    # assign technology from table to object
                    layout_obj = self.patch_dict.get_layout_obj(event.artist)
                    layout_obj.tech = selected_tech

                    if isinstance(selected_tech, BondWire):
                        layout_obj.wire = True
                        layout_obj.num_wires = row_item.num_wires
                        layout_obj.wire_sep = row_item.wire_sep

                print self.patch_dict.get_layout_obj(event.artist).tech

                # redraw canvas
                self.symb_canvas[0].draw()
        except:
            QtGui.QMessageBox.warning(self, 'Error', 'Please Select Component on the Component Selection Tab')
    def component_pressed(self):
        """Enable relevant text fields for the selected component and display the previously entered values for that component."""
        selected_row = self.ui.tbl_projDevices.currentRow()
        row_item = self.ui.tbl_projDevices.item(selected_row, 1)
        self._clear_component_fields()

        if isinstance(row_item.tech, DeviceInstance):
            self.ui.txt_device_heat_flow.setEnabled(True);
            self.ui.txt_device_heat_flow.setText(str(row_item.tech.heat_flow))
            self.ui.txt_devAttchThickness.setEnabled(True);
            self.ui.txt_devAttchThickness.setText(str(row_item.tech.attach_thickness))
        elif isinstance(row_item.tech, BondWire):
            self.ui.txt_bondwire_count.setEnabled(True);
            self.ui.txt_bondwire_count.setText(str(row_item.num_wires))
            self.ui.txt_bondwire_separation.setEnabled(True);
            self.ui.txt_bondwire_separation.setText(str(row_item.wire_sep))

    def remove_component(self):
        selected_row = self.ui.tbl_projDevices.currentRow()
        print "selected row"
        print selected_row
        self.ui.tbl_projDevices.selectionModel().selectedIndexes()[0].row()
        # Remove from row from table
        self.ui.tbl_projDevices.removeRow(selected_row)

        # Clear and disable text fieldsdd
        self.ui.txt_device_heat_flow.setText("")
        self.ui.txt_device_heat_flow.setEnabled(False)
        self.ui.txt_devAttchThickness.setText("")
        self.ui.txt_devAttchThickness.setEnabled(False)
        self.ui.txt_bondwire_count.setText("")
        self.ui.txt_bondwire_count.setEnabled(False)
        self.ui.txt_bondwire_separation.setText("")
        self.ui.txt_bondwire_separation.setEnabled(False)

        # Remove colors from symbolic figure and reset layout object
        for patch_key in self.component_row_dict:
            if self.component_row_dict[patch_key] == selected_row:
                # Reset color
                patch_key.set_facecolor(self.default_color)
                # Reset layout object to nothing
                layout_obj = self.patch_dict.get_layout_obj(patch_key)
                if isinstance(layout_obj.tech, BondWire):
                        layout_obj.wire = False
                        layout_obj.num_wires = None
                        layout_obj.wire_sep = None
                layout_obj.tech = None

        # Redraw Canvas
        self.symb_canvas[self.LAYOUT_SELECTION_PLOT].draw()

    def modify_component(self):
        """Save updated device heat flow and attach thickness by reading in the current values from the text entered by the user."""
        selected_row = self.ui.tbl_projDevices.currentRow()
        row_item = self.ui.tbl_projDevices.item(selected_row, 1)
        if isinstance(row_item.tech, DeviceInstance):
            error = self._check_device_fields()
            if not error:
                row_item.tech.heat_flow = float(self.ui.txt_device_heat_flow.text())
                row_item.tech.attach_thickness = float(self.ui.txt_devAttchThickness.text())
        elif isinstance(row_item.tech, BondWire):
            error = self._check_bondwire_fields()
            if not error:
                row_item.num_wires = int(self.ui.txt_bondwire_count.text())
                row_item.wire_sep = float(self.ui.txt_bondwire_separation.text())

    def save_deviceTable(self):
        self.project.deviceTable = []
        for row in range(self.ui.tbl_projDevices.rowCount()):
            row_obj = self.ui.tbl_projDevices.item(row,1)
            component = [row_obj.text(), row_obj.tech]
            if isinstance(row_obj.tech, BondWire):
                component.append(row_obj.num_wires)
                component.append(row_obj.wire_sep)

            self.project.deviceTable.append(component)

    def load_deviceTable(self):
        # clear component table
        for row in xrange(self.ui.tbl_projDevices.rowCount()):
            self.ui.tbl_projDevices.removeRow(row)

        for row in self.project.deviceTable:
            if self.cw1 == len(self.color_wheel)-1:
                raise Exception('Component color wheel overflow!')
            self.cw1 += 1
            row_count = self.ui.tbl_projDevices.rowCount()
            self.ui.tbl_projDevices.insertRow(row_count)
            self.ui.tbl_projDevices.setItem(row_count,0,QtGui.QTableWidgetItem())
            self.ui.tbl_projDevices.item(row_count,0).setBackground(QtGui.QBrush(self.color_wheel[self.cw1-1]))
            self.ui.tbl_projDevices.setItem(row_count,1,QtGui.QTableWidgetItem())
            self.ui.tbl_projDevices.item(row_count,1).setText(row[0])
            self.ui.tbl_projDevices.item(row_count,1).tech = row[1]
            if isinstance(row[1], BondWire):
                self.ui.tbl_projDevices.item(row_count,1).num_wires = row[2]
                self.ui.tbl_projDevices.item(row_count,1).wire_sep = row[3]

            # Connect the drawing up
            col = self.color_wheel[self.cw1-1]
            color = col.getRgbF()
            color = (color[0],color[1],color[2],0.5)
            for patch in self.patch_dict:
                layout_obj = self.patch_dict.get_layout_obj(patch)
                if patch.window == 0:
                    match = False
                    if isinstance(layout_obj.tech, BondWire) and isinstance(row[1], BondWire):
                        # match tech, num_wires, wire_sep
                        if (layout_obj.tech.name == row[1].name) and \
                        (layout_obj.num_wires == row[2]) and \
                        (layout_obj.wire_sep == row[3]):
                            match = True
                    elif isinstance(layout_obj.tech, DeviceInstance) and isinstance(row[1], DeviceInstance):
                        # match device tech, attach tech, attach_thickness, heat_flow
                        if (layout_obj.tech.device_tech.name == row[1].device_tech.name) and \
                         (layout_obj.tech.attach_tech.properties.name == row[1].attach_tech.properties.name) and \
                         (layout_obj.tech.attach_thickness == row[1].attach_thickness) and \
                         (layout_obj.tech.heat_flow == row[1].heat_flow):
                            match = True
                    elif isinstance(layout_obj.tech, Lead) and isinstance(row[1], Lead):
                        # match tech
                        if (layout_obj.tech.name == row[1].name):
                            match = True

                    if match:
                        patch.set_facecolor(color)
                        self.component_row_dict[patch] = row_count

# ------------------------------------------------------------------------------------------
# ------ Constraint Creation ---------------------------------------------------------------

    def enter_constraint_page(self):
        self.clear_constraints()

    def clear_constraints(self):
        # De-selects and clear everything
        self.constraint_select = None
        self.ui.txt_fixedWidth.setText(''); self.ui.txt_fixedWidth.setStyleSheet("background-color:white")
        self.ui.txt_minWidth.setText(''); self.ui.txt_fixedWidth.setStyleSheet("background-color:white")
        self.ui.txt_maxWidth.setText(''); self.ui.txt_fixedWidth.setStyleSheet("background-color:white")

        # De-highlight everything
        children = self.symb_axis[self.CONSTRAINT_PLOT].get_children()
        for obj in children: 
            obj.set_alpha(0.25)
        self.symb_canvas[self.CONSTRAINT_PLOT].draw()

    def constraint_min_edit(self):
        # clear fixed textbox
        self.ui.txt_fixedWidth.setText('')
        self.ui.txt_fixedWidth.setStyleSheet("background-color:white")

        # make sure something is selected
        if self.constraint_select is None:
            self.ui.txt_minWidth.setText('')
            return

        # make sure its numeric
        if (not self.ui.txt_minWidth.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.constraint_error = True
            self.ui.txt_minWidth.setStyleSheet("background-color:pink")
            return
        else:
            self.ui.txt_minWidth.setStyleSheet("background-color:white")

        if self.patch_dict[self.constraint_select].constraint is None:
            # creating new constraint
            if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                    for obj in self.constraint_select.symmetry:
                        obj.constraint = (float(self.ui.txt_minWidth.text()),None,None)
            else:
                self.patch_dict[self.constraint_select].constraint = (float(self.ui.txt_minWidth.text()),None,None)
            self.constraint_error = True # because they haven't entered a maximum yet
            self.ui.txt_maxWidth.setStyleSheet("background-color:pink")
        else:
            # check against maxWidth
            if float(self.ui.txt_maxWidth.text()) > float(self.ui.txt_minWidth.text()):
                if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                    for obj in self.constraint_select.symmetry:
                        obj.constraint = (float(self.ui.txt_minWidth.text()),float(self.ui.txt_maxWidth.text()),None)
                else:
                    self.patch_dict[self.constraint_select].constraint = (float(self.ui.txt_minWidth.text()),float(self.ui.txt_maxWidth.text()),None)
                self.constraint_error = False
                self.ui.txt_minWidth.setStyleSheet("background-color:white")
                self.ui.txt_maxWidth.setStyleSheet("background-color:white")
            else:
                if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                    for obj in self.constraint_select.symmetry:
                        obj.constraint = (float(self.ui.txt_minWidth.text()),None,None)
                else:
                    self.patch_dict[self.constraint_select].constraint = (float(self.ui.txt_minWidth.text()),None,None)
                self.constraint_error = True
                self.ui.txt_minWidth.setStyleSheet("background-color:pink")

        #print self.patch_dict[self.constraint_select].constraint

    def constraint_max_edit(self):
        # clear fixed textbox
        self.ui.txt_fixedWidth.setText('')
        self.ui.txt_fixedWidth.setStyleSheet("background-color:white")

        # make sure something is selected
        if self.constraint_select is None:
            self.ui.txt_maxWidth.setText('')
            return
        else:
            self.ui.txt_maxWidth.setStyleSheet("background-color:white")

        # make sure its numeric
        if (not self.ui.txt_maxWidth.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.constraint_error = True
            self.ui.txt_maxWidth.setStyleSheet("background-color:pink")
            return

        if self.patch_dict[self.constraint_select].constraint is None:
            # creating new constraint
            if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                for obj in self.constraint_select.symmetry:
                    obj.constraint = (None,self.ui.txt_maxWidth.text(),None)
            else:
                self.patch_dict[self.constraint_select].constraint = (None,self.ui.txt_maxWidth.text(),None)
            self.constraint_error = True # because they haven't entered a minimun yet
            self.ui.txt_minWidth.setStyleSheet("background-color:pink")
        else:
            # check against minWidth
            if float(self.ui.txt_maxWidth.text()) > float(self.ui.txt_minWidth.text()):
                if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                    for obj in self.constraint_select.symmetry:
                        obj.constraint = (float(self.ui.txt_minWidth.text()),float(self.ui.txt_maxWidth.text()),None)
                else:
                    self.patch_dict[self.constraint_select].constraint = (float(self.ui.txt_minWidth.text()),float(self.ui.txt_maxWidth.text()),None)
                self.constraint_error = False
                self.ui.txt_minWidth.setStyleSheet("background-color:white")
                self.ui.txt_maxWidth.setStyleSheet("background-color:white")
            else:

                if self.constraint_select.symmetry is not None: # apply to everything in symmetry
                    for obj in self.constraint_select.symmetry:
                        obj.constraint = (None,self.ui.txt_maxWidth.text(),None)
                else:
                    self.patch_dict[self.constraint_select].constraint = (None,self.ui.txt_maxWidth.text(),None)
                self.constraint_error = True
                self.ui.txt_maxWidth.setStyleSheet("background-color:pink")

        #print self.patch_dict[self.constraint_select].constraint

    def constraint_fixed_edit(self):
        # clear min and max textboxes
        self.ui.txt_minWidth.setText('')
        self.ui.txt_minWidth.setStyleSheet("background-color:white")
        self.ui.txt_maxWidth.setText('')
        self.ui.txt_maxWidth.setStyleSheet("background-color:white")

        # make sure something is selected
        if self.constraint_select is None:
            self.ui.txt_fixedWidth.setText('')
            return

        # make sure its numeric
        if (not self.ui.txt_fixedWidth.text().replace(".", "", 1).replace("e", "", 1).isdigit()):
            self.constraint_error = True
            self.ui.txt_fixedWidth.setStyleSheet("background-color:pink")
            return
        else:
            self.ui.txt_fixedWidth.setStyleSheet("background-color:white")

        # add constraint
        if self.constraint_select.symmetry is not None: # apply to everything in symmetry
            for obj in self.constraint_select.symmetry:
                obj.constraint = (None, None, float(self.ui.txt_fixedWidth.text()),1.2)
        else:
            self.patch_dict[self.constraint_select].constraint = (None, None, float(self.ui.txt_fixedWidth.text()),1.2)
        self.constraint_error = False

        #print self.patch_dict[self.constraint_select]
        #print self.patch_dict[self.constraint_select].constraint

    def constraint_pick(self, event):
        """Pick event called when constraint creation symbolic layout is clicked"""
        # dehighlight everything
        children = self.symb_axis[2].get_children()
        for obj in children:
            try:
                obj.set_alpha(0.25)
            except:
                print traceback.print_exc()

        # highlight everything in symmetry group
        if event.artist.symmetry is not None:
            for obj in event.artist.symmetry:
                self.patch_dict.get_patch(obj, 2).set_alpha(0.5)
        else:
            event.artist.set_alpha(0.5)
        self.symb_canvas[2].draw()

        # clear constraints
        for text in [self.ui.txt_minWidth,self.ui.txt_maxWidth,self.ui.txt_fixedWidth]:
            text.setText('')

        # display constraints
        if self.patch_dict.get_layout_obj(event.artist).constraint is not None:
            if self.patch_dict.get_layout_obj(event.artist).constraint[0] is not None:
                self.ui.txt_minWidth.setText(str(self.patch_dict.get_layout_obj(event.artist).constraint[0]))
            if self.patch_dict.get_layout_obj(event.artist).constraint[1] is not None:
                self.ui.txt_maxWidth.setText(str(self.patch_dict.get_layout_obj(event.artist).constraint[1]))
            if self.patch_dict.get_layout_obj(event.artist).constraint[2] is not None:
                self.ui.txt_fixedWidth.setText(str(self.patch_dict.get_layout_obj(event.artist).constraint[2]))

        # link to text boxes
        self.constraint_select = event.artist

    def constraint_remove(self):
        if self.constraint_select is not None:
            # Check if in symmetry group
            if self.constraint_select.symmetry is not None:
                for obj in self.constraint_select.symmetry:
                    obj.constraint = None # remove all constraints in symmetry group
            else:
                self.patch_dict.get_layout_obj(self.constraint_select).constraint = None
            self.clear_constraints()
        else:
            print 'Nothing selected.'

# ------------------------------------------------------------------------------------------
# ------ Results ---------------------------------------------------------------------------

    def start_optimization(self):
        run_optimization = True
        # check if saved solutions already exist
        # Quang And then ask user to save_as project to a different directory
        if len(self.project.solutions) > 0:
            reply = QtGui.QMessageBox.question(self, "Data Loss Warning",
                                             "Warning: Previously saved solution data will be lost if new optimization is run! Please save the previous data in a different file !",
                                             QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
            if reply==QtGui.QMessageBox.Ok:  # if the user hit 'Ok', save the project in new place and run the optimization.
                self.save_project_as()
                run_optimization = True
            else:
                run_optimization = False

        # create module stack
        if not self.build_module_stack():
            QtGui.QMessageBox.warning(self, "Module Stack Error", "One or more settings on the module stack page have an error.")
            run_optimization = False

        if run_optimization:
            self.ui.btn_runSim.setEnabled(False)
            # clear out saved project solutions
            self.clear_saved_solutions_ui()
            self.project.solutions = []

            if self.project.module_data.design_rules is None:
                QtGui.QMessageBox.warning(self, "Input Error", "Process design rules not configured. Using defaults.")
                self.project.module_data.design_rules = ProcessDesignRules(1.2, 1.2, 0.2, 0.1, 1.0, 0.2, 0.2, 0.2)
            
            try:
                self.project.num_gen = int(self.ui.txt_numGenerations.text())
            except:
                QtGui.QMessageBox.warning(self, "Input Error", "Number of generations must be a number! Defaulting to 100.")
                self.project.num_gen = 100
                self.ui.txt_numGenerations.setText(str(self.project.num_gen))
                print traceback.print_exc()
            '''QL'''
            new_seed=int(time.time()) #load a new seed
            #fixedseed=1
            #iseed=fixedseed
            iseed=new_seed           
            '''QL'''
            
            try:
                print "Starting Optimization"
                starttime = time.time()
                print "proj_builder.py > start_optimization() > TEMP_DIR=", self.TEMP_DIR
                self.project.symb_layout.form_design_problem(self.project.module_data, self.TEMP_DIR)
                print "project.symb_layout.form_design_problem() completed."
                self.project.symb_layout.err_report={}
                self.project.symb_layout.optimize(iseed,inum_gen = self.project.num_gen, progress_fn=self.update_opt_progress_bar)
                print 'Optimization Complete'
                print 'seed is : ', iseed
                print self.project.symb_layout.err_report
                print 'Runtime:',time.time()-starttime,'seconds.'
                print 'Opening Solution Browser...'                
                self.update_opt_progress_bar(100)
                self.project.symb_layout.opt_progress_fn = None
                self.sol_browser = GrapheneWindow(self)
                self.sol_browser.show()
                self.update_opt_progress_bar(0)
            except:
                self.update_opt_progress_bar(0)
                QtGui.QMessageBox.warning(self, "Optimization Error", "Failed to complete optimization process. Please check console/log.")
                print traceback.print_exc()
                
        self.ui.btn_runSim.setEnabled(True)
        
        # Save out newly generated solution set and then (export data to csv)--> runs when btn clicked in graphing_form.py
        #new_solution_set = self.sol_browser.solution_library.measure_data
        #new_names_units = self.sol_browser.solution_library.measure_names_units
        #py_csv(self.sol_browser.solution_library.measure_data, self.sol_browser.solution_library.measure_names_units, "no_btn01.csv")
                
    def update_opt_progress_bar(self, val):
        print val, '%'
        self.ui.prgbar_optimize.setValue(int(val))
        
    def open_sol_browser(self):
        if len(self.project.solutions) > 0:
            reopen = False
            if self.sol_browser is not None:
                if not self.sol_browser.isVisible():
                    # the browser window has just been closed
                    reopen = True
            else:
                # solutions exist, but the browser window isn't open
                reopen = True
                
            if reopen:
                del self.sol_browser # clear any old data out
                self.sol_browser = GrapheneWindow(self) # reopen the browser
                self.sol_browser.show()
        else:
            QtGui.QMessageBox.warning(self, "Solution Browser", "No solutions exist.")
        
    def add_solution(self, solution):
        # save solution in project
        self.project.add_solution(solution)
        self.add_to_solution_list(solution)
        
    def add_to_solution_list(self, solution):
        # add solution to solution list
        self.ui.sol = QtGui.QListWidgetItem(solution.name)
        self.ui.lst_solution.addItem(self.ui.sol)
        self.show_sol_doc(self.ui.sol)
        
    def show_sol_doc(self, item):
        # add mdi window for viewing
        sol = self.project.solutions[self.ui.lst_solution.row(item)]
        self.project.symb_layout.gen_solution_layout(sol.index)
        m = SolutionWindow(sol, self.project.symb_layout)
        self.ui.mdiArea.addSubWindow(m)
        m.show()
        
        '''
        # create hspice export netlist (test)
        from powercad.spice_export.netlist_graph import Module_SPICE_netlist_graph
        from powercad.spice_export.hspice_interface import write_SPICE_netlist
        from powercad.spice_export.simulations import TransientSimulation
        
        export_path = 'C:\Users\jhmain\Dropbox\Spice Import and Export files\spice export\R&D 100'
        
        spice_netlist_graph = Module_SPICE_netlist_graph('netlist_test', self.project.symb_layout, sol.index, template_graph=None)
        spice_netlist_graph.write_SPICE_subcircuit(export_path)

        #trans_sim = TransientSimulation('Trans Simulation 1', 'NL1', 'NL2', 'NL1', 'NL3')
        #netlist = write_SPICE_netlist(export_path,trans_sim, spice_netlist_graph)

        #spice_netlist_graph.run_hspice()
        #spice_netlist_graph.draw_HSPICE_output()
        
        print 'SPICE export path:', export_path
        print 'SPICE export complete.'
        '''
        
    def clear_saved_solutions_ui(self):
        # close windows in the mdi area
        self.ui.mdiArea.closeAllSubWindows()
        # remove solutions from list area
        self.ui.lst_solution.clear()
        
    def load_saved_solutions_list(self):
        self.clear_saved_solutions_ui()

        # loads the list of previously saved solutions into the list display
        for sol in self.project.solutions:
            self.add_to_solution_list(sol)
            
        # display the number of generations ran in the last optimization run here
        self.ui.txt_numGenerations.setText(str(self.project.num_gen))
        
    
# ------------------------------------------------------------------------------------------        
# ------ Menu Bar --------------------------------------------------------------------------       
        
    def save_project(self):
        if self.ui.navigation.isEnabled():
            try:
                self.save_moduleStack()
                self.save_deviceTable()
                
                # make project directory
                save_path = os.path.join(self.project.directory, str(self.project.name))
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                
                # Make temporary copy of existing project file, if it exists
                if os.path.exists(os.path.join(save_path, "project.p")):
                    shutil.copy(os.path.join(save_path, "project.p"), os.path.join(save_path, "project.p.temp"))
                # Attempt to pickle the project
                self.project.symb_layout.prepare_for_pickle() # prepare the symbolic layout object for pickling
                save_file(self.project,os.path.join(save_path, "project.p"))
                QtGui.QMessageBox.about(self,"Project Saved","Project Saved")
                self.project.directory = save_path
                self.layout_script_dir=save_path
            except:
                # Replace the original copy
                if os.path.exists(os.path.join(save_path, "project.p.temp")):
                    os.remove(os.path.join(save_path, "project.p"))
                    shutil.copy(os.path.join(save_path, "project.p.temp"), os.path.join(save_path, "project.p"))
                
                QtGui.QMessageBox.warning(self, "Project Save Failed", "Your project was not saved! Please check console/log for details.")
                print traceback.format_exc()
            
    def save_project_as(self):
        if self.ui.navigation.isEnabled():
            # get new project name
            save_path = QtGui.QFileDialog.getExistingDirectory()
            '''
            proj_name, ok = QtGui.QInputDialog.getText(self, "Save Project As...", "New Project Name:")
            if len(proj_name) > 0 and ok:
                self.project.name = proj_name
            else:
                return
            '''
            try:
                self.save_moduleStack()
                self.save_deviceTable()
                #save_path = os.path.join(self.project.directory, str(self.project.name))
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                
                # Make temporary copy of existing project file, if it exists
                if os.path.exists(os.path.join(save_path, "project.p")):
                    shutil.copy(os.path.join(save_path, "project.p"), os.path.join(save_path, "project.p.temp"))
                
                # Attempt to pickle the project
                self.project.symb_layout.prepare_for_pickle() # prepare the symbolic layout object for pickling
                save_file(self.project,os.path.join(save_path, "project.p"))
                QtGui.QMessageBox.about(self,"Project Saved","Project Saved")
                self.project.directory=save_path
                self.layout_script_dir = save_path
            except:
                # Replace the original copy
                if os.path.exists(os.path.join(save_path, "project.p.temp")):
                    os.remove(os.path.join(save_path, "project.p"))
                    shutil.copy(os.path.join(save_path, "project.p.temp"), os.path.join(save_path, "project.p"))
                
                QtGui.QMessageBox.warning(self, "Project Save Failed", "Your project was not saved! Please check console/log for details.")
                print traceback.format_exc()
                
    def load_symbolic_layout(self):
        QtGui.QMessageBox.warning(self, "Load Symbolic Layout", "Not implemented yet.")
        if self.ui.navigation.isEnabled():
            symbolic_file = QFileDialog.getOpenFileName(self, "Select Symbolic Layout", self.project.directory, "SVG Files (*.svg)", "SVG Files (*.svg)")

class PatchDictionary(dict):
    def __init__(self):
        dict.__init__(self)

    def get_patch(self, layout_obj, window):
        patches = [patch[0] for patch in self.items() if (patch[1] == layout_obj and patch[0].window == window)]
        return patches[0]
    
    def get_layout_obj(self, patch):
        return self[patch]

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main_window = ProjectBuilder()
    main_window.show()
    sys.exit(app.exec_())
    
# --------------- Bugs found/ To do --------------------
# 
# - Optimization progress bar (graphic) pauses even though optimization is in progress (as seen on console). This is especially true for large number of generations.
# 
# - "Open Solution Browser" button needs to be disabled while solution browser is already open, and vice versa. 

        