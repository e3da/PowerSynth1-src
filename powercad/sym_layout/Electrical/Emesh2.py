'''
Rewrite mesh method for nodes in cell center to include capacitance models
'''

class Mesh_node:
    def __init__(self, pos, type, node_id, group_id=None):
        self.node_id = node_id
        self.group_id = group_id  # Use to define if nodes  are on same trace_group
        self.type = type  # Node type
        self.b_type = []  # if type is boundary this will tell if it is N,S,E,W
        self.pos = pos  # Node Position x , y ,z

        # For neighbours nodes of each point
        self.West = None
        self.East = None
        self.North = None
        self.South = None
        # For evaluation
        self.V = 0  # Updated node voltage later

        # Neighbour Edges on same layer:
        self.N_edge = None
        self.S_edge = None
        self.W_edge = None
        self.E_edge = None


class Mesh_edge:
    # The 1D element for electrical meshing
    def __init__(self, m_type=None, nodeA=None, nodeB=None, data={}, length=1, z=0, thick=0.2, ori=None, side=None):
        self.type = m_type  # Edge type, internal, boundary or external
        # Edge parasitics (R, L for now). Handling C will be different
        self.R = 1
        self.L = 1
        self.C = 1
        self.len = length

        self.z = z  # if None this is an hier edge
        self.thick = thick
        # Evaluated width and length for edge
        self.data = data
        self.name = data['name']
        # Updated Edge Current
        self.I = 0
        self.J = 0
        self.E = 0

        # Edges neighbour nodes
        self.nodeA = nodeA
        self.nodeB = nodeB
        # Always == None if this is hierarchy type 1
        self.ori = ori
        self.side = side  # 0:NE , 1:NW , 2:SW , 3:SE

