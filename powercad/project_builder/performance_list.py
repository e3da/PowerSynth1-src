'''
Created on Apr 29, 2013

@author: bxs003
'''

from PySide import QtCore, QtGui
from matplotlib.patches import Circle, Rectangle

from powercad.sym_layout.symbolic_layout import ThermalMeasure, ElectricalMeasure

class PerformanceItem(object):
    def __init__(self, PerfUI, measure, row_item):
        self.PerfUI = PerfUI
        self.table = self.PerfUI.ui.tbl_performance
        self.measures = self.PerfUI.parent.project.symb_layout.perf_measures
        self.measure = measure
        self.row_item = row_item # used to identify which row this is (without an index)
        self.btn_del = self.create_del_button()
        
    def create_del_button(self):
        # create delete button
        btn_del = QtGui.QPushButton(self.table)
        btn_del.setText('X')
        self.table.setCellWidget(self.row_index(),4,btn_del)
        btn_del.pressed.connect(self.remove)
        return btn_del
    
    def remove(self):
        self.measures.remove(self.measure)
        self.table.removeRow(self.row_index())
        self.PerfUI.perf_items.remove(self)
        
    def row_index(self):
        return self.table.row(self.row_item)
        
class PerformanceListUI(object):
    
    def __init__(self, parent):
        ''' Performance Identification Module
        
            Keyword Arguments:
            parent: ProjectBuilder object
        '''
        self.parent = parent
        self.ui = self.parent.ui
        self.perform_devices = [] # used to temporarily store picked devices/leads
        self.perform_lines = [] # used to temp store picked lines
        self.perf_items = []
        
        # Connect Actions
        self.ui.btn_perform_addPerformance.pressed.connect(self.add_performance)
        self.ui.txt_perform_name.textChanged.connect(self.populate_cmb_elec_therm)
        self.ui.cmb_perform_elecTherm.currentIndexChanged.connect(self.populate_cmb_type)
        self.ui.cmb_perform_type.currentIndexChanged.connect(self.disp_perform_step2)
        
        self.parent.symb_canvas[self.parent.MEASURES_PLOT].mpl_connect('pick_event', self.performance_pick)

    def populate_cmb_elec_therm(self):
        if self.ui.txt_perform_name.text() == '':
            self.ui.cmb_perform_elecTherm.clear()
            self.ui.cmb_perform_type.clear()
        elif self.ui.cmb_perform_elecTherm.currentText() == "":
            self.ui.cmb_perform_elecTherm.addItem("Select..")
            self.ui.cmb_perform_elecTherm.addItem("Electrical")
            self.ui.cmb_perform_elecTherm.addItem("Thermal")
            
    def populate_cmb_type(self):
        self.ui.cmb_perform_type.clear()
        if self.ui.cmb_perform_elecTherm.currentText() == "Electrical":
            self.ui.cmb_perform_type.addItem("Select..")
            self.ui.cmb_perform_type.addItem("Resistance")
            self.ui.cmb_perform_type.addItem("Capacitance")
            self.ui.cmb_perform_type.addItem("Inductance")
        elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
            self.ui.cmb_perform_type.addItem("Select..")
            self.ui.cmb_perform_type.addItem("Max")
            self.ui.cmb_perform_type.addItem("Average")
            self.ui.cmb_perform_type.addItem("Std. Dev.")
            
    def disp_perform_step2(self):
        perf_text = self.ui.cmb_perform_type.currentText()
        if perf_text != "Select..":
            self.ui.lbl_perform_step2.setEnabled(True)
            if self.ui.cmb_perform_elecTherm.currentText() == "Electrical":
                if perf_text == "Resistance" or perf_text == "Inductance":
                    self.ui.lbl_perform_step2.setText("Step 2:  Select two devices/leads on the right to define path.")
                elif perf_text == "Capacitance":
                    self.ui.lbl_perform_step2.setText("Step 2:  Select one or more traces (lines) on right for capacitance measurement.")
            elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
                self.ui.lbl_perform_step2.setText("Step 2:  Select device(s) on the right to include in measurements.")
        else:
            # clear steps 2 and 3
            self.ui.lbl_perform_step2.setEnabled(False)
            self.ui.lbl_perform_step3.setEnabled(False)
            self.ui.btn_perform_addPerformance.setEnabled(False)
            self.ui.lbl_perform_step2.setText("Step 2:  Select Devices/Leads.")
            # uncolor everything
            for device in self.perform_devices:
                self.parent.patch_dict.get_patch(device, 3).set_facecolor(self.parent.default_color)
            self.parent.symb_canvas[3].draw()
            # de-select all devices
            self.perform_devices = []
        
    def performance_pick(self, event):
        """Pick event called when performance identification symbolic layout is clicked"""
        if self.ui.lbl_perform_step2.isEnabled():
            perf = self.ui.cmb_perform_elecTherm.currentText()
            perf_desc = self.ui.cmb_perform_type.currentText()
            if perf == "Thermal" or perf_desc == "Resistance" or perf_desc == "Inductance":
                self._handle_thermal_res_ind(event)
            elif perf_desc == "Capacitance":
                self._handle_cap(event)
            self.parent.symb_canvas[3].draw() # redraw
                
    def _handle_thermal_res_ind(self, event):
        if isinstance(event.artist, Circle):
            # color the object
            col = self.parent.color_wheel[0]
            color = col.getRgbF()
            color = (color[0],color[1],color[2],0.5)
            # if the artist is already colored that color
            if event.artist.get_facecolor() == color:
                # set back to default color
                event.artist.set_facecolor(self.parent.default_color)
                # remove object from performance list
                self.perform_devices.remove(self.parent.patch_dict.get_layout_obj(event.artist))
            else:
                layout_pt = self.parent.patch_dict.get_layout_obj(event.artist)
                add_pt = True
                # only allow devices if measuring thermal
                if self.ui.cmb_perform_elecTherm.currentText() == "Thermal" and (not layout_pt.is_device()):
                    add_pt = False
                
                if add_pt:
                    event.artist.set_facecolor(color) # color object
                    self.perform_devices.append(layout_pt) # add object to performance list
            
            perf_type = self.ui.cmb_perform_type.currentText()
            if perf_type == "Resistance" or perf_type == "Inductance":
                # only keep two objects (remove first object if necessary)
                if len(self.perform_devices) > 2:
                    self.parent.patch_dict.get_patch(self.perform_devices[0], 3).set_facecolor(self.parent.default_color)
                    self.perform_devices.pop(0)
                # if two are selected, move to set 3
                elif len(self.perform_devices) == 2:
                    self.ui.lbl_perform_step3.setEnabled(True)
                    self.ui.btn_perform_addPerformance.setEnabled(True)
                # if there are less than 2, unenable step 3
                else:
                    self.ui.lbl_perform_step3.setEnabled(False)
                    self.ui.btn_perform_addPerformance.setEnabled(False)
            elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
                # if anything is selected, move to step 3
                if len(self.perform_devices) > 0:
                    self.ui.lbl_perform_step3.setEnabled(True)
                    self.ui.btn_perform_addPerformance.setEnabled(True)
                # if nothing is selected, unenable step 3
                else:
                    self.ui.lbl_perform_step3.setEnabled(False)
                    self.ui.btn_perform_addPerformance.setEnabled(False)
                    # print self.perform_devices
    
    def _handle_cap(self, event):
        if isinstance(event.artist, Rectangle):
            layout_line = self.parent.patch_dict.get_layout_obj(event.artist)
            # color the object
            col = self.parent.color_wheel[0]
            color = col.getRgbF()
            color = (color[0],color[1],color[2],0.5)
            
            if event.artist.get_facecolor() == color:
                # set back to default color
                event.artist.set_facecolor(self.parent.default_color)
                # remove object from performance list
                self.perform_lines.remove(layout_line)
            else:
                # only allow trace lines when measuring cap.
                if not layout_line.wire:
                    event.artist.set_facecolor(color) # color object
                    self.perform_lines.append(layout_line) # add object to performance list
                    
            if len(self.perform_lines) > 0:
                self.ui.btn_perform_addPerformance.setEnabled(True)
            else:
                self.ui.btn_perform_addPerformance.setEnabled(False)
            
    def add_performance(self):
        """Add performance item to list"""
        # create performace measure
        if self.ui.cmb_perform_elecTherm.currentText() == "Electrical":
            # get type
            if self.ui.cmb_perform_type.currentText() == "Resistance":
                measure = ElectricalMeasure.MEASURE_RES
            elif self.ui.cmb_perform_type.currentText() == "Capacitance":
                measure = ElectricalMeasure.MEASURE_CAP
            elif self.ui.cmb_perform_type.currentText() == "Inductance":
                measure = ElectricalMeasure.MEASURE_IND
            else: 
                print "Error"
                return 1
            # get frequency
            try:
                freq = float(self.ui.txt_switchFreq.text())*1e3 # Convert to kHz
            except (ValueError):
                print "Error: No switching frequency"
                return 1
            if freq == 0:  
                print "Error: Switching frequency must be greater than zero"
                return 1
            # create performace measure
            if measure == ElectricalMeasure.MEASURE_CAP:
                performance_measure = ElectricalMeasure(None,None,measure,freq,self.ui.txt_perform_name.text(),self.perform_lines)
            else:
                performance_measure = ElectricalMeasure(self.perform_devices[0],self.perform_devices[1],measure,freq,self.ui.txt_perform_name.text()) 
        elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
            # get type
            if self.ui.cmb_perform_type.currentText() == "Max":
                stat_fn = ThermalMeasure.FIND_MAX
            elif self.ui.cmb_perform_type.currentText() == "Average":
                stat_fn = ThermalMeasure.FIND_AVG
            elif self.ui.cmb_perform_type.currentText() == "Std. Dev.":
                stat_fn = ThermalMeasure.FIND_STD_DEV
            else: 
                print "Error"
                return 1
            # create performace measure
            performance_measure = ThermalMeasure(stat_fn,self.perform_devices,self.ui.txt_perform_name.text()) 
        
        performance_measure.disp = (self.ui.cmb_perform_elecTherm.currentText(),self.ui.cmb_perform_type.currentText())
            
        # add row to table
        row = self.ui.tbl_performance.rowCount()
        self.ui.tbl_performance.insertRow(row)
        for i in range(4):
            self.ui.tbl_performance.setItem(row,i,QtGui.QTableWidgetItem())
        self.ui.tbl_performance.item(row,0).setText("")
        self.ui.tbl_performance.item(row,1).setText(self.ui.txt_perform_name.text())
        self.ui.tbl_performance.item(row,2).setText(self.ui.cmb_perform_elecTherm.currentText())
        self.ui.tbl_performance.item(row,3).setText(self.ui.cmb_perform_type.currentText())
        
        perf_item = PerformanceItem(self, performance_measure, self.ui.tbl_performance.item(row,0))
        self.perf_items.append(perf_item)
        # add to performance measure list in symbolic layout
        self.parent.project.symb_layout.perf_measures.append(performance_measure)
        # clean out gui list
        #print len(self.perf_items)
     
        # clear everything
        self.ui.txt_perform_name.setText('')
        # uncolor everything
        for device in self.perform_devices:
            self.parent.patch_dict.get_patch(device, 3).set_facecolor(self.parent.default_color)
        for line in self.perform_lines:
            self.parent.patch_dict.get_patch(line, 3).set_facecolor(self.parent.default_color)
        self.parent.symb_canvas[3].draw()
        
    def load_measures(self):
        for measure in self.parent.project.symb_layout.perf_measures:
            # add row to table
            row = self.ui.tbl_performance.rowCount()
            self.ui.tbl_performance.insertRow(row)
            for i in range(4):
                self.ui.tbl_performance.setItem(row,i,QtGui.QTableWidgetItem())
            self.ui.tbl_performance.item(row,0).setText("")
            self.ui.tbl_performance.item(row,1).setText(measure.name)
            self.ui.tbl_performance.item(row,2).setText(measure.disp[0])
            self.ui.tbl_performance.item(row,3).setText(measure.disp[1])
            
            perf_item = PerformanceItem(self, measure, self.ui.tbl_performance.item(row,0))
            self.perf_items.append(perf_item)
