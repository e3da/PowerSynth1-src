#@authors: Quang Le
import os

import networkx as nx

from powercad.design.module_data import gen_test_module_data
from powercad.general.settings import settings
from powercad.parasitics.analysis import parasitic_analysis
from powercad.sym_layout.plot import plot_layout
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure
from powercad.tech_lib.test_techlib import get_device, get_dieattach
from powercad.tech_lib.test_techlib import get_power_bondwire, get_signal_bondwire
from powercad.tech_lib.test_techlib import get_signal_lead

import powercad.design.module_design as md

import matplotlib.pyplot as plt
import pandas as pd
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


def add_test_measures(sym_layout,dev_states):
    ''' ADD Test Measure Here'''
    pts = []
    ''' Read through all symbolic objects'''
    ''' Here I only select 2 names for one loop from DC_plus to DC_neg (See the layout script)
    If you need multiple loops, write a nested loop with pair of net name [[DC_plus,DC_neg]], .... ]  ? '''
    for sym in sym_layout.all_sym:
        if sym.element.path_id == 'DC_plus':
            pts.append(sym)
        if sym.element.path_id == 'DC_neg':
            pts.append(sym)
        if len(pts) > 1:
            break
    ''' ELECTRICAL '''

    ''' if there are 2 points this code will be the same as resistance and inductance measurement setup in your UI'''
    if len(pts) == 2:
        m1 = ElectricalMeasure(pt1=pts[0], pt2=pts[1], measure=ElectricalMeasure.MEASURE_IND, name="Loop Inductance", mdl='MS',
                               device_state=dev_states)
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pt1=pts[0], pt2=pts[1], measure=ElectricalMeasure.MEASURE_RES, name="Loop Resistance", mdl='MS',
                               device_state=dev_states)
        sym_layout.perf_measures.append(m2)

    ''' THERMAL '''
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

def make_test_setup2(f,directory):

    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    results=[]
    # powers= [[1.89,1.98,1.92,1.98],[2.31,2.44,2.34,2.41],[2.83,2.93,2.844,2.938],[3.6096,3.788,3.66,3.776],[3.966,4.1004,4.033,4.1004]]
    powers = [[1, 1, 1, 1]]
    h_val =[102.331, 105.986, 110.236, 115.238, 117.656]
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
        make_test_devices(sym_layout.all_sym,dev_dict={'M1':dev1,'M2':dev2,'M3':dev3,'M4':dev4})  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object
        # make_test_symmetries(sym_layout) # You can assign the symmetry objects here
        dev_states = make_tbl_dev_states()

        add_test_measures(sym_layout,dev_states)  # Assign a measurement between 2 SYM-Points (using their IDs)

        module = gen_test_module_data(f, h)

        # Prepare for optimization.
        sym_layout.form_design_problem(module, table_df, temp_dir) # Collect data to user interface
        sym_layout._map_design_vars()

        #sym_layout.optimize()
        individual =[10, 4, 10, 2.0, 2.0, 10, 4, 0.38232573137878245, 0.7, 0.68, 0.24]
        sym_layout.rev_map_design_vars(individual)
        sym_layout.generate_layout()
        add_thermal_measure(sym_layout)
        plot_layout(sym_layout)
        # plt.show()
        results.append(thermal_measure(sym_layout))
        print results
    for r in results:
        print r
    ax = plt.subplot('111', adjustable='box', aspect=1.0)
    plot_layout(sym_layout,filletFlag=False,ax=ax)
    return md.ModuleDesign(sym_layout)
# The test goes here, moddify the path below as you wish...




def make_test_setup3(directory):
    '''
    This script will run the evaluation one single time for electrical and thermal
    '''
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored
    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want
    sym_layout = SymbolicLayout()  # initiate a symbolic layout object
    sym_layout.load_layout(test_file, 'script')  # load the script

    ''' Set up devices with 10 W power dissipation'''
    dev1 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev2 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev3 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev4 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    ''' Setup module design '''
    module = gen_test_module_data(100.0, 1000.0)

    ''' Setup leads connections'''
    pow_lead = None  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object

    table_df = pd.DataFrame()
    table_df = make_test_bonds(table_df, signal_bw, power_bw)

    make_test_leads(sym_layout.all_sym, pow_lead,
                    sig_lead)  # Depends on the layout script you have, you can assign the lead object to a SYM-POINT using the id of the object
    ''' Setup devices here'''

    make_test_devices(sym_layout.all_sym, dev_dict={'M1': dev1, 'M2': dev2, 'M3': dev3,
                                                    'M4': dev4})  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object
    # make_test_symmetries(sym_layout) # You can assign the symmetry objects here


    ''' Setup measurement '''
    # mdl = load_file("C://Users//qmle//Desktop//Testing//FastHenry//Fasthenry3_test_gp//WorkSpace//test5.rsmdl")
    # sym_layout.set_RS_model(mdl)
    dev_states = make_tbl_dev_states()
    add_test_measures(sym_layout,dev_states)  # Assign a measurement between 2 SYM-Points (using their IDs)

    ''' Setup optimization '''
    sym_layout.form_design_problem(module, table_df, temp_dir)  # Collect data to user interface
    sym_layout._map_design_vars()

    ''' This will run optimization '''
    # sym_layout.optimize()
    ''' List of layout solutions here:'''
    # print sym_layout.solutions
    ''' Single Individual Evaluation'''
    ''' During optimization you can print individual in opt_eval function to see the individual list. Change this manually
    first to test your model. Then you can design your new EMI eval function in opt_eval and run optimization'''
    individual = [10, 4, 10, 2.0, 2.0, 10, 4, 0.38232573137878245, 0.7, 0.68, 0.24]

    sym_layout.rev_map_design_vars(individual)
    # if no optimization
    sym_layout.eval_count = 1
    sym_layout.generate_layout()
    ''' This code will perform the measurements ( based on ones you had in measurement setup '''
    ''' This will return a list with n values for n is number of measurements'''
    results = sym_layout._opt_eval(individual)
    print results
    ''' This code below do 1 single thermal measurement only ( I commented it out)'''
    #add_thermal_measure(sym_layout)
    ''' Plot the layout'''
    plot = False # Change this flag
    if plot == True:
        plot_layout(sym_layout)
        plt.show()

    return sym_layout

# For testing in console
directory ='Layout/journal_2(v2).psc' # directory to layout script
# md = make_test_setup2(100.0,directory)
sl = make_test_setup3(directory)


if __name__ == '__main__':
    '''
    directory ='Layout/journal_2(v2).psc' # directory to layout script

    #md = make_test_setup2(100.0,directory)
    make_test_setup3(directory)
    '''