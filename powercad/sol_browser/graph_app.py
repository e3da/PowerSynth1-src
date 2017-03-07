'''
Created on March 6, 2012

@author: shook
'''

import sys
import operator

from PySide import QtCore, QtGui

import powercad.sym_layout.plot as plot
plot.plt.matplotlib.use('Qt4Agg')
plot.plt.matplotlib.rcParams['backend.qt4']='PySide'

import numpy as npy
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from mpl_toolkits.mplot3d import Axes3D

from graphing_form import Ui_GrapheneWindow
from objective_widget import ObjectiveWidget
from powercad.sol_browser.solution import Solution
from powercad.sol_browser.solution_lib import SolutionLibrary
from powercad.sym_layout.plot import plot_layout

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
        
        # Setup selected solution objective values
        self.obj_values_model = ObjectiveValuesTableModel(self)
        self.ui.objective_values_table.setModel(self.obj_values_model)
         
    # Called when an x, y, or z checkbox is clicked    
    def set_graph_axis(self, objective, axis):
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
        self.axes.scatter(self.x_axis.displayable_data, self.y_axis.displayable_data, picker=1)
        # set limits
        self.axes.set_xlim(self.x_axis.position-(self.x_axis.envelope/2), self.x_axis.position+(self.x_axis.envelope/2))
        self.axes.set_ylim(self.y_axis.position-(self.y_axis.envelope/2), self.y_axis.position+(self.y_axis.envelope/2))   
        # set labels
        self.axes.set_xlabel(self.x_axis.name_units[0] + " (" + self.x_axis.name_units[1] + ")")
        self.axes.set_ylabel(self.y_axis.name_units[0] + " (" + self.y_axis.name_units[1] + ")") 
        
    def draw_graph_3D(self):
        # plot data
#        self.axes = self.figure.add_subplot(111, projection='3d')
        self.axes = Axes3D(self.figure)
        self.axes.scatter(self.graph_axis['x'].displayable_data, self.graph_axis['y'].displayable_data, self.graph_axis['z'].displayable_data, picker=1)
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
                if (closest_point is None) or (npy.hypot(x-self.x_axis.displayable_data[point], y-self.y_axis.displayable_data[point]) < closest_point):
                    closest_point = point
        except:
            closest_point = event.ind[0]
       
        #print 'Sol. Index', self.disp_data_indx_map[closest_point] 
        # obtain solution parameters as a list of lists: [[name1, units1, data1],[name2, units2, data2],...]
        self.sol_params = [[objective.name_units[0],objective.name_units[1],objective.data[self.disp_data_indx_map[closest_point]]] 
                           for objective in self.obj_widg]
        self.obj_values_model.set_table(self.sol_params)
        
        # draw layout preview
        self.sol_index = self.disp_data_indx_map[closest_point]
        self.draw_layout_preview(self.sol_index)


    def draw_layout_preview(self, index):
        # generate layout for preview
        self.sym_layout.gen_solution_layout(index)
        
        if self.sym_layout.layout_ready:
            # plot layout
            self.preview_figure.clear()
            self.preview_axes = self.preview_figure.add_subplot(1,1,1, aspect=1.0)
            plot_layout(self.sym_layout, self.preview_axes, new_window=False)
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
            
                self.solution.index = self.sol_index
                self.solution.params = self.sol_params
                self.parent.add_solution(self.solution)
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
#    1.  Error checking - for everything
#    2.  Make sure everything is getting passed by reference to conserve memory (i think it is)
#    3.  Add docstrings to everything
#    4.  Everything is rounded to two decimal places.  What if we need smaller than that?
#    5.  Edit ScrollArea's max height for different number of objectives
#    6.  What if envelope min needs to be smaller than 1?
#    7.  What if only one axis is checked to be graphed?
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
#    ...
#    ------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass