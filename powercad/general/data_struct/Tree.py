
#@author qmle
import matplotlib.cm as cm
import networkx as nx
from matplotlib.colors import Normalize
from collections import OrderedDict
''' This is a general Tree structure'''


def mesh(name=None):
    print "performed mesh on", name


class dummy_trace():
    def __init__(self,name):
        self.name =name

class T_Node():
    def __init__(self,data=None,name=None,type=None,tree=None):
        self.parent=None # Parent pointer
        self.depth=0
        self.name=name
        self.data=data
        self.nodes= OrderedDict() # dictionary for children
        self.type=type # Quick description of this data type
        self.rank=0
        self.tree = tree
        self.tree.nodes.append(self)
    def update_rank(self):
        self.rank=self.parent.rank+1
        if self.rank > self.tree.max_rank:
            self.tree.max_rank=self.rank
    def add_children(self,nodes):
        for n in nodes:
            n.parent=self
            n.depth=self.depth+1
            self.nodes[n.name]=n

    def add_child(self,node):
        node.parent = self
        node.depth = self.depth + 1
        self.nodes[node.name]=node

    def remove_all_children(self):
        self.nodes= OrderedDict()

    def remove_child(self,name):
        self.nodes.pop(name,None)

    def __del__(self):
        self.nodes.clear()
        del self.nodes

class Tree():
    def __init__(self):
        self.nodes=[]
        self.root = T_Node(None,'ROOT','ROOT',tree=self)
        self.digraph=nx.DiGraph()
        self.max_rank =0
        self.cm=cm.jet
    def __del__(self):
        del self.nodes
        del self.root
        self.digraph.clear()
        del self.digraph

    def search_tree(self,start_node=None,kname='ROOT'):
        ''' Perform a recursive search for node with name kname'''
        result=None
        for n in start_node.nodes.keys():
            if kname in start_node.nodes.keys():
                result = start_node.nodes[kname]
            else:
                node = start_node.nodes[n]
                #print " Searching for children of ", node.name
                result = self.search_tree(node, kname)

        if result!=None:
            return result
    def remove(self,start_node=None, node_name=None):
        for n in start_node.nodes.keys():
            if node_name in start_node.nodes.keys():
                del start_node.nodes[node_name]
                return
            else:
                node = start_node.nodes[n]
                self.remove(node, node_name)
    def print_tree(self,x=None):
        # x is starting node
        if x ==None:
            x=self.root
        if x.nodes!={}:
            for n in x.nodes.keys():
                node = x.nodes[n]
                b=''
                for n in range(node.depth-1):
                    b+='+....+'
                print b, node.name
                self.print_tree(node)
        else:
            return

    def apply_func(self,func=None,start_node=None):
        if start_node!=None:
            for n in start_node.nodes.keys():
                node = start_node.nodes[n]
                if node.data!=None:
                    func(node.name)
                else:
                    self.test_mesh(func,node)


    def update_digraph(self):
        for n in self.nodes:
            self.digraph.add_node(n.name,rank=n.rank)
        for n in self.nodes:
            for c in n.nodes.keys():
                self.digraph.add_edge(n.name, c)

    def plot_tree(self,ax=None):
        G = self.digraph
        self.update_color()
        pos = self.update_pos()
        nx.draw_networkx_nodes(G, pos, node_size=500,ax=ax,node_color=self.clist,font_size=16,weight='bold',alpha=0.7)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='black',width=2, arrows=True,ax=ax)

    def update_pos(self):
        pos = OrderedDict()
        for i in range(self.max_rank + 1):
            counter = 0
            for n in self.digraph.nodes(data=True):
                node = n[0]
                rank = n[1]['rank']
                if i == rank:
                    x=counter
                    y = self.max_rank+1 -rank
                    pos[node]=(x,y)
                    counter +=1
        return pos
    def update_color(self):
        ''' for plotting only based on rank'''
        self.clist=[]
        norm_rank = Normalize(0, self.max_rank)
        for n in self.digraph.nodes(data=True):
            rank = n[1]['rank']
            for i in range(self.max_rank + 1):
                if i == rank:
                    color = self.cm(norm_rank(i))
                    self.clist.append(color)
if __name__ == "__main__":
    T1 = Tree()
    # Layer 1
    node1 = T_Node(name='G1')
    node2 = T_Node(name='G2')
    node3 = T_Node(name='G3')
    # Layer 2
    node4 = T_Node(name='T1',data=dummy_trace('T1'))
    node5 = T_Node(name='T2', data=dummy_trace('T2'))
    node6 = T_Node(name='T3', data=dummy_trace('T3'))
    node7 = T_Node(name='T4', data=dummy_trace('T4'))
    node8 = T_Node(name='T5', data=dummy_trace('T5'))
    node9 = T_Node(name='T6', data=dummy_trace('T6'))
    node10 = T_Node(name='T7', data=dummy_trace('T7'))
    node11 = T_Node(name='T8', data=dummy_trace('T8'))
    # Layer 3
    node12 = T_Node(name='L1')
    node13 = T_Node(name='L2')
    node14 = T_Node(name='bw1')
    node15 = T_Node(name='bw2')

    # ADD Groups
    T1.root.add_child(node1)
    T1.root.add_child(node2)
    T1.root.add_child(node3)
    # Trace group 1
    node1.add_child(node4)
    node1.add_child(node5)
    node1.add_child(node6)
    # Trace group 2
    node2.add_child(node7)
    node2.add_child(node8)
    node2.add_child(node9)
    node2.add_child(node10)
    # Trace group 3
    node3.add_child(node11)
    # Trace1
    node4.add_child(node12)
    # Trace 7
    node10.add_child(node13)
    # Trace 3
    node6.add_child(node14)
    # Trace 5
    node8.add_child(node15)

    T1.print_tree()
    node=T1.search_tree(T1.root,'T1')
    print "FOUND IT", node.name
    node2.remove_all_children()
    T1.print_tree()
    T1.apply_func(func=mesh,start_node=T1.root)
