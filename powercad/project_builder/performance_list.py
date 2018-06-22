'''
Created on Apr 29, 2013

@author: bxs003
'''

from PySide import QtCore, QtGui
from matplotlib.patches import Circle, Rectangle
import psidialogs
from powercad.sym_layout.symbolic_layout import ThermalMeasure, ElectricalMeasure,SymLine,SymPoint
from powercad.project_builder.proj_dialogs import Device_states_dialog
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
        '''
        Remove an Item from list
        '''
        #pm_type=self.measure.mdl


        self.measures.remove(self.measure)


        self.table.removeRow(self.row_index())
        self.PerfUI.perf_items.remove(self)
        self.PerfUI.refresh_window()
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
        self.perform_devices_pins=[] # used to temporarily map to the picked devices D S or G
        self.perform_lines = [] # used to temp store picked lines
        self.perf_items = []
        self.device_states_df=None
        # Connect Actions
        self.ui.btn_setup_device_state.pressed.connect(self.open_device_state_dialog)
        self.ui.btn_perform_addPerformance.pressed.connect(self.add_performance)
        self.ui.txt_perform_name.textChanged.connect(self.populate_cmb_elec_therm)
        self.ui.cmb_perform_elecTherm.currentIndexChanged.connect(self.populate_cmb_type)
        self.ui.cmb_perform_type.currentIndexChanged.connect(self.disp_perform_step2)
        self.ui.cmb_thermal_model.currentIndexChanged.connect(self.disp_perform_step3)
        self.parent.symb_canvas[self.parent.MEASURES_PLOT].mpl_connect('pick_event', self.performance_pick)
        self.ui.tbl_performance.pressed.connect(self.show_performance)

    def refresh_window(self):
        all_points = self.parent.project.symb_layout.points
        all_lines = [x for x in self.parent.project.symb_layout.all_sym if isinstance(x, SymLine)]
        all_traces = [x for x in all_lines if not (x.wire)]
        all_elements = all_traces+ all_points
        for e in all_elements:
            self.parent.patch_dict.get_patch(e, 3).set_facecolor(self.parent.default_color)
        self.parent.symb_canvas[3].draw()


    def show_performance(self):
        self.refresh_window()
        all_measures=self.parent.project.symb_layout.perf_measures
        all_points =self.parent.project.symb_layout.points
        all_lines = [x for x in self.parent.project.symb_layout.all_sym if isinstance(x,SymLine)]
        all_traces = [x for x in all_lines if not(x.wire)]
        for i in range(len(all_measures)):
            row = self.ui.tbl_performance.currentRow()
            if row == i:
                measure = all_measures[i]

                if isinstance(measure,ElectricalMeasure):
                    if measure.measure==3:
                        all_names = [x.name for x in measure.lines if not(x.wire)]
                        for line in all_traces:
                            if line.name in all_names:
                                self.parent.patch_dict.get_patch(line, 3).set_facecolor('#00FF00')
                    else:
                        for device in all_points:

                            if device.name == measure.pt1.name or device.name==measure.pt2.name:
                                self.parent.patch_dict.get_patch(device, 3).set_facecolor('#00FF00')
                elif isinstance(measure,ThermalMeasure):
                    all_names = [x.name for x in measure.devices]
                    for device in all_points:
                        if device.name in all_names:
                            self.parent.patch_dict.get_patch(device, 3).set_facecolor('#00FF00')
        self.parent.symb_canvas[3].draw()
    def open_device_state_dialog(self):
        device_state=Device_states_dialog(self.parent,self)
        device_state.exec_()
        self.ui.btn_perform_addPerformance.setEnabled(True)

    def electrical_model_options(self):
        if self.ui.cmb_elec_model.currentText()=='Matlab':
            Matlab_dialog=MatlabInterfaceDialog(self.parent)
            if (Matlab_dialog.exec_()):


                print "successfully open new dialog"

    def thermal_model_options(self):
        if self.ui.cmb_thermal_model.currentText()=='Matlab':
            Matlab_dialog=MatlabInterfaceDialog(self.parent)
            Matlab_dialog.set_matlab_script(Thermal_Module.format(""))
            Matlab_dialog.open_instruction("Instruction for Thermal Model goes here")
            if (Matlab_dialog.exec_()):
                print "successfully open new dialog"

    def populate_cmb_elec_therm(self):
        self.refresh_window()
        self.ui.tbl_performance.setEnabled(False)

        if self.ui.txt_perform_name.text() == '':
            self.ui.cmb_perform_elecTherm.clear()
            self.ui.cmb_perform_type.clear()
            self.ui.tbl_performance.setEnabled(True)
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
            self.ui.lbl_sel_electrical_model.setEnabled(True)
            self.ui.lbl_sel_thermal_model.setEnabled(True)
            self.ui.lbl_perform_step3.setEnabled(True)
            self.ui.cmb_thermal_model.setEnabled(True)
            self.ui.cmb_elec_model.setEnabled(True)
            if self.ui.cmb_perform_elecTherm.currentText() == "Electrical":
                if perf_text == "Resistance" or perf_text == "Inductance":
                    self.ui.lbl_perform_step3.setText("Step 3: Select two devices/leads on the right to define path.")
                elif perf_text == "Capacitance":
                    self.ui.lbl_perform_step3.setText("Step 3: Select one or more traces (lines) on right for capacitance\n measurement.")
            elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
                self.ui.lbl_perform_step3.setText("Step 3:Select device(s) on the right to include in measurements.")
        else:
            # clear steps 3 and 4
            self.ui.lbl_perform_step3.setEnabled(False)
            self.ui.cmb_thermal_model.setEnabled(False)
            self.ui.cmb_elec_model.setEnabled(False)
            self.ui.lbl_sel_electrical_model.setEnabled(False)
            self.ui.lbl_perform_step3.setEnabled(False)
            self.ui.lbl_perform_step4.setEnabled(False)
            self.ui.btn_perform_addPerformance.setEnabled(False)
            self.ui.lbl_perform_step3.setText("Step 3:  Select Devices/Leads.")
            # uncolor everything
            for device in self.perform_devices:
                self.parent.patch_dict.get_patch(device, 3).set_facecolor(self.parent.default_color)
            self.parent.symb_canvas[3].draw()
            # de-select all devices
            self.perform_devices = []

    def disp_perform_step3(self):
        elec_txt=self.ui.cmb_perform_type.currentText()
        elec_txt = self.ui.cmb_perform_type.currentText()

    def performance_pick(self, event):
        """Pick event called when performance identification symbolic layout is clicked"""
        if self.ui.lbl_sel_electrical_model.isEnabled():
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
                id = self.perform_devices.index(self.parent.patch_dict.get_layout_obj(event.artist))
                self.perform_devices_pins.remove(id)
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
                if layout_pt.is_device():
                    if layout_pt.is_diode():
                        type=psidialogs.choice(choices=['Anode','Cathode'],message="Select the device pin",title="Select one choice only!!")
                    elif layout_pt.is_transistor():
                        type=psidialogs.choice(choices=['D','S','G'],message="Select the device pin",title="Select one choice only!!")
                    self.perform_devices_pins.append(type)
                else:
                    self.perform_devices_pins.append('Lead')
                # only keep two objects (remove first object if necessary)
                if len(self.perform_devices) > 2:
                    self.parent.patch_dict.get_patch(self.perform_devices[0], 3).set_facecolor(self.parent.default_color)
                    self.perform_devices.pop(0)
                # if two are selected, move to set 3
                elif len(self.perform_devices) == 2:
                    self.ui.lbl_perform_step3.setEnabled(True)
                    self.ui.btn_setup_device_state.setEnabled(True)
                # if there are less than 2, unenable step 3
                else:
                    self.ui.lbl_perform_step3.setEnabled(False)
                    self.ui.btn_setup_device_state.setEnabled(False)

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
            if self.ui.cmb_elec_model.currentText()=="Micro Strip":
                model='MS'
            elif self.ui.cmb_elec_model.currentText()=="Response Surface":
                model='RS'
            # get measure typr
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
                performance_measure = ElectricalMeasure(None,None,measure,freq,self.ui.txt_perform_name.text(),self.perform_lines,model)
            else:
                performance_measure = ElectricalMeasure(pt1=self.perform_devices[0],pt2=self.perform_devices[1],measure=measure,freq=freq,name=self.ui.txt_perform_name.text(),lines=None,mdl=model,src_sink_type=self.perform_devices_pins,device_state=self.device_states_df)
        elif self.ui.cmb_perform_elecTherm.currentText() == "Thermal":
            # get type
            # get type
            if self.ui.cmb_thermal_model.currentText() == "Fast Thermal (FEM)":
                model = 'TFSM_MODEL'
            elif self.ui.cmb_thermal_model.currentText() == "Rectangle Flux":
                model = 'RECT_FLUX_MODEL'

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
            performance_measure = ThermalMeasure(stat_fn,self.perform_devices,self.ui.txt_perform_name.text(),model)
        
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
        # print len(self.perf_items)
     
        # clear everything
        self.ui.txt_perform_name.setText('')
        # uncolor everything
        for device in self.perform_devices:
            self.parent.patch_dict.get_patch(device, 3).set_facecolor(self.parent.default_color)
            self.perform_devices=[]
        for line in self.perform_lines:
            self.parent.patch_dict.get_patch(line, 3).set_facecolor(self.parent.default_color)
            self.perform_lines=[]
        self.parent.symb_canvas[3].draw()
        # Reset everything
        self.ui.lbl_perform_step3.setEnabled(False)
        self.ui.cmb_thermal_model.setEnabled(False)
        self.ui.cmb_elec_model.setEnabled(False)
        self.ui.lbl_sel_electrical_model.setEnabled(False)
        self.ui.lbl_perform_step3.setEnabled(False)
        self.ui.lbl_perform_step4.setEnabled(False)
        self.ui.btn_perform_addPerformance.setEnabled(False)
        self.ui.btn_setup_device_state.setEnabled(False)
        self.ui.lbl_perform_step3.setText("Step 3:  Select Devices/Leads.")
        self.ui.tbl_performance.setEnabled(True)

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

    def show_selected(self):
        print self.ui.tbl_performance