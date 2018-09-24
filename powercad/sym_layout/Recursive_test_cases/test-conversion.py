# This will test the new lumped graph structure along with Kelvin connection
#@authors: Quang Le
import os
import copy
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib
from powercad.Spice_handler.spice_import.NetlistImport import Netlist, Netlis_export_ADS
from powercad.design.module_data import gen_test_module_data
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
import sys
from PySide import QtGui
from PySide.QtGui import QFileDialog,QMainWindow
from powercad.project_builder.proj_dialogs import New_layout_engine_dialog
from powercad.corner_stitch.API_PS import *
from powercad.corner_stitch.CornerStitch import *
from powercad.general.data_struct.util import *
class Rectangle(Rect):
    def __init__(self,type=None,x=None,y=None,width=None,height=None,name=None,Schar=None,Echar=None,Netid=None):
        '''

        Args:
            type: type of each component: Trace=Type_1, MOS= Type_2, Lead=Type_3, Diode=Type_4
            x: bottom left corner x coordinate of a rectangle
            y: bottom left corner y coordinate of a rectangle
            width: width of a rectangle
            height: height of a rectangle
            Netid: id of net, in which component is connected to
            name: component path_id (from sym_layout object)
            Schar: Starting character of each input line for input processing:'/'
            Echar: Ending character of each input line for input processing: '/'
        '''


        self.type = type
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.Schar = Schar
        self.Echar=Echar
        self.Netid=Netid
        self.name=name

        # inheritence member variables
        self.top=self.y+self.height
        self.bottom = self.y
        self.left = self.x
        self.right = self.x + self.width






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
    dev_mos = DeviceInstance(0.1, 5.0, get_mosfet(),get_dieattach())  # Create a device instance with 10 W power dissipation. Highlight + "Crtl+Shift+I" to see the definition of this object

    pow_lead = get_power_lead()  # Get a power lead object

    sig_lead = get_signal_lead()  # Get a signal lead object

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

def plot_layout(Layout_Rects,level,path=None,name=None):
    Patches=[]
    if level==0:
        Rectangles=[]
        for k,v in Layout_Rects.items():
            if k=='H':
                for rect in v:                    #rect=[x,y,width,height,type]
                    Rectangles.append(rect)
        max_x = 0
        max_y = 0
        min_x = 1000
        min_y = 1000

        for i in Rectangles:

            if i[0] + i[2] > max_x:
                max_x = i[0] + i[2]
            if i[1] + i[3] > max_y:
                max_y = i[1] + i[3]
            if i[0] < min_x:
                min_x = i[0]
            if i[1] < min_y:
                min_y = i[1]
        #fig1, ax1 = plt.subplots()
        colors=['White','green','red','blue','yellow','pink']
        type=['EMPTY','Type_1','Type_2','Type_3','Type_4']
        ALL_Patches={}
        key=(max_x,max_y)
        ALL_Patches.setdefault(key,[])
        for i in Rectangles:
            for t in type:
                if i[4]==t:
                    type_ind=type.index(t)
                    colour=colors[type_ind]
            R=matplotlib.patches.Rectangle(
                    (i[0], i[1]),  # (x,y)
                    i[2],  # width
                    i[3],  # height
                    facecolor=colour,

                )
            ALL_Patches[key].append(R)

            #ax1.add_patch(R)



        #plt.xlim(0, max_x)
        #plt.ylim(0, max_y)

        #fig1.savefig(path+'/'+name+'-layout.png', bbox_inches='tight')
        #plt.close()
        Patches.append(ALL_Patches)



    else:
        for k,v in Layout_Rects.items():

            if k=='H':
                Total_H = {}

                for j in range(len(v)):


                    Rectangles = []
                    for rect in v[j]:  # rect=[x,y,width,height,type]
                        Rectangles.append(rect)
                    max_x = 0
                    max_y = 0
                    min_x = 1000
                    min_y = 1000

                    for i in Rectangles:
                        #print i
                        if i[0] + i[2] > max_x:
                            max_x = i[0] + i[2]
                        if i[1] + i[3] > max_y:
                            max_y = i[1] + i[3]
                        if i[0] < min_x:
                            min_x = i[0]
                        if i[1] < min_y:
                            min_y = i[1]
                    key=(max_x,max_y)
                    Total_H.setdefault(key,[])
                    Total_H[(max_x,max_y)].append(Rectangles)
        j = 0


        for k,v in Total_H.items():
            for i in range(len(v)):

                Rectangles = v[i]
                max_x=k[0]
                max_y=k[1]
                ALL_Patches = {}
                key = (max_x, max_y)
                ALL_Patches.setdefault(key, [])
                #fig1 = matplotlib.pyplot.figure()
                #ax1 = fig1.add_subplot(111, aspect='equal')

                colors = ['White', 'green', 'red', 'blue', 'yellow', 'pink']
                type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4']
                for i in Rectangles:
                    for t in type:
                        if i[4] == t:
                            type_ind = type.index(t)
                            colour = colors[type_ind]
                    R= matplotlib.patches.Rectangle(
                            (i[0], i[1]),  # (x,y)
                            i[2],  # width
                            i[3],  # height
                            facecolor=colour,

                        )
                    ALL_Patches[key].append(R)


                #plt.xlim(0, max_x)
                #plt.ylim(0, max_y)
                #fig1.savefig(path + '/' + name +'-'+str(j)+ '.png', bbox_inches='tight')
                j+=1
                Patches.append(ALL_Patches)

    return Patches



