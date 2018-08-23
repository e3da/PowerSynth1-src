# This will test the new lumped graph structure along with Kelvin connection
#@authors: Quang Le
import os

import matplotlib.pyplot as plt
import networkx as nx

from powercad.Spice_handler.spice_import.NetlistImport import Netlist, Netlis_export_ADS
from powercad.design.module_data import gen_test_module_data_RD100
from powercad.general.settings import settings
from powercad.interfaces.FastHenry.fh_layers import output_fh_script, read_result
from powercad.parasitics.analysis import parasitic_analysis
from powercad.sym_layout.Recursive_test_cases.map_id_net import map_id_net
from powercad.sym_layout.plot import plot_layout
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure
from powercad.tech_lib.test_techlib import get_dieattach, get_mosfet
from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
from powercad.tech_lib.test_techlib import get_signal_lead, get_power_lead
import matplotlib.pyplot as plt
import pandas as pd
from powercad.interfaces.Q3D.Q3D import output_q3d_vbscript
from powercad.design.module_design import ModuleDesign


def make_test_symmetries(sym_layout):
    symm1 = []
    symm2 = []
    symm3 = []
    symm4 = []
    symm5 = []

    for obj in sym_layout.all_sym:
        if obj.element.path_id in ['Tg','Ti','Ts','Tc']:
            symm1.append(obj)
        if obj.element.path_id == 'Tl' or obj.element.path_id == 'Tb':
            symm2.append(obj)
        if obj.element.path_id == 'Tr' or obj.element.path_id == 'Tf':
            symm3.append(obj)
        if obj.element.path_id == 'Te' or obj.element.path_id == 'Tn':
            symm4.append(obj)
        if obj.element.path_id == 'Tt' or obj.element.path_id == 'Tj':
            symm5.append(obj)
    sym_layout.symmetries.append(symm1)
    sym_layout.symmetries.append(symm2)
    sym_layout.symmetries.append(symm3)
    sym_layout.symmetries.append(symm4)
    sym_layout.symmetries.append(symm5)


def make_test_constraints(sym_layout):
    for obj in sym_layout.all_sym:
        if obj.element.path_id == 'Tr' or obj.element.path_id == 'Tf':
            obj.constraint = (None, None, 2)



def make_test_devices(symbols, dev=None,dev_dict=None):
    # symbols list of all SymLine and SymPoints in a loaded layout (sym_layout.all_sym)
    if dev_dict == None: # Apply same powers
        for obj in symbols:
                if 'M' in obj.name:
                    obj.tech = dev
    else:
        for obj in symbols:
                if obj.name in dev_dict.keys():
                    obj.tech = dev_dict[obj.name]




def make_test_leads(symbols, pow_lead, sig_lead):
    for obj in symbols:
        if obj.name == 'DC_neg' or obj.name== 'DC_plus' or obj.name == 'Out':
            obj.tech = pow_lead
        elif obj.name == 'G_low' or obj.name == 'G_high':
            obj.tech = sig_lead

