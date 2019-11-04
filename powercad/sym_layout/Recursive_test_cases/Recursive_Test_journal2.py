#@authors: Quang Le
import os

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import powercad.design.module_design as md
from powercad.design.module_data import gen_test_module_data
from powercad.general.settings import settings
from powercad.parasitics.analytical.analysis import parasitic_analysis
from powercad.sym_layout.plot import plot_layout
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure
from powercad.tech_lib.test_techlib import get_device, get_dieattach
from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
from powercad.tech_lib.test_techlib import get_signal_lead

import powercad.design.module_design as md


import pandas as pd
import powercad.interfaces.ParaPowerAPI.MDConverter as mdc

#from powercad.design.MDConverter import MDEncoder


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
        if obj.name == 'DC_neg':
            obj.tech = sig_lead
            obj.center_position = [6, 6]
        elif obj.name== 'DC_plus':
            obj.center_position = [6, 35]
            obj.tech = sig_lead
        elif obj.name == 'G_low' or obj.name == 'G_high' or obj.name == 'Out':
            obj.tech = sig_lead

def make_test_bonds(df,bw_sig,bw_power):
    bw_data=[['POWER','M4','T1','a',bw_power],
    ['POWER','M2','T1','a',bw_power],
    ['POWER','M1','T7','a',bw_power],
    ['POWER','M3','T7','a',bw_power],
    ['SIGNAL','M4','T3','a',bw_sig],
    ['SIGNAL','M2','T3','a',bw_sig],
    ['SIGNAL','M1','T5','a',bw_sig],
    ['SIGNAL','M3','T5','a',bw_sig]]
    cols=['bw_type', 'start', 'stop', 'obj']
    for row in range(8):
        for col in range(5):
            df.loc[row,col]=bw_data[row][col]
    print df
    print df.iloc[0,0]
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


def add_test_measures(sym_layout, matlab_engine=None):
    pts = []
    for sym in sym_layout.all_sym:
        if sym.element.path_id == '0002':
            pts.append(sym)
        if sym.element.path_id == '0010':
            pts.append(sym)
        if len(pts) > 1:
            break

    if len(pts) == 2:
        m1 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_IND, 100, "Loop Inductance", None, 'MS')
        # sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pts[0], pts[1], ElectricalMeasure.MEASURE_RES, 100, "Loop Resistance", None, 'MS')
        # sym_layout.perf_measures.append(m2)

    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)

    m3 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "PowerSynth Max Temp.", 'TFSM_MODEL')
    sym_layout.perf_measures.append(m3)

    m4 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "ParaPower Max Temp.", "ParaPowerThermal", matlab_engine=matlab_engine)
    sym_layout.perf_measures.append(m4)
    print "perf", sym_layout.perf_measures


def setup_model(symlayout):
    for pm in symlayout.perf_measures:
        if isinstance(pm, ElectricalMeasure):
            # ctypes.windll.user32.MessageBoxA(0, pm.mdl, 'Model', 1)
            symlayout.mdl_type['E']=pm.mdl


def one_measure(symlayout, matlab_engine=None):
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
            elif type == 'ParaPowerThermal':
                type_id = 4
            val = symlayout._thermal_analysis(measure, type_id, matlab_engine=matlab_engine)
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

def make_tbl_dev_states():
    ''' This will set up dev states'''
    data = [['M1', 1, 1, 1], ['M2', 1, 1, 1], ['M3', 1, 1, 1], ['M4', 1, 1, 1]]
    ''' DEV_ID , Drain_Source, Gate_Source, Gate_Drain'''
    df = pd.DataFrame(data)
    print df
    return df

