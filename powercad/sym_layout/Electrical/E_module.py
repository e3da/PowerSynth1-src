'''
@author: Quang Le
This is a simple representation of a module in pads and rect
'''
import networkx as nx
from powercad.sym_layout.Electrical.E_plate import *
from powercad.sym_layout.Electrical.E_hierarchy import *
from powercad.parasitics.models_bondwire import wire_inductance, wire_partial_mutual_ind, wire_resistance, \
    ball_mutual_indutance, ball_self_inductance
import math
import csv
import numpy as np


class E_comp:
    def __init__(self, sheet=[], conn=[], val=[], type="passive"):
        '''
        Args:
            sheet: list of sheet for device's pins
            conn: list if sheet.nets pair that connected
            val: corresponded R,L,C value for each branch
            type: by default passive.
        '''
        self.sheet = sheet
        self.net_graph = nx.Graph()
        self.conn = conn  # based on net name of the sheets
        self.passive = val  # value of each edge, if -1 then 2 corresponding node in graph will be merged
        # else: this is a dict of {'R','L','C'}
        self.type = type
        self.update_nodes()

    def update_nodes(self):
        for sh in self.sheet:
            self.net_graph.add_node(sh.net, node=sh)
            sh.component = self

    def update_edges(self):
        for c, v in zip(self.conn, self.passive):
            self.net_graph.add_edge(c[0], c[1], edge_data=v)

    def build_graph(self):
        self.update_edges()


class E_wires(E_comp):
    def __init__(self, wire_radius=0, num_wires=0, wire_dis=0, start=None, stop=None, wire_model=None, frequency=10e3,
                 p=2.65e-8, circuit=None):
        '''

        Args:
            wire_radius: radius of each wire
            wire_dis: wire distance in mm
            num_wires: number of wires
            start: start sheet
            stop: stop sheet
            wire_model: if this is an interpolated model
            frequency: frequency of operation
            p: material resistivity (default: Al)
        '''
        E_comp.__init__(self, sheet=[start, stop], conn=[[start.net, stop.net]], type="wire_group")
        self.num_wires = num_wires
        self.f = frequency
        self.r = wire_radius
        self.p = p
        self.d = wire_dis
        self.circuit = circuit

        if wire_model == None:
            self.mode = 'analytical'
        else:
            self.mode = 'interpolated'

    def update_wires_parasitic(self):
        '''
        Update the parasitics of a wire group. Return single R,L,C result

        '''
        c_s = self.sheet[0].get_center()
        c_e = self.sheet[1].get_center()
        length = math.sqrt((c_s[0] - c_e[0]) ** 2 + (c_s[1] - c_e[1]) ** 2)

        start = 1
        mid = 2

        end = 0
        if self.mode == 'analytical':
            group = {}  # all mutual inductance pair
            R_val = wire_resistance(f=self.f, r=self.r, p=self.p, l=length) * 1e-3
            L_val = wire_inductance(r=self.r, l=length) * 1e-9
            for i in range(self.num_wires):
                R_name = 'R{0}'.format(i)
                L_name = 'L{0}'.format(i)
                self.circuit._graph_add_comp(name=R_name, pnode=start, nnode=mid, val=R_val)
                self.circuit._graph_add_comp(name=L_name, pnode=mid, nnode=end, val=L_val)
                for j in range(self.num_wires):
                    if i != j and not ((i, j) in group):
                        group[(i, j)] = None  # save new key
                        group[(j, i)] = None  # save new key
                        distance = abs(j - i) * self.d
                        L1_name = 'L{0}'.format(i)
                        L2_name = 'L{0}'.format(j)
                        M_name = 'M{0}{1}'.format(i, j)
                        M_val = wire_partial_mutual_ind(length, distance) * 1e-9
                        self.circuit._graph_add_M(M_name, L1_name, L2_name, M_val)
            self.circuit.assign_freq(self.f)
            self.circuit.indep_voltage_source(1, 0, val=1)
            self.circuit.build_current_info()
            self.circuit.solve_iv()
            R, L = self.circuit._compute_imp2(1, 0)

            print R, L
            self.net_graph.add_edge(self.sheet[0].net, self.sheet[1].net, edge_data={'R': R, 'L': L, 'C': None})
            # print self.net_graph.edges(data=True)

    def build_graph(self):
        self.update_wires_parasitic()


