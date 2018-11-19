import networkx as nx
import random
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from math import sqrt
from matplotlib.colors import *
from matplotlib.patches import Rectangle
import pandas as pd


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


def plot_E_map_test(G=None,ax=None,cmap=None):
    all_E=[]
    all_V=[]
    for e in G.edges(data=True):
        edge = e[2]['data']
        V1 = edge.nodeA.V
        V2 = edge.nodeB.V
        edge.E = abs(V1-V2)/ (edge.len*1e-3)
        all_E.append(edge.E)
    for n in G.nodes:
        node= G.node[n]['node']
        all_V.append(node.V)
    V_min = min (all_V)
    V_max = max (all_V)
    E_min = min(all_E)
    E_max = max(all_E)
    normV = Normalize(V_min,V_max)
    normE = Normalize(E_min, E_max)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=normE)
    sm._A = []
    cbar=plt.colorbar(sm, fraction=0.03, pad=0.04)

    cbar.set_label('E Field (V/m)', fontsize=12)
    color_dict = {}
    for e in G.edges(data=True):
        edge = e[2]['data']
        pos1 = edge.nodeA.pos
        pos2 =edge.nodeB.pos
        color = cmap(normE(edge.E))
        ax.arrow(pos1[0],pos1[1], pos2[0]-pos1[0],pos2[1]-pos1[1],color=color,head_width = 0.2, head_length = 0.2,linewidth=2)
        color_dict[edge.name] = color
    for n in G.nodes():
        node=G.node[n]['node']
        pos = node.pos
        color = cmap(normV(node.V))
        ax.scatter(pos[0],pos[1],color=color,s= 20, alpha=0.5)
def network_plot_3D(G, ax, cmap_node={}, cmap_edge={}):
    pos = {}
    labels = {}
    type = {}
    for n in G.nodes():
        node = G.node[n]['node']
        pos[n] = node.pos
        type[n]=node.type
        labels[n] = node.node_id
    # 3D network plot
    with plt.style.context(('ggplot')):
        # Loop on the pos dictionary to extract the x,y,z coordinates of each node
        for lbl, key in zip(labels.values(), pos):
            pos_val = pos[key]
            xi = pos_val[0]
            yi = pos_val[1]
            zi = pos_val[2]

            # Scatter plot
            if cmap_node == {}:
                if type[key]=='internal':
                    ax.scatter(xi, yi, zi, c='blue', s=10, edgecolors='k', alpha=1)
                else:
                    ax.scatter(xi, yi, zi, c='red', s=10, edgecolors='k', alpha=1)

            else:
                name = str(xi) + str(yi) + str(zi)
                color = cmap_node[name]
                ax.scatter(xi, yi, zi, c=color, s=10, edgecolors='k', alpha=0.5)

            ax.text(xi, yi, zi, lbl,fontsize=5)
        # Loop on the list of edges to get the x,y,z, coordinates of the connected nodes
        # Those two points are the extrema of the line to be plotted
        for e in G.edges(data=True):
            j= [e[0],e[1]]
            type = e[2]['data'].type
            name = e[2]['data'].name
            x = np.array((pos[j[0]][0], pos[j[1]][0]))
            y = np.array((pos[j[0]][1], pos[j[1]][1]))
            z = np.array((pos[j[0]][2], pos[j[1]][2]))

            # Plot the connecting lines
            if cmap_edge == {}:
                if type == 'internal':
                    ax.plot(x, y, z, c='gray', alpha=0.5, linewidth=2.5)
                elif type == 'boundary':
                    ax.plot(x, y, z, c='black', alpha=1, linewidth=2.5)
                else:
                    ax.plot(x, y, z, dashes=[6, 2],c='blue', alpha=0.5, linewidth=2.5)

            else:
                color = cmap_edge[name]
                ax.plot(x, y, z, c=color, alpha=1, linewidth=10)

    # Set the initial view
    ax.view_init(30, -60)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    plt.axis('equal')
    return


def plot_v_map_3D(norm=None, cmap='jet', G=None,ax =None):
    # plot voltage level map after being solved
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm)
    cbar.set_label('Voltage Distribution(V)', fontsize=12)
    color_dict = {}
    for n in G.nodes():
        node = G.node[n]['node']
        pos = node.pos
        name = str(pos[0]) + str(pos[1]) + str(pos[2])
        color = cmap(norm(node.V))
        color_dict[name] = color
    network_plot_3D(G, ax, cmap_node=color_dict)


def plot_J_map_3D(norm=None, fig=None, ax=None, cmap='jet', G=None):
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm,
                        ticks=[0, 2.567e4, 5.135e4, 7.702e4, 1.027e5, 1.283e5, 1.541e5, 1.797e5, 2.054e5, 2.310e5,
                               2.567e5])
    cbar.set_label('Current Density (A/m^2)', fontsize=12)
    e_color = []
    for e in G.edges(data=True):
        edge = e[2]['data']
        e_color.append(cmap(norm(edge.J)))


def plot_I_map_3D(norm=None, fig=None, ax=None, cmap='jet', G=None):
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm)
    cbar.set_label('Current (A)', fontsize=12)
    color_dict = {}
    for e in G.edges(data=True):
        name = str(e[0]) + str(e[1])
        edge = e[2]['data']
        color = cmap(norm(edge.I))
        color_dict[name] = color
    network_plot_3D(G, 0, fig, ax, cmap_edge=color_dict)

