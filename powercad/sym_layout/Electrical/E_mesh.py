
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from powercad.design.module_design import ModuleDesign
from powercad.general.data_struct.util import Rect,Line,draw_rect_list
from powercad.Spice_handler.spice_export.lumped_2d_solve import *
import timeit
from scipy import *
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from powercad.parasitics.mdl_compare import trace_resistance,trace_inductance,trace_ind_krige,trace_res_krige
from powercad.parasitics.mdl_compare import load_mdl
from powercad.parasitics.mutual_inductance import mutual_between_bars,bar_ind
import os
from powercad.design.solution_structures import DeviceSolution, LeadSolution, BondwireSolution
from powercad.sym_layout.Electrical.E_hierarchy import *
from powercad.sym_layout.Electrical.E_plate import *
from powercad.sym_layout.Electrical.E_module import *
from powercad.sym_layout.Electrical.plot3D import network_plot_3D


class Mesh_node:
    def __init__(self,pos,type, node_id, group_id=None,):

        self.node_id =node_id
        self.group_id= group_id # Use to define if nodes  are on same trace_group
        self.type=type  # Node type
        self.b_type=[] # if type is boundary this will tell if it is N,S,E,W

        self.pos=pos # Node Position x , y ,z

        # For neighbours nodes of each point
        self.West=None
        self.East=None
        self.North=None
        self.South=None
        # For evaluation
        self.V = 0  # Updated node voltage later

        # Neighbour Edges on same layer:
        self.N_edge=None
        self.S_edge=None
        self.W_edge=None
        self.E_edge=None

class Mesh_edge:
    # The 1D element for electrical meshing
    def __init__(self,m_type=None,nodeA=None,nodeB=None,data={}, length=1):

        self.type= m_type  # Edge type, internal, boundary or external
        # Edge parasitics (R, L for now). Handling C will be different
        self.R=1
        self.L=1
        self.C=1
        self.len=length
        # Evaluated width and length for edge
        self.data = data
        self.name = data['name']
        # Updated Edge Current
        self.I=0
        self.J=0
        # Edges neighbour nodes
        self.nodeA=nodeA
        self.nodeB=nodeB


# Flat level
class ElectricalMesh():
    # Electrical Meshing for one selected layer
    def __init__(self,hier_E=None,freq=1000):
        self.hier_E=hier_E
        self.graph=nx.Graph()
        self.m_graph=nx.Graph() # A graph represent Mutual
        self.node_count=1
        self.node_dict = {}
        self.c_map =cm.jet
        self.f = freq
        self.mdl = load_mdl("C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\Model\workspace",
                                 'test2d.rsmdl')
    def plot_3d(self,fig,ax):
        network_plot_3D(self.graph,0,fig,ax)
    def plot_lumped_graph(self):
        pos = {}
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            pos[n] = (node.pos[0],node.pos[1])
            print pos[n]
        nx.draw(self.graph, pos=pos, node_size=100, with_labels=False,alpha=0.5)

    def add_node(self,node,type=None):
        node_name =str(node.pos[0])+'_'+str(node.pos[1])
        self.node_dict[node_name]=node # Store for quick access of node
        self.graph.add_node(self.node_count,node=node,type=type)
        self.node_count+=1

    def update_edges(self,n1 ,n2, edge_data):
        if edge_data.data['type']=='trace':
            data = edge_data.data
            p=1.68e-8
            l=data['l']
            t=0.2
            w= data['w']
            f=self.f
        if f!=0:
            res = trace_res_krige(f,w,l,t=0,p=0,mdl=self.mdl['R'])*1e-3
            ind = trace_ind_krige(f, w, l, mdl=self.mdl['L'])*1e-9
            cap = 1*1e-12
        else:
            res = p* l/(w*t)*1e-3
            ind = 1
            cap = 1
        edge_data.R = res
        edge_data.L = ind
        edge_data.C = cap
        self.graph.add_edge(n1, n2, attr={'trace': edge_data,'ind':ind,'res':res,'cap':cap})
        # when update edge, update node in M graph as edge data to store M values later
        edge_name = str(n1)+'_'+str(n2)
        self.m_graph.add_node(edge_name) # edge name by 2 nodes

    def add_hier_edge(self, n1, n2,edge_data=None):
        if edge_data==None:
            res = 1e-6
            ind = 1e-12
            cap = 1 * 1e-13
        else:
            res = edge_data['R']
            ind = edge_data['L']
            cap = edge_data['C']
        edge_data=Mesh_edge(m_type='hyer', nodeA=n1, nodeB=n2, data={'type':'hyer','name':str(n1) + '_' + str(n2)})
        self.graph.add_edge(n1, n2, attr={'trace': edge_data, 'ind': ind, 'res': res, 'cap': cap})

    def update_mutual(self):
        total_compute=0
        for e1 in self.graph.edges(data=True):
            data1= e1
            n1_1 = self.graph.node[data1[0]]['node']  # node 1 on edge 1
            n1_2 = self.graph.node[data1[1]]['node']  # node 2 on edge 1
            p1_1 =n1_1.pos
            p1_2 =n1_2.pos
            edge1 = data1[2]['attr']['trace']
            if edge1.type!='hyer':
                w1= edge1.data['w']
                l1 = edge1.len
                t1 = 0.2
                z1 = 0
            else:
                continue
            e1_name = str(data1[0]) + '_' + str(data1[1])
            for e2 in self.graph.edges(data=True):
                if e1!=e2 and edge1.type != 'hyer':
                    # First define the new edge name as a node name of Mutual graph
                    data2 = e2
                    e2_name = str(data2[0]) + '_' + str(data2[1])
                    if not(self.m_graph.has_edge(e1_name,e2_name)):
                        n2_1 = self.graph.node[data2[0]]['node']  # node 1 on edge 1
                        n2_2 = self.graph.node[data2[1]]['node']  # node 2 on edge 1
                        p2_1 = n2_1.pos
                        p2_2 = n2_2.pos
                        edge2 = data2[2]['attr']['trace']
                        if edge2.type != 'hyer':
                            w2 = edge2.data['w']
                            l2 = edge2.len
                            t2 = 0.2
                            z2 = 0
                        else:
                            continue
                        start=time.time()
                        sub=0

                        if edge1.type=='boundary':
                            sub+=w1
                        else:
                            sub+=w1/2

                        if edge2.type == 'boundary':
                            sub += w2
                        else:
                            sub += w2 / 2

                        if p1_1[1]==p1_2[1] and p2_1[1] == p2_2[1] and not(p2_2[1]== p1_2[1]): # 2 horizontal parallel pieces
                            dis= abs(p1_1[1]-p2_1[1]) -sub #on y direction
                            x1_s = [p1_1[0],p1_2[0]]  # get all x from trace 1
                            x2_s = [p2_1[0], p2_2[0]] # get all x from trace 2
                            x1_s.sort(),x2_s.sort()
                            l3 = abs(x1_s[0]-x2_s[0]) # longtitude distance
                            if dis > 0:
                                M12 = mutual_between_bars(w1=w1, l1=l1, t1=t1, w2=w2, l2=l2, t2=t2, l3=l3,
                                                          p=abs(z1 - z2),
                                                          d=dis)
                            total_compute+=time.time()-start
                        elif p1_1[0] == p1_2[0] and p2_1[0] == p2_2[0] and not (p2_2[0] == p1_2[0]):  # 2 vertical parallel pieces
                            dis = abs(p1_1[0] - p2_1[0]) - sub  # on x direction
                            y1_s = [p1_1[1], p1_2[1]]  # get all y from trace 1
                            y2_s = [p2_1[1], p2_2[1]]  # get all y from trace 2
                            y1_s.sort(), y2_s.sort()
                            l3 = abs(y1_s[0] - y2_s[0])  # longtitude distance
                            if dis>0:
                                M12 = mutual_between_bars(w1=w1, l1=l1, t1=t1, w2=w2, l2=l2, t2=t2, l3=l3, p=abs(z1 - z2),
                                                              d=dis)
                            total_compute += time.time() - start
                        else:
                            M12 =0

                        if M12>0:
                            #print e1_name, e2_name
                            #print M12, "in nH"
                            self.m_graph.add_edge(e1_name,e2_name,attr={'Mval':M12*1e-9})
        print "total computed time",total_compute

    def check_bound_type(self,rect,point):
        b_type =[]
        if point[0]==rect.left:
            b_type.append('W')
        if point[0] == rect.right:
            b_type.append('E')
        if point[1] == rect.top:
            b_type.append('N')
        if point[1] == rect.bottom:
            b_type.append('S')
        return b_type


    def mesh_grid_hier(self,Nx=3,Ny=3):
        # Todo: gotta make this recursive code
        hier_E=self.hier_E
        comp_dict ={} # Use to remember the component that has its graph built (so we dont do it again)
        # all comp points
        comp_nodes ={}
        net={}
        self.graph = nx.Graph()
        self.node_count = 1
        # First search through all sheet and add their edges, nodes to the mesh
        for sh in hier_E.sheet:
            group =sh.parent.parent # Define the trace island (containing a sheet)
            if not(group in comp_nodes): # Create a list in dictionary to store all hierarchy node for each group
                comp_nodes[group]=[]
            comp = sh.data.component     # Get the component of a sheet.
            if not(comp in comp_dict) and comp != None:
                comp.build_graph()
                sheet_data = sh.data
                type = "hier"
                # Get x,y,z positions
                x, y = sheet_data.rect.center()
                z = sheet_data.z
                cp = [x, y, z]
                if not (sheet_data.net in net):
                    cp_node = Mesh_node(pos=cp, type=type, node_id=self.node_count, group_id=None)
                    net[sheet_data.net] = self.node_count
                    self.add_node(cp_node)
                    comp_nodes[group].append(cp_node)
                    comp_dict[comp] = 1
                for n in comp.net_graph.nodes(data=True): # node without parents
                    sheet_data= n[1]['node']
                    type = "hier"
                    # Get x,y,z positions
                    x, y = sheet_data.rect.center()
                    z = sheet_data.z
                    cp = [x, y, z]
                    if not (sheet_data.net in net):
                        cp_node = Mesh_node(pos=cp, type=type, node_id=self.node_count, group_id=None)
                        net[sheet_data.net] = self.node_count
                        self.add_node(cp_node)
                        comp_dict[comp]=1
                for e in comp.net_graph.edges(data=True):
                    self.add_hier_edge(net[e[0]],net[e[1]])
            else:
                sheet_data = sh.data
                type = "hier"
                # Get x,y,z positions
                x, y = sheet_data.rect.center()
                z = sheet_data.z
                cp = [x, y, z]
                if not (sheet_data.net in net):
                    cp_node = Mesh_node(pos=cp, type=type, node_id=self.node_count, group_id=None)
                    net[sheet_data.net] = self.node_count

                    self.add_node(cp_node)
                    comp_nodes[group].append(cp_node)
                    comp_dict[comp] = 1

        # These are applied for each different groups on each layer.
        for g in hier_E.isl_group: # g here represents a trace island in T_Node
            # First forming all nodes and edges for a trace piece
            corners_trace_dict = {}  # Dictionary to store all corners of each rectangular piece
            lines_corners_dict = {}  # Dictionary to store all lines connected to corners
            corners = []             # All bound corners
            node_dict = {}           # Use to store hashed data positions
            lines = []               # All rect bound lines
            points=[]                # All mesh points

            for k in g.nodes: # Search for all traces in trace island
                # take the traces of this group ( by definition, each group have a different z level)
                trace=g.nodes[k]
                tr = trace.data.rect
                # mesh this trace
                z = trace.data.z +trace.data.dz # layer level for this node
                xs = np.linspace(tr.left, tr.right, Nx)
                ys = np.linspace(tr.bottom, tr.top, Ny)
                X, Y = np.meshgrid(xs, ys) # XY on each layer

                mesh = zip(X.flatten(), Y.flatten())
                for p in mesh:
                    p=list(p)
                    name = str(p[0])+str(p[1])#+str(z)
                    # check dict/hash table for new point
                    if not(name in node_dict):
                        p.append(z)
                        node_dict[name]=p
                        points.append(p)
                # Forming corner - trace relationship
                corners += tr.get_all_corners()
                corners = list(set(corners))
                lines += tr.get_all_lines()

            # Form relationship between corner and trace
            for c in corners:
                for k in g.nodes:
                    trace = g.nodes[k]
                    tr = trace.data.rect
                    if tr.encloses(c[0], c[1]):
                        if not (c in corners_trace_dict.keys()):
                            corners_trace_dict[c] = [tr]
                        else:
                            corners_trace_dict[c].append(tr)
                corners_trace_dict[c] = list(set(corners_trace_dict[c]))
            # Form relationship between lines and points, to split into boundary lines
            for l in lines:
                split = False
                for c in corners:
                    if l.include(c) and c != l.pt1 and c != l.pt2:
                        if not (l in lines_corners_dict.keys()):
                            lines_corners_dict[l] = [c]
                            split = True
                        else:
                            lines_corners_dict[l].append(c)
                if not split:
                    lines_corners_dict[l] = []
            all_lines = []
            # Create a list of boundary lines
            for l in lines_corners_dict.keys():
                cpoints = lines_corners_dict[l]
                if cpoints != []:
                    new_line = l.split(cpoints)
                    all_lines += new_line
                else:
                    all_lines.append(l)
                    # remove intersecting lines
            for l1 in all_lines:
                for l2 in all_lines:
                    if l1 != l2:
                        if l1.equal(l2):
                            all_lines.remove(l1)
                            all_lines.remove(l2)

            # Finding mesh nodes for group
            self.mesh_nodes(points=points,corners_trace_dict=corners_trace_dict,boundary_line=all_lines,group=g)
            # Finding mesh edges for group
            self.mesh_edges()

            # Once we have all the nodes and edges for the trace group, we need to add node and approximated edges
            for cp_node in comp_nodes[g]:
                min_dis = 1000
                SW = None
                cp = cp_node.pos
                # Finding the point on South West corner
                for p in points:  # all point in group
                    del_x = cp[0] - p[0]
                    del_y = cp[1] - p[1]
                    distance = math.sqrt(del_x ** 2 + del_y ** 2)
                    if del_x > 0 and del_y > 0:
                        if distance < min_dis:
                            min_dis = distance
                            SW = p
                node_name = str(SW[0]) + '_' + str(SW[1])

                # Compute SW data:
                SW = self.node_dict[node_name]
                d_sw_x = del_x
                d_sw_y = del_y
                Rx = SW.E_edge.R*d_sw_x/SW.E_edge.len
                Lx = SW.E_edge.L * d_sw_x / SW.E_edge.len
                Ry = SW.N_edge.R * d_sw_y / SW.N_edge.len
                Ly = SW.N_edge.L * d_sw_y / SW.N_edge.len
                R = np.sqrt(Rx ** 2 + Ry ** 2)
                L = np.sqrt(Lx ** 2 + Ly ** 2)
                SW_data={'R':R,'L':L,'C':  1e-12}

                # Compute NW data:
                NW = SW.North
                d_nw_x = abs(cp_node.pos[0] - NW.pos[0])
                d_nw_y = abs(cp_node.pos[1] - NW.pos[1])
                Rx = NW.E_edge.R * d_nw_x / NW.E_edge.len
                Lx = NW.E_edge.L * d_nw_x / NW.E_edge.len
                Ry = NW.S_edge.R * d_nw_y / NW.S_edge.len
                Ly = NW.S_edge.L * d_nw_y / NW.S_edge.len
                R = np.sqrt(Rx ** 2 + Ry ** 2)
                L = np.sqrt(Lx ** 2 + Ly ** 2)
                NW_data = {'R': R, 'L': L, 'C': 1e-12}

                # Compute NE data:
                NE = NW.East
                d_ne_x = abs(cp_node.pos[0] - NE.pos[0])
                d_ne_y = abs(cp_node.pos[1] - NE.pos[1])
                Rx = NE.W_edge.R * d_ne_x / NE.W_edge.len
                Lx = NE.W_edge.L * d_ne_x / NE.W_edge.len
                Ry = NE.S_edge.R * d_ne_y / NE.S_edge.len
                Ly = NE.S_edge.L * d_ne_y / NE.S_edge.len
                R = np.sqrt(Rx ** 2 + Ry ** 2)
                L = np.sqrt(Lx ** 2 + Ly ** 2)
                NE_data = {'R': R, 'L': L, 'C': 1e-12}

                # Compute SE data:
                SE = NE.South
                d_se_x = abs(cp_node.pos[0] - SE.pos[0])
                d_se_y = abs(cp_node.pos[1] - SE.pos[1])
                Rx = SE.W_edge.R * d_se_x / SE.W_edge.len
                Lx = SE.W_edge.L * d_se_x / SE.W_edge.len
                Ry = SE.N_edge.R * d_se_y / SE.N_edge.len
                Ly = SE.N_edge.L * d_se_y / SE.N_edge.len
                R = np.sqrt(Rx ** 2 + Ry ** 2)
                L = np.sqrt(Lx ** 2 + Ly ** 2)
                SE_data = {'R': R, 'L': L, 'C':  1e-12}

                self.add_hier_edge(n1=cp_node.node_id, n2=SW.node_id,edge_data=SW_data)
                self.add_hier_edge(n1=cp_node.node_id, n2=NW.node_id, edge_data=NW_data)
                self.add_hier_edge(n1=cp_node.node_id, n2=NE.node_id, edge_data=NE_data)
                self.add_hier_edge(n1=cp_node.node_id, n2=SE.node_id, edge_data=SE_data)



    def mesh_edges(self):
        # Forming edges and define node neighbour
        # First finding all node neighbours
        for n1 in self.graph.nodes():
            node1 = self.graph.node[n1]['node']
            type1= node1.type
            min_N = 1e3
            min_S = 1e3
            min_W = 1e3
            min_E = 1e3
            North = None;
            South = None;
            West = None;
            East = None
            for n2 in self.graph.nodes():
                node2 = self.graph.node[n2]['node']
                type2 = node2.type
                if n1 != n2 and (type1 != 'hier' and type2 != 'hier'):
                    node2 = self.graph.node[n2]['node']
                    if node1.group_id == node2.group_id:  # Same trace group
                        delta_x = node2.pos[0] - node1.pos[0]
                        delta_y = node2.pos[1] - node1.pos[1]
                        if node1.pos[1] == node2.pos[1]:  # Same Y checking for East and West neighbour
                            if delta_x > 0 and node1.East == None:  # on East side
                                if abs(delta_x) <= min_E:
                                    min_E = abs(delta_x)
                                    East = node2
                            elif delta_x < 0 and node1.West == None:  # on West side
                                if abs(delta_x) <= min_W:
                                    min_W = abs(delta_x)
                                    West = node2

                        if node1.pos[0] == node2.pos[0]:  # Same X checking for North and South neighbour
                            if delta_y > 0:  # on North side
                                if abs(delta_y) <= min_N and node1.North == None:
                                    min_N = abs(delta_y)
                                    North = node2

                            elif delta_y < 0:  # on South side
                                if abs(delta_y) <= min_S and node1.South == None:
                                    min_S = abs(delta_y)
                                    South = node2
            if node1.type == 'boundary':
                if 'E' in node1.b_type:
                    East = None
                if 'W' in node1.b_type:
                    West = None
                if 'N' in node1.b_type:
                    North = None
                if 'S' in node1.b_type:
                    South = None
            # Update neighbours

            if node1.North == None:
                node1.North = North
            if North != None:
                North.South = node1
            if node1.South == None:
                node1.South = South
            if South != None:
                South.North = node1
            if node1.East == None:
                node1.East = East
            if East != None:
                East.West = node1
            if node1.West == None:
                node1.West = West
            if West != None:
                West.East = node1

        # Forming Edges and Updating Edges width, length
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            # Handle vertical edges
            North = node.North
            South = node.South
            East = node.East
            West = node.West
            node_type = node.type
            trace_type = 'internal'
            if North != None:
                name = str(node.node_id) + '_' + str(North.node_id)
                if not self.graph.has_edge(n, North.node_id):
                    length = North.pos[1] - node.pos[1]
                    if node_type == 'internal' or North.type == 'internal':
                        width = (East.pos[0] - West.pos[0]) / 2
                        # width = (East.pos[0] - West.pos[0]) -2*sd

                    elif node_type == 'boundary':
                        if East == None:
                            width = (node.pos[0] - West.pos[0]) / 2
                            # width = sd

                        elif West == None:
                            width = (East.pos[0] - node.pos[0]) / 2
                            # width = sd

                    if North.type == 'boundary' and node_type == 'boundary':
                        trace_type = 'boundary'
                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name}


                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data,length=length)
                    # Update node's neighbour edges
                    node.N_edge=edge_data
                    North.S_edge=edge_data
                    # Add edge to mesh
                    self.update_edges(n, North.node_id, edge_data)

            if South != None:
                name = str(node.node_id) + '_' + str(South.node_id)
                if not self.graph.has_edge(n, South.node_id):
                    length = node.pos[1] - South.pos[1]
                    if node_type == 'internal' or South.type == 'internal':
                        width = (East.pos[0] - West.pos[0]) / 3
                        # width = (East.pos[0] - West.pos[0]) -2*sd

                    elif node_type == 'boundary':
                        if East == None:
                            width = (node.pos[0] - West.pos[0]) / 2
                            # width = sd

                        elif West == None:
                            width = (East.pos[0] - node.pos[0]) / 2
                            # width = sd

                    if South.type == 'boundary' and node_type == 'boundary':
                        trace_type = 'boundary'
                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name}

                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data,length = length)
                    # Update node's neighbour edges
                    node.S_edge = edge_data
                    South.N_edge = edge_data
                    # Add edge to mesh
                    self.update_edges(n, South.node_id, edge_data)
            if West != None:
                name = str(node.node_id) + '_' + str(West.node_id)

                if not self.graph.has_edge(n, West.node_id):
                    length = node.pos[0] - West.pos[0]
                    if node_type == 'internal' or West.type == 'internal':
                        width = (North.pos[1] - South.pos[1]) / 3
                        # width = (North.pos[1] - South.pos[1]) - 2*sd

                    elif node_type == 'boundary':
                        if North == None:
                            width = (node.pos[1] - South.pos[1]) / 2
                            # width = sd

                        elif South == None:
                            width = (North.pos[1] - node.pos[1]) / 2
                            # width = sd

                    if West.type == 'boundary' and node_type == 'boundary':
                        trace_type = 'boundary'
                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name}

                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=length)
                    # Update node's neighbour edges
                    node.W_edge = edge_data
                    West.E_edge = edge_data
                    # Add edge to mesh
                    self.update_edges(n, West.node_id, edge_data)

            if East != None:
                name = str(node.node_id) + '_' + str(East.node_id)

                if not self.graph.has_edge(n, East.node_id):
                    length = East.pos[0] - node.pos[0]
                    if node_type == 'internal' or East.type == 'internal':
                        width = (North.pos[1] - South.pos[1]) / 3
                        # width = (North.pos[1] - South.pos[1]) - 2*sd

                    elif node_type == 'boundary':
                        if North == None:
                            width = (node.pos[1] - South.pos[1]) / 2
                            # width = sd

                        elif South == None:
                            width = (North.pos[1] - node.pos[1]) / 2
                            # width = sd

                    if East.type == 'boundary' and node_type == 'boundary':
                        trace_type = 'boundary'
                    data = {'type':'trace','w': width, 'l': length, 'name': name}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=length)
                    # Update node's neighbour edges
                    node.E_edge = edge_data
                    East.W_edge = edge_data
                    # Add edge to mesh
                    self.update_edges(n, East.node_id, edge_data)

    def mesh_nodes(self,points=[],group=None,corners_trace_dict=None,boundary_line=None):
        # Use for hierachy mode
        # Define points type, 2 types: boundary and internal
        # For each point, define the boundary type it has to that it will reduce the computation time for width and length

        # Find all internal and boundary points
        for p in points:
            # First take into account special cases
            if p in corners_trace_dict.keys():
                if len(corners_trace_dict[p]) == 1:  # Speical point
                    type = "boundary"
                    r = corners_trace_dict[p][0]
                    b_type = self.check_bound_type(r, p)
                    new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                    new_node.b_type = b_type

                    self.add_node(new_node)
                    continue

                elif len(corners_trace_dict[p]) == 2:  # Special point 2
                    type = "boundary"
                    ref_rect = corners_trace_dict[p][0]  # take first rectangle as reference
                    l_count = 0
                    left = ref_rect.left
                    r_count = 0
                    right = ref_rect.right
                    t_count = 0
                    top = ref_rect.top
                    b_count = 0
                    bottom = ref_rect.bottom
                    for rect in corners_trace_dict[p]:
                        if rect.left == left: l_count += 1
                        if rect.right == right: r_count += 1
                        if rect.top == top: t_count += 1
                        if rect.bottom == bottom: b_count += 1
                    if l_count == 2:
                        b_type = ['W']
                    elif r_count == 2:
                        b_type = ['E']
                    elif t_count == 2:
                        b_type = ['N']
                    elif b_count == 2:
                        b_type = ['S']
                    else:
                        b_type = []

                    new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                    new_node.b_type = b_type
                    self.add_node(new_node)
                    continue
                elif len(corners_trace_dict[p]) == 3:
                    type = "boundary"
                    b_type = []
                    new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                    new_node.b_type = b_type
                    self.add_node(new_node)
                    continue
                elif len(corners_trace_dict[p]) == 4:  # a point surrounded by 4 rect is an internal point
                    type = "internal"
                    new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                    self.add_node(new_node)
                    continue
            type = "internal"
            for l in boundary_line:
                if l.include(p):
                    type = 'boundary'
            for k in group.nodes:
                trace = group.nodes[k]
                tr = trace.data.rect
                # For now care about the conductor, #TODO: take care of insulator later
                if tr.encloses(p[0], p[1]):
                    if type == 'boundary':
                        b_type = self.check_bound_type(tr, p)
                        new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                        new_node.b_type = b_type
                        self.add_node(new_node)
                        break
                    elif type == 'internal':
                        new_node = Mesh_node(p, type, node_id=self.node_count, group_id=group.name)
                        self.add_node(new_node)
                        break
            continue



    def plot_v_map(self, norm,fig,ax):
        # plot voltage level map after being solved
        sm = plt.cm.ScalarMappable(cmap=self.c_map, norm=norm)
        sm._A = []
        cbar = plt.colorbar(sm)
        cbar.set_label('Voltage Distribution(V)', fontsize=12)
        color_dict={}
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            pos = node.pos
            name = str(pos[0])+str(pos[1])+str(pos[2])
            color = self.c_map(norm(node.V))
            color_dict[name]=color
        network_plot_3D(self.graph,0,fig,ax,cmap_node=color_dict)
    def plot_J_map(self, norm, pos):
        sm = plt.cm.ScalarMappable(cmap=self.c_map, norm=norm)
        sm._A = []
        cbar = plt.colorbar(sm,
                            ticks=[0, 2.567e4, 5.135e4, 7.702e4, 1.027e5, 1.283e5, 1.541e5, 1.797e5, 2.054e5, 2.310e5,
                                   2.567e5])
        cbar.set_label('Current Density (A/m^2)', fontsize=12)
        e_color = []
        for e in self.graph.edges(data=True):
            edge = e[2]['trace']
            e_color.append(self.c_map(norm(edge.J)))
        nx.draw_networkx_edges(self.graph, pos,
                               edgelist=self.graph.edges(),
                               width=5, alpha=1, edge_color=e_color)

    def plot_I_map(self, norm, fig, ax):
        sm = plt.cm.ScalarMappable(cmap=self.c_map, norm=norm)
        sm._A = []
        cbar = plt.colorbar(sm)
        cbar.set_label('Current (A)', fontsize=12)
        e_color = []
        color_dict = {}
        for e in self.graph.edges(data=True):
            name =str(e[0])+str(e[1])
            edge = e[2]['attr']['trace']
            color=self.c_map(norm(edge.I))
            color_dict[name]=color
        network_plot_3D(self.graph, 0, fig, ax, cmap_edge=color_dict)

    def find_node(self, pt):
        min = 1000
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            pos = node.pos
            new_dis = sqrt(abs(pt[0] - pos[0]) ** 2 + abs(pt[1] - pos[1]) ** 2)
            if new_dis < min:
                select = n
                min = new_dis
        return select