class E_sd_balls(E_comp):
    def __init__(self, ball_radi=None, ball_grid=[], ball_height=None, pitch=None, start=None, stop=None,
                 ball_model=None, frequency=100e3, p=2.65e-8, circuit=None):
        '''

        Args:
            ball_radi: radius of one ball
            ball_grid: a numpy array represent a ball grid
            ball_height: solder thickness
            pitch: solder ball pitch
            start: start sheet
            stop: stop sheet
            ball_model: if this is an interpolated model
            frequency: frequency of operation
            p: material resistivity (default: Al)
        '''
        E_comp.__init__(self, sheet=[start, stop], conn=[[start.net, stop.net]], type="ball_group")
        self.h = ball_height
        self.f = frequency
        self.r = ball_radi
        self.p = p
        self.pitch = pitch
        self.circuit = circuit
        self.grid = ball_grid
        if ball_model == None:
            self.mode = 'analytical'
        else:
            self.mode = 'interpolated'

    def update_sb_parasitic(self):
        '''
        Update the parasitics of a ball group. Return single R,L,C result
        '''
        start = 1
        mid = 2
        end = 0
        if self.mode == 'analytical':
            R_val = wire_resistance(f=self.f, r=self.r, p=self.p, l=self.h) * 1e-3
            L_val = ball_self_inductance(r=self.r, h=self.h)
            names = []
            id = []
            for r in range(self.grid.shape[0]):
                for c in range(self.grid.shape[1]):
                    if self.grid[r, c] == 1:  # if there is a solder ball in this location
                        R_name = 'R{0}{1}'.format(r, c)
                        L_name = 'L{0}{1}'.format(r, c)
                        self.circuit._graph_add_comp(name=R_name, pnode=start, nnode=mid, val=R_val)
                        self.circuit._graph_add_comp(name=L_name, pnode=mid, nnode=end, val=L_val)
                        names.append('L{0}{1}'.format(r, c))
                        id.append((r, c))
                    else:
                        continue

            for i in range(len(names)):
                for j in range(len(names)):
                    L1 = names[i]
                    L2 = names[j]
                    if L1 != L2:
                        id1 = names.index(L1)
                        id1 = id[id1]
                        id2 = names.index(L2)
                        id2 = id[id2]
                        dx = abs(id1[0] - id2[0]) * self.pitch
                        dy = abs(id1[1] - id2[1]) * self.pitch
                        distance = math.sqrt(dx ** 2 + dy ** 2)
                        M_name = 'M{0}{1}'.format(id1, id2)
                        M_val = ball_mutual_indutance(h=self.h, r=self.r, d=distance)
                        self.circuit._graph_add_M(M_name, L1, L2, M_val)


                    else:
                        continue

            self.circuit.assign_freq(self.f)
            self.circuit.indep_voltage_source(1, 0, val=1)
            self.circuit.build_current_info()
            self.circuit.solve_iv()
            R, L = self.circuit._compute_imp2(1, 0)
            self.net_graph.add_edge(self.sheet[0].net, self.sheet[1].net, edge_data={'R': R, 'L': L, 'C': None})
            # print self.net_graph.edges(data=True)
            print R, L

    def build_graph(self):
        self.update_sb_parasitic()


class E_stack():
    '''
    A Simple Layer Stack for Electrical Parasitics computation
    '''

    def __init__(self, file):
        self.csvfile = file
        self.layer_id = []  # layer ID
        self.thick = {}  # layer thickness in mm
        self.z = {}  # layer z in mm
        self.mat = {}  # material conductivity in Ohm.m

    def load_layer_stack(self):
        with open(self.csvfile) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.layer_id.append(row['ID'])
                self.thick[row['ID']] = float(row['thick'])
                self.z[row['ID']] = float(row['z'])
                self.mat[row['ID']] = float(row['mat'])

    def id_by_z(self, z):
        for i in self.layer_id:
            if z == self.z[i]:
                return i


