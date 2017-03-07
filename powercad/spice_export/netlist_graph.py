'''
@author: Peter N. Tucker
'''
import os
import re
import networkx as nx
import matplotlib.pyplot as plt
from powercad.design.library_structures import Device
from powercad.spice_export.components import *
from powercad.sym_layout.plot import plot_layout

class Module_SPICE_netlist_graph():
    def __init__(self, name, sym_layout, solution_index, template_graph=None):
        """
        Creates a graph to hold SPICE information based on a symbolic layout solution or template graph
        
        Keyword Arguments:
            sym_layout     -- symbolic layout object containing layout solutions
            solution_index -- index of layout in solutions of sym_layout
            template_graph -- lumped graph from which the SPICE graph will be based on
            
        Returns:
            spice_graph
        """
        
        self.name = name.replace(' ','')
        
        # load solution
        self.sym_layout = sym_layout
        self.sym_layout.gen_solution_layout(solution_index)
        if template_graph is None:
            template_graph = self.sym_layout.lumped_graph
        
        # ensure every node has a type
        self._check_node_types(template_graph)
        
        # create graph
        self.spice_graph = nx.Graph()
        
        # get nodes and edges from template_graph
        nbunch = template_graph.nodes(data=True)
        ebunch = template_graph.edges(data=True)
        
        # ensure every node begins with a letter for SPICE
        nbunch[:] = [('N{}'.format(node[0]),node[1]) for node in nbunch]
        ebunch[:] = [('N{}'.format(edge[0]),'N{}'.format(edge[1]),edge[2]) for edge in ebunch]
        
        # add nodes to spice_graph
        self.spice_graph.add_nodes_from(nbunch)
        
        # prepare spice_node dictionaries to map between networkx nodes and SPICE nodes/components
        self.spice_node = {}
        self.spice_node_count = 1 # node 0 is a special node reserved for ground
        self.spice_name = {}
        self.spice_name_count = 1
        
        # create pi or L models from each edge in template_graph
        for edge in ebunch:
            if self.spice_graph.node[edge[0]]['type']=='lead':
                self._build_wire_L_model(edge,edge[0],edge[1])
            elif self.spice_graph.node[edge[1]]['type']=='lead':
                self._build_wire_L_model(edge,edge[1],edge[0])
            else:
                self._build_wire_pi_model(edge)
                
        # create devices
        self.device_models = {} # {'device_name': '(device_model_name, model)', ...}
        for device in [node for node in self.spice_graph.nodes(data=True) if node[1]['type']=='device']:
            # find model, if it doesn't exist, add it to the device dictionary
            device_name = device[1]['obj'].tech.device_tech.name
            if device_name in self.device_models:
                model_name = self.device_models[device_name][0]
            else:
                # get Verilog-A model
                model = device[1]['obj'].tech.device_tech.device_model
                # check Verilog-A file for module
                try:
                    model_name = ((re.search('(?<=module) \w+', model)).group(0)).strip()
                except AttributeError:
                    raise DeviceError(DeviceError.NO_VA_MODULE, device[1]['obj'].tech.device_tech.name)
                # add to device dictionary
                self.device_models[device_name] = (model_name, model)
            
            # determine device type and create device
            if device[1]['obj'].tech.device_tech.device_type == Device.DIODE:
                self._create_diode(device[0], model_name)
            elif device[1]['obj'].tech.device_tech.device_type == Device.TRANSISTOR:
                self._create_mosfet(device[0], model_name)
            else:
                raise DeviceError(DeviceError.UNKNOWN_DEVICE, device[1]['obj'].tech.device_tech.name)

    
    def _check_node_types(self, graph):
        """
        Ensures that each node has a 'type'
        
        Keyword Arguments:
            graph -- networkx graph
        """
        for node,node_attrib in graph.nodes_iter(data=True):
            try:
                node_attrib['type']  # check that node has a 'type'
            except KeyError:         # if not, give it a 'type' of 'node'
                node_attrib['type'] = 'node'
                        
        return graph
    
    
    def get_SPICE_node(self, nx_node):
        """
        Return a unique SPICE node for the networkx node.
            The defined networkx nodes in spice_graph contain spatial information,
            but nodes in SPICE must be a non-negative integer between 0-9999.
            This function maps between the two node spaces
            
        Keyword Arguments:
            nx_node -- networkx node name
            
        Returns:
            spice node equivalent of nx_node
        """
        # if it is not already in the dictionary, add it
        if self.spice_node.get(nx_node) is None:
            self.spice_node[nx_node] = str(self.spice_node_count).zfill(4)
            self.spice_node_count += 1
            # check that node count is less than or equal to 9999
            if self.spice_node_count > 9999:
                raise SpiceNodeError('Node count too high')
        
        # return respective SPICE node
        return self.spice_node[nx_node]
        
        
    def get_SPICE_component(self, nx_node):
        """
        Return a unique SPICE component name for the networkx node.
            The defined networkx node names in spice_graph contain spatial information,
            but component names in SPICE must be an alphanumeric identifier less than
            seven characters long. This function maps between the two name spaces
            
        Keyword Arguments:
            nx_node -- networkx node name
            
        Returns:
            spice name equivalent of nx_node
        """
        # if it is not already in the dictionary, add it
        if self.spice_name.get(nx_node) is None:
            self.spice_name[nx_node] = str(self.spice_name_count).zfill(7)
            self.spice_name_count += 1
            # check that node name is less than 7 characters
            if self.spice_name_count > 999999:
                raise SpiceNameError('Name count too high')
        
        # return respective SPICE node
        return self.spice_name[nx_node]
    
    
    def _build_wire_pi_model(self, edge):
        """
        Builds a pi wire delay model
        
        Keyword Arguments:
            edge  -- edge of template_graph to be converted to pi model in spice_graph
        """
        # get nodes on either side
        node_1 = edge[0]
        node_2 = edge[1]
        
        # add intermediate node
        interm_node = '{}{}'.format(node_1,node_2)
        self.spice_graph.add_node(interm_node, attr_dict={'type':'node'})
        group_name = interm_node
        
        # check for devices on either side
        #    in the event of a device, create a new node for connections
        #    and connect to device
        if self.spice_graph.node[node_1]['type']=='device':
            new_node_1 = '{}{}'.format(node_1,interm_node)
            self.spice_graph.add_node(new_node_1, attr_dict={'type':'node'})
            self.spice_graph.add_edge(node_1,new_node_1, attr_dict={'type':edge[2]['type']})
            node_1 = new_node_1
        if self.spice_graph.node[node_2]['type']=='device':
            new_node_2 = '{}{}'.format(interm_node,node_2)
            self.spice_graph.add_node(new_node_2, attr_dict={'type':'node'})
            self.spice_graph.add_edge(new_node_2,node_2, attr_dict={'type':edge[2]['type']})
            node_2 = new_node_2

        # add resistance node
        res = ((1.0/edge[2]['res'])*1e-3)
        spice_res = Resistor(self.get_SPICE_component(group_name),
                             self.get_SPICE_node(node_1),
                             self.get_SPICE_node(interm_node),
                             res)
        self.spice_graph.add_node('R{}'.format(group_name), attr_dict={'type':'res','component':spice_res})
        self.spice_graph.add_edge(node_1,'R{}'.format(group_name))
        self.spice_graph.add_edge('R{}'.format(group_name),interm_node)
        
        # add inductance node
        ind = ((1.0/edge[2]['ind'])*1e-9)
        spice_ind = Inductor(self.get_SPICE_component(group_name),
                             self.get_SPICE_node(interm_node),
                             self.get_SPICE_node(node_2),
                             ind)
        self.spice_graph.add_node('L{}'.format(group_name), attr_dict={'type':'ind','component':spice_ind})
        self.spice_graph.add_edge(interm_node,'L{}'.format(group_name))
        self.spice_graph.add_edge('L{}'.format(group_name),node_2)
        
        # add two capacitance nodes
        cap = ((1.0/float(edge[2]['cap']))*1e-12)
        # create two imaginary nodes for the body (for visual purposes)
        self.spice_graph.add_node('B{}_1'.format(group_name), attr_dict={'type':'body'})
        self.spice_graph.add_node('B{}_2'.format(group_name), attr_dict={'type':'body'})
        # create capacitor nodes
        spice_cap1 = Capacitor(self.get_SPICE_component('1'+group_name),
                               self.get_SPICE_node(node_1),
                               self.get_SPICE_node('body'),
                               cap/2.0)
        self.spice_graph.add_node('C{}_1'.format(group_name), attr_dict={'type':'cap','component':spice_cap1})
        self.spice_graph.add_edge(node_1,'C{}_1'.format(group_name))
        self.spice_graph.add_edge('C{}_1'.format(group_name),'B{}_1'.format(group_name))
        spice_cap2 = Capacitor(self.get_SPICE_component('2'+group_name),
                               self.get_SPICE_node(node_2),
                               self.get_SPICE_node('body'),
                               cap/2.0)
        self.spice_graph.add_node('C{}_2'.format(group_name), attr_dict={'type':'cap','component':spice_cap2})
        self.spice_graph.add_edge(node_2,'C{}_2'.format(group_name))
        self.spice_graph.add_edge('C{}_2'.format(group_name),'B{}_2'.format(group_name))
    
    
    def _build_wire_L_model(self, edge, lead, non_lead):
        """
        Builds an L wire delay model
        
        Keyword Arguments:
            edge     -- edge of template_graph to be converted to L model in spice_graph
            lead     -- lead node
            non_lead -- non-lead node
        """
        # add intermediate node
        interm_node = '{}{}'.format(edge[0],edge[1])
        self.spice_graph.add_node(interm_node, attr_dict={'type':'node'})
        group_name = interm_node
        
        # check for device on non_lead side
        #    in the event of a device, create a new node for connections
        #    and connect to device
        if self.spice_graph.node[non_lead]['type']=='device':
            new_non_lead = '{}{}'.format(non_lead,interm_node)
            self.spice_graph.add_node(new_non_lead, attr_dict={'type':'node'})
            self.spice_graph.add_edge(non_lead,new_non_lead, attr_dict={'type':edge[2]['type']})
            non_lead = new_non_lead
        
        # add resistance node
        res = ((1.0/edge[2]['res'])*1e-3)
        spice_res = Resistor(self.get_SPICE_component(group_name),
                             self.get_SPICE_node(lead),
                             self.get_SPICE_node(interm_node),
                             res)
        self.spice_graph.add_node('R{}'.format(group_name), attr_dict={'type':'res','component':spice_res})
        self.spice_graph.add_edge(lead,'R{}'.format(group_name))
        self.spice_graph.add_edge('R{}'.format(group_name),interm_node)
        
        # add inductance node
        ind = ((1.0/edge[2]['ind'])*1e-9)
        spice_ind = Inductor(self.get_SPICE_component(group_name),
                             self.get_SPICE_node(interm_node),
                             self.get_SPICE_node(non_lead),
                             ind)
        self.spice_graph.add_node('L{}'.format(group_name), attr_dict={'type':'ind','component':spice_ind})
        self.spice_graph.add_edge(interm_node,'L{}'.format(group_name))
        self.spice_graph.add_edge('L{}'.format(group_name),non_lead)
        
        # add single capacitance node on non_lead side
        cap = ((1.0/float(edge[2]['cap']))*1e-12)
        # create imaginary node for the body (for visual purposes)
        self.spice_graph.add_node('B{}'.format(group_name), attr_dict={'type':'body'})
        # create capacitance node
        spice_cap = Capacitor(self.get_SPICE_component(group_name),
                              self.get_SPICE_node(non_lead),
                              self.get_SPICE_node('body'),
                              cap)
        self.spice_graph.add_node('C{}'.format(group_name), attr_dict={'type':'cap','component':spice_cap})
        self.spice_graph.add_edge(non_lead,'C{}'.format(group_name))
        self.spice_graph.add_edge('C{}'.format(group_name),'B{}'.format(group_name))

            
    def _create_diode(self, node, model_name):
        """
        Creates a diode model
        
        Keyword Arguments:
            node -- diode node
        """
        # determine diode terminals
        anode = []
        cathode = []
        for edge in self.spice_graph.edges(node, data=True):
            if edge[2]['type'] == 'trace':
                anode.append([an for an in edge if an != node][0])
            elif edge[2]['type'] == 'bw power':
                cathode.append([ca for ca in edge if ca != node][0])
        
        # check terminal connections
        namespace = locals()
        for terminal in [anode,cathode]:
            num_connect = len(terminal)
            # check that all terminals have been assigned
            if num_connect == 0:
                raise TerminalError('Diode', node, [name for name in namespace if namespace[name] is terminal][0])
            # check for multiple connections connected to terminal
            if num_connect > 1:
                # if so, create shorts to connect all traces/bondwires to first node
                for connect in range(1,num_connect):
                    short = Short(self.get_SPICE_node(terminal[connect]),
                                         self.get_SPICE_node(terminal[0]))
                    self.spice_graph.add_node('R{}_short'.format(terminal[connect]), attr_dict={'type':'short','component':short})
                    self.spice_graph.add_edge(terminal[connect],'R{}_short'.format(terminal[connect]))
                    self.spice_graph.add_edge('R{}_short'.format(terminal[connect]),terminal[0])
        
        # create diode
        self.spice_graph.node[node]['component'] = Diode(self.get_SPICE_component(node),
                                                         self.get_SPICE_node(anode[0]),
                                                         self.get_SPICE_node(cathode[0]),
                                                         model_name)
    
    
    def _create_mosfet(self, node, model_name):
        """
        Creates a mosfet model
        
        Keyword Arguments:
            node -- mosfet node
        """
        # determine mosfet terminals
        drain = []
        gate = []
        source = []
        for edge in self.spice_graph.edges(node, data=True):
            if edge[2]['type'] == 'trace':
                drain.append([dr for dr in edge if dr != node][0])
            elif edge[2]['type'] == 'bw signal':
                gate.append([gt for gt in edge if gt != node][0])
            elif edge[2]['type'] == 'bw power':
                source.append([src for src in edge if src != node][0])
            
        # check terminal connections
        namespace = locals()
        for terminal in [drain,gate,source]:
            num_connect = len(terminal)
            # check that all terminals have been assigned
            if num_connect == 0:
                raise TerminalError('MOSFET', node, [name for name in namespace if namespace[name] is terminal][0])
            # check for multiple connections connected to terminal
            elif num_connect > 1:
                # if so, create shorts to connect all traces/bondwires to first node
                for connect in range(1,num_connect):
                    short = Short(self.get_SPICE_node(terminal[connect]),
                                  self.get_SPICE_node(terminal[0]))
                    self.spice_graph.add_node('R{}_short'.format(terminal[connect]), attr_dict={'type':'short','component':short})
                    self.spice_graph.add_edge(terminal[connect],'R{}_short'.format(terminal[connect]))
                    self.spice_graph.add_edge('R{}_short'.format(terminal[connect]),terminal[0])
        
        # create mosfet
        self.spice_graph.node[node]['component'] = Mosfet(self.get_SPICE_component(node),
                                                          self.get_SPICE_node(drain[0]),
                                                          self.get_SPICE_node(gate[0]),
                                                          self.get_SPICE_node(source[0]),
                                                          model_name)
        
        
    def write_SPICE_subcircuit(self, directory):
        """
        Writes H-SPICE subcircuit out to [self.name].inc in the directory specified
        
        Keyword Arguments:
            directory  -- file directory to write file to
            
        Returns:
            SPICE file path
        """
      
        # write each device Verilog-A file to local directory
        for model in self.device_models.itervalues():
            full_path = os.path.join(directory, '{}.va'.format(model[0]))
            model_file = open(full_path, 'w')
            model_file.write(model[1])
            model_file.close()
        
        # find leads of module
        lead_list = ''
        for lead in [node for node in self.spice_graph.nodes(data=True) if node[1]['type']=='lead']:
            lead_list += ' ' + self.get_SPICE_node(lead[0])
        lead_list += ' ' + self.get_SPICE_node('body')
        
        # prepare netlist file
        full_path = os.path.join(directory, '{}.inc'.format(self.name))
        spice_file = open(full_path, 'w')
        
        # include each device model
        spice_file.write('\n*** Device Models ***\n')
        for model in self.device_models.itervalues():
            spice_file.write('.hdl "{}.va"\n'.format(model[0]))
            
        # write subcircuit start line with list of lead nodes
        spice_file.write('\n\n.SUBCKT {}{}\n'.format(self.name, lead_list))
        
        # write SPICE line for each node that has a component
        spice_file.write('\n*** {} Components ***\n'.format(self.name))
        for node in self.spice_graph.nodes(data=True):
            if node[1].get('component') is not None:
                spice_file.write(node[1]['component'].SPICE +'\n')
        
        # end subcircuit file
        spice_file.write('\n.ENDS {}'.format(self.name))
        spice_file.close()
        
        # save layout image to clarify lead names
        self.draw_layout()
        plt.savefig(os.path.join(directory, '{}_lead_layout.png'.format(self.name)))
        
