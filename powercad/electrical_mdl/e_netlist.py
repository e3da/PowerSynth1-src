from powercad.electrical_mdl.e_module import EModule
from powercad.electrical_mdl.e_mesh import EMesh
import copy
import numpy as np

class ENetlist():
    '''
    This module convert the mesh structure with parasitics info and its original hierarchy structure into a SPICE netlist
    '''

    def __init__(self, emodule=EModule(), emesh=EMesh()):
        '''
        Args:
            emodule: the original structure
            emesh: the mesh with evaluated parasitic
        '''
        self.module = emodule
        self.mesh = emesh
        self.terminals = []  # a list of terminals name
        self.comp_net = []  # a list of list for all net (node id on the graph) for component pins
        self.mutual_mode = "K"  # if M then we need to rewrite the netlist accordingly
        self.net_graph = None  # This will be a deep copy of the mesh.graph. Later, we need to modify this to disconnect
        # component internal nets used in loop calculation
        self.netlist = ""  # This is the exported netlist


    def find_terminals(self):
        '''
        Find all terminals from the original structure
        update self.terminals (list of terminal names)
        '''
        # Seacrh for all sheet type in module to find its terminals if there are active components, their pins are also
        # included
        for sh in self.module.sheet:
            if sh.net_type == "external":
                self.terminals.append(sh.net)  # append the net name to the netlist if this is a terminal


    def prepare_graph_for_export(self):
        '''
        Disconnect all internal edges of each component in a graph using its corresponded net name
        '''
        # copy a new instance of mesh graph
        self.net_graph = copy.deepcopy(self.mesh.graph)
        # get the net-graph index relationship
        net_graph_id = self.mesh.comp_net_id
        for comp in self.module.components:
            all_net = []  # all nets for a single component
            for sh in comp.sheet:
                all_net.append(net_graph_id[sh.net])  # create a list of net id for component pins
            self.comp_net.append(all_net)
        # All edges among pins in each component need to be removed
        for pins in self.comp_net:
            edge = {}
            for p1 in pins:
                for p2 in pins:
                    if p1 != p2 and not ((p1, p2) in edge):
                        edge[(p1, p2)] = 1
            for e in edge:
                try:
                    self.net_graph.remove_edge(*e)
                    #print "found one edge between", e[0], e[1]
                except:
                    #print "no edge between", e[0], e[1], "continue"
                    continue


    def export_netlist_to_ads(self,file_name = "test.net"):
        text_file = open(file_name, 'w')
        self.find_terminals()
        self.prepare_graph_for_export()
        # invert the dictionary relationship for net_graph
        keys = self.mesh.comp_net_id.values()
        values = self.mesh.comp_net_id.keys()
        id_to_net = dict(zip(keys, values))
        # refresh netlist prepare to write
        self.netlist = ""
        sub = ".subckt X1"
        for t in self.terminals:
            sub += " " + t
        self.netlist += sub + "\n"
        Netname = "n{}"
        Intnet = "{}_{}"
        Rname = "R{}"
        Lname = "L{}"
        L_dict = {}
        for edge in self.net_graph.edges(data=True):
            name = edge[2]['data'].name
            n1 = edge[0]
            n2 = edge[1]
            if n1 in id_to_net:
                net1 = id_to_net[n1]
            else:
                net1 = Netname.format(n1)
            if n2 in id_to_net:
                net2 = id_to_net[n2]
            else:
                net2 = Netname.format(n2)
            # internal net between R and L
            int_net = Intnet.format(net1, net2)

            # get the values from graph
            Rval = edge[2]['res']
            Lval = edge[2]['ind']

            # firt we add the reistor:
            el = Rname.format(name)
            self.netlist += ' '.join([el, net1, int_net, str(Rval), '\n'])
            # then we add the inductor:
            el = Lname.format(name)
            L_dict[el]=Lval
            self.netlist += ' '.join([el, int_net, net2, str(Lval), '\n'])
        M_text ="" # mutual inductance
        for edge in self.mesh.m_graph.edges(data=True):
            M_val = edge[2]['attr']['Mval']
            L1_name = 'L' + str(edge[0])
            L2_name = 'L' + str(edge[1])
            L1_val = L_dict[L1_name]
            L2_val = L_dict[L2_name]
            k = M_val / np.sqrt(L1_val * L2_val)
            if k >1:
                continue
            M_name = 'K' + '_' + L1_name + '_' + L2_name

            M_text += ' '.join([M_name, L1_name, L2_name, str(k), '\n'])
        self.netlist+=M_text

        self.netlist+= ".end"
        text_file.write(self.netlist)
        text_file.close()


        # for debug only
        debug = False

        if debug:
            print self.netlist
            print M_text




