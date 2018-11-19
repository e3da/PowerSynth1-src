from sympy import *
import scipy
from scipy.sparse.linalg import gmres
from powercad.Spice_handler.spice_export.LTSPICE import *
from powercad.Spice_handler.spice_export.HSPICE import *
from powercad.Spice_handler.spice_export.raw_read import *
from numba import jit

class diag_prec:
    def __init__(self, A):
        self.shape = A.shape
        n = self.shape[0]
        self.dinv = numpy.empty(n)
        for i in xrange(n):
            self.dinv[i] = 1.0 / A[i, i]

    def precon(self, x, y):
        numpy.multiply(x, self.dinv, y)


class Circuit():
    def __init__(self):
        self.num_rlc = 0  # number of RLC elements
        self.num_ind = 0  # number of inductors
        self.num_V = 0  # number of independent voltage sources
        self.num_I = 0  # number of independent current sources
        self.i_unk = 0  # number of current unknowns
        self.num_opamps = 0  # number of op amps
        self.num_vcvs = 0  # number of controlled sources of various types
        self.num_vccs = 0
        self.num_cccs = 0
        self.num_ccvs = 0
        self.num_cpld_ind = 0  # number of coupled inductors

        # light version
        # Element names are used as keys
        self.element =[]
        self.pnode={}
        self.nnode={}
        self.cp_node={}
        self.cn_node={}
        self.vout={}
        self.value={}
        self.Vname={}
        # Handle Mutual inductance
        self.Lname1={}
        self.Lname2={}

        self.V_node=None


        # Data frame for unknown current
        # light version
        # Element names are used as keys
        self.cur_element = []
        self.cur_pnode = {}
        self.cur_nnode = {}
        self.cur_value = {}

        self.net_data = None  # storing data from netlist or graph
        self.branch_cnt = 0  # number of branches in the netlist
        # Matrices:
        self.G = None
        self.B = None
        self.C = None
        self.D = None
        self.V = None
        self.J = None
        self.I = None
        self.Ev = None
        self.Z = None
        self.X = None
        self.A = None
        self.M = {}  # Dictionary for coupling pairs
        # List of circuit equations:
        self.equ = None
        self.func = []
        self.solver = None
        self.max_net_id = 0 # maximum used net id value
        self.results_dict={}
        self.Rport=50
        self.freq = 1000

    def assign_freq(self,freq=1000):
        self.freq = freq
        self.s = 2 * freq * np.pi * 1j

    def _graph_add_comp(self,name, pnode, nnode, val):
        self.element.append(name)
        self.pnode[name] = pnode
        self.nnode[name] = nnode
        self.value[name] = float(val)
    def _graph_add_M(self,name,L1_name,L2_name,val):
        self.element.append(name)
        self.Lname1[name] = L1_name
        self.Lname2[name] = L2_name
        self.value[name] = float(val)

    def indep_current_source(self, pnode=0, nnode=0, val=1):
        self.element.append('Is')
        self.pnode['Is'] = pnode
        self.nnode['Is'] = nnode
        self.value['Is'] = float(val)

    def indep_voltage_source(self, pnode=0, nnode=0, val=1000, name='Vs'):
        self.V_node=pnode
        self.element.append(name)
        self.pnode[name] = pnode
        self.nnode[name] = nnode
        self.value[name] = float(val)





    def _graph_read(self,graph):
        '''
        this will be used to read mesh graph and forming matrices
        :param lumped_graph: networkX graph from PowerSynth
        :return: update self.net_data
        '''
        # List out all ports
        self.node_dict = {}
        # MAP the ports first
        net_id = 1  # starting at 1 saving 0 for ground
        Rname = "R{0}"
        Lname = "L{0}"
        Cname = "C{0}"
        rem_list=[]
        for edge in graph.edges(data=True):
            n1 = edge[0]
            n2 = edge[1]
            edged = edge[2]['data']
            data = edged.data
            node1 = graph.node[n1]['node']
            C1 = graph.node[n1]['cap']
            pos1 = node1.pos
            node2 = graph.node[n2]['node']
            C2 = graph.node[n2]['cap']

            pos2 = node2.pos
            node1 = n1
            node2 = n2

            if data['type']=='trace':
                if data['ori'] == 'h':
                    # make sure the node with smaller x will be positive
                    if pos1[0]>pos2[0]:
                        temp = n1
                        node1 = n2
                        node2 = temp
                elif data['ori'] == 'v':
                    # make sure the node with smaller y will be positive
                    if pos1[1] > pos2[1]:
                        temp = n1
                        node1 = n2
                        node2 = temp

            RLname = edge[2]['data'].name
            if node1 not in self.node_dict.keys():
                net1 = net_id
                self.node_dict[node1] = net1
                net_id += 1
            else:
                net1 = self.node_dict[node1]
            # add an internal net for each branch
            int_net = net_id
            # add a reistor between net1 and internal net
            net_id += 1
            val = edge[2]['res']
            self._graph_add_comp(Rname.format(RLname), net1, int_net, val)
            if node2 not in self.node_dict.keys():
                net2 = net_id
                self.node_dict[node2] = net2
                net_id += 1
            else:
                net2 = self.node_dict[node2]

            # add an inductor between internal net and net2
            val = edge[2]['ind']
            #print Lname.format(RLCname)
            self._graph_add_comp(Lname.format(RLname), int_net, net2, val)

            #ADD CAP

            if not (n1 in rem_list):
                self._graph_add_comp(Cname.format(RLname+'_1'), net1, 0, C1)
                rem_list.append(n1)
            if not (n2 in rem_list):
                self._graph_add_comp(Cname.format(RLname + '_2'), net2, 0, C2)
                rem_list.append(n2)
            '''
            if 'cap' in edge[2].keys():  # IF this branch has a capacitance
                val = edge[2]['cap']
                self._graph_add_comp(Cname.format(RLname + '_1'), net1, 0, val/2)
                self._graph_add_comp(Cname.format(RLname + '_2'), net2, 0, val / 2)
            '''
        self.max_net_id=net_id
    def m_graph_read(self,m_graph):
        '''

        Args:
            m_graph: is the mutual coupling info from mesh

        Returns:
            update M elemts
        '''
        for edge in m_graph.edges(data=True):
            M_val = edge[2]['attr']['Mval']
            L1_name = 'L' + str(edge[0])
            L2_name = 'L' + str(edge[1])
            M_name='M'+'_'+L1_name+'_'+L2_name
            self._graph_add_M(M_name,L1_name,L2_name,M_val)

    def refresh_current_info(self):
        '''
        Refresh current info to initial state
        '''
        self.cur_element=[]
        self.cur_pnode={}
        self.cur_nnode = {}
        self.cur_value = {}

    def build_current_info(self):
        '''
        Update the current value from circuit component data frame
        # Build df2: consists of branches with current unknowns, used for C & D matrices
        # walk through data frame and find these parameters
        :return:
        '''
        for i in range(len(self.element)):
            # process all the elements creating unknown currents
            el = self.element[i]
            x = self.element[i][0]  # get 1st letter of element name
            if (x == 'L') or (x == 'V') or (x == 'O') or (x == 'E') or (x == 'H') or (x == 'F'):
                self.cur_element.append(el)
                self.cur_pnode[el] = self.pnode[el]
                self.cur_nnode[el] = self.nnode[el]
                self.cur_value[el] = self.value[el]

    def _assign_vsource(self,source_node,vname='Vs',volt=1):
        # add current source to source_node
        self.V_node=source_node
        source_net =self.node_dict[source_node]
        vnet=self.max_net_id
        #self.indep_voltage_source(source_net, 0, val=volt, name=vname)

        if self.Rport!=0:
            self.indep_voltage_source(vnet,0,val=volt,name=vname)
            R_name = 'Rin' + str(source_net)
            self._graph_add_comp(R_name, vnet, source_net, self.Rport)
        else:
            self.indep_voltage_source(vnet, source_net, val=volt, name=vname)

        self.max_net_id += 1

    def equiv(self, nodes,net=None):
        '''
        equiv all nodes in the nodes list
        Args:
            nodes: list object
        Returns: Update the matrix
        '''
        print self.node_dict

        if net==None: # Equiv multiple nets mode
            eq_net = self.node_dict[nodes[0]]
        else:
            eq_net=net
        print "eq_net",eq_net
        all_nets = [self.node_dict[n] for n in nodes]
        # Check over all p and n nodes, if they are in equiv list rename them to eq_net. If p and n node of a component
        # are the same, remove the component.
        for k in self.pnode.keys():
            p_net = self.pnode[k]
            n_net = self.nnode[k]
            if p_net in all_nets and n_net in all_nets:
                print "delete component", k
                del self.pnode[k]
                del self.nnode[k]
                del self.element[k]
                del self.value[k]
            elif p_net in all_nets:
                if eq_net==0:
                    self.nnode[k] = eq_net
                else:
                    self.pnode[k]=eq_net
            elif n_net in all_nets:
                self.nnode[k] = eq_net

        print self.node_dict
    def _remove_comp(self,name=None):
        #print "delete component", name
        del self.pnode[name]
        del self.nnode[name]
        self.element.remove(name)
        del self.value[name]
    def _remove_vsrc(self, source_node, vname='Vs'):
        self._remove_comp(vname)
        source_net = self.node_dict[source_node]
        if self.Rport!=0:
            R_name = 'Rin' + str(source_net)
            self._remove_comp(R_name)
        self.max_net_id-=1

    def _remove_port(self,node):
        port = self.node_dict[node]
        if self.Rport!=0:
            R_name = 'Rin' + str(port)
            self._remove_comp(R_name)

    def _add_ports(self,node,port=True):
        newport = self.node_dict[node]
        if port:
            R_name = 'Rin' + str(newport)
            if self.Rport!=0:
                self._graph_add_comp( R_name, newport, 0, self.Rport)
            else:
                self.equiv([newport],0)
        else:
            self.equiv([node],0)
    def get_source_current(self,vsrc_name):
        Iname='I_'+ vsrc_name
        return self.results[Iname]
    def find_port_current(self,node):
        ''' Find port voltage and devide by its resistance to find the output current'''
        port = self.node_dict[node]
        port_v = 'v' + str(port)
        v_port = self.results[port_v]
        return v_port/self.Rport

    def find_vname(self, name):
        for i in range(len(self.cur_element)):
            el = self.cur_element[i]
            if name == el:
                n1 = self.cur_pnode[name]
                n2 = self.cur_nnode[name]
                return n1, n2, i

        print('failed to find matching branch element in find_vname')


    def _compute_S_params(self,ports=[]):
        '''
                Perform multiple calculation to find the Sparams src sink pair
                Args:
                    srcs: list of sources
                    sinks: list of sinks
                    *src and sink at same list index will be in a pair
                Returns:
        '''
        all_ports = list(ports)  # list of ports
        S_mat = np.ndarray([len(all_ports), len(all_ports)])  # Form an impedance matrix
        ana_ports = []  # list of ports that got analyzed already
        for p in all_ports:
            print p
            self._add_ports(p, True)
        for sel_port in all_ports:  # go to each source in the list assign a voltage source
            id = all_ports.index(sel_port)
            self._remove_port(sel_port)
            self._assign_vsource(sel_port, vname='Vs', volt=1)
            self.build_current_info()
            self.solve_iv()
            #self.solve_iv_hspice(filename='S_para.sp',
            #    env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
            #self.results=self.hspice_result
            port_i = 'v' + str(self.node_dict[sel_port])
            vi = self.results[port_i]
            ii = -self.get_source_current('Vs')
            Zin = vi/ii
            Z0 = self.Rport
            #print Z0,Zin
            S_mat[id, id] = 20 * np.log10(np.abs(((Zin - Z0) / (Zin + Z0)))) # Update diagonal values
            #print S_mat[id,id]
            #raw_input()
            for j_port in all_ports:
                if j_port!=sel_port:
                    id2 = all_ports.index(j_port)
                    port_j = 'v' + str(self.node_dict[all_ports[id2]])
                    vj = self.results[port_j]
                    S_mat[id, id2] = 20 * np.log10(np.abs(2 * vj))
                    #S_mat[id2, id] = 20 * np.log10(np.abs(2 * vj))
            self._remove_vsrc(sel_port, 'Vs')
            self._add_ports(sel_port,True)
            self.refresh_current_info()
            self.results={}
        return S_mat
    def _compute_matrix(self, srcs=[], sinks=[]):
        print "mat solve"
        '''
        Perform multiple calculation to find the loop inductance of each src sink pair
        Args:
            srcs: list of sources
            sinks: list of sinks
            *src and sink at same list index will be in a pair
        Returns:
        '''
        all_ports= list(srcs+sinks) # list of ports
        imp_mat = np.ndarray([len(srcs),len(sinks)],dtype=np.complex128) # Form an impedance matrix
        ana_ports=[] # list of ports that got analyzed already
        for p in all_ports:
            self._add_ports(p,True)
        for id in range(len(srcs)): # go to each source in the list assign a voltage source
            cur_src = srcs[id]
            cur_sink = sinks[id]
            if not (cur_src in ana_ports):
                ana_ports.append(cur_sink) # add to list
                self._remove_port(cur_src)
                self._assign_vsource(cur_src, vname='Vs', volt=1)
                self.build_current_info()
                self.solve_iv()
                #print self.element
                #self.solve_iv_hspice(filename='testM.sp',
                #    env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
                #self.results=self.hspice_result
                #raw_input()
                #print self.results
                src_i = 'v'+ str(self.node_dict[cur_src])
                sink_i = 'v'+str(self.node_dict[cur_sink])
                dvi = self.results[src_i] - self.results[sink_i]
                ii = self.get_source_current('Vs')
                Ri = np.real(dvi / ii)
                Li = np.imag(dvi / ii) / abs(self.s)
                imp_mat[id,id]= abs(Ri) + abs(Li)*1j # Update diagonal values
                for mea_sink in list(set(sinks)-set(ana_ports)):
                    id2 = sinks.index(mea_sink)
                    src_j = 'v' + str(self.node_dict[srcs[id2]])
                    sink_j = 'v' + str(self.node_dict[sinks[id2]])
                    dvj = self.results[src_j] - self.results[sink_j]
                    Rij = np.real(dvj / ii)
                    Lij = np.imag(dvj / ii) / abs(self.s)
                    imp_mat[id,id2]= abs(Rij) + abs(Lij) * 1j   # Update off-diagonal values
                    imp_mat[id2, id] = abs(Rij) + abs(Lij) * 1j  # Update off-diagonal values
                self._remove_vsrc(cur_src,'Vs')
                self._add_ports(cur_src)
                self.refresh_current_info()

        for row in imp_mat:
            print row

    def _compute_mutual(self,srcs=[],sinks=[],vname=None):
        '''
        Assume the current go out at 2 sinks
        Args:
            srcs: 2 srcs node
            sinks: 2 sink node

        Returns:
        '''
        # Assign signal to first port
        self._assign_vsource(srcs[0], vname=vname, volt=1)
        # ADD a port to 2nd source
        self._add_ports(srcs[1],True)
        self._add_ports(sinks[0], True)
        self._add_ports(sinks[1], True)
        self.build_current_info()
        self.solve_iv()
        #self.solve_iv_hspice(filename='testM.sp',
        #                     env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
        #self.results=self.hspice_result
        src_net1 = self.node_dict[srcs[0]]
        sink_net1 = self.node_dict[sinks[0]]
        src_net2 = self.node_dict[srcs[1]]
        sink_net2 = self.node_dict[sinks[1]]
        src1 = 'v' + str(src_net1)
        sink1 = 'v' + str(sink_net1)
        src2 = 'v' + str(src_net2)
        sink2 = 'v' + str(sink_net2)
        vs1 = self.results[src1] - self.results[sink1]
        vs2 = self.results[src2] - self.results[sink2]
        i1 = self.find_port_current(sinks[0])
        print 'R1',np.real(vs1/i1),'L1',np.imag(vs1/i1)/abs(self.s)

        print 'R12', np.real(vs2/i1),'L12',np.imag(vs2/i1)/abs(self.s)

    def _compute_imp(self,source_node,sink_node,I_node):
        source_net = self.node_dict[source_node]
        sink_net = self.node_dict[sink_node]
        print 'src,sink',source_net,sink_net
        source_v = 'v' + str(source_net)
        sink_v = 'v' + str(sink_net)
        v_source=self.results[source_v]
        v_sink = self.results[sink_v]
        I =self.find_port_current(I_node)
        #print (v_source - v_sink), I
        imp =(v_source-v_sink)/I
        return np.real(imp),np.imag(imp)/abs(self.s) # R vs L

    def GBCD_mat(self, i_unk):
        s = self.s
        sn =0

        for i in range(len(self.element)):
            el = self.element[i]

            x = el[0]

            # G MATRIX
            if x == 'R' or x == 'C' or x == 'V' or x == 'L':
                n1 = self.pnode[el]
                n2 = self.nnode[el]
                #print n1,n2,el,self.value[el]
            # G_mat
            if x == 'R':
                g = float(1.0/self.value[el])
            elif x == 'C':
                g = s * float(self.value[el])

            if (x == 'R') or (x == 'C'):
                # If neither side of the element is connected to ground
                # then subtract it from appropriate location in matrix.
                if (n1 != 0) and (n2 != 0):
                    self.G[n1 - 1, n2 - 1] += -g
                    self.G[n2 - 1, n1 - 1] += -g

                # If node 1 is connected to ground, add element to diagonal of matrix
                if n1 != 0:
                    self.G[n1 - 1, n1 - 1] += g

                # same for for node 2
                if n2 != 0:
                    self.G[n2 - 1, n2 - 1] += g
            # B MATRIX
            if x == 'V':
                if i_unk > 1:  # is B greater than 1 by n?, V
                    if n1 != 0:
                        self.B[n1 - 1, sn] = 1
                        self.C[sn, n1 - 1] = 1

                    if n2 != 0:
                        self.B[n2 - 1, sn] = -1
                        self.C[sn, n2 - 1] = -1

                else:
                    if n1 != 0:
                        self.B[n1 - 1] = 1
                        self.C[n1 - 1] = 1

                    if n2 != 0:
                        self.B[n2 - 1] = -1
                        self.C[n2 - 1] = -1

                sn += 1  # increment source count
            if x == 'L':

                if i_unk > 1:  # is B greater than 1 by n?, L
                    self.D[sn, sn] += -s * float(self.value[el])

                    if n1 != 0:
                        self.B[n1 - 1, sn] = 1
                        self.C[sn, n1 - 1] = 1

                    if n2 != 0:
                        self.B[n2 - 1, sn] = -1
                        self.C[sn, n2 - 1] = -1

                else:
                    self.D[sn] += -s *float(self.value[el])

                    if n1 != 0:
                        self.B[n1 - 1] = 1
                        self.C[n1 - 1] = 1

                    if n2 != 0:
                        self.B[n2 - 1] = -1
                        self.C[n2 - 1] = -1

                sn += 1  # increment source count
                # check source count

            if x == 'M':  # M in H
                Mname = 'M' + el[1:]
                vn1, vn2, ind1_index = self.find_vname(
                    self.Lname1[el])
                vn1, vn2, ind2_index = self.find_vname(
                    self.Lname2[el])
                Mval = self.value[el]
                #print 'model',Mval, self.Lname1[el],self.Lname2[el]
                #Lval1=self.value[self.Lname1[el]]
                #Lval2 = self.value[self.Lname2[el]]
                #kval = round(Mval / sqrt(Lval1 * Lval2), 4)
                self.M[Mname] = Mval
                self.D[ind1_index, ind2_index] += -s * Mval  # s*Mxx
                self.D[ind2_index, ind1_index] += -s * Mval  # -s*Mxx
        # ERR CHECK
        if sn != i_unk:
            print('source number, sn={:d} not equal to i_unk={:d} in matrix B and C'.format(sn, i_unk))


    def V_mat(self, num_nodes):
        # generate the V matrix
        for i in range(num_nodes):
            self.V[i] = 'v{0}'.format(i + 1)

    def J_mat(self):
        # The J matrix is an mx1 matrix, with one entry for each i_unk from a source
        # sn = 0   # count i_unk source number
        # oan = 0   #count op amp number
        for i in range(len(self.cur_element)):
            # process all the unknown currents
            self.J[i] = 'I_{0}'.format(self.cur_element[i])

    def I_mat(self):
        # generate the I matrix, current sources have n2 = arrow end of the element
        for i in range(len(self.cur_element)):
            el = self.cur_element[i]
            n1 = self.cur_pnode[el]
            n2 = self.cur_nnode[el]
            # process all the passive elements, save conductance to temp value
            x = el[0]
            if x == 'I':
                g = float(self.cur_value[el])
                # sum the current into each node
                if n1 != 0:
                    self.I[n1 - 1] -= g
                if n2 != 0:
                    self.I[n2 - 1] += g

    def Ev_mat(self):
        # generate the E matrix
        sn = 0  # count source number
        for i in range(len(self.cur_element)):
            # process all the passive elements
            el = self.cur_element[i]
            x = el[0]
            if x == 'V':
                self.Ev[sn] = self.cur_value[el]
                sn += 1
            else:
                self.Ev[sn] = 0
                sn += 1

    def Z_mat(self):
        self.Z = np.concatenate((self.I[:], self.Ev[:]),axis=0)  # the + operator in python concatinates the lists
        # print self.Z  # display the Z matrix

    def X_mat(self):
        self.X = np.concatenate((self.V[:], self.J[:]), axis=0)# the + operator in python concatinates the lists

    def A_mat(self, num_nodes, i_unk):
        n = num_nodes
        m = i_unk
        self.A = np.zeros((m + n, m + n), dtype=np.complex_)
        for i in range(n):
            for j in range(n):
                self.A[i, j] = self.G[i, j]

        if i_unk > 1:
            for i in range(n):
                for j in range(m):
                    self.A[i, n + j] = self.B[i, j]
                    self.A[n + j, i] = self.C[j, i]

            for i in range(m):
                for j in range(m):
                    self.A[n + i, n + j] = self.D[i, j]

        if i_unk == 1:
            for i in range(n):
                self.A[i, n] = self.B[i]
                self.A[n, i] = self.C[i]



    def solve_iv(self):
        # initialize some symbolic matrix with zeros
        # A is formed by [[G, C] [B, D]]
        # Z = [I,E]
        # X = [V, J]
        num_nodes = max([max(self.nnode.values()),max(self.pnode.values())])
        self.V = np.chararray((num_nodes,1), itemsize=4)
        self.I = np.zeros((num_nodes, 1), dtype=np.complex_)
        self.G = np.zeros((num_nodes, num_nodes), dtype=np.complex_)  # also called Yr, the reduced nodal matrix

        # count the number of element types that affect the size of the B, C, D, E and J arrays
        # these are element types that have unknown currents
        i_unk = len(self.cur_element)
        # if i_unk == 0, just generate empty arrays

        self.B = np.zeros((num_nodes, i_unk), dtype=np.complex_)
        self.C = np.zeros((i_unk, num_nodes), dtype=np.complex_)
        self.D = np.zeros((i_unk, i_unk), dtype=np.complex_)
        self.Ev = np.zeros((i_unk, 1), dtype=np.complex_)
        self.J = np.chararray((i_unk,1),itemsize =10)
        _form_time = time.time()
        self.GBCD_mat(i_unk)
        #print "forming GBCD_mat time", time.time() - _form_time
        _form_time = time.time()

        self.J_mat()
        self.V_mat(num_nodes)
        self.I_mat()
        self.Ev_mat()
        self.Z_mat()
        self.X_mat()
        #print "forming J,V,I,Ev,Z,X matrices time", time.time() - _form_time
        _form_time = time.time()
        self.A_mat(num_nodes, i_unk)
        #print "forming A matrix time", time.time() - _form_time
        Z = self.Z
        A = self.A
        #print cd_A.dinv
        #A=cd_A.dinv*A
        #Z=cd_A.dinv*Z
        #print "conditioner matrix", numpy.linalg.cond(A)

        t = time.time()
        print "solving ...",self.freq,'Hz'
        method=1
        if method ==1:
            self.results= scipy.sparse.linalg.spsolve(A,Z)
        elif method ==2:
            self.results= np.linalg.solve(A,Z)
        elif method ==3:
            self.results = scipy.linalg.solve(A, Z)
        elif method ==4:
            self.results = np.linalg.lstsq(A, Z)[0]
        elif method ==5:
            A=np.matrix(A)
            Z=np.matrix(Z)
            self.results = np.linalg.inv(A)*Z
            self.results=np.squeeze(np.asarray(self.results))
        #print "solve", time.time() - t, "s"
        results_dict={}
        for i in range(len(self.X)):
            results_dict[str(self.X[i,0])]=self.results[i]
        self.results=results_dict
        #print "A matrix",A
        #print self.X
        #print "Z matrix",Z
        #print self.V_node

        #print self.results

    def solve_iv_ltspice(self,env=None,filename=None):
        work_space = os.getcwd()
        file =os.path.join(work_space,filename)
        LT_SPICE =LTSPICE(env,file)
        LT_SPICE.write2(circuit=self,frange=[self.freq+0.001,self.freq+0.001,1])
        raw_file = file.split('.')[0]
        raw_file += '.raw'
        #LT_SPICE.run()
        result = SimData(raw_file)
        lt_result = result.get_data_dict()
        #print lt_result
        results_dict = {}

        for i in range(len(self.X)):
            x = str(self.X[i,0])
            if x[0] == 'v':
                id = x[1:]
                node = list(id.zfill(4))
                node[0] = 'n'
                node = ''.join(node)
                ltspice_key= 'V'+'('+node+')'
                #print ltspice_key, lt_result[ltspice_key][0]

            elif x[0] == 'I':
                Lname = x[2:]
                ltspice_key = 'I' + '(' + Lname + ')'
                #print ltspice_key, lt_result[ltspice_key][0]

            results_dict[x] = lt_result[ltspice_key][0]
        #print self.results
        self.results = results_dict


    def solve_iv_hspice(self,env=None, filename=None,mode='AC'):
        num_nodes = max([max(self.nnode.values()), max(self.pnode.values())])
        i_unk = len(self.cur_element)
        self.Ev = np.zeros((i_unk, 1), dtype=np.complex_)
        self.J = np.chararray((i_unk, 1), itemsize=10)
        self.V = np.chararray((num_nodes, 1), itemsize=4)
        self.I = np.zeros((num_nodes, 1), dtype=np.complex_)
        self.J_mat()
        self.V_mat(num_nodes)
        self.I_mat()


        self.Ev_mat()
        self.Z_mat()
        self.X_mat()
        #print self.X
        work_space = os.getcwd()
        file = os.path.join(work_space, filename)
        H_SPICE = HSPICE(env,file)
        H_SPICE.write2(circuit=self, frange=[self.freq, self.freq, 2])
        raw_file = file.split('.')[0]
        raw_file += '.ac0'
        H_SPICE.run()
        data = H_SPICE.read_hspice(raw_file,self,mode)
        self.hspice_result = data
        #print "hspice",self.hspice_result


