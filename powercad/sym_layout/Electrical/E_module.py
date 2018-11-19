'''
@author: Quang Le
This is a simple representation of a module in pads and rect
'''
import networkx as nx
from powercad.sym_layout.Electrical.E_plate import *
from powercad.sym_layout.Electrical.E_hierarchy import *
import csv


class Component:
    def __init__(self, sheet=[], conn=[],val=[],type="p"):
        self.sheet=sheet
        self.net_graph=nx.Graph()
        self.conn=conn # based on net name of the sheets
        self.passive = val # value of each edge, if -1 then 2 corresponding node in graph will be merged
                       # else: this is a dict of {'R','L','C'}
        self.type=type
        self.update_nodes()

    def update_nodes(self):
        for sh in self.sheet:
            self.net_graph.add_node(sh.net,node=sh)
            sh.component = self
    def update_edges(self):
        for c,v in zip(self.conn,self.passive):
            if callable(v): # check if this is a function type
                self.net_graph.add_edge(c[0], c[1], attr_dict=v)
            else:
                self.net_graph.add_edge(c[0],c[1],attr_dict=v)
    def build_graph(self):
        self.update_edges()

class E_stack():
    '''
    A Simple Layer Stack for Electrical Parasitics computation
    '''

    def __init__(self,file):
        self.csvfile = file
        self.layer_id=[] # layer ID
        self.thick={} # layer thickness in mm
        self.z={}   # layer z in mm
        self.mat={} # material conductivity in Ohm.m
    def load_layer_stack(self):
        with open(self.csvfile) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.layer_id.append(row['ID'])
                self.thick[row['ID']]= float(row['thick'])
                self.z[row['ID']] = float(row['z'])
                self.mat[row['ID']] = float(row['mat'])
        print self.layer_id
        print self.thick
        print self.z
        print self.mat

    def id_by_z(self,z):
        for i in self.layer_id:
            if z == self.z[i]:
                return i


class E_module:

    def __init__(self,sheet=[],plate=[],layer_stack=None,components=[]):
        '''
        Representation of a power module in multiple sheets and plates
        Args:
            sheet:
            plate:
            layer_stack:
        '''
        self.sheet = sheet # patches list Sheet objects
        self.plate = plate # list of conductor 3D plates
        self.layer_stack= layer_stack # Will be used later to store layer info
        self.group={} # trace islands in any layer
        self.components = components
        if self.components!=[]:
            self.unpack_comp()

    def unpack_comp(self):
        for comp in self.components:
            self.sheet+=comp.sheet

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
        plate_group=self.group
        self.plate=[]
        self.group_layer_dict={}
        splitted_group = {}
        for group in plate_group.keys():  # First collect all xs and ys coordinates
            counter=0
            xs = []
            ys = []
            splitted_group[group] = []
            z= plate_group[group][0].z
            if self.layer_stack != None:
                self.group_layer_dict[group] = self.layer_stack.id_by_z(z)
            dz = plate_group[group][0].dz
            n= plate_group[group][0].n
            for plate in plate_group[group]:
                trace=plate.rect
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

                        trace=plate.rect
                        if trace.encloses(midx, midy):
                            split = True
                            break

                    if split:
                        newRect = Rect(top=top, bottom=bot, left=left, right=right)
                        newPlate = E_plate(rect=newRect,z=z,dz=dz,n=n)
                        newPlate.name = 'T'+str(counter)+'_('+'isl'+str(group)+')'
                        counter+=1

                        splitted_group[group].append(newPlate)
                        if self.layer_stack != None:
                            self.group_layer_dict[group] = self.layer_stack.id_by_z(z)
                        self.plate.append(newPlate)
                    #else:
                    #    splitted_group[group].append(cur_plate)
        self.group=splitted_group

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
    r6 = Rect(10,-1,-5,-1)
    R6 = E_plate(rect=r6, z=0, dz=0.2)
    r7 = Rect(10, -1, 15, 20)
    R7 = E_plate(rect=r7, z=0, dz=0.2)

    sh1 = Rect(7, 5, 11, 13)
    S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1),z=0.2)
    sh2 = Rect(6.5, 5.5, 12, 13)
    S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
    sh3 = Rect(6.25,5.75,11.25,11.75)
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

    new_module = E_module(plate=[R1,R2,R3,R4,R5,R6,R7],sheet=[S1,S2,S3,S4,S5,S6,S7,S8,S9,S10,S11,S12,S13])
    new_module.form_group()
    new_module.split_layer_group()

    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(-5, 20)
    ax.set_ylim3d(-5, 20)
    ax.set_zlim3d(0, 5)
    plot_rect3D(rect2ds=new_module.plate+new_module.sheet,ax=ax)

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
    comp =Component(sheet=[S1,S2,S3],conn=[['M1_D','M1_S']],val=[{'R': 200e-3, 'L': 0, 'C': 10e-12}],type='a')
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
    ax.set_zlim3d(0,0.4)
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
    comp = Component(sheet=[S1, S2, S3], conn=[['M1_D', 'M1_S']], val=[{'R': 200e-3, 'L': 0, 'C': 10e-12}], type='a')
    comp.build_graph()

def load_e_stack_test(file):
    es=E_stack(file=file)
    es.load_layer_stack()

if __name__ == '__main__':
    #test_comp()
    load_e_stack_test("C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\ELayerStack//2_layers.csv")


