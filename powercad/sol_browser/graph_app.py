'''
Created on March 6, 2012

@author: shook, mukherjee, qmle
'''

import sys
import operator
import networkx as nx
import matplotlib.pyplot as plt
from PySide import QtCore, QtGui

import powercad.sym_layout.plot as plot
#from matplotlib.sphinxext.plot_directive import align # SM - unused import
#plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'

import numpy as npy
import matplotlib
#matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT  as NavigationToolbar

from mpl_toolkits.mplot3d import Axes3D

from graphing_form import Ui_GrapheneWindow
from objective_widget import ObjectiveWidget
from powercad.sol_browser.solution import Solution
from powercad.sol_browser.solution_lib import SolutionLibrary

from powercad.sym_layout.plot import plot_layout
from powercad.electro_thermal.ElectroThermal_toolbox import ET_analysis
from powercad.spice_handler.spice_export.thermal_netlist_graph import Module_Full_Thermal_Netlist_Graph
from powercad.export.py_csv import py_csv 

class GrapheneWindow(QtGui.QMainWindow):
    def __init__(self, parent):
        # set up main window
        QtGui.QMainWindow.__init__(self, None)
        self.ui = Ui_GrapheneWindow()
        self.ui.setupUi(self)
        
        # used for saving out solutions
        self.parent = parent
        self.sym_layout = parent.project.symb_layout
        self.solution_library = parent.project.symb_layout.solution_lib
        self.sol_count = 0
        
        # used for graph
        self.graph_axis = {}
        self.x_axis = None
        self.y_axis = None
        
        # Temporary layout plot storage
        self.ax = None
        
        # Create vertical layout for objectives listing
        self.objective_layout = QtGui.QVBoxLayout()
        self.ui.scrollAreaWidgetContents.setLayout(self.objective_layout)
        
        # create an widget object for each objective
        self.obj_widg = []
        for i in range(len(self.solution_library.measure_data)):
            self.obj_widg.append(ObjectiveWidget(self.solution_library.measure_names_units[i],
                                                 self.solution_library.measure_data[i], i,
                                                 self.ui.scrl_objectivesWindow, self))
            self.objective_layout.addWidget(self.obj_widg[i])
        
        # set up initial graph axis
        if len(self.obj_widg) >= 1:
            self.graph_axis['x'] = self.obj_widg[0]
            self.graph_axis['x'].chkbox_dict['x'].setCheckState(QtCore.Qt.Checked)
            if len(self.obj_widg) >= 2:
                self.graph_axis['y'] = self.obj_widg[1]
                self.graph_axis['y'].chkbox_dict['y'].setCheckState(QtCore.Qt.Checked)
                if len(self.obj_widg) >= 3:
                    self.graph_axis['z'] = self.obj_widg[2]
                    self.graph_axis['z'].chkbox_dict['z'].setCheckState(QtCore.Qt.Checked)
                else:
                    self.graph_axis['z'] = None
            else:
                self.graph_axis['y'] = None
        else:
            self.graph_axis['x'] = None
            
        # set up graphing area
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # set up preview area
        self.preview_figure = Figure()
        self.preview_canvas = FigureCanvas(self.preview_figure)
        self.ui.preview_layout = QtGui.QGridLayout(self.ui.gfx_layoutPreview)
        self.ui.preview_layout.setContentsMargins(0,0,0,0)
        self.ui.preview_layout.addWidget(self.preview_canvas,0,0,1,1)

        # set up matplot widget and navbar widget
        self.ui.plot_layout = QtGui.QGridLayout(self.ui.plot_widget)
        self.ui.plot_layout.setContentsMargins(0,0,0,0)
        self.ui.plot_layout.addWidget(self.canvas,0,0,1,1)
        self.ui.nav_layout = QtGui.QGridLayout(self.ui.navbar_widget)
        self.ui.nav_layout.setContentsMargins(0,0,0,0)
        self.ui.nav_layout.addWidget(self.toolbar,0,0,1,1)
    
        # used to map displayed data points to original data set
        self.disp_data_indx_map = []
    
        # draw graph
        self.filter_graph()
        self.filter_graph2()

        # connect actions to methods
        self.canvas.mpl_connect('pick_event', self.select_solution)
        self.ui.bnt_saveLayout.pressed.connect(self.save_solution)
        self.ui.btn_export_csv.pressed.connect(self.save_solution_set)
        #self.ui.Electro_Thermal_btn.pressed.connect(self.test_ET)
        # Setup selected solution objective values
        self.obj_values_model = ObjectiveValuesTableModel(self)
        self.ui.objective_values_table.setModel(self.obj_values_model)
    '''     
    # Called when an x, y, or z checkbox is clicked    
    # This is the original method. A duplicate called set_graph_axis() was created to test what happens when no boxes are checked.
    # NOTE: THIS METHOD IS NEVER CALLED IN GRAPH_APP
    def set_graph_axis2(self, objective, axis):
        # if the check box got checked
        if objective.chkbox_dict[axis].isChecked() is True:
            # if there is already another objective on this axis
            if self.graph_axis[axis] is not None:
                # uncheck old objective's checkbox
                self.graph_axis[axis].chkbox_dict[axis].setCheckState(QtCore.Qt.Unchecked)
            #if there is already an axis assigned for this objective
            for i in objective.chkbox_dict:
                if objective.chkbox_dict[i].isChecked() is True:
                    # uncheck it
                    objective.chkbox_dict[i].setCheckState(QtCore.Qt.Unchecked)
                    # remove it from the axis list
                    self.graph_axis[i] = None
            # assign this objective to the axis
            self.graph_axis[axis] = objective
            # check the checkbox
            objective.chkbox_dict[axis].setCheckState(QtCore.Qt.Checked)
        else:
            self.graph_axis[axis] = None
        # redraw the graph
        self.draw_graph()
    '''
    # Called when an x, y, or z checkbox is clicked. This is a duplicate of set_graph_axis2() to test what happens when no boxes are checked.
    # NOTE: THIS METHOD IS NEVER CALLED IN GRAPH_APP.PY; It is called from objective_widget.py
    def set_graph_axis(self, objective, axis):
        #print axis, objective.name_units[0]
        print "graph axis (previous state): ", "x", self.graph_axis['x'].name_units[0] if self.graph_axis['x'] is not None else "none", "y", self.graph_axis['y'].name_units[0] if self.graph_axis['y'] is not None else "none", "z", self.graph_axis['z'].name_units[0] if self.graph_axis['z'] is not None else "none"
        # if the check box got checked
        if objective.chkbox_dict[axis].isChecked() is True:            
            # if there is already another objective on this axis
            if self.graph_axis[axis] is not None: # CHECKING PREVIOUS STATE
                # uncheck old objective's checkbox
                self.graph_axis[axis].chkbox_dict[axis].setCheckState(QtCore.Qt.Unchecked)
                ''' self.graph_axis[axis] = objective '''
            # if there is already an axis assigned for this objective
            for i in objective.chkbox_dict:
                if objective.chkbox_dict[i].isChecked() is True:
                    # uncheck it
                    objective.chkbox_dict[i].setCheckState(QtCore.Qt.Unchecked)
                    # remove it from the axis list
                    self.graph_axis[i] = None
            # assign this objective to the axis
            self.graph_axis[axis] = objective
            # check the checkbox
            objective.chkbox_dict[axis].setCheckState(QtCore.Qt.Checked)
        # if the check box got unchecked
        elif objective.chkbox_dict[axis].isChecked() is False:
            # uncheck it
            objective.chkbox_dict[axis].setCheckState(QtCore.Qt.Unchecked)
            # remove it from the axis list
            self.graph_axis[axis] = None
            #print "graph axis (new state): ", "x", self.graph_axis['x'].name_units[0] if self.graph_axis['x'] is not None else "none", "y", self.graph_axis['y'].name_units[0] if self.graph_axis['y'] is not None else "none", "z", self.graph_axis['z'].name_units[0] if self.graph_axis['z'] is not None else "none"
            # count how many axes are already assigned
        n = 0
        for i in self.graph_axis:
            if self.graph_axis[i] is not None:
                n += 1
        # if less than 2 axes have been assigned
        if n<2:
            # clear graph
            print "clearing graph..."
            self.figure.clear()
            # add empty subplot
            self.figure.add_subplot(111)
            # add text at specified coordinates # FIND A WAY TO CENTER THE TEXT (currently hard coded)
            self.figure.text(0.3, 0.5, "Select at least two performance parameters.")
            #self.figure.suptitle("Select at least two performance parameters.") # ADDS TEXT ABOVE THE GRAPH (CENTERED)
            # draw canvas as specified above (blank plot with text)
            self.canvas.draw() 
            print "graph cleared."
        else:
            # redraw the graph
            self.draw_graph()
            print "new graph drawn."
        print "graph axis (new state): ", "x", self.graph_axis['x'].name_units[0] if self.graph_axis['x'] is not None else "none", "y", self.graph_axis['y'].name_units[0] if self.graph_axis['y'] is not None else "none", "z", self.graph_axis['z'].name_units[0] if self.graph_axis['z'] is not None else "none"
            
    def save_2D_paretofront_solutions(self):
        print 'here'    
    def draw_graph(self):
        #clear figure
        self.figure.clear()
        # draw a 2D or 3D graph accordingly
        if (self.graph_axis['x'] is None):
            self.x_axis = self.graph_axis['y']
            self.y_axis = self.graph_axis['z']
            self.draw_graph_2D()
        elif (self.graph_axis['y'] is None):
            self.x_axis = self.graph_axis['x']
            self.y_axis = self.graph_axis['z']
            self.draw_graph_2D()
        elif (self.graph_axis['z'] is None):
            self.x_axis = self.graph_axis['x']
            self.y_axis = self.graph_axis['y']
            self.draw_graph_2D()
        else:
            self.draw_graph_3D()
        # draw graph
        self.canvas.draw()
        
    def draw_graph_2D(self):
        # plot data
        self.axes = self.figure.add_subplot(111)
        #[P_X,P_Y]=self.pareto_frontiter2D(self.x_axis.displayable_data, self.y_axis.displayable_data, MinX=True, MinY=True)
        self.axes.scatter(self.x_axis.displayable_data, self.y_axis.displayable_data, picker=1)
        #self.axes.scatter(P_X, P_Y, picker=1)
        
        
        # set limits
        self.axes.set_xlim(self.x_axis.position - (self.x_axis.envelope / 2),
                           self.x_axis.position + (self.x_axis.envelope / 2))
        self.axes.set_ylim(self.y_axis.position - (self.y_axis.envelope / 2),
                           self.y_axis.position + (self.y_axis.envelope / 2))
        # plot data
        try:
            self.axes.scatter(self.x_axis.displayable_data, self.y_axis.displayable_data, picker=1, marker='D', c='b')
            sel_point = self.sel_ind
            #print 'sel_point', sel_point
            self.axes.scatter(self.x_axis.displayable_data[sel_point], self.y_axis.displayable_data[sel_point], picker=1, marker='D', c='r',s=100)
        #[P_X,P_Y]=self.pareto_frontiter2D(self.x_axis.displayable_data, self.y_axis.displayable_data, MinX=True, MinY=True)

        #self.axes.scatter(P_X, P_Y, picker=1)

        except:
            self.axes.scatter(self.x_axis.displayable_data, self.y_axis.displayable_data, picker=1, marker='o', c='b')

        # set labels
        self.axes.set_xlabel(self.x_axis.name_units[0] + " (" + self.x_axis.name_units[1] + ")")
        self.axes.set_ylabel(self.y_axis.name_units[0] + " (" + self.y_axis.name_units[1] + ")") 
        '''
        for point in range(len(P_X)):
            self.sol_params = [[objective.name_units[0],objective.name_units[1],objective.data[self.disp_data_indx_map[point]]] 
                           for objective in self.obj_widg]
            self.obj_values_model.set_table(self.sol_params)
           
        # draw layout preview
            self.sol_index = self.disp_data_indx_map[point]
            self.draw_layout_preview(self.sol_index)
        '''

    def draw_graph_3D(self):
        # plot data
