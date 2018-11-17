import networkx as nx
import pandas as pd
from powercad.parasitics.analysis import parasitic_analysis
from powercad.parasitics.mdl_compare import trace_cap_krige, trace_ind_krige, trace_res_krige
from powercad.parasitics.models_bk import trace_inductance, trace_resistance, trace_capacitance, wire_inductance, \
    wire_resistance
from powercad.general.data_struct.util import Rect, complex_rot_vec, get_overlap_interval, distance
import math
from powercad.design.project_structures import DeviceInstance
from powercad.design.library_structures import Lead, BondWire
from powercad.parasitics.mdl_compare import load_mdl
from powercad.sym_layout.plot import plot_layout
import matplotlib.pyplot as plt
import copy

DEVICE_POI = 1
BAR_LEAD_POI = 2
RND_LEAD_POI = 3
TRACE_POI = 4
BW_POI = 5
TRACE_TRACE_BW_POI = 6
SUPER_POI = 7
LONG_POI = 8
END_POI = 9

class E_graph():

    def __init__(self,sym_layout):

        # Set of data structure between sym_layout and E_graph().. Will be returned to sym_layout object
        self.sym_layout=sym_layout
        self.trace_info=[]
        self.trace_nodes=[]
        self.corner_nodes=[]
        self.corner_info=[]

        # Required data from Sym_layout
        self.all_super_traces=sym_layout.all_super_traces
        self.all_trace_lines=sym_layout.all_trace_lines
        self.boundary_connections=sym_layout.boundary_connections
        self.mdl_type=sym_layout.mdl_type
        self.module = sym_layout.module
        self.super_traces=sym_layout.all_super_traces
        # Data frame to store NODEs on each traces
        self.normal_trace_df = pd.DataFrame(columns=["ID", "POI_Type", "Data_Type","Point","Condition",'node','i','j','side']) # for non super traces case
        if sym_layout.mdl_type['E']=='RS':
            self.set_model()
    def set_model(self):
        self.LAC_mdl = self.sym_layout.LAC_mdl
        self.RAC_mdl = self.sym_layout.RAC_mdl
        self.C_mdl = self.sym_layout.C_mdl
        '''
        self.bw_mdl = load_mdl('C://Users//qmle//Desktop//Testing//FastHenry//Fasthenry3_test_gp//WorkSpace_bw',
                               mdl_name='bw.mdl')  # TODO: Remember to fix after WIPDA
        corner_mdl = load_mdl(dir='C://Users//qmle//Desktop//Testing//FastHenry//Fasthenry3_test_gp//WorkSpace1',
                              mdl_name='corner_test_adapt_2.rsmdl')
        self.L_corner_mdl = corner_mdl['L']
        '''
    def _get_trace_data(self):
        thickness = self.module.substrate.substrate_tech.metal_thickness
        sub_thick = self.module.substrate.substrate_tech.isolation_thickness
        sub_epsil = self.module.substrate.substrate_tech.isolation_properties.rel_permit
        resist = self.module.substrate.substrate_tech.metal_properties.electrical_res
        freq = self.module.frequency
        return [thickness,sub_thick,sub_epsil,resist,freq]

    def _add_node(self, graph, vert_count, attrib):
        # point spine
        graph.add_node(vert_count, attr_dict=attrib)
        nodeout = vert_count
        vert_count += 1
        return nodeout, vert_count

    def _spine_path_eval(self, n1, n2, trace_data, lumped_graph):
        # trace_data = (trace, metal thickness, iso thickness, lumped_graph)
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']
        if trace_data[0].element.vertical:
            width = trace_data[0].trace_rect.width()
            length = math.fabs(pt2[1] - pt1[1])
        else:
            width = trace_data[0].trace_rect.height()
            length = math.fabs(pt2[0] - pt1[0])
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1, 'res': 1.0 / 1, 'cap': 1.0 / 1,
                               'type': 'trace', 'width': width, 'length': length})
        self._collect_trace_parasitic_post_eval(width, length, n1, n2)
        return lumped_graph

    def _trace_conn_path_eval(self, n1, n2, trace_data, conn_trace, lumped_graph):
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']

        main = None  # main trace
        conn = None  # connecting trace
        # Determine which trace is ortho. to conn. direction
        if pt1[0] == pt2[0]:
            # Conn. is vertical
            if conn_trace.element.vertical:
                conn = conn_trace
                main = trace_data[0]
            else:
                conn = trace_data[0]
                main = conn_trace
        else:
            # Conn. is horizontal
            if not conn_trace.element.vertical:
                conn = conn_trace
                main = trace_data[0]
            else:
                conn = trace_data[0]
                main = conn_trace

        if main.element.vertical:
            width = conn.trace_rect.height()
            length = math.fabs(pt2[0] - pt1[0])
        else:
            width = conn.trace_rect.width()
            length = math.fabs(pt2[1] - pt1[1])
        # print 'corner', width,length*2
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1e-3, 'res': 1.0 / 1e-3, 'cap': 1.0 / 1e-2,
                               'type': 'trace', 'width': width, 'length': length})
        self._collect_trace_parasitic_post_eval(width, length, n1,
                                                n2)  # Source of overestimation, need to look at this again
        self._collect_corner_correction_post_eval(width, length * 2, n1, n2)

        return lumped_graph

    def _lead_trace_path_eval(self, n1, n2, trace_data, lead, lumped_graph):
        pt1 = trace_data[3].node[n1]['point']
        pt2 = trace_data[3].node[n2]['point']
        if trace_data[0].element.vertical:
            length = math.fabs(pt2[0] - pt1[0])
        else:
            length = math.fabs(pt2[1] - pt1[1])

        width = lead.tech.dimensions[0]

        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1e-3, 'res': 1 / 1e-6, 'cap': 1.0 / 1e-3,
                               'type': 'trace', 'width': width, 'length': length})
        #self._collect_trace_parasitic_post_eval(10000, 0, n1, n2)
        return lumped_graph

    def _bondwire_to_spine_eval(self, n1, n2, trace_data, num_wires, wire_eff_diam, lumped_graph):
        trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil = trace_data
        pt1 = lumped_graph.node[n1]['point']
        pt2 = lumped_graph.node[n2]['point']
        path_length = distance(pt1, pt2)
        width = num_wires * wire_eff_diam
        lumped_graph.add_edge(n1, n2,
                              {'ind': 1.0 / 1e-3, 'res': 1.0 / 1e-3, 'cap': 1.0 / 1e-3,
                               'type': 'trace_bw', 'width': width, 'length': path_length})
        # self._collect_trace_parasitic_post_eval(10000, 0, n1, n2)
        return lumped_graph

    def _bondwire_eval(self, n1, n2, trace_data, bw, num_wires):
        # Partial Inductance:
        wire_radius = 0.5 * bw.tech.eff_diameter()
        resist = bw.tech.properties.electrical_res
        inv_ind = 0.0
        inv_res = 0.0
        b = bw.tech.b
        a = bw.tech.a
        # print "a,b",a,b
        for pt1, pt2 in zip(bw.start_pts, bw.end_pts):
            D = distance(pt1, pt2)
            l1 = D - D / 8
            length = l1 / math.cos(math.atan(2 * a / l1)) + D / 8
            wire_ind = wire_inductance(length, wire_radius)
            wire_res = wire_resistance(trace_data[4], length, wire_radius, resist)
            inv_res += 1.0 / wire_res
            inv_ind += 1.0 / wire_ind
        #self.bw_mdl = load_mdl('C://Users//qmle//Desktop//Testing//FastHenry//Fasthenry3_test_gp//WorkSpace_bw',
                               #mdl_name='bw.mdl')
        #R, L = wire_group(self.bw_mdl, D)
        '''
        print "distance",D
        print "bw group",R,L
        '''
        if trace_data[4] < 1000:
            R = 1.25
        # print 'wire group',R,L
        #inv_res = 1 / R
        #inv_ind = 1 / L

        return 1.0 / inv_ind, 1.0 / inv_res, 1e-3
        # return 1e-6, 1e-6, 1e-3

    def _build_lumped_edges(self, trace_data, lumped_graph):
        '''
        :param trace_data:
        :param lumped_graph:
        :return:
        '''
        w_all = []
        l_all = []
        w1_all = []
        w2_all = []
        t_num = len(self.trace_info)  # number of traces
        c_num = len(self.corner_info)
        # print "corner num",c_num
        f = trace_data[4]
        print self.mdl_type['E']
        if self.mdl_type['E'] == 'RS':
            # print "selected RS"
            for w, l in self.trace_info:
                w_all.append(w)
                l_all.append(l)
            # print 'width,length', w_all,l_all
            ind1 = trace_ind_krige(f, w_all, l_all, self.LAC_mdl).tolist()
            res1 = trace_res_krige(f, w_all, l_all, trace_data[1], trace_data[5], self.RAC_mdl).tolist()
            if self.C_mdl != None:
                cap1 = trace_cap_krige(w_all, l_all, self.C_mdl).tolist()
            else:
                cap1 = []
                for pair in zip(w_all, l_all):
                    cap1.append(trace_capacitance(pair[0], pair[1], trace_data[1], trace_data[2], trace_data[6]))
            for i in range(t_num):
                nodes = self.trace_nodes[i]
                # print "traces - nodes",nodes
                lumped_graph[nodes[0]][nodes[1]]['ind'] = 1 / ind1[i]
                lumped_graph[nodes[0]][nodes[1]]['res'] = 1 / res1[i]
                lumped_graph[nodes[0]][nodes[1]]['cap'] = 1 / cap1[i]
            # corner correction here:
            for w1, w2 in self.corner_info:
                w1_all.append(w1)
                w2_all.append(w2)
                # print "widths",w1,w2
            #correction = trace_90_corner_ind(f, w1_all, w2_all, self.L_corner_mdl)
            for i in range(c_num):  # go through all corners
                nodes = self.corner_nodes[i]
                # take the piece out:
                # 'corners',nodes[0],nodes[1]
                l = 1 / lumped_graph[nodes[0]][nodes[1]]['ind']
                # apply correction
                # print correction[i]
                # l=l-correction[i] # TODO: General layout cases to apply
                lumped_graph[nodes[0]][nodes[1]]['ind'] = 1 / l

        elif self.mdl_type['E'] == 'MS':
               # print "selected MS"
            for i in range(t_num):
                nodes = self.trace_nodes[i]
                [w1, l1] = self.trace_info[i]
                if l1 <= 0.01:
                    l, r, c = [1e-6, 1e-6, 1e-3]
                else:
                    l, r, c = self._eval_parasitic_models(w1, l1, trace_data)
                lumped_graph[nodes[0]][nodes[1]]['ind'] = 1 / l
                lumped_graph[nodes[0]][nodes[1]]['res'] = 1 / r
                lumped_graph[nodes[0]][nodes[1]]['cap'] = 1 / c


    def _collect_corner_correction_post_eval(self, w1, w2, node1, node2):
        # print "hello"
        self.corner_info.append([w1, w2])
        self.corner_nodes.append([node1, node2])

    def _collect_trace_parasitic_post_eval(self, width, length, node_l, node_r):
        self.trace_info.append([width, length])
        nodes = [node_l, node_r]
        self.trace_nodes.append(nodes)

    def _eval_parasitic_models(self, width, length, trace_data):
        ind = trace_inductance(width, length, trace_data[1], trace_data[2])
        res = trace_resistance(trace_data[4], width, length, trace_data[1], trace_data[2], trace_data[5])
        cap = trace_capacitance(width, length, trace_data[1], trace_data[2], trace_data[6])
        return ind, res, cap

    def _eval_supertrace_parasitic_models(self, width, length, thickness, sub_thick, freq, resist, sub_epsil):
        ind = trace_inductance(width, length, thickness, sub_thick)
        res = trace_resistance(freq, width, length, thickness, sub_thick, resist)
        cap = trace_capacitance(width, length, thickness, sub_thick, sub_epsil)
        return ind, res, cap

    def plot_lumped_graph(self):
        pos = {}

        for n in self.sym_layout.lumped_graph.nodes():
            pos[n] = self.sym_layout.lumped_graph.node[n]['point']
        nx.draw_networkx(self.sym_layout.lumped_graph, pos)
        plt.show()
        #plot_layout(self.sym_layout)

    def update_trace_df(self,row_id,trace_id=None,poi_type=None,data_type=None,point=None,condition=None,node=None,i=None,j=None,side=None):
        self.normal_trace_df.loc[row_id,'ID']=trace_id
        self.normal_trace_df.loc[row_id,'POI_Type']=poi_type
        self.normal_trace_df.loc[row_id,'Data_Type']=data_type
        self.normal_trace_df.loc[row_id,'Point']=point
        self.normal_trace_df.loc[row_id,'Condition']=condition
        if poi_type==LONG_POI:
            self.normal_trace_df.loc[row_id, 'node'] = node
            self.normal_trace_df.loc[row_id, 'i'] = i
            self.normal_trace_df.loc[row_id, 'j'] = j
            self.normal_trace_df.loc[row_id, 'side'] = side
        row_id+=1
        return row_id
    def convert_POI(self,num):
        if num==1:
            return "DEVICE_POI"
        elif num ==2:
            return "BAR_LEAD_POI"
        elif num ==3:
            return "RND_LEAD_POI"
        elif num == 4:
            return "TRACE_POI"
        elif num == 5:
            return "BW_POI"
        elif num == 6:
            return "TRACE_TRACE_BW_POI"
        elif num == 7:
            return "SUPER_POI"
        elif num == 8:
            return "LONG_POI"
        elif num == 9:
            return "END_POI"

    def _build_normal_POI(self,supertrace_conn,supertrace_sum,long_conn,long_sum,lumped_graph):
        # Update normal traces data frame
        # Ids to help sort out different POI cases
        # Handle normal trace elements
        row_id = 0
        for trace_id in range(len(self.all_trace_lines)):
            trace = self.all_trace_lines[trace_id]
            ta = trace.trace_rect

            if not trace.is_supertrace():
                # Check for all children on a parent trace. This includes all LEADS and DEVICES
                for child in trace.child_pts:
                    if isinstance(child.tech, Lead):
                        if child.tech.lead_type == Lead.BUSBAR:
                            # Add busbar type leads
                            if trace.element.vertical:
                                dtype = BAR_LEAD_POI;
                                obj = child;
                                point = (ta.center_x(), child.center_position[1])
                            else:
                                dtype = BAR_LEAD_POI;
                                obj = child;
                                point = (child.center_position[0], ta.center_y())
                        elif child.tech.lead_type == Lead.ROUND:
                            # Add round type leads
                            if trace.element.vertical:
                                dtype = BAR_LEAD_POI;
                                obj = child;
                                point = (ta.center_x(), child.center_position[1])
                            else:
                                dtype = BAR_LEAD_POI;
                                obj = child;
                                point = (child.center_position[0], ta.center_y())
                    elif isinstance(child.tech, DeviceInstance):
                        # Add devices
                        dtype = DEVICE_POI;
                        obj = child;
                        point = child.center_position

                    row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype,
                                                  point=point, data_type=obj)

                # Check for all Bondwires connected to a trace
                for bw in trace.conn_bonds:
                    # Add bondwires
                    if (bw.land_pt is not None) and (bw.land_pt2 is None):
                        # bondwire connects device to trace
                        poi_type = BW_POI
                    elif (bw.land_pt is not None) and (bw.land_pt2 is not None):
                        # bondwire connects trace to trace
                        poi_type = TRACE_TRACE_BW_POI
                    '''Test for Colinear BWs, this might work for any direction wirebond too '''
                    # Problem with bw connection here This assumes bw have to be perpendicular again
                    try:
                        if trace.element.vertical:
                            # if this is vertical we have 2 options:
                            if ta.encloses(ta.center_x(), bw.land_pt[1]):
                                dtype = poi_type;
                                obj = bw;
                                point = (ta.center_x(), bw.land_pt[1])
                            elif ta.encloses(ta.center_x(), bw.land_pt2[1]):
                                dtype = poi_type;
                                obj = bw;
                                point = (ta.center_x(), bw.land_pt2[1])

                        else:
                            # if this is horizontal we have 2 options:
                            if ta.encloses(bw.land_pt[0], ta.center_y()):
                                dtype = poi_type;
                                obj = bw;
                                point = (bw.land_pt[0], ta.center_y())

                            elif ta.encloses(bw.land_pt2[0], ta.center_y()):
                                dtype = poi_type;
                                obj = bw;
                                point = (bw.land_pt2[0], ta.center_y())
                        row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype,
                                                      point=point, data_type=obj)
                    except:
                        print "wrong solution, due to packaging"
                trace_bound=[True,True] # [TOP , BOT] or [RIGHT, LEFT] THAT DOESNT HAVE TRACE CONNECTED
                # Trace to trace connection
                for conn in trace.trace_connections:
                    # Ignore connections at supertrace boundaries.
                    # These are handled by the supertrace connection system
                    # Long contacts break the space between a trace and supertrace though
                    # so these connections should be handled as a normal connection
                    bound_conn = (frozenset([conn, trace]) in self.boundary_connections)
                    if not (conn.is_supertrace()) and not (bound_conn):
                        tb = conn.trace_rect
                        side = ta.find_contact_side(tb)
                        ortho = trace.element.vertical ^ conn.element.vertical
                        dtype = TRACE_POI;
                        if trace.element.vertical:
                            # if connection is top or bottom: place point at middle of connection trace

                            if side == Rect.TOP_SIDE:
                                obj = conn;
                                point = (ta.center_x(), ta.top);
                                cond = ortho
                                trace_bound[0]=False
                            elif side == Rect.BOTTOM_SIDE:
                                obj = conn;
                                point = (ta.center_x(), ta.bottom);
                                cond = ortho
                                trace_bound[1] = False
                            # if connection is left or right: place point at left/right
                            elif side == Rect.RIGHT_SIDE or side == Rect.LEFT_SIDE:
                                obj = conn;
                                point = (ta.center_x(), tb.center_y());
                                cond = ortho
                        else:
                            # if connection is top or bottom: place point at middle of connection trace
                            if side == Rect.TOP_SIDE or side == Rect.BOTTOM_SIDE:
                                obj = conn;
                                point = (tb.center_x(), ta.center_y());
                                cond = ortho

                            # if connection is left or right: place point at left/right
                            elif side == Rect.RIGHT_SIDE:
                                obj = conn;
                                point = (ta.right, ta.center_y());
                                cond = ortho
                                trace_bound[0] = False

                            elif side == Rect.LEFT_SIDE:
                                dtype = TRACE_POI;
                                obj = conn;
                                point = (ta.left, ta.center_y());
                                cond = ortho
                                trace_bound[1] = False

                        row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype,
                                                      point=point, data_type=obj, condition=cond)


                # Adding missing boundaries points for trace - trace connect
                if trace_bound[0] or trace_bound [1]: # if there is one
                    dtype = END_POI
                    if trace.element.vertical: # TOP BOT
                        if trace_bound[0]: # IF There is a missing boundary point top
                            point = (ta.center_x(),ta.top)
                            row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype, point=point)
                        if trace_bound[1]: # IF There is a missing boundary point bottom
                            point = (ta.center_x(), ta.bottom)
                            row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype, point=point)
                    else: # RIGHT LEFT
                        if trace_bound[0]: # IF There is a missing boundary point on the right
                            point = (ta.right,ta.center_y())
                            row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype, point=point)
                        if trace_bound[1]: # IF There is a missing boundary point on the left
                            point = (ta.left, ta.center_y())
                            row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=dtype, point=point)

                # End for Conn Trace

                # Add supertrace connection points
                # Add long contact connections points
                for superconn in trace.super_connections:
                    if frozenset([superconn[0], trace]) in supertrace_conn:
                        node = supertrace_conn[frozenset([superconn[0], trace])]
                        supertrace_sum -= 1
                        pt = lumped_graph.node[node]['point']

                        row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=SUPER_POI,
                                                      point=pt, data_type=superconn[0], condition="SUPER_TRACE")
                    elif frozenset([superconn[0], trace]) in long_conn:
                        conn_list = long_conn[frozenset([superconn[0], trace])]
                        long_sum -= 1
                        for info in conn_list:
                            node, i, j, side = info
                            pt = lumped_graph.node[node]['point']
                            row_id = self.update_trace_df(row_id=row_id, trace_id=trace_id, poi_type=LONG_POI,
                                                      point=pt, data_type=superconn[0], condition="SUPER_TRACE",
                                                          node=node,i=i,j=j,side=side)
        return supertrace_sum,long_sum


    def form_graph(self,lumped_graph,mesh_nodes,supertrace_conn,supertrace_sum,long_sum,vert_count):
        ind, res, cap = [1, 1, 1]  # initialize parasitic values to build edges
        df = self.normal_trace_df
        debug = False # IF SET TO TRUE, the Developer can see the lumped graph building process
        # TAKE OUT ALL CONNECTION CASES SO WE CAN SOLVE THEM CASE BY CASE
        try:
            all_devices=df.loc[df['POI_Type']==DEVICE_POI]
            dv_all=True
        except:
            dv_all=False
            print " NO DEVICES IN THIS LAYOUT"
        try:
            all_bondwires=df.loc[df['POI_Type']==BW_POI]
            bw_all=True
        except:
            bw_all = False
            print " NO BONDWIRES IN THIS LAYOUT"
        try:
            all_leads=df[(df['POI_Type']==BAR_LEAD_POI) | (df['POI_Type']==RND_LEAD_POI)]
            lead_all = True
        except:
            lead_all=False
            print " NO LEADS IN THIS LAYOUT"
        try:
            all_trace_trace=df[df['POI_Type']==TRACE_POI]
            trace_all=True
        except:
            trace_all=False
            all_trace_trace=[]
            print " NO TRACE TO TRACE FOUND"
        try:
            all_trace_trace_bw=df[df['POI_Type']==TRACE_TRACE_BW_POI]
            bw_trace=True
        except:
            bw_trace=False
            all_trace_trace_bw=[]
            print "NO TRACE TO TRACE BW"
        try:
            all_super_poi=df[df['POI_Type']==SUPER_POI]
            super_poi_all = True
        except:
            super_poi_all = False
            print "NO SUPER TRACE"
        try:
            all_long_poi=df[df['POI_Type']==LONG_POI]
            long_poi_all = True
        except:
            long_poi_all=False
            print "NO SUPER TRACE"

        try:
            all_end_poi = df[df['POI_Type'] == END_POI]
            end_all = True
        except:
            end_all=False
            print "NO END POINTS"
        #----------------------------------------------------------------
        # Represent special connections in device
        con_ind = 1e-7
        con_res = 1e-7
        con_cap = 1e-7

        thickness, sub_thick, sub_epsil, resist, freq = self._get_trace_data()
        trace_groups={} # Group of all nodes for each trace.
        for id,row in df.iterrows():
            trace_groups[row['ID']]=[]
        # FIRST WE CONNECT ALL DEVICES TO ITS BONDWIRES
        if dv_all and bw_all:
            dx, dy = [2, 2]
            for dev_id,dev_row in all_devices.iterrows():
                dev_pt = dev_row['Point']
                dev_obj = dev_row['Data_Type']
                # Handle Super Node: # TODO: for more complex and heterogenous deivces. this need to be come a class
                if dev_obj.is_transistor():
                    attrib = {'point': dev_pt, 'type': 'deviceD', 'obj': dev_obj}
                    node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                    dev_obj.lumped_node = node
                    dev_id = node  # Drain
                    source_id = dev_id * 1000 + 1
                    gate_id = dev_id * 1000 + 2
                    drain_trace = dev_row['ID']
                    trace_groups[drain_trace].append(dev_id)
                elif dev_obj.is_diode():
                    attrib = {'point': dev_pt, 'type': 'deviceC', 'obj': dev_obj}
                    node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                    dev_obj.lumped_node = node
                    dev_id = node # Cathode
                    anode_id = dev_id*1000+1
                    cathode_trace = dev_row['ID']
                    trace_groups[cathode_trace].append(dev_id)
                # Finish node assignment for MOSFET and Diode


                for bw_id,bw_row in all_bondwires.iterrows():
                    bondwire = bw_row['Data_Type']  # get the bondwire
                    if (bondwire.device == dev_obj) and (bondwire in dev_obj.sym_bondwires):
                        trace_id = bw_row['ID']
                        parent_trace = self.all_trace_lines[trace_id]
                        trace_data = [parent_trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil]
                        wire_type = bondwire.tech.wire_type
                        bw_pt = bw_row['Point']
                        spine_attrib = {'type': 'bw_spine', 'point': bw_pt}
                        node, vert_count = self._add_node(lumped_graph, vert_count, spine_attrib)  # spine node
                        trace_groups[trace_id].append(node) # ADD SPINE NODE TO TRACE GROUP
                        land_attrib = {'type': 'bw_land', 'point': bondwire.land_pt}
                        bw_node, vert_count = self._add_node(lumped_graph, vert_count, land_attrib)  # bw landing node
                        # Add connection edge from spine to bondwire landing
                        num_wires = len(bondwire.end_pts)  # count bondwires
                        lumped_graph = self._bondwire_to_spine_eval(node, bw_node, trace_data, num_wires,
                                                                    bondwire.tech.eff_diameter(), lumped_graph)
                        ind1, res1, cap1 = self._bondwire_eval(bw_node, dev_id, trace_data, bondwire, num_wires)
                        if dev_obj.is_transistor(): # ADD 2 NODES:
                            P_pt=[dev_pt[0]+dx,dev_pt[1]+dy] # POWER POINT LOCATION (LUMPED GRAPH)
                            attrib = {'point': P_pt, 'type': 'deviceS', 'obj': dev_obj}
                            Snode, dummy = self._add_node(lumped_graph, source_id, attrib)
                            S_pt = [dev_pt[0] - dx, dev_pt[1] - dy] # SIGNAL POINT LOCATION (LUMPED GRAPH)
                            attrib = {'point': S_pt, 'type': 'deviceG', 'obj': dev_obj}
                            Gnode, dummy = self._add_node(lumped_graph, gate_id, attrib)
                        elif dev_obj.is_diode(): # ADD 1 NODE
                            P_pt=[dev_pt[0]+dx,dev_pt[1]+dy] # POWER POINT LOCATION (LUMPED GRAPH)
                            attrib = {'point': P_pt, 'type': 'deviceA', 'obj': dev_obj}
                            Anode, dummy = self._add_node(lumped_graph, anode_id, attrib)
                        if wire_type == BondWire.POWER:
                            bw_type = 'bw power'
                            # SET UP CONNECTION BASED ON USER SELECTED PATH
                            if dev_obj.is_diode():
                                if dev_obj.states[0]==1: # Condition for user select connection between Annode to Cathode
                                    lumped_graph.add_edge(dev_id, Anode,
                                                          {'ind': 1.0 / con_ind, 'res': 1.0 / con_res,
                                                           'cap': 1.0 / con_cap,
                                                           'type': 'Anode_to_Cathode',
                                                           'obj': None})  # We might need to define an object in the future
                                lumped_graph.add_edge(bw_node, Anode,
                                                      {'ind': 1.0 / ind1, 'res': 1.0 / res1, 'cap': 1.0 / cap1,
                                                       'type': bw_type, 'obj': bondwire})
                            elif dev_obj.is_transistor():
                                if dev_obj.states[0] == 1: # Condition for user select connection between Drain to Source
                                    lumped_graph.add_edge(dev_id, Snode,
                                                          {'ind': 1.0 / con_ind, 'res': 1.0 / con_res,
                                                           'cap': 1.0 / con_cap,
                                                           'type': 'Drain_to_Source',
                                                           'obj': None})  # We might need to define an object in the future
                                # ADD BW Between Source/Anode node and bondwire landing
                                lumped_graph.add_edge(bw_node, Snode,
                                                      {'ind': 1.0 / ind1, 'res': 1.0 / res1, 'cap': 1.0 / cap1,
                                                       'type': bw_type, 'obj': bondwire})
                            # Create an isolation between S and D -- always off


                        elif wire_type == BondWire.SIGNAL: # Only works for transistor

                            bw_type = 'bw signal'
                            # ADD BW Between Gate node and bondwire landing
                            lumped_graph.add_edge(bw_node, Gnode,
                                                  {'ind': 1.0 / ind1, 'res': 1.0 / res1, 'cap': 1.0 / cap1,
                                                   'type': bw_type, 'obj': bondwire})
                            # SET UP CONNECTION BASED ON USER SELECTED PATH
                            if dev_obj.is_transistor():
                                if dev_obj.states[1]==1:
                                    lumped_graph.add_edge(Gnode, Snode,
                                                          {'ind': 1.0 / con_ind, 'res': 1.0 / con_res,
                                                           'cap': 1.0 / con_cap,
                                                           'type': 'Drain_to_Source',
                                                           'obj': None})  # We might need to define an object in the future
                                elif dev_obj.states[2]==1:
                                    lumped_graph.add_edge(Gnode, dev_id,
                                                          {'ind': 1.0 / con_ind, 'res': 1.0 / con_res,
                                                           'cap': 1.0 / con_cap,
                                                           'type': 'Drain_to_Source',
                                                           'obj': None})  # We might need to define an object in the future


                        if lumped_graph != None and debug:
                            print lumped_graph.nodes()
                            print lumped_graph.edges()
                            self.sym_layout.lumped_graph = lumped_graph
                            self.plot_lumped_graph()
        # CONNECT THE LEADS to TRACES
        if lead_all:
            for lead_id,lead_row in all_leads.iterrows():
                type = lead_row['POI_Type']
                lead_obj=lead_row['Data_Type']
                point =lead_row['Point']
                trace_id = lead_row['ID']
                parent_trace = self.all_trace_lines[trace_id]

                trace_data = [parent_trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil]
                if type == BAR_LEAD_POI:
                    # Add busbar lead nodes
                    attrib = {'point': point,'type':'spine_node'}
                    node, vert_count = self._add_node(lumped_graph, vert_count, attrib)  # add spine node
                    attrib = {'type': 'lead', 'point': lead_obj.center_position, 'obj': lead_obj}
                    lead_node, vert_count = self._add_node(lumped_graph, vert_count, attrib)  # add lead node
                    # Add connection edge for trace to lead from spine
                    lumped_graph = self._lead_trace_path_eval(lead_node, node, trace_data, lead_obj, lumped_graph)
                    lead_obj.lumped_node = lead_node  # used for measurement

                elif type == RND_LEAD_POI:
                    # Add round lead nodes

                    if distance(point, lead_obj.center_position) < 0.1:
                        # if close enough, treat node as direct connection to spine
                        attrib = {'point': point, 'type': 'lead', 'obj': lead_obj}
                        node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                        lead_obj.lumped_node = node
                    else:
                        attrib = {'point': point}
                        node, vert_count = self._add_node(lumped_graph, vert_count, attrib)  # add spine node
                        attrib = {'type': 'lead', 'point': lead_obj.center_position, 'obj': lead_obj}
                        lead_node, vert_count = self._add_node(lumped_graph, vert_count, attrib)  # add lead node
                        # Add connection edge for trace to lead from spine
                        lumped_graph = self._lead_trace_path_eval(lead_node, node, trace_data, lead_obj, lumped_graph)
                        lead_obj.lumped_node = lead_node  # used for measurement
                trace_groups[trace_id].append(node)
                if lumped_graph != None and debug:
                    print "add lead"
                    print lumped_graph.nodes()
                    print lumped_graph.edges()
                    self.sym_layout.lumped_graph = lumped_graph
                    self.plot_lumped_graph()
        conn_dict = {};
        conn_sum = 0
        overlap_pts = {};
        overlap_sum = 0
        if trace_all:
            # CONNECT TRACE TO TRACE:
            for id,row_trace in all_trace_trace.iterrows():
                trace_id=row_trace['ID']
                trace=self.all_trace_lines[trace_id]
                trace_b=row_trace['Data_Type']
                ortho=row_trace['Condition']
                point = row_trace['Point']
                attrib = {'type': 'trace-to-trace', 'point': point}

                if ortho:
                    node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                    trace_groups[trace_id].append(node)
                    if frozenset([trace_b, trace]) in conn_dict:
                        conn_node = conn_dict[frozenset([trace_b, trace])]
                        lumped_graph = self._trace_conn_path_eval(conn_node, node, trace_data, trace_b,
                                                                  lumped_graph)
                        conn_sum -= 1
                    else:  # Add node to conn_dict and the connection will be found next time
                        conn_dict[frozenset([trace_b, trace])] = node
                        conn_sum += 1
                else:
                    # Check if a node has already been added
                    if frozenset([trace, trace_b]) in overlap_pts:
                        node = overlap_pts[frozenset([trace, trace_b])]
                        overlap_sum -= 1
                    else:  # If not added yet, add it
                        node, vert_count = self._add_node(lumped_graph, vert_count, attrib)

                        overlap_pts[frozenset([trace, trace_b])] = node
                        overlap_sum += 1
                    trace_groups[trace_id].append(node)
                if lumped_graph != None and debug:
                    self.sym_layout.lumped_graph = lumped_graph
                    self.plot_lumped_graph()

        wire_wire_dict = {};
        ww_sum = 0
        if bw_trace:
            # CONNECT BW FROM TRACE TO TRACE:
            for id, row_trace_bw in all_trace_trace_bw.iterrows():
                wire = row_trace_bw['Data_Type']
                wire_type=wire.tech.wire_type
                point = row_trace_bw['Point']
                trace_id=row_trace_bw['ID']

                # Determine correct landing point
                if wire.start_pt_conn is trace:
                    land_pt = wire.land_pt  # landing point 1 is on this trace
                else:
                    land_pt = wire.land_pt2  # landing point 2 is on this trace
                spine_attrib = {'type': 'bw_spine', 'point': point}
                node, vert_count = self._add_node(lumped_graph, vert_count, spine_attrib)  # spine node
                trace_groups[trace_id].append(node)
                land_attrib = {'type': 'bw_land', 'point': land_pt}
                bw_node, vert_count = self._add_node(lumped_graph, vert_count, land_attrib)  # bw landing node
                trace_groups[trace_id].append(bw_node)
                # Add connection edge from spine to bondwire landing
                num_wires = len(wire.end_pts)  # count bondwires
                lumped_graph = self._bondwire_to_spine_eval(node, bw_node, trace_data, num_wires,
                                                            wire.tech.eff_diameter(), lumped_graph)

                # Connecting to node on the other trace (use wire_wire_dict)
                # Check for trace to trace (other end of bondwire) connection node
                # eg: (node A).---wire----.(node B)
                if frozenset([wire]) in wire_wire_dict:
                    # Found the partner node
                    bw_node2 = wire_wire_dict[frozenset([wire])]
                    ind1, res1, cap1 = self._bondwire_eval(bw_node, bw_node2, trace_data, wire, num_wires)
                    if wire_type == BondWire.POWER:
                        bw_type = 'bw power'
                    elif wire_type == BondWire.SIGNAL:
                        bw_type = 'bw signal'
                    lumped_graph.add_edge(bw_node, bw_node2,
                                          {'ind': 1.0 / ind1, 'res': 1.0 / res1, 'cap': 1.0 / cap1,
                                           'type': bw_type, 'obj': wire})
                    ww_sum -= 1
                else:  # Add to connection dict
                    wire_wire_dict[frozenset([wire])] = bw_node
                    ww_sum += 1

        if super_poi_all:
            # CONNECT SUPER TRACES (SUPER POI)
            for id, row_super in all_super_poi.iterrows():
                trace_id=row_super['ID']
                trace=self.all_trace_lines[trace_id]
                super_trace=row_super['Data_Type']
                node = supertrace_conn[frozenset([super_trace, trace])]
                trace_groups[trace_id].append(node)
        if long_poi_all:
            # CONNECT SUPER TRACES (LONG POI)
            for id, row_long in all_long_poi.iterrows():
                trace_id = row_long['ID']

                trace =self.all_trace_lines[trace_id]
                ta=trace.trace_rect
                super_trace = row_long['Data_Type']
                point=row_long['Point']
                conn_node=row_long['node']
                i=row_long['i']
                j=row_long['j']
                side=row_long['side']
                # Create new spine points (and connect them)
                if trace.element.vertical:
                    new_pt = (ta.center_x(), point[1])
                else:
                    new_pt = (point[0], ta.center_y())
                attrib = {'type': 'long_conn', 'point': new_pt}
                node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                trace_groups[trace_id].append(node)
                # find width of connecting edge, find the one deep internal edge inside the supertrace
                # this will give the width of the connecting edge
                if side == Rect.TOP_SIDE:
                    a = 0;
                    b = -1
                elif side == Rect.BOTTOM_SIDE:
                    a = 0;
                    b = 1
                elif side == Rect.RIGHT_SIDE:
                    a = -1;
                    b = 0
                elif side == Rect.LEFT_SIDE:
                    a = 1;
                    b = 0
                boundary_node = mesh_nodes[i][j]
                internal_node = mesh_nodes[i + a][j + b]
                width = lumped_graph[boundary_node][internal_node]['width']
                length = distance(new_pt, point)
                
                lumped_graph.add_edge(conn_node, node,
                                      {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                       'type': 'trace', 'width': width, 'length': length})
                
                self._collect_trace_parasitic_post_eval(width, length, conn_node, node)

        if end_all:
            for id, row_end in all_end_poi.iterrows():
                pt=row_end['Point']
                trace_id=row_end['ID']
                attrib = {'type': 'end_pt', 'point': pt}
                node, vert_count = self._add_node(lumped_graph, vert_count, attrib)
                trace_groups[trace_id].append(node)

        # NOW SINCE ALL SPECIAL CASES ARE SOLVED, WE JUST NEED TO WORK ON THE TRACE NODES
        # CONNECT ALL TRACE NODES
        for trace_id in trace_groups.keys():
            trace=self.all_trace_lines[trace_id] # Loop through each trace
            trace_data=[trace, thickness, sub_thick, lumped_graph, freq, resist, sub_epsil]
            nodes=trace_groups[trace_id]
            points=[]
            for n in nodes:
                points.append(lumped_graph.node[n]['point'])
            keydict=dict(zip(nodes, points))
            nodes.sort(key=keydict.get) # sort from high to low (vertical or horizontal)
            # NOW WE WILL CONNECT FROM LOW TO HIGH
            nodes.append(None) # add a tail
            for i in range(len(nodes)):
                n1=nodes[i] # current node
                n2=nodes[i+1] # next node
                if n2 == None:
                    break
                else:
                    lumped_graph = self._spine_path_eval(n1, n2, trace_data, lumped_graph)
                if lumped_graph != None and debug:
                    self.sym_layout.lumped_graph = lumped_graph
                    self.plot_lumped_graph()

        # End For Trace

        # Make sure the dictionary connection systems are working
        msg = "Trace connection error during lumped element graph generation."
        assert conn_sum == 0, msg

        msg = "Not all overlapping nodes determined during lumped element graph generation."
        assert overlap_sum == 0, msg

        #msg = "Not all bondwire connections found during lumped element graph generation."
        #assert bw_sum == 0, msg

        msg = "Not all trace to trace bondwire connections found during lumped element graph generation."
        assert ww_sum == 0, msg

        msg = "Not all supertrace connections were linked during lumped element graph generation."
        assert supertrace_sum == 0, msg

        msg = "Not all long contact supertrace connections were linked during lumped element graph generation."
        assert long_sum == 0, msg
        self._build_lumped_edges(trace_data, lumped_graph)

        # Update self.sym_layout
        self.sym_layout.lumped_graph = lumped_graph
        self.sym_layout.all_super_traces = self.all_super_traces
        self.sym_layout.trace_info = self.trace_info
        self.sym_layout.trace_nodes = self.trace_nodes
        self.sym_layout.corner_nodes = self.corner_nodes
        self.sym_layout.corner_info = self.corner_info


    def handle_super_trace(self,lumped_graph,vert_count,supertrace_conn,supertrace_sum,long_conn,long_sum):
        # All graph value will be 1 prior to computation
        ind, res, cap = [1, 1, 1]  # initialize parasitic values to build edges
        # Handle Supertraces first
        if self.all_super_traces==[]:
            mesh_nodes=None
        for st in self.all_super_traces:
            trace = st[0]  # Only grab the vertical element (represents both h and v)
            ta = trace.trace_rect
            vPOI = []
            hPOI = []

            # 1. Connected traces are always on the boundaries of supertrace
            # 2. Long contacts get multiple connections along supertrace

            # Add default edge points (at beg and end of trace)
            vPOI.append((None, ta.bottom, -1))
            vPOI.append((None, ta.top, -1))
            hPOI.append((None, ta.left, -1))
            hPOI.append((None, ta.right, -1))

            for conn in trace.normal_connections:
                tb = conn[0].trace_rect
                side = ta.find_contact_side(tb)
                if side == Rect.TOP_SIDE or side == Rect.BOTTOM_SIDE:
                    if conn[1] == 1 or conn[1] == 2:  # Horiz. Contact
                        hPOI.append((conn[0], tb.center_x(), side))
                elif side == Rect.RIGHT_SIDE or side == Rect.LEFT_SIDE:
                    if conn[1] == 1 or conn[1] == 2:  # Vert. Contact
                        vPOI.append((conn[0], tb.center_y(), side))

            # Sort vspine and hspine
            vPOI.sort(key=lambda pt: pt[1])
            hPOI.sort(key=lambda pt: pt[1])

            # Create mesh nodes
            horiz_len = len(hPOI)
            vert_len = len(vPOI)
            mesh_nodes = []
            for i in xrange(horiz_len):
                col = []
                for j in xrange(vert_len):
                    x = hPOI[i][1]
                    y = vPOI[j][1]
                    lumped_graph.add_node(vert_count, point=(x, y), spine=True)
                    node = vert_count
                    col.append(node)
                    vert_count += 1
                    if j > 0:
                        w1 = 0.0
                        if i - 1 >= 0:
                            w1 = math.fabs(x - hPOI[i - 1][1])
                        w2 = 0.0
                        if i + 1 <= (horiz_len - 1):
                            w2 = math.fabs(hPOI[i + 1][1] - x)
                        width = 0.5 * (w1 + w2)
                        length = math.fabs(y - vPOI[j - 1][1])
                        lumped_graph.add_edge(node, col[j - 1], {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                                                 'type': 'trace', 'width': width, 'length': length})
                        self._collect_trace_parasitic_post_eval(width, length, node, col[j - 1])

                    if i > 0:
                        w1 = 0.0
                        if j - 1 >= 0:
                            w1 = math.fabs(y - vPOI[j - 1][1])
                        w2 = 0.0
                        if j + 1 <= (vert_len - 1):
                            w2 = math.fabs(vPOI[j + 1][1] - y)
                        width = 0.5 * (w1 + w2)
                        length = math.fabs(x - hPOI[i - 1][1])
                        lumped_graph.add_edge(node, mesh_nodes[i - 1][j],
                                              {'ind': 1.0 / ind, 'res': 1.0 / res, 'cap': 1.0 / cap,
                                               'type': 'trace', 'width': width, 'length': length})
                        self._collect_trace_parasitic_post_eval(width, length, node, mesh_nodes[i - 1][j])

                    # Create trace connections
                    if j == 0 and hPOI[i][2] == Rect.BOTTOM_SIDE:
                        supertrace_conn[frozenset([st, hPOI[i][0]])] = node
                        supertrace_sum += 1
                    elif j == vert_len - 1 and hPOI[i][2] == Rect.TOP_SIDE:
                        supertrace_conn[frozenset([st, hPOI[i][0]])] = node
                        supertrace_sum += 1
                    if i == 0 and vPOI[j][2] == Rect.LEFT_SIDE:
                        supertrace_conn[frozenset([st, vPOI[j][0]])] = node
                        supertrace_sum += 1
                    elif i == horiz_len - 1 and vPOI[j][2] == Rect.RIGHT_SIDE:
                        supertrace_conn[frozenset([st, vPOI[j][0]])] = node
                        supertrace_sum += 1

                    if len(trace.long_contacts) > 0:
                        for lc in trace.long_contacts:
                            side = trace.long_contacts[lc]
                            add_node = False
                            if i == 0 and side == Rect.LEFT_SIDE:
                                add_node = True
                            elif i == horiz_len - 1 and side == Rect.RIGHT_SIDE:
                                add_node = True
                            elif j == 0 and side == Rect.BOTTOM_SIDE:
                                add_node = True
                            elif j == vert_len - 1 and side == Rect.TOP_SIDE:
                                add_node = True

                            if add_node:
                                if frozenset([lc, st]) in long_conn:
                                    conn_list = long_conn[frozenset([lc, st])]
                                    conn_list.append(
                                        (node, i, j, side))  # append the mesh node indices too, need this info later on
                                else:
                                    conn_list = []
                                    conn_list.append(
                                        (node, i, j, side))  # append the mesh node indices too, need this info later on
                                    long_conn[frozenset([lc, st])] = conn_list
                                    long_sum += 1
                mesh_nodes.append(col)
        return mesh_nodes,lumped_graph,vert_count,supertrace_conn,supertrace_sum,long_conn,long_sum

    def _build_lumped_graph(self):
        # STABLE CODE -- IN CASE THERE ARE BUGS PLZ REUSE
        # To do:
        # 1. Implement bondwire to spine connection parasitic eval
        # 2. Implement long contact point to spine connection eval

        # Initialize nx.graph structure to store trace graph
        lumped_graph = nx.Graph()
        vert_count = 1 # counting ids for nodes
        supertrace_conn = {};
        supertrace_sum = 0
        long_conn = {};
        long_sum = 0
        # HANDLE SUPER TRACE FIRST
        mesh_nodes, lumped_graph, vert_count, supertrace_conn, supertrace_sum, long_conn, long_sum = self.handle_super_trace(
            lumped_graph, vert_count, supertrace_conn, supertrace_sum, long_conn, long_sum)
        # BUILD POI DATA BASE
        supertrace_sum, long_sum=self._build_normal_POI(supertrace_conn, supertrace_sum, long_conn, long_sum, lumped_graph,)
        # FORM GRAPH
        self.form_graph(lumped_graph, mesh_nodes,supertrace_conn,supertrace_sum,long_sum,vert_count)

    def export_graph_to_file(self,lumped_graph,f_edge="C:\Users\qmle\Desktop\TestPy\Electrical\Solver\MNA//edges.txt",
                             f_node="C:\Users\qmle\Desktop\TestPy\Electrical\Solver\MNA//nodes.txt"):
        file = open(f_node, 'wb')
        # Clear the data so that a raw map can be extracted
        G = copy.deepcopy(lumped_graph)
        for n in G.nodes(data=True):

            if 'obj' in G.node[n[0]].keys():
                del G.node[n[0]]['obj']
        for n in G.nodes(data=True):
            file.write(str(n))
            file.write('\n')

        for edge in G.edges(data=True):
            try:
                del G[edge[0]][edge[1]]['obj']
            except:
                x=1
        nx.write_edgelist(G, f_edge, data=True)
