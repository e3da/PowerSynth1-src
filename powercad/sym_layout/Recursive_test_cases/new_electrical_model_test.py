# This will test the new lumped graph structure along with Kelvin connection
# @authors: Quang Le

import os

import matplotlib.pyplot as plt
import pandas as pd
from PySide import QtGui

from powercad.cons_aware_en.cons_engine import New_layout_engine
from powercad.corner_stitch.CornerStitch import *
from powercad.design.module_data import *
from powercad.general.settings import settings
from powercad.parasitics.analytical.analysis import parasitic_analysis
from powercad.sym_layout.symbolic_layout import SymbolicLayout, DeviceInstance, SymLine, SymPoint, ElectricalMeasure, \
    ThermalMeasure, plot_layout


#from powercad.opt.pareto import *


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


def make_tbl_dev_states():
    ''' This will set up dev states'''
    data = [['M1', 1, 1, 1], ['M2', 1, 1, 1]]
    ''' DEV_ID , Drain_Source, Gate_Source, Gate_Drain'''
    df = pd.DataFrame(data)
    return df


def make_test_leads(symbols, pow_lead, sig_lead):
    for obj in symbols:
        if obj.name == 'L1' or obj.name == 'L3' or obj.name == 'L2':
            obj.tech = sig_lead


def make_test_bonds(df, bw_sig, bw_power):
    bw_data = [['POWER', 'M2', 'T2', 'a', bw_power],
               ['POWER', 'M1', 'T7', 'a', bw_power],
               ['SIGNAL', 'M2', 'T5', 'a', bw_sig],
               ['SIGNAL', 'M1', 'T5', 'a', bw_sig]]
    for row in range(4):
        for col in range(5):
            df.loc[row, col] = bw_data[row][col]

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


def add_test_measures(sym_layout, dev_states):
    ''' ADD Test Measure Here'''
    pts = []
    ''' Read through all symbolic objects'''
    ''' Here I only select 2 names for one loop from DC_plus to DC_neg (See the layout script)
    If you need multiple loops, write a nested loop with pair of net name [[DC_plus,DC_neg]], .... ]  ? '''
    for sym in sym_layout.all_sym:
        if sym.element.path_id == 'L1':
            pts.append(sym)
        if sym.element.path_id == 'L3':
            pts.append(sym)

        if len(pts) > 1:
            break

    ''' ELECTRICAL '''

    ''' if there are 2 points this code will be the same as resistance and inductance measurement setup in your UI'''
    if len(pts) == 2:
        m1 = ElectricalMeasure(pt1=pts[0], pt2=pts[1], measure=ElectricalMeasure.MEASURE_IND, name="Loop Inductance",
                               mdl='MS', device_state=dev_states)
        sym_layout.perf_measures.append(m1)
        m2 = ElectricalMeasure(pt1=pts[0], pt2=pts[1], measure=ElectricalMeasure.MEASURE_RES, name="Loop Resistance",
                               mdl='MS',
                               device_state=dev_states)
        # sym_layout.perf_measures.append(m2)

    ''' THERMAL '''
    devices = []
    for sym in sym_layout.all_sym:
        devices.append(sym)
    m3 = ThermalMeasure(ThermalMeasure.FIND_MAX, devices, "Max Temp.", 'RECT_FLUX_MODEL')
    sym_layout.perf_measures.append(m3)

    # "perf", sym_layout.perf_measures


def setup_model(symlayout):
    for pm in symlayout.perf_measures:
        if isinstance(pm, ElectricalMeasure):
            # ctypes.windll.user32.MessageBoxA(0, pm.mdl, 'Model', 1)
            symlayout.mdl_type['E'] = pm.mdl


