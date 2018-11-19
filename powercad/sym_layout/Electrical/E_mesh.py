
from powercad.parasitics.mdl_compare import trace_ind_krige,trace_res_krige,trace_capacitance
from powercad.parasitics.mdl_compare import load_mdl
from powercad.parasitics.mutual_inductance_saved import *
from powercad.sym_layout.Electrical.E_module import *
from powercad.sym_layout.Electrical.plot3D import *
from powercad.general.data_struct.util import Rect, draw_rect_list
import math
from numba import jit


class Mesh_node:
    def __init__(self,pos,type, node_id, group_id=None):

        self.node_id =node_id
        self.group_id= group_id # Use to define if nodes  are on same trace_group
        self.type=type  # Node type
        self.b_type=[] # if type is boundary this will tell if it is N,S,E,W
        self.pos=pos # Node Position x , y ,z
        self.C = 1

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
    def __init__(self,m_type=None,nodeA=None,nodeB=None,data={},width=1, length=1,z=0,thick=0.2,ori=None ,side =None):
        self.type= m_type  # Edge type, internal, boundary or external
        # Edge parasitics (R, L for now). Handling C will be different
        self.R=1
        self.L=1
        self.len=length
        self.width=width
        self.z=z # if None this is an hier edge
        self.thick = thick
        # Evaluated width and length for edge
        self.data = data
        self.name = data['name']
        # Updated Edge Current
        self.I=0
        self.J=0
        self.E = 0

        # Edges neighbour nodes
        self.nodeA=nodeA
        self.nodeB=nodeB
        # Always == None if this is hierarchy type 1
        self.ori = ori
        self.side = side # 0:NE , 1:NW , 2:SW , 3:SE



    # Flat level

