# Collecting layout information from CornerStitch, ask user to setup the connection and show the loop
from powercad.design.parts import *
from powercad.electrical_mdl.e_module import *
from powercad.electrical_mdl.e_struct import *
from powercad.general.data_struct.util import Rect
import networkx as nx
from powercad.corner_stitch.input_script import *


class CS_API:
    # This is an API with cornerstitch
    def __init__(self, comp_dict={}, layout_data=[], layer_to_z={}):
        self.pins = None
        self.comp_dict = comp_dict
        self.layout_data = layout_data
        self.e_plates = []  # list of electrical components
        self.e_sheets = []  # list of sheets for connector presentaion
        self.e_comps = []  # list of all components
        self.layer_to_z = layer_to_z
        self.conn_dict = {}  # key: comp name, Val: list of connecition based on the connection table input

    def form_connection_table(self):
        '''
        Form a connection table only once, which can be reused for multiple evaluation
        :return: update self.conn_dict
        '''
        for c in self.comp_dict:
            comp = self.comp_dict[c]
            print comp.layout_component_id,comp.type
            if isinstance(comp,Part):
                if comp.type==1:
                    name = comp.layout_component_id
                    table = Connection_Table(name=name, cons=comp.conn_dict)
                    table.set_up_table()
                    self.conn_dict[name] = table.states
                    print self.conn_dict

    def read_parts_to_sheets(self):
        '''
        Read part info and link them with part info
        :return: updating self.e_sheets, self.e_plates
        '''
        # UPDATE ALL PLATES and SHEET FOR THE LAYOUT
        for k in self.layout_data:
            data = self.layout_data[k]
            for rect in data:
                x, y, w, h = rect / 1000.0  # convert from integer to float TODO: send in correct data
                new_rect = Rect(top=y + h, bottom=y, left=x, right=x + w)
                p = E_plate(rect=new_rect, z=self.layer_to_z['T'][0], dz=self.layer_to_z['T'][1])
                self.e_plates.append(p)
                type = k[0]

                if type in ['B', 'D', 'L']:  # if this is bondwire pad or device or lead type.
                    # Below we need to link the pad info and update the sheet list
                    # Get the object
                    obj = self.comp_dict[k]
                    if isinstance(obj, RoutingPath):  # If this is a routing object
                        # reuse the rect info and create a sheet
                        self.e_sheets.append(Sheet(rect=new_rect, net_name=k, net_type='internal', n=(0, 0, 1), z=
                        self.layer_to_z[type][0]))  # For now assume all z direction to be up
                        # need to have a more generic way in the future
                    elif isinstance(obj, Part):
                        if obj.type == 0:  # If this is lead type:
                            self.e_sheets.append(Sheet(rect=new_rect, net_name=k, net_type='internal', n=(0, 0, 1), z=
                            self.layer_to_z[k[0]][0]))  # For now assume all z direction to be up
                        elif obj.type == 1:  # If this is a component
                            dev_name = obj.layout_component_id
                            dev_pins = []  # all device pins
                            dev_conn = []  # list of device connection pairs
                            dev_para = []  # list of device connection internal parasitic for corresponded pin
                            for pin_name in obj.pin_locs:
                                net_name = dev_name + '_' + pin_name
                                locs = obj.pin_locs[pin_name]
                                x, y, width, height, side = locs
                                if side == 'B':  # if the pin on the bottom side of the device
                                    z = self.layer_to_z[type][0]
                                elif side == 'T':  # if the pin on the top side of the device
                                    z = self.layer_to_z[type][0] + obj.thickness
                                pin = Sheet(rect=Rect(top=y + height, bottom=y, left=x, right=x + width),
                                            net_name=net_name,
                                            z=z)
                                dev_pins.append(pin)







