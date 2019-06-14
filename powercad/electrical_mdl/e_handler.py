import numpy as np

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