def plot_I_map_layer(norm=None, ax=None, cmap='jet', G=None, sel_z=0, ori='v', mode='I'):
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm,ticks=[0, 10270, 20540, 30810, 41080, 51350, 61620, 71890, 82160, 92430, 102700])
    if mode == 'I':
        cbar.set_label('Current (A)', fontsize=12)
    elif mode == 'J':
        cbar.set_label('Current Density (A/m^2)', fontsize=12)
    for e in G.edges(data=True):
        edge = e[2]['data']
        data = edge.data
        type = data['type']
        if edge.z == sel_z and type == 'trace':
            if ori == data['ori']:
                if mode == 'I':
                    color = cmap(norm(edge.I))
                elif mode == 'J':
                    color = cmap(norm(edge.J))

                rect = data['rect']
                R = Rectangle((rect.left, rect.bottom), rect.width(), rect.height())
                R.set_fc(color)
                R.set_ec('black')
                R.set_alpha(1)
                ax.add_patch(R)
                txt = str(data['w']) + '_' + str(data['l']) #+ str(edge.R)+'_'
                #txt = str(edge.R)
                #str(edge.L)
                ax.text((rect.left+rect.right)/2, (rect.bottom + rect.top) / 2, txt)


def plot_combined_I_map_layer(norm=None, ax=None, cmap='jet', G=None, sel_z=0, mode='I', W=[0, 10], H=[0, 10], rows=10,
                              cols=10):
    xx = np.linspace(W[0], W[1], cols)
    yy = np.linspace(H[0], H[1], rows)
    sizex = float(W[1] - W[0]) / cols
    sizey = float(H[1] - H[0]) / rows
    patches = []
    gapx = sizex /10
    gapy = sizey / 10
    for xi in xx:
        for yi in yy:
            sq = Rectangle((xi, yi), sizex-gapx, sizey-gapy, fill=True)
            patches.append(sq)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm,ticks=[0,10270, 20540,30810,41080,51350,61620,71890,82160,92430,102700])
    if mode == 'I':
        cbar.set_label('Current (A)', fontsize=12)
    elif mode == 'J':
        cbar.set_label('Current Density (A/m^2)', fontsize=12)
    for p in patches:
        x = p.get_x() + sizex / 2
        y = p.get_y() + sizey / 2
        I = 0
        J = 0
        for e in G.edges(data=True):
            edge = e[2]['data']
            data = edge.data
            type = data['type']
            if edge.z == sel_z and type == 'trace':
                rect = data['rect']
                if rect.encloses(x, y):
                    I += (edge.I)**2
                    J += edge.J**2
        if mode == 'I':
            color = cmap(norm(sqrt(I)))
        elif mode == 'J':
            color = cmap(norm(sqrt(J)))
        if J != 0:
            p.set_fc(color)
            p.set_ec('black')

        else:
            p.set_fc('white')
            p.set_ec('white')
        p.set_linewidth(0)

        p.set_alpha(1)
        ax.add_patch(p)


def plot_combined_I_quiver_map_layer(norm=None, ax=None, cmap='jet', G=None, sel_z=0, mode='I', W=[0, 10], H=[0, 10], numvecs=100,name='test',mesh='grid'):
    df = pd.DataFrame(columns=['x','y','z','Jx','Jy','Jz'])
    if mesh == 'grid':
        xx = np.linspace(W[0], W[1], numvecs+1)
        yy = np.linspace(H[0], H[1], numvecs+1)
        xx,yy=np.meshgrid(xx,yy)
        xy =zip(xx.flatten(),yy.flatten())
        rowid =0
    elif mesh =='nodes':
        xs =[]
        ys =[]
        dx = dy = 0
        for n in G.nodes(data=True):
            node = n[1]['node']
            pos =node.pos
            if node.North ==None:
                dy = -0.01
            elif node.South == None:
                dy=0.01
            elif node.East == None:
                dx= -0.01
            elif node.West == None:
                dx =0.01
            xs.append(pos[0]+dx)
            ys.append(pos[1]+dy)
        xx, yy = np.meshgrid(xs, ys)
        xy = zip(xx.flatten(), yy.flatten())
        rowid = 0
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm)
    if mode == 'I':
        cbar.set_label('Current (A)', fontsize=12)
    elif mode == 'J':
        cbar.set_label('Current Density (A/m^2)', fontsize=12)
        #cbar.set_label('Electric Field (V/m)', fontsize=12)

    for xi,yi in xy:
        Ix=0
        Iy=0
        Jx=0
        Jy=0
        I=[]
        J=[]
        for e in G.edges(data=True):
            edge = e[2]['data']
            data = edge.data
            type = data['type']
            if edge.z == sel_z and type == 'trace':
                rect = data['rect']
                if rect.encloses(xi, yi):
                    if data['ori'] == 'h':
                        Ix = edge.I
                        Jx = edge.J
                        I.append(Ix)
                        J.append(Jx)
                    if data['ori'] == 'v':
                        Iy = edge.I
                        Jy = edge.J
                        I.append(Iy)
                        J.append(Jy)
        if mode == 'I':
            if I!=[]:
                Itot = 0
                for i in I:
                    Itot+=i**2

                color = cmap(norm(sqrt(Itot)))
            else:
                color='white'
            ax.quiver(xi,yi,Ix,Iy,color=color)
        elif mode == 'J':
            if J != []:
                Jtot = 0
                for j in J:
                    Jtot += j ** 2

                color = cmap(norm(sqrt(Jtot)))
            else:
                color = 'white'
            quiveropts = dict(color=color, headlength=0.01,headwidth=0.01)  # common options
            ax.quiver(xi, yi, Jx, Jy,**quiveropts)
            df.loc[rowid]=[xi,yi,0,Jx,Jy,0]
            rowid+=1
    df.to_csv(name+'.csv')
def test_3D_mesh():
    n = 20
    G = generate_random_3Dgraph(n_nodes=n, radius=0.25, seed=1)
    network_plot_3D(G, 0)
    plt.show()