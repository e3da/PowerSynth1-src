'''
Created on Jun 27, 2012

@author: bxs003
'''

# To Do:
# - Support devices/leads on supertraces
# - Support Supertrace Supertrace contact
# - Support Bondwires from device to supertrace
# - Devices need to be constrained to the correct topological space
# - Fixed Lead positions
# - Check device types have proper amount of connections (transitor->signal,power) (diode->power)
# - Bug: If two horz. traces are abutted, and two vert. traces are above and below,
#       the vertical piece on the bottom has some strange issues

# Supertrace future work:
# - 3 options for devices on supertrace:
#     *1. 2DOF; 2. Vert. Constrained; 3. Horz. Constrained
#     *Default to Vert. Constrained
# - Bondwire interaction:
#     *if bondwire is horizontal (treat supertrace as vertical)
#     *if bondwire is vertical (treat st as horiz.)
# - Need to handle supertrace connecting to supertrace
#     * this will involve writing/changing code in both layout generation and parasitic extraction

# Future work notes:
# Work the concept of supertraces into the program better (more elegantly)
# Remove the use of dictionaries in the design variable formulation process
# Break up the SymbolicLayout class into smaller class extensions (inheritance)
# Remove the use of isinstance in determining SymPoints vs. SymLines, etc. (replace with homogeneous object lists)

import math
import time
from copy import copy, deepcopy
import random
import pickle
import inspect
import os

import networkx as nx
import numpy as np
from numpy.linalg.linalg import LinAlgError

from powercad.util import Rect, complex_rot_vec, get_overlap_interval, distance
from powercad.sym_layout.svg import load_svg, normalize_layout, check_for_overlap,load_script
from powercad.sym_layout.svg import LayoutLine, LayoutPoint
from powercad.design.module_data import gen_test_module_data
from powercad.design.library_structures import Lead, BondWire,Device
from powercad.design.project_structures import DeviceInstance
from powercad.opt.optimizer import NSGAII_Optimizer, DesignVar
from powercad.parasitics.analysis import parasitic_analysis
from powercad.parasitics.models_bk import trace_inductance, trace_resistance, trace_capacitance
#Testing
from powercad.parasitics.mdl_compare import trace_cap_krige,trace_ind_krige,trace_res_krige,load_mdl
from powercad.parasitics.models import wire_inductance, wire_resistance
from powercad.thermal.analysis import perform_thermal_analysis, TFSM_MODEL, RECT_FLUX_MODEL
from powercad.sol_browser.solution_lib import SolutionLibrary
from powercad.thermal.elmer_characterize import characterize_devices
import powercad.settings as settings
from PySide import QtCore, QtGui
import ctypes

#Used in Pycharm only


def pause(flag):  # use this to force the profile in pycharm to add a function to the graph
    if flag:
        ctypes.windll.user32.MessageBoxA(0, "hit OK", "Add this to Graph",1)  # Open a Message Box to notify users about the error Ctypes


class LayoutError(Exception):
    def __init__(self, msg):
        ctypes.windll.user32.MessageBoxA(0, msg, "Layout Error", 1)  # Open a Message Box to notify users about the error Ctypes
        self.args = [msg]


class FormulationError(Exception):
    def __init__(self, msg):
        ctypes.windll.user32.MessageBoxA(0, msg, "Formulation Error", 1)    # Open a Message Box to notify users about the error Ctypes
        self.args = [msg]


class ThermalMeasure(object):
    FIND_MAX = 1
    FIND_AVG = 2
    FIND_STD_DEV = 3
    
    UNIT = ('K', 'Kelvin')
    
    def __init__(self, stat_fn, devices, name):
        """
        Thermal performance measure object
        
        Keyword Arguments:
        stat_fn -- takes on either FIND_MAX or FIND_AVG;
            FIND_MAX -> find maximum of device temperatures
            FIND_AVG -> find average of device temperatures
            FIND_STD_DEV -> find standard deviation of device temperatures
        devices -- list of SymPoint objects which represent devices
        name -- user given name to performance measure
        """
        self.stat_fn = stat_fn
        self.devices = devices
        self.name = name
        self.units = self.UNIT[0]

class ElectricalMeasure(object):
    MEASURE_RES = 1
    MEASURE_IND = 2
    MEASURE_CAP = 3
    
    UNIT_RES = ('mOhm', 'milliOhm')
    UNIT_IND = ('nH', 'nanoHenry')
    UNIT_CAP = ('pF', 'picoFarad')
    
    def __init__(self, pt1, pt2, measure, freq, name, lines=None, mdl='RS'):
        """
        Electrical parasitic measure object
        
        Keyword Arguments:
        pt1 -- SymPoint object which represents start of electrical path
        pt2 -- SymPoint object which represents end of electrical path
        lines -- list of SymLine objects which represent the traces which are to be measured for capacitance.
        measure -- id whether to measure resistance, inductance or capacitance
            MEASURE_RES -> measure resistance
            MEASURE_IND -> measure inductance
            MEASURE_CAP -> measure substrate capacitance of selected traces
        name -- user given name to performance measure
        mdl -- electrical model selection
        """
        self.pt1 = pt1
        self.pt2 = pt2
        self.lines = lines
        self.measure = measure
        self.name = name
        self.mdl=mdl
        if measure == self.MEASURE_RES:
            self.units = self.UNIT_RES[0]
        elif measure == self.MEASURE_IND:
            self.units = self.UNIT_IND[0]
        elif measure == self.MEASURE_CAP:
            self.units = self.UNIT_CAP[0]


class RowCol(object):
    def __init__(self):
        self.left = None
        self.mid = None
        self.right = None
        self.phantom = None
        self.dv_index = None
        self.elements = {}
        self.definable = None
        self.removed = None
        self.all_super = False
        # Phantoms only
        self.phantom_constraint = None


class SymLine(object):
    def __init__(self, line, raw_line):
        self.raw_element = raw_line
        self.element = line
        self.wire = False
        self.tech = None # holds a reference to Bondwire object
         
        # Traces only
        self.trace_line = None
        self.constraint = None # (min, max, fixed) either (min and max) or fixed
        self.trace_rect = None
        self.child_pts = None
        self.conn_bonds = []
        self.dv_index = None
        self.trace_connections = []
        self.super_connections = [] # ((v supertrace, h supertrace, vert_range, horz_range), conn_type)
        
        # Super Traces (only single intersections supported)
        self.intersecting_trace = None # the supertrace's intersecting partner (None if not supertrace)
        self.has_rect = True           # Identifies whether this supertrace carries the full trace rect
        self.normal_connections = []   # (trace, conn_type)
        self.long_contacts = {}        # key:trace, value:side
        
        # Bondwires only
        self.device = None      # device in which wire is connected to
        self.dev_pt = None      # 1 or 2 -- which end is connected to device
        self.trace = None       # trace that wire is connected to
        self.trace2 = None      # 2nd trace that wire is connected to
        self.start_pts = None   # Bondwire points starting from device
        self.end_pts = None     # Bondwire points ending on trace
        # Note: land_pt is always the starting point and land_pt2 is always the ending point in trace to trace connections
        self.land_pt = None     # A midpoint of the bondwire group landing position used for PEX
        self.land_pt2 = None    # A second midpoint of the bondwire group landing position used for PEX
        self.start_pt_conn = None # points to the trace object in which start_pts are connected to
        self.end_pt_conn = None # points to the trace object in which end_pts are connected to
        self.num_wires = None   # Number of wires in the trace to trace bondwire
        self.wire_sep = None    # Separation between wires in trace to trace bondwire
        
    def reset_to_pre_analysis(self):
        self.trace_line = None
        self.trace_rect = None
        self.child_pts = None
        self.conn_bonds = []
        self.dv_index = None
        self.trace_connections = []
        self.super_connections = []
        self.intersecting_trace = None
        self.has_rect = True
        self.normal_connections = []
        self.long_contacts = {}
        self.device = None
        self.dev_pt = None
        self.trace = None
        self.start_pts = None
        self.end_pts = None
        self.land_pt = None
        self.land_pt2 = None
        self.start_pt_conn = None
        self.end_pt_conn = None
        
    def make_bondwire(self, bw_tech):
        self.wire = True
        self.tech = bw_tech
        
    def make_trace(self):
        self.wire = False
        self.tech = None
        
    def is_supertrace(self):
        return (self.intersecting_trace is not None)
        
    def __str__(self):
        if self.wire:
            return 'bw'
        else:
            if self.is_supertrace():return 'super'
            else: return 'trace'


class SymPoint(object):
    def __init__(self, point, raw_point):
        self.raw_element = raw_point
        self.element = point
        
        self.tech = None # holds a reference to either a DeviceInstance or Lead object
        self.constraint = None # (min, max, fixed) either (min and max) or fixed
        
        self.parent_line = None
        self.dv_index = None
        self.center_position = None
        self.footprint_rect = None
        self.orientation = None # 1:Top,2:Bottom,3:Right,4:Left (up vector)
        self.sym_bondwires = []
        self.lumped_node = None
        
    def reset_to_pre_analysis(self):
        self.parent_line = None
        self.dv_index = None
        self.center_position = None
        self.footprint_rect = None
        self.orientation = None
        self.sym_bondwires = []
        self.lumped_node = None
        
    def is_device(self):
        return isinstance(self.tech, DeviceInstance)
    
    def is_lead(self):
        return isinstance(self.tech, Lead)
        
    def __str__(self):
        if self.is_device():
            return 'Device'
        elif self.is_lead():
            return 'Lead'


'''------------------------------------------------------------------------------------------------------------------'''


class SymbolicLayout(object):
    HORZ_DV = 1
    VERT_DV = 2
    DEV_DV = 3
    BONDWIRE_DV = 4

    def __init__(self):
        self.design_rules = None
        self.sub_dim = None
        self.gap = None
        
        self.all_sym = None # List of all SymLines and SymPoints
        self.points = None # List of all SymPoint objects
        
        self.layout = None # List of all LayoutLines and LayoutPoints (from svg.py)
        self.xlen = None # Length of normalized layout (on x axis)
        self.ylen = None # Length of normalized layout (on y axis)
        
        self.all_super_traces = None
        self.all_trace_lines = None # list of all trace type SymLines
        self.trace_layout = None
        self.trace_xlen = None
        self.trace_ylen = None
        self.vg_matrix = None
        self.trace_rects = None # All trace rectangles in a layout
        
        self.symbol_graph = None # NetworkX graph of layout topology (built at form_design_problem)
        self.trace_graph = None # NetworkX graph of trace connections
        self.trace_graph_components = None
        self.lumped_graph = None # Lumped element graph of extracted layout
        
        # trace_trace_connections is a unique set of all regular trace connections in a layout
        self.trace_trace_connections = None # List of tuples (trace1, trace2, conn_type) conn_type: 1-ortho, 2-parallel
        # self.trace_super_connections = None
        self.boundary_connections = None # Trace to Trace connections made at the boundary of a supertrace
        
        self.symmetries = []
        self.fixed_constraints = None # equality constraints
        self.tol_constraints = None # inequality constraints
        
        self.h_rowcol_list = None
        self.h_dv_list = None
        self.removed_horiz_dv_index = None
        self.h_design_var_dict = None
        
        self.v_rowcol_list = None
        self.v_dv_list = None
        self.removed_vert_dv_index = None
        self.v_design_var_dict = None
        
        self.devices = None
        self.dev_dv_list = None
        self.leads = None
        self.bondwires = None
        self.bondwire_dv_list = None
        
        self.h_design_values = None       # control trace's horizontal value
        self.v_design_values = None       # control trace's vertical value
        self.dev_design_values = None
        self.bondwire_design_values = None
        
        self.h_overflow = None
        self.v_overflow = None
        self.h_min_max_overflow = None
        self.v_min_max_overflow = None
        
        self.layout_ready = False
        
        # Performance Measures
        self.perf_measures = []
        
        # Optimization
        self.opt_to_sym_index = None
        self.opt_dv_list = None
        self.opt_progress_fn = None # function to control optimization progress bar in GUI
        
        # Types
        self.SymLine = SymLine
        self.SymPoint = SymPoint
        
        #analysis added by Quang
        self.algorithm= None # algorithm for optimizer
        self.seed=None
        self.ctest=0 # testing number of drc check
        self.err_report={} # a list of report for drc_check function
        self.mode=7

        # Testing
        self.trace_info = [] # used to save all width and length for evaluation
        self.trace_nodes = [] # all nodes that will be used to connect traces to lumped_graph
        self.mdl_dir = 'D:\Testing\Py_Q3D_test\All rs models'
        self.mdl_type='MS'
        self.LAC_mdl=load_mdl(self.mdl_dir,'LAC_mesh_100_krige.rsmdl')
        self.RAC_mdl = load_mdl(self.mdl_dir, 'RAC_mesh_100_krige.rsmdl')
        self.C_mdl = load_mdl(self.mdl_dir,'C_mesh_100_krige.rsmdl')

    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''        
    def add_constraints(self):
        ''' Adds a contraints field to any layout object which lacks it. '''
        for sym in self.all_sym:
            if not hasattr(sym, 'constraint'):
                sym.constraint = None

    def load_layout(self, path,mode):
        self.__init__()                   # Invalidate old data
        if mode =='svg':                  # if the sym_layout is from a svg file 
            self.layout = load_svg(path)  # using load svg method  
        elif mode =='script':             # in case this is a script
            self.layout=load_script(path) # using the load script method     
        self.raw_layout = deepcopy(self.layout) # raw_layout is the list of LayoutLine and LayoutPoint definded by SVG or script
        self.xlen, self.ylen = normalize_layout(self.layout, 0.01) # using normalizae method to get the normalize layout
        check_for_overlap(self.layout)          # check for overlapping in this layout  
        
        # Create SymLines and SymPoints
        self.all_sym = []
        self.points = []
        
        for i in xrange(len(self.layout)): # iterate through the layout 
            obj = self.layout[i]           # for each object in the layout add the normalized obj to obj list
            raw = self.raw_layout[i]       # add the raw object to object list
            if isinstance(obj, LayoutLine):# if this is a LayoutLine then make a SymLine object 
                sym = SymLine(obj, raw)    # make a SymLine object
            elif isinstance(obj, LayoutPoint): # if this is a LayoutPoint then make a SymPoint object
                sym = SymPoint(obj, raw)   # make a SymPoint object
                self.points.append(sym)    # append this to the points list 
            self.all_sym.append(sym)       # append the sym obj to all_sym list
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''                            
    def form_design_problem(self, module, temp_dir=settings.TEMP_DIR): 
        """ Formulate and check the design problem before optimization.
        Keyword Arguments:
        module: A powercad.sym_layout.module_data.ModuleData object 
        temp_dir: A path to a temp. dir. for doing thermal characterizations (must be absolute)
        """
        #pause(True)  # add to graph
        self.module = module                       # this object include user inputs from PowerSynth interface e.g: frequency, materials...
        self.design_rules = module.design_rules    # design_rules from user interface->Project->Design Rules Editor
        self.module.check_data()                   # check if the input is not None.. go to powercad->design->module_data for more info      
        self.temp_dir = temp_dir                   # temp_dir where the characterization thermal files will be stored
        print "symbolic_layout.py > form_design_problem() > temp_dir=", self.temp_dir    
        
        ledge_width = module.substrate.ledge_width # collect module data information... go to powercad->design->module_data->project_structures to learn ab this
        self.sub_dim = (module.substrate.dimensions[0]-2*ledge_width, module.substrate.dimensions[1]-2*ledge_width) # This is the dimension of the top metal layer (before tracing)
        
        self.gap = self.design_rules.min_trace_trace_width   # minimum gap between two traces   
        # Make sure data structures are reset
        for symbol in self.all_sym:                          # going through all the symbolic lines and points to reset it
            symbol.reset_to_pre_analysis()
            
        self._check_formulation()                  # check formulation if there is errors, notify users with message box > go to this method to read more
        self._build_trace_layout()                 # Go through only traces and collect SymLine to a list object
        self._find_trace_connections()             # Search in the list of traces built above to create a connection list  >go to this method to read more    
        self._build_virtual_grid_matrix()          # go to this method to read more
        
        self._find_parent_lines()                                # build up connections between lines and points > go to this method to read more
        self.dev_dv_list = self._get_device_design_vars()        # go to this method to read more
        self.bondwire_dv_list = self._get_bondwire_design_vars() # go to this method to read more
        self._get_trace_design_vars()                            # go to this method to read more 
        
        self._build_symbol_graph()
        self._build_trace_graph()                                # go to this method to read more
        
        # Pre-initialize the design value lists (so there are spots to drop numbers into)
        self.h_design_values = [None]*len(self.h_dv_list)
        self.v_design_values = [None]*len(self.v_dv_list)
        self.dev_design_values = [None]*len(self.dev_dv_list)
        self.bondwire_design_values = [None]*len(self.bondwire_dv_list)
        
        # Check Device Thermal Characterizations (checks for cached characterizations)
        dev_char_dict, sub_tf = characterize_devices(self, temp_dir) 
        self.module.sublayers_thermal = sub_tf
        for dev in self.devices:
            dev.tech.thermal_features = dev_char_dict[dev.tech]
        
    def _check_formulation(self):
        #pause(True)                        # add to graph
        # Every layout point should have a techlib object bound to it (devices, leads)
        for sym in self.all_sym:           # go through all points and lines-> if there is no tech lib bound to a single point report the problem
            if isinstance(sym, SymPoint):   
                if sym.tech is None:
                    raise FormulationError('A layout point element has not been identified!')
        # Check over design rules and sub_dims, gap_width, etc. to make sure everything looks valid
        # Check number of performance objectives (should be greater than zero)
        if len(self.perf_measures) < 1:    # in case the user forget to insert performance measure notify them to do so             
            raise FormulationError('At least one performance measure needs to be identified for layout optimization! Please go to "Design Performance Identification" tab')
        elif len(self.perf_measures) == 1: # if single objective, make a copy of the single objective so NSGA-II can work
            self.perf_measures.append(self.perf_measures[0])

    def _build_trace_layout(self):
        #pause(True)  # add to graph
        # This method will collect the symline object from the user interface and store them in lists..  
        # Collect SymLine objects only
        self.trace_layout = []                                      # A list of LayoutLine object (of Traces only)
        self.all_trace_lines = []                                   # A list of SymLine object (of Traces only)
        
        # Constraints
        self.fixed_constraints = []                                 # a list to sort out objects with fixed constraints
        self.tol_constraints = []                                   # a list to sort out objects with tolerance constraints
        
        for sym in self.all_sym: #sym is a SymLine or SymPoint object (as opposed to LayoutLine/LayoutPoint object)
            ele = sym.element                                       # take the element object from symbolic object
            if isinstance(ele, LayoutLine) and (not sym.wire):      # distinguish between different SymLine object which include bondwire and traces
                trace_line = copy(sym.element)                      # copy the LayoutLine element
                sym.trace_line = trace_line
                self.trace_layout.append(trace_line)                # save the LayoutLine in a list    
                self.all_trace_lines.append(sym)                    # save the symLine object including LayoutLine in a list
                
                # Make new rectangle object
                sym.trace_rect = Rect()
                # Store which elements have constraints
                if sym.constraint is not None:                      # check if there are any constraints
                    if sym.constraint[2] is not None:               # check if fixed constraint is not none
                        self.fixed_constraints.append(sym)          # append the symline object with fixed constraint to list 
                    else:
                        self.tol_constraints.append(sym)            # append the symline object with tolerance constraint to list
            
        # Normalize the layout
        self.trace_xlen, self.trace_ylen = normalize_layout(self.trace_layout, 0.01) # Read the SVG and count number of Line object on X and Y dimension.
        
    def _find_trace_connections(self):
        """
        The connections of the trace objects need to be identified,
        now that bond wires have been identified by the user.
        """
        #pause(True)  # add to graph
        self.tmp_conn_dict = {}                                     # temp dict to filter out duplicated connections
        self.trace_trace_connections = []                           # trace to trace connection list
        
        # Identify Supertraces first and basic trace connectivity
        self.all_super_traces = []                                  # Super traces list
        for trace1 in self.all_trace_lines:                         # search a trace in all_trace_line  created in _build_trace_layout
            for trace2 in self.all_trace_lines:                     # search a trace in all_trace_line  created in _build_trace_layout
                if trace1 is not trace2:                            # make sure the 2 traces above can form a pair
                    vv = (trace1.element.vertical and trace2.element.vertical)         # both traces are vertical        
                    hh = (not trace1.element.vertical and not trace2.element.vertical) # both traces are horizontal
                    if trace1.element.vertical and (not trace2.element.vertical):      # in case they are orthogonal 
                        self._id_ortho_connections(trace1, trace2)                     # go to orthogonal connection analysis to read
                    elif vv or hh:                                                     # in case they are parallel (which might include adjacent case)
                        self._id_adjancent_connections(trace1, trace2)                 # go to adjacent connection analysis to read > Check this idea with shilpi
                    
        # Id normal trace to supertrace connections
        for supertrace in self.all_super_traces:
            for trace in self.all_trace_lines:
                if trace.intersecting_trace is None:
                    self._trace_supertrace_connection(trace, supertrace)
                   
        # Id supertrace to supertrace connections 
        for supertrace1 in self.all_super_traces:
            for supertrace2 in self.all_super_traces:
                if supertrace1 is not supertrace2:
                    self._supertrace_connection(supertrace1, supertrace2)
                    
        self._prune_trace_trace_connections() # remove supertraces from trace-trace connections list
        
        # Id normal trace connections at supertrace boundaries
        self._id_supertrace_boundary_connections()
        
        
    def _id_ortho_connections(self, trace1, trace2):
        obj1 = trace1.trace_line # vertical
        obj2 = trace2.trace_line # horizontal
        
        # Identify connected normal traces
        # Connections at right angle
        if obj1.pt1[0] >= obj2.pt1[0] and obj1.pt1[0] <= obj2.pt2[0] and \
           obj2.pt1[1] >= obj1.pt1[1] and obj2.pt1[1] <= obj1.pt2[1]:     #  Draw 2 traces and named them obj1 and obj2.. obj1 is vertical and should form a T or L shape with obj2.   
           # pt1 and pt2 are 2 points at 2 ends of the traces... Draw a X-Y axis and put this picture in you can imagine this condition 
            trace1.trace_connections.append(trace2)                       #  Set trace 1 trace_connections value equal trace 2
            trace2.trace_connections.append(trace1)                       #  Set trace 2 trace_connections value equal trace 1
            if not(frozenset([trace1, trace2]) in self.tmp_conn_dict):    #  check if these 2 are already added to a set or not
                # Append the connection to list
                self.tmp_conn_dict[frozenset([trace2, trace1])] = 1       # if not create a set for them this set type is 1 
                pt = self._intersection_pt(obj1, obj2)                    # Find the intersection point of 2 traces go to _intersection_pt to read more  
                self.trace_trace_connections.append([trace1, trace2, pt, False]) # add this connection group to the list
        # Identify Supertraces
        if obj1.pt1[0] > obj2.pt1[0] and obj1.pt1[0] < obj2.pt2[0] and \
           obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1]:       # in case of T shape (from the pic you drew above this is a super trace
            if trace1.is_supertrace() or trace2.is_supertrace():          
                raise LayoutError("Multiple intersection supertraces not supported! check for multiple T shapes on your layout")
            trace1.intersecting_trace = trace2                            #  Set trace 1 intersecting_trace value equal trace 2 > go to SymLine class to read more  
            trace2.intersecting_trace = trace1                            #  Set trace 2 intersecting_trace value equal trace 1 > go to SymLine class to read more
            # trace1 is vertical, trace2 is horizontal
            self.all_super_traces.append((trace1, trace2, (obj2.pt1[0],obj2.pt2[0]), (obj1.pt1[1],obj1.pt2[1])))  # append this group to supertrace list 
    
    def _intersection_pt(self, line1, line2):    # Find intersection point of 2 orthogonal traces
        x = 0                                    # initialize at 0
        y = 0                                    # initialize at 0
        if line1.vertical:                       # line 1 is vertical
            x = line1.pt1[0]                     # take the x value from line 1
        else:                                    # line 1 is horizontal
            y = line1.pt1[1]                     # take the y value from line 1
            
        if line2.vertical:                       # line2 is vertical
            x = line2.pt1[0]                     # take the x value from line 2 
        else:                                    # line 2 is horizontal 
            y = line2.pt1[1]                     # take the y value from line 2
            
        return x, y
            
    def _id_adjancent_connections(self, trace1, trace2):   # update tomorrow in changelog
        pt1 = trace1.trace_line.pt1
        pt2 = trace2.trace_line.pt2
        if (pt1[0] == pt2[0]) and (pt1[1] == pt2[1]):      # check if 2 sumline is connected
            trace1.trace_connections.append(trace2)        #  Set trace 1 trace_connections value equal trace 2
            trace2.trace_connections.append(trace1)        #  Set trace 2 trace_connections value equal trace 1
            if not(frozenset([trace1, trace2]) in self.tmp_conn_dict):
                self.tmp_conn_dict[frozenset([trace2, trace1])] = 2               # create a set for them this set type is 2
                self.trace_trace_connections.append([trace1, trace2, pt1, False]) # append the connection to trace connection list
        
    def _trace_supertrace_connection(self, trace, supertrace):
        # Figure what traces are contacting the supertraces
        # No end points should be inside a supertrace
        # Lines should be just contacting the outside of the supertrace
        # End point on boundary
        # Some midpoints along boundary
        # If a line is contacting the supertrace and endpoints more than
        # span the length of the supertrace -- it needs to be dealt with a bit differently
        
        # Should the connections be identified first?

        left,right = supertrace[2] # super trace X boundary
        bottom,top = supertrace[3] # super trace Y boundary
        pt1 = trace.trace_line.pt1
        pt2 = trace.trace_line.pt2
        
        pt1_contact = False
        pt2_contact = False
        long_contact = False
        long_pt = 0
        long_side = 0
        
        if pt1[0] >= left and pt1[0] <= right and pt1[1] >= bottom and pt1[1] <= top:
            if pt1[0] > left and pt1[0] < right and pt1[1] > bottom and pt1[1] < top:
                raise LayoutError("A trace is inside a supertrace!")
            else:
                pt1_contact = True
        
        if pt2[0] >= left and pt2[0] <= right and pt2[1] >= bottom and pt2[1] <= top:
            if pt2[0] > left and pt2[0] < right and pt2[1] > bottom and pt2[1] < top:
                raise LayoutError("A trace is inside a supertrace!")
            else:
                pt2_contact = True
                
        if pt1_contact is False and pt2_contact is False:
            if trace.element.vertical:
                if (supertrace[1].trace_line.pt1[0] == trace.trace_line.pt1[0] or \
                    supertrace[1].trace_line.pt2[0] == trace.trace_line.pt1[0]) and \
                   (supertrace[1].trace_line.pt1[1] > trace.trace_line.pt1[1] and \
                    supertrace[1].trace_line.pt1[1] < trace.trace_line.pt2[1]):
                    long_contact = True
                    if supertrace[1].trace_line.pt1[0] == trace.trace_line.pt1[0]:
                        long_pt = 1
                        long_side = Rect.LEFT_SIDE
                    else:
                        long_pt = 2
                        long_side = Rect.RIGHT_SIDE
            else:
                if (supertrace[0].trace_line.pt1[1] == trace.trace_line.pt1[1] or \
                    supertrace[0].trace_line.pt2[1] == trace.trace_line.pt1[1]) and \
                   (supertrace[0].trace_line.pt1[0] > trace.trace_line.pt1[0] and \
                    supertrace[0].trace_line.pt1[0] < trace.trace_line.pt2[0]):
                    long_contact = True
                    if supertrace[0].trace_line.pt1[1] == trace.trace_line.pt1[1]:
                        long_pt = 1
                        long_side = Rect.BOTTOM_SIDE
                    else:
                        long_pt = 2
                        long_side = Rect.TOP_SIDE
                
        # Contact Types
        # 1: Pt1 is contacting the supertrace
        # 2: Pt2 is contacting the supertrace
        # 3: Horizontal or Vertical 'long' contact with the supertrace at pt1
        # 4: Horizontal or Vertical 'long' contact with the supertrace at pt2
        # 5: Supertrace Supertrace contact
        if pt1_contact and pt2_contact:
            raise LayoutError("A trace is inside a supertrace!")
        elif pt1_contact:
            trace.super_connections.append((supertrace, 1))
            supertrace[0].normal_connections.append((trace, 1))
        elif pt2_contact:
            trace.super_connections.append((supertrace, 2))
            supertrace[0].normal_connections.append((trace, 2))
        elif long_contact:
            trace.super_connections.append((supertrace, long_pt+2))
            supertrace[0].normal_connections.append((trace, long_pt+2))
            supertrace[0].long_contacts[trace] = long_side
            
    def _supertrace_connection(self, supertrace1, supertrace2):
        left,right = supertrace1[2]
        bottom,top = supertrace1[3]
        rect1 = Rect(top, bottom, left, right)
        
        left,right = supertrace2[2]
        bottom,top = supertrace2[3]
        rect2 = Rect(top, bottom, left, right)
        
        inter = rect1.intersection(rect2)
        if inter is not None:
            # Check whether they are just contacted or internally intersecting
            if inter.area() > 0:
                raise LayoutError("Supertraces are intersecting, should only be contacting!")
            else:
                supertrace1[0].super_connections.append((supertrace2, 5))
                supertrace1[1].super_connections.append((supertrace2, 5))
                
    def _prune_trace_trace_connections(self):
        # Prune trace to trace connection list (remove supertrace connections)
        # The trace connection list (self.trace_trace_connections)
        # should only contain trace to trace connections
        rem_list = []
        for conn in self.trace_trace_connections:
            if conn[0].is_supertrace() or conn[1].is_supertrace():
                rem_list.append(conn)
        for rem in rem_list:
            self.trace_trace_connections.remove(rem)
                
    def _id_supertrace_boundary_connections(self):
        # Note: this identification process is for parasitic extraction purposes
        
        self.boundary_connections = {}
        # Normal trace connections internal to a supertrace
        # Could solve this problem by ignoring any connections
        # that are made at the boundary of the supertrace (thus internal)
        # Detect these connections and make the proper parasitic extraction paths
        # Next, find the real connection point between the trace and supertrace
        # Long contact type connections should be handled differently,
        # Connections are allowed along a long contact boundary of a supertrace
        for conn in self.trace_trace_connections:
            for st in self.all_super_traces:
                rect = Rect()
                rect.left, rect.right = st[2]
                rect.bottom, rect.top = st[3]
                if rect.encloses(conn[2][0], conn[2][1]):
                    # Determine if long contact: don't ignore
                    # boundary connections to long contacted traces
                    lc_bound = False
                    side = rect.find_pt_contact_side(conn[2])
                    for lc in st[0].long_contacts:
                        lc_side = st[0].long_contacts[lc]
                        if side[0] == lc_side or side[1] == lc_side:
                            lc_bound = True
                            
                    if not lc_bound:
                        conn[3] = True
                        self.boundary_connections[frozenset([conn[0], conn[1]])] = (1, st[0])
                        break
        
    def _build_virtual_grid_matrix(self):
        # build up virtual grid matrix
        # Each x,y location contains a dictionary of the elements (the keys) that exist
        # in that spot coupled with a value of whether the object is an endpoint (True) or midpoint (False)
        self.vg_matrix = []                # initialize virtual grid matrix
        for x in xrange(self.trace_xlen):  
            col = []
            for y in xrange(self.trace_ylen):
                col.append({})            # each element of the matrix is a dictionary
            self.vg_matrix.append(col)
        
        for line in self.all_trace_lines:
            self._lay_line_in_matrix(line)

    def _lay_line_in_matrix(self, line):
        # iterate over a line, laying it into the matrix
        # stamp the line into the matrix
        obj = line.trace_line
        if obj.vertical:
            for y in xrange(obj.pt1[1], obj.pt2[1]+1):
                ele_dict = self.vg_matrix[obj.pt1[0]][y]
                if y == obj.pt1[1]:
                    ele_dict[line] = True # Adds the SymLine to the ele_dict
                elif y == obj.pt2[1]:
                    ele_dict[line] = True
                else:
                    ele_dict[line] = False
        else:
            for x in xrange(obj.pt1[0], obj.pt2[0]+1):
                ele_dict = self.vg_matrix[x][obj.pt1[1]]
                if x == obj.pt1[0]:
                    ele_dict[line] = True
                elif x == obj.pt2[0]:
                    ele_dict[line] = True
                else:
                    ele_dict[line] = False
                    
    def _build_symbol_graph(self):
        self.symbol_graph = nx.Graph()
        for sym in self.all_sym:
            self.symbol_graph.add_node(sym)
            if isinstance(sym, SymPoint):
                self.symbol_graph.add_edge(sym, sym.parent_line)
                if isinstance(sym.tech, DeviceInstance):
                    for bw in sym.sym_bondwires:
                        self.symbol_graph.add_edge(sym, bw)
            elif isinstance(sym, SymLine):
                if sym.wire:
                    self.symbol_graph.add_edge(sym, sym.device)
                    self.symbol_graph.add_edge(sym, sym.trace)
                else:
                    if sym.intersecting_trace is None:
                        # Ignore supertrace elements
                        for trace in sym.trace_connections:
                                self.symbol_graph.add_edge(sym, trace)
                            
                        for superconn in sym.super_connections:
                            self.symbol_graph.add_edge(sym, superconn[0][0])
                    elif (sym.is_supertrace()) and (not sym.element.vertical):
                        # Remove horizontal supertrace elements
                        self.symbol_graph.remove_node(sym)

    def _build_trace_graph(self):
        """ Builds a graph which represents connections between traces in a layout. """
        self.trace_graph = nx.Graph()
        for line in self.all_trace_lines:
            if not line.is_supertrace():
                self.trace_graph.add_node(line)
                for conn in line.trace_connections:
                    if not conn.is_supertrace():
                        self.trace_graph.add_node(conn)
                        self.trace_graph.add_edge(line, conn)
                
                for super_conn in line.super_connections:
                    st = super_conn[0][0] # Vertical element of the connected supertrace
                    self.trace_graph.add_edge(line, st)
                    
        # Identify components of trace graph (separate graph pieces)
        # Create list of devices per component
        # This info will be used to analyze the thermal model
        # The components with devices are 'trace islands'
        self.trace_graph_components = []
        for comp in nx.connected_components(self.trace_graph):
            comp_devices = []
            for line in comp:
                for pt in line.child_pts:
                    if pt.is_device():
                        comp_devices.append(pt)
            self.trace_graph_components.append([comp, comp_devices])
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''      
    def _find_parent_lines(self):
        self.leads = []
        self.devices = []
        
        self.bondwires = []
        for sym in self.all_sym:
            if isinstance(sym.element, LayoutLine):
                if sym.wire:
                    #self._wire_device_trace_intersection(sym)
                    self._find_bondwire_connection(sym)
                else:
                    self._trace_device_intersection(sym)
                    
        # Check that all points have a parent line
        for pt in self.points:
            if pt.parent_line is None:
                raise LayoutError("Not all layout points are connected to a layout line!")
            
    def _find_bondwire_connection(self, sym_wire):
        self.bondwires.append(sym_wire)
        
        sym_wire.dev_pt = None
        # Check against devices
        for point in self.points:
            if isinstance(point.tech, DeviceInstance):
                dev = point.element
                line = sym_wire.element
                pt1_hit = (dev.pt[0] == line.pt1[0] and dev.pt[1] == line.pt1[1])
                pt2_hit = (dev.pt[0] == line.pt2[0] and dev.pt[1] == line.pt2[1])
                if pt1_hit:
                    point.sym_bondwires.append(sym_wire)
                    sym_wire.device = point
                    sym_wire.dev_pt = 1
                elif pt2_hit:
                    point.sym_bondwires.append(sym_wire)
                    sym_wire.device = point
                    sym_wire.dev_pt = 2
                    
        # Note: sym_wire.dev_pt will be None if no device is connected
        if sym_wire.dev_pt is None:
            # check both points for trace connection
            trace1 = self._find_bondwire_trace_connection(sym_wire, sym_wire.element.pt1)
            trace2 = self._find_bondwire_trace_connection(sym_wire, sym_wire.element.pt2)
            if trace1 is None or trace2 is None:
                raise FormulationError('A bondwire is not connected to a trace or device!')
            else:
                # connect the traces
                sym_wire.trace = trace1
                trace1.conn_bonds.append(sym_wire)
                sym_wire.trace2 = trace2
                trace2.conn_bonds.append(sym_wire)
        else:
            # only check the other point for trace connection
            if sym_wire.dev_pt == 1:
                pt = sym_wire.element.pt2 # check at pt2
            else:
                pt = sym_wire.element.pt1 # check at pt1
            
            # Check against traces
            trace = self._find_bondwire_trace_connection(sym_wire, pt)
            if trace is None:
                raise FormulationError('A bondwire is connected to a device but not a trace!')
            else:
                # connect the trace
                sym_wire.trace = trace
                trace.conn_bonds.append(sym_wire)
                
    def _find_bondwire_trace_connection(self, sym_wire, pt):
        x, y = pt
        for trace in self.all_trace_lines:
            if trace.is_supertrace():
                # If trace is a part of a supertrace pair of traces
                # only take a look at the vertical element of the pair
                # so, the connection is only checked once.
                if trace.element.vertical:
                    partner = trace.intersecting_trace
                    region = Rect(trace.element.pt2[1], trace.element.pt1[1], \
                                  partner.element.pt1[0], partner.element.pt2[0])
                    if region.encloses(x, y):
                        return trace
            else:
                tele = trace.element
                if tele.vertical:
                    if x == tele.pt1[0] and (y >= tele.pt1[1] and y <= tele.pt2[1]):
                        return trace
                else:
                    if y == tele.pt1[1] and (x >= tele.pt1[0] and x <= tele.pt2[0]):
                        return trace
        return None
                            
    def _trace_device_intersection(self, trace):
        """ Finds what devices/leads reside on a trace. """
        # Todo: Need to consider moving this method into the check_formulation method
        trace.child_pts = []
        name=1
        for point in self.points:
            pele = point.element
            tele = trace.element
            
            online = False
            if tele.vertical:
                if tele.pt1[0] == pele.pt[0] and pele.pt[1] < tele.pt2[1] and pele.pt[1] > tele.pt1[1]:
                    online = True
            else:
                if tele.pt1[1] == pele.pt[1] and pele.pt[0] < tele.pt2[0] and pele.pt[0] > tele.pt1[0]:
                    online = True
                    
            if online:
                trace.child_pts.append(point)
                point.parent_line = trace
                if isinstance(point.tech, DeviceInstance):
                    point.dv_index = len(self.devices)
                    self.devices.append(point)
                    #self.devices_name.append(str(name))
                    name+=1
                elif isinstance(point.tech, Lead):
                    self.leads.append(point)
    
    def _get_device_design_vars(self):
        dv_list = []
        dv_dict = {}
        for device in self.devices:
            dv_found = False
            for sym_list in self.symmetries:
                if device in sym_list:
                    # we need to find out if this pair/or more already has a dv index
                    for tmp_dev in sym_list:
                        if tmp_dev in dv_dict:
                            # found an assigned dv!
                            dv_index = dv_dict[tmp_dev] # get the device's index
                            dv_dict[device] = dv_index  # add new dv_dict entry for this device
                            device.dv_index = dv_index  # assign dv index to device
                            dv_list[dv_index].append(device)
                            dv_found = True
                            break
                        
            if not dv_found:
                device.dv_index = len(dv_list)
                dv_list.append([device]) # add device to the dv_list
                dv_dict[device] = device.dv_index # add device to dv_dict
                
        return dv_list
    
    def _get_bondwire_design_vars(self):
        dv_list = []
        for bw in self.bondwires:
            if bw.trace2 is not None: # only consider bondwires which connect two traces
                bw.dv_index = len(dv_list)
                dv_list.append(bw)
                
        return dv_list
                
    def _get_trace_design_vars(self):
        # Finds which element widths and lengths are design vars
        # This function assumes no overlapping traces lines or intersections
        
        # Horizontal scan
        ret = self._trace_dv_scan(True) # dv_list, rowcol_list, removed_dv_index
        self.h_dv_list = ret[0]
        self.h_rowcol_list = ret[1]
        self.removed_horiz_dv_index = ret[2]
        
        if self.removed_horiz_dv_index is None:
            raise FormulationError('Optimization will be difficult with this layout. Horizontal flexibility is low.')
        
        # Vertical scan
        ret = self._trace_dv_scan(False) # dv_list, rowcol_list, removed_dv_index
        self.v_dv_list = ret[0]
        self.v_rowcol_list = ret[1]
        self.removed_vert_dv_index = ret[2]
        
        if self.removed_vert_dv_index is None:
            raise FormulationError('Optimization will be difficult with this layout. Vertical flexibility is low.')
        
    def _trace_dv_scan(self, h_scan):
        dv_dict = {}
        dv_list = []
        rowcol_list = []
        
        # Choose correct indices for horizontal or vertical scan
        if h_scan:
            ulen = self.trace_xlen # x is u
            vlen = self.trace_ylen # y is v
        else:
            ulen = self.trace_ylen # y is u
            vlen = self.trace_xlen # x is v
        
        for u in xrange(ulen):
            col = RowCol()
            for v in xrange(vlen):
                # Coordinate transform
                if h_scan: x = u; y = v;
                else: x = v; y = u;
                
                # Sort out which element in a row/col are vert or horiz
                for sym in self.vg_matrix[x][y]:
                    if sym.element.vertical:
                        if h_scan: # add the element if h scan
                            col.elements[sym] = 1
                    else:
                        if not h_scan: # add the element if v scan
                            col.elements[sym] = 1
                        
            if len(col.elements) <= 0:
                col.phantom = True
                col.definable = True
                col.dv_index = len(dv_list)
                dv_list.append([col])
            elif len(col.elements) == 1:
                col.phantom = False
                col.definable = True
                ortho_ele = col.elements.items()[0][0]
                # Check whether this element has a symmetry
                dv_found = False
                for sym_list in self.symmetries:
                    if ortho_ele in sym_list:
                        # we need to find out if this pair/or more already has a dv index
                        for ele in sym_list:
                            if ele in dv_dict:
                                # found an assigned dv!
                                dv_index = dv_dict[ele] # get the element's index
                                dv_dict[ortho_ele] = dv_index # add new dv_dict entry for this element
                                ortho_ele.dv_index = col.dv_index = dv_index # assign col dv and add col to dv_list
                                dv_list[dv_index].append(col)
                                dv_found = True
                                break
                            
                if not dv_found:
                    ortho_ele.dv_index = col.dv_index = len(dv_list)
                    dv_list.append([col]) # add col to the dv_list
                    dv_dict[ortho_ele] = col.dv_index # add ele to dv_dict
                            
            else:
                col.phantom  = False
                col.definable = False
                for ortho_ele in col.elements:
                    # Check whether this element has a symmetry
                    dv_found = False
                    for sym_list in self.symmetries:
                        if ortho_ele in sym_list:
                            # we need to find out if this pair/or more already has a dv index
                            for ele in sym_list:
                                if ele in dv_dict:
                                    # found an assigned dv!
                                    # give new dv_dict entry
                                    dv_index = dv_dict[ele]
                                    dv_dict[ortho_ele] = dv_index
                                    # assign col dv and add col to dv_list
                                    ortho_ele.dv_index = dv_index
                                    dv_list[dv_index].append(ortho_ele)
                                    dv_found = True
                                    break
                                
                    if not dv_found:
                        ortho_ele.dv_index = len(dv_list)
                        dv_list.append([ortho_ele])
                        dv_dict[ortho_ele] = ortho_ele.dv_index
            
            rowcol_list.append(col)
            
        # Find a design_variable which points to all column objects and index it
        removed_dv_index = None
        for dv in dv_list:
            all_removable = True
            for obj in dv:
                if isinstance(obj, SymLine):
                    # this element exists in a multi-element column b/c it is a line (not removable)
                    all_removable = False
                    break
                else:
                    # this is a col. element
                    if not obj.phantom:
                        # Check if single element column has a fixed constraint
                        ortho_ele = obj.elements.items()[0][0]
                        if ortho_ele.constraint is not None:
                            if not ortho_ele.constraint[2] is None:
                                # it has a fixed constraint
                                all_removable = False
                                break
                            
            if all_removable:
                removed_dv_index = dv[0].dv_index
                break
            
        return dv_list, rowcol_list, removed_dv_index
    
    def set_layout_design_values(self, h_design_values, v_design_values, dev_design_values, bondwire_design_values):
        self.h_design_values = h_design_values
        self.v_design_values = v_design_values
        self.dev_design_values = dev_design_values
        self.bondwire_design_values = bondwire_design_values
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''      
    def generate_layout(self):
        self.layout_ready = False
        self._handle_fixed_constraints()
        
        self.h_overflow, self.h_min_max_overflow = self._gen_scan(self.h_rowcol_list, self.h_dv_list, 
                                             self.removed_horiz_dv_index, self.h_design_values, self.sub_dim[0], True)
        
        self.v_overflow, self.v_min_max_overflow = self._gen_scan(self.v_rowcol_list, self.v_dv_list, 
                                             self.removed_vert_dv_index, self.v_design_values, self.sub_dim[1], False)
        
        self._fix_supertrace_overlaps()
        self._replace_intersections()
        self._build_trace_rect_list()
        self._place_devices()
        self._place_leads()
        self._place_bondwires()
        #self._build_trace_rect_list()
        
        self.layout_ready = True
        
    def _handle_fixed_constraints(self):
        # Go through all constraints find what dvs they affect
        # replace the dv value with the constraint value
        for sym in self.fixed_constraints:
            if sym.element.vertical:
                self.h_design_values[sym.dv_index] = sym.constraint[2] # apply fixed width
                #self.v_design_values[sym.dv_index] = sym.constraint[3] # apply fixed length
            else:
                self.v_design_values[sym.dv_index] = sym.constraint[2] # apply fixed width
                #self.h_design_values[sym.dv_index] = sym.constraint[3] # apply fixed length  
    def _gen_scan(self, rowcol_list, dv_list, rem_dv_index, design_values, total, h_scan):
        if h_scan:
            lower = 'left'
            upper = 'right'
            coord_index = 0
        else:
            lower = 'bottom'
            upper = 'top'
            coord_index = 1
        
        #-----------------------------
        # Conservation pass
        #-----------------------------
        # Find removed design variable width
        # Divide the removed design variable width by number of symmetries
        
        # Find total gap width
        # Find total known widths
        # Sub width is known
        # total_unknown = Sub_w - total_gap - total_known
        # total_min: total unknown minimum constraints
        
        total_gap = 0.0
        total_known = 0.0
        undef_indices = []
        for rowcol_index in xrange(len(rowcol_list)):
            rowcol = rowcol_list[rowcol_index]
            
            # No gap in the row/col if all traces in the row/col are supertraces
            all_super_trace = True
            for ele in rowcol.elements:
                if ele.intersecting_trace is None:
                    all_super_trace = False
                    break
            rowcol.all_super = all_super_trace
                    
            if (rowcol_index < len(rowcol_list)-1) and (not rowcol.phantom) and (not all_super_trace):
                total_gap += self.gap
            
            if rowcol.phantom:
                if rowcol.dv_index == rem_dv_index:
                    undef_indices.append(rowcol_index)
                else:
                    total_known += design_values[rowcol.dv_index]
            else:
                if rowcol.dv_index == rem_dv_index:
                    undef_indices.append(rowcol_index)
                else:   
                    max_width = None
                    for element in rowcol.elements:
                        dv_index = element.dv_index
                        if dv_index != rem_dv_index:
                            ele_width = design_values[dv_index]
                            if ele_width > max_width:
                                max_width = ele_width
                    assert(max_width is not None)
                    rowcol.max_width = max_width
                    total_known += max_width
        # End RowCol scan
        
        overflow = 0.0
        total_undef = total - (total_known + total_gap)
        if total_undef < 0.0:
            overflow = math.fabs(total_undef)
        div_undef_width = total_undef/len(undef_indices)
        
        min_constraint_overflow = 0.0
        max_constraint_overflow = 0.0
        for index in undef_indices:
            rowcol = rowcol_list[index]
            rowcol.undef_width = div_undef_width
            
            # Make sure the min and max constraints of the removed variables are met
            if rowcol.phantom: # Check phantom constraint
                if rowcol.phantom_constraint is not None:
                    if rowcol.phantom_constraint[0] is not None:
                        assert(rowcol.phantom_constraint[2] is None)
                        if div_undef_width < rowcol.phantom_constraint[0]:
                            min_constraint_overflow += (rowcol.phantom_constraint[0] - div_undef_width)  
                        elif div_undef_width > rowcol.phantom_constraint[1]:
                            max_constraint_overflow += (div_undef_width - rowcol.phantom_constraint[1])
            else: # Check normal element constraints
                ele = rowcol.elements.items()[0][0]
                if ele.constraint is not None:
                    if ele.constraint[0] is not None:
                        assert(ele.constraint[2] is None)
                        if div_undef_width < ele.constraint[0]:
                            min_constraint_overflow += (ele.constraint[0] - div_undef_width)
                        elif div_undef_width > ele.constraint[1]:
                            max_constraint_overflow += (div_undef_width - ele.constraint[1])
                            
            rowcol.removed = True
        # End conservation pass
        
        # Make single forward pass now that all width values are known
        for rowcol_index in xrange(len(rowcol_list)):
            rowcol = rowcol_list[rowcol_index]
            
            if rowcol_index > 0:
                prev_col_right = rowcol_list[rowcol_index-1].right
            else: # Begin from the right/bottom (0.0)
                prev_col_right = 0.0
            
            rowcol.left = prev_col_right
            if rowcol.phantom:
                if rowcol.removed:
                    width = rowcol.undef_width
                else:
                    width = design_values[rowcol.dv_index]
                    
                rowcol.right = rowcol.left + width
                rowcol.mid = 0.5*(rowcol.left + rowcol.right)
            elif len(rowcol.elements) == 1:
                ele = rowcol.elements.items()[0][0]
                
                if rowcol.removed:
                    width = rowcol.undef_width
                else:
                    width = design_values[ele.dv_index]
                
                # Set trace rectangle coordinates
                tr = ele.trace_rect
                setattr(tr, lower, rowcol.left)
                setattr(tr, upper, rowcol.left + width)
                    
                if rowcol_index == len(rowcol_list)-1:
                    rowcol.right = getattr(tr, upper)
                else:
                    rowcol.right = getattr(tr, upper) + self.gap
                
                # No gap, if all elements in row or col. are super
                if rowcol.all_super:
                    rowcol.right = getattr(tr, upper)
                    
                rowcol.mid = 0.5*(getattr(tr, lower) + getattr(tr, upper))
                
            elif len(rowcol.elements) > 1:
                # If we are at the end, no gap
                if rowcol_index == len(rowcol_list)-1:
                    rowcol.right = rowcol.left + rowcol.max_width
                else:
                    rowcol.right = rowcol.left + rowcol.max_width + self.gap
                    
                # No gap, if all elements in row or col. are super
                if rowcol.all_super:
                    rowcol.right = rowcol.left + rowcol.max_width
                    
                # Always use rowcol.left + rowcol.max_width (do not adjust mid for gap)
                rowcol.mid = 0.5*(rowcol.left + rowcol.left + rowcol.max_width)
                for ele in rowcol.elements:
                    hwidth = 0.5*design_values[ele.dv_index]
                    setattr(ele.trace_rect, lower, rowcol.mid - hwidth)
                    setattr(ele.trace_rect, upper, rowcol.mid + hwidth)
                    
        # ----------------------------------------------------------------
        # Orthogonal Element Scan (Give length to the orthogonal elements)
        # ----------------------------------------------------------------
        # Move through supertrace elements first (normal trace elements depend on these)
        for sym in self.all_trace_lines:
            if (h_scan ^ sym.trace_line.vertical) and (sym.is_supertrace()):
                # Set Lower Range
                lower_index = sym.trace_line.pt1[coord_index]
                lower_val = rowcol_list[lower_index].left
                
                # Set Higher Range
                upper_index = sym.trace_line.pt2[coord_index]
                
                # Check whether we are at the edge of the module
                if upper_index == len(rowcol_list)-1:
                    upper_val = rowcol_list[upper_index].right # Go all the way to the right
                else:
                    upper_val = rowcol_list[upper_index].right - self.gap # Leave some space
                    
                setattr(sym.trace_rect, lower, lower_val)
                setattr(sym.trace_rect, upper, upper_val)
        
        # Move through elements and give them lengths
        for sym in self.all_trace_lines:
            # h_scan xor sym.vertical -> if horizontal scan: get horizontal objects
            # -> if vertical scan: get vertical objects
            if (h_scan ^ sym.trace_line.vertical) and (sym.intersecting_trace is None):
                # Set Lower Range
                lower_index = sym.trace_line.pt1[coord_index]
                lower_val = rowcol_list[lower_index].left
                
                # Set Higher Range
                upper_index = sym.trace_line.pt2[coord_index]
                
                # Check whether we are at the edge of the module
                if upper_index == len(rowcol_list)-1:
                    upper_val = rowcol_list[upper_index].right # Go all the way to the right
                else:
                    upper_val = rowcol_list[upper_index].right - self.gap # Leave some space
                    
                #setattr(sym.trace_rect, lower, lower_val)
                #setattr(sym.trace_rect, upper, upper_val)
                    
                # Check Upper and Lower Abutments
                # Lower Abutment Check
                x = sym.trace_line.pt1[0]
                y = sym.trace_line.pt1[1]
                for check_sym in self.vg_matrix[x][y]:
                    if (check_sym is not sym):
                        if not(h_scan ^ check_sym.element.vertical):
                            # Horiz-Vert or Vert-Horiz Abutment
                            if not(h_scan and self.vg_matrix[x][y][check_sym]):
                                lower_val = getattr(check_sym.trace_rect, upper)
                # End Lower Check

                # Upper Abutment Check
                x = sym.trace_line.pt2[0]
                y = sym.trace_line.pt2[1]
                for check_sym in self.vg_matrix[x][y]:
                    if (check_sym is not sym) and not(check_sym.is_supertrace()):
                        if (not h_scan ^ check_sym.element.vertical):
                            # Horiz-Vert or Vert-Horiz Abutment
                            if not(h_scan and self.vg_matrix[x][y][check_sym]):
                                upper_val = getattr(check_sym.trace_rect, lower)
                        else:
                            # Horiz-Horiz or Vert-Vert Abutment
                            # Handle normal trace with same orientation here
                            if (sym.intersecting_trace is None):
                                upper_val = rowcol_list[upper_index].left
                # End Upper Check
                
                # Set the lower and upper rect values
                setattr(sym.trace_rect, lower, lower_val)
                setattr(sym.trace_rect, upper, upper_val)
        # End Layout Scan
        
        return overflow, (min_constraint_overflow, max_constraint_overflow)
    
    def _fix_supertrace_overlaps(self):
        for sym in self.all_trace_lines:
            if not sym.is_supertrace():
                if sym.element.vertical:
                    lower = 'bottom'
                    upper = 'top'
                    coord_index = 0
                    
                    lower_ortho = 'left'
                    upper_ortho = 'right'
                    super_index = 1
                else:
                    lower = 'left'
                    upper = 'right'
                    coord_index = 1
                    
                    lower_ortho = 'bottom'
                    upper_ortho = 'top'
                    super_index = 0
                    
                if len(sym.super_connections) > 0:
                    for conn in sym.super_connections:
                        supertrace = conn[0]
                        conn_type = conn[1]
                        long_contacts = supertrace[0].long_contacts
                        side = 0
                        if sym.element.vertical:
                            if conn_type == 1:
                                side = Rect.TOP_SIDE
                            elif conn_type == 2:
                                side = Rect.BOTTOM_SIDE
                        else:
                            if conn_type == 1:
                                side = Rect.RIGHT_SIDE
                            elif conn_type == 2:
                                side = Rect.LEFT_SIDE
                            
                        if conn_type == 1:
                            # Element connected at Pt1
                            long_contact_side_detected = False
                            for lc in long_contacts:
                                if long_contacts[lc] == side:
                                    long_contact_side_detected = True
                                    break
                            if not long_contact_side_detected:
                                lower_val = getattr(supertrace[coord_index].trace_rect, upper)
                                setattr(sym.trace_rect, lower, lower_val)
                        elif conn_type == 2:
                            # Element connected at Pt2
                            long_contact_side_detected = False
                            for lc in long_contacts:
                                if long_contacts[lc] == side:
                                    long_contact_side_detected = True
                                    break
                            if not long_contact_side_detected:
                                upper_val = getattr(supertrace[coord_index].trace_rect, lower)
                                setattr(sym.trace_rect, upper, upper_val)
                        elif conn_type == 3:
                            # Element connected by long contact (supertrace needs to move)
                            upper_val = getattr(sym.trace_rect, upper_ortho)
                            setattr(supertrace[super_index].trace_rect, lower_ortho, upper_val)
                        elif conn_type == 4:
                            # Element connected by long contact (supertrace needs to move)
                            lower_val = getattr(sym.trace_rect, lower_ortho)
                            setattr(supertrace[super_index].trace_rect, upper_ortho, lower_val)
    
    def _replace_intersections(self):
        # For supertraces:
        # replace intersecting traces with one rectangle
        for sym in self.all_trace_lines:
            if sym.is_supertrace() and sym.element.vertical:
                i_trace = sym.intersecting_trace
                i_trace.has_rect = False
                if sym.element.vertical:
                    sym.trace_rect.left = i_trace.trace_rect.left
                    sym.trace_rect.right = i_trace.trace_rect.right
    
    def _place_devices(self):
        for dev in self.devices:
            width, length, thickness = dev.tech.device_tech.dimensions
            hwidth = 0.5*width
            hlength = 0.5*length
            fract_pos = self.dev_design_values[dev.dv_index]
            
            line = dev.parent_line
            trace_rect = line.trace_rect
            
            xpos = 0.0
            ypos = 0.0
            if line.element.vertical:
                top = trace_rect.top - self.design_rules.min_die_trace_dist - hlength
                bottom = trace_rect.bottom + self.design_rules.min_die_trace_dist + hlength
                ypos = top*fract_pos + bottom*(1.0-fract_pos)
                xpos = 0.5*(trace_rect.left + trace_rect.right)
                dev.footprint_rect = Rect(ypos+hlength, ypos-hlength, xpos-hwidth, xpos+hwidth)
                dev.orientation = 1
            else:
                right = trace_rect.right - self.design_rules.min_die_trace_dist - hlength
                left = trace_rect.left + self.design_rules.min_die_trace_dist + hlength
                xpos = right*fract_pos + left*(1.0-fract_pos)
                ypos = 0.5*(trace_rect.top + trace_rect.bottom)
                dev.footprint_rect = Rect(ypos+hwidth, ypos-hwidth, xpos-hlength, xpos+hlength)
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
                    if powerbond.dev_pt == 2:
                        dev.orientation = dev.tech.device_tech.power_side
                    else:
                        if dev.tech.device_tech.power_side == 1:
                            dev.orientation = 2 # 180 degrees from ref.
                        else:
                            dev.orientation = 1 # 0 degrees from ref.
                elif dev.orientation == 3:
                    # die resides on horizontal trace
                    # orient device by power bonds
                    if powerbond.dev_pt == 1:
                        if dev.tech.device_tech.power_side == 1:
                            dev.orientation = 4 # -90 degrees from ref.
                        else:
                            dev.orientation = 3 # 90 degrees from ref.
                    else:
                        if dev.tech.device_tech.power_side == 1:
                            dev.orientation = 3
                        else:
                            dev.orientation = 4
        
    def _place_leads(self):
        for lead in self.leads:
            if lead.tech.shape == Lead.BUSBAR:
                self._place_rect_lead(lead)
            elif lead.tech.shape == Lead.ROUND:
                self._place_round_lead(lead)
            
    def _place_rect_lead(self, lead):
        line = lead.parent_line
        trace_rect = line.trace_rect
        xpos = 0.0
        ypos = 0.0
        if line.element.vertical:
            hwidth = 0.5*lead.tech.dimensions[1]
            hlength = 0.5*lead.tech.dimensions[0]
            lead.orientation = 3
            # find if near left or right (decide orientation)
            # for power leads only right now
            edge_dist = self.sub_dim[0] - 0.5*(trace_rect.left + trace_rect.right)
            if edge_dist < 0.5*self.sub_dim[0]:
                # right
                xpos = trace_rect.right - hwidth
                lead.orientation = 3
            else:
                # left
                xpos = trace_rect.left + hwidth
                lead.orientation = 4
            
            ypos = 0.5*(trace_rect.bottom + trace_rect.top)
            lead.footprint_rect = Rect(ypos+hlength, ypos-hlength, xpos-hwidth, xpos+hwidth)
        else:
            # find if near top or bottom (decide orientation)
            hwidth = 0.5*lead.tech.dimensions[0]
            hlength = 0.5*lead.tech.dimensions[1]
            lead.orientation = 1
            
            edge_dist = self.sub_dim[1] - 0.5*(trace_rect.top + trace_rect.bottom)
            if edge_dist < 0.5*self.sub_dim[1]:
                # top
                ypos = trace_rect.top - hlength
                lead.orientation = 1
            else:
                # bottom
                ypos = trace_rect.bottom + hlength
                lead.orientation = 2
                
            xpos = 0.5*(trace_rect.left + trace_rect.right)
            lead.footprint_rect = Rect(ypos+hlength, ypos-hlength, xpos-hwidth, xpos+hwidth)
            
        lead.center_position = (xpos, ypos)
    
    def _place_round_lead(self, lead):
        line = lead.parent_line
        trace_rect = line.trace_rect
        radius = 0.5*lead.tech.dimensions[0]
        space = self.gap + radius
        center = [0.0, 0.0]
        
        if line.element.vertical:
            lower = 'bottom'
            upper = 'top'
            ortho_lower = 'left'
            ortho_upper = 'right'
            coord = 1
            ortho_coord = 0
        else:
            lower = 'left'
            upper = 'right'
            ortho_lower = 'bottom'
            ortho_upper = 'top'
            coord = 0
            ortho_coord = 1
        
        # Determine if lead should stick to (top, mid, bottom) / (left, mid, right)
        pos = lead.raw_element.pt[coord] - line.raw_element.pt1[coord]
        end = line.raw_element.pt2[coord] - line.raw_element.pt1[coord]
        mid = end/2
        end_dist = math.fabs(end - pos)
        mid_dist = math.fabs(mid - pos)
        beg_dist = math.fabs(pos)
        at_beg = 0; at_mid = 1; at_end = 2
        dists = [(beg_dist, at_beg), (mid_dist, at_mid), (end_dist, at_end)]
        dists.sort(key=lambda dist_tuple: dist_tuple[0])
        
        pos = 0.0
        if dists[0][1] == at_beg:
            pos = getattr(trace_rect, lower) + space
        elif dists[0][1] == at_mid:
            pos = 0.5*(getattr(trace_rect, upper) + getattr(trace_rect, lower))
        elif dists[0][1] == at_end:
            pos = getattr(trace_rect, upper) - space
        center[coord] = pos
            
        mid = 0.5*(getattr(trace_rect, ortho_upper) + getattr(trace_rect, ortho_lower))
        center[ortho_coord] = mid
        
        lead.footprint_rect = Rect(center[1]+radius, center[1]-radius,
                                   center[0]-radius, center[0]+radius)
        lead.center_position = center
                    
    def _place_bondwires(self):
        for wire in self.bondwires:
            if wire.dev_pt is not None:
                self._place_device_bondwire(wire)
            elif wire.trace2 is not None:
                self._place_trace_to_trace_bondwire(wire)
            
    def _place_device_bondwire(self, wire):
        start_pts = []
        end_pts = []
        
        assert wire.device is not None, "A bondwire is not connected to a device."
        dev_tech = wire.device.tech.device_tech
        
        assert wire.trace is not None, "A bondwire is not connected to trace."
        trace_rect = wire.trace.trace_rect
        
        if wire.tech.wire_type == BondWire.POWER:
            dist = self.design_rules.power_wire_trace_dist
        elif wire.tech.wire_type == BondWire.SIGNAL:
            dist = self.design_rules.signal_wire_trace_dist
        else:
            dist = self.design_rules.power_wire_trace_dist
        
        if wire.device.orientation == 1:
            theta = 0.0
        elif wire.device.orientation == 2:
            theta = 180.0
        elif wire.device.orientation == 3:
            theta = 90.0
        elif wire.device.orientation == 4:
            theta = -90.0
            
        rot_vec = complex_rot_vec(theta)
        hwidth, hlength = (0.5*dev_tech.dimensions[0], 0.5*dev_tech.dimensions[1])
        
        for landing in dev_tech.wire_landings:
            if landing.bond_type == wire.tech.wire_type:
                lx, ly = landing.position
                coord = complex(lx - hwidth, ly - hlength) # create coordinates wrt the die center
                coord = coord*rot_vec # Rotate coordinates by theta
                
                start_pt = (coord.real+wire.device.center_position[0], 
                            coord.imag+wire.device.center_position[1])
                if wire.trace.element.vertical:
                    if wire.dev_pt == 2:
                        trace_x = trace_rect.right - dist
                    else:
                        trace_x = trace_rect.left + dist
                    end_pt = (trace_x, start_pt[1])
                    land_pt = (trace_x, wire.device.center_position[1])
                else:
                    if wire.dev_pt == 2:
                        trace_y = trace_rect.top - dist
                    else:
                        trace_y = trace_rect.bottom + dist
                    end_pt = (start_pt[0], trace_y)
                    land_pt = (wire.device.center_position[1], trace_y)
                    
                start_pts.append(start_pt)
                end_pts.append(end_pt)
                
        wire.start_pts = start_pts
        wire.end_pts = end_pts
        wire.land_pt = land_pt
        wire.land_pt2 = None
        
    def _place_trace_to_trace_bondwire(self, wire):
        start_pts = []
        end_pts = []
        
        assert wire.trace is not None, 'Bondwire is not connected to trace!'
        assert wire.trace2 is not None, 'Bondwire is not connected to trace!'
        
        if wire.num_wires is None:
            print 'None is got!'
            wire.num_wires = 1
            
        if wire.wire_sep is None:
            wire.wire_sep = 0
            
        trace_inset = 0.0
        if wire.tech.wire_type == BondWire.POWER:
            trace_inset = self.design_rules.power_wire_trace_dist
        elif wire.tech.wire_type == BondWire.SIGNAL:
            trace_inset = self.design_rules.signal_wire_trace_dist
            
        frac_pos = self.bondwire_design_values[wire.dv_index]
        
        rect1 = wire.trace.trace_rect
        rect2 = wire.trace2.trace_rect
        
        vert_interval = get_overlap_interval([rect1.bottom, rect1.top], [rect2.bottom, rect2.top])
        horz_interval = get_overlap_interval([rect1.left, rect1.right], [rect2.left, rect2.right])
        
        vert_overlap = vert_interval[1] - vert_interval[0]
        horz_overlap = horz_interval[1] - horz_interval[0]
        
        if vert_overlap > 0.0:
            # rect2 will be to the left if this criterion is met
            # otherwise it is on the right
            on_left = rect2.right < rect1.left
            if on_left:
                start_x = rect2.right-trace_inset
                end_x = rect1.left+trace_inset
                start_pt_conn = wire.trace2
                end_pt_conn = wire.trace
            else:
                start_x = rect1.right-trace_inset
                end_x = rect2.left+trace_inset
                start_pt_conn = wire.trace
                end_pt_conn = wire.trace2
            
            wire_region = (2*trace_inset+(wire.num_wires-1)*wire.wire_sep)
            placement_space = vert_overlap-wire_region
            start_y = vert_interval[0]+trace_inset+frac_pos*placement_space
            for i in xrange(wire.num_wires):
                start_pts.append((start_x, start_y))
                end_pts.append((end_x, start_y))
                start_y += wire.wire_sep
                
            midpoint_y = vert_interval[0]+frac_pos*placement_space+0.5*wire_region
            land_pt1 = (start_x, midpoint_y)
            land_pt2 = (end_x, midpoint_y)
                
        elif horz_overlap > 0.0:
            # rect2 is underneath if this criterion is met
            # otherwise it is on top
            on_bottom = rect2.top < rect1.bottom
            
            if on_bottom:
                start_y = rect2.top-trace_inset
                end_y = rect1.bottom+trace_inset
                start_pt_conn = wire.trace2
                end_pt_conn = wire.trace
            else:
                start_y = rect1.top-trace_inset
                end_y = rect2.bottom+trace_inset
                start_pt_conn = wire.trace
                end_pt_conn = wire.trace2
            
            wire_region = (2*trace_inset+(wire.num_wires-1)*wire.wire_sep)
            placement_space = horz_overlap-wire_region
            start_x = horz_interval[0]+trace_inset+frac_pos*placement_space
            for i in xrange(wire.num_wires):
                start_pts.append((start_x, start_y))
                end_pts.append((start_x, end_y))
                start_x += wire.wire_sep
                
            midpoint_x = horz_interval[0]+frac_pos*placement_space+0.5*wire_region
            land_pt1 = (midpoint_x, start_y)
            land_pt2 = (midpoint_x, end_y)
        else:
            # target is diagonal (not applicable)
            land_pt1 = None
            land_pt2 = None
            start_pt_conn = None
            end_pt_conn = None
            
        wire.start_pts = start_pts
        wire.end_pts = end_pts
        wire.land_pt = land_pt1
        wire.land_pt2 = land_pt2
        wire.start_pt_conn = start_pt_conn
        wire.end_pt_conn = end_pt_conn
            
    def _build_trace_rect_list(self):
        self.trace_rects = []
        for line in self.all_trace_lines:
            if line.has_rect:
                self.trace_rects.append(line.trace_rect)
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''  
    def drc_err_dict_update(self,name):
        '''
        Quang:
        This method is used to add a new error type to symbolic layout error dictionary.
        Used for error analysis
        Input: an error name, it will be counted up for each evaluation and saved in a python dictionary
        Return: None
        '''
        try: 
            self.err_report[str(name)]+=1 # update error count for existing tuples
        except:
            self.err_report[str(name)]=0 # when the error first occur, this method will add the new name to error dictionary
    def drc_single_check(self,var_name,var_description,debug):
        ''' 
        Quang:
        This method will check the drc for a drc type with descrition
        Input: var_name --- The variable represent drc_error 
               var_description --- Description in error dictionary and Debug mode
               Debug--- set equal True to print out error messages
        Return: 0 or 1 so that this value can be added in the err_counter'''
        if var_name >0.0:
            if debug:
                self.drc_err_dict_update(var_description)
            return var_name
        else:
            return 0
    def passes_drc(self, debug = False):
        '''
        Quang: 
        This method will check all the DRC error and report an error counter for each layout
        It is then used in _opt_eval the more errors there are, the more disadvantage will be added to the individual (so that it will be eliminated)
        Errors name and count will be added into self.err_report, this dictionary is used for analysis to improve the software
        I HAVE INCLUDED 2 methods to make this code concise
        plz check: drc_err_dict_update(self,name) and drc_single_check(self,var_name,var_description,debug):
        '''
        err_count=0
        try:                                            # evaluations counter is store in self.ctest
            self.ctest += 1
        except:
            self.ctest = 1

        err_count+= self.drc_single_check(self.h_overflow, 'Horizontal_Overflow', debug)
        err_count+= self.drc_single_check(self.v_overflow, 'Vertical_Overflow', debug)
        err_count+= self.drc_single_check(self.h_min_max_overflow[0], 'Min. Horizontal_Overflow', debug)
        err_count+= self.drc_single_check(self.h_min_max_overflow[1], 'Max. Horizontal_Overflow', debug)
        err_count+= self.drc_single_check(self.v_min_max_overflow[0], 'Min. Vertical_Overflow', debug)
        err_count+= self.drc_single_check(self.v_min_max_overflow[1], 'Max. Vertical_Overflow', debug)
        err_count+= self.drc_single_check(self._trace_min_width(), 'Traces less than Min_Width', debug) 
        err_count+= self.drc_single_check(self._lead_trace_overlap(), 'Leads are overlapping trace', debug)
        err_count+= self.drc_single_check(self._device_trace_overlap(), 'Devices are not overlapping trace', debug) 
        err_count+= self.drc_single_check(self._component_overlap(), 'Two or more components are overlapping', debug)
        err_count+= self.drc_single_check(self._bondwire_trace_overlap(), 'Bondwires are not contacting trace', debug)
        err_count+= self.drc_single_check(self._bondwire_component_overlap(), 'Bondwires are intersecting other layout components', debug)
        print err_count
        return err_count
    def _trace_min_width(self):
        # Check that all traces are greater than minimum width
        min_width = self.design_rules.min_trace_width
        total_error = 0.0
        for rect in self.trace_rects:
            if rect.width()!= 0.0 and rect.height() != 0.0:
                if rect.width() < min_width:
                    total_error += min_width - rect.width()
                if rect.height() < min_width:
                    total_error += min_width - rect.height()
            else:
                total_error=1000000
                print 'Special case, width or length is zero'
                return total_error
        return total_error
    
    def _lead_trace_overlap(self):
        # Check Lead/Trace Overlap
        total_error = 0.0
        for lead in self.leads:
            # only check against the parent line's immediate connections
            # instead of going through all of the layouts traces
            pline = lead.parent_line
            traces = [pline.trace_rect]
            for line in pline.trace_connections:
                if line.is_supertrace():
                    if line.element.vertical:
                        traces.append(line.trace_rect)
                    else:
                        traces.append(line.intersecting_trace.trace_rect)
                else:
                    traces.append(line.trace_rect) 
                
            lead_rect = lead.footprint_rect.deepCopy()
            #lead_rect.change_size(self.design_rules.min_die_trace_dist)
            lead_area = lead_rect.area()
            area_sum = 0.0
            for rect in traces:
                inter = rect.intersection(lead_rect)
                if inter is not None:
                    area_sum += inter.area()
                if area_sum >= lead_area:
                    break
                
            total_error += lead_area - area_sum
            
        return total_error
            
    def _device_trace_overlap(self):
        # Check Device/Trace Overlap
        total_error = 0.0
        for device in self.devices:
            # only check against the parent line
            dev_rect = device.footprint_rect.deepCopy()
            dev_rect.change_size(self.design_rules.min_die_trace_dist)
            inter = device.parent_line.trace_rect.intersection(dev_rect)
            if inter is not None:
                total_error += dev_rect.area() - inter.area()
            
        return total_error
    
    def _component_overlap(self):
        # Check Device->(Device or Trace) Overlap
        checked = {}
        total_error = 0.0
        for pt1 in self.points:
            for pt2 in self.points:
                if pt1 is not pt2:
                    if not((pt1, pt2) in checked):
                        if isinstance(pt1.tech, DeviceInstance) and isinstance(pt2.tech, DeviceInstance):
                            rect1 = pt1.footprint_rect.deepCopy()
                            rect2 = pt2.footprint_rect
                            rect1.change_size(self.design_rules.min_die_die_dist)
                        else:
                            rect1 = pt1.footprint_rect
                            rect2 = pt2.footprint_rect
                            
                        inter = rect1.intersection(rect2)
                        if inter is not None:
                            total_error += inter.area()
                                
                        checked[(pt2, pt1)] = True
        return total_error
    
    def _bondwire_trace_overlap(self):
        total_error = 0.0
        for bw in self.bondwires:
            if bw.tech.wire_type == BondWire.POWER:
                trace_inset = self.design_rules.power_wire_trace_dist
            elif bw.tech.wire_type == BondWire.SIGNAL:
                trace_inset = self.design_rules.signal_wire_trace_dist
                
            if (bw.land_pt is None) and (bw.land_pt2 is None):
                # bondwires were not even able to be placed
                total_error += len(bw.start_pts+bw.end_pts)
            elif (bw.land_pt is not None) and (bw.land_pt2 is None):
                # bondwire connects device to trace
                rect = bw.trace.trace_rect.deepCopy()
                rect.change_size(-trace_inset) # reduces size of trace by how much room the wire should be given via DRs
                for pt in bw.end_pts:
                    if not rect.encloses(pt[0], pt[1]):
                        total_error += distance(pt, rect.center())
            else: 
                # bondwire connects trace to trace
                start_rect = bw.start_pt_conn.trace_rect.deepCopy()
                end_rect = bw.end_pt_conn.trace_rect.deepCopy()
                # Reduce size of rects by the min. design rule width
                start_rect.change_size(-trace_inset)
                end_rect.change_size(-trace_inset)
                # Check if points are within the design rule area inside rectangle
                for pt in bw.start_pts:
                    if not (start_rect.encloses(pt[0], pt[1])):
                        total_error += distance(pt, start_rect.center())
                
                for pt in bw.end_pts:
                    if not (end_rect.encloses(pt[0], pt[1])):
                        total_error += distance(pt, end_rect.center())
                
        return total_error
    
    def _bondwire_component_overlap(self):
        '''Checks whether the landing points of bondwires intersect with the wrong components'''
        total_error = 0.0
        for bw in self.bondwires:
            if bw.tech.wire_type == BondWire.POWER:
                trace_inset = self.design_rules.power_wire_component_dist
            elif bw.tech.wire_type == BondWire.SIGNAL:
                trace_inset = self.design_rules.signal_wire_component_dist
                
            if (bw.land_pt is not None) and (bw.land_pt2 is None):
                # bondwire connects device to trace
                for pt in self.points:
                    if pt is not bw.dev_pt:
                        # check for intersection
                        for bwpt in bw.end_pts:
                            rect = pt.footprint_rect.deepCopy()
                            rect.change_size(trace_inset)
                            if rect.encloses(bwpt[0], bwpt[1]):
                                d=distance(bwpt, rect.center())
                                if d!=0:
                                    total_error += 1.0/(distance(bwpt, rect.center()))  # this can create divide for zero problem... In the case that it happen again set a big value as an answer
                                else: 
                                    total_error += float('Inf')
            else:
                # bondwire connects trace to trace
                for pt in self.points:
                    # check for intersection between all components
                    for bwpt in bw.start_pts+bw.end_pts:
                        rect = pt.footprint_rect.deepCopy()
                        rect.change_size(trace_inset)
                        if rect.encloses(bwpt[0], bwpt[1]):
                            d=distance(bwpt, rect.center())
                            if d!=0:
                                total_error += 1.0/(distance(bwpt, rect.center()))  # this can create divide for zero problem... In the case that it happen again set a big value as an answer
                            else: 
                                total_error += float('Inf')
                
        return total_error
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''  
    def optimize(self, iseed=None, inum_gen=800, mu=15, ilambda=30, progress_fn=None):
        self.eval_count = 0
        self.eval_total = inum_gen*ilambda    # check this... this sounds not correct to me -- Quang
        self.opt_progress_fn = progress_fn
        self._map_design_vars()
        # When the project is saved, must save the seed also..... so that we can regenerate it
        for pm in self.perf_measures:
            if isinstance(pm, ElectricalMeasure):
                self.mdl_type=pm.mdl
                print 'mdl_type',self.mdl_type
             
        print 'seed:',iseed
