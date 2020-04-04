import numpy as np
import matplotlib.pyplot as plt
import time
import scipy
import warnings
import sys
warnings.filterwarnings("ignore")
class diag_prec:
    def __init__(self, A):
        self.shape = A.shape
        n = self.shape[0]
        self.dinv = np.empty(n)
        for i in range(n):
            self.dinv[i] = 1.0 / A[i, i]

    def precon(self, x, y):
        np.multiply(x, self.dinv, y)


class RL_circuit():
    def __init__(self):
        '''
        Accelerated RL computation, no Capacitance
        '''
        self.num_rl = 0  # number of RL elements
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
        self.L_id = {} # A relationship between Lname and current id in the matrix
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
        self.M = None
        self.M_t = None
        self.D = None
        self.V = None
        self.J = None
        self.Ii = None
        self.Vi = None
        self.Z = None
        self.X = None
        self.A = None
        self.Mutual = {}  # Dictionary for coupling pairs
        # List of circuit equations:
        self.func = []
        self.solver = None
        self.max_net_id = 0 # maximum used net id value
        self.results_dict={}
        self.node_dict={}
        self.Rport=50
        self.freq = 1000

        self.cur_src=[]
        self.src_pnode = {}
        self.src_nnode = {}
        self.src_value = {}


        # Counting number of elements
        self.L_count = 0
        self.R_count = 0
        self.C_count = 0
        self.M_count = 0

    '''
    def __del__(self):
        del self.pnode
        del self.nnode
        del self.cp_node
        del self.cn_node
        del self.vout
        del self.value
        del self.Vname
        # Handle Mutual inductance
        del self.Lname1
        del self.Lname2
        del self.L_id  # A relationship between Lname and current id in the matrix
        del self.element
        del self.node_dict
        del self.results_dict
    '''
    def assign_freq(self,freq=1000):
        self.freq = freq
        self.s = 2 * freq * np.pi * 1j

    def _graph_add_comp(self,name, pnode, nnode, val):
        self.element.append(name)
        self.pnode[name] = pnode
        self.nnode[name] = nnode
        self.value[name] = val
        # name,pnode,nnode,val

    def _graph_add_M(self,name,L1_name,L2_name,val):
        self.element.append(name)
        self.Lname1[name] = L1_name
        self.Lname2[name] = L2_name
        self.value[name] = float(val)

    def indep_current_source(self, pnode=0, nnode=0, val=1,name='Is'):
        self.cur_src.append(name)
        self.src_pnode[name] = pnode
        self.src_nnode[name] = nnode
        self.src_value[name] = float(val)

    def indep_voltage_source(self, pnode=0, nnode=0, val=1000, name='Vs'):
        self.V_node=pnode
        self.element.append(name)
        self.pnode[name] = pnode
        self.nnode[name] = nnode
        self.value[name] = float(val)


    def _add_termial(self, node, ground=0,val=1e-4 + 1e-10j):
        #newport = self.node_dict[node]
        Equiv_name = 'Bt_' + str(node)
        self._graph_add_comp(Equiv_name, node, ground, val)
    def refresh(self):
        self.cur_element = []
        self.cur_pnode = {}
        self.cur_nnode = {}
        self.cur_value = {}
        self.element = []
        self.pnode = {}
        self.nnode = {}
        self.cp_node = {}
        self.cn_node = {}
        self.vout = {}
        self.value = {}
        self.Vname = {}
        # Handle Mutual inductance
        self.Lname1 = {}
        self.Lname2 = {}
        self.L_id = {}  # A relationship between Lname and current id in the matrix
        self.max_net_id = 0  # maximum used net id value
        self.results_dict = {}
        self.node_dict = {}

        self.L_count = 0
        self.R_count = 0
        self.C_count = 0
        self.M_count = 0
    def _graph_read(self,graph):
        '''
        this will be used to read mesh graph and forming matrices
        :param lumped_graph: networkX graph from PowerSynth
        :return: update self.net_data
        '''

        for edge in graph.edges(data=True):
            n1 = edge[0]
            n2 = edge[1]
            edged = edge[2]['data']
            data = edged.data
            node1 = graph.nodes[n1]['node']
            pos1 = node1.pos
            node2 = graph.nodes[n2]['node']

            pos2 = node2.pos
            node1 = n1
            node2 = n2
            p_node=node1
            n_node=node2
            if data['type']=='trace':
                if data['ori'] == 'h':
                    # make sure the node with smaller x will be positive
                    if pos1[0]>pos2[0]:
                        n_node = node1
                        p_node = node2
                elif data['ori'] == 'v':
                    # make sure the node with smaller y will be positive
                    if pos1[1] > pos2[1]:
                        n_node = node1
                        p_node = node2
            elif data['type'] == 'hier':
                if abs(pos1[0] - pos2[0]) > abs(pos1[1] - pos2[1]):
                    if pos1[0] > pos2[0]:
                        n_node = node1
                        p_node = node2
                elif abs(pos1[1] - pos2[1]) > abs(pos1[0] - pos2[0]):
                    if pos1[1] > pos2[1]:
                        n_node = node1
                        p_node = node2

            if p_node not in list(self.node_dict.keys()):
                self.node_dict[p_node] = p_node
            if n_node not in list(self.node_dict.keys()):
                self.node_dict[n_node] = n_node
            ''' Since an edge will have R and L together we can group them in one value to reduce the matrix'''
            RLname = edge[2]['data'].name
            #print edge
            #print p_node,n_node
            #raw_input()
            Rval = edge[2]['res']
            Lval = edge[2]['ind']
            self.L_count+=1
            self.R_count+=1
            branch_val = 1j*Lval+Rval
            self._graph_add_comp("B{0}".format(RLname), p_node, n_node, branch_val)

    def m_graph_read(self,m_graph,debug =False):
        '''

        Args:
            m_graph: is the mutual coupling info from mesh

        Returns:
            update M elemts
        '''
        if debug ==True:
            all_vals = []
            for edge in m_graph.edges(data=True):
                M_val = edge[2]['attr']['Mval']
                #if not M_val in all_vals:
                all_vals.append(M_val)
            all_vals.sort()
            plt.bar(np.arange(len(all_vals)),all_vals,align='center', alpha=0.5)
            plt.show()
        else:
            for edge in m_graph.edges(data=True):
                M_val = edge[2]['attr']['Mval']
                #if M_val<1e-10:
                #    M_val = 5e-11

                L1_name = 'B' + str(edge[0])
                L2_name = 'B' + str(edge[1])
                M_name='M'+'_'+L1_name+'_'+L2_name
                self._graph_add_M(M_name,L1_name,L2_name,M_val)
                self.M_count+=1
    def refresh_current_info(self):
        '''
        Refresh current info to initial state
        '''
        self.cur_element=[]
        self.cur_pnode={}
        self.cur_nnode = {}
        self.cur_value = {}

    def build_current_info(self):
        ''' collect all branches'''
        for i in range(len(self.element)):
            # process all the elements creating unknown currents
            el = self.element[i]
            x = self.element[i][0]  # get 1st letter of element name
            if (x == 'B'or x=='V'): # add this for current through source or (x == 'V'):
                self.cur_element.append(el)
                self.cur_pnode[el] = self.pnode[el]
                self.cur_nnode[el] = self.nnode[el]
                self.cur_value[el] = self.value[el]
                if x =='B':
                    self.L_id[el]=i




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

    def matrix_formation(self, i_unk):
        s = self.s
        sn =0

        for i in range(len(self.element)):
            el = self.element[i]

            x = el[0]
            # node info for elements
            if x!='M':
                n1 = self.pnode[el]
                n2 = self.nnode[el]

            if (x == 'C'):
                g = s * self.value[el]
                # If neither side of the element is connected to ground
                # then subtract it from appropriate location in matrix.
                if (n1 != 0) and (n2 != 0):
                    self.G[n1 - 1, n2 - 1] += -g
                    self.G[n2 - 1, n1 - 1] += -g

                # If node 1 is connected to ground, add element to diagonal of matrix
                if n1 == 0:
                    self.G[n1 - 1, n1 - 1] += g

                # same for for node 2
                if n2 == 0:
                    self.G[n2 - 1, n2 - 1] += g
            # B  C MATRIX

            if x == 'V':
                if i_unk > 1:  # is B greater than 1 by n?, V
                    if n1 != 0:
                        self.M[n1 - 1, sn] = 1
                        self.M_t[sn, n1 - 1] = 1

                    if n2 != 0:
                        self.M[n2 - 1, sn] = -1
                        self.M_t[sn, n2 - 1] = -1

                else:
                    if n1 != 0:
                        self.M[n1 - 1] = 1
                        self.M_t[n1 - 1] = 1

                    if n2 != 0:
                        self.M[n2 - 1] = -1
                        self.M_t[n2 - 1] = -1

                sn += 1  # increment source count

            if x == 'B':

                if i_unk > 1:  # is B greater than 1 by n?, L
                    imp = -s * np.imag(self.value[el]) - np.real(self.value[el])
                    self.D[sn, sn] += imp
                    if n1 != 0:
                        self.M[n1 - 1, sn] = 1
                        self.M_t[sn, n1 - 1] = 1

                    if n2 != 0:
                        self.M[n2 - 1, sn] = -1
                        self.M_t[sn, n2 - 1] = -1

                else:
                    self.D[sn] += -s * np.imag(self.value[el]) - np.real(self.value[el])

                    if n1 != 0:
                        self.M[n1 - 1] = 1
                        self.M_t[n1 - 1] = 1

                    if n2 != 0:
                        self.M[n2 - 1] = -1
                        self.M_t[n2 - 1] = -1

                sn += 1  # increment source count
                # check source count

            if x == 'M':  # M in H
                Mname = 'M' + el[1:]
                ind1_index = self.L_id[self.Lname1[el]]
                ind2_index = self.L_id[self.Lname2[el]]
                L1_val = self.value[self.Lname1[el]]
                L2_val = self.value[self.Lname2[el]]

                Mval = self.value[el]
                k = Mval / np.sqrt(L1_val * L2_val)

                self.Mutual[Mname] = Mval
                #print Mval,'nH'
                self.D[ind1_index, ind2_index] += -s * Mval
                self.D[ind2_index, ind1_index] += -s * Mval

        # ERR CHECK
        if sn != i_unk:
            print(('source number, sn={:d} not equal to i_unk={:d} in matrix B and C'.format(sn, i_unk)))


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

    def Ii_mat(self):
        if self.cur_src!=[]:
            for i in range(len(self.cur_src)):
                el = self.cur_src[i]
                n1 = self.src_pnode[el]
                n2 = self.src_nnode[el]
                g = float(self.src_value[el])
                # sum the current into each node
                if n1 != 0:
                    self.Ii[n1 - 1] += -g
                if n2 != 0:
                    self.Ii[n2 - 1] += -g
    def Vi_mat(self):
        # generate the E matrix
        sn = 0  # count source number
        for i in range(len(self.cur_element)):
            # process all the passive elements
            el = self.cur_element[i]
            x = el[0]
            if x == 'V':
                print ("added V source")
                self.Vi[sn] = self.cur_value[el]
                sn += 1
            else:
                self.Vi[sn] = 0
                sn += 1

    def Z_mat(self):
        self.Z = np.concatenate((self.Ii[:], self.Vi[:]),axis=0)
        # print self.Z  # display the Z matrix

    def X_mat(self):
        self.X = np.concatenate((self.V[:], self.J[:]), axis=0)

    def A_mat(self, num_nodes, i_unk):
        n = num_nodes
        m = i_unk
        self.A = np.zeros((m + n, m + n), dtype=np.complex_)
        first_row = np.concatenate((self.G,self.M),axis= 1) # form [G , M]
        second_row = np.concatenate((self.M_t, self.D), axis=1)  # form [M_t , D]
        self.A = np.concatenate((first_row,second_row),axis=0)

    #precision = 10
    #fp = open('memory_profiler_basic_mean.log', 'w+')
    #@profile(precision=precision, stream=fp)
    def solve_iv(self,mode = 0):
        debug=False
        # initialize some symbolic matrix with zeros
        # A is formed by [[G, M] [M_t, D]]
        # Z = [I,E]
        # X = [V, J]
        num_nodes = max([max(self.nnode.values()),max(self.pnode.values())])
        # Forming matrices
        self.V = np.chararray((num_nodes,1), itemsize=4)
        self.Ii = np.zeros((num_nodes, 1), dtype=np.complex_)
        self.G = np.zeros((num_nodes, num_nodes), dtype=np.complex_)  # also called Yr, the reduced nodal matrix
        i_unk = len(self.cur_element)
        self.M = np.zeros((num_nodes, i_unk), dtype=np.complex_)
        self.M_t = np.zeros((i_unk, num_nodes), dtype=np.complex_)
        self.D = np.zeros((i_unk, i_unk), dtype=np.complex_)
        self.Vi = np.zeros((i_unk, 1), dtype=np.complex_)
        self.J = np.chararray((i_unk,1),itemsize =10)
        self.matrix_formation(i_unk)
        # Output preparation
        self.J_mat()
        self.V_mat(num_nodes)
        self.Ii_mat()
        self.Vi_mat()
        self.Z_mat()
        self.X_mat()

        self.A_mat(num_nodes, i_unk)
        if mode ==0:
            case = "no_current"
        elif mode == 1:
            case = "no_voltage"
        elif mode ==2:
            case = "full_eval"
        if case == "no_current":
            Z = self.Ii
            Dinv = -np.linalg.inv(self.D)
            A = np.linalg.multi_dot([self.M,Dinv,self.M_t])
        elif case == "full_eval":
            Z = self.Z
            A = self.A
        elif case =="no_voltage":
            Z = self.Vi
            A = self.D

        t = time.time()
        #self.debug_singular_mat_issue(A) # uncomment to debug

        method=1

        if method ==1:
            self.results= scipy.sparse.linalg.spsolve(A,Z)
        elif method ==2:
            print(A)
            self.results= np.linalg.solve(A,Z)
        elif method ==3:
            self.results = scipy.linalg.solve(A, Z)
        elif method ==4:
            self.results = np.linalg.lstsq(A, Z)[0]
        elif method ==5: # direct inverse method.
            self.results = np.linalg.inv(A)*Z
            self.results=np.squeeze(np.asarray(self.results))
        #print(("solve", time.time() - t, "s"))

        #print np.shape(self.A)
        #print "RESULTS",self.results
        if debug: # for debug and time analysis
            print(('RL', np.shape(A)))
            np.savetxt("M.csv", self.M_t, delimiter=",")
            np.savetxt("Mt.csv", self.M, delimiter=",")
            np.savetxt("D.csv", self.D, delimiter=",")
            print((self.J))
            print((self.V))
            print((self.Z))

            np.savetxt("M.csv", self.M_t, delimiter=",")
            np.savetxt("A.csv", self.A, delimiter=",")
            np.savetxt("Z.csv", Z, delimiter=",")
            print(("solve", time.time() - t, "s"))
        self.results_dict={}
        rlmode=True

        if case == "no_current":
            names = self.V
        elif case =='full_eval':
            names = self.X
        elif case == "no_voltage":
            names = self.J
            print((self.J.shape))
        if rlmode:
            for i in range(len(names)):
                self.results_dict[names[i,0].decode()]=self.results[i]

        self.results=self.results_dict
        #print "R,L,M", self.R_count,self.L_count,self.M_count
    def debug_singular_mat_issue(self,mat_A):
        '''
        :param mat_A: a square matrix to analyze
        :return: a debug sequence. Use pycharm debugger for better view
        '''
        if not (np.linalg.cond(mat_A) < 1 / sys.float_info.epsilon):
            print(("machine epsilon", sys.float_info.epsilon))
            print(("A is singular, check it", np.linalg.cond(mat_A), "1/eps", 1 / sys.float_info.epsilon))
            N = mat_A.shape[0]
            V=np.zeros((N,N)) # Make a matrix V for view, to see if a row or a collumn is all 0
            for r in range(N):
                for c in range(N):
                    if int(mat_A[r,c]) != 0:
                        V[r,c] =1
            #print(V)
            #print((np.where(~V.any(axis=1))[0]))