def validate_solver_simple():
    circuit =Circuit()
    circuit.assign_freq(1000)
    circuit._graph_add_comp('R1', 2, 4, 1e-3)
    circuit._graph_add_comp('R2', 3, 4, 1e-3)
    circuit._graph_add_comp('R3', 4, 0, 1000)

    circuit._graph_add_comp('L1', 1, 2, 1e-9)
    circuit._graph_add_comp('L2', 1, 3, 1e-9)
    circuit._graph_add_M('M12','L1', 'L2', 0.1e-9)
    circuit.indep_voltage_source(1,0,val=1)
    circuit.build_current_info()

    circuit.solve_iv()
    #circuit._compute_imp(1, 4, 4)

    circuit.solve_iv_hspice(filename='validate.sp',
                            env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
    #circuit._compute_imp(1, 4, 4)
def validatae_mutual():
    circuit = Circuit()
    circuit.assign_freq(1000)
    circuit._graph_add_comp('R1', 2, 4, 1e-3)
    circuit._graph_add_comp('R2', 3, 4, 1e-3)

def validate_solver_2():
    circuit = Circuit()
    circuit.assign_freq(1000)
    circuit._graph_add_comp('R1', 1, 0, 2)
    circuit._graph_add_comp('R2', 2, 3, 4)
    circuit._graph_add_comp('R3', 2, 0, 8)
    circuit.indep_voltage_source(1, 2, val=1,name='V1')
    circuit.indep_voltage_source(3, 0, val=1, name='V2')
    circuit.build_current_info()
    circuit.solve_iv()
    #circuit.solve_iv_hspice(filename='validate.sp',
    #                        env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
    print circuit.cur_element
    #circuit.results=circuit.hspice_result
    print circuit.results
if __name__ == "__main__":
    #validate_solver_simple()
    validate_solver_2()