class ElectricalMesh():
    # Electrical Meshing for one selected layer
    def __init__(self,hier_E=None,freq=1000,mdl_dir="C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\Model\workspace",mdl_name='2d_high_freq.rsmdl'):
        self.hier_E=hier_E
        self.graph=nx.Graph()#nx.MultiGraph()
        self.m_graph=nx.Graph() # A graph represent Mutual
        self.node_count=1
        self.node_dict = {}
        self.c_map =cm.jet
        self.f = freq
        self.mdl = load_mdl(mdl_dir,mdl_name)
        self.all_nodes = []
        # list object used in RS model
        self.all_W=[]
        self.all_L = []
        self.all_n1 = []
        self.all_n2 = []
        self.rm_edges=[]
        self.div=2 # by default, special case for gp
    def plot_3d(self,fig,ax):
        network_plot_3D(G=self.graph,ax=ax)

    def plot_lumped_graph(self):
        pos = {}
        label={}
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            pos[n] = (node.pos[0],node.pos[1])
            label[n]=node.node_id
        nx.draw(self.graph, pos=pos, node_size=100, with_labels=False,alpha=0.5)
        nx.draw_networkx_labels(self.graph, pos,label)

    def add_node(self,node,type=None):
        self.all_nodes.append(node)
        node_name =str(node.pos[0])+'_'+str(node.pos[1])
        self.node_dict[node_name]=node # Store for quick access of node
        self.graph.add_node(self.node_count,node=node,type=type,cap=1e-16)
        self.node_count+=1

    def store_edge_info(self,n1 ,n2, edge_data):

        if edge_data.data['type']=='trace':
            data = edge_data.data
            l=data['l']
            w= data['w']

        res = 1e-5
        ind = 1e-11

        self.graph.add_edge(n1, n2, data= edge_data,ind=ind,res=res,name=edge_data.data['name'])
        # when update edge, update node in M graph as edge data to store M values later
        edge_name = edge_data.data['name']
        if 1:
            self.all_W.append(w)
            self.all_L.append(l)
            self.all_n1.append(n1)
            self.all_n2.append(n2)
            self.m_graph.add_node(edge_name) # edge name by 2 nodes

    def compute_all_cap(self, t=0.035, h=1.0):
        Cap = []
        for w, l in zip(self.all_W, self.all_L):
            C = trace_capacitance(w=w, l=l, t=t, h=h)
            Cap.append(C)
        print sum(Cap)
        return Cap

    def update_C_val(self, t=0.035, h=1.0):
        Ctot=0
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            # Find Width,Height value
            Width=0
            Height=0
            if node.W_edge!=None:
                Width += node.W_edge.len/2
            if node.E_edge != None:
                Width += node.E_edge.len/2
            if node.N_edge != None:
                Height += node.N_edge.len / 2
            if node.S_edge != None:
                Height += node.S_edge.len / 2
            self.graph.node[n]['cap'] = 5.8 / 21 * 1e-12# trace_capacitance(w=Width, l=Height, t=t, h=h, k=4.6,fringe=True) * 1e-12
            #if node.type=='internal':
            #    self.graph.node[n]['cap'] = trace_capacitance(w=Height, l=Width, t=t, h=h,k=4.6)*1e-12
            #else:
            #    self.graph.node[n]['cap'] = trace_capacitance(w=Height, l=Width, t=t, h=h, k=4.6) * 1e-12

            #print node.node_id,"w",Width,"h",Height, self.graph.node[n]['cap']
            Ctot+= self.graph.node[n]['cap']
        print Ctot ,'F'
        #raw_input()
    def update_trace_RL_val(self, p=1.68e-8,t=0.2):
        if self.f != 0: # AC mode
            all_r = trace_res_krige(self.f, self.all_W, self.all_L, t=0, p=0, mdl=self.mdl['R']).tolist()
            all_l = trace_ind_krige(1000, self.all_W, self.all_L, mdl=self.mdl['L']).tolist()
            #all_c = self.compute_all_cap()
            for i in range(len(self.all_W)):
                n1 = self.all_n1[i]
                n2 = self.all_n2[i]
                #print 'bf',self.graph[n1][n2].values()[0]
                if not ([n1,n2] in self.rm_edges):
                    self.graph[n1][n2].values()[0]['res'] = all_r[i]*1e-3
                    self.graph[n1][n2].values()[0]['ind'] = all_l[i] * 1e-9
                    #self.graph[n1][n2].values()[0]['cap'] = all_c[i] * 1e-12

                    edge_data = self.graph[n1][n2].values()[0]['data']
                    edge_data.R = all_r[i]*1e-3
                    edge_data.L = all_l[i]*1e-9
                    #edge_data.C = all_c[i]*1e-12
        else: # DC mode
            all_r = p * np.array(self.all_L) / (np.array(self.all_W) * t) * 1e-3
            for i in range(len(self.all_W)):
                n1 = self.all_n1[i]
                n2 = self.all_n2[i]
                self.graph[n1][n2].values()[0]['res'] = all_r[i]
                edge_data = self.graph[n1][n2].values()[0]['data']
                edge_data.R = all_r[i]

    def add_hier_edge(self, n1, n2,edge_data=None):
        if edge_data==None:
            res = 1e-6
            ind = 1e-12
            cap = 1 * 1e-13
        else:
            res = edge_data['R']
            ind = edge_data['L']
            cap = 1 * 1e-13

        edge_data=Mesh_edge(m_type='hier', nodeA=n1, nodeB=n2, data={'type':'hier','name':str(n1) + '_' + str(n2)})

        self.graph.add_edge(n1, n2, data=edge_data, ind=ind, res=res, cap=cap)
    def remove_edge(self,edge):
        try:
            self.rm_edges.append([edge.nodeA.node_id, edge.nodeB.node_id])
            self.graph.remove_edge(edge.nodeA.node_id,edge.nodeB.node_id)
        except:
            print "cant find edge" , edge.nodeA.node_id, edge.nodeB.node_id

    def update_mutual(self):
        u = 4 * math.pi * 1e-7
        sd_met = math.sqrt(1 / (math.pi * self.f*1000 * u * 5.96e7 * 1e6))*1000
        for e1 in self.graph.edges(data=True):
            data1= e1
            n1_1 = self.graph.node[data1[0]]['node']  # node 1 on edge 1
            n1_2 = self.graph.node[data1[1]]['node']  # node 2 on edge 1
            p1_1 = n1_1.pos
            p1_2 = n1_2.pos
            ori1 = 'h' if p1_1[1] == p1_2[1] else 'v'
            edge1 = data1[2]['data']


            if edge1.type!='hier':
                w1= edge1.data['w']
                diff1=0
                #if edge1.type=='boundary':
                #    diff1 = w1 - sd_met
                    #w1=sd_met
                l1 = edge1.data['l']
                t1 = edge1.thick
                z1 = edge1.z
                rect1 = edge1.data['rect']
                rect1_data=[w1,l1,t1,z1]
            else:
                continue

            e1_name = edge1.data['name']
            for e2 in self.graph.edges(data=True):
                if e1!=e2 and edge1.type != 'hier':
                    # First define the new edge name as a node name of Mutual graph
                    data2 = e2
                    edge2 = data2[2]['data']
                    e2_name = edge2.data['name']

                    if not(self.m_graph.has_edge(e1_name,e2_name)):
                        n2_1 = self.graph.node[data2[0]]['node']  # node 1 on edge 1
                        n2_2 = self.graph.node[data2[1]]['node']  # node 2 on edge 1
                        p2_1 = n2_1.pos
                        p2_2 = n2_2.pos
                        ori2 = 'h' if p2_1[1] == p2_2[1] else 'v'


                        if edge2.type != 'hier':
                            w2 = edge2.data['w']
                            diff2 = 0

                            #if edge2.type == 'boundary':
                            #    diff2 = w2 - sd_met

                            #    w2 = sd_met

                            l2 = edge2.data['l']
                            t2 = edge2.thick
                            z2 = edge2.z
                            rect2 = edge2.data['rect']
                            rect2_data = [w2, l2, t2, z2]
                        else:
                            continue

                        if ori1=='h' and ori2 == 'h' and not(p2_2[1]== p1_2[1]): # 2 horizontal parallel pieces
                            x1_s = [p1_1[0],p1_2[0]]  # get all x from trace 1
                            x2_s = [p2_1[0], p2_2[0]] # get all x from trace 2
                            x1_s.sort(),x2_s.sort()
                            if rect1.left>=rect2.left:
                                r2 = rect1
                                r1 = rect2
                                w1, l1, t1, z1 = rect2_data
                                w2, l2, t2, z2 = rect1_data
                            else:
                                r1 = rect1
                                r2 = rect2
                                w1, l1, t1, z1 = rect1_data
                                w2, l2, t2, z2 = rect2_data
                            p= z2-z1
                            E= r2.bottom- r1.bottom+diff1+diff2
                            l3= r2.left-r1.left
                            M12 = mutual_between_bars(w1=w1, l1=l1, t1=t1, w2=w2, l2=l2, t2=t2, l3=l3,
                                                        p=p, E=E)
                            #if M12<0:
                            #    print "case horizontal"

                        elif ori1 == 'v' and ori2 == 'v' and not (p2_2[0] == p1_2[0]):  # 2 vertical parallel pieces
                            y1_s = [p1_1[1], p1_2[1]]  # get all y from trace 1
                            y2_s = [p2_1[1], p2_2[1]]  # get all y from trace 2
                            y1_s.sort(), y2_s.sort()
                            if rect1.top <= rect2.top:
                                r2 = rect1
                                r1 = rect2
                                w1, l1, t1, z1 = rect2_data
                                w2, l2, t2, z2 = rect1_data
                            else:
                                r1 = rect1
                                r2 = rect2
                                w1, l1, t1, z1 = rect1_data
                                w2, l2, t2, z2 = rect2_data
                            p = abs(z1 - z2)
                            E = r2.left - r1.left + diff1 + diff2
                            l3 = r1.top - r2.top
                            M12 = mutual_between_bars(w1=w1, l1=l1, t1=t1, w2=w2, l2=l2, t2=t2, l3=l3,
                                                      p=p, E=E)
                            #if M12 < 0:
                            #    print "case vertical"
                        else: # non - orthogonal not supported now
                            M12=0


                        if M12>0:

                            #if ori1 =='v' and ori2 == 'v' and z1!=z2:
                            #    rects = [r1, r2]
                            #    print M12,'nH'

                            #    draw_rect_list(rects,'blue','+')

                            #if z1!=z2:
                            #    print z1, z2
                            #    print "diff", abs(z1 - z2), M12
                            #    raw_input("stop")
                            self.m_graph.add_edge(e1_name,e2_name,attr={'Mval':M12*1e-9})

                        elif M12<0:
                            print ori1,ori2
                            print "new cal"
                            print 'w1', w1, 'l1', l1, 't1', t1
                            print r1.bottom, r1.left, r1.top, r1.right
                            print 'w2', w2, 'l2', l2, 't2', t2
                            print r2.bottom,r2.left,r2.top,r2.right
                            print 'p', p, 'E', E, 'l3', l3
                            print M12,'nH'
                            rects = [r1, r2]
                            #    print M12,'nH'

                            draw_rect_list(rects,'blue','+',['r1','r2'])
                            raw_input()
                            # print "a",w1,'b',t1,'l1',l1,'E',E,'d',w2,'c',t2,'l2',l2,'p',p,'l3',l3


    def find_E(self,ax=None):
        bound_graph= nx.Graph()
        bound_nodes=[]
        min_R=1.5
        for e in self.graph.edges(data=True):
            edge = e[2]['data']
            if edge.type =='boundary':
                pos1 = edge.nodeA.pos
                pos2 = edge.nodeB.pos
                ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]],color='black',linewidth=3)
        for node in self.all_nodes:
            if node.type == 'boundary':
                bound_nodes.append(node)
                bound_graph.add_node(node.node_id,node=node,type=node.type)
        for n1 in bound_nodes:
            min_dis = min_R
            nb=[]
            for n2 in bound_nodes:
                if n1!=n2 and n1.group_id != n2.group_id:
                    dis = [(n1.pos[i]-n2.pos[i])**2 for i in range(2)]
                    dis = sum(dis)
                    if dis <= min_dis:
                        min_dis=dis
                        nb.append(n2)
            if nb!=[]:
                for n in nb:
                    name = 'dielec_'+str(n1.node_id)+'_'+str(n.node_id)
                    edge=Mesh_edge(m_type='dielec',nodeA=n1,nodeB=n,data={'type':'dielec','name':name},length=min_dis)
                    if n1.V >= n.V:
                        bound_graph.add_edge(n1.node_id,n.node_id,data=edge)
                    else:
                        bound_graph.add_edge(n.node_id, n1.node_id, data=edge)

        plot_E_map_test(G=bound_graph,ax=ax,cmap=self.c_map)

        plt.show()
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
        self.graph = nx.MultiGraph()
        self.node_count = 1
        # First search through all sheet and add their edges, nodes to the mesh
        for sh in hier_E.sheet:
            group =sh.parent.parent # Define the trace island (containing a sheet)
            if not(group in comp_nodes): # Create a list in dictionary to store all hierarchy node for each group
                comp_nodes[group]=[]

            comp = sh.data.component     # Get the component of a sheet.
            if comp != None and not (comp in comp_dict):
                #print "case 1"
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
                    if sheet_data.node.parent.parent == None: # floating net
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

        for c in comp_dict.keys(): # Once all components are built we make the edges
            for e in c.net_graph.edges(data=True):
                self.add_hier_edge(net[e[0]], net[e[1]],edge_data={'R':1.08e-3,'L':2.2e-9}) # TODO add bondwire model here


        # These are applied for each different groups on each layer.
        for g in hier_E.isl_group: # g here represents a trace island in T_Node

            # First forming all nodes and edges for a trace piece
            if hier_E.isl_group_data!={}:
                thick = hier_E.isl_group_data[g]['thick']
            else:
                thick = 0.035

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
                z = trace.data.z  # layer level for this node
                #print "Z",z
                num_x = Nx
                num_y = Ny
                # Forming corner - trace relationship
                corners += tr.get_all_corners()
                # Form relationship between corner and trace
                for c in corners:
                    if tr.encloses(c[0], c[1]):
                        if not (c in corners_trace_dict.keys()):
                            corners_trace_dict[c] = [tr]
                        else:
                            corners_trace_dict[c].append(tr)
                    corners_trace_dict[c] = list(set(corners_trace_dict[c]))
                corners = list(set(corners))
                lines += tr.get_all_lines()
                '''
                # GROUND PLANE
                if z ==0: # TEST FOR NOW , HAVE TO SPECIFY LATER
                    num_x=7#+  int(self.f/100)
                    num_y=7#+ int(self.f / 100)
                    self.div=2
                else:
                    num_x = Nx
                    num_y = Ny
                    self.div=2
                '''
                #xs = np.linspace(tr.left, tr.right, num_x)
                #ys = np.linspace(tr.bottom, tr.top, num_y)
                # TESTING

                if tr.width()>tr.height():
                    xs = np.linspace(tr.left, tr.right, num_y)
                    ys = np.linspace(tr.bottom, tr.top, num_x)
                elif tr.width() < tr.height():
                    xs = np.linspace(tr.left, tr.right, num_x)
                    ys = np.linspace(tr.bottom, tr.top, num_y)
                elif tr.width() == tr.height(): # Case corner piece
                    num_c = max([num_x,num_y])
                    xs = np.linspace(tr.left, tr.right, num_c)
                    ys = np.linspace(tr.bottom, tr.top, num_c)

                X, Y = np.meshgrid(xs, ys) # XY on each layer

                mesh = zip(X.flatten(), Y.flatten())
                for p in mesh:
                    p=list(p)
                    name = str(p[0])+str(p[1])+str(z)
                    # check dict/hash table for new point
                    if not(name in node_dict):
                        p.append(z)#+ trace.data.dz)
                        node_dict[name]=p
                        points.append(p)


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

            bound_lines=[]
            for l1 in all_lines:
                add = True
                for l2 in all_lines:
                    if l1 != l2:
                        if l1.equal(l2):
                            add=False
                if add:
                    bound_lines+=[l1]
            #for l in bound_lines:
                #print l.pt1, l.pt2
                #plt.plot([l.pt1[0], l.pt2[0]], [l.pt1[1], l.pt2[1]], color='red', linewidth=3)
            #for p in points:
            #    plt.scatter([p[0]],[p[1]])
            #plt.show()
            # Finding mesh nodes for group
            self.mesh_nodes(points=points,corners_trace_dict=corners_trace_dict,boundary_line=bound_lines,group=g)
            # Finding mesh edges for group
            self.mesh_edges(thick)

            #self.mesh_edges2(thick)
            #fig,ax = plt.subplots()
            #draw_rect_list(all_rect,ax,'blue',None)

            # Once we have all the nodes and edges for the trace group, we need to add node and approximated edges
            #print 'comp nodes',comp_nodes
            if comp_nodes!={} and g in comp_nodes: # CASE there are no components
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
                                d_sw_x=del_x
                                d_sw_y=del_y
                                SW = p
                    node_name = str(SW[0]) + '_' + str(SW[1])

                    # Compute SW data:
                    #print cp,SW
                    rat=2
                    SW = self.node_dict[node_name]
                    d_SW = np.sqrt(d_sw_x ** 2 + d_sw_y ** 2)
                    Rx = SW.E_edge.R*d_sw_x/SW.E_edge.len
                    Lx = SW.E_edge.L * d_sw_x / SW.E_edge.len
                    Ry = SW.N_edge.R * d_sw_y / SW.N_edge.len
                    Ly = SW.N_edge.L * d_sw_y / SW.N_edge.len
                    #print SW.E_edge.R, SW.E_edge.L

                    R = Rx * Ry / (Rx + Ry)
                    L = Lx * Ly / (Lx + Ly)
                    R=1e-6 if R==0 else R
                    L = 1e-10 if L == 0 else L

                    SW_data={'R':R,'L':L,'C':  1e-12}

                    # Compute NW data:
                    NW = SW.North
                    d_nw_x = abs(cp_node.pos[0] - NW.pos[0])
                    d_nw_y = abs(cp_node.pos[1] - NW.pos[1])
                    d_NW = np.sqrt(d_nw_x ** 2 + d_nw_y ** 2)

                    Rx = NW.E_edge.R * d_nw_x / NW.E_edge.len
                    Lx = NW.E_edge.L * d_nw_x / NW.E_edge.len
                    Ry = NW.S_edge.R * d_nw_y / NW.S_edge.len
                    Ly = NW.S_edge.L * d_nw_y / NW.S_edge.len

                    R=Rx*Ry/(Rx+Ry)
                    L = Lx * Ly / (Lx + Ly)
                    R = 1e-6 if R == 0 else R
                    L = 1e-10 if L == 0 else L

                    NW_data = {'R': R, 'L': L, 'C': 1e-12}

                    # Compute NE data:
                    NE = NW.East
                    d_ne_x = abs(cp_node.pos[0] - NE.pos[0])
                    d_ne_y = abs(cp_node.pos[1] - NE.pos[1])
                    d_NE = np.sqrt(d_ne_x ** 2 + d_ne_y ** 2)

                    Rx = NE.W_edge.R * d_ne_x / NE.W_edge.len
                    Lx = NE.W_edge.L * d_ne_x / NE.W_edge.len
                    Ry = NE.S_edge.R * d_ne_y / NE.S_edge.len
                    Ly = NE.S_edge.L * d_ne_y / NE.S_edge.len

                    R = Rx * Ry / (Rx + Ry)
                    L = Lx * Ly / (Lx + Ly)
                    R = 1e-6 if R == 0 else R
                    L = 1e-10 if L == 0 else L
                    NE_data = {'R': R, 'L': L, 'C': 1e-12}

                    # Compute SE data:
                    SE = NE.South
                    d_se_x = abs(cp_node.pos[0] - SE.pos[0])
                    d_se_y = abs(cp_node.pos[1] - SE.pos[1])
                    d_SE = np.sqrt(d_se_x ** 2 + d_se_y ** 2)

                    Rx = SE.W_edge.R * d_se_x / SE.W_edge.len
                    Lx = SE.W_edge.L * d_se_x / SE.W_edge.len
                    Ry = SE.N_edge.R * d_se_y / SE.N_edge.len
                    Ly = SE.N_edge.L * d_se_y / SE.N_edge.len

                    R = Rx * Ry / (Rx + Ry)
                    L = Lx * Ly / (Lx + Ly)
                    R = 1e-6 if R == 0 else R
                    L = 1e-10 if L == 0 else L
                    SE_data = {'R': R, 'L': L, 'C':  1e-12}

                    if not (cp_node.pos[0]==NE.pos[0] or cp_node.pos[1] == NW.pos[1]):
                        self.add_hier_edge(n1=cp_node.node_id, n2=SW.node_id,edge_data=SW_data)
                        self.add_hier_edge(n1=cp_node.node_id, n2=NW.node_id, edge_data=NW_data)
                        self.add_hier_edge(n1=cp_node.node_id, n2=NE.node_id, edge_data=NE_data)
                        self.add_hier_edge(n1=cp_node.node_id, n2=SE.node_id, edge_data=SE_data)
                    else:
                        if cp_node.pos[0] == NE.pos[0]:
                            self.add_hier_edge(n1=cp_node.node_id, n2=SE.node_id, edge_data=SW_data)
                            self.add_hier_edge(n1=cp_node.node_id, n2=NE.node_id, edge_data=NW_data)
                        elif cp_node.pos[1] == NW.pos[1]:
                            self.add_hier_edge(n1=cp_node.node_id, n2=NW.node_id, edge_data=NW_data)
                            self.add_hier_edge(n1=cp_node.node_id, n2=NE.node_id, edge_data=NE_data)

    def mesh_edges2(self,thick=None):
        # THIS IS NOT OPTIMIZED -- NEED A BETTER SOLUTION AFTER POETS
        # Forming Edges and Updating Edges width, length
        all_edge = []
        tot_rect=0
        conn_dict={}
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            conn_dict[node.node_id]={}
        for n in self.graph.nodes():
            all_rect = []

            node = self.graph.node[n]['node']
            # Handle vertical edges
            North = node.North
            South = node.South
            East = node.East
            West = node.West
            N_edge = []
            S_edge = []
            W_edge = []
            E_edge = []
            Dir = [North, South,East,West]
            Dir = [t !=None for t in Dir]
            Count = sum(Dir) # number of neighbours for each node
            z = node.pos[2]
            node_type = node.type
            trace_type = 'internal'
            if Count == 3: # Missing 1 neighbour, node is at 1 side of the trace
                # Will have 4 traces
                if North==None :
                    # Horizontal edges
                    ori = 'h'
                    trace_type = 'boundary'
                    side = 3
                    width = (node.pos[1] - South.pos[1])/2
                    le = abs(node.pos[0]-East.pos[0])
                    xy = (node.pos[0], (node.pos[1] + South.pos[1]) / 2)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) +'_'+str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z,ori=ori,side=side,thick=thick)
                    E_edge.append(edge_data)

                    # ---------------------------------
                    side = 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], (node.pos[1] + South.pos[1]) / 2)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + lw)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_'+str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z,ori=ori,side=side,
                                          thick=thick)
                    W_edge.append(edge_data)
                    # ---------------------------------
                    # Vertical edges
                    trace_type = 'internal'
                    ori = 'v'
                    side= 3
                    length =abs(node.pos[1]-South.pos[1])
                    we = abs(node.pos[0] - East.pos[0])/2
                    xy = (South.pos[0],South.pos[1])
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + we)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                    # ---------------------------------
                    side = 2
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = ((West.pos[0]+node.pos[0])/2, South.pos[1])
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + ww)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                elif South == None:
                    # Horizontal edges
                    ori = 'h'
                    trace_type = 'boundary'
                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=xy[1]+width, bottom=xy[1], left=xy[0], right=xy[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z,
                                          ori=ori, side=side, thick=thick)
                    E_edge.append(edge_data)
                    # ---------------------------------
                    side = 1
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1]+width, bottom=xy[1], left=xy[0], right=xy[0] + lw)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z,
                                          ori=ori, side=side, thick=thick)
                    W_edge.append(edge_data)
                    # ---------------------------------
                    # Vertical edges
                    trace_type = 'internal'

                    ori = 'v'
                    side = 0
                    length = abs(node.pos[1] - North.pos[1])
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (node.pos[0], node.pos[1])
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + we)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    # ---------------------------------
                    side = 1
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (West.pos[0]+ww, node.pos[1])
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + ww)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                elif East == None:
                    # Vertical edges
                    ori = 'v'
                    trace_type = 'boundary'
                    side = 1
                    width = abs(node.pos[0] - West.pos[0]) / 2
                    ln = abs(node.pos[1] - North.pos[1])
                    xy = (node.pos[0]-width, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ln, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=ln, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    # ---------------------------------
                    side = 2
                    ls = abs(node.pos[1] - South.pos[1])
                    xy = (node.pos[0] - width, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0]+width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ls, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=ls, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                    # ---------------------------------
                    # Horizontal edges
                    trace_type = 'internal'

                    ori = 'h'
                    side = 1
                    length = abs(node.pos[0] - West.pos[0])
                    wn = abs(node.pos[1] - North.pos[1]) / 2
                    xy = (West.pos[0], West.pos[1])
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    rect = Rect(top=xy[1]+wn, bottom=xy[1], left=xy[0], right=xy[0] + length)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': wn, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    W_edge.append(edge_data)
                    # ---------------------------------
                    side = 2
                    ws = abs(node.pos[1] - South.pos[1]) / 2
                    xy = (West.pos[0], node.pos[1]-ws)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + length)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': ws, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    W_edge.append(edge_data)
                elif West == None:
                    # Vertical edges
                    ori = 'v'
                    trace_type = 'boundary'
                    side = 0
                    width = abs(node.pos[0] - East.pos[0]) / 2
                    ln = abs(node.pos[1] - North.pos[1])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0]+width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ln, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=ln, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    # ---------------------------------
                    side = 3
                    ls = abs(node.pos[1] - South.pos[1])
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ls, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=ls, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                    # ---------------------------------
                    # Horizontal edges
                    trace_type = 'internal'

                    ori = 'h'
                    side = 0
                    length = abs(node.pos[0] - East.pos[0])
                    wn = abs(node.pos[1] - North.pos[1]) / 2
                    xy = (node.pos[0], node.pos[1])
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    rect = Rect(top=xy[1] + wn, bottom=xy[1], left=xy[0], right=xy[0] + length)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': wn, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    E_edge.append(edge_data)
                    # ---------------------------------
                    side = 3
                    ws = abs(node.pos[1] - South.pos[1]) / 2
                    xy = (node.pos[0], node.pos[1] - ws)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + length)
                    all_rect.append(rect)
                    data = {'type': 'trace', 'w': ws, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=length, z=z,
                                          ori=ori, side=side, thick=thick)
                    E_edge.append(edge_data)
            elif Count == 2:  # Missing 2 neighbours, Convex case
                if North == None and West ==None:
                    # Vertical edge
                    trace_type = 'boundary'
                    ori = 'v'
                    side = 3
                    width = abs(node.pos[0] - East.pos[0]) / 2
                    ls = abs(node.pos[1] - South.pos[1])
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ls, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=ls, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                    ori = 'h'
                    side = 0
                    width = (node.pos[1] - South.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], (node.pos[1] + South.pos[1]) / 2)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=xy[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                elif North == None and East == None:
                    # Vertical edge
                    trace_type = 'boundary'
                    ori = 'v'
                    side = 2
                    width = abs(node.pos[0] - West.pos[0]) / 2
                    ls = abs(node.pos[1] - South.pos[1])
                    xy = (South.pos[0]-width, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ls, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=ls, z=z,
                                          ori=ori, side=side, thick=thick)
                    S_edge.append(edge_data)
                    ori = 'h'
                    side = 1
                    width = (node.pos[1] - South.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], (node.pos[1] + South.pos[1]) / 2)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                elif South == None and East == None:
                    # Vertical edge
                    trace_type = 'boundary'
                    ori = 'v'
                    side = 1
                    width = abs(node.pos[0] - West.pos[0]) / 2
                    ln = abs(node.pos[1] - North.pos[1])
                    xy = (node.pos[0] - width, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ln, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=ln, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    #----------------------------------------
                    ori = 'h'
                    side = 1
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], node.pos[1] )
                    rect = Rect(top=node.pos[1]+width, bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                elif South == None and West == None:
                    # Vertical edge
                    trace_type = 'boundary'
                    ori = 'v'
                    side = 0
                    width = abs(node.pos[0] - East.pos[0]) / 2
                    ln = abs(node.pos[1] - North.pos[1])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0]+width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ln, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=ln, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    # ----------------------------------------
                    ori = 'h'
                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=node.pos[0]+le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)

            elif Count == 4: # All concave cases and internal nodes

                if North.West == West.North == None:    # 6 connections
                    trace_type = 'boundary'
                    # Vertical edge
                    ori = 'v'
                    side = 0
                    width = abs(node.pos[0] - East.pos[0]) / 2
                    ln = abs(node.pos[1] - North.pos[1])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0]+width)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': ln, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=ln, z=z,
                                          ori=ori, side=side, thick=thick)
                    N_edge.append(edge_data)
                    # ----------------------------------------
                    ori = 'h'
                    side = 2
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], node.pos[1]-width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                    trace_type = 'internal'
                    # ----------------------------------------
                    ori = 'h'
                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1]+width, bottom=xy[1], left=xy[0], right=node.pos[0]+le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                    side = 3
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1]-width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                    # ----------------------------------------
                    ori = 'v'
                    side = 3
                    length = abs(node.pos[1] - South.pos[1])
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z, ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                    side = 2
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (South.pos[0]-ww, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z, ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                elif South.West==West.South==None:      # 6 connections
                    trace_type = 'internal'
                    ori = 'v'
                    length = abs(node.pos[1] - North.pos[1])
                    side = 1
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (node.pos[0] - ww, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)
                    side = 0
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)

                    # ----------------------------------------
                    ori = 'h'
                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=node.pos[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                    side = 3
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1] - width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)

                    trace_type = 'boundary'
                    side = 3
                    length = abs(node.pos[1] - South.pos[1])
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                    side =1
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                elif North.East== East.North==None:     # 6 connections
                    trace_type='internal'
                    ori = 'v'
                    side = 3
                    length = abs(node.pos[1] - South.pos[1])
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                    side = 2
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (South.pos[0] - ww, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)


                    # ----------------------------------------
                    ori = 'h'
                    side = 1
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=West.pos[0] + lw)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                    side = 2
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1] - width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)

                    side = 1
                    length = abs(node.pos[1] - North.pos[1])
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (node.pos[0] - ww, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)
                    side = 3
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1] - width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0]+le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)

                elif South.East == East.South == None:  # 6 connections
                    # ----------------------------------------
                    ori = 'h'
                    side = 1
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=West.pos[0] + lw)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                    side = 2
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1] - width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)

                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=East.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                    #---------------------------------------
                    ori = 'v'
                    length = abs(node.pos[1] - North.pos[1])
                    side = 1
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (node.pos[0] - ww, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)
                    side = 0
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)

                    length = abs(node.pos[1] - South.pos[1])
                    side = 2
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (node.pos[0] - ww, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)

                else: # 8 connections
                    trace_type = 'internal'
                    # ----------------------------------------
                    ori = 'h'
                    side = 0
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=node.pos[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)
                    side = 3
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    le = abs(node.pos[0] - East.pos[0])
                    xy = (node.pos[0], node.pos[1] - width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + le)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(East.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': le, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=le, z=z, ori=ori,
                                          side=side, thick=thick)
                    E_edge.append(edge_data)

                    # ----------------------------------------
                    side=1
                    width = abs(node.pos[1] - North.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1])
                    rect = Rect(top=node.pos[1] + width, bottom=xy[1], left=xy[0], right=West.pos[0] + lw)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                    side = 2
                    width = abs(node.pos[1] - South.pos[1]) / 2
                    lw = abs(node.pos[0] - West.pos[0])
                    xy = (West.pos[0], West.pos[1]-width)
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(West.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': width, 'l': lw, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=lw, z=z, ori=ori,
                                          side=side, thick=thick)
                    W_edge.append(edge_data)
                    # ----------------------------------------
                    ori = 'v'
                    side = 3
                    length = abs(node.pos[1] - South.pos[1])
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (South.pos[0], South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0] + we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                    side = 2
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (South.pos[0] - ww, South.pos[1])
                    rect = Rect(top=node.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(South.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    S_edge.append(edge_data)
                    # ----------------------------------------
                    length = abs(node.pos[1] - North.pos[1])

                    side = 1
                    ww = abs(node.pos[0] - West.pos[0]) / 2
                    xy = (node.pos[0] - ww, node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0])
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': ww, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)
                    side = 0
                    we = abs(node.pos[0] - East.pos[0]) / 2
                    xy = (node.pos[0], node.pos[1])
                    rect = Rect(top=North.pos[1], bottom=xy[1], left=xy[0], right=node.pos[0]+we)
                    all_rect.append(rect)
                    name = str(node.node_id) + '_' + str(North.node_id) + '_' + str(side)
                    data = {'type': 'trace', 'w': we, 'l': length, 'name': name, 'rect': rect, 'ori': ori}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data, length=length, z=z,
                                          ori=ori,
                                          side=side, thick=thick)
                    N_edge.append(edge_data)

            conn = 0
            if North!=None:
                for e in N_edge:
                    nA = e.nodeA.node_id
                    nB = e.nodeB.node_id
                    if not(nB in conn_dict[nA]) or not(nA in conn_dict[nB]):
                        all_edge.append(e)

                conn_dict[nA][nB]=1
                conn_dict[nB][nA]=1
                conn +=1
            if South!=None:
                for e in S_edge:
                    nA = e.nodeA.node_id
                    nB = e.nodeB.node_id
                    if not (nB in conn_dict[nA]) or not (nA in conn_dict[nB]):
                        all_edge.append(e)
                conn_dict[nA][nB] = 1
                conn_dict[nB][nA] = 1
                conn += 1

            if East != None:
                for e in E_edge:
                    nA = e.nodeA.node_id
                    nB = e.nodeB.node_id
                    if not (nB in conn_dict[nA]) or not (nA in conn_dict[nB]):
                        all_edge.append(e)
                conn_dict[nA][nB] = 1
                conn_dict[nB][nA] = 1
                conn += 1

            if West!=None:
                for e in W_edge:
                    nA = e.nodeA.node_id
                    nB = e.nodeB.node_id
                    if not (nB in conn_dict[nA]) or not (nA in conn_dict[nB]):
                        all_edge.append(e)
                conn_dict[nA][nB] = 1
                conn_dict[nB][nA] = 1
                conn += 1
            #print North==None,South==None,East==None,West==None
            #print len(N_edge)
            #print len(S_edge)
            #print len(E_edge)
            #print len(W_edge)
            #print conn_dict

            #draw_rect_list(all_rect, 'blue', None)

            '''
            if len(N_edge)==0 or len(S_edge) ==0 or len(E_edge) ==0 or len(W_edge) ==0:
                draw_rect_list(all_rect,'blue',None)
            '''
        #print len(all_edge)
        for e in all_edge:
            self.store_edge_info(e.nodeA.node_id,e.nodeB.node_id,e)
    def mesh_edges(self,thick=None,cond=5.96e7):
        u = 4 * math.pi * 1e-7
        err_mag =0.9999  # Ensure no touching in inductance calculation

        #if cond!=None:
        #    sd_met = math.sqrt(1 / (math.pi * self.f * u * cond * 1e6))*1000 *10# in mm
        # Forming Edges and Updating Edges width, length
        div = 3#self.div

        for n in self.graph.nodes():

            node = self.graph.node[n]['node']
            # Handle vertical edges
            North = node.North
            South = node.South
            East = node.East
            West = node.West
            z = node.pos[2]
            node_type = node.type
            if North != None and node.N_edge==None:
                name = str(node.node_id) + '_' + str(North.node_id)
                if not self.graph.has_edge(n, North.node_id):
                    length = North.pos[1] - node.pos[1]
                    if node_type == 'internal' or North.type == 'internal':
                        width = abs(East.pos[0] - West.pos[0]) * (1 - float(1) / div) * err_mag
                        xy= ((node.pos[0] + West.pos[0])/2 , node.pos[1])
                        trace_type = 'internal'


                    elif node_type == 'boundary':
                        if East == None:
                            width = abs(node.pos[0] - West.pos[0]) / div * err_mag
                            xy = (node.pos[0] - width, node.pos[1])

                        elif West == None:
                            width = abs(East.pos[0] - node.pos[0]) / div * err_mag
                            xy = (node.pos[0], node.pos[1])

                        if North.type == 'boundary':
                            if East!=None and West!=None:
                                if North.East==None:
                                    width = abs(node.pos[0] - West.pos[0]) / div * err_mag
                                    xy = (node.pos[0] - width, node.pos[1])
                                else:
                                    width = abs(node.pos[0] - East.pos[0]) / div * err_mag
                                    xy = (node.pos[0], node.pos[1])
                        #width = sd_met
                        trace_type = 'boundary'
                    length*=err_mag
                    rect = Rect(top=xy[1]+length,bottom=xy[1],left=xy[0],right=xy[0]+width)
                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name,'rect':rect, 'ori': 'v'}

                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=North, data=data,length=length,z=z,thick=thick)
                    # Update node's neighbour edges
                    node.N_edge=edge_data
                    North.S_edge=edge_data
                    # Add edge to mesh
                    self.store_edge_info(n, North.node_id, edge_data)

            if South != None and node.S_edge==None:
                name = str(node.node_id) + '_' + str(South.node_id)
                if not self.graph.has_edge(n, South.node_id):
                    length = node.pos[1] - South.pos[1]
                    if node_type == 'internal' or South.type == 'internal':
                        width = (East.pos[0] - West.pos[0]) * (1 - float(1) / div) * err_mag
                        xy= ((node.pos[0] + West.pos[0]) / 2, South.pos[1])
                        trace_type = 'internal'

                    elif node_type == 'boundary':
                        if East == None:
                            width = abs(node.pos[0] - West.pos[0]) / div * err_mag
                            xy = (South.pos[0] - width, South.pos[1])

                        elif West == None:
                            width = abs(East.pos[0] - node.pos[0]) / div * err_mag
                            xy = (South.pos[0], South.pos[1])

                        if South.type == 'boundary':
                            if East != None and West != None:
                                if South.East==None:
                                    width = abs(node.pos[0] - West.pos[0]) / div * err_mag
                                    xy = (South.pos[0] - width, South.pos[1])
                                else:
                                    width = abs(node.pos[0] - East.pos[0]) / div * err_mag
                                    xy = (South.pos[0], South.pos[1])
                        #width = sd_met
                        trace_type = 'boundary'
                    length *= err_mag

                    rect = Rect(top=xy[1] + length, bottom=xy[1], left=xy[0], right=xy[0] + width)
                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name,'rect':rect, 'ori': 'v'}

                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=South, data=data,length = length,z=z,thick=thick)
                    # Update node's neighbour edges
                    node.S_edge = edge_data
                    South.N_edge = edge_data
                    # Add edge to mesh
                    self.store_edge_info(n, South.node_id, edge_data)
            if West != None and node.W_edge==None:
                name = str(node.node_id) + '_' + str(West.node_id)

                if not self.graph.has_edge(n, West.node_id):
                    length = node.pos[0] - West.pos[0]
                    if node_type == 'internal' or West.type == 'internal':
                        width = abs(North.pos[1] - South.pos[1]) * (1 - float(1) / div) * err_mag
                        xy= (West.pos[0], (node.pos[1] + South.pos[1]) / 2)
                        trace_type = 'internal'

                    elif node_type == 'boundary':
                        if North == None:
                            width = abs(node.pos[1] - South.pos[1]) / div * err_mag
                            xy = (West.pos[0],West.pos[1]-width)

                        elif South == None:
                            width = abs(North.pos[1] - node.pos[1]) / div * err_mag
                            xy = (West.pos[0], West.pos[1])

                        if West.type == 'boundary' :
                            if North!=None and South!=None:
                                if West.North==None:
                                    width = abs(South.pos[1] - node.pos[1]) / div * err_mag
                                    xy = (West.pos[0], West.pos[1] - width)
                                elif West.South==None:
                                    width = abs(node.pos[1] - North.pos[1]) / div * err_mag
                                    xy = (West.pos[0], West.pos[1])
                        #width = sd_met
                        trace_type = 'boundary'
                    length *= err_mag

                    rect = Rect(top=xy[1] + width, bottom=xy[1], left=xy[0], right=xy[0] + length)


                    data = {'type': 'trace', 'w': width, 'l': length, 'name': name,'rect':rect, 'ori': 'h'}

                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=West, data=data, length=length,z=z,thick=thick)
                    # Update node's neighbour edges
                    node.W_edge = edge_data
                    West.E_edge = edge_data
                    # Add edge to mesh
                    self.store_edge_info(n, West.node_id, edge_data)

            if East != None and node.E_edge==None:
                name = str(node.node_id) + '_' + str(East.node_id)

                if not self.graph.has_edge(n, East.node_id):
                    length = East.pos[0] - node.pos[0]
                    if node_type == 'internal' or East.type == 'internal':
                        width = abs(North.pos[1] - South.pos[1]) * (1 - float(1) / div) * err_mag
                        xy = (node.pos[0],(node.pos[1]+South.pos[1])/2)
                        trace_type = 'internal'

                    elif node_type == 'boundary':

                        if North == None:
                            width = abs(node.pos[1] - South.pos[1]) / div * err_mag
                            xy = (node.pos[0], node.pos[1] - width)
                            trace_type = 'boundary'


                        elif South == None:
                            width = abs(North.pos[1] - node.pos[1]) / div * err_mag
                            xy = (node.pos[0], node.pos[1])
                            trace_type = 'boundary'

                        if East.type == 'boundary':
                            if North != None and South != None:
                                if East.South == None:
                                    width = abs(North.pos[1] - node.pos[1]) / div * err_mag
                                    xy = (node.pos[0], node.pos[1])
                                elif East.North==None:
                                    width = abs(node.pos[1] - South.pos[1]) / div * err_mag
                                    xy = (node.pos[0], node.pos[1] - width)
                            #width = sd_met
                            trace_type = 'boundary'
                    length *= err_mag

                    rect = Rect(top=xy[1] + width, bottom=xy[1], left=xy[0], right=xy[0] + length)

                    data = {'type':'trace','w': width, 'l': length, 'name': name,'rect':rect,'ori':'h'}
                    edge_data = Mesh_edge(m_type=trace_type, nodeA=node, nodeB=East, data=data, length=length,z=z,thick=thick)
                    # Update node's neighbour edges
                    node.E_edge = edge_data
                    East.W_edge = edge_data
                    # Add edge to mesh
                    self.store_edge_info(n, East.node_id, edge_data)

    def mesh_nodes(self,points=[],group=None,corners_trace_dict=None,boundary_line=None):
        # Use for hierachy mode
        # Define points type, 2 types: boundary and internal
        # For each point, define the boundary type it has to that it will reduce the computation time for width and length
        #print group.name
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

        # First finding all node neighbours
        for n1 in self.graph.nodes():
            node1 = self.graph.node[n1]['node']
            type1 = node1.type
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



    def find_node(self, pt):
        min = 1000
        for n in self.graph.nodes():
            node = self.graph.node[n]['node']
            pos = node.pos
            new_dis = sqrt(abs(pt[0] - pos[0]) ** 2 + abs(pt[1] - pos[1]) ** 2)
            if new_dis < min and pos[2]==pt[2]:
                select = n
                min = new_dis
        return select