def test_RL_circuit1():
    print("new method")
    circuit = RL_circuit()
    circuit._graph_add_comp('B1', 1, 2, 1 + 1e-9j)
    circuit._graph_add_comp('B2', 3, 4, 1 + 1e-9j)
    #circuit._graph_add_comp('B3', 2, 0, 1 + 1e-9j)
    circuit._graph_add_M('M12', 'B1', 'B2', 0.2e-9)

    circuit.indep_current_source(1,0,1)
    #circuit.indep_voltage_source(1, 0, 1)

    circuit.assign_freq(10000)
    circuit.build_current_info()
    circuit.solve_iv()
    print((circuit.results))



    imp = (circuit.results['v1'])# / circuit.results['I_Vs']
    print((np.real(imp), np.imag(imp) / circuit.s))


def test_RL_circuit2():
    circuit = RL_circuit()
    circuit._graph_add_comp('B1', 1, 2, 1 + 1e-9j)
    circuit._graph_add_comp('B2', 2, 3, 1 + 1e-9j)
    circuit._graph_add_comp('B3', 1, 3, 1 + 1e-9j)
    circuit._graph_add_comp('B4', 3, 0, 1 + 1e-9j)

    circuit._graph_add_M('M13', 'B1', 'B3', 1e-9)
    circuit._graph_add_M('M12', 'B2', 'B3', 1e-9)

    # circuit._graph_add_comp('C1', 1, 0, 1e-12)
    # circuit._graph_add_comp('C2', 2, 0, 2e-12)
    circuit.indep_current_source(0, 1, 1)
    circuit.assign_freq(100)
    circuit.build_current_info()
    circuit.solve_iv()
    print((circuit.results))

    imp = (circuit.results['v1']) / 1
    print((np.real(imp), np.imag(imp) / circuit.s))

if __name__ == "__main__":
    #validate_solver_simple()
    #validate_solver_2()
    test_RL_circuit1()