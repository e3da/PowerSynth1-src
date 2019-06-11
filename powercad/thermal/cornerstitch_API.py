# for corner stitch need to use analytical model since the layout size can be changed



from PySide.QtGui import QFileDialog
from powercad.layer_stack.layer_stack_import import LayerStackHandler
from PySide import QtCore, QtGui
from powercad.design.module_data import *
from powercad.thermal.rect_flux_channel_model import Baseplate, ExtaLayer, Device, layer_average, \
    compound_top_surface_avg
from powercad.design.parts import Part
import sys
from collections import deque

class ThermalMeasure(object):
    FIND_MAX = 1
    FIND_AVG = 2
    FIND_STD_DEV = 3
    Find_All = 4

    UNIT = ('K', 'Kelvin')

    def __init__(self, devices=None, name=None):
        self.devices = devices
        self.name = name


class Thermal_data_collect_main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)


class CornerStitch_Tmodel_API:
    def __init__(self, comp_dict={}):
        self.width = 0  # substrate width
        self.height = 0  # substrate height
        self.layer_stack_import = None
        self.comp_dict = comp_dict
        self.model = 'analytical'  # or 'characterized'
        self.thermal_main = Thermal_data_collect_main()  # a fake main window to link with some dialogs
        self.module_data = ModuleData()
        self.devices = {}
        self.dev_powerload_table = {}
        self.mat_lib = '..//..//..//tech_lib//Material//Materials.csv'
        self.measure = []

    def import_layer_stack(self, filename=None):  # Import layer stack from CSV file
        prev_folder = 'C://'
        # print filename
        # Open a layer stack CSV file and extract the layer stack data from it

        if filename == None:
            layer_stack_csv_file = QFileDialog.getOpenFileName(self.thermal_main, "Select Layer Stack File",
                                                               prev_folder, "CSV Files (*.csv)")
            layer_stack_csv_file = layer_stack_csv_file[0]
        else:
            layer_stack_csv_file = filename
        self.layer_stack_import = LayerStackHandler(layer_stack_csv_file, mat_lib=self.mat_lib)
        self.layer_stack_import.import_csv()

        if self.layer_stack_import.compatible:
            self.module_data.baseplate = self.layer_stack_import.baseplate
            self.module_data.substrate_attach = self.layer_stack_import.substrate_attach
            self.module_data.substrate = self.layer_stack_import.substrate



    def set_up_thermal_props(self, layout_data=None):  # for analytical model of a simple 6 layers
        baseplate = self.module_data.baseplate
        sub = self.module_data.substrate.substrate_tech
        sub_attach = self.module_data.substrate_attach
        met = (sub.metal_thickness, sub.metal_properties.thermal_cond)
        iso = (sub.isolation_thickness, sub.isolation_properties.thermal_cond)
        attach = (sub_attach.thickness, sub_attach.attach_tech.properties.thermal_cond)
        thickness, thermal_cond = layer_average([met, iso, met, attach])
        layer = ExtaLayer(thickness * 1e-3, thermal_cond)
        self.width, self.height = layout_data.keys()[0]
        self.width = round(self.width / 1000.0, 3)
        self.height = round(self.height / 1000.0, 3)
        # thermal baseplate object
        t_bp = Baseplate(width=(self.width + 2) * 1e-3,
                         length=(self.height + 2) * 1e-3,
                         thickness=baseplate.dimensions[2] * 1e-3,
                         conv_coeff=self.bp_conv,
                         thermal_cond=baseplate.baseplate_tech.properties.thermal_cond)
        # device thermal
        devices = []
        self.layout_data = layout_data.values()[0]
        for k in self.devices:
            dev = self.devices[k]
            dev_heat_flow = self.dev_powerload_table[k]
            dev_rect = self.layout_data[k][0]
            device = Device(width=dev.footprint[0] * 1e-3,
                            length=dev.footprint[1] * 1e-3,
                            center=(dev_rect.center_x() * 1e-3, dev_rect.center_y() * 1e-3),
                            Q=dev_heat_flow)
            devices.append(device)
        return t_bp, layer, devices

    def dev_result_table_eval(self, layout_data=None):
        t_bp, layer, devices = self.set_up_thermal_props(layout_data)
        self.temp_res = {}
        for k in self.devices:
            # Find extra temp. through die
            dev = self.devices[k]
            A = dev.footprint[0] * dev.footprint[1] * 1e-6
            t1 = dev.thickness * 1e-3
            res = t1 / (A * dev.thermal_cond)
            dev_delta = res * self.dev_powerload_table[k]

            temp = compound_top_surface_avg(t_bp, layer, devices, self.devices.keys().index(k))
            temp += self.t_amb + dev_delta
            self.temp_res[k] = temp

    def set_up_device_power(self, data=None):
        if data==None:
            print "load a table to collect power load"
            for k in self.comp_dict:
                comp = self.comp_dict[k]
                if isinstance(comp, Part):
                    if comp.type == 1:  # if this is a component
                        self.devices[comp.layout_component_id] = comp
                        value = raw_input("enter a power for " + comp.layout_component_id + ": ")
                        self.dev_powerload_table[comp.layout_component_id] = float(value)
            value = raw_input("enter a value for heat convection coefficient of the baseplate:")
            self.bp_conv = float(value)
            value = raw_input("enter a value for ambient temperature:")
            self.t_amb = float(value)
        else:
            power_list = deque(data['Power']) # pop from left to right
            for k in self.comp_dict:
                comp = self.comp_dict[k]
                if isinstance(comp, Part):
                    if comp.type == 1:  # if this is a component
                        self.devices[comp.layout_component_id] = comp
                        value = power_list.popleft()
                        self.dev_powerload_table[comp.layout_component_id] = float(value)
            self.bp_conv = float(data['heat_conv'])
            self.t_amb = float(data['t_amb'])

    def measurement_setup(self,data=None):
        if data ==None:
            print "List of Devices:"
            for device in self.devices:
                print device
            num_measure = int(raw_input("Input number of thermal measurements:"))

            for i in range(num_measure):
                name = raw_input("Enter a name for this thermal measurement")
                print "Type in a list of devices above separated by commas"
                input = raw_input("Input sequence here:")
                devices = tuple(input.split(','))
                self.measure.append(ThermalMeasure(devices=devices, name=name))
            return self.measure
        else: # Only support single measure for now.
            name = data['name']
            devices = data['devices']
            self.measure.append(ThermalMeasure(devices=devices, name=name))
            return self.measure

    def eval_max_temp(self, layout_data):
        self.dev_result_table_eval(layout_data)
        return max(self.temp_res.values())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    cs_temp = CornerStitch_Tmodel_API()
    cs_temp.import_layer_stack()