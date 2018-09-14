# This will test the new lumped graph structure along with Kelvin connection
#@authors: Quang Le
import os
import copy
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
from powercad.corner_stitch import *
from powercad.corner_stitch import CornerStitch as CS

class Rectangle():
    def __init__(self,type=None,x=None,y=None,width=None,height=None,Schar=None,Echar=None,Netid=None):

        self.type = type
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.Schar = Schar
        self.Echar=Echar
        self.Netid=Netid





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

def draw_layout(Rectangles,max_x,max_y,path):
    fig10, ax5 = plt.subplots()
    colors=['green','red','blue','yellow','pink']
    type=['Type_1','Type_2','Type_3','Type_4']
    for i in Rectangles:
        for t in type:
            if i.type==t:
                type_ind=type.index(t)
                colour=colors[type_ind]


        ax5.add_patch(
            matplotlib.patches.Rectangle(
                (i.x, i.y),  # (x,y)
                i.width,  # width
                i.height,  # height
                facecolor=colour, edgecolor='black'

            )
        )


    plt.xlim(0, max_x)
    plt.ylim(0, max_y)
    # plt.xlim(0, 60)
    # plt.ylim(0, 100)#fig10.show()
    # return fig10
    #plt.show()
    fig10.savefig(path+'/'+'layout.png', bbox_inches='tight')
    # fig10.savefig(testdir + '/' +'Mode-'+str(level)+'/'+ testbase + str(k) + "H.eps",format='eps', bbox_inches='tight')
    plt.close()
def _id_ortho_connections(self, trace1, trace2):
    obj1 = trace1.trace_line # vertical
    obj2 = trace2.trace_line # horizontal

    # Identify connected normal traces
    # Connections at right angle
    if obj1.pt1[0] >= obj2.pt1[0] and obj1.pt1[0] <= obj2.pt2[0] and \
       obj2.pt1[1] >= obj1.pt1[1] and obj2.pt1[1] <= obj1.pt2[1]:     #  Draw 2 traces and named them obj1 and obj2.. obj1 is vertical and should form a T or L shape with obj2.
       # pt1 and pt2 are 2 points at 2 ends of the traces... Draw a X-Y axis and put this picture in you can imagine this condition
        trace1.trace_connections.append(trace2)                       #  Set trace 1 trace_connections value equal trace 2
        trace2.trace_connections.append(trace1)                       #  Set trace 2 trace_connections value equal trace 1
        if not(frozenset([trace1, trace2]) in self.tmp_conn_dict):    #  check if these 2 are already added to a set or not
            # Append the connection to list
            self.tmp_conn_dict[frozenset([trace2, trace1])] = 1       # if not create a set for them this set type is 1
            pt = self._intersection_pt(obj1, obj2)                    # Find the intersection point of 2 traces go to _intersection_pt to read more
            self.trace_trace_connections.append([trace1, trace2, pt, False]) # add this connection group to the list
    # Identify Supertraces
    if obj1.pt1[0] > obj2.pt1[0] and obj1.pt1[0] < obj2.pt2[0] and \
       obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1]:       # in case of T shape (from the pic you drew above this is a super trace
        if trace1.is_supertrace() or trace2.is_supertrace():
            raise LayoutError("Multiple intersection supertraces not supported! check for multiple T shapes on your layout")
        trace1.intersecting_trace = trace2                            #  Set trace 1 intersecting_trace value equal trace 2 > go to SymLine class to read more
        trace2.intersecting_trace = trace1                            #  Set trace 2 intersecting_trace value equal trace 1 > go to SymLine class to read more
        # trace1 is vertical, trace2 is horizontal
        self.all_super_traces.append((trace1, trace2, (obj2.pt1[0],obj2.pt2[0]), (obj1.pt1[1],obj1.pt2[1])))  # append this group to supertrace list
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