#        print 'num gen:',inum_gen
#        print 'mu:',mu
        print self.opt_dv_list
        print self.perf_measures
        
        self.algorithm='NSGAII'
        if self.algorithm=='NSGAII':
            opt = NSGAII_Optimizer(self.opt_dv_list, self._opt_eval, 
                                   len(self.perf_measures), seed=iseed, num_gen=inum_gen, mu=mu, ilambda=ilambda)
            
            opt.run()
            self.solutions = opt.solutions
            self.solution_lib = SolutionLibrary(self)
        
        #print self.solution_lib
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''      
    def debug_single_eval(self):
        self.eval_count = 0
        self.eval_total = 1
        
        self._map_design_vars()
        opt = NSGAII_Optimizer(self.opt_dv_list, self._opt_eval, 
                               len(self.perf_measures), seed=time.time(), num_gen=1)
        self._opt_eval(opt.population[0])
        
    def _map_design_vars(self):
        # Do not optimize fixed constraints! (Get rid of them)
        # Form one list of design variables (including device locations)
        
        self.opt_dv_list = [] # list of all optimization DesignVar objects
        self.opt_to_sym_index = [] # Each entry represents a DesignVar's map back to SymLayout
        
        self._dv_map_scan(True) # horizontal trace vars
        self._dv_map_scan(False) # vertical trace vars
        self._device_dv_scan() # device vars
        self._bondwire_dv_scan() # trace to trace bondwires
        assert len(self.opt_dv_list) == len(self.opt_to_sym_index), 'Optimization design variable list should be same length as optimization to symbolic map list!'
                
    def _dv_map_scan(self, h_scan):
        if h_scan:
            scan_list = self.h_dv_list
            max_default = self.sub_dim[0]
            div = len(self.h_rowcol_list)
            dv_type = self.HORZ_DV
            rem_index = self.removed_horiz_dv_index
        else:
            scan_list = self.v_dv_list
            max_default = self.sub_dim[1]
            div = len(self.v_rowcol_list)
            dv_type = self.VERT_DV
            rem_index = self.removed_vert_dv_index
            
        for i in xrange(len(scan_list)):
            # Get or make dv constraint
            constraint = None
            init_values = None
            fixed = False
            removed = (i == rem_index)
            obj = scan_list[i][0]
            
            if not removed:
                # Assign constraints if there are any already bound to the design variable object
                if isinstance(obj, SymLine):
                    if obj.constraint is not None:
                        constraint = obj.constraint
                    else:
                        constraint = None
                elif isinstance(obj, RowCol):
                    if obj.phantom:
                        constraint = obj.phantom_constraint
                    else:
                        constraint = obj.elements.items()[0][0].constraint
                        
                if constraint is None:
                    # Make default constraint (can't be larger than layout dim)
                    min_const = self.design_rules.min_trace_trace_width
                    if isinstance(obj, RowCol):
                        if obj.phantom:
                            min_const = 0.0  # Phantom rows/cols can go to zero
                        
                    constraint = (min_const, max_default)
                    
                    # Make default init. range (start at a reasonable size)
                    avg = max_default/div
                    delta = avg/3.0
                    init_values = (avg-delta, avg+delta)
                else:
                    if constraint[2] is not None:
                        fixed = True
                    else:
                        constraint = constraint[0:2]
                        init_values = constraint
                    
                if not fixed:
                    dv = DesignVar(constraint, init_values)
                    self.opt_dv_list.append(dv)
                    self.opt_to_sym_index.append((dv_type, i))
                
    def _device_dv_scan(self):
        for i in xrange(len(self.dev_dv_list)):
            constraint = (0.0, 1.0)
            init_values = (0.0, 1.0)
            dv = DesignVar(constraint, init_values)
            self.opt_dv_list.append(dv)
            self.opt_to_sym_index.append((self.DEV_DV, i))
            
    def _bondwire_dv_scan(self):
        for i in xrange(len(self.bondwire_dv_list)):
            constraint = (0.0, 1.0)
            init_values = (0.0, 1.0)
            dv = DesignVar(constraint, init_values)
            self.opt_dv_list.append(dv)
            self.opt_to_sym_index.append((self.BONDWIRE_DV, i))
            
    def rev_map_design_vars(self, individual):
        for i in xrange(len(self.opt_dv_list)):
            dv_type, index = self.opt_to_sym_index[i]
            if dv_type == self.HORZ_DV:
                self.h_design_values[index] = individual[i]
            elif dv_type == self.VERT_DV:
                self.v_design_values[index] = individual[i]
            elif dv_type == self.DEV_DV:
                self.dev_design_values[index] =  individual[i]
            elif dv_type == self.BONDWIRE_DV:
                self.bondwire_design_values[index] = individual[i]
                
    def gen_solution_layout(self, solution_index):
        individual = self.solution_lib.individuals[solution_index]
        self.rev_map_design_vars(individual)
        self._opt_eval(individual)
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''      
    def _opt_eval(self, individual):
        
        self.rev_map_design_vars(individual)
        self.generate_layout()
        ret = []       
        drc_val = self.passes_drc(False)
        if drc_val > 0.0:                             # non-convergence case
            #Brett's method
            for i in xrange(len(self.perf_measures)):
                ret.append(drc_val+10000)
            return ret         
        else:                 
            print ' new solution is found *******'    #convergence case 
            parasitic_time = 0.0
            start_time = time.time()
            self._build_lumped_graph()

            parasitic_time += time.time() - start_time;            
            for measure in self.perf_measures:
                if isinstance(measure, ElectricalMeasure):
                    start_time = time.time()
                    type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                                 ElectricalMeasure.MEASURE_IND: 'ind',
                                 ElectricalMeasure.MEASURE_CAP: 'cap'}
                    measure_type = type_dict[measure.measure]
                    if measure.measure == ElectricalMeasure.MEASURE_CAP:
                        val = self._measure_capacitance(measure)
                    else:
                        # Measure res. or ind. from src node to sink node
                        src = measure.pt1.lumped_node
                        sink = measure.pt2.lumped_node
                        try:
                            val = parasitic_analysis(self.lumped_graph, src, sink, measure_type)
                        except LinAlgError:
                            val = 1e6
                                
    #                    print measure_type, val
                    ret.append(val)
                    parasitic_time += time.time() - start_time;
                elif isinstance(measure, ThermalMeasure):
                    val = self._thermal_analysis(measure)
                    ret.append(val)
        
        # Update progress bar and eval count
        self.eval_count += 1
        percent_done = 100.0*float(self.eval_count)/float(0.8*self.eval_total)
        if percent_done > 100.0:
            percent_done = 100.0


        if hasattr(self, 'opt_progress_fn'):
            if self.opt_progress_fn is not None:
                self.opt_progress_fn(percent_done)
        else:
            print 'Eval. Count:', self.eval_count, ' %', percent_done, ' complete.'
        return ret
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''  
    def _measure_capacitance(self, measure):
        if not hasattr(measure, 'lines'): # if measure doesn't have lines attribute, just return zero (for backward compatibilty)
            return 0.0
        # Iterate over each trace line
        # Sum area of each trace line rectangle
        # Use total area of trace to evaluate capacitance
        metal_t = self.module.substrate.substrate_tech.metal_thickness
        iso_t = self.module.substrate.substrate_tech.isolation_thickness
        epsil = self.module.substrate.substrate_tech.isolation_properties.rel_permit
        total_cap = 0.0
        supertraces = [] # make sure supertraces are not handled twice
        for line in measure.lines:
            if (not line.wire) and (line.trace_rect is not None):
                trace = None
                if line.is_supertrace():
                    if line.has_rect:
                        if line not in supertraces:
                            trace = line.trace_rect
                            supertraces.append(line)
                    else:
                        if line.intersecting_trace not in supertraces:
                            trace = line.intersecting_trace.trace_rect
                            supertraces.append(line.intersecting_trace)
                else:
                    trace = line.trace_rect
                    
                if trace is not None:
                    total_cap += trace_capacitance(trace.width(), trace.height(), metal_t, iso_t, epsil)
        return total_cap
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''  
    def _thermal_analysis(self, measure):
        # RECT_FLUX_MODEL
        temps = perform_thermal_analysis(self, TFSM_MODEL)#<--RECT_FLUX_MODEL
        if isinstance(measure,int):
            return temps
        else:
            if measure.stat_fn == ThermalMeasure.FIND_MAX:
                return np.max(temps)
            elif measure.stat_fn == ThermalMeasure.FIND_AVG:
                return np.average(temps)
            elif measure.stat_fn == ThermalMeasure.FIND_STD_DEV:
                return np.std(temps)
            else:
                return np.max(temps)
        
    '''-----------------------------------------------------------------------------------------------------------------------------------------------------'''         
                
    def _build_lumped_graph(self): # when lumped graph is built everything is computed
        # To do:
        # 1. Implement bondwire to spine connection parasitic eval
        # 2. Implement long contact point to spine connection eval

        # Trace graph res ind cap and points for post model run
        self.trace_info = []  # used to save all width and length for evaluation
        self.trace_nodes = []  # all nodes that will be used to connect traces to lumped_graph

        # Initialize nx.graph structure to store trace graph
        lumped_graph = nx.Graph()
        vert_count = 0
        conn_dict = {}; conn_sum = 0
        overlap_pts = {}; overlap_sum = 0
        wire_dev_dict = {}; bw_sum = 0
        wire_wire_dict = {}; ww_sum = 0
        supertrace_conn = {}; supertrace_sum = 0
        long_conn = {}; long_sum = 0

        # Trace data
        thickness = self.module.substrate.substrate_tech.metal_thickness
        sub_thick = self.module.substrate.substrate_tech.isolation_thickness
        sub_epsil = self.module.substrate.substrate_tech.isolation_properties.rel_permit
        resist = self.module.substrate.substrate_tech.metal_properties.electrical_res
        freq = self.module.frequency

        # All graph value will be 1 prior to computation
        ind,res,cap=[1,1,1] # initialize parasitic values to build edges

        # Handle Supertraces first
        for st in self.all_super_traces:
            trace = st[0] # Only grab the vertical element (represents both h and v)
            ta = trace.trace_rect
            vPOI = []
            hPOI = []
            
            # 1. Connected traces are always on the boundaries of supertrace
            # 2. Long contacts get multiple connections along supertrace
            
            # Add default edge points (at beg and end of trace)
            vPOI.append((None, ta.bottom, -1))
            vPOI.append((None, ta.top, -1))
            hPOI.append((None, ta.left, -1))
            hPOI.append((None, ta.right, -1))
            
            for conn in trace.normal_connections:
                tb = conn[0].trace_rect
                side = ta.find_contact_side(tb)
                if side == Rect.TOP_SIDE or side == Rect.BOTTOM_SIDE:
                    if conn[1] == 1 or conn[1] == 2: # Horiz. Contact
                        hPOI.append((conn[0], tb.center_x(), side))
                elif side == Rect.RIGHT_SIDE or side == Rect.LEFT_SIDE:
                    if conn[1] == 1 or conn[1] == 2:  # Vert. Contact
                        vPOI.append((conn[0], tb.center_y(), side))
                        
            # Sort vspine and hspine
            vPOI.sort(key=lambda pt: pt[1])
            hPOI.sort(key=lambda pt: pt[1])
            
            # Create mesh nodes
            horiz_len = len(hPOI)
            vert_len = len(vPOI)
            mesh_nodes = []
            for i in xrange(horiz_len):
                col = []
                for j in xrange(vert_len):
                    x = hPOI[i][1]
                    y = vPOI[j][1]
                    lumped_graph.add_node(vert_count, point=(x, y), spine=True)
                    node = vert_count
                    col.append(node)
                    vert_count += 1
                    if j > 0:
                        w1 = 0.0
                        if i-1 >= 0:
                            w1 = math.fabs(x - hPOI[i-1][1])
                        w2 = 0.0
                        if i+1 <= (horiz_len-1):
                            w2 = math.fabs(hPOI[i+1][1] - x)
                        width = 0.5*(w1 + w2)
                        length = math.fabs(y - vPOI[j-1][1])
                        lumped_graph.add_edge(node, col[j-1], {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                                                   'type': 'trace', 'width': width, 'length': length})
                        self._collect_trace_parasitic_post_eval(width, length, node, col[j-1])

                    if i > 0:
                        w1 = 0.0
                        if j-1 >= 0:
                            w1 = math.fabs(y - vPOI[j-1][1])
                        w2 = 0.0
                        if j+1 <= (vert_len-1):
                            w2 = math.fabs(vPOI[j+1][1] - y)
                        width = 0.5*(w1 + w2)
                        length = math.fabs(x - hPOI[i-1][1])
                        lumped_graph.add_edge(node, mesh_nodes[i-1][j], {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                                                 'type': 'trace', 'width': width, 'length': length})
                        self._collect_trace_parasitic_post_eval(width, length, node, mesh_nodes[i-1][j])
                        
                    # Create trace connections
                    if j == 0 and hPOI[i][2] == Rect.BOTTOM_SIDE:
                        supertrace_conn[frozenset([st, hPOI[i][0]])] = node
                        supertrace_sum += 1
                    elif j == vert_len-1 and hPOI[i][2] == Rect.TOP_SIDE:
                        supertrace_conn[frozenset([st, hPOI[i][0]])] = node
                        supertrace_sum += 1
                    if i == 0 and vPOI[j][2] == Rect.LEFT_SIDE:
                        supertrace_conn[frozenset([st, vPOI[j][0]])] = node
                        supertrace_sum += 1
                    elif i == horiz_len-1 and vPOI[j][2] == Rect.RIGHT_SIDE:
                        supertrace_conn[frozenset([st, vPOI[j][0]])] = node
                        supertrace_sum += 1
                        
                    if len(trace.long_contacts) > 0:
                        for lc in trace.long_contacts:
                            side = trace.long_contacts[lc]
                            add_node = False
                            if i == 0 and side == Rect.LEFT_SIDE:
                                add_node = True
                            elif i == horiz_len-1 and side == Rect.RIGHT_SIDE:
                                add_node = True
                            elif j == 0 and side == Rect.BOTTOM_SIDE:
                                add_node = True
                            elif j == vert_len-1 and side == Rect.TOP_SIDE:
                                add_node = True
                                
                            if add_node:
                                if frozenset([lc, st]) in long_conn:
                                    conn_list = long_conn[frozenset([lc, st])]
                                    conn_list.append((node, i, j, side)) # append the mesh node indices too, need this info later on
                                else:
                                    conn_list = []
                                    conn_list.append((node, i, j, side)) # append the mesh node indices too, need this info later on
                                    long_conn[frozenset([lc, st])] = conn_list
                                    long_sum += 1
                mesh_nodes.append(col)
        
        # Ids to help sort out different POI cases
        DEVICE_POI = 1
        BAR_LEAD_POI = 2
        RND_LEAD_POI = 3
        TRACE_POI = 4
        BW_POI = 5
        TRACE_TRACE_BW_POI = 6
        SUPER_POI = 7
        LONG_POI = 8
        
        # Handle normal trace elements
        for trace in self.all_trace_lines:
            ta = trace.trace_rect
            trace_data = [trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil]
            if not trace.is_supertrace():
                POI = [] # Points of Interest (type, destination object, spine point, overlap)
                for child in trace.child_pts:
                    if isinstance(child.tech, Lead):
                        if child.tech.lead_type == Lead.BUSBAR:
                            # Add busbar type leads
                            if trace.element.vertical:
                                POI.append((BAR_LEAD_POI, child, (ta.center_x(), child.center_position[1])))
                            else:
                                POI.append((BAR_LEAD_POI, child, (child.center_position[0], ta.center_y())))
                        elif child.tech.lead_type == Lead.ROUND:
                            # Add round type leads
                            if trace.element.vertical:
                                POI.append((RND_LEAD_POI, child, (ta.center_x(), child.center_position[1])))
                            else:
                                POI.append((RND_LEAD_POI, child, (child.center_position[0], ta.center_y())))
                    elif isinstance(child.tech, DeviceInstance):
                        # Add devices
                        POI.append((DEVICE_POI, child, child.center_position))
                        
                for bw in trace.conn_bonds:
                    # Add bondwires
                    if (bw.land_pt is not None) and (bw.land_pt2 is None):
                        # bondwire connects device to trace
                        poi_type = BW_POI
                    elif (bw.land_pt is not None) and (bw.land_pt2 is not None):
                        # bondwire connects trace to trace
                        poi_type = TRACE_TRACE_BW_POI
                            
                    if trace.element.vertical:
                        POI.append((poi_type, bw, (ta.center_x(), bw.land_pt[1])))
                    else:
                        POI.append((poi_type, bw, (bw.land_pt[0], ta.center_y())))
                        
                for conn in trace.trace_connections:
                    # Ignore connections at supertrace boundaries.
                    # These are handled by the supertrace connection system
                    # Long contacts break the space between a trace and supertrace though
                    # so these connections should be handled as a normal connection
                    bound_conn = (frozenset([conn, trace]) in self.boundary_connections)
                    if not(conn.is_supertrace()) and not(bound_conn):
                        tb = conn.trace_rect
                        side = ta.find_contact_side(tb)
                        
                        ortho = trace.element.vertical ^ conn.element.vertical
                        if trace.element.vertical:
                            # if connection is top or bottom: place point at middle of connection trace
                            if side == Rect.TOP_SIDE:
                                POI.append((TRACE_POI, conn, (ta.center_x(), ta.top), ortho))
                            elif side == Rect.BOTTOM_SIDE:
                                POI.append((TRACE_POI, conn, (ta.center_x(), ta.bottom), ortho))
                            # if connection is left or right: place point at left/right
                            elif side == Rect.RIGHT_SIDE or side == Rect.LEFT_SIDE:
                                POI.append((TRACE_POI, conn, (ta.center_x(), tb.center_y()), ortho))
                        else:
                            # if connection is top or bottom: place point at middle of connection trace
                            if side == Rect.TOP_SIDE or side == Rect.BOTTOM_SIDE:
                                POI.append((TRACE_POI, conn, (tb.center_x(), ta.center_y()), ortho))
                            # if connection is left or right: place point at left/right
                            elif side == Rect.RIGHT_SIDE:
                                POI.append((TRACE_POI, conn, (ta.right, ta.center_y()), ortho))
                            elif side == Rect.LEFT_SIDE:
                                POI.append((TRACE_POI, conn, (ta.left, ta.center_y()), ortho))
                # End for Conn Trace
                
                # Add supertrace connection points
                # Add long contact connections points
                for superconn in trace.super_connections:
                    if frozenset([superconn[0], trace]) in supertrace_conn:
                        node = supertrace_conn[frozenset([superconn[0], trace])]
                        supertrace_sum -= 1
                        pt = lumped_graph.node[node]['point']
                        POI.append((SUPER_POI, superconn[0], pt))
                    elif frozenset([superconn[0], trace]) in long_conn:
                        conn_list = long_conn[frozenset([superconn[0], trace])]
                        long_sum -= 1
                        for info in conn_list:
                            node, i, j, side = info
                            pt = lumped_graph.node[node]['point']
                            POI.append((LONG_POI, superconn[0], pt, node, i, j, side))
                
                # Sort the POI
                if trace.element.vertical:
                    POI.sort(key=lambda pt: pt[2][1])
                else:
                    POI.sort(key=lambda pt: pt[2][0])
                    
                nprev = None
                for pt in POI:
                    if pt[0] == DEVICE_POI:
                        # Add device node
                        attrib = {'point':pt[2], 'type':'device', 'obj':pt[1]}
                        node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                        pt[1].lumped_node = node

                        # Connect device and bondwire node
                        for bw in pt[1].sym_bondwires:
                            if frozenset([bw, pt[1]]) in wire_dev_dict:
                                bw_node = wire_dev_dict[frozenset([bw, pt[1]])]
                                ind, res, cap = self._bondwire_eval(bw_node, node, trace_data, bw,1)
                                if bw.tech.wire_type == BondWire.POWER:
                                    bw_type = 'bw power'
                                elif bw.tech.wire_type == BondWire.SIGNAL:
                                    bw_type = 'bw signal'
                                    
                                lumped_graph.add_edge(bw_node, node, {'ind': 1.0/ind, 'res':1.0/res, 'cap':1.0/cap,
                                                                      'type':bw_type, 'obj':bw})
                                bw_sum -= 1
                            else:
                                # Add the device node (so bw code will find it)
                                wire_dev_dict[frozenset([bw, pt[1]])] = node
                                bw_sum += 1
                    elif pt[0] == BAR_LEAD_POI:
                        # Add busbar lead nodes
                        attrib = {'point':pt[2]}
                        node, vert_count = self._add_node(lumped_graph, vert_count, attrib) # add spine node
                        attrib = {'type':'lead', 'point':pt[1].center_position, 'obj':pt[1]}
                        lead_node, vert_count = self._add_node(lumped_graph, vert_count, attrib) # add lead node
                        # Add connection edge for trace to lead from spine
                        lumped_graph=self._lead_trace_path_eval(lead_node, node, trace_data, pt[1],lumped_graph)
                        pt[1].lumped_node = lead_node # used for measurement
                    elif pt[0] == RND_LEAD_POI:
                        # Add round lead nodes
                        if distance(pt[2], pt[1].center_position) < 0.1:
                            # if close enough, treat node as direct connection to spine
                            attrib = {'point':pt[2], 'type':'lead', 'obj':pt[1]}
                            node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                            pt[1].lumped_node = node
                        else:
                            attrib = {'point':pt[2]}
                            node, vert_count = self._add_node(lumped_graph, vert_count, attrib) # add spine node
                            attrib = {'type':'lead', 'point':pt[1].center_position, 'obj':pt[1]}
                            lead_node, vert_count = self._add_node(lumped_graph, vert_count, attrib) # add lead node
                            # Add connection edge for trace to lead from spine
                            lumped_graph=self._lead_trace_path_eval(lead_node, node,trace_data, pt[1],lumped_graph)
                            pt[1].lumped_node = lead_node # used for measurement
                    elif pt[0] == TRACE_POI:
                        # Add trace node
                        ortho = pt[3]
                        if ortho:
                            node, vert_count = self._add_node(lumped_graph, vert_count, {'point':pt[2]})
                            if frozenset([pt[1], trace]) in conn_dict:
                                conn_node = conn_dict[frozenset([pt[1], trace])]
                                lumped_graph=self._trace_conn_path_eval(conn_node, node, trace_data, pt[1],lumped_graph)
                                conn_sum -= 1
                            else: # Add node to conn_dict and the connection will be found next time
                                conn_dict[frozenset([pt[1], trace])] = node
                                conn_sum += 1
                        else:
                            # Check if a node has already been added
                            if frozenset([trace, pt[1]]) in overlap_pts:
                                node = overlap_pts[frozenset([trace, pt[1]])]
                                overlap_sum -= 1
                            else: # If not added yet, add it
                                node, vert_count = self._add_node(lumped_graph, vert_count, {'point':pt[2]})
                                overlap_pts[frozenset([trace, pt[1]])] = node
                                overlap_sum += 1
                    elif pt[0] == BW_POI:
                        wire = pt[1]
                        node, vert_count = self._add_node(lumped_graph, vert_count, {'point':pt[2]}) # spine node
                        bw_node, vert_count = self._add_node(lumped_graph, vert_count, {'point':wire.land_pt}) # bw landing node
                        
                        # Add connection edge from spine to bondwire landing
                        num_wires = len(wire.end_pts) # count bondwires
                        lumped_graph=self._bondwire_to_spine_eval(node, bw_node, trace_data, num_wires, wire.tech.eff_diameter(),lumped_graph)
                        # Check for device to bondwire connection
                        if frozenset([wire, wire.device]) in wire_dev_dict:
                            dev_node = wire_dev_dict[frozenset([wire, wire.device])]
                            ind, res, cap = self._bondwire_eval(bw_node, dev_node, trace_data, wire,num_wires)
                            if bw.tech.wire_type == BondWire.POWER:
                                bw_type = 'bw power'
                            elif bw.tech.wire_type == BondWire.SIGNAL:
                                bw_type = 'bw signal'
                            lumped_graph.add_edge(bw_node, dev_node, {'ind': 1.0/ind, 'res':1.0/res, 'cap':1.0/cap,
                                                                      'type':bw_type, 'obj':bw})
                            bw_sum -= 1
                        else: # Add to connection dict and add edge in device POI
                            wire_dev_dict[frozenset([wire, wire.device])] = bw_node
                            bw_sum += 1
                    elif pt[0] == TRACE_TRACE_BW_POI:
                        wire = pt[1]
                        # Determine correct landing point
                        if wire.start_pt_conn is trace:
                            land_pt = wire.land_pt # landing point 1 is on this trace
                        else:
                            land_pt = wire.land_pt2 # landing point 2 is on this trace
                        
                        node, vert_count = self._add_node(lumped_graph, vert_count, {'point':pt[2]})  # spine node
                        bw_node, vert_count = self._add_node(lumped_graph, vert_count, {'point':land_pt}) # bw landing node
                        
                        # Add connection edge from spine to bondwire landing
                        num_wires = len(wire.end_pts) # count bondwires
                        lumped_graph=self._bondwire_to_spine_eval(node, bw_node, trace_data, num_wires, wire.tech.eff_diameter(),lumped_graph)
                        
                        # Connecting to node on the other trace (use wire_wire_dict)
                        # Check for trace to trace (other end of bondwire) connection node
                        # eg: (node A).---wire----.(node B)
                        if frozenset([wire]) in wire_wire_dict:
                            # Found the partner node
                            bw_node2 = wire_wire_dict[frozenset([wire])]
                            ind, res, cap = self._bondwire_eval(bw_node, bw_node2, trace_data, wire,num_wires)
                            if bw.tech.wire_type == BondWire.POWER:
                                bw_type = 'bw power'
                            elif bw.tech.wire_type == BondWire.SIGNAL:
                                bw_type = 'bw signal'
                            lumped_graph.add_edge(bw_node, bw_node2, {'ind': 1.0/ind, 'res':1.0/res, 'cap':1.0/cap,
                                                                      'type':bw_type, 'obj':bw})
                            bw_sum -= 1
                        else: # Add to connection dict
                            wire_wire_dict[frozenset([wire])] = bw_node
                            bw_sum += 1
                    elif pt[0] == SUPER_POI:
                        node = supertrace_conn[frozenset([pt[1], trace])]
                    elif pt[0] == LONG_POI:
                        id, supertrace, point, conn_node, i, j, side = pt
                        # Create new spine points (and connect them)
                        if trace.element.vertical:
                            new_pt = (ta.center_x(), point[1])
                        else:
                            new_pt = (point[0], ta.center_y())
                        node, vert_count = self._add_node(lumped_graph, vert_count, {'point':new_pt})
                        
                        # find width of connecting edge, find the one deep internal edge inside the supertrace
                        # this will give the width of the connecting edge
                        if side == Rect.TOP_SIDE:      a=0; b=-1
                        elif side == Rect.BOTTOM_SIDE: a=0; b=1
                        elif side == Rect.RIGHT_SIDE:  a=-1; b=0
                        elif side == Rect.LEFT_SIDE:   a=1; b=0
                        boundary_node = mesh_nodes[i][j]
                        internal_node = mesh_nodes[i+a][j+b]
                        width = lumped_graph[boundary_node][internal_node]['width']
                        length = distance(new_pt,point)
                        lumped_graph.add_edge(conn_node, node,
                                              {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                               'type': 'trace', 'width': width, 'length': length})
                        self._collect_trace_parasitic_post_eval(width, length, conn_node, node)
                        
                    # Add spine edge
                    if nprev is not None:
                        lumped_graph=self._spine_path_eval(nprev, node, trace_data,lumped_graph)
                    nprev = node
        # End For Trace
        
        # Make sure the dictionary connection systems are working
        msg = "Trace connection error during lumped element graph generation."
        assert conn_sum == 0, msg
        
        msg = "Not all overlapping nodes determined during lumped element graph generation."
        assert overlap_sum == 0, msg
        
        msg = "Not all bondwire connections found during lumped element graph generation."
        assert bw_sum == 0, msg
        
        msg = "Not all trace to trace bondwire connections found during lumped element graph generation."
        assert ww_sum == 0, msg
        
        msg = "Not all supertrace connections were linked during lumped element graph generation."
        assert supertrace_sum == 0, msg
        
        msg = "Not all long contact supertrace connections were linked during lumped element graph generation."
        assert long_sum == 0, msg
        self._build_lumped_edges(trace_data, lumped_graph)

    def _add_node(self, graph, vert_count, attrib):
        # point spine
        graph.add_node(vert_count, attr_dict=attrib)
        nodeout = vert_count
        vert_count += 1
        return nodeout, vert_count

    def _spine_path_eval(self, n1, n2, trace_data,lumped_graph):
        # trace_data = (trace, metal thickness, iso thickness, lumped_graph)
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']
        if trace_data[0].element.vertical:
            width = trace_data[0].trace_rect.width()
            length = math.fabs(pt2[1] - pt1[1])
        else:
            width = trace_data[0].trace_rect.height()
            length = math.fabs(pt2[0] - pt1[0])
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1, 'res': 1.0 / 1, 'cap': 1.0 / 1,
                               'type': 'trace', 'width': width, 'length': length})
        self._collect_trace_parasitic_post_eval(width, length, n1, n2)
        return lumped_graph

    def _trace_conn_path_eval(self, n1, n2, trace_data, conn_trace,lumped_graph):
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']

        main = None  # main trace
        conn = None  # connecting trace
        # Determine which trace is ortho. to conn. direction
        if pt1[0] == pt2[0]:
            # Conn. is vertical
            if conn_trace.element.vertical:
                conn = conn_trace
                main = trace_data[0]
            else:
                conn = trace_data[0]
                main = conn_trace
        else:
            # Conn. is horizontal
            if not conn_trace.element.vertical:
                conn = conn_trace
                main = trace_data[0]
            else:
                conn = trace_data[0]
                main = conn_trace

        if main.element.vertical:
            width = conn.trace_rect.height()
            length = math.fabs(pt2[0] - pt1[0])
        else:
            width = conn.trace_rect.width()
            length = math.fabs(pt2[1] - pt1[1])
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1, 'res': 1.0 / 1, 'cap': 1.0 / 1,
                               'type': 'trace', 'width': width, 'length': length})
        self._collect_trace_parasitic_post_eval(width, length, n1, n2)
        return lumped_graph
    def _lead_trace_path_eval(self, n1, n2,trace_data,lead,lumped_graph):
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']
        if trace_data[0].element.vertical:
            length = math.fabs(pt2[0] - pt1[0])
        else:
            length = math.fabs(pt2[1] - pt1[1])

        width = lead.tech.dimensions[0]
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1, 'res': 1.0 / 1, 'cap': 1.0 / 1,
                               'type': 'trace', 'width': width, 'length': length})
        self._collect_trace_parasitic_post_eval(width, length, n1, n2)
        return lumped_graph

    def _bondwire_to_spine_eval(self, n1, n2, trace_data, num_wires, wire_eff_diam, lumped_graph):
        trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil = trace_data
        pt1 = lumped_graph.node[n1]['point']
        pt2 = lumped_graph.node[n2]['point']
        path_length = distance(pt1, pt2)

        width = num_wires * wire_eff_diam
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1, 'res': 1.0 / 1, 'cap': 1.0 / 1,
                               'type': 'trace', 'width': width, 'length': path_length})
        self._collect_trace_parasitic_post_eval(width, path_length, n1, n2)
        return lumped_graph

    def _bondwire_eval(self, n1, n2, trace_data, bw,num_wires):
        wire_radius = 0.5*bw.tech.eff_diameter()
        resist = bw.tech.properties.electrical_res
        inv_ind = 0.0
        inv_res = 0.0
        b = bw.tech.b
        a = bw.tech.a
        for pt1, pt2 in zip(bw.start_pts, bw.end_pts):
            D = distance(pt1, pt2)
            l1=D- b
            length=a+b+l1/math.cos(math.atan(2*a/l1))
            wire_ind = wire_inductance(length, wire_radius)/num_wires
            wire_res = wire_resistance(trace_data[4], length, wire_radius, resist)/num_wires
            inv_res += 1.0/wire_res
            inv_ind += 1.0/wire_ind
            
        return 1.0/inv_ind, 1.0/inv_res, 1e-3

    def _build_lumped_edges(self,trace_data,lumped_graph):
        w_all=[]
        l_all=[]
        t_num=len(self.trace_info) # number of traces
        if self.mdl_type=='RS':
            for w,l in self.trace_info:
                w_all.append(w)
                l_all.append(l)
            ind1 = trace_ind_krige(trace_data[4],w_all, l_all,self.LAC_mdl).tolist()
            res1 = trace_res_krige(trace_data[4], w_all, l_all,self.RAC_mdl).tolist()
            print res1
            cap1 = trace_cap_krige(w_all, l_all, self.C_mdl).tolist()
            for i in range(t_num):
                nodes=self.trace_nodes[i]
                lumped_graph[nodes[0]][nodes[1]]['ind']=1/ind1[i]
                lumped_graph[nodes[0]][nodes[1]]['res']=1/res1[i]
                lumped_graph[nodes[0]][nodes[1]]['cap']=1/cap1[i]
        elif self.mdl_type=='MS':
            for i in range(t_num):
                nodes = self.trace_nodes[i]
                [w, l] = self.trace_info[i]
                l,r,c = self._eval_parasitic_models(w, l, trace_data)
                lumped_graph[nodes[0]][nodes[1]]['ind'] = 1 / l
                lumped_graph[nodes[0]][nodes[1]]['res'] = 1 / r
                lumped_graph[nodes[0]][nodes[1]]['cap'] = 1 / c
        self.lumped_graph=lumped_graph

    def _collect_trace_parasitic_post_eval(self,width,length,node_l,node_r):
        self.trace_info.append([width,length])
        nodes=[node_l, node_r]
        self.trace_nodes.append(nodes)

    def _eval_parasitic_models(self, width, length, trace_data):
        ind = trace_inductance(width, length, trace_data[1], trace_data[2])
        res = trace_resistance(trace_data[4], width, length, trace_data[1], trace_data[2], trace_data[5])
        cap = trace_capacitance(width, length, trace_data[1], trace_data[2], trace_data[6])
        return ind, res, cap
    
    def _eval_supertrace_parasitic_models(self, width, length, thickness, sub_thick, freq, resist, sub_epsil):
        ind = trace_inductance(width, length, thickness, sub_thick)
        res = trace_resistance(freq, width, length, thickness, sub_thick, resist)
        cap = trace_capacitance(width, length, thickness, sub_thick, sub_epsil)
        return ind, res, cap
    
    def prepare_for_pickle(self):
        # Remove complex optimization object before pickling
        if hasattr(self, 'solutions'):
            del self.solutions
            
        if hasattr(self, 'opt_progress_fn'):
            del self.opt_progress_fn
    '''----------------------------------------------------------------------------------------------------'''    
#-----------------------------------------------------
#--------------- Test Case Functions -----------------
#-----------------------------------------------------

def make_test_symmetries(sym_layout):
    for i in xrange(1,11):
        symm = []
        for obj in sym_layout.all_sym:
            if obj.element.path_id.count('s'+str(i)) > 0:
                symm.append(obj)
                
        if len(symm) > 0:
            sym_layout.symmetries.append(symm)

def make_test_constraints(symbols):
    for obj in symbols:
        if obj.element.path_id.count('c1') > 0:
            obj.constraint = (None, None, 1.27)
        if obj.element.path_id.count('c2') > 0:
            obj.constraint = (4.8, 10.0, None)

def make_test_devices(symbols, dev):
    # symbols list of all SymLine and SymPoints in a loaded layout (sym_layout.all_sym)
    for obj in symbols:
        if obj.element.path_id.count('dev1') > 0 and isinstance(obj.element, LayoutPoint):
            obj.tech = dev
            
def make_test_leads(symbols, pow_lead, sig_lead):
    for obj in symbols:
        if obj.element.path_id.count('pow_ld') > 0 and isinstance(obj.element, LayoutPoint):
            obj.tech = pow_lead
        elif obj.element.path_id.count('sig_ld') > 0 and isinstance(obj.element, LayoutPoint):
            obj.tech = sig_lead
            
def make_test_bonds(symbols, power, signal):
    for obj in symbols:
        if 'pow_bw' in obj.element.path_id and isinstance(obj.element, LayoutLine):
            obj.make_bondwire(power)
        elif 'sig_bw' in obj.element.path_id > 0 and isinstance(obj.element, LayoutLine):
            obj.make_bondwire(signal)
            
def make_test_design_values(sym_layout, dimlist, default):
    hdv = []
    vdv = []
    dev_dv = []
    
    for i in sym_layout.h_dv_list:
        hdv.append(default)
        
    for i in sym_layout.v_dv_list:
        vdv.append(default)
        
    for i in sym_layout.devices:
        dev_dv.append(default)
    
    for sym in sym_layout.all_sym:
        if 'id' in sym.element.path_id:
            pos = sym.element.path_id.find('id')
            id = int(sym.element.path_id[pos+2:pos+2+1])
            dv = dimlist[id]
            if isinstance(sym, SymLine):
                if not sym.wire:
                    if sym.element.vertical:
                        hdv[sym.dv_index] = dv
                    else:
                        vdv[sym.dv_index] = dv
            elif isinstance(sym, SymPoint) and isinstance(sym.tech, DeviceInstance):
                dev_dv[sym.dv_index] = dv
            
    return hdv, vdv, dev_dv

def add_test_measures(sym_layout):
    pts = []
    for sym in sym_layout.all_sym:
        if 'E1' in sym.element.path_id:
            pts.append(sym)
        if len(pts) > 1:
            break
        
    if len(pts) == 2:
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100e3, "Loop Inductance")
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100e3, "Loop Resistance")
        sym_layout.perf_measures.append(m2)
        
    devices = []
    for sym in sym_layout.all_sym:
        if 'dev1' in sym.element.path_id:
            devices.append(sym)
            
    m2 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.")
    sym_layout.perf_measures.append(m2)

def make_test_setup():
    import os
    from powercad.tech_lib.test_techlib import get_power_lead, get_signal_lead
    from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
    from powercad.tech_lib.test_techlib import get_device, get_dieattach
                                        
    temp_dir = os.path.abspath(settings.TEMP_DIR)
    test_file = os.path.abspath('../../../sym_layouts/rd100.svg')
    
    sym_layout = SymbolicLayout()
    sym_layout.load_layout(test_file)
    symbols = sym_layout.all_sym
    
    dev = DeviceInstance(0.08, 10.0, get_device(), get_dieattach())
    pow_lead = get_power_lead()
    sig_lead = get_signal_lead()
    power_bw = get_power_bondwire()
    signal_bw = get_signal_bondwire()
    
    make_test_devices(symbols, dev)
    make_test_leads(symbols, pow_lead, sig_lead)
    make_test_bonds(symbols, power_bw, signal_bw)
    
    make_test_symmetries(sym_layout)
    make_test_constraints(symbols)
    
    add_test_measures(sym_layout)
    
    module = gen_test_module_data()
    print "symbolic_layout.py > make_test_setup() > temp_dir=", temp_dir
    sym_layout.form_design_problem(module, temp_dir)
    return sym_layout

