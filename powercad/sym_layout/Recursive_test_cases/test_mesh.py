# @authors: Quang Le

import cProfile
import pstats

from powercad.design.module_data import gen_test_module_data
from powercad.design.module_design import ModuleDesign
from powercad.electrical_mdl.e_mesh import *
from powercad.electrical_mdl.e_struct import *
from powercad.electrical_mdl.spice_eval.rl_mat_eval import *
from powercad.general.settings import settings
from powercad.parasitics.analysis import parasitic_analysis
from powercad.parasitics.mdl_compare import *
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


def make_test_devices(symbols, dev=None, dev_dict=None):
    # symbols list of all SymLine and SymPoints in a loaded layout (sym_layout.all_sym)
    if dev_dict == None:  # Apply same powers
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
        elif obj.name == 'DC_plus':
            obj.center_position = [6, 35]
            obj.tech = sig_lead
        elif obj.name == 'G_low' or obj.name == 'G_high' or obj.name == 'Out':
            obj.tech = sig_lead


def make_test_bonds(df, bw_sig, bw_power):
    bw_data = [['POWER', 'M4', 'T1', 'a', bw_power],
               ['POWER', 'M2', 'T1', 'a', bw_power],
               ['POWER', 'M1', 'T7', 'a', bw_power],
               ['POWER', 'M3', 'T7', 'a', bw_power],
               ['SIGNAL', 'M4', 'T3', 'a', bw_sig],
               ['SIGNAL', 'M2', 'T3', 'a', bw_sig],
               ['SIGNAL', 'M1', 'T5', 'a', bw_sig],
               ['SIGNAL', 'M3', 'T5', 'a', bw_sig]]
    cols = ['bw_type', 'start', 'stop', 'obj']
    for row in range(8):
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
    for sym in sym_layout.all_sym:
        if sym.element.path_id == '0002':
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
            symlayout.mdl_type['E'] = pm.mdl


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
                val = parasitic_analysis(symlayout.lumped_graph, src, sink, measure_type, node_dict)
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
        if isinstance(sym, SymPoint) and 'M' in sym.name:
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