def intersection_pt(line1, line2):    # Find intersection point of 2 orthogonal traces
    x = 0                                    # initialize at 0
    y = 0                                    # initialize at 0
    if line1.vertical:                       # line 1 is vertical
        x = line1.pt1[0]                     # take the x value from line 1
    else:                                    # line 1 is horizontal
        y = line1.pt1[1]                     # take the y value from line 1

    if line2.vertical:                       # line2 is vertical
        x = line2.pt1[0]                     # take the x value from line 2
    else:                                    # line 2 is horizontal
        y = line2.pt1[1]                     # take the y value from line 2

    return x, y
def Sym_to_CS(input_rects,Htree,Vtree):
    ALL_RECTS={}
    DIM=[]

    for j in Htree.hNodeList[0].stitchList:

        #for j in i.stitchList:
        p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
        DIM.append(p)
    ALL_RECTS['H']=DIM
    DIM = []
    for j in Vtree.vNodeList[0].stitchList:

        #for j in i.stitchList:
        p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
        DIM.append(p)
    ALL_RECTS['V']=DIM

    SYM_CS={}
    for rect in input_rects:
        x1=rect.x
        y1=rect.y
        x2=rect.x+rect.width
        y2=rect.y+rect.height
        type=rect.type
        name=rect.name
        for k,v in ALL_RECTS.items():
            if k=='H':
                key=name
                SYM_CS.setdefault(key,[])
                for i in v:
                    if i[0]>=x1 and i[1]>=y1 and i[0]+i[2]<=x2 and i[1]+i[3]<=y2 and i[4]==type:
                        SYM_CS[key].append(i)
                    else:
                        continue
    return SYM_CS




def random_layout(directory):
    ''' Test generate layout time for WIPDA (Imam)'''
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script

    #for obj in sym_layout.all_sym:
        #print  type(obj)
    

    path = 'D:\Initial_Layouts\TEST'
    name = "RD-100"
    app = QtGui.QApplication(sys.argv)
    window = QMainWindow()
    New_engine = New_layout_engine()
    New_engine.init_layout_from_symlayout(sym_layout)
    New_engine.open_new_layout_engine(window=window)
    