def make_test_bonds(df, bw_sig, bw_power):
    bw_data = [['POWER', 'M1', 'Tc', 'a', bw_power],
               ['POWER', 'M2', 'Tc', 'a', bw_power],
               ['POWER', 'M3', 'Tc', 'a', bw_power],
               ['POWER', 'M4', 'Tp', 'a', bw_power],
               ['POWER', 'M5', 'Tp', 'a', bw_power],
               ['POWER', 'M6', 'Tp', 'a', bw_power],
               ['POWER', 'M7', 'Tk', 'a', bw_power],
               ['POWER', 'M8', 'Tk', 'a', bw_power],
               ['POWER', 'M9', 'Tk', 'a', bw_power],
               ['POWER', 'M10', 'Ti', 'a', bw_power],
               ['POWER', 'M11', 'Ti', 'a', bw_power],
               ['POWER', 'M12', 'Ti', 'a', bw_power],
               ['SIGNAL', 'M1', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M2', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M3', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M4', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M5', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M6', 'Tr', 'a', bw_sig],
               ['SIGNAL', 'M7', 'Tf', 'a', bw_sig],
               ['SIGNAL', 'M8', 'Tf', 'a', bw_sig],
               ['SIGNAL', 'M9', 'Tf', 'a', bw_sig],
               ['SIGNAL', 'M10', 'Tf', 'a', bw_sig],
               ['SIGNAL', 'M11', 'Tf', 'a', bw_sig],
               ['SIGNAL', 'M12', 'Tf', 'a', bw_sig],
               ]

    cols = ['bw_type', 'start', 'stop', 'obj']
    for row in range(24):
        for col in range(5):
            df.loc[row, col] = bw_data[row][col]
    print df
    print df.iloc[0, 0]
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
    lns = []
    for sym in sym_layout.all_sym:
        if sym.element.path_id == 'DC_plus':
            pts.append(sym)
        if sym.element.path_id == 'DC_neg':
            pts.append(sym)

        if len(pts) > 1:
            break
    row =0
    dev_states = pd.DataFrame()

    for sym in sym_layout.all_sym:
        if isinstance(sym, SymPoint) and isinstance(sym.tech, DeviceInstance):
            for col in range(4):
                if col == 0:
                    dev_states.loc[row, col]=sym.name
                elif col ==1:
                    dev_states.loc[row, col] = 1
                else:
                    dev_states.loc[row, col] = 0
            row+=1
        elif isinstance(sym, SymLine):
            lns.append(sym)

    if len(pts) == 2:
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'MS',device_state=dev_states)
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'MS',
                               device_state=dev_states)
        sym_layout.perf_measures.append(m2)

    m3 = ElectricalMeasure(lines=lns,measure= ElectricalMeasure.MEASURE_CAP, freq=100, name="Total cap", mdl='MS',
                           device_state=dev_states)
    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)

    #m3 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.", 'TFSM_MODEL')
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

def add_thermal_measure(sym_layout):
    devices = []
    for sym in sym_layout.all_sym:
        if isinstance(sym,SymPoint) and 'M' in sym.name:
            devices.append(sym)
    m1 = ThermalMeasure(ThermalMeasure.Find_All, devices, "All Temp", 'TFSM_MODEL')
    sym_layout.perf_measures.append(m1)
def thermal_measure(sym_layout):
    for measure in sym_layout.perf_measures:
        val = sym_layout._thermal_analysis(measure, 'TFSM_MODEL')
    return val
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
    dev_mos = DeviceInstance(0.1, 5.0, get_mosfet(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = get_power_lead()  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object

    table_df = pd.DataFrame()
    table_df=make_test_bonds(table_df,signal_bw,power_bw)

    make_test_leads(sym_layout.all_sym, pow_lead,sig_lead)  # Depends on the layout script you have, you can assign the lead object to a SYM-POINT using the id of the object
    make_test_devices(sym_layout.all_sym,dev_dict={'M1': dev_mos,'M2': dev_mos,'M3': dev_mos,'M4': dev_mos,
                                                   'M5': dev_mos, 'M6': dev_mos, 'M7': dev_mos, 'M8': dev_mos,
                                                   'M9': dev_mos, 'M10': dev_mos, 'M11': dev_mos, 'M12': dev_mos,})  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object
    make_test_symmetries(sym_layout) # You can assign the symmetry objects here
    make_test_constraints(sym_layout)
    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data_RD100(f,100,300.0)

    # Pepare for optimization.
    sym_layout.form_design_problem(module,table_df, temp_dir) # Collect data to user interface
    sym_layout._map_design_vars()
    setup_model(sym_layout)
    individual= [6.6792689017536055, 8.520954191778017, 7.681592868581593, 6.202692454990171, 10.89284111447856,
                 4.6782082887774425, 8.241788783730751, 9.564268711545886, 0.2, 8.617059202394898, 18.90822975209389,
                 11.493503127654577, 6.801037223656925, 0.8, 0.3, 0.1, 0.3,
                 0.8, 0.1, 0.1, 0.8, 0.3,
                 0.3, 0.8, 0.1]
    print 'individual', individual
    print "opt_to_sym_index", sym_layout.opt_to_sym_index
    #sym_layout.optimize()
    sym_layout.running=False
    sym_layout.rev_map_design_vars(individual)
    sym_layout.generate_layout()
    plot_layout(sym_layout)
    plt.show()
    md = ModuleDesign(sym_layout)

    output_q3d_vbscript(md=md, filename='big_gap')

    print sym_layout._opt_eval(individual)
# The test goes here, moddify the path below as you wish...
directory ='Layout//RD100_12sw.psc' # directory to layout script
make_test_setup2(100.0,directory)