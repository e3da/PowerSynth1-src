''' list of function that can be used outside of the main data structure , or to be organized later'''


from powercad.general.data_struct.util import Rect
import numpy as np

class E_Rect(Rect):
    '''
    This is a rectangle type for module trace, which has neighbour info (not include gaps)
    '''
    def __init__(self,top=0.0,bottom=0.0,left=0.0,right=0.0):
        Rect.__init__(top=top,bottom=bottom,left=left,right=right)
        self.North = []
        self.South = []
        self.East = []
        self.West = []











def generate_mesh_matrix(mesh_graph,result):
    # Make M:
    N = len(mesh_graph.edges) # Number of mesh elements
    col =2 # loop_id, sign
    M = np.zeros([N,col],int)
    e_name_to_id={}
    # Get the current value from the mesh:
    id = 0
    for e in mesh_graph.graph.edges(data=True):
        edge = e[2]['data']
        edge_name = edge.name
        I_name = 'I_B' + edge_name
        edge.I = np.abs(result[I_name])