def one_measure(sym_layout):
    ret = []
    for measure in sym_layout.perf_measures:

        if isinstance(measure, ElectricalMeasure):
            type_dict = {ElectricalMeasure.MEASURE_RES: 'res',
                         ElectricalMeasure.MEASURE_IND: 'ind',
                         ElectricalMeasure.MEASURE_CAP: 'cap'}
            measure_type = type_dict[measure.measure]
            if measure.measure == ElectricalMeasure.MEASURE_CAP:
                val = sym_layout._measure_capacitance(measure)
            else:

                # load device states table
                tbl_states = measure.dev_state
                for row in range(len(tbl_states.axes[0])):
                    dev_name = tbl_states.loc[row, 0]
                    for dev in sym_layout.devices:
                        if (dev.name == dev_name) or dev.element.path_id == dev_name:
                            if dev.is_transistor():
                                dev.states = [tbl_states.loc[row, 1], tbl_states.loc[row, 2], tbl_states.loc[row, 3]]
                            if dev.is_diode():
                                dev.states = [tbl_states.loc[row, 1]]

                sym_layout._build_lumped_graph()  # Rebuild the lumped graph for different device state.

                # plot_lumped_graph(sym_layout)
                # Measure res. or ind. from src node to sink node
                source_terminal = measure.src_term
                sink_terminal = measure.sink_term

                src = measure.pt1.lumped_node
                sink = measure.pt2.lumped_node

                if source_terminal != None:
                    if source_terminal == 'S' or source_terminal == 'Anode':
                        src = src * 1000 + 1
                    elif source_terminal == 'G':
                        src = src * 1000 + 2

                if sink_terminal != None:
                    if sink_terminal == 'S' or source_terminal == 'Anode':
                        sink = sink * 1000 + 1
                    elif sink_terminal == 'G':
                        sink = sink * 1000 + 2

                node_dict = {}
                index = 0
                for n in sym_layout.lumped_graph.nodes():
                    node_dict[n] = index
                    index += 1

                val = parasitic_analysis(sym_layout.lumped_graph, src, sink, measure_type, node_dict)
                # print 'ind',val

            ret.append(val)


        elif isinstance(measure, ThermalMeasure):
            type = measure.mdl
            if type == 'TFSM_MODEL':
                type_id = 1
            elif type == 'RECT_FLUX_MODEL':
                type_id = 2
            elif type == 'Matlab':
                type_id = 3
            val = sym_layout._thermal_analysis(measure, 2)
            ret.append(val)
            # Update progress bar and eval count
    return ret


def plot_lumped_graph(sym_layout):
    pos = {}
    for n in sym_layout.lumped_graph.nodes():
        pos[n] = sym_layout.lumped_graph.node[n]['point']
    nx.draw_networkx(sym_layout.lumped_graph, pos)
    plt.show()
    plot_layout(sym_layout)


def layout_plot(layout, ax):
    # print"Len", len(layout)
    for i in range(len(layout)):
        figures = layout[i]
        size = figures.keys()[0]
        patches = figures.values()[0]
        for p in patches:
            ax.add_patch(p)
        ax.set_xlim(0, size[0])
        ax.set_ylim(0, size[1])
    plt.show()


def plot_selected_solutions(individual, ax, W, H, engine):
    figure, CS_SYM, X_Loc, Y_Loc = engine.generate_solutions(level=2, num_layouts=1, W=W, H=H, fixed_x_location=None,
                                                             fixed_y_location=None, individual=individual)

    for i in range(len(figure)):
        figures = figure[i]
        size = figures.keys()[0]
        patches = figures.values()[0]
        for p in patches:
            ax.add_patch(p)
        ax.set_xlim(0, size[0])
        ax.set_ylim(0, size[1])
    plt.show()


def form_sym_obj_rect_dict(layout_data, div=1000):
    '''
    From group of CornerStitch Rectangles, form a single rectangle for each trace
    Output type : {"Layout id": {'Sym_info': symb_rect_dict,'Dims': [W,H]} --- Dims is the dimension of the baseplate
    where symb_rect_dict= {'Symbolic ID': [R1,R2 ... Ri]} where Ri is a Rectangle object
    '''
    #print layout_data
    all_data=[]
    for data in layout_data:
        p_data = data
        symb_rect_dict = {}

        # print "p_data",p_data
        W, H = p_data.keys()[0]
        W = float(W) / div
        H = float(H) / div
        rect_dict = p_data.values()[0]
        for r_id in rect_dict.keys():
            # print 'rect id',r_id
            left = 1e32
            bottom = 1e32
            right = 0
            top = 0
            for rect in rect_dict[r_id]:
                type = rect.type
                min_x = float(rect.left) / div
                max_x = float(rect.right) / div
                min_y = float(rect.bottom) / div
                max_y = float(rect.top) / div
                if min_x <= left:
                    left = float(min_x)
                if min_y <= bottom:
                    bottom = float(min_y)
                if max_x >= right:
                    right = float(max_x)
                if max_y >= top:
                    top = float(max_y)
                symb_rect_dict[r_id] = Rectangle(x=left, y=bottom, width=right - left, height=top - bottom, type=type)
        all_data.append(symb_rect_dict)
    # print symb_rect_dict
    # raw_input("end")
    return all_data