class E_module:
    def __init__(self, sheet=[], plate=[], layer_stack=None, components=[]):
        '''
        Representation of a power module in multiple sheets and plates
        Args:
            sheet: A data structure for devices pad and bondwire pad (zero thickness)
            plate: A data structure for conductor.
            layer_stack: A layer stack for material properties and thickness information
        '''
        self.sheet = sheet  # patches list Sheet objects
        self.plate = plate  # list of conductor 3D plates
        self.layer_stack = layer_stack  # Will be used later to store layer info
        self.group = {}  # trace islands in any layer
        self.components = components
        if self.components != []:
            self.unpack_comp()

    def unpack_comp(self):
        for comp in self.components:
            self.sheet += comp.sheet

    def form_group(self):
        '''
        Form island of traces (self.plate), this is used to define correct mesh boundary for each trace group
        Returns: a dictionary of group ID for plates

        '''
        # "Sourec: https://stackoverflow.com/questions/27016803/find-sets-of-disjoint-sets-from-a-list-of-tuples-or-sets-in-python" a=[]
        a = []
        traces = self.plate
        if len(traces) > 1:
            for t1 in traces:
                for t2 in traces:
                    if t1.intersects(t2):
                        a.append([t1, t2])
            d = {tuple(t): set(t) for t in a}  # forces keys to be unique
            while True:
                for tuple_, set1 in d.items():
                    try:
                        match = next(k for k, set2 in d.items() if k != tuple_ and set1 & set2)
                    except StopIteration:
                        # no match for this key - keep looking
                        continue
                    else:
                        d[tuple_] = set1 | d.pop(match)
                        break
                else:
                    # no match for any key - we are done!
                    break
            output = sorted(tuple(s) for s in d.values())

        else:
            output = [[traces[0]]]

        for i in range(len(output)):
            self.group[i] = output[i]

    def split_layer_group(self):
        plate_group = self.group
        self.plate = []
        self.group_layer_dict = {}
        splitted_group = {}
        for group in plate_group.keys():  # First collect all xs and ys coordinates
            counter = 0
            xs = []
            ys = []
            splitted_group[group] = []
            z = plate_group[group][0].z
            if self.layer_stack != None:
                self.group_layer_dict[group] = self.layer_stack.id_by_z(z)
            dz = plate_group[group][0].dz
            n = plate_group[group][0].n
            for plate in plate_group[group]:
                trace = plate.rect
                xs += [trace.left, trace.right]
                ys += [trace.top, trace.bottom]
            # final sort and clean up
            xs = list(set(xs))
            ys = list(set(ys))
            xs.sort()
            ys.sort()

            ls = range(len(xs) - 1)  # left
            ls = [xs[i] for i in ls]
            ls.sort()
            rs = range(1, len(xs))  # right
            rs = [xs[i] for i in rs]
            rs.sort()
            bs = range(len(ys) - 1)  # bot
            bs = [ys[i] for i in bs]
            bs.sort()
            ts = range(1, len(ys))  # top
            ts = [ys[i] for i in ts]
            ts.sort()

            for left, right in zip(ls, rs):
                for bot, top in zip(bs, ts):
                    midx = left + (right - left) / 2
                    midy = bot + (top - bot) / 2
                    split = False
                    for plate in plate_group[group]:
                        cur_plate = plate

                        trace = plate.rect
                        if trace.encloses(midx, midy):
                            split = True
                            break

                    if split:
                        newRect = Rect(top=top, bottom=bot, left=left, right=right)
                        newPlate = E_plate(rect=newRect, z=z, dz=dz, n=n)
                        newPlate.name = 'T' + str(counter) + '_(' + 'isl' + str(group) + ')'
                        counter += 1

                        splitted_group[group].append(newPlate)
                        if self.layer_stack != None:
                            self.group_layer_dict[group] = self.layer_stack.id_by_z(z)
                        self.plate.append(newPlate)
                        # else:
                        #    splitted_group[group].append(cur_plate)
        self.group = splitted_group


