# Collecting layout information from CornerStitch, ask user to setup the connection and show the loop
from powercad.electrical_mdl.spice_eval.rl_mat_eval import *
from powercad.electrical_mdl.e_mesh import *
from powercad.corner_stitch.input_script import *
from powercad.parasitics.mdl_compare import load_mdl
import cProfile
import pstats
from mpl_toolkits.mplot3d import Axes3D
from collections import deque

class ElectricalMeasure(object):
    MEASURE_RES = 1
    MEASURE_IND = 2
    #MEASURE_CAP = 3

    UNIT_RES = ('mOhm', 'milliOhm')
    UNIT_IND = ('nH', 'nanoHenry')
    #UNIT_CAP = ('pF', 'picoFarad')

    def __init__(self, measure, name, source, sink):

        self.name = name
        self.measure = measure
        self.source = source
        self.sink = sink

class CornerStitch_Emodel_API:
    # This is an API with NewLayout Engine
    def __init__(self, comp_dict={}, layer_to_z={}, wire_conn={}):
        '''

        :param comp_dict: list of all components and routing objects
        :param layer_to_z: a simple layerstack info for thickness and elevation of each layer
        :param wire_conn: a simple table for bondwires setup
        '''
        self.pins = None
        self.comp_dict = comp_dict
        self.layer_to_z = layer_to_z
        self.conn_dict = {}  # key: comp name, Val: list of connecition based on the connection table input
        self.wire_dict = wire_conn  # key: wire name, Val list of data such as wire radius,
        # wire distance, number of wires, start and stop position
        # and bondwire object
        self.module = None
        self.freq = 1000  # kHz
        self.width = 0
        self.height = 0
        self.measure = []

    def form_connection_table(self, dev_conn=None):
        '''
        Form a connection table only once, which can be reused for multiple evaluation
        :return: update self.conn_dict
        '''

        if dev_conn==None:
            for c in self.comp_dict:
                comp = self.comp_dict[c]
                if isinstance(comp, Part):
                    if comp.type == 1:
                        name = comp.layout_component_id
                        table = Connection_Table(name=name, cons=comp.conn_dict)
                        table.set_up_table_cmd()
                        self.conn_dict[name] = table.states
        else:
            for c in self.comp_dict:
                comp = self.comp_dict[c]
                if isinstance(comp, Part):
                    if comp.type == 1:
                        name = comp.layout_component_id
                        self.conn_dict[name] = dev_conn[name]

    def get_frequency(self, frequency=None):
        if frequency==None:
            freq=raw_input("Frequency for the extraction in kHz:")
            self.freq=float(freq)
        else:
            self.freq=frequency
    def load_rs_model(self, mdl_file):
        self.rs_model = load_mdl(file=mdl_file)

    def init_layout(self, layout_data=None):
        '''
        Read part info and link them with part info, from an updaed layout, update the electrical network
        :return: updating self.e_sheets, self.e_plates
        '''
        sig = 4
        # UPDATE ALL PLATES and SHEET FOR THE LAYOUT
        #print "data"
        #print layout_data
        self.layout_data = layout_data.values()[0]
        self.width, self.height = layout_data.keys()[0]
        #self.width = round(self.width/1000.0, sig)
        #self.height = round(self.height/1000.0, sig)
        self.e_plates = []  # list of electrical components
        self.e_sheets = []  # list of sheets for connector presentaion
        self.e_comps = []  # list of all components
        self.net_to_sheet = {}  # quick look up table to find the sheet object based of the net_name
        # Update based on layout info
        for k in self.layout_data:
            data = self.layout_data[k]
            for rect in data:
                x, y, w, h = [rect.x, rect.y, rect.width,
                              rect.height]  # convert from integer to float TODO: send in correct data
                #x = x / 1000
                #y = y / 1000
                #w = w / 1000
                #h = h / 1000
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
                        z = self.layer_to_z[type][0]
                        new_rect = Rect(top=(y + h)/1000, bottom=y / 1000, left=x / 1000, right=(x + w) / 1000)

                        pin = Sheet(rect=new_rect, net_name=k, net_type='internal', n=(0, 0, 1), z=z)
                        self.e_sheets.append(pin)
                        # need to have a more generic way in the future
                        self.net_to_sheet[k] = pin
                    elif isinstance(obj, Part):
                        if obj.type == 0:  # If this is lead type:
                            new_rect = Rect(top=(y + h) / 1000, bottom=y / 1000, left=x / 1000, right=(x + w) / 1000)
                            z = self.layer_to_z[type][0]
                            pin = Sheet(rect=new_rect, net_name=k, net_type='internal', n=(0, 0, 1), z=z)
                            self.net_to_sheet[k] = pin
                            self.e_sheets.append(pin)
                        elif obj.type == 1:  # If this is a component
                            dev_name = obj.layout_component_id
                            dev_pins = []  # all device pins
                            dev_conn_list = []  # list of device connection pairs
                            dev_para = []  # list of device connection internal parasitic for corresponded pin
                            for pin_name in obj.pin_locs:
                                net_name = dev_name + '_' + pin_name
                                locs = obj.pin_locs[pin_name]
                                px, py, pwidth, pheight, side = locs
                                if side == 'B':  # if the pin on the bottom side of the device
                                    z = self.layer_to_z[type][0]
                                elif side == 'T':  # if the pin on the top side of the device
                                    z = self.layer_to_z[type][0] + obj.thickness
                                top = y/1000 + (py + pheight)
                                bot = y / 1000 + py
                                left =x / 1000+ px
                                right =x / 1000+ (px + pwidth)
                                rect = Rect(top=top, bottom=bot, left=left, right=right)
                                pin = Sheet(rect=rect,net_name=net_name,z=z)
                                self.net_to_sheet[net_name] = pin
                                dev_pins.append(pin)
                            # Todo: need to think of a way to do this only once
                            dev_conns = self.conn_dict[dev_name]  # Access the connection table
                            for conn in dev_conns:
                                if dev_conns[conn] == 1:  # if the connection is selected
                                    pin1 = dev_name + '_' + conn[0]
                                    pin2 = dev_name + '_' + conn[1]
                                    dev_conn_list.append([pin1, pin2])  # update pin connection
                                    dev_para.append(obj.conn_dict[conn])  # update intenal parasitics values

                            self.e_comps.append(
                                EComp(sheet=dev_pins, conn=dev_conn_list, val=dev_para))  # Update the component

        self.make_wire_table()
        # Update module object
        self.module = EModule(plate=self.e_plates, sheet=self.e_sheets, components=self.wires + self.e_comps)
        self.module.form_group()
        self.module.split_layer_group()
        hier = EHier(module=self.module)
        hier.form_hierachy()
        self.emesh = EMesh(hier_E=hier, freq=self.freq, mdl=self.rs_model)
        self.emesh.mesh_grid_hier(corner_stitch=True)
        self.emesh.update_trace_RL_val()
        self.emesh.update_hier_edge_RL()
        #pr = cProfile.Profile()
        #pr.enable()
        #fig = plt.figure(4)
        #ax = Axes3D(fig)
        #ax.set_xlim3d(0, 42)
        #ax.set_ylim3d(0, 80)
        #ax.set_zlim3d(0, 2)
        #self.emesh.plot_3d(fig=fig, ax=ax, show_labels=True)
        #plt.show()
        self.emesh.mutual_data_prepare(mode=0)
        self.emesh.update_mutual(mode=0)
        #pr.disable()
        #pr.create_stats()
        #file = open('C:\Users\qmle\Desktop\New_Layout_Engine\New_design_flow\mystats.txt', 'w')
        #stats = pstats.Stats(pr, stream=file)
        #stats.sort_stats('time')
        #stats.print_stats()

    def make_wire_table(self):
        self.wires = []
        for w in self.wire_dict:
            wire_data = self.wire_dict[w]  # get the wire data
            wire_obj = wire_data['BW_object']
            num_wires = int(wire_data['num_wires'])
            start = wire_data['Source']
            stop = wire_data['Destination']
            s1 = self.net_to_sheet[start]
            s2 = self.net_to_sheet[stop]
            spacing = float(wire_data['spacing'])
            wire = EWires(wire_radius=wire_obj.radius, num_wires=num_wires, wire_dis=spacing, start=s1, stop=s2,
                       wire_model=None,
                       frequency=self.freq, circuit=RL_circuit())

            self.wires.append(wire)

    def plot_3d(self):
        fig = plt.figure(1)
        ax = a3d.Axes3D(fig)
        ax.set_xlim3d(-2, self.width + 2)
        ax.set_ylim3d(-2, self.height + 2)
        ax.set_zlim3d(0, 2)
        ax.set_aspect('equal')
        plot_rect3D(rect2ds=self.module.plate + self.module.sheet, ax=ax)
        fig = plt.figure(2)
        ax = a3d.Axes3D(fig)
        ax.set_xlim3d(-2, self.width + 2)
        ax.set_ylim3d(-2, self.height + 2)
        ax.set_zlim3d(0, 2)
        ax.set_aspect('equal')
        self.emesh.plot_3d(fig=fig, ax=ax, show_labels=True)
        plt.show()

    def measurement_setup(self,meas_data=None):
        if meas_data==None:
            # Print source sink table:
            print "List of Pins:"
            for c in self.comp_dict:
                comp = self.comp_dict[c]
                if isinstance(comp, Part):
                    if comp.type == 0:
                        print ("Connector:",comp.layout_component_id)
                    elif comp.type ==1:
                        for p in comp.pin_name:
                            print("Device pins:",comp.layout_component_id+'_'+p)
            # Only support single loop extraction for now.
            name = raw_input("Loop name:")
            type = int(raw_input("Measurement type (0 for Resistance, 1 for Inductance):"))
            source = raw_input("Source name:")
            sink = raw_input("Sink name:")
            self.measure.append(ElectricalMeasure(measure=type,name=name,source=source,sink=sink))
            return self.measure
        else:
            name = meas_data['name']
            type = meas_data['type']
            source =meas_data['source']
            sink = meas_data['sink']
            self.measure.append(ElectricalMeasure(measure=type, name=name, source=source, sink=sink))
            return self.measure
    def extract_RL(self,src=None,sink=None):
        '''
        Input src and sink name, then extract the inductance/resistance between them
        :param src:
        :param sink:
        :return:
        '''
        pt1 = self.emesh.comp_net_id[src]
        pt2 = self.emesh.comp_net_id[sink]
        circuit = RL_circuit()
        circuit._graph_read(self.emesh.graph)
        circuit.m_graph_read(self.emesh.m_graph)
        circuit.assign_freq(self.freq)
        circuit.indep_current_source(pt1, 0, 1)
        #print "src",pt1,"sink",pt2
        circuit._add_termial(pt2)
        circuit.build_current_info()
        circuit.solve_iv()
        vname = 'v' + str(pt1)
        imp = circuit.results[vname]
        R = abs(np.real(imp)*1e3)
        L = abs(np.imag(imp)) * 1e9 / (2 * np.pi * circuit.freq)
        print R,L
        return R[0],L[0]
