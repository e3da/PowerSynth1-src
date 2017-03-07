'''
Created on May 22, 2015

@author: jhmain
'''
import networkx as nx
import matplotlib.pyplot as plt
from networkx.classes.function import all_neighbors

class CompNode():   # Defines node for a component
    
    def __init__(self, data):
        self.data = data
        self.type = data[0][0:2]
        self.name = data[0][2:]
        self.connections = [] 
        
    def find_connections(self):
        if self.type == 'D_' or self.type == 'V_':      # 2-port components - voltage sources and diodes
            self.connections = self.data[1:3]
        elif self.type == 'M_' or self.type == 'X_':    # 3-port components - MOSFETs and thyristors
            self.connections = self.data[1:4]


def create_layout(data, filename):
    
    # Initialize graph from data. Identify sources, gates, and devices (MOSFETs, thyristors, diodes)
    graph = nx.Graph()
    
    vsource_list = []
    mos_thy_list = []       # mos_thy includes all MOSFETs and thyristors
    mos_thy_comp_list = []
    gate_list = []
    diode_list = []
    
    for i in range(len(data)):
        tempcomp = CompNode(data[i])
        tempcomp.find_connections()
        graph.add_node(tempcomp.name) # Add nodes for components
        
        for i in tempcomp.connections:
            if i != '0':
                if i not in graph:
                    graph.add_node(i)   # Add nodes between components
                graph.add_edge(tempcomp.name, i)    # Add edges between components and nodes
    
        if tempcomp.type == 'V_':
            vsource_list.append(tempcomp.name)    
        elif tempcomp.type == 'X_' or tempcomp.type == 'M_':
            mos_thy_list.append(tempcomp.name)
            mos_thy_comp_list.append(tempcomp)
        elif tempcomp.type == 'D_':
            diode_list.append(tempcomp.name)
        for mosfet in mos_thy_comp_list:
            if mosfet.connections[1] not in gate_list:
                gate_list.append(mosfet.connections[1])
    if len(gate_list) > 2:
        print 'Error. Design must have 2 or fewer gates.'
    
    # Find seminal node (output)
    centrality = nx.betweenness_centrality(graph)
    centrality_list = centrality.items()
    centrality_list.sort(key=lambda x: x[1],reverse=True)
    i=0
    seminal_node = centrality_list[0][0]
    while centrality_list[i][0] in vsource_list or centrality_list[i][0] in mos_thy_list or centrality_list[i][0] in gate_list or centrality_list[i][0] in diode_list:  #Ensure seminal node is not a source, gate, or device
        seminal_node = centrality_list[i+1][0]      
        i+=1
        
    # Label voltage sources (vp = positive source, vn = negative source)
    try:
        vp = vsource_list[0]
        vn = vsource_list[1]
    except:
        print 'Error. Design must have 2 voltage sources'
    
    # Identify one device controlled by each gate (used to identify gate location later)
    gate_dict = {}
    for gate in gate_list:
        if gate not in gate_dict:
            gate_dict[gate] = all_neighbors(graph, gate).next()

    # Remove gate node edges in graph
    for node in nx.nodes(graph):
        if node in gate_list:
            graph.remove_node(node)
            graph.add_node(node)
            
    # Find paths from voltage sources to seminal node
    paths_vp = list(nx.all_simple_paths(graph, vp, seminal_node))
    paths_vn = list(nx.all_simple_paths(graph, vn, seminal_node))
    
    if len(paths_vp) > 2:
        print 'Error. Design must have either 1 or 2 paths between positive voltage source and output.'
    if len(paths_vn) > 2:
        print 'Error. Design must have either 1 or 2 paths between negative voltage source and output.'
    
    # Group devices by path
    devices_vp = []
    devices_vn = []
    for i in range(len(paths_vp)):
        tempgroup = []
        for node in paths_vp[i]:
            if node in mos_thy_list or node in diode_list:
                tempgroup.append(node)
        devices_vp.append(tempgroup)
    for i in range(len(paths_vn)):
        tempgroup = []
        for node in paths_vn[i]:
            if node in mos_thy_list or node in diode_list:
                tempgroup.append(node)
        devices_vn.append(tempgroup)
    
    # Identify gate locations
    gate_vp = ''
    gate_vn = ''
    for gate in gate_list:
        for path in paths_vp:
            if gate_dict[gate] in path: 
                gate_vp = gate
        for path in paths_vn:
            if gate_dict[gate] in path:
                gate_vn = gate
  
    # Remove extra nodes from graph
    for node in nx.nodes(graph):
        if node not in vsource_list and node not in mos_thy_list and node not in diode_list and node not in gate_list:
            graph.remove_node(node)
    
    
    
    #---------------------------------------------------------------------------------------------------------------------------
    #    DRAWING
    #---------------------------------------------------------------------------------------------------------------------------
    
    # Determine height (based on longest path from source to seminal node)
    longest_path = 0
    for path in devices_vp:
        if longest_path < len(path):
            longest_path = len(path)
    for path in devices_vn:
        if longest_path < len(path):
            longest_path = len(path)
    height = longest_path + 1
    
    # Initialize position dictionary. Add seminal node and trace
    pos = {seminal_node:(0,0)}  
    graph.add_edge('SP1', 'SN1')
    
    # Add voltage source nodes and traces. Extend seminal node traces
    if len(paths_vp) == 2:
        pos['SP1'] = (-3,0)
        pos['SP2'] = (-3,1)
        pos['SP3'] = (-5,1)
        pos['SP4'] = (-1,1)
        pos['SP5'] = (-5,height+2)
        pos['SP6'] = (-1,height+2)
        pos['SP8'] = (-4,2)
        pos['SP9'] = (-2,2)
        pos['SP10'] = (-4,height+3)
        pos['SP11'] = (-2,height+3)
        pos[vp] = (-3,height+3)
        graph.add_edge('SP1','SP2')
        graph.add_edge('SP3','SP4')
        graph.add_edge('SP3','SP5')
        graph.add_edge('SP4','SP6')
        graph.add_edge('SP8','SP10')
        graph.add_edge('SP9','SP11')
        graph.add_edge('SP10','SP11')
    elif len(paths_vp) == 1:
        pos['SP1'] = (-5,0)
        pos['SP5'] = (-5,height+2)
        pos['SP8'] = (-4,2)
        pos['SP9'] = (-2,2)
        pos['SP10'] = (-5,height+3)
        pos['SP11'] = (-3,height+3)
        pos[vp] = (-4,height+3)
        graph.add_edge('SP1','SP5')
        graph.add_edge('SP8',vp)
        graph.add_edge(vp,'SP10')
        graph.add_edge('SP10','SP11')
    if len(paths_vn) == 2:
        pos['SN1'] = (3,0)
        pos['SN2'] = (3,1)
        pos['SN3'] = (2,1)
        pos['SN4'] = (4,1)
        pos['SN5'] = (2,height+2)
        pos['SN6'] = (4,height+2)
        pos['SN8'] = (1,2)
        pos['SN9'] = (5,2)
        pos['SN10'] = (1,height+3)
        pos['SN11'] = (5,height+3)
        pos[vn] = (3,height+3)
        graph.add_edge('SN1','SN2')
        graph.add_edge('SN3','SN4')
        graph.add_edge('SN3','SN5')
        graph.add_edge('SN4','SN6')
        graph.add_edge('SN8','SN10')
        graph.add_edge('SN9','SN11')
        graph.add_edge('SN10','SN11')
    elif len(paths_vn) == 1:
        pos['SN1'] = (4,0)
        pos['SN6'] = (4,height+2)
        pos['SN8'] = (1,2)
        pos['SN9'] = (5,2)
        pos['SN10'] = (4,height+3)
        pos['SN11'] = (6,height+3)
        pos[vn] = (5,height+3)
        graph.add_edge('SN1','SN6')
        graph.add_edge('SN9',vn)
        graph.add_edge('SN10','SN11')
    
    # Add gate nodes and traces 
    if gate_vp != '':
        pos[gate_vp] = (-3,2)
        pos['SP7'] = (-3,height+2)
        graph.add_edge(gate_vp,'SP7')
    if gate_vn != '':
        pos[gate_vn] = (3,2)
        pos['SN7'] = (3,height+2)
        graph.add_edge(gate_vn,'SN7')

    # Add shadow nodes for device horizontal connections
    for i in range(height-1):
        if i == 0:
            graph.add_node('SPL'+str(i))
            graph.add_node('SNR'+str(i))
            pos['SPL'+str(i)] = (-5,height+1-i)
            pos['SNR'+str(i)] = (5,height+1-i)
            if gate_vp != '':
                graph.add_node('SPG'+str(i))
            if gate_vn != '':
                graph.add_node('SNG'+str(i))
            if len(paths_vp) > 1:
                graph.add_node('SPR'+str(i))
            if len(paths_vn) > 1:
                graph.add_node('SNL'+str(i)) 
        else:
            graph.add_node('SPL'+str(i))
            graph.add_node('SNR'+str(i))
            if gate_vp != '':
                graph.add_node('SPG'+str(i))   
            if gate_vn != '': 
                graph.add_node('SNG'+str(i))
            if len(paths_vp) > 1:
                graph.add_node('SPR'+str(i))
            if len(paths_vn) > 1:
                graph.add_node('SNL'+str(i))
        pos['SPL'+str(i)] = (-5,height+1-i)
        pos['SNR'+str(i)] = (5,height+1-i)
        if gate_vp != '':
            pos['SPG'+str(i)] = (-3,height+1-i)  
        if gate_vn != '':
            pos['SNG'+str(i)] = (3,height+1-i)
        if len(paths_vp) > 1:
            pos['SPR'+str(i)] = (-1,height+1-i)
        if len(paths_vn) > 1:
            pos['SNL'+str(i)] = (1,height+1-i)
            
    # Add devices and their horizontal connections
    for i in range(len(devices_vp)):
        if i == 0:
            for j in range(len(devices_vp[i])):
                pos[devices_vp[i][j]] = (-4,height+1-j)
                graph.add_node(devices_vp[i][j])
                graph.add_edge(devices_vp[i][j], 'SPL'+str(j))
                if devices_vp[i][j] in mos_thy_list:
                    graph.add_edge(devices_vp[i][j], 'SPG'+str(j))
        elif i == 1:
            for j in range(len(devices_vp[i])):
                pos[devices_vp[i][j]] = (-2,height+1-j)
                graph.add_node(devices_vp[i][j])
                graph.add_edge(devices_vp[i][j], 'SPR'+str(j))
                if devices_vp[i][j] in mos_thy_list:
                    graph.add_edge(devices_vp[i][j], 'SPG'+str(j))
    for i in range(len(devices_vn)):
        if i == 0:
            for j in range(len(devices_vn[i])):
                pos[devices_vn[i][j]] = (4,height+1-j)
                graph.add_node(devices_vn[i][j])
                graph.add_edge(devices_vn[i][j], 'SNR'+str(j))
                if devices_vn[i][j] in mos_thy_list:
                    graph.add_edge(devices_vn[i][j], 'SNG'+str(j))
        elif i == 1:
            for j in range(len(devices_vn[i])):
                pos[devices_vn[i][j]] = (2,height+1-j)
                graph.add_node(devices_vn[i][j])
                graph.add_edge(devices_vn[i][j], 'SNL'+str(j))
                if devices_vn[i][j] in mos_thy_list:
                    graph.add_edge(devices_vn[i][j], 'SNG'+str(j)) 
             
    # Identify nodes to draw
    nodes_draw = [seminal_node,vp,vn]
    for mos_thy in mos_thy_list:
        nodes_draw.append(mos_thy)
    for gate in gate_list:
        nodes_draw.append(gate)
    for diode in diode_list:
        nodes_draw.append(diode)
    
    # Draw graph and save SVG file using Matplotlib
    nx.draw_networkx(graph, pos, with_labels = False, nodelist=nodes_draw, node_size = 500, width = 2.0, font_size = 10, linewidths = 0.0)
    plt.axis('off')
    plt.grid('off')
    plt.savefig(str(filename)+'.svg', format = 'svg')
    #plt.show()