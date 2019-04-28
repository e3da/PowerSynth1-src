'''
Created on Oct 16, 2012
modified on April 15 2016 by Quang
@author: pxt002
sxm063 - added function "export_spice_reduced_parasitics()" and its corresponding button.
Quang- on the solution figure, now we can see the dies are now labeled with number so users can know the whereabouts of the interested dies
'''

import os
import sys
import time
import traceback

import numpy as np
from PySide import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from powercad.Spice_handler.spice_import.NetlistImport import Netlist, Netlis_export_ADS
from powercad.Spice_handler.spice_export.thermal_netlist_graph import Module_Full_Thermal_Netlist_Graph
from powercad.Spice_handler.spice_export.netlist_graph import Module_SPICE_netlist_graph_v2, Module_SPICE_lumped_graph
from powercad.design.module_design import ModuleDesign
from powercad.drc.design_rule_check import DesignRuleCheck
from powercad.electro_thermal.ElectroThermal_toolbox import ET_analysis
from powercad.interfaces.EMPro.EMProExport import EMProScript
from powercad.interfaces.FastHenry.fh_layers import output_fh_script
from powercad.interfaces.Q3D.Q3D import output_q3d_vbscript
from powercad.interfaces.Solidworks.solidworks import output_solidworks_vbscript
from powercad.project_builder.dialogs.solutionWindow_ui import Ui_layout_form
from powercad.project_builder.proj_dialogs import SolidworkVersionCheckDialog
from powercad.sym_layout.plot import plot_layout
from powercad.Spice_handler.spice_export.circuit import Circuit

class SolutionWindow(QtGui.QWidget):
    """Solution windows that show up in MDI area"""
    def __init__(self, solution=None, sym_layout=None, flag=0,filletFlag=None,dir=None,parent=None):
        """Set up the solution window"""
        QtGui.QWidget.__init__(self)
        self.ui = Ui_layout_form()
        self.ui.setupUi(self)
        self.setWindowTitle(solution.name)
        self.ui.btn_run_drc.pressed.connect(self.run_drc)
        self.ui.btn_export_selected.pressed.connect(self.export_script)
        self.parent=parent
        self.flag=flag # plotting new layout engine layout 0:old engine, 1:new engine
        #self.ui.btn_run_succesive_approxomation.pressed.connect(self.Run_Sucessive_approximation)#sxm; new button function added based on self.export_spice_parasitics

        self.solution = solution
        #print self.solution

        self.sym_layout = sym_layout
        self.default_save_dir=dir # This will make all save functions default to project dir
        # display objective data in table widget
        self.ui.tbl_info.setRowCount(len(solution.params))
        self.i = 0
        for objective in solution.params:
            #print objective
            self.tbl_item = QtGui.QTableWidgetItem(objective[0])
            self.ui.tbl_info.setItem(self.i,0,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(str(round(objective[1],4)))
            self.ui.tbl_info.setItem(self.i,1,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(objective[2])
            self.ui.tbl_info.setItem(self.i,2,self.tbl_item)
            self.i += 1


        fig = Figure()
        canvas =  FigureCanvas(fig)
        self.ui.preview_layout = QtGui.QGridLayout(self.ui.grfx_layout)
        self.ui.preview_layout.setContentsMargins(0,0,0,0)
        self.ui.preview_layout.addWidget(canvas,0,0,1,1)

        ax = fig.add_subplot(111, aspect=1.0)
        plot_layout(sym_layout,flag, filletFlag, ax, new_window=False)
        canvas.draw()

    def run_drc(self):
        drc = DesignRuleCheck(self.sym_layout)
        if drc.passes_drc(False):
            QtGui.QMessageBox.about(None, "Design Rule Check", "DRC complete. No DRC errors were found.")
        else:
            QtGui.QMessageBox.warning(None, "Design Rule Check", "DRC errors found! Check log/console.")
    def export_script(self):
        selected=str(self.ui.cmbox_export_option.currentText())
        if self.parent.project.layout_engine=="SL":
            self.sym_layout.gen_solution_layout(self.solution.index)
        if selected == 'Q3D':
            self.export_q3d()
        elif selected== 'Solidworks':
            self.export_solidworks()
        elif selected == 'Electrical netlist ':
            self.export_spice_parasitics(self.sym_layout)
        elif selected == 'Thermal netlist':
            self.export_spice_thermal()
        elif selected == 'FastHenry':
            self.export_FH()
        elif selected == 'EMPro':
            self.export_empro()
    def export_FH(self):
        fn = QtGui.QFileDialog.getSaveFileName(self,dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        if len(outname) > 0:
            try:
                md = ModuleDesign(self.sym_layout)
                #output_fh_script_mesh(md,outname)
                output_fh_script(self.sym_layout,outname)
                QtGui.QMessageBox.about(None, "FH Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "FH Script", "Failed to export FH script! Check log/console.")
                print traceback.format_exc()

    def export_empro(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir,options=QtGui.QFileDialog.ShowDirsOnly)
        print fn
        outname = fn[0]

        if len(outname) > 0:
            try:
                md = ModuleDesign(self.sym_layout)
                empro_script = EMProScript(md, outname+".py")
                empro_script.generate()
                QtGui.QMessageBox.about(None, "EMPro Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "EMPro Script", "Failed to export script! Check log/console.")
                print traceback.format_exc()

    def export_q3d(self):
        fn = QtGui.QFileDialog.getSaveFileName(self,dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
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
        version=SolidworkVersionCheckDialog(self)
        if version.exec_():
            version=version.version_output()
        fn = QtGui.QFileDialog.getSaveFileName(self, dir=self.default_save_dir,options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]

        if len(outname) > 0:
            print 'exporting solidworks file'
            try:
                md = ModuleDesign(self.sym_layout)

                data_dir = 'C:/ProgramData/SolidWorks/SolidWorks '+version
                output_solidworks_vbscript(md, os.path.basename(outname), data_dir, os.path.dirname(outname))
                QtGui.QMessageBox.about(None, "SolidWorks Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SolidWorks Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()

    def export_spice_parasitics(self,sym_layout):
        fn = QtGui.QFileDialog.getSaveFileName(self,dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]

        if len(outname) > 0:
            print 'exporting spice electrical parasitics netlist file'
            try:
                #spice_netlist_graph = Module_SPICE_netlist_graph_v2(os.path.basename(outname), self.sym_layout, self.solution.index, template_graph=None)
                #spice_netlist_graph.write_SPICE_subcircuit(os.path.dirname(outname))

                spice_netlist=Circuit()
                spice_netlist._graph_read(sym_layout.lumped_graph)
                ads_net = Netlis_export_ADS(df=spice_netlist.df_circuit_info, pm=spice_netlist.portmap)
                ads_net.export_ads2(outname)
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
        fn = QtGui.QFileDialog.getSaveFileName(self,dir=self.default_save_dir, options=QtGui.QFileDialog.ShowDirsOnly)
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

# test - Jul 25, 2017