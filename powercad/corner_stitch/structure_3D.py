'''
Data structure for holding the complete 3D layout information
Author @ ialrazi
March 31, 2020
'''

from powercad.corner_stitch.CornerStitch import Node

class Structure_3D():
    def __init__(self):
        self.layers=[] # list of layer objects in the structure
        self.Htree=[] # list of horizontal cs tree from each layer
        self.Vtree=[] # list of vertical cs tree from each layer
        self.solutions=None
        self.floorplan_size=[] # floorplan size of the overall structure
        self.via_connected_layers={} # a dictionary to hold information of via and corresponding connected layers: {'via_id':[list of layer ids]}
        self.root_node_h=None
        self.root_node_v = None
        self.root_node_h_edges=[] # hcg edges for root node
        self.root_node_v_edges=[] # vcg edges for root node
        self.root_node_ZDL_H=[]
        self.root_node_ZDL_V=[]
        self.root_node_removed_h={}
        self.root_node_removed_v={}
        self.reference_node_removed_h={}
        self.reference_node_removed_v={}
        self.root_node_locations_h={}
        self.root_node_locations_v={}
        self.min_location_h = {} # to capture the final location of each layer's horizontal cg node in the structure
        self.min_location_v = {}# to capture the final location of each layer's vertical cg node in the structure
        self.mode_2_locations_v={}
        self.mode_2_locations_h={}
    

    def assign_floorplan_size(self):
        width=0.0
        height=0.0
        for layer in self.layers:
            if layer.width>width:
                width=layer.width
            if layer.height>height:
                height=layer.height
        self.floorplan_size=[width,height]

    def create_root(self):
        self.root_node_h=Node_3D(id=-1)
        self.root_node_v = Node_3D(id=-1)
        self.root_node_h.edges=[]
        self.root_node_v.edges=[]
        for layer in self.layers:
            self.root_node_h.child.append(layer.New_engine.Htree.hNodeList[0])
            self.root_node_v.child.append(layer.New_engine.Vtree.vNodeList[0])
            for node in layer.New_engine.Htree.hNodeList:
                for rect in node.stitchList:
                    if 'Via' in constraint.constraint.all_component_types:
                        via_index=constraint.constraint.all_component_types.index('Via')
                        if rect.cell.type==layer.New_engine.Types[via_index]:
                            if [rect.cell.x,rect.cell.x+rect.getWidth()] not in layer.via_locations:
                                 layer.via_locations.append([rect.cell.x,rect.cell.x+rect.getWidth()])
            for node in layer.New_engine.Vtree.vNodeList:
                for rect in node.stitchList:
                    if 'Via' in constraint.constraint.all_component_types:
                        via_index=constraint.constraint.all_component_types.index('Via')
                        if rect.cell.type==layer.New_engine.Types[via_index]:
                            if [rect.cell.y,rect.cell.y+rect.getHeight()] not in layer.via_locations:
                                layer.via_locations.append([rect.cell.y,rect.cell.y+rect.getHeight()])



    def calculate_min_location_root(self):
        edgesh_root=self.root_node_h_edges
        edgesv_root=self.root_node_v_edges
        ZDL_H=self.root_node_ZDL_H
        ZDL_V=self.root_node_ZDL_V

        ZDL_H=list(set(ZDL_H))
        ZDL_H.sort()
        ZDL_V = list(set(ZDL_V))
        ZDL_V.sort()
        #print"root", ZDL_H
        #print ZDL_V
        #raw_input()
        # G2 = nx.MultiDiGraph()
        dictList1 = []
        # print self.edgesh
        for foo in edgesh_root:
            # print "EDGE",foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        # print dictList1
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        # print "d",ID, edge_labels1
        nodes = [x for x in range(len(ZDL_H))]
        # G2.add_nodes_from(nodes)

        edge_label = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels1[branch]:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}

            # G2.add_weighted_edges_from(data)
        # mem = Top_Bottom(ID, parentID, G2, label)  # top to bottom evaluation purpose
        # self.Tbeval.append(mem)

        edge_label_h=edge_label
        location=self.min_location_eval(ZDL_H,edge_label_h)

        for i in list(location.keys()):
            self.root_node_locations_h[ZDL_H[i]] = location[i]
        #print"root", self.root_node_locations_h
        #raw_input()
        #GV = nx.MultiDiGraph()
        dictList1 = []
        # print self.edgesh
        for foo in edgesv_root:
            # print foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        # print dictList1

        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        edge_label = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels1[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}
                # print data,label

            #GV.add_weighted_edges_from(data)



        edge_label_v=edge_label
        location=self.min_location_eval(ZDL_V,edge_label_v)
        for i in list(location.keys()):
            self.root_node_locations_v[ZDL_V[i]] = location[i]


    def min_location_eval(self, ZDL, edge_label):
        d3 = defaultdict(list)
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d3[k].append(v)
        # print d3
        X = {}
        H = []
        for i, j in list(d3.items()):
            X[i] = max(j)
        #print"rootX",  X
        for k, v in list(X.items()):
            H.append((k[0], k[1], v))
        G = nx.MultiDiGraph()
        n = [x for x in range(len(ZDL))]
        G.add_nodes_from(n)
        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
        G.add_weighted_edges_from(H)

        A = nx.adjacency_matrix(G)
        B = A.toarray()
        # print B
        Location = {}
        for i in range(len(n)):
            if n[i] == 0:
                Location[n[i]] = 0
            else:
                k = 0
                val = []
                # for j in range(len(B)):
                for j in range(0, i):
                    if B[j][i] > k:
                        # k=B[j][i]
                        pred = j
                        val.append(Location[n[pred]] + B[j][i])
                # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                # loc2=Location[n[pred]]+k
                Location[n[i]] = max(val)
        # print Location
        # Graph_pos_h = []

        dist = {}
        for node in Location:
            key = node

            dist.setdefault(key, [])
            dist[node].append(node)
            dist[node].append(Location[node])
        return Location





class Node_3D(Node):
    def __init__(self,id):
        self.id=id
        self.parent=None
        self.child=[]
        self.edges=[]

        Node.__init__(self, parent=self.parent,boundaries=None,stitchList=None,id=self.id)