def random_layout(directory):
    ''' Test generate layout time for WIPDA (Imam)'''
    temp_dir = os.path.abspath(settings.TEMP_DIR)  # The directory where thermal characterization files are stored

    test_file = os.path.abspath(directory)  # A layout script file, you can link this to any file you want

    sym_layout = SymbolicLayout()  # initiate a symbolic layout object

    sym_layout.load_layout(test_file, 'script')  # load the script

    #for obj in sym_layout.all_sym:
        #print  type(obj)
    x_coordinates=[]                        # stores the x coordinates of all objects for conversion
    y_coordinates=[]                        # stores the y coordinates of all objects for conversion
    for obj in sym_layout.all_lines:

        x_coordinates.append(obj.pt1[0])
        y_coordinates.append(obj.pt1[1])

        x_coordinates.append(obj.pt2[0])
        y_coordinates.append(obj.pt2[1])
    for obj in sym_layout.all_points:
        x_coordinates.append(obj.pt[0])
        y_coordinates.append(obj.pt[1])
    #print set(x_coordinates),set(y_coordinates)
    x_coordinates=list(set(x_coordinates))
    y_coordinates=list(set(y_coordinates))

    converted_x_coordinates=[(i+1)*10 for i in x_coordinates] # stores the converted x coordinates of all objects for conversion
    converted_y_coordinates = [(i+1) * 10 for i in y_coordinates] # stores the converted y coordinates of all objects for conversion
    x_max = max(converted_x_coordinates) # stores maximum x value to determine total width of the layout
    y_max = max(converted_y_coordinates) # stores max y value to determine total height of the layout
    #print x_max,y_max, converted_x_coordinates, converted_y_coordinates
    Rectangles=[] # stores rectangle objects with (Type,x,y,width,height)
    Super_Traces=[] # stores super traces
    Super_Traces_dict={} # stores super traces {(vertical trace y2,y2,x2,x2):horizontal trace}
    Connected={}

    Points=[]
    for obj in sym_layout.all_lines:
        Points.append(obj.pt1)
        Points.append(obj.pt2)

    Points=list(set(Points))
    print Points
    '''
    for point in Points:
        key=point
        Connected.setdefault(key,[])
        for obj1 in sym_layout.all_lines:
            for obj2 in sym_layout.all_lines:
                if point==obj1.pt2==obj2.pt1 or point==obj1.pt1==obj2.pt1 or point==obj1.pt1==obj2.pt2 or point==obj1.pt2==obj2.pt2:
                    if obj1 not in Connected.values():
                        Connected[point].append(obj1)
                    if obj2 not in Connected.values():
                        Connected[point].append(obj2)
    '''

    for obj1 in sym_layout.all_lines:
        for obj2 in sym_layout.all_lines:
            if obj1!=obj2:
                if obj1.pt1[0] >= obj2.pt1[0] and obj1.pt1[0] <= obj2.pt2[0] and \
                        obj2.pt1[1] >= obj1.pt1[1] and obj2.pt1[1] <= obj1.pt2[1]:
                    pt=intersection_pt(obj1, obj2)
                    if not (frozenset([obj1, obj2]) in Connected.values()):
                        Connected[pt]=([obj1,obj2])



    for obj1 in sym_layout.all_lines:
        for obj2 in sym_layout.all_lines:
            if obj1!=obj2:

                if obj1.pt1[0] > obj2.pt1[0] and obj1.pt1[0] < obj2.pt2[0] and obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1] and obj1.vertical!=obj2.vertical:  # in case of T shape (from the pic you drew above this is a super trace
                    #print obj1.pt1,obj1.pt2,obj2.pt1,obj2.pt2
                    Super_Traces.append(obj1)
                    Super_Traces.append(obj2)
                    Super_Traces_dict[(obj1.pt2[1],obj1.pt1[1],obj1.pt2[0],obj1.pt1[0])]=obj2
            else:
                continue

                    #sym_layout.all_lines.remove(obj1)

    #print Connected
    Intersections={}
    for k, v in Connected.items():
        print k
        for i in v:
            print i.path_id

        lines=list(set(v))
        if len(lines)>1:
            Intersections[k]=lines




    Net={}

    N=Intersections.values()
    print N
    id=0
    All_objects=[item for sublist in N for item in sublist]
    All_objects=list(set(All_objects))


    for obj in All_objects:
        key=id
        Net.setdefault(key, [])
        for element in N:
            if obj in element and element not in Net.values():
                Net[key].append(element)
            else:
                continue
        id+=1
    print Net
    Nets=[]
    for k,v in Net.items():

        if len(v)>1:
            Value = [item for sublist in v for item in sublist]
            Value=list(set(Value))
            Nets.append(Value)
        elif len(v)>0:
            if v not in Nets:
                Nets.append(v)
    #print"N", len(Nets)
    print len(Nets)
    All_connected=[item for sublist in Nets for item in sublist]
    for obj1 in sym_layout.all_lines:

        if obj1 not in All_connected:
            Nets.append([obj1])
    print"N", len(Nets)

    for obj in sym_layout.all_lines:
        if obj not in Super_Traces:
            if obj.vertical == True:
                x_ind=x_coordinates.index(obj.pt1[0])
                y_ind=y_coordinates.index(obj.pt1[1])
                #x_ind2=x_coordinates.index(obj.pt2[0])
                y_ind2=y_coordinates.index(obj.pt2[1])

                x=converted_x_coordinates[x_ind]
                y=converted_y_coordinates[y_ind]
                height=converted_y_coordinates[y_ind2]-y
                width=8


            else:
                x_ind = x_coordinates.index(obj.pt1[0])
                y_ind = y_coordinates.index(obj.pt1[1])
                x_ind2=x_coordinates.index(obj.pt2[0])
                #print x_ind2
                #y_ind2 = y_coordinates.index(obj.pt2[1])
                x = converted_x_coordinates[x_ind]
                y = converted_y_coordinates[y_ind]
                width = converted_x_coordinates[x_ind2] - x+8
                height = 8


        else:
            if obj.vertical== False:

                for k,v in Super_Traces_dict.items():
                    if v==obj:
                        x_ind = x_coordinates.index(obj.pt1[0])
                        y_ind = y_coordinates.index(k[1])
                        x_ind2 = x_coordinates.index(obj.pt2[0])
                        # print x_ind2
                        # y_ind2 = y_coordinates.index(obj.pt2[1])
                        x = converted_x_coordinates[x_ind]
                        y = converted_y_coordinates[y_ind]
                        width = converted_x_coordinates[x_ind2] - x + 8
                        y_ind2 = y_coordinates.index(k[0])
                        # x_ind2=x_coordinates.index(obj.pt2[0])
                        y_ind1 = y_coordinates.index(k[1])
                        y2=converted_y_coordinates[y_ind2]
                        y1=converted_y_coordinates[y_ind1]
                        height=y2-y1
                        #print"H", x,y,height

        if obj.pt1  in Intersections.keys() and obj.pt2 in Intersections.keys() :
            Schar = '%'
            Echar = '%'
        elif obj.pt1 not in Intersections.keys() and obj.pt2 not in Intersections.keys() :
            Schar = '/'
            Echar = '/'
        else:
            Schar=None
            Echar=None
        for element in Nets:
            if obj in element:
                Netid=Nets.index(element)



        Rectangles.append(Rectangle('Type_1',x,y,width,height,Schar,Echar,Netid))
        #print obj.path_id, x, y, width, height
    Rectangles.sort(key=lambda x: x.Netid, reverse=False)
    ID=[i for i in range(len(Nets))]
    #print ID
    for i in ID:
        count = 0
        for R in Rectangles:

            if i==R.Netid:

                if R.Schar==None and R.Echar==None:
                    if count == 0:
                        count+=1
                        R.Schar='/'
                        R.Echar='%'
                    else:
                        R.Schar = '%'
                        R.Echar = '/'
                else:
                    continue
    Rectangles_cpy=copy.deepcopy(Rectangles)
    Input_rects=[]
    while len(Rectangles_cpy)>0:
        for i in ID:
            for rect in Rectangles_cpy:
                if rect.Schar=='/' and i==rect.Netid :
                    Input_rects.append(rect)
                    Rectangles_cpy.remove(rect)
                else:
                    continue
            for rect in Rectangles_cpy:
                if rect.Schar=='%' and i==rect.Netid and rect.Echar=='%' :
                    Input_rects.append(rect)
                    Rectangles_cpy.remove(rect)
                else:
                    continue
            for rect in Rectangles_cpy:
                if rect.Echar=='/' and i==rect.Netid :
                    Input_rects.append(rect)
                    Rectangles_cpy.remove(rect)
                else:
                    continue
            for rect in Rectangles_cpy:
                if rect.Schar=='/' and i==rect.Netid and rect.Echar=='/' :
                    Input_rects.append(rect)
                    Rectangles_cpy.remove(rect)
                else:
                    continue

    for obj in sym_layout.all_points:
        if obj.path_id[0]=='M':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind]+2
            y = converted_y_coordinates[y_ind]+2
            width=4
            height=4
            type='Type_2'
        elif obj.path_id[0]=='L':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind]+1
            y = converted_y_coordinates[y_ind]+2
            width=6
            height=4
            type='Type_3'
        elif obj.path_id[0]=='D':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind]+2
            y = converted_y_coordinates[y_ind]+2
            width=3
            height=3
            type='Type_4'

        Input_rects.append(Rectangle(type, x, y, width, height,Schar='/',Echar='/'))
        path='D:\Initial_Layouts\TEST'
        name="layout"

    for R in Input_rects:

        print"T", R.Schar, R.x, R.y, R.width, R.height, R.type, R.Echar, R.Netid
    CS1=CS.CornerStitch(0)
    CS1.getConstraints(path+'/'+'Constraints-1.csv')
    INPUT=CS1.read_input('list',Rect_list=Input_rects)
    CS1.input_processing(INPUT,x_max+20,y_max+20,path,name)

        #print obj.path_id,x,y,width,height

    #draw_layout(Rectangles,x_max+20,y_max+20,path)


    raw_input()

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

    module = gen_test_module_data(f)
    # Pepare for optimization.

    sym_layout.form_design_problem(module, temp_dir)  # Collect data to user interface
    sym_layout._map_design_vars()
    setup_model(sym_layout)

def test1():
    # The test goes here, moddify the path below as you wish...
    directory ='Layout//CS-conversion//layout.psc' # directory to layout script
    random_layout(directory)

test1()