class new_engine_opt:
    def __init__(self, engine, W, H, sym_layout, method="FMINCON"):
        self.engine = engine
        self.W = W
        self.H = H
        self.symlayout = sym_layout
        self.gen_layout_func = self.engine.generate_solutions
        self.count=0




    def optimize(self, num_layout=100):


        figure, CS_SYM, X_Loc, Y_Loc = self.gen_layout_func(level=2, num_layouts=num_layout, W=self.W, H=self.H,
                                                            fixed_x_location=None,
                                                            fixed_y_location=None,individual=None)
        symb_rect_dict = form_sym_obj_rect_dict(layout_data=CS_SYM)
        #self.save_figure(figure) # to save the figures
        return symb_rect_dict


    def save_figure(self, figures):
        for i in figures:
            self.count += 1
            figure = i
            fig9 = matplotlib.pyplot.figure()
            ax1 = fig9.add_subplot(111, aspect='equal')
            for k, v in figure.items():
                for i in v:
                    ax1.add_patch(i)
                plt.xlim(-2000, 22000)
                plt.ylim(-2000, 22000)
            plt.savefig(
                "D:\Demo\Optimization_Results\Latest_Comparison\\5000_Layouts\\" + str(self.count) + ".png")



def init_sym_layout(directory):
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script
    '''
    sym_layout.mdl_type['E'] = 'MS'

    dev1 = DeviceInstance(0.1, 10, get_mosfet(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation.
    dev2 = DeviceInstance(0.1, 10, get_mosfet(),
                          get_dieattach())  # Create a device instance with 10 W power dissipation.
    make_test_devices(sym_layout.all_sym, dev_dict={'M1': dev1, 'M2': dev2})

    sig_lead = get_signal_lead()  # Get a signal lead object

    power_bw = get_power_bondwire()  # Get bondwire object
    signal_bw = get_signal_bondwire()  # Get bondwire object
    pow_lead = None
    table_df = pd.DataFrame()
    table_df = make_test_bonds(table_df, signal_bw, power_bw)
    make_test_leads(sym_layout.all_sym, pow_lead,
                    sig_lead)
    module = gen_test_module_data(100.0)
    dev_states = make_tbl_dev_states()

    add_test_measures(sym_layout, dev_states)  # Assign a measurement between 2 SYM-Points (using their IDs)
    '''
    module = gen_test_module_data(100.0,h=100.0)
    table_df = pd.DataFrame()
    sym_layout.form_api_cs(module, table_df, temp_dir)  # Collect data to user interface
    return sym_layout


def sym_update_layout(sym_layout=None, sym_info=None):
    # ToDo:Here we can add the automate symbolic layout - Corner Stitch interface to update thermal
    sym_update_trace_lines(sym_layout=sym_layout, sym_info=sym_info)
    sym_place_devices(sym_layout=sym_layout, sym_info=sym_info)
    sym_place_leads(sym_layout=sym_layout, sym_info=sym_info)
    sym_place_bondwires(sym_layout=sym_layout)


def sym_update_trace_lines(sym_layout, sym_info=None):
    '''
    *Only used when a symbolic layout is introduced
    Use the rectangles built from corner stitch to make trace rectangles in sym layout
    '''
    # Handle traces
    sym_layout.trace_rects = []

    for tr in sym_layout.all_trace_lines:
        rect = sym_info[tr.element.path_id]
        sym_layout.trace_rects.append(rect)
        tr.trace_rect = rect


def sym_place_devices(sym_layout, sym_info=None):
    '''
    *Only used when a symbolic layout is introduced
    Use the rectangles built from corner stitch to update device locations in sym layout
    '''

    for dev in sym_layout.devices:

        dev_region = sym_info[dev.name]
        width, height, thickness = dev.tech.device_tech.dimensions

        line = dev.parent_line
        trace_rect = line.trace_rect
        if line.element.vertical:
            dev.orientation = 1
            dev.footprint_rect = Rect(dev_region.bottom + height, dev_region.bottom, dev_region.left,
                                      dev_region.left + width)
            xpos = trace_rect.center_x()
            ypos = dev_region.bottom + height / 2
        else:
            dev.footprint_rect = Rect(dev_region.bottom + width, dev_region.bottom, dev_region.left,
                                      dev_region.left + height)

            xpos = dev_region.left + height / 2
            ypos = trace_rect.center_y()
            dev.orientation = 3
        dev.center_position = (xpos, ypos)
        if len(dev.sym_bondwires) > 0:
            powerbond = None
            for bw in dev.sym_bondwires:
                if bw.tech.wire_type == BondWire.POWER:
                    powerbond = bw
                    break

            if powerbond is None:
                raise LayoutError('No connected power bondwire!')

            if dev.orientation == 1:

                # On vertical trace
                # orient device by power bonds
                if powerbond.trace.trace_rect.left < trace_rect.left:
                    dev.orientation = 2  # 180 degrees from ref.
                else:
                    dev.orientation = 1  # 0 degrees from ref.
            elif dev.orientation == 3:
                if powerbond.trace.trace_rect.top < trace_rect.top:
                    dev.orientation = 3  # 180 degrees from ref.
                else:
                    dev.orientation = 4  # 0 degrees from ref.