def test1():
    r1 = Rect(14, 10, 0, 10)
    R1 = E_plate(rect=r1, n=(0, 0, 1), z=0, dz=0.2)
    r2 = Rect(10, 0, 0, 5)
    R2 = E_plate(rect=r2, z=0, dz=0.2)
    r3 = Rect(14, 0, 10, 14)
    R3 = E_plate(rect=r3, z=0, dz=0.2)
    r4 = Rect(-1, -6, -5, 20)
    R4 = E_plate(rect=r4, z=0, dz=0.2)
    r5 = Rect(9, 0, 7, 8)
    R5 = E_plate(rect=r5, z=0, dz=0.2)
    r6 = Rect(10, -1, -5, -1)
    R6 = E_plate(rect=r6, z=0, dz=0.2)
    r7 = Rect(10, -1, 15, 20)
    R7 = E_plate(rect=r7, z=0, dz=0.2)

    sh1 = Rect(7, 5, 11, 13)
    S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 12, 13)
    S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 11.25, 11.75)
    S3 = Sheet(rect=sh3, net='M1_G', type='point', n=(0, 0, 1), z=0.4)

    sh1 = Rect(7, 5, 1, 3)
    S4 = Sheet(rect=sh1, net='M2_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 1, 2)
    S5 = Sheet(rect=sh2, net='M2_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 2.25, 2.75)
    S6 = Sheet(rect=sh3, net='M2_G', type='point', n=(0, 0, 1), z=0.4)
    sh7 = Rect(14, 12, 4, 11)
    S7 = Sheet(rect=sh7, net='DC_plus', type='point', n=(0, 0, 1), z=0.2)
    sh8 = Rect(-4, -6, 4, 11)
    S8 = Sheet(rect=sh8, net='DC_minus', type='point', n=(0, 0, 1), z=0.2)

    sh9 = Rect(2, 1, 7.25, 7.75)
    S9 = Sheet(rect=sh9, net='Gate', type='point', n=(0, 0, 1), z=0.2)

    sh10 = Rect(6, 5, 7.25, 7.35)
    S10 = Sheet(rect=sh10, net='bwG_m2', type='point', n=(0, 0, 1), z=0.2)

    sh11 = Rect(6, 5, 7.65, 7.75)
    S11 = Sheet(rect=sh11, net='bwG_m1', type='point', n=(0, 0, 1), z=0.2)

    sh12 = Rect(6, 5, 15.25, 15.35)
    S12 = Sheet(rect=sh12, net='bwS_m1', type='point', n=(0, 0, 1), z=0.2)

    sh13 = Rect(6, 5, -1.35, -1.25)
    S13 = Sheet(rect=sh13, net='bwS_m2', type='point', n=(0, 0, 1), z=0.2)

    new_module = E_module(plate=[R1, R2, R3, R4, R5, R6, R7],
                          sheet=[S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13])
    new_module.form_group()
    new_module.split_layer_group()

    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(-5, 20)
    ax.set_ylim3d(-5, 20)
    ax.set_zlim3d(0, 5)
    plot_rect3D(rect2ds=new_module.plate + new_module.sheet, ax=ax)

    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    hier.tree.update_digraph()
    fig, ax = plt.subplots()
    hier.tree.plot_tree(ax)
    plt.show()


def test_comp():
    # Test draw a mosfet:
    sh1 = Rect(7, 5, 11, 13)
    S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 12, 13)
    S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 11.25, 11.75)
    S3 = Sheet(rect=sh3, net='M1_G', type='point', n=(0, 0, 1), z=0.4)
    comp = E_comp(sheet=[S1, S2, S3], conn=[['M1_D', 'M1_S']], val=[{'R': 200e-3, 'L': 0, 'C': 10e-12}], type='a')
    comp.build_graph()
    '''
    fig = plt.figure(1)

    pos = nx.shell_layout(comp.net_graph)
    nx.draw_networkx_nodes(comp.net_graph,pos=pos)
    nx.draw_networkx_edges(comp.net_graph, pos=pos)
    nx.draw_networkx_labels(comp.net_graph,pos)
    nx.draw_networkx_edge_labels(comp.net_graph,pos)
    '''
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(9, 14)
    ax.set_ylim3d(5, 8)
    ax.set_zlim3d(0, 0.4)
    plot_rect3D(rect2ds=comp.sheet, ax=ax)
    plt.show()


def test_comp2():
    # http://www.ti.com/lit/ds/symlink/ucc5350.pdf
    # A SiC Gate driver

    sh1 = Rect(7, 5, 11, 13)
    S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    sh2 = Rect(6.5, 5.5, 12, 13)
    S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25, 5.75, 11.25, 11.75)
    S3 = Sheet(rect=sh3, net='M1_G', type='point', n=(0, 0, 1), z=0.4)
    comp = E_comp(sheet=[S1, S2, S3], conn=[['M1_D', 'M1_S']], val=[{'R': 200e-3, 'L': 0, 'C': 10e-12}], type='a')
    comp.build_graph()


def load_e_stack_test(file):
    es = E_stack(file=file)
    es.load_layer_stack()


def test_bondwires_group():
    R7 = Rect(49, 48, 34, 35)
    R8 = Rect(39, 38, 34, 35)
    nets = ['bw1_s', 'bw1_e']
    rects_sh = [R7, R8]
    sheets = [Sheet(rect=sh, net=nets[rects_sh.index(sh)], type='point', n=(0, 0, 1), z=0.4) for sh in rects_sh]
    wire_group = E_wires(0.1, 4, 0.1, sheets[0], sheets[1], None, 10e3)
    wire_group.update_wires_parasitic()


def test_solderball_group():
    from powercad.Spice_handler.spice_export.PEEC_num_solver import Circuit
    import time
    R7 = Rect(49, 48, 34, 35)
    nets = ['source_z1', 'source_z2']
    sheet1 = Sheet(rect=R7, net=nets[0], type='point', n=(0, 0, 1), z=0.2)
    sheet2 = Sheet(rect=R7, net=nets[0], type='point', n=(0, 0, 1), z=0.4)
    ball_grid = np.random.choice([0, 1], size=(3,3), p=[0. / 10, 10. / 10])
    print ball_grid
    dis = [0.508, 0.762, 1.016, 1.27]
    for d in dis:
        ball_group = E_sd_balls(ball_radi=0.2032, ball_grid=ball_grid, ball_height=0.2032, pitch=d, start=sheet1,
                                stop=sheet2, frequency=500e3,
                                circuit=Circuit())
        ball_group.build_graph()


if __name__ == '__main__':
    # test_comp()
    # load_e_stack_test("C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\ELayerStack//2_layers.csv")
    # test_bondwires_group()
    test_solderball_group()