#        testing
        print 'names'
        for key,val in self.spice_name.items(): print '{}: {}'.format(key,val)
        print '\nodes'
        for key,val in self.spice_node.items(): print '{}: {}'.format(key,val)
        
        return full_path
        

    def draw_layout(self):
        """ Draws symbolic layout and labels lead nodes for connecting into circuit """
        ax = plt.subplot('111', adjustable='box', aspect=1.0)
        ax.set_axis_off()
        fig = plot_layout(self.sym_layout, ax = ax, new_window=False)
        # label leads
        for lead in [node for node in self.spice_graph.nodes(data=True) if node[1]['type']=='lead']:
            pos = lead[1]['point']
            name = lead[0]
            fig.text(pos[0], pos[1], self.get_SPICE_node(name),
                    horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='yellow', alpha=0.8))
        # add body label
        fig.text(0,0,'body: {}'.format(self.get_SPICE_node('body')),horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='yellow', alpha=0.8))
        
        # show plot
        plt.title(self.name)
#        plt.show()
        
    def draw_graph(self):
        """ Draws networkx graph of spice_graph """
        pos = nx.spring_layout(self.spice_graph,scale=50)
        nx.draw_networkx_nodes(self.spice_graph, pos, node_size=400, node_color='blue', node_shape='o', alpha=0.7)
        nx.draw_networkx_edges(self.spice_graph, pos, edge_color='black')
        nx.draw_networkx_labels(self.spice_graph, pos, font_size=10, font_weight=2)
        plt.show()



# unit-testing
if __name__ == '__main__':
    
    import pickle
    from test_functions import *

    test_graph = None
#    test_graph = build_test_graph();
#    test_graph = build_diode_test_graph()
#    test_graph = build_diode_test_graph_2()
#    test_graph = build_mosfet_test_graph()
#    test_graph = build_mosfet_test_graph_2()
  
    def load_symbolic_layout(filename):
        f = open(filename, 'r')
        sym_layout = pickle.load(f)
        f.close()
        return sym_layout
    
    sym_layout = load_symbolic_layout("../../../export_data/symlayout.p")
    
    spice_graph = Module_SPICE_netlist_graph('Module_2', sym_layout, 10, test_graph)
    spice_graph.write_SPICE_subcircuit('C:/Users/pxt002/Desktop/heatingsicmodel/')
    spice_graph.draw_layout()

#    spice_graph.draw_graph()
