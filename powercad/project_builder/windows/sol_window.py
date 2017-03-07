'''
Created on Oct 16, 2012
modified on April 15 2016 by Quang
@author: pxt002
sxm063 - added function "export_spice_reduced_parasitics()" and its corresponding button.
Quang- on the solution figure, now we can see the dies are now labeled with number so users can know the whereabouts of the interested dies
'''

import sys
import traceback
import os
import time
from powercad.project_builder.dialogs.solutionWindow_ui import Ui_layout_form
from PySide import QtCore, QtGui, QtOpenGL
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from powercad.project_builder.proj_dialogs import SolidworkVersionCheckDialog
from powercad.sym_layout.plot import plot_layout
from powercad.export.Q3D import output_q3d_vbscript
from powercad.export.solidworks import output_solidworks_vbscript
from powercad.design.module_design import ModuleDesign
from powercad.spice_export.netlist_graph import Module_SPICE_netlist_graph,Module_SPICE_netlist_graph_v2, Module_SPICE_lumped_graph
from powercad.spice_export.thermal_netlist_graph import Module_Full_Thermal_Netlist_Graph
from powercad.electro_thermal.ElectroThermal_toolbox import ET_analysis
import numpy as np
class SolutionWindow(QtGui.QWidget):
    """Solution windows that show up in MDI area"""
    def __init__(self, solution, sym_layout):
        """Set up the solution window"""
        QtGui.QWidget.__init__(self)
        self.ui = Ui_layout_form()
        self.ui.setupUi(self)
        self.setWindowTitle(solution.name)
        
        self.ui.btn_export_q3d.pressed.connect(self.export_q3d)
        self.ui.btn_export_solidworks.pressed.connect(self.export_solidworks)
        self.ui.btn_export_spice_parasitics.pressed.connect(self.export_spice_parasitics)        
        self.ui.btn_export_spice_thermal.pressed.connect(self.export_spice_thermal)
        self.ui.btn_run_succesive_approxomation.pressed.connect(self.Run_Sucessive_approximation)#sxm; new button function added based on self.export_spice_parasitics
        
        self.solution = solution
        self.sym_layout = sym_layout
        
        # display objective data in table widget
        self.ui.tbl_info.setRowCount(len(solution.params))
        self.i = 0
        for objective in solution.params:
            self.tbl_item = QtGui.QTableWidgetItem(objective[0])
            self.ui.tbl_info.setItem(self.i,0,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(str(round(objective[1],4)))
            self.ui.tbl_info.setItem(self.i,2,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(objective[2])
            self.ui.tbl_info.setItem(self.i,1,self.tbl_item)
            self.i += 1
        
        
        fig = Figure()
        canvas =  FigureCanvas(fig)
        self.ui.preview_layout = QtGui.QGridLayout(self.ui.grfx_layout)
        self.ui.preview_layout.setContentsMargins(0,0,0,0)
        self.ui.preview_layout.addWidget(canvas,0,0,1,1)
        
        ax = fig.add_subplot(111, aspect=1.0)
        plot_layout(sym_layout, ax, new_window=False)
        canvas.draw()
        
    def export_q3d(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        print fn
        outname = fn[0]
        
        if len(outname) > 0:
            try:
                self.sym_layout.gen_solution_layout(self.solution.index)
                md = ModuleDesign(self.sym_layout)
                output_q3d_vbscript(md, outname)
                QtGui.QMessageBox.about(None, "Q3D VB Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "Q3D VB Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()
        
    def export_solidworks(self):
        version=SolidworkVersionCheckDialog(self)
        if version.exec_():
            version=version.version_output()
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        
        if len(outname) > 0:
            print 'exporting solidworks file'
            try:
                self.sym_layout.gen_solution_layout(self.solution.index)
                md = ModuleDesign(self.sym_layout)
                
                data_dir = 'C:/ProgramData/SolidWorks/SolidWorks '+version
                output_solidworks_vbscript(md, os.path.basename(outname), data_dir, os.path.dirname(outname))
                QtGui.QMessageBox.about(None, "SolidWorks Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SolidWorks Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()
                
    def export_spice_parasitics(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        
        if len(outname) > 0:
            print 'exporting spice electrical parasitics netlist file'
            try:
                starttime=time.time()
                spice_netlist_graph = Module_SPICE_netlist_graph_v2(os.path.basename(outname), self.sym_layout, self.solution.index, template_graph=None)
                runtime=time.time()-starttime
                spice_netlist_graph.write_SPICE_subcircuit(os.path.dirname(outname)) 
                
                print runtime
                QtGui.QMessageBox.about(None, "SPICE Electrical Parasitics Netlist", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SPICE Electrical Parasitics Netlist", "Failed to export netlist! Check log/console.")
                print traceback.format_exc()

    def Run_Sucessive_approximation(self):
        outname='aaa'
        thermal_netlist_graph = Module_Full_Thermal_Netlist_Graph(os.path.basename(outname), self.sym_layout, self.solution.index)   
        electrothermal=ET_analysis(thermal_netlist_graph)
        thermal_mdl=electrothermal.ET_formation_1(20e3)
        filedes='C:\Users\qmle\Desktop\Transistors_data\cpmf_1200_0080B'
        rds_fn='Rdson.csv'
        crss_fn='Crss.csv'
        vth_fn='Vth.csv'
        parameters=electrothermal.curve_fitting_all(filedes, rds_fn, crss_fn,vth_fn) 
        num_island=max(electrothermal.r_parent)
        num_dies=max(electrothermal.r_id)
        side=num_island+num_dies+1  
        To=np.ones((side,1))
        To=electrothermal.Tamb*To
        To=np.asarray(To)
        Po=electrothermal.ptot_all(To[0:num_dies], parameters)
        #electrothermal.Run_sim(thermal_mdl, parameters, 300000)
        start=time.time()
        electrothermal.sucessive_approximation(Po, parameters)
        runtime=time.time()-start
        print 'runtime: ' + str(runtime)
    def export_spice_reduced_parasitics(self): #sxm; new function added (template based on export_spice_parasitics() function defined above)
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        
        if len(outname) > 0:
            print 'exporting spice electrical parasitics (reduced) netlist file'
            try:
                spice_reduced_netlist_graph = Module_SPICE_lumped_graph(os.path.basename(outname), self.sym_layout, self.solution.index, template_graph=None)
                spice_reduced_netlist_graph.write_SPICE_reduced_subcircuit(os.path.dirname(outname)) 
                QtGui.QMessageBox.about(None, "SPICE Electrical Parasitics (reduced) Netlist", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SPICE Electrical Parasitics (reduced) Netlist", "Failed to export netlist! Check log/console.")
                print traceback.format_exc()
         
    
    def export_spice_thermal(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        
        if len(outname) > 0:
            print 'exporting spice thermal netlist file'
            try:
                thermal_netlist_graph = Module_Full_Thermal_Netlist_Graph(os.path.basename(outname), self.sym_layout, self.solution.index)
                #electrothermal=ET_analysis(thermal_netlist_graph)
                thermal_netlist_graph.write_full_thermal_circuit(os.path.dirname(outname))
                QtGui.QMessageBox.about(None, "SPICE Thermal Netlist", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SPICE Thermal Netlist", "Failed to export netlist! Check log/console.")
                print traceback.format_exc()
        
#    def electro_thermal_simulation(self):
        
                    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    test = SolutionWindow()
    test.show()
    sys.exit(app.exec_())