#        self.axes = self.figure.add_subplot(111, projection='3d')
        self.axes = Axes3D(self.figure)
        try:
            self.axes.scatter(self.graph_axis['x'].displayable_data, self.graph_axis['y'].displayable_data,
                              self.graph_axis['z'].displayable_data, picker=1)
            sel_point=self.sel_ind
            self.axes.scatter(self.graph_axis['x'].displayable_data[sel_point],
                              self.graph_axis['y'].displayable_data[sel_point],
                              self.graph_axis['z'].displayable_data[sel_point], picker=1, c='r',marker='D',s=100)
        except:
            self.axes.scatter(self.graph_axis['x'].displayable_data, self.graph_axis['y'].displayable_data,
                              self.graph_axis['z'].displayable_data, picker=1)

        # set limits
        self.axes.set_xlim(self.graph_axis['x'].min-1, self.graph_axis['x'].max+1)
        self.axes.set_ylim(self.graph_axis['y'].min-1, self.graph_axis['y'].max+1)
        self.axes.set_zlim(self.graph_axis['z'].min-1, self.graph_axis['z'].max+1)
        # set labels
        self.axes.set_xlabel(self.graph_axis['x'].name_units[0] + " (" + self.graph_axis['x'].name_units[1] + ")")
        self.axes.set_ylabel(self.graph_axis['y'].name_units[0] + " (" + self.graph_axis['y'].name_units[1] + ")")
        self.axes.set_zlabel(self.graph_axis['z'].name_units[0] + " (" + self.graph_axis['z'].name_units[1] + ")")
        
#    Trying numpy arrays to make faster    
#    def filter_graph(self):
#        self.data_array = npy.zeros(5, dtype=([('x',npy.float64,(1,1)),('y',npy.float64,(1,1)),('z',npy.float64,(1,1))]))
#        self.data_array['x'][0] = self.graph_axis['x']
#        print self.data_array
#        
#    def filter_graph2(self):
#        print 'filter2'
    def test_ET(self):
        self.solution = Solution()
        self.solution.index = self.sol_index
        self.solution.params = self.sol_params  
        thermal_netlist_graph = Module_Full_Thermal_Netlist_Graph('dont care', self.sym_layout, self.solution.index)
        T_list= self.sym_layout._thermal_analysis(4).tolist()
        #print T_list
        T_list=(x[0][0] for x in T_list)
        
        electrothermal=ET_analysis(thermal_netlist_graph)
        thermal_mdl=electrothermal.ET_formation_1(20e3)
        filedes='C:\Users\qmle\Desktop\Transistors_data\cpmf_1200_0080B'
        rds_fn='Rdson.csv'
        crss_fn='Crss.csv'
        vth_fn='Vth.csv'
        parameters=electrothermal.curve_fitting_all(filedes, rds_fn, crss_fn,vth_fn)
        electrothermal.Run_sim(thermal_mdl , parameters, 300000)
        #print electrothermal.ptot_all(T_list, parameters)  
    def filter_graph(self):
        for objective in self.obj_widg:
            # clear all old points
            objective.displayable_data = []
            self.disp_data_indx_map = []
            # filter data inside objective
            objective.bool_data = map(objective.filter_point,objective.data)
            
    def filter_graph2(self):
        for data_point in range(0,self.obj_widg[0].data_size):
            # add displayable data points to list
            if any(objective.bool_data[data_point] is False for objective in self.obj_widg):
                None
            else:
                for objective in self.obj_widg:
                    objective.displayable_data.append(objective.data[data_point])
                self.disp_data_indx_map.append(data_point)
            
        # redraw graph
        self.draw_graph()
    def pareto_frontiter2D(self,X,Y,MinX=True,MinY=True):
        #Display only the pareto front solution
        data_list=sorted([[X[i], Y[i]] for i in range(len(X))], reverse=not(MinX))
        p_front=[data_list[0]]
        for pair in data_list[1:]:
            if MinY: 
                if pair[1] <= p_front[-1][1]: # Look for higher values of Y
                    p_front.append(pair) # and add them to the Pareto frontier
            else:
                if pair[1] >= p_front[-1][1]: # Look for lower values of Y
                    p_front.append(pair) # and add them to the Pareto frontie
        p_frontX = [pair[0] for pair in p_front]
        p_frontY = [pair[1] for pair in p_front]
        return p_frontX, p_frontY
    def select_solution(self, event):
        # check that there are some indices
        if not len(event.ind): return True
        
        # the click locations
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata
        
        # get the closest index
        try:
            closest_point = None
            for point in event.ind:
                #print event.ind
                if (closest_point is None) or (npy.hypot(x-self.x_axis.displayable_data[point], y-self.y_axis.displayable_data[point]) < closest_point):
                    closest_point = point
        except:
            closest_point = event.ind[0]
       
        #print 'Sol. Index', self.disp_data_indx_map[closest_point] 
        # obtain solution parameters as a list of lists: [[name1, units1, data1],[name2, units2, data2],...]
        self.sol_params = [[objective.name_units[0],objective.data[self.disp_data_indx_map[closest_point]],objective.name_units[1]]
                           for objective in self.obj_widg]
        self.obj_values_model.set_table(self.sol_params)
        '''
        pos = nx.spring_layout(self.sym_layout.lumped_graph)
        nx.draw(self.sym_layout.lumped_graph, pos)
        nx.draw_networkx_edge_labels(self.sym_layout.lumped_graph, pos)
        plt.show()
        '''
        # draw layout preview
        self.sol_index = self.disp_data_indx_map[closest_point]
        self.sel_ind=closest_point
        self.draw_graph()
        self.draw_layout_preview(self.sol_index)


    def draw_layout_preview(self, index):
        # generate layout for preview
        self.sym_layout.gen_solution_layout(index)
        
        if self.sym_layout.layout_ready:
            # plot layout
            self.preview_figure.clear()
            self.preview_axes = self.preview_figure.add_subplot(1,1,1, aspect=1.0)
            filletFlag = False
            flag=0  # for new layout engine plotting 0:old engine, 1:new engine
            plot_layout(self.sym_layout,flag, filletFlag, self.preview_axes, new_window=False)
            self.preview_canvas.draw()
        
    def save_solution(self):
        if self.parent is not None:
            self.sol_count += 1
            self.sol_name = QtGui.QInputDialog.getText(self,"Solution Name","Enter a name for this solution:",
                                                       QtGui.QLineEdit.Normal,"Solution " + str(self.sol_count))
            self.solution = Solution()
            if self.sol_name[1]:
                if self.sol_name[0] == "":
                    self.solution.name = "Solution " + str(self.sol_count)
                else:
                    self.solution.name = self.sol_name[0]
            # ----> what if the name already exists?
                #print"index", self.sol_index
                self.solution.index = self.sol_index
                self.solution.params = self.sol_params
                #print "in graph",self.solution.name, self.solution.index
                self.parent.add_solution(self.solution)
                #self.parent.project.add_solution(self.solution)

            else:
                self.sol_count -= 1
        else:
            # Debug mode
            # Save out Q3D of selected solution
            from powercad.export.Q3D import output_q3d_vbscript
            from powercad.design.module_design import ModuleDesign
            import pickle
            
            md = ModuleDesign(self.sym_layout)
            output_q3d_vbscript(md, "../../../export_data/q3d_out.vbs")
            
            # Pickle Symbolic Layout
            f = open("../../../export_data/symlayout.p", 'w')
            self.sym_layout.solutions = []
            pickle.dump(self.sym_layout, f)
            f.close()
            
    def save_solution_set(self):
    # Called when "Export Solution Set" button is clicked. Opens file browser to select file save location and specify a csv file name. 
    # Collects solution data and sends it to py_csv module for csv export
        
        '''print 'specify file name' ''' # for developer
        
        # open file browser and get file name and directory (restrict to csv):
        tgt_file = QtGui.QFileDialog.getSaveFileName(self, "Export CSV", "", 'CSV (Comma separated values) (*.csv)', options=QtGui.QFileDialog.ShowDirsOnly)
        '''print tgt_file # for developer'''
        
        # if target file name was entered
        if tgt_file[0]!="":
            # send data, file name, and directory to py_csv 
            py_csv(self.solution_library.measure_data, self.solution_library.measure_names_units, tgt_file[0])
        else: # if name is blank or user clicks 'cancel'
            pass
        
                              
class ObjectiveValuesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.header = ["Name", "Value", "Unit"]
        self.obj_values = []
    
    def rowCount(self, parent):
        return len(self.obj_values)
    
    def columnCount(self, parent):
        return len(self.header)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return  None
        return self.obj_values[index.row()][index.column()]
    
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        else:
            return None
        
    def clear_table(self):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.obj_values = []
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        
    def set_table(self, obj_values):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.obj_values = obj_values
        self.emit(QtCore.SIGNAL("layoutChanged()"))

#----------------------------------------------------------------------------------------------------PNT---
#    To do:
#    
#    1.  Error checking - for everything # how to do this?
#    2.  Make sure everything is getting passed by reference to conserve memory (i think it is) # how to chk this? self.object?
#    3.  Add docstrings to everything # not affecting code; comments sufficient
#    4.  Everything is rounded to two decimal places.  What if we need smaller than that? # CHK THIS
#    5.  Edit ScrollArea's max height for different number of objectives #SM- fixed window size
#    6.  What if envelope min needs to be smaller than 1?
#    7.  What if only one axis is checked to be graphed? # SM - completed
#    8.  Make certain variables and functions private
#    9.  Speed up filtering or add "apply"/"dynamic" button
#    10. To fix warning that comes up at start, play around with the order of the imports
#    11. Write code to find families of curves and families of surfaces
#    12. Be able to sort objectives by their impact on the data (high priority objectives on top)
#    13. ScrollArea extended under the display area below when displayed on Matt's small laptop screen
#    14. Be able to "dump the design space" into something like a PDF
#    15. Do gradient colors on points to see extra dimensions
#    16. Matt mentioned something about maybe "profilers" or "decorators" to speed up the filtering
#    17. Get envelopes in sync with the matplotlib toolbar
#    18. Show layoutID in Solution browser when a solution is clicked
#    ...
#    ------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass