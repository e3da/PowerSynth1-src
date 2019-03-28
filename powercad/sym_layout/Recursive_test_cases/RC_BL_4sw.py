# This will test the new lumped graph structure along with Kelvin connection
#@authors: Quang Le
import os

import matplotlib.pyplot as plt
import networkx as nx

from powercad.spice_handler.spice_import.NetlistImport import Netlist, Netlis_export_ADS
from powercad.design.module_data import gen_test_module_data_BL
from powercad.general.settings import settings
from powercad.interfaces.FastHenry.fh_layers import output_fh_script, read_result
from powercad.parasitics.analytical.analysis import parasitic_analysis
from powercad.sym_layout.Recursive_test_cases.map_id_net import map_id_net
from powercad.sym_layout.plot import plot_layout
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure
from powercad.tech_lib.test_techlib import get_dieattach, get_mosfet
from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
from powercad.tech_lib.test_techlib import get_signal_lead, get_power_lead


def make_test_symmetries(sym_layout):
    symm1 = []
    symm2 = []

    for obj in sym_layout.all_sym:
        if obj.element.path_id == '0009' or obj.element.path_id == '0010':
            symm1.append(obj)
        if obj.element.path_id == '0000' or obj.element.path_id == '0001':
            symm2.append(obj)

    sym_layout.symmetries.append(symm1)
    sym_layout.symmetries.append(symm2)


def make_test_constraints(symbols):
    for obj in symbols:
        if obj.element.path_id.count('c1') > 0:
            obj.constraint = (None, None, 1.27)
        if obj.element.path_id.count('c2') > 0:
            obj.constraint = (4.8, 10.0, None)


def make_test_devices(symbols, dev,dev_id):
    # symbols list of all SymLine and SymPoints in a loaded layout (sym_layout.all_sym)
    for obj in symbols:
        for id in dev_id:
            if obj.element.path_id == id:
                obj.tech = dev


def make_test_leads(symbols, lead_type,lead_id):
    for obj in symbols:
        for id in lead_id:
            if obj.element.path_id == id:
                obj.tech = lead_type


def make_test_bonds(symbols, bond_type, bond_id,wire_spec):
    for obj in symbols:
        for id in bond_id:
            if obj.element.path_id == id:
                obj.make_bondwire(bond_type)
                obj.wire_sep = wire_spec[0]
                obj.num_wires = wire_spec[1]


def make_test_design_values(sym_layout, dimlist, default):
    hdv = []
    vdv = []
    dev_dv = []

    for i in sym_layout.h_dv_list:
        hdv.append(default)

    for i in sym_layout.v_dv_list:
        vdv.append(default)

    for i in sym_layout.devices:
        dev_dv.append(default)

    for sym in sym_layout.all_sym:
        if 'id' in sym.element.path_id:
            pos = sym.element.path_id.find('id')
            id = int(sym.element.path_id[pos + 2:pos + 2 + 1])
            dv = dimlist[id]
            if isinstance(sym, SymLine):
                if not sym.wire:
                    if sym.element.vertical:
                        hdv[sym.dv_index] = dv
                    else:
                        vdv[sym.dv_index] = dv
            elif isinstance(sym, SymPoint) and isinstance(sym.tech, DeviceInstance):
                dev_dv[sym.dv_index] = dv

    return hdv, vdv, dev_dv


def add_test_measures(sym_layout):
    pts = []
    for sym in sym_layout.all_sym:
        if sym.element.path_id == '0013':
            pts.append(sym)
        if sym.element.path_id == '0012':
            pts.append(sym)
        if len(pts) > 1:
            break

    if len(pts) == 2:
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'MS')
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'MS')
        sym_layout.perf_measures.append(m2)

    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)

    m3 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.", 'TFSM_MODEL')
    sym_layout.perf_measures.append(m3)
    print "perf", sym_layout.perf_measures


def setup_model(symlayout):
    for pm in symlayout.perf_measures:
        if isinstance(pm, ElectricalMeasure):
            # ctypes.windll.user32.MessageBoxA(0, pm.mdl, 'Model', 1)
            symlayout.mdl_type['E']=pm.mdl


def one_measure(symlayout):
    ret = []
    for measure in symlayout.perf_measures:
        if isinstance(measure, ElectricalMeasure):
            type = measure.mdl

            type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                         ElectricalMeasure.MEASURE_IND: 'ind',
                         ElectricalMeasure.MEASURE_CAP: 'cap'}
            measure_type = type_dict[measure.measure]
            if measure.measure == ElectricalMeasure.MEASURE_CAP:
                val = symlayout._measure_capacitance(measure)
            else:
                # Measure res. or ind. from src node to sink node
                src = measure.pt1.lumped_node
                sink = measure.pt2.lumped_node
                id = symlayout.mdl_type['E'].index(type)
                node_dict = {}
                index = 0
                for n in symlayout.lumped_graph.nodes():
                    node_dict[n] = index
                    index += 1
                val = parasitic_analysis(symlayout.lumped_graph, src, sink, measure_type,node_dict)
                    #                    print measure_type, val
            ret.append(val)


        elif isinstance(measure, ThermalMeasure):
            type = measure.mdl
            if type == 'TFSM_MODEL':
                type_id = 1
            elif type == 'RECT_FLUX_MODEL':
                type_id = 2
            elif type == 'Matlab':
                type_id = 3
            val = symlayout._thermal_analysis(measure, type_id)
            ret.append(val)
    return ret
def plot_lumped_graph(sym_layout):
    pos = {}
    for n in sym_layout.lumped_graph.nodes():
        pos[n] = sym_layout.lumped_graph.node[n]['point']
    nx.draw_networkx(sym_layout.lumped_graph, pos)
    plt.show()
    plot_layout(sym_layout)

