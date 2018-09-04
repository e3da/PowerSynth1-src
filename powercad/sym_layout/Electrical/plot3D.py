import networkx as nx
import random
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np




# PLOT 3 D GRAPHs, WILL BE USED TO DEMONSTRATE MESH PLOTS

# SOURCE : https://www.idtools.com.au/3d-network-graphs-python-mplot3d-toolkit/

def generate_random_3Dgraph(n_nodes, radius, seed=None):
    if seed is not None:
        random.seed(seed)

    # Generate a dict of positions
    pos = {i: (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) for i in range(n_nodes)}

    # Create random 3D network
    G = nx.random_geometric_graph(n_nodes, radius, pos=pos)

    return G


def network_plot_3D(G, angle,fig,ax,cmap_node={},cmap_edge={}):
    pos = {}
    labels = {}
    for n in G.nodes():
        node = G.node[n]['node']
        pos[n] = node.pos
        labels[n]=node.node_id
    # 3D network plot
    with plt.style.context(('ggplot')):
        # Loop on the pos dictionary to extract the x,y,z coordinates of each node
        for lbl, key in zip(labels.values(),pos):
            pos_val=pos[key]
            xi = pos_val[0]
            yi = pos_val[1]
            zi = pos_val[2]

            # Scatter plot
            if cmap_node=={}:
                ax.scatter(xi, yi, zi, c='red', s=10, edgecolors='k', alpha=0.5)
            else:
                name = str(xi)+str(yi)+str(zi)
                color = cmap_node[name]
                ax.scatter(xi, yi, zi, c=color, s=100, edgecolors='k', alpha=0.5)

            ax.text(xi,yi,zi,lbl)
        # Loop on the list of edges to get the x,y,z, coordinates of the connected nodes
        # Those two points are the extrema of the line to be plotted
        for i, j in enumerate(G.edges()):
            x = np.array((pos[j[0]][0], pos[j[1]][0]))
            y = np.array((pos[j[0]][1], pos[j[1]][1]))
            z = np.array((pos[j[0]][2], pos[j[1]][2]))

            # Plot the connecting lines
            if cmap_edge=={}:
                ax.plot(x, y, z, c='black', alpha=1)
            else:
                name = str(j[0])+ str(j[1])
                color = cmap_edge[name]
                ax.plot(x, y, z, c=color, alpha=1)

    # Set the initial view
    ax.view_init(30, angle)



    return

def test_3D_mesh():
    n = 20
    G = generate_random_3Dgraph(n_nodes=n, radius=0.25, seed=1)
    network_plot_3D(G, 0)
    plt.show()