def test_hier2():
    r1 = Rect(14, 10, 0, 10)
    R1 = E_plate(rect=r1, n=(0, 0, 1), z=0, dz=0.2)
    r2 = Rect(10, 0, 0, 5)
    R2 = E_plate(rect=r2, z=0, dz=0.2)
    r3 = Rect(14, 0, 10, 14)
    R3 = E_plate(rect=r3, z=0, dz=0.2)
    r4 = Rect(-1, -6, -5, 20)
    R4 = E_plate(rect=r4, z=0, dz=0.2)
    r5 = Rect(9, 0, 7, 8)
    R5 = E_plate(rect=r5, z=0, dz=0.2)
    r6 = Rect(10, -1, -5, -1)
    R6 = E_plate(rect=r6, z=0, dz=0.2)
    r7 = Rect(10, -1, 15, 20)
    R7 = E_plate(rect=r7, z=0, dz=0.2)

    sh1 = Rect(7, 5, 11, 13)
    S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 12, 13)
    S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 11.25, 11.75)
    S3 = Sheet(rect=sh3, net='M1_G', type='point', n=(0, 0, 1), z=0.4)
    sh1 = Rect(7, 5, 1, 3)
    S4 = Sheet(rect=sh1, net='M2_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 1, 2)
    S5 = Sheet(rect=sh2, net='M2_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 2.25, 2.75)
    S6 = Sheet(rect=sh3, net='M2_G', type='point', n=(0, 0, 1), z=0.4)
    sh7 = Rect(14, 12, 4, 11)
    S7 = Sheet(rect=sh7, net='DC_plus', type='point', n=(0, 0, 1), z=0.2)
    sh8 = Rect(-4, -6, 4, 11)
    S8 = Sheet(rect=sh8, net='DC_minus', type='point', n=(0, 0, 1), z=0.2)

    sh9 = Rect(2, 1, 7.25, 7.75)
    S9 = Sheet(rect=sh9, net='Gate', type='point', n=(0, 0, 1), z=0.2)

    sh10 = Rect(6, 5, 7.25, 7.35)
    S10 = Sheet(rect=sh10, net='bwG_m2', type='point', n=(0, 0, 1), z=0.2)

    sh11 = Rect(6, 5, 7.65, 7.75)
    S11 = Sheet(rect=sh11, net='bwG_m1', type='point', n=(0, 0, 1), z=0.2)

    sh12 = Rect(6, 5, 15.25, 15.35)
    S12 = Sheet(rect=sh12, net='bwS_m1', type='point', n=(0, 0, 1), z=0.2)

    sh13 = Rect(6, 5, -1.35, -1.25)
    S13 = Sheet(rect=sh13, net='bwS_m2', type='point', n=(0, 0, 1), z=0.2)

    Mos1 = Component(sheet=[S1, S2, S3],conn=[['M1_D','M1_S']],val=[-1])
    Mos2 = Component(sheet=[S4, S5, S6],conn=[['M2_D','M2_S']],val=[-1])
    Bw_S1 = Component(sheet=[S2,S12],conn=[['bwS_m1','M1_S']],val=[-1])
    Bw_S2 = Component(sheet=[S5, S13], conn=[['bwS_m2', 'M2_S']], val=[-1])
    Bw_G1 = Component(sheet=[S3, S11], conn=[['bwG_m1', 'M1_G']], val=[-1])
    Bw_G2 = Component(sheet=[S6, S10], conn=[['bwG_m2', 'M2_G']], val=[-1])

    new_module = E_module(plate=[R1, R2, R3, R4, R5, R6, R7],
                          sheet=[S7, S8, S9],components=[Mos1,Mos2,Bw_S1,Bw_S2,Bw_G1,Bw_G2])

    new_module.form_group()
    new_module.split_layer_group()
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(-5, 20)
    ax.set_ylim3d(-5, 20)
    ax.set_zlim3d(0, 5)
    plot_rect3D(rect2ds=new_module.plate + new_module.sheet, ax=ax)
    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    fig = plt.figure(2)
    ax = a3d.Axes3D(fig)
    emesh=ElectricalMesh(hier_E=hier)
    emesh.mesh_grid_hier()
    ax.set_xlim3d(0, 15)
    ax.set_ylim3d(0, 15)
    ax.set_zlim3d(0, 15)
    emesh.plot_3d(fig=fig,ax=ax)
    emesh.update_mutual()

    # EVALUATION
    circuit = Circuit()
    pt1 = (7, -4)
    pt2 = (7, 14)
    src1 = emesh.find_node(pt1)
    sink1 = emesh.find_node(pt2)
    circuit.comp_mode = 'val'
    circuit._graph_read(emesh.graph)
    circuit.m_graph_read(emesh.m_graph)
    circuit.assign_freq(100000)
    circuit._assign_vsource(src1, vname='Vs1', volt=1)
    circuit._add_ports(sink1)
    circuit.build_current_info()
    circuit.solve_iv()
    result = circuit.results
    print result
    all_V = []
    all_I = []

    pos={}
    for n in emesh.graph.nodes():
        node = emesh.graph.node[n]['node']
        pos[n] = node.pos
        net = circuit.node_dict[node.node_id]
        V_name = 'v' + str(net)
        node.V = np.abs(result[V_name])
        all_V.append(node.V)
    v_min = min(all_V)
    v_max = max(all_V)
    normV = Normalize(v_min, v_max)
    fig = plt.figure(3)
    ax = a3d.Axes3D(fig)
    emesh.plot_v_map(norm=normV,fig=fig,ax=ax)

    for e in emesh.graph.edges(data=True):
        edge = e[2]['attr']['trace']
        edge_name = edge.name
        I_name = 'I_L' + edge_name
        edge.I = np.abs(result[I_name])
        all_I.append(edge.I)
    I_min = min(all_I)
    I_max = max(all_I)
    normI = Normalize(I_min, I_max)
    fig = plt.figure(4)
    ax = a3d.Axes3D(fig)
    emesh.plot_I_map(normI,fig,ax)
    plt.show()
def test_hierarchy():
    md = ModuleDesign()
    md.traces = [ Rect(5,0,0,7), Rect(15, 6, 0, 8), Rect(6, 0, 12, 20), Rect(20, 16, 0, 20),
                 Rect(16, 7, 13, 20), Rect(15, 0, 8, 12)]  # U shape

    lead1 = LeadSolution((3.5, 17.5),None,None)
    lead2 = LeadSolution((18, 2.5), None, None)
    md.leads=[lead1,lead2]
    BW2 = BondwireSolution(positions=[(11, 11), (14, 11)])
    BW1 = BondwireSolution(positions=[(11, 12), (14, 12)])

    md.bondwires=[BW1,BW2]

    H1 = Hier_E(module=md)
    H1.form_hierachy()
    H1.tree.print_tree()

    emesh = ElectricalMesh(module=md)
    emesh.mesh_grid_hier(hier_E=H1,Nx=3,Ny=3)
    emesh.update_mutual()
    circuit = Circuit()
    pt1 = (3.6, 17.7)
    pt2 = (18, 2.5)
    src1 = emesh.find_node(pt1)
    sink1=emesh.find_node(pt2)
    circuit.comp_mode = 'val'
    circuit._graph_read(emesh.graph)
    circuit.m_graph_read(emesh.m_graph)
    # print "Read time = ", time.time()-s
    circuit.assign_freq(100000)
    circuit._assign_vsource(src1, vname='Vs1', volt=1)
    circuit._add_ports(sink1)
    circuit.build_current_info()
    circuit.solve_iv()
    result = circuit.results
    print result
    all_V = []
    all_I = []
    pos = {}
    for e in emesh.graph.edges(data=True):
        edge = e[2]['trace']
        edge_name = edge.name
        I_name = 'I_L' + edge_name
        edge.I = np.abs(result[I_name])
        all_I.append(edge.I)
    for n in emesh.graph.nodes():
        node = emesh.graph.node[n]['node']
        pos[n]=node.pos
        net = circuit.node_dict[node.node_id]
        V_name = 'v' + str(net)
        node.V = np.abs(result[V_name])
        all_V.append(node.V)
    v_min = min(all_V)
    v_max = max(all_V)
    I_min = min(all_I)
    I_max = max(all_I)
    normI = Normalize(I_min, I_max)
    normV = Normalize(v_min, v_max)
    emesh.plot_v_map(norm=normV, pos=pos)
    plt.show()
    emesh.plot_I_map(normI,pos)
    plt.show()


if __name__ == '__main__':
    test_hier2()
