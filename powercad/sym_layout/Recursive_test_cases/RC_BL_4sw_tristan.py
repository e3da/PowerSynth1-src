# This will test the new lumped graph structure along with Kelvin connection
#@authors: Quang Le
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from powercad.spice_handler.spice_import.NetlistImport import Netlist, Netlis_export_ADS
from powercad.design.module_data import gen_test_module_data_BL_te
from powercad.design.module_design import ModuleDesign
from powercad.general.settings import settings
from powercad.general.settings.save_and_load import load_file
from powercad.interfaces.EMPro.EMProExport import EMProScript
from powercad.interfaces.FastHenry.fh_layers import read_result
from powercad.parasitics.analytical.analysis import parasitic_analysis
from powercad.sym_layout.Recursive_test_cases.Netlist.circuit import Circuit
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
        if obj.element.path_id == 'T7' or obj.element.path_id == 'T8':
            symm1.append(obj)
        if obj.element.path_id == 'T1' or obj.element.path_id == 'T2':
            symm2.append(obj)

    sym_layout.symmetries.append(symm1)
    sym_layout.symmetries.append(symm2)


def make_test_constraints(symbols):
    for obj in symbols:
        if obj.element.path_id == 'T1' or obj.element.path_id == 'T2' or obj.element.path_id == 'T7' or obj.element.path_id == 'T8':
            obj.constraint = (None, None, 2.0)

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

def make_dev_states(symbols):
    for obj in symbols:
        if isinstance(obj,SymPoint):
            if obj.name[0]=='M':
                obj.states=[0,1,0]
def make_test_bonds(df, bw_sig, bw_power):
    bw_data = [['POWER', 'M4', 'T4', 'a', bw_power],
               ['POWER', 'M2', 'T5', 'a', bw_power],
               ['POWER', 'M1', 'T5', 'a', bw_power],
               ['POWER', 'M3', 'T4', 'a', bw_power],
               ['SIGNAL', 'M4', 'T2', 'a', bw_sig],
               ['SIGNAL', 'M2', 'T7', 'a', bw_sig],
               ['SIGNAL', 'M1', 'T7', 'a', bw_sig],
               ['SIGNAL', 'M3', 'T2', 'a', bw_sig]]
    cols = ['bw_type', 'start', 'stop', 'obj']
    for row in range(8):
        for col in range(5):
            df.loc[row, col] = bw_data[row][col]
    print(df)
    print(df.iloc[0, 0])
    return df

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
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'RS')
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'RS')
        sym_layout.perf_measures.append(m2)

    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)

    m3 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.", 'TFSM_MODEL')
    sym_layout.perf_measures.append(m3)
    print("perf", sym_layout.perf_measures)


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

    layout_ratio = 1.0
    dev_mos = DeviceInstance(0.1, 5.0, get_mosfet(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = get_power_lead()  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object
    # This will be added into the UI later based on Tristan import
    net_id={'L2':'DC_plus','L1':'DC_neg','L5':'G_High','L4':'G_Low','L3':'Out','M1':'M1','M2':'M2','M3':'M3',
            'M4':'M4'}
    map_id_net(dict=net_id,symbols=sym_layout.all_sym)

    make_test_leads(symbols=sym_layout.all_sym, lead_type=sig_lead,
                    lead_id=['L4','L5'])
    make_test_leads(symbols=sym_layout.all_sym,lead_type=pow_lead,lead_id=['L1', 'L2','L3'])

    table_df = pd.DataFrame()

    table_df = make_test_bonds(table_df, signal_bw, power_bw)

    make_test_devices(symbols=sym_layout.all_sym,dev=dev_mos,dev_id=['M1','M2','M3','M4'])
    make_dev_states(sym_layout.all_sym)
    make_test_symmetries(sym_layout) # You can assign the symmetry objects here
    make_test_constraints(sym_layout.all_sym)
    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data_BL_te(f, 100, 300.0)
    # Pepare for optimization.
    sym_layout.form_design_problem(module, table_df, temp_dir)  # Collect data to user interface

    sym_layout._map_design_vars()
    setup_model(sym_layout)
    #sym_layout.optimize()
    individual=[11.374, 11.2557, 17.265866846201355, 15.45, 2.0, 4.611548973825832, 3.77, 0.059880225267239205, 0.3988074701262332, 0.4894976020309876, 1.0]
    print(len(individual))
    print('individual', individual)
    print("opt_to_sym_index", sym_layout.opt_to_sym_index)
    sym_layout.rev_map_design_vars(individual)
    sym_layout.generate_layout()
    plot_layout(sym_layout)
    #plt.show()

    mdl = load_file("C:\\Users\qmle\Desktop\Testing\FastHenry\Fasthenry3_test_gp\WorkSpace//high_f_bl.rsmdl")
    sym_layout.mdl_type['E'] = 'RS'
    sym_layout.set_RS_model(mdl)

    sym_layout._build_lumped_graph()

    this_circuit=Circuit()
    this_circuit._graph_read(sym_layout.lumped_graph)
    #sym_layout.E_graph.export_graph_to_file(sym_layout.lumped_graph)
    # form netlist assignment form netlist import
    netlist= Netlist('Netlist//H_bridge4sw.txt')
    #netlist.form_assignment_list_fh()
    #external=netlist.get_external_list_fh()
    #output_fh_script(sym_layout,"C:\Users\qmle\Desktop\Balancing\Mutual_test\layout cases//BL_layout_pos_TE",external=external)
    ads_net = Netlis_export_ADS(df=this_circuit.df_circuit_info, pm=this_circuit.portmap)
    ads_net.export_ads2('RC_BL_4sw_TE'+'_'+str(f)+'kHz'+'.net')
    empro_script = EMProScript(ModuleDesign(sym_layout), 'RC_BL_4sw_TE' + '_' + str(f) + 'kHz'+'.py')
    empro_script.generate()
    #plot_lumped_graph(sym_layout)
    #print one_measure(sym_layout)
def make_netlist():
    netlist = Netlist('Netlist//H_bridge4sw.txt')
    netlist.form_assignment_list_fh()
    net_data = read_result("C:\\Users\qmle\Desktop\Balancing\Mutual_test\layout cases//fh_results//BL_layout_pos1_200.inp.M.txt")
    df, pm = netlist.get_assign_df()
    ads_net = Netlis_export_ADS(df=df, pm=pm)
    ads_net.import_net_data(net_data)
    ads_net.export_ads('RC_BL_4sw_pos1_200.net')


# The test goes here, moddify the path below as you wish...

directory ='Layout//balancing_4sw_te.psc' # directory to layout script
make_test_setup2(10000.0,directory)
