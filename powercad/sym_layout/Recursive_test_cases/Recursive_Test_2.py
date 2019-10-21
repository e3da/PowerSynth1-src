#@authors: Quang Le
import os

import networkx as nx

from powercad.design.module_data import gen_test_module_data
from powercad.general.settings import settings
from powercad.general.settings.save_and_load import load_file
from powercad.parasitics.analytical.analysis import parasitic_analysis
from powercad.sym_layout.plot import plot_layout
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure
from powercad.tech_lib.test_techlib import get_device, get_dieattach
from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
from powercad.tech_lib.test_techlib import get_signal_lead


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


def make_test_devices(symbols, dev):
    # symbols list of all SymLine and SymPoints in a loaded layout (sym_layout.all_sym)
    for obj in symbols:
        print obj.element.path_id
        if obj.element.path_id == '0018' or obj.element.path_id == '0019':
            obj.tech = dev


def make_test_leads(symbols, pow_lead, sig_lead):
    for obj in symbols:
        if obj.element.path_id == '0003':
            obj.tech = sig_lead
            obj.center_position = [6, 6]
            print "center", obj.center_position, type(obj)
        elif obj.element.path_id == '0006':
            obj.tech = sig_lead
        elif obj.element.path_id == '0008':
            obj.tech = sig_lead
        elif obj.element.path_id == '0010':
            obj.center_position = [6, 35]
            obj.tech = sig_lead
            print "center", obj.center_position, type(obj)
        elif obj.element.path_id == '0013':
            obj.tech = sig_lead


def make_test_bonds(symbols, power, signal):
    for obj in symbols:
        if obj.element.path_id == '0014':
            obj.make_bondwire(power)
            obj.wire_sep = 2
            obj.num_wires = 2
        elif obj.element.path_id == '0015':
            obj.make_bondwire(power)
            obj.wire_sep = 2
            obj.num_wires = 2
        elif obj.element.path_id == '0016' or obj.element.path_id == '0017':
            obj.make_bondwire(signal)


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
        if sym.element.path_id == '0003':
            pts.append(sym)
        if sym.element.path_id == '0010':
            pts.append(sym)
        if len(pts) > 1:
            break

    if len(pts) == 2:
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'MS')
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'MS')
        sym_layout.perf_measures.append(m2)
        m3 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'RS')
        sym_layout.perf_measures.append(m3)
        m4 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'RS')
        sym_layout.perf_measures.append(m4)

    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)

    m5 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.", 'TFSM_MODEL')
    sym_layout.perf_measures.append(m5)
    print "perf", sym_layout.perf_measures


def setup_model(symlayout):
    for pm in symlayout.perf_measures:
        if isinstance(pm, ElectricalMeasure):
            # ctypes.windll.user32.MessageBoxA(0, pm.mdl, 'Model', 1)
            symlayout.mdl_type['E'].append(pm.mdl)
    symlayout.mdl_type['E'] = list(set(symlayout.mdl_type['E']))
    symlayout.lumped_graph = [nx.Graph() for i in range(len(symlayout.mdl_type['E']))]


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
                try:
                    val = parasitic_analysis(symlayout.lumped_graph[id], src, sink, measure_type)
                except LinAlgError:
                    val = 1e6

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


def make_test_setup2(f,directory):

    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script

    dev = DeviceInstance(0.1, 10, get_device(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = None  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object
    make_test_leads(sym_layout.all_sym, pow_lead,sig_lead)  # Depends on the layout script you have, you can assign the lead object to a SYM-POINT using the id of the object
    make_test_bonds(sym_layout.all_sym, power_bw,signal_bw)  # Depends on the layout script you have, you can assign the bw object to a SYM-Line using the id of the object
    make_test_devices(sym_layout.all_sym,dev)  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object

    # make_test_symmetries(sym_layout) # You can assign the symmetry objects here

    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data(f)

    # Pepare for optimization.

    sym_layout.form_design_problem(module, temp_dir) # Collect data to user interface
    mdl = load_file("C://PowerSynth_git//Response_Surface//PowerCAD-full//tech_lib//Model//Trace//t1.rsmdl")
    mdl = load_file("C://Users//qmle//Desktop//Testing//FastHenry//Fasthenry3_test_gp//WorkSpace//test3.rsmdl")
    sym_layout.set_RS_model(mdl)
    sym_layout._map_design_vars()
    setup_model(sym_layout)
    individual = [18, 4, 4, 8, 8, 2, 2,10, 10,4, 0.3, 0.1] # This one change depends on the number of design variables you have. This is the design vector basically
    print 'individual', individual
    print "opt_to_sym_index", sym_layout.opt_to_sym_index
    sym_layout.rev_map_design_vars(individual)
    sym_layout.generate_layout()
    sym_layout._build_lumped_graph()
    ret = one_measure(sym_layout)
    print ret # As I set this up the first value is inductance, then resistance, then temperature
    plot_layout(sym_layout)



# The test goes here, moddify the path below as you wish...
directory ='C:/Users/qmle/Desktop/POETS/Final/T1/layout.psc' # directory to layout script
f=100.0
make_test_setup2(f,directory)