def sym_place_leads(sym_layout, sym_info=None):
    for lead in sym_layout.leads:
        if lead.tech.shape == Lead.BUSBAR:
            line = lead.parent_line
            trace_rect = line.trace_rect

            if line.element.vertical:
                hwidth = 0.5 * lead.tech.dimensions[1]
                hlength = 0.5 * lead.tech.dimensions[0]
                lead.orientation = 3

                # find if near left or right (decide orientation)
                # for power leads only right now
                edge_dist = sym_layout.sub_dim[0] - 0.5 * (trace_rect.left + trace_rect.right)
                if edge_dist < 0.5 * sym_layout.sub_dim[0]:
                    # right
                    xpos = trace_rect.right - hwidth
                    lead.orientation = 3
                else:
                    # left
                    xpos = trace_rect.left + hwidth
                    lead.orientation = 4

                ypos = 0.5 * (trace_rect.bottom + trace_rect.top)
                lead.footprint_rect = Rect(ypos + hlength, ypos - hlength, xpos - hwidth, xpos + hwidth)
            else:
                # find if near top or bottom (decide orientation)
                hwidth = 0.5 * lead.tech.dimensions[0]
                hlength = 0.5 * lead.tech.dimensions[1]
                lead.orientation = 1

                edge_dist = sym_layout.sub_dim[1] - 0.5 * (trace_rect.top + trace_rect.bottom)
                if edge_dist < 0.5 * sym_layout.sub_dim[1]:
                    # top
                    ypos = trace_rect.top - hlength
                    lead.orientation = 1
                else:
                    # bottom
                    ypos = trace_rect.bottom + hlength
                    lead.orientation = 2

                xpos = 0.5 * (trace_rect.left + trace_rect.right)
                lead.footprint_rect = Rect(ypos + hlength, ypos - hlength, xpos - hwidth, xpos + hwidth)

            lead.center_position = (xpos, ypos)
        elif lead.tech.shape == Lead.ROUND:
            lead_region = sym_info[lead.element.path_id]
            radius = 0.5 * lead.tech.dimensions[0]
            center = [lead_region.left + radius, lead_region.bottom]
            lead.footprint_rect = Rect(center[1] + radius, center[1] - radius,
                                       center[0] - radius, center[0] + radius)
            lead.center_position = center


def sym_place_bondwires(sym_layout):
    for wire in sym_layout.bondwires:
        if wire.dev_pt is not None:
            sym_layout._place_device_bondwire(wire)


def eval_layout(sym_layout=None, layout_info=None, id=None):
    # convert a layout to right PS format
    sym_update_layout(sym_layout=sym_layout, sym_info=layout_info)  # Generate the traces in PowerSynth

    ''' Plot the layout'''
    plot = False  # Change this flag
    if plot == True:
        fig, ax = plt.subplots()
        plot_layout(sym_layout=sym_layout, ax=ax)
        plt.show
    # raw_input()
    ret = one_measure(sym_layout)
    # print ret
    return ret


def random_layout(directory):
    sym_layout = init_sym_layout(directory)
    New_engine = New_layout_engine()
    New_engine.init_layout_from_symlayout(sym_layout)

    cons_file = 'out.csv'
    if cons_file is not None:
        New_engine.cons_df = pd.read_csv(cons_file)

    W = 20000 # width of the layout
    H = 20000 # height of the layout

    opt_problem = new_engine_opt(engine=New_engine, W=W, H=H, sym_layout=sym_layout)

    data=opt_problem.optimize() # list of solutions: [{'T2': x: 2.123, y: 1.638, w: 17.877, h: 7.439, 'T3': x: 0.0, y: 9.077, w: 20.0, h: 10.923, 'T1': x: 0.0, y: 0.0, w: 20.0, h: 1.638},....,{.....}]

    print data



def test1():
    # The test goes here, moddify the path below as you wish...
    app = QtGui.QApplication(sys.argv)
    directory = 'Layout//u_shape.psc'  # directory to layout script
    random_layout(directory)
    sys.exit(app.exec_())


test1()