def make_test_setup2(f,directory):

    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script
    name_file=None
    #sym_layout.assign_name(name_file)

    layout_ratio = 2.0
    dev_mos = DeviceInstance(0.1, 5.0, get_mosfet(layout_ratio),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = get_power_lead()  # Get a power lead object

    sig_lead = get_signal_lead(layout_ratio)  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object
    # This will be added into the UI later based on Tristan import
    net_id={'0013':'DC_plus','0012':'DC_neg','0016':'G_High','0015':'G_Low','0014':'Out','0010':'M1','0011':'M2','0008':'M3',
            '0009':'M4'}
    map_id_net(dict=net_id,symbols=sym_layout.all_sym)

    make_test_leads(symbols=sym_layout.all_sym, lead_type=sig_lead,
                    lead_id=['0016','0015','0014', '0013','0012'])
    '''make_test_leads(symbols=sym_layout.all_sym, lead_type=pow_lead,
                    lead_id=[])'''
    make_test_bonds(symbols=sym_layout.all_sym, bond_type=signal_bw,
                    bond_id=['0019', '0023','0022','0026'], wire_spec=[2, 10])
    make_test_bonds(symbols=sym_layout.all_sym, bond_type=power_bw,
                    bond_id=['0024','0020','0021','0025'], wire_spec=[2, 10])
    make_test_devices(symbols=sym_layout.all_sym,dev=dev_mos,dev_id=['0008','0009','0010','0011'])

    # make_test_symmetries(sym_layout) # You can assign the symmetry objects here

    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data_BL(f, 100, 300.0, layout_ratio)
    # Pepare for optimization.

    sym_layout.form_design_problem(module, temp_dir) # Collect data to user interface
    sym_layout._map_design_vars()
    setup_model(sym_layout)
    #sym_layout.optimize()
    # layout 1
    #individual = [8.832333588157837, 11.47321729522074, 11.47321729522074, 11.47321729522074, 2.0, 4.554984513520513, 4.412775882777208, 4.412775882777208, 4.685335776775386, 2, 4.412775882777208, 0.32383276483316237, 0.0, 0.3, 0.9]
    # layout 2
    individual = [8.832333588157837, 11.47321729522074, 11.47321729522074, 11.47321729522074, 2.0, 4.554984513520513, 4.412775882777208, 4.412775882777208, 4.685335776775386, 2, 4.412775882777208, 0.32383276483316237, 0.0, 0.52383276483316237, 0.8]
    # layout 3
    #individual = [8.832333588157837, 11.47321729522074, 11.47321729522074, 11.47321729522074, 2.0, 4.554984513520513, 4.412775882777208, 4.412775882777208, 4.685335776775386, 2, 4.412775882777208, 0.32383276483316237, 0.0, 0.75, 0.95]
    # layout 4
    #individual = [8.832333588157837, 11.47321729522074, 11.47321729522074, 11.47321729522074, 2.0, 4.554984513520513, 4.412775882777208, 4.412775882777208, 4.685335776775386, 2, 4.412775882777208, 0.35, 0.55, 0.75, 0.95]

    individual=[i*layout_ratio if i>1 else i for i in individual] # layout i ratio i
    individual_spara =[4.723828657253275, 16.472407757897972, 3.027772807643007, 0.7291915966525637, 0.34930748270444323, 0.1808883006719934, 0.3962145355607477]
    print 'individual', individual
    print "opt_to_sym_index", sym_layout.opt_to_sym_index
    sym_layout.rev_map_design_vars(individual)
    sym_layout.generate_layout()
    plot_layout(sym_layout)
    plt.show()
    sym_layout._build_lumped_graph()
    #sym_layout.E_graph.export_graph_to_file(sym_layout.lumped_graph)
    # form netlist assignment form netlist import
    netlist= Netlist('Netlist//H_bridge4sw.txt')
    netlist.form_assignment_list_fh()
    external=netlist.get_external_list_fh()
    output_fh_script(sym_layout,"C:\Users\qmle\Desktop\Balancing\Mutual_test\layout cases//BL_layout_pos1_200",external=external)

    #plot_lumped_graph(sym_layout)
    #print one_measure(sym_layout)
def make_netlist():
    netlist = Netlist('Netlist//H_bridge4sw.txt')
    netlist.form_assignment_list_fh()
    net_data = read_result("C:\Users\qmle\Desktop\Balancing\Mutual_test\layout cases//fh_results//BL_layout_pos1_200.inp.M.txt")
    df, pm = netlist.get_assign_df()
    ads_net = Netlis_export_ADS(df=df, pm=pm)
    ads_net.import_net_data(net_data)
    ads_net.export_ads('RC_BL_4sw_pos1_200.net')

def random_layout(directory):
    ''' Test generate layout time for WIPDA (Imam)'''
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script
    layout_ratio = 1.0
    dev_mos = DeviceInstance(0.1, 5.0, get_mosfet(layout_ratio),
                             get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = get_power_lead()  # Get a power lead object

    sig_lead = get_signal_lead(layout_ratio)  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object
    # This will be added into the UI later based on Tristan import
    net_id = {'0013': 'DC_plus', '0012': 'DC_neg', '0016': 'G_High', '0015': 'G_Low', '0014': 'Out', '0010': 'M1',
              '0011': 'M2', '0008': 'M3',
              '0009': 'M4'}
    map_id_net(dict=net_id, symbols=sym_layout.all_sym)

    make_test_leads(symbols=sym_layout.all_sym, lead_type=sig_lead,
                    lead_id=['0016', '0015', '0014', '0013', '0012'])
    '''make_test_leads(symbols=sym_layout.all_sym, lead_type=pow_lead,
                    lead_id=[])'''
    make_test_bonds(symbols=sym_layout.all_sym, bond_type=signal_bw,
                    bond_id=['0019', '0023', '0022', '0026'], wire_spec=[2, 10])
    make_test_bonds(symbols=sym_layout.all_sym, bond_type=power_bw,
                    bond_id=['0024', '0020', '0021', '0025'], wire_spec=[2, 10])
    make_test_devices(symbols=sym_layout.all_sym, dev=dev_mos, dev_id=['0008', '0009', '0010', '0011'])

    # make_test_symmetries(sym_layout) # You can assign the symmetry objects here

    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data_BL(f, 100, 300.0, layout_ratio)
    # Pepare for optimization.

    sym_layout.form_design_problem(module, temp_dir)  # Collect data to user interface
    sym_layout._map_design_vars()
    setup_model(sym_layout)

def test1():
    # The test goes here, moddify the path below as you wish...
    directory ='Layout//balancing_4sw.psc' # directory to layout script
    #make_test_setup2(100.0,directory)
    make_netlist()