def optimization_test(sym_layout):
    sym_layout.optimize(inum_gen=500)
    #return sym_layout
    
    from pylab import plot, show, figure
    f1 = []
    f2 = []
    for sol in sym_layout.solutions:
        f1.append(sol.fitness.values[0])
        f2.append(sol.fitness.values[1])
    fig1 = figure()
    plot(f1, f2, 'o')
    show()
    
    # Plot the first solution in the list
#    mid_sol = int(len(sym_layout.solutions)*0.75)
#    sym_layout.rev_map_design_vars(sym_layout.solutions[mid_sol])
#    sym_layout.generate_layout()
#    plot_layout(sym_layout)
            
def build_test_layout():
    from powercad.sym_layout.plot import plot_layout
    
    sym_layout = make_test_setup()
    sym_layout.debug_single_eval()
    print sym_layout.passes_drc(True)
    
    lg = sym_layout.lumped_graph
    if lg is not None:
        test_pts = []
        pos_data = {}
        for node in lg.nodes(data = True):
            test_pts.append(node[1]['point'])
            pos_data[node[0]] = node[1]['point']
                    
        nx.draw(lg, pos=pos_data, hold=True, node_size=200)
        plot_layout(sym_layout)
    
    return sym_layout

def test_pickle_symbolic_layout():
    sym_layout = make_test_setup()
    sym_layout.optimize(inum_gen=10)
    
    f = open(r'C:\Users\bxs003\Desktop\sym_layout.p', 'w')
    pickle.dump(sym_layout, f)
    f.close()
    del sym_layout
    
    f = open(r'C:\Users\bxs003\Desktop\sym_layout.p', 'r')
    sym_layout = pickle.load(f)
    f.close()
    
    from pylab import plot, show
    f1 = []
    f2 = []
    for sol in sym_layout.solutions:
        f1.append(sol.fitness.values[0])
        f2.append(sol.fitness.values[1])
    plot(f1, f2, 'o')
    show()

if __name__ == '__main__':
    sym_layout = make_test_setup()
    build_test_layout()
    #optimization_test(sym_layout)
    #sym_layout = build_test_layout()
    #test_pickle_symbolic_layout()
    