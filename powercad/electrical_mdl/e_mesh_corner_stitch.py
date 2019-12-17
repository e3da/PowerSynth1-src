'''
author: Quang Le
Getting mesh directly from CornerStitch points and islands data
'''

from powercad.electrical_mdl.e_mesh_direct import *
from powercad.general.data_struct.util import Rect,draw_rect_list
SINGLE_TRACE = 0
L_SHAPE = 1
T_SHAPE = 2

class EMesh_CS(EMesh):
    def __init__(self, hier_E=None,islands=[], freq=1000, mdl='', layer_thickness=0.2):
        '''

        Args:
            islands: A list of CS island object where all of the mesh points/element position can be updated
            layer_thickness: a dictionary to map between layer_id in CS to its thickness in MDK
        '''
        EMesh.__init__(self,freq=freq, mdl=mdl)
        self.islands = islands
        self.layer_thickness = layer_thickness
        self.hier_E=hier_E
        self.trace_ori = {}


    def mesh_update(self, mode =0):
        '''
        Update the mesh with and without trace orientation information
        :param mode: 0 : using old method
                     1 : based on given orientations
        :return:
        '''

        self.mesh_init()

        if mode ==0:
            self.mesh_update_full()
        elif mode ==1:
            self.mesh_update_optimized()

    def mesh_init(self):
        '''
        Initialize the graph structure used for this mesh
        :return:
        '''
        self.graph = nx.MultiGraph()
        self.node_count = 1
        self.comp_dict = {}  # Use to remember the component that has its graph built (so we dont do it again)
        self.comp_nodes = {}
        self.comp_net_id = {}
        self._handle_pins_connections()

    def mesh_update_optimized(self, Nw = 3):
        '''
        If trace orientations are included, this will be used
        :param Nw: number of mesh points on the width of traces
        :return:
        '''
        print "accelerate the mesh generation"
        isl_dict = {isl.name: isl for isl in self.islands}
        for g in self.hier_E.isl_group:
            print g.name
            isl = isl_dict[g.name]
            types = self.find_connect_types(island=isl)
            print types
            trace_cells = self.handle_trace_trace_connections(island=isl,types=types)
            trace_cells = self.handle_pins_connect_trace_cells(trace_cells=trace_cells,island_name=g.name)
            nodes = self.mesh_nodes_trace_cells(trace_cells=trace_cells,Nw = 3)

            print self.trace_ori


        self.update_E_comp_parasitics(net=self.comp_net_id, comp_dict=self.comp_dict)

    def mesh_nodes_trace_cells(self,trace_cells=None,Nw=3):
        # Loop through each trace cell and form the
        print "mesh trace cells"

    def handle_pins_connect_trace_cells(self,trace_cells = None, island_name =None):
        for sh in self.hier_E.sheets:
            group = sh.parent.parent  # Define the trace island (containing a sheet)
            if island_name == group.name: # means if this sheet is in this island
                if not (group in self.comp_nodes):  # Create a list in dictionary to store all hierarchy node for each group
                    self.comp_nodes[group] = []

                comp = sh.data.component  # Get the component data from sheet.
                # print "C_DICT",len(self.comp_dict),self.comp_dict
                if comp != None and not (comp in self.comp_dict):
                    comp.build_graph()
                    sheet_data = sh.data
                    conn_type = "hier"
                    # Get x,y,z positions
                    x, y = sheet_data.rect.center()
                    z = sheet_data.z
                    cp = [x*1000, y*1000, z*1000]
                    for tc in trace_cells: # find which trace cell will have this components
                        if tc.enclose(x*1000,y*1000):
                            tc.handle_component(pt=(x*1000,y*1000))
                    if not (sheet_data.net in self.comp_net_id):
                        cp_node = MeshNode(pos=cp, type=conn_type, node_id=self.node_count, group_id=None)
                        self.comp_net_id[sheet_data.net] = self.node_count
                        self.add_node(cp_node)
                        self.comp_nodes[group].append(cp_node)
                        self.comp_dict[comp] = 1
                    for n in comp.net_graph.nodes(data=True):  # node without parents
                        sheet_data = n[1]['node']
                        if sheet_data.node == None:  # floating net
                            x, y = sheet_data.rect.center()
                            z = sheet_data.z
                            cp = [x*1000, y*1000, z*1000]
                            # print "CP",cp
                            if not (sheet_data.net in self.comp_net_id):
                                cp_node = MeshNode(pos=cp, type=conn_type, node_id=self.node_count, group_id=None)
                                # print self.node_count
                                self.comp_net_id[sheet_data.net] = self.node_count
                                self.add_node(cp_node)
                                self.comp_dict[comp] = 1

                else:
                    sheet_data = sh.data
                    type = "hier"
                    # Get x,y,z positions
                    x, y = sheet_data.rect.center()
                    z = sheet_data.z
                    cp = [x*1000, y*1000, z*1000]
                    if not (sheet_data.net in self.comp_net_id):
                        cp_node = MeshNode(pos=cp, type=type, node_id=self.node_count, group_id=None)
                        self.comp_net_id[sheet_data.net] = self.node_count
                        self.add_node(cp_node)
                        self.comp_nodes[group].append(cp_node)

        return trace_cells # trace cells with updated component information
    def find_connect_types(self,island):
        '''
        return the list of connect types from given island elements
        :param island:
        :return: list of connection types
        '''
        if len(island.element_names) == 1:
            return [SINGLE_TRACE]
        if len(island.element_names) >= 2: # T or L types
            types =[]
            for i in range(len(island.elements)-1):
                el1 = island.elements[i]
                el2 = island.elements[i+1]
                types+=[self.check_trace_to_trace_type(el1,el2)]

            return types

    def handle_trace_trace_connections(self,island,types):
        '''
        Based on the connect type, return the list of elements
        :param island: island of traces
        :param type: list of connect type
        :return: List of rect elements
        '''
        elements = island.elements
        el_names = island.element_names
        trace_cells ={} # add tcell by using its left,right,top,bottom to hash
        if len(elements) == 1:
            el = elements[0]
            l,r,b,t =self.get_elements_coord(el)
            tc= TraceCell(left=l,right=r,bottom=b,top=t)
            print self.trace_ori
            tc.type = 0 if self.trace_ori[el_names[0]] == 'H' else 1
            return [tc]
        for i in range(len(elements)-1):
            el1 = elements[i]
            el2 = elements[i+1]
            # get orientation
            o1 = self.trace_ori[el_names[i]]
            o2 = self.trace_ori[el_names[i+1]]
            l1, r1, b1, t1 = self.get_elements_coord(el1)  # get left right bottom top
            l2, r2, b2, t2 = self.get_elements_coord(el2)
            c_type = types[i]
            if c_type == T_SHAPE:
                print "handle T_SHAPE cut"
            elif c_type == L_SHAPE:
                s = 0 # check the cases if not correct then switch el1 and el2 to handle all possible case
                print "handle L_SHAPE"
                while(s == 0):
                    if r1 == l2: # el1 on the left of el2
                        s = 1
                        if o1 == 'V' and o2 == 'H': # vertical vs horizontal
                            tc2 = TraceCell(left=l2, right=r2, top=t2, bottom=b2)
                            tc2.type = 0  # horizontal
                            tc3 = TraceCell(left=l1, right=r1, top=t2, bottom=b2)
                            tc3.type = 2 # Corner
                            tc1 = TraceCell(left=l1, right=r1, top=0, bottom=0)
                            tc1.type = 1  # vertical
                            tc3.right_cell = tc2
                            if t1 == t2: # case 1 share top coordinate
                                tc1.bottom = b1
                                tc1.top = b2
                                tc3.bot_cell = tc1
                            if b1 == b2:
                                tc1.bottom = t2
                                tc1.top = t1
                                tc3.top_cell = tc1
                        if o1=='H' and o2 =='V':
                            tc1 = TraceCell(left=l1,right=r1,top =t1,bottom=b1)
                            tc1.type = 1
                            tc3 = TraceCell(left=l2,right = r2,top=t1,bottom=b1)
                            tc3.typ3 = 2
                            tc2 = TraceCell(left=l2, right=r2, bottom=0, top=0)
                            tc2.typ2 = 0
                            tc3.left_cell = tc1
                            if t1 == t2:
                                tc2.top = b1
                                tc2.bottom = b2
                                tc3.bot_cell = tc2
                            elif b1 == b2:
                                tc2.top = t2
                                tc2.bottom = t1
                                tc3.top_cell = tc2
                    elif t1 == b2: # el1 on the bottom of el2
                        s = 1
                        if o1 == 'V' and o2 == 'H':
                            tc1 = TraceCell(left=l1, right =r1, bottom= b1,top = t1)
                            tc1.type = 1
                            tc2 = TraceCell(left= 0, right = 0, bottom= b2, top =t2)
                            tc2.type = 0
                            tc3 = TraceCell(left= l1, right = r1, top = t2, bottom= b2)
                            tc3.typ3 =2
                            tc3.bot_cell = tc1
                            if l1 == l2:
                                tc3.right_cell = tc2
                                tc2.left = r1
                                tc2.right = r2
                            elif r1 == r2:
                                tc3.left_cell = tc2
                                tc2.left = l2
                                tc2.right= l1
                        if o1 == 'H' and o2 =='V':
                            tc1 = TraceCell(left =0 , right = 0, top = t1, bottom= b1)
                            tc1.type = 0
                            tc2 = TraceCell(left=l2,right =r2, top = t2, bottom=b2)
                            tc2.type = 1
                            tc3 = TraceCell(left=l1,right = r1, top = t2, bottom= b2)
                            tc3.type = 2
                            tc3.top = tc1
                            if l1 == l2:
                                tc1.left = r2
                                tc1.right = r1
                                tc3.right = tc1
                            elif r1 == r2:
                                tc1.left =l1
                                tc1.right = l2
                                tc3.left = tc1
                    else: # switch them to and run again
                        l1, r1, b1, t1 = self.get_elements_coord(el2)  # get left right bottom top
                        l2, r2, b2, t2 = self.get_elements_coord(el1)
                # ADD to hash table so we dont overlap the traces
                trace_cells[tc1.get_hash()] = tc1
                trace_cells[tc2.get_hash()] = tc2
                trace_cells[tc3.get_hash()] = tc3

        return trace_cells.values()
    def get_elements_coord(self,el):
        '''
        :return: coordinates for an element : left ,right ,bottom ,top
        '''
        return el[1], el[1] +el[3], el[2], el[2] + el[4]
    def check_trace_to_trace_type(self,el1,el2):
        '''
        :param el1:
        :param el2:
        :return:
        '''
        xs = []
        ys = []
        # First collect x , y coordinate of all rectangles
        xs += [el1[1], el1[1] + el1[3]]
        xs += [el2[1], el2[1] + el2[3]]
        ys += [el1[2], el1[2] + el1[4]]
        ys += [el2[2], el2[2] + el2[4]]
        # sort the values from small to big
        xs.sort()
        ys.sort()
        # then find the unique values
        xu = list(set(xs))
        yu = list(set(ys))
        # num edges that are shared between 2 traces
        num_shared_edge = len(xs)-len(xu) + len(ys) - len(yu)
        if num_shared_edge == 1:
            return T_SHAPE # must be T type
        else:
            return L_SHAPE

    def mesh_update_full(self):
        isl_dict = {isl.name: isl for isl in self.islands}
        for g in self.hier_E.isl_group:
            isl = isl_dict[g.name]
            points = self.mesh_nodes_full(isl=isl)
            self.hier_group_dict = {}
            self.mesh_edges(thick=0.2)  # the thickness is fixed right now but need to be updated by MDK later
            self.plot_isl_mesh(plot = True)
            self.handle_hier_node(points, g)

    def mesh_nodes_full(self,isl=None):
        '''
        Overidding the old method in EMesh, similar but in this case take nodes info directly from island info
        param: isl, the current island to form mesh
        Returns: list of mesh nodes
        '''
        add_node = self.add_node  # prevent multiple function searches

        z = 0 # set a default z for now
        xs = []  # a list  to store all x locations
        ys = []  # a list to store all y locations
        locs_to_node = {}  # for each (x,y) tuple, map them to their node id
        points = []
        mesh_nodes = isl.mesh_nodes  # get all mesh nodes object from the trace island
        # for each island set the
        #print "num nodes",len(mesh_nodes)
        for node in mesh_nodes:
            node.pos[0] = node.pos[0] / 1000.0
            node.pos[1] = node.pos[1] / 1000.0
            node.type = 'internal' if node.b_type == [] else 'boundary'  # set boundary type, b_type is set from CS
            node.node_id = self.node_count  # update node_id
            node.group_id = isl.name
            xs.append(node.pos[0])  # get x locs
            ys.append(node.pos[1])  # get y locs
            name = str(node.pos[0]) + str(node.pos[1]) + str(z)
            node.pos.append(z)
            if not (name in self.node_dict):
                p = (node.pos[0], node.pos[1], z)
                self.node_dict[name] = p
            points.append(node.pos)  # store the points location for later neighbour setup
            locs_to_node[(node.pos[0], node.pos[1])] = node  # map x y locs to node object
            add_node(node,node.type)  # add this node to graph

        # Sort xs and ys in increasing order
        xs = list(set(xs))
        ys = list(set(ys))
        xs.sort()
        ys.sort()
        self.plot_points(plot =True,points=points)
        self.set_nodes_neigbours(points=points, locs_map=locs_to_node, xs=xs, ys=ys)
        # setup hierarchical node

        return points

    def mesh_edges_optimized(self,island=None):
        '''

        :param island: trace island from cornersticth
            island.elements=[] ; all traces elements
            island.element_names= []; all traces name
            island.childe =[] ; all children objects
         :return:
        '''
        # First get all traces orientations from the island
        orient_list = [self.trace_ori[name] for name in island.element_names]
        if len(orient_list) == 1: # Case 1, if there is a single trace
            # Get all points using type 1:

            if orient_list[0] == 'H': # Handle horizontal trace
                print "horizontal connections"

                # First getting the points and form the vertical cuts for devices/bondwires/leads
            elif orient_list[0] == 'V': # Handle vertical trace
                # First getting the points and form the horizontal cuts for devices/bondwires/leads
                print "veritcal connections"


        # Then, we need to decide the orientations for the traces cross-sections



        print "handle mesh with orientation here"

    def mesh_nodes_optimized(self,island =None,type = 0, oris = []):
        '''
        Handling nodes by integers
        :param island: trace island from corner stitch
            island.mesh_nodes = [] ; initial mesh nodes from CS
        :param type : 0 --> single trace
                      1 --> L shape
                      2 --> T shape
        :param oris: list of orientations to form neighbours between nodes, 0 for horizontal and 1 for vertical
        :return:
        '''
        add_node = self.add_node  # prevent multiple function searches

        z = 0  # set a default z for now
        xs = []  # a list  to store all x locations
        ys = []  # a list to store all y locations
        locs_to_node = {}  # for each (x,y) tuple, map them to their node id
        points = []
        mesh_nodes = island.mesh_nodes  # get all mesh nodes object from the trace island
        for node in mesh_nodes:
            node.type = 'internal' if node.b_type == [] else 'boundary'  # set boundary type, b_type is set from CS
            node.node_id = self.node_count  # update node_id
            node.group_id = island.name
            xs.append(node.pos[0])  # get x locs
            ys.append(node.pos[1])  # get y locs
            name = str(node.pos[0]) + str(node.pos[1]) + str(z)
            node.pos.append(z)
            if not (name in self.node_dict):
                p = (node.pos[0], node.pos[1], z)
                self.node_dict[name] = p
            points.append(node.pos)  # store the points location for later neighbour setup
            locs_to_node[(node.pos[0], node.pos[1])] = node  # map x y locs to node object
            if type == 0: # type = 0, add node anyway
                add_node(node,node.type)  # add this node to graph

        self.find_neighbours(points=points,type = type, oris = oris)
        return points

    def find_neighbours(self,points = None,type=None,oris=None):
        '''
        This will handle the neighbours based on integers
        Find neighbours nodes based on the type of connections and orientations
        :param type : 0 --> single trace
                      1 --> L shape
                      2 --> T shape
                      3 --> Complex shape
        :param oris: list of orientations to form neighbours between nodes, 0 for horizontal and 1 for vertical
        :return: neighbours
        '''
        if type == 0:
            self.set_nodes_neigbours(points=points) # Handle like a plane






    def plot_points(self,plot = False,points = []):
        if plot:
            xs = [pt[0] for pt in points]
            ys = [pt[1] for pt in points]
            plt.scatter(xs,ys)
            plt.show()

    def plot_isl_mesh(self,plot = False):
        if plot:
            fig = plt.figure(1)
            ax = Axes3D(fig)
            ax.set_xlim3d(0, 22)
            ax.set_ylim3d(0, 42)
            ax.set_zlim3d(0, 2)
            self.plot_3d(fig=fig, ax=ax, show_labels=True, highlight_nodes=None)
            plt.show()