def make_test_setup2(f, directory):

    matlab_path = 'C:/Users/tmevans/Documents/MATLAB/ParaPower/ARL_ParaPower/ARL_ParaPower'
    matlab_engine = mdc.init_matlab(matlab_path)

    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    ps_results = []
    pp_results = []
    ps_time = []
    pp_time = []
    # powers= [[1.89,1.98,1.92,1.98],[2.31,2.44,2.34,2.41],[2.83,2.93,2.844,2.938],[3.6096,3.788,3.66,3.776],[3.966,4.1004,4.033,4.1004]]
    # powers = [[8., 8., 8., 8.]]
    powers = [[2.5, 2.5, 2.5, 2.5], [5., 5., 5., 5.], [7.5, 7.5, 7.5, 7.5], [10., 10., 10., 10.],
              [12.5, 12.5, 12.5, 12.5]]
    # h_val = [102.331, 105.986, 110.236, 115.238, 117.656]
    h_val = [150.0, 150.0, 150.0, 150.0, 150.0]
    # h_val = [150.0]
    for p, h in zip(powers, h_val):
        print "Test Case", p, h
        sym_layout = SymbolicLayout()  # initiate a symbolic layout object
        sym_layout.load_layout(test_file, 'script')  # load the script
        dev1 = DeviceInstance(0.1, p[0], get_device(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
        dev2 = DeviceInstance(0.1, p[1], get_device(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
        dev3 = DeviceInstance(0.1, p[2], get_device(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
        dev4 = DeviceInstance(0.1, p[3], get_device(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

        pow_lead = None  # Get a power lead object

        sig_lead = get_signal_lead()  # Get a signal lead object

        power_bw = get_power_bondwire()  # Get bondwire object
        signal_bw = get_signal_bondwire()  # Get bondwire object

        table_df = pd.DataFrame()
        table_df = make_test_bonds(table_df, signal_bw, power_bw)

        make_test_leads(sym_layout.all_sym, pow_lead,sig_lead)  # Depends on the layout script you have, you can assign the lead object to a SYM-POINT using the id of the object
        make_test_devices(sym_layout.all_sym, dev_dict={'M1':dev1,'M2':dev2,'M3':dev3,'M4':dev4})  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object
        # make_test_symmetries(sym_layout) # You can assign the symmetry objects here

        add_test_measures(sym_layout, matlab_engine=matlab_engine)  # Assign a measurement between 2 SYM-Points (using their IDs)

        module = gen_test_module_data(f, h)

        # Prepare for optimization.
        sym_layout.form_design_problem(module, table_df, temp_dir) # Collect data to user interface
        sym_layout._map_design_vars()

        #sym_layout.optimize(inum_gen=50)
        individual = [10, 4, 10, 2.0, 2.0, 10, 4, 0.38232573137878245, 0.7, 0.68, 0.24]
        sym_layout.rev_map_design_vars(individual)
        sym_layout.generate_layout()
        sym_layout.eval_count = 0
        thermal_result = sym_layout._opt_eval(individual)

        ps_results.append(thermal_result[0])
        ps_time.append(thermal_result[1])
        pp_results.append(thermal_result[2])
        pp_time.append(thermal_result[3])

        # add_thermal_measure(sym_layout)
        plot_layout(sym_layout)
        # plt.show()
        # results.append(thermal_measure(sym_layout))
        # print results
    # for r in results:
    #     print r
    ax = plt.subplot('111', adjustable='box', aspect=1.0)
    plot_layout(sym_layout, filletFlag=False, ax=ax)
    plot_compare_temp(powers, ps_results, pp_results)
    return md.ModuleDesign(sym_layout), np.array(ps_time), np.array(pp_time)
# The test goes here, moddify the path below as you wish...


def plot_compare_temp(power_list, ps_results, pp_results):
    power = []
    for powers in power_list:
        p = 0.
        for i in powers:
            p += i
        power.append(p)
    print '\n'
    print '=_=' * 30
    print 'power', power
    print 'PowerSynth Results', ps_results
    print 'ParaPower Results', pp_results
    print '=_=' * 30

    ps_results = np.array(ps_results) - 273.5 - 20.
    pp_results = np.array(pp_results) - 273.5 - 20.

    error = np.abs((ps_results - pp_results)/ps_results)*100

    font_small = 14
    font_large = 16
    lw = 4
    fig, ax = plt.subplots(1, 1, figsize=(9, 5))
    ax.plot(power, ps_results, color='navy', linewidth=lw, label='PowerSynth')
    ax.scatter(power, ps_results, color='navy', s=40)
    ax.plot(power, pp_results, color='darkorange', linewidth=lw, linestyle=':', label='ParaPower')
    ax.scatter(power, pp_results, color='darkorange', s=40)
    ax.set_ylabel('Temperature Rise $\Delta T_J$ ($^\circ$C)', fontsize=font_small)
    ax.set_xlabel('Total Power Dissipation (W)', fontsize=font_small)
    ax2 = ax.twinx()
    ax2.plot(power, error, color='green', linestyle='--', linewidth=lw, label='Rel. Difference')
    ax2.scatter(power, error, color='green', s=40)
    ax2.set_ylabel('Relative Difference (%)', fontsize=font_small)
    ax.legend(loc='upper left', fontsize=12)
    ax2.legend(loc='lower right', fontsize=12)
    plt.title('PowerSynth and ParaPower\nThermal Model Comparison', weight='bold', fontsize=font_large)
    ax2.set_ylim(0.2, 0.26)
    ax.set_ylim(10, 100)
    ax.set_xlim(5, 55)
    ax.grid(which='major', axis='both')
    ax.tick_params(labelsize=12)
    ax2.set_yticks([0.2, 0.22, 0.24, 0.25, 0.26], minor=True)
    # ax2.tick_params(axis='y', which='minor', labelsize=12)
    plt.savefig('0_3_PS_PP_Compare_Thermal.png', dpi=200)
    plt.plot()


# directory ='Layout/journal_2(v2).psc' # directory to layout script
# md, ps_time, pp_time = make_test_setup2(100.0, directory)
# pp = mdc.ParaPowerWrapper(md)
# pp.parapower.save_parapower()
#maxtemp = pp.parapower.run_parapower_thermal()
'''
print '\n'
print '=' * 30
print '|\tMax Temp: ', maxtemp
print '=' * 30
'''

if __name__ == '__main__':

    directory ='Layout/journal_2(v2).psc' # directory to layout script
    md = make_test_setup2(100.0,directory)
    pp = mdc.ParaPowerWrapper(md)
