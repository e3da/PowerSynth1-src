'''
Created on May 22, 2015

@author: jhmain
'''
# - mos_thy includes all MOSFETs and thyristors
# - comp lists contain CompNode instances - other lists contain component names only


import os
import networkx as nx


class CompNode():   # Defines node for a component
    
    def __init__(self, data):
        
        try:
            self.data = data
            self.type = data[0][0:2]
            self.name = data[0][2:]
            self.connections = []
            
        except:
            raise Exception('Invalid netlist format - could not find component type and name!')
        
    def find_connections(self):
        
        if self.type == 'D_' or self.type == 'V_':      # 2-port components (voltage sources and diodes)
            self.connections = self.data[1:3]
            if len(self.connections) < 2:
                raise Exception('Invalid netlist format for component "' + self.name + '" - voltage sources and diodes must have 2 connections!')
            
        elif self.type == 'M_' or self.type == 'X_':    # 3-port components (MOSFETs and thyristors)
            self.connections = self.data[1:4]
            if len(self.connections) < 3:
                raise Exception('Invalid netlist format for component "' + self.name + '" - MOSFETs and thyristors must have 3 connections!')
        
        elif self.type == 'R_' or self.type == 'L_' or self.type == 'C_':
            raise Exception('Design cannot include resistors, inductors, or capacitors!')
        
        else:
            raise Exception('Invalid netlist format for component "' + self.name + '" - could not find valid component type!')



