'''
Created on Oct 16, 2012

@author: pxt002
'''

import sys
import traceback
import os

from solutionWindow_ui import Ui_layout_form
from PySide import QtCore, QtGui, QtOpenGL
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from powercad.sym_layout.plot import plot_layout
from powercad.export.Q3D import output_q3d_vbscript
from powercad.export.solidworks import output_solidworks_vbscript
from powercad.design.module_design import ModuleDesign

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
        
        self.solution = solution
        self.sym_layout = sym_layout
        
        # display objective data in table widget
        self.ui.tbl_info.setRowCount(len(solution.params))
        self.i = 0
        for objective in solution.params:
            self.tbl_item = QtGui.QTableWidgetItem(objective[0])
            self.ui.tbl_info.setItem(self.i,0,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(str(round(objective[2],4)))
            self.ui.tbl_info.setItem(self.i,1,self.tbl_item)
            self.tbl_item = QtGui.QTableWidgetItem(objective[1])
            self.ui.tbl_info.setItem(self.i,2,self.tbl_item)
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
        fn = QtGui.QFileDialog.getSaveFileName(self, options=QtGui.QFileDialog.ShowDirsOnly)
        outname = fn[0]
        
        if len(outname) > 0:
            print 'exporting solidworks file'
            try:
                self.sym_layout.gen_solution_layout(self.solution.index)
                md = ModuleDesign(self.sym_layout)
                data_dir = 'C:/ProgramData/SolidWorks/SolidWorks 2012'
                output_solidworks_vbscript(md, os.path.basename(outname), data_dir, os.path.dirname(outname))
                QtGui.QMessageBox.about(None, "SolidWorks Script", "Export successful.")
            except:
                QtGui.QMessageBox.warning(None, "SolidWorks Script", "Failed to export vb script! Check log/console.")
                print traceback.format_exc()
        

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    test = SolutionWindow()
    test.show()
    sys.exit(app.exec_())