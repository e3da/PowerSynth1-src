'''
author: Quang Le
Getting mesh directly from CornerStitch points and islands data
'''

from powercad.electrical_mdl.e_mesh_direct import *


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

    def mesh_update(self):
        self.graph = nx.MultiGraph()
        self.node_count = 1
        isl_dict = {isl.name:isl for isl in self.islands}
        self.comp_dict = {}  # Use to remember the component that has its graph built (so we dont do it again)
        self.comp_nodes={}
        self.comp_net_id={}
        self._handle_pins_connections()
        for g in self.hier_E.isl_group:
            isl = isl_dict[g.name]
            points = self.mesh_nodes(isl=isl)
            self.hier_group_dict = {}
            self.mesh_edges(thick=0.2)  # the thickness is fixed right now but need to be updated by MDK later
            plot = False
            if plot:
                fig = plt.figure(1)
                ax = Axes3D(fig)
                ax.set_xlim3d(0, 22)
                ax.set_ylim3d(0, 42)
                ax.set_zlim3d(0, 2)
                self.plot_3d(fig=fig, ax=ax, show_labels=True)
                plt.show()
            self.handle_hier_node(points, g)

    def mesh_nodes(self,isl=None):
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
        print "num nodes",len(mesh_nodes)
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
        self.set_nodes_neigbours(points=points, locs_map=locs_to_node, xs=xs, ys=ys)
        # setup hierarchical node
        return points