def make_test_setup2(f, directory):
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object
    sym_layout.load_layout(test_file, 'script')  # load the script
    dev1 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev2 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev3 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object
    dev4 = DeviceInstance(0.1, 10, get_device(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = None  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object

    table_df = pd.DataFrame()
    table_df = make_test_bonds(table_df, signal_bw, power_bw)

    make_test_leads(sym_layout.all_sym, pow_lead,
                    sig_lead)  # Depends on the layout script you have, you can assign the lead object to a SYM-POINT using the id of the object
    make_test_devices(sym_layout.all_sym, dev_dict={'M1': dev1, 'M2': dev2, 'M3': dev3,
                                                    'M4': dev4})  # Depends on the layout script you have, you can assign the device object to a SYM-POINT using the id of the object
    # make_test_symmetries(sym_layout) # You can assign the symmetry objects here

    add_test_measures(sym_layout)  # Assign a measurement between 2 SYM-Points (using their IDs)

    module = gen_test_module_data(f, 1000)

    # Pepare for optimization.
    sym_layout.form_design_problem(module, table_df, temp_dir)  # Collect data to user interface
    sym_layout._map_design_vars()
    individual = [10, 4, 10, 2.0, 2.0, 10, 4, 0.38232573137878245, 0.7, 0.68, 0.24]
    sym_layout.rev_map_design_vars(individual)
    sym_layout.generate_layout()
    #plot_layout(sym_layout)
    md = ModuleDesign(sym_layout)
    plates = get_traces_from_md(md)
    # ADD SHEET
    # First bw group
    x1=16.5
    x2=18.5
    x3=15.5
    x4=16.5
    #es = E_stack(file="C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\ELayerStack//2_layers.csv")
    #es.load_layer_stack()
    bw11 = Rect(40.5, 38.5, x1, x2)
    BW1s = Sheet(rect=bw11, net_name='bw11', type='point', n=(0, 0, 1), z=1.04)
    bw12 = Rect(45.5, 44.5, x1, x2)
    BW1e = Sheet(rect=bw12, net_name='bw12', type='point', n=(0, 0, 1), z=1.04)
    # Second bw group
    bw21 = Rect(14.5, 12.5, x3, x4)
    BW2s = Sheet(rect=bw21, net_name='bw21', type='point', n=(0, 0, 1), z=1.04)
    bw22 = Rect(8.5, 7.5, x3, x4)
    BW2e = Sheet(rect=bw22, net_name='bw22', type='point', n=(0, 0, 1), z=1.04)
    # First Pad
    p1 = Rect(37.5, 36.5, 4, 6)
    P1 = Sheet(rect=p1, net_name='P1', type='point', n=(0, 0, 1), z=1.04)
    p2 = Rect(6.5, 5.5, 4, 6)
    P2 = Sheet(rect=p2, net_name='P2', type='point', n=(0, 0, 1), z=1.04)

    Bw1 = EComp(sheet=[BW1s, BW1e], conn=[['bw11', 'bw12']], val={'R':0.6e-3, 'L':1e-9})
    Bw2 = EComp(sheet=[BW2s, BW2e], conn=[['bw21', 'bw22']], val={'R':0.6e-3, 'L': 1e-9})
    bs_copper = Rect(50, 0, 0, 40)
    #bs_plate=E_plate(rect=bs_copper, z=0, dz=0.2)
    #plates.append(bs_plate)
    sheets = [P1,P2]
    new_module = EModule(plate=plates, components = [Bw1, Bw2], sheet=sheets)#,layer_stack=es)
    new_module.form_group()
    new_module.split_layer_group()


    hier = EHier(module=new_module)
    hier.form_hierachy()
    freqs=[10,20,50,100,500,1000]
    mdl_dir = "C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\Model\workspace"
    mdl_name = '2d_high_freq_journal.rsmdl'
    rsmdl = load_mdl(mdl_dir, mdl_name)
    for freq in freqs:
        pr = cProfile.Profile()

        pr.enable()
        emesh = EMesh(hier_E=hier, freq=freq, mdl=rsmdl)
        #fig = plt.figure(1)
        emesh.mesh_grid_hier(Nx=3, Ny=3)
        #ax = plt.subplot('111', adjustable='box', aspect=1.0)
        #emesh.plot_lumped_graph()
        #plt.show()
        start = time.time()

        emesh.update_trace_RL_val()
        emesh.update_hier_edge_RL()
        emesh.update_mutual()

        # EVALUATION
        circuit = RL_circuit()
        pt1 = (4, 37,0.84)
        pt2 = (4, 6,0.84)
        src1 = emesh.find_node(pt1)
        sink1 = emesh.find_node(pt2)

        circuit.comp_mode = 'val'
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        circuit.assign_freq(freq*1000)
        circuit.Rport=1e-10
        circuit.indep_current_source(src1, 0, 1)
        circuit._add_termial(sink1)

        circuit.build_current_info()
        circuit.solve_iv()
        print time.time()-start,'s'
        print 'f',freq,'kHz'
        pr.disable()
        pr.create_stats()
        file = open('mystats.txt', 'w')
        stats = pstats.Stats(pr, stream=file)
        stats.sort_stats('cumulative')
        stats.print_stats()
        #print "model",circuit._compute_imp(src1, sink1, sink1)

        '''
        all_I=[]
        result = circuit.results
        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            if edge.data['type']!='hier':
                width = edge.data['w'] * 1e-3
                thick = edge.thick*1e-3
                A = width * thick
                I_name = 'I_L' + edge_name
                edge.I = np.real(result[I_name])
                edge.J = edge.I / A
                all_I.append(abs(edge.J))
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(I_min, I_max)
        normI = Normalize(0,50000)
        fig = plt.figure(2)
        ax = fig.add_subplot(111)
        plt.xlim([0, 40])
        plt.ylim([0, 50])
        plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0.84, mode='J',
                                         W=[2, 37],
                                         H=[2, 47], numvecs=61)
        plt.show()

        '''

# The test goes here, moddify the path below as you wish...
directory = 'Layout/journal_2(v2).psc'  # directory to layout script
make_test_setup2(100.0, directory)