class LayoutBuilder():  # Creates symbolic layout from netlist
    
    def __init__(self, data, fname, vp, vn, output_node):
        
        self.data = data
        self.fname = fname
        self.vp = vp
        self.vn = vn
        self.output_node = output_node
        
        self.graph = nx.Graph()
        
        self.vsource_list = []
        self.vsource_comp_list = []
        self.mos_thy_list = []
        self.mos_thy_comp_list = []
        self.diode_list = []
        self.diode_comp_list = []
        self.gate_list = []
        
        self.gate_vp = ''
        self.gate_vn = ''
        self.paths_vp = []
        self.paths_vn = []
        self.devices_vp = []
        self.devices_vn = []
        
        self.height = -1
        self.pos = {}
        
        # Check for empty netlist
        if len(self.data) < 1:
            raise Exception('No data found in netlist!')

    def generate_symbolic_layout(self):    # Top level function
        
        self.create_graph()
        self.perform_checks()
        self.analyze_prepare_graph()
        self.drawing_setup()
        self.draw_layout_SVG()
        
        
    def create_graph(self):     # Builds NetworkX graph from netlist data and identifies source leads, devices (MOSFETs, thyristors, diodes), and gate signal leads
        
        # Build NetworkX graph
        for i in range(len(self.data)):
            tempcomp = CompNode(self.data[i])
            tempcomp.find_connections()
            self.graph.add_node(tempcomp.name)   # Add nodes for components
            
            for i in tempcomp.connections:
                if i not in self.graph:
                    self.graph.add_node(i)   # Add nodes between components
                self.graph.add_edge(tempcomp.name, i)    # Add edges between components and nodes
                
            # Identify source leads, devices, and gate signal leads
            if tempcomp.type == 'V_':
                self.vsource_list.append(tempcomp.name)    
                self.vsource_comp_list.append(tempcomp)
            elif tempcomp.type == 'D_':
                self.diode_list.append(tempcomp.name)
                self.diode_comp_list.append(tempcomp)
            elif tempcomp.type == 'X_' or tempcomp.type == 'M_':
                self.mos_thy_list.append(tempcomp.name)
                self.mos_thy_comp_list.append(tempcomp)
            for mosfet in self.mos_thy_comp_list:
                if mosfet.connections[1] not in self.gate_list:
                    self.gate_list.append(mosfet.connections[1])
        
        
    def perform_checks(self):   # Checks user input and design validity
        
        # Check for valid positive and negative sources
        if self.vp == '':
            raise Exception('A positive source must be defined!')
        if self.vn == '':
            raise Exception('A negative source must be defined!')
        if self.vp not in self.vsource_list:
            raise Exception('Invalid positive source defined - source "' + self.vp + '" not found in netlist!')
        if self.vn not in self.vsource_list:
            raise Exception('Invalid negative source defined - source "' + self.vn + '" not found in netlist!')
        
        # Check if voltage sources are connected to ground
        for vsource in self.vsource_comp_list:
            if '0' not in vsource.connections:
                print 'Warning: Voltage source not connected to ground!'
        
        # Check for valid output node
        if self.output_node == '':
            raise Exception('An output node must be defined!')
        if (self.output_node in self.vsource_list 
              or self.output_node in self.mos_thy_list 
              or self.output_node in self.diode_list 
              or self.output_node in self.gate_list):
            raise Exception('Output node cannot be a source lead, device, or gate signal lead!')
        if self.output_node not in self.graph.nodes():
            raise Exception('Invalid output node defined - output node not found in netlist!')
        
        # Check for valid number of gate signal leads
        if len(self.gate_list) > 2:
            raise Exception('Design cannot have more than 2 gate signal leads!')
        
        # Check that diodes are not connected to gate signal leads
        for diode in self.diode_comp_list:
            for connection in diode.connections:
                if connection in self.gate_list:
                    raise Exception('Diode "' + diode.name + '" cannot be connected to a gate!')
        
        # Check for potential naming conflicts with shadow nodes
        for node in self.graph.nodes():
            if node[:2] == 'SP' or node[:2] == 'SN':
                print 'Warning: Possible conflict between node name "' + node + '" and layout template nodes!'
        
        # Check if output node is seminal node (developer purposes)
        centrality = nx.betweenness_centrality(self.graph)
        centrality_list = centrality.items()
        centrality_list.sort(key=lambda x: x[1],reverse=True)
        i=0
        seminal_node = centrality_list[0][0]
        while (centrality_list[i][0] in self.vsource_list 
               or centrality_list[i][0] in self.mos_thy_list 
               or centrality_list[i][0] in self.gate_list 
               or centrality_list[i][0] in self.diode_list 
               or centrality_list[i][0] == self.vp 
               or centrality_list[i][0] == self.vn):  #Ensure seminal node is not a source, gate, or device
            seminal_node = centrality_list[i+1][0]      
            i+=1
        if seminal_node != self.output_node:
            print 'Warning: Output node is not seminal node!'
        
        
    def analyze_prepare_graph(self):    # Analyzes graph for paths and groupings. Cleans up graph to prepare for drawing setup
        
        # Remove ground nodes
        for node in self.graph.nodes():
            if node == '0':
                self.graph.remove_node(node)
          
        # Handle gate signal voltage sources. Check for unexpected voltage sources
        vsource_gate_list = []
        for vsource in self.vsource_comp_list:
            if vsource.name != self.vp and vsource.name != self.vn:
                for connection in vsource.connections:
                    if connection in self.gate_list:
                        vsource_gate_list.append(vsource.name)
                        self.graph.remove_node(vsource.name)
                if vsource.name not in vsource_gate_list:
                    raise Exception('Unexpected voltage source "' + vsource.name + '" - voltage sources must be positive lead, negative lead, or gate signal lead!')
        
        # Identify devices controlled by each gate (used later to identify gate locations)
        gate1 = ''
        gate2 = ''
        gate1_devices = []
        gate2_devices = []
        if len(self.gate_list) >= 1:
            gate1 = self.gate_list[0]
            for gate_device in nx.all_neighbors(self.graph, self.gate_list[0]):
                gate1_devices.append(gate_device)
        if len(self.gate_list) == 2:
            gate2 = self.gate_list[1]
            for gate_device in nx.all_neighbors(self.graph, self.gate_list[1]):
                gate2_devices.append(gate_device)
      
        # Remove gate node edges in graph
        for node in nx.nodes(self.graph):
            if node in self.gate_list:
                self.graph.remove_node(node)
                self.graph.add_node(node)
             
        # Find paths from source leads to output node
        self.paths_vp = list(nx.all_simple_paths(self.graph, self.vp, self.output_node))
        self.paths_vn = list(nx.all_simple_paths(self.graph, self.vn, self.output_node))
        
        # Check for valid number of paths
        if len(self.paths_vp) < 1:
            raise Exception('No paths found between positive voltage source and output!')
        if len(self.paths_vn) < 1:
            raise Exception('No paths found between negative voltage source and output!')
        
        # Find devices on paths (limit of one device per path)
        for path in self.paths_vp:
            tempgroup = []
            for node in path:
                if node in self.mos_thy_list or node in self.diode_list:
                    tempgroup.append(node)
            if len(tempgroup) == 0:
                raise Exception('No devices found on path between positive lead and output!')
            if len(tempgroup) > 1:
                raise Exception('More than one device found on path between positive lead and output!')
            self.devices_vp.append(tempgroup[0])
        for path in self.paths_vn:
            tempgroup = []
            for node in path:
                if node in self.mos_thy_list or node in self.diode_list:
                    tempgroup.append(node)
            if len(tempgroup) == 0:
                raise Exception('No devices found on path between negative lead and output!')
            if len(tempgroup) > 1:
                raise Exception('More than one device found on path between negative lead and output!')
            self.devices_vn.append(tempgroup[0])
        
        # Check that all gates on the positive [negative] side use the same gate signal lead
        for device in self.devices_vp:
            if device in gate1_devices and device in gate2_devices:
                raise Exception('All gates on the positive side of the layout must use the same gate signal lead!')
        for device in self.devices_vn:
            if device in gate1_devices and device in gate2_devices:
                raise Exception('All gates on the negative side of the layout must use the same gate signal lead!')
        
        # Identify gate locations by matching gate devices to paths      
        if len(self.gate_list) >= 1:
            for device in self.devices_vp:
                if device in self.mos_thy_list and device in gate1_devices:
                        self.gate_vp = gate1
                        break
            for device in self.devices_vn:
                if device in self.mos_thy_list and device in gate1_devices:
                        self.gate_vn = gate1
                        break
        if len(self.gate_list) == 2:
            for device in self.devices_vp:
                if device in self.mos_thy_list and device in gate2_devices:
                        self.gate_vp = gate2
                        break
            for device in self.devices_vn:
                if device in self.mos_thy_list and device in gate2_devices:
                        self.gate_vn = gate2
                        break
        
        # Check that the same gate is not used on both sides
        if self.gate_vp != '' and self.gate_vp == self.gate_vn:
            raise Exception('Gate "' + self.gate_vp + '" cannot be used on both the positive side and negative side of the layout!')

        # Clear graph for rebuilding
        for node in nx.nodes(self.graph):
            self.graph.remove_node(node)
        
        
    def drawing_setup(self):    # Rebuilds graph for drawing
           
        try:
            # Determine height based on number of paths from source leads to output
            self.height = (max(len(self.paths_vp), len(self.paths_vn)) / 2) + 2
            if max(len(self.paths_vp), len(self.paths_vn)) % 2 == 0:
                self.height -= 1
            
            # Add source lead nodes and output node
            self.graph.add_node(self.vp, attr_dict={'type':'lead'})
            self.graph.add_node(self.vn, attr_dict={'type':'lead'})
            self.graph.add_node(self.output_node, attr_dict={'type':'lead'})
                
            # Assign node positions and add traces for source leads and output
            self.pos[self.output_node] = (0,0) 
            self.graph.add_edge('SP1','SN1', attr_dict={'type':'trace'})
            if len(self.paths_vp) > 1:
                self.pos['SP1'] = (-3,0)
                self.pos['SP2'] = (-3,1)
                self.pos['SP3'] = (-5,1)
                self.pos['SP4'] = (-1,1)
                self.pos['SP5'] = (-5,self.height+2)
                self.pos['SP6'] = (-1,self.height+2)
                self.pos['SP8'] = (-4,2)
                self.pos['SP9'] = (-2,2)
                self.pos['SP10'] = (-4,self.height+3)
                self.pos['SP11'] = (-2,self.height+3)
                self.pos[self.vp] = (-3,self.height+3)
                self.graph.add_edge('SP1','SP2', attr_dict={'type':'trace'})
                self.graph.add_edge('SP3','SP4', attr_dict={'type':'trace'})
                self.graph.add_edge('SP3','SP5', attr_dict={'type':'trace'})
                self.graph.add_edge('SP4','SP6', attr_dict={'type':'trace'})
                self.graph.add_edge('SP8','SP10', attr_dict={'type':'trace'})
                self.graph.add_edge('SP9','SP11', attr_dict={'type':'trace'})
                self.graph.add_edge('SP10','SP11', attr_dict={'type':'trace'})
            else:
                self.pos['SP1'] = (-5,0)
                self.pos['SP5'] = (-5,self.height+2)
                self.pos['SP8'] = (-4,2)
                self.pos['SP9'] = (-2,2)
                self.pos['SP10'] = (-5,self.height+3)
                self.pos['SP11'] = (-3,self.height+3)
                self.pos[self.vp] = (-4,self.height+3)
                self.graph.add_edge('SP1','SP5', attr_dict={'type':'trace'})
                self.graph.add_edge('SP8',self.vp, attr_dict={'type':'trace'})
                self.graph.add_edge('SP10','SP11', attr_dict={'type':'trace'})
            if len(self.paths_vn) > 1:
                self.pos['SN1'] = (3,0)
                self.pos['SN2'] = (3,1)
                self.pos['SN3'] = (2,1)
                self.pos['SN4'] = (4,1)
                self.pos['SN5'] = (2,self.height+2)
                self.pos['SN6'] = (4,self.height+2)
                self.pos['SN8'] = (1,2)
                self.pos['SN9'] = (5,2)
                self.pos['SN10'] = (1,self.height+3)
                self.pos['SN11'] = (5,self.height+3)
                self.pos[self.vn] = (3,self.height+3)
                self.graph.add_edge('SN1','SN2', attr_dict={'type':'trace'})
                self.graph.add_edge('SN3','SN4', attr_dict={'type':'trace'})
                self.graph.add_edge('SN3','SN5', attr_dict={'type':'trace'})
                self.graph.add_edge('SN4','SN6', attr_dict={'type':'trace'})
                self.graph.add_edge('SN8','SN10', attr_dict={'type':'trace'})
                self.graph.add_edge('SN9','SN11', attr_dict={'type':'trace'})
                self.graph.add_edge('SN10','SN11', attr_dict={'type':'trace'})
            else:
                self.pos['SN1'] = (4,0)
                self.pos['SN6'] = (4,self.height+2)
                self.pos['SN8'] = (1,2)
                self.pos['SN9'] = (5,2)
                self.pos['SN10'] = (4,self.height+3)
                self.pos['SN11'] = (6,self.height+3)
                self.pos[self.vn] = (5,self.height+3)
                self.graph.add_edge('SN1','SN6', attr_dict={'type':'trace'})
                self.graph.add_edge('SN9',self.vn, attr_dict={'type':'trace'})
                self.graph.add_edge('SN10','SN11', attr_dict={'type':'trace'})
            
            # Add gate signal lead nodes and traces 
            if self.gate_vp != '':
                self.pos[self.gate_vp] = (-3,2)
                self.pos['SP7'] = (-3,self.height+2)
                self.graph.add_node(self.gate_vp, attr_dict={'type':'gate_signal_lead'})
                self.graph.add_edge(self.gate_vp,'SP7', attr_dict={'type':'trace'})
            if self.gate_vn != '':
                self.pos[self.gate_vn] = (3,2)
                self.pos['SN7'] = (3,self.height+2)
                self.graph.add_node(self.gate_vn, attr_dict={'type':'gate_signal_lead'})
                self.graph.add_edge(self.gate_vn,'SN7', attr_dict={'type':'trace'})
        
            # Add shadow node positions for source and gate bondwires
            for i in range(self.height):
                self.pos['SPL'+str(i)] = (-5,self.height+1-i)
                self.pos['SNR'+str(i)] = (5,self.height+1-i)
                if len(self.paths_vp) > 1:
                    self.pos['SPR'+str(i)] = (-1,self.height+1-i)
                if len(self.paths_vn) > 1:
                    self.pos['SNL'+str(i)] = (1,self.height+1-i)
                if self.gate_vp != '':
                    self.pos['SPG'+str(i)] = (-3,self.height+1-i)  
                if self.gate_vn != '':
                    self.pos['SNG'+str(i)] = (3,self.height+1-i)
            
            # Add device nodes and bondwires
            for i in range(len(self.devices_vp)):
                self.graph.add_node(self.devices_vp[i], attr_dict={'type':'device'})
                if i % 2 == 0:
                    self.pos[self.devices_vp[i]] = (-4,self.height+1-i/2)
                    self.graph.add_edge(self.devices_vp[i], 'SPL' + str(i/2), attr_dict={'type':'bondwire'})
                else:
                    self.pos[self.devices_vp[i]] = (-2,self.height+1-i/2)
                    self.graph.add_edge(self.devices_vp[i], 'SPR' + str(i/2), attr_dict={'type':'bondwire'})
                if self.devices_vp[i] in self.mos_thy_list:
                    self.graph.add_edge(self.devices_vp[i], 'SPG' + str(i/2), attr_dict={'type':'bondwire'})
            for i in range(len(self.devices_vn)):
                self.graph.add_node(self.devices_vn[i], attr_dict={'type':'device'})
                if i % 2 == 0:
                    self.pos[self.devices_vn[i]] = (4,self.height+1-i/2)
                    self.graph.add_edge(self.devices_vn[i], 'SNR' + str(i/2), attr_dict={'type':'bondwire'})
                else:
                    self.pos[self.devices_vn[i]] = (2,self.height+1-i/2)
                    self.graph.add_edge(self.devices_vn[i], 'SNL' + str(i/2), attr_dict={'type':'bondwire'})
                if self.devices_vn[i] in self.mos_thy_list:
                    self.graph.add_edge(self.devices_vn[i], 'SNG' + str(i/2), attr_dict={'type':'bondwire'})

            # Check that all nodes have a type
            for node in self.graph.nodes(data=True):    
                try:
                    node[1]['type']
                except:
                    node[1]['type'] = 'shadow'
                
        except:
            raise Exception('Drawing setup unsuccessful')

    
    def draw_layout_SVG(self):    # Draws layout as SVG file using XML
        
        try:
            # Set image size
            image_size = self.height*6
           
            # Adjust node positions to keep layout on page
            for node in self.pos:
                self.pos[node] = (self.pos[node][0]+(image_size/2),-self.pos[node][1]+image_size)
        
        
            # Create XML file with header
            f = open(str(self.fname) + '.svg', 'w')
            f.write('<?xml version="1.0" encoding="utf-8" ?>\n')
            f.write('<svg baseProfile="full" width="' + str(image_size) + '" height="' + str(image_size) 
                    + '" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"><defs />\n')
            
            path_count = 0
            
            # Draw lines for edges (traces and bondwires)
            for edge in self.graph.edges(data=True):
                if edge[2]['type'] == 'trace':
                    path_count += 1
                    f.write('\t' + '<path\n')
                    f.write('\t\t' + 'id="path_' + str(path_count) + '"\n')
                    f.write('\t\t' + 'd="M ' + str(self.pos[edge[0]][0]) + ',' + str(self.pos[edge[0]][1]) + ' L ' + str(self.pos[edge[1]][0]) + ',' + str(self.pos[edge[1]][1]) + '"\n')
                    f.write('\t\t' + 'style="color:#000000;fill:none;stroke:#ff0000;stroke-width:0.1" />\n')
                elif edge[2]['type'] == 'bondwire':
                    path_count += 1
                    f.write('\t' + '<path\n')
                    f.write('\t\t' + 'id="path_' + str(path_count) + '"\n')
                    f.write('\t\t' + 'd="M ' + str(self.pos[edge[0]][0]) + ',' + str(self.pos[edge[0]][1]) + ' L ' + str(self.pos[edge[1]][0]) + ',' + str(self.pos[edge[1]][1]) + '"\n')
                    f.write('\t\t' + 'style="color:#000000;fill:none;stroke:#000000;stroke-width:0.1" />\n')
                else:
                    raise Exception('Could not find type trace or bondwire for edge!')
            
            # Draw circles for nodes (source leads, output, gate signal leads, and devices)
            for node in self.graph.nodes(data=True):
                if node[1]['type'] == 'lead' or node[1]['type'] == 'gate_signal_lead':
                    path_count += 1
                    f.write('\t' + '<path\n')
                    f.write('\t\t' + 'id="path_' + str(path_count) + '"\n')
                    f.write('\t\t' + 'sodipodi:type="arc"\n')
                    f.write('\t\t' + 'sodipodi:cx="' + str(self.pos[node[0]][0]) + '"\n')
                    f.write('\t\t' + 'sodipodi:cy="' + str(self.pos[node[0]][1]) + '"\n')
                    f.write('\t\t' + 'sodipodi:rx="0.25"\n')
                    f.write('\t\t' + 'sodipodi:ry="0.25"\n')
                    f.write('\t\t' + 'd="M ' + str(self.pos[node[0]][0]+0.25) + ',' + str(self.pos[node[0]][1]) + ' a 0.25,0.25 0 1 1 -0.5,0 0.25,0.25 0 1 1 0.5,0"\n')
                    f.write('\t\t' + 'style="fill:#008000;stroke:none"' + ' />\n')
                elif node[1]['type'] == 'device':
                    path_count += 1
                    f.write('\t' + '<path\n')
                    f.write('\t\t' + 'id="path_' + str(path_count) + '"\n')
                    f.write('\t\t' + 'sodipodi:type="arc"\n')
                    f.write('\t\t' + 'sodipodi:cx="' + str(self.pos[node[0]][0]) + '"\n')
                    f.write('\t\t' + 'sodipodi:cy="' + str(self.pos[node[0]][1]) + '"\n')
                    f.write('\t\t' + 'sodipodi:rx="0.25"\n')
                    f.write('\t\t' + 'sodipodi:ry="0.25"\n')
                    f.write('\t\t' + 'd="M ' + str(self.pos[node[0]][0]+0.25) + ',' + str(self.pos[node[0]][1]) + ' a 0.25,0.25 0 1 1 -0.5,0 0.25,0.25 0 1 1 0.5,0"\n')
                    f.write('\t\t' + 'style="fill:#E40CEB;stroke:none"' + ' />\n')
                else:
                    pass    # Node is a shadow node
            
            # Add close SVG tag. Close file
            f.write('</svg>')
            f.close()

        except:
            # Ensure generated SVG file has been closed and deleted if unsuccessful
            if not f.closed:
                f.close()
            os.remove(str(self.fname) + '.svg')
            raise Exception('Layout drawing unsuccessful')