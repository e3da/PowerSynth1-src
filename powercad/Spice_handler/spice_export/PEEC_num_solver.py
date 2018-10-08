import os
import time
import pandas as pd
from sympy import *
from IPython.display import display
import scipy
from scipy.sparse.linalg import gmres
from powercad.Spice_handler.spice_export.LTSPICE import *
from powercad.Spice_handler.spice_export.HSPICE import *
from decida.Data import *
from powercad.Spice_handler.spice_export.raw_read import *
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
        # Data frame for circuit info
        self.df_circuit_info = pd.DataFrame(
            columns=['element', 'p node', 'n node', 'cp node', 'cn node', 'Vout', 'value', 'Vname', 'Lname1', 'Lname2'])
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
        self.df_uk_current = pd.DataFrame(columns=['element', 'p node', 'n node', 'value'])
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
        self.line_cnt=0
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


    def form_report(self):
        print "Dataframe for circuit info:"
        display(self.df_circuit_info)
        print "Dataframe for Current branches info:"
        display(self.df_uk_current)


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

        for edge in graph.edges(data=True):
            n1 = edge[0]
            n2 = edge[1]
            edged = edge[2]['data']
            data = edged.data
            node1 = graph.node[n1]['node']
            pos1 = node1.pos
            node2 = graph.node[n2]['node']
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

            RLCname = edge[2]['data'].name
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
            self._graph_add_comp(Rname.format(RLCname), net1, int_net, val)
            if node2 not in self.node_dict.keys():
                net2 = net_id
                self.node_dict[node2] = net2
                net_id += 1
            else:
                net2 = self.node_dict[node2]

            # add an inductor between internal net and net2
            val = edge[2]['ind']
            #print Lname.format(RLCname)
            self._graph_add_comp(Lname.format(RLCname), int_net, net2, val)

            #
            #if 'cap' in edge[2].keys():  # IF this branch has a capacitance
            #    self._graph_add_comp(Cname.format(RLCname), net2, 0, val)

        self.line_cnt = len(self.element)
    def m_graph_read(self,m_graph):
        '''

        Args:
            m_graph: is the mutual coupling info from mesh

        Returns:
            update M elemts
        '''
        self.line_cnt = len(self.element)
        for edge in m_graph.edges(data=True):
            M_val = edge[2]['attr']['Mval']
            L1_name = 'L' + str(edge[0])
            L2_name = 'L' + str(edge[1])
            M_name='M'+'_'+L1_name+'_'+L2_name
            #print M_name, M_val,L1_name,L2_name
            self._graph_add_M(M_name,L1_name,L2_name,M_val)
        self.line_cnt = len(self.element)

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
        index = self.line_cnt
        # add current source to source_node
        self.V_node=source_node
        source_net =self.node_dict[source_node]
        self.indep_voltage_source(source_net,0,val=volt,name=vname)
        self.line_cnt+=1


    def _add_ports(self,node):
        newport = self.node_dict[node]
        R_name = 'R' + str(newport)
        self._graph_add_comp( R_name, newport, 0, self.Rport)
        self.line_cnt += 1

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
        return np.real(imp),np.imag(imp)#/abs(self.s) # R vs L

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
                print 'model',Mval, self.Lname1[el],self.Lname2[el]
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
        print num_nodes

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
        t = time.time()
        print "solving ..."
        method=5
        if method ==1:
            self.results= scipy.sparse.linalg.spsolve(A,Z,permc_spec='MMD_ATA')
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
        print "solve", time.time() - t, "s"
        results_dict={}
        for i in range(len(self.X)):
            results_dict[str(self.X[i,0])]=self.results[i]
        self.results=results_dict
        #print "A matrix",A
        #print self.X
        #print "Z matrix",Z
        #print self.V_node

        print self.results

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


    def solve_iv_hspice(self,env=None, filename=None):
        work_space = os.getcwd()
        file = os.path.join(work_space, filename)
        H_SPICE = HSPICE(env,file)
        H_SPICE.write2(circuit=self, frange=[self.freq, self.freq, 2])
        raw_file = file.split('.')[0]
        raw_file += '.ac0'
        H_SPICE.run()
        d=Data()
        item=d.read_hspice(raw_file)
        print item
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
    #circuit._compute_imp(1,4,4)
    circuit.solve_iv_hspice(filename='validate.sp',
                            env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
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

if __name__ == "__main__":
    validate_solver_simple()
    #validate_solver_2()