class New_layout_engine():
    def __init__(self):
        self.W=None
        self.H=None
        self.window=None
        self.Htree=None
        self.Vtree=None
        self.cons_df=None
        # for initialize only
        self.init_data=[]
        self.cornerstitch=CornerStitch()
        # current solutions
        self.cur_fig_data=None
    def open_new_layout_engine(self,window):
        self.window=window
        patches = self.init_data[0]
        graph=self.init_data[2]
        self.new_layout_engine = New_layout_engine_dialog(self.window, patches,graph, self.W+20, self.H+20,engine=self)
        self.new_layout_engine.exec_()
    def init_layout_from_symlayout(self,sym_layout):
        '''
        initialize new layout engine with old symlayout data structure
        Returns:
        '''
        input_rects, self.W, self.H = input_conversion(sym_layout)
        input = self.cornerstitch.read_input('list', Rect_list=input_rects)
        self.Htree, self.Vtree = self.cornerstitch.input_processing(input, self.W + 20, self.H + 20)
        #print self.Htree
        #print self.Vtree
        #print input_rects



        patches,combined_graph=self.cornerstitch.draw_layout(input_rects)
        sym_to_cs = Sym_to_CS(input_rects, self.Htree, self.Vtree)

        self.init_data=[patches,sym_to_cs,combined_graph]


    def generate_solutions(self,level,num_layouts=1,W=None,H=None):
        CG1 = CS_to_CG(level)
        # CG1.getConstraints(path+'/'+'Constraints-1.csv')
        CG1.getConstraints(self.cons_df)
        #Node_conbined = CG1.combined_graph(self.Htree, self.Vtree)
        #print Node_conbined
        sym_to_cs=self.init_data[1]
        if level == 0:
            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None,XLoc=None,YLoc=None)
            CS_SYM_information, Layout_Rects = CG1.UPDATE_min(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree,sym_to_cs)  # CS_SYM_information is a dictionary where key=path_id(component name) and value=list of updated rectangles, Layout Rects is a dictionary for minimum HCS and VCS evaluated rectangles (used for plotting only)
            #print "CY", CS_SYM_information

            self.cur_fig_data = plot_layout(Layout_Rects, level)
            #print self.cur_fig_data
            CS_SYM_Updated={}
            for i in self.cur_fig_data:
                for k,v in i.items():
                    CS_SYM_Updated[k]=CS_SYM_information
            #print "CY", CS_SYM_Updated

        elif level==1:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=None, H=None,XLoc=None, YLoc=None)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y,self.Htree, self.Vtree, sym_to_cs)

            self.cur_fig_data = plot_layout(Layout_Rects, level)
        elif level==2:
            CG2 = CS_to_CG(0)
            Evaluated_X0, Evaluated_Y0 = CG2.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None,XLoc=None,YLoc=None)

            #print"Eval0", Evaluated_X0, Evaluated_Y0
            Min_X_Loc = {}
            Min_Y_Loc = {}
            for k, v in Evaluated_X0.items():
                XLoc = v.keys()
                max_x = v[max(XLoc)]
            for k, v in Evaluated_Y0.items():
                YLoc = v.keys()
                max_y = v[max(YLoc)]
            XLoc.sort()
            YLoc.sort()

            #Min_X_Loc[0] = 0
            #Min_Y_Loc[0] = 0
            Min_X_Loc[len(XLoc) - 1] = max_x
            Min_Y_Loc[len(YLoc) - 1] = max_y


            for k,v in Min_X_Loc.items():
                if W>v:
                    Min_X_Loc[0] = 0
                    Min_X_Loc[k]=W
            for k,v in Min_Y_Loc.items():
                if H>v:
                    Min_Y_Loc[0] = 0
                    Min_Y_Loc[k]=H

            #print Min_X_Loc, Min_Y_Loc,num_layouts
            Min_X_Loc=collections.OrderedDict(sorted(Min_X_Loc.items()))
            Min_Y_Loc = collections.OrderedDict(sorted(Min_Y_Loc.items()))
            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=W, H=H,XLoc=Min_X_Loc, YLoc=Min_Y_Loc)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs)
            #print "CY", CS_SYM_information
            self.cur_fig_data = plot_layout(Layout_Rects, level)


        return self.cur_fig_data
def test1():
    # The test goes here, moddify the path below as you wish...
    directory ='Layout//CS-conversion//simple_switch.psc' # directory to layout script
    random_layout(directory)

test1()