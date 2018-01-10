from sets import Set
import numpy as np
import constraint
import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt
from collections import defaultdict
import json

import scipy as sp
class constraintGraph:
    """
    the graph representation of constraints pertaining to cells and variables, informed by several different 
    sources
    """

    def __init__(self, vertices, edges):
        """
        create from a given set of edges and vertices
        vertexMatrix is a 2d list n vertices long that shows the connectivity between the vertices
        edges is just a set of edges
        zeroDimensionList is where, independent of orientation, the list index corresponds to the graph's orientation
        zero dimension representation. For example, in a very simple horizontally oriented 30 x30 plane,
        where the only cell has a lower left corner of 5,15 and an upper right corner of 10, 25, zeroDimensionList will 
        be as follows: [0]:0, [1]:5, [2]:10, [3]:30. Notice that it is arranged in increasing order, and we are only 
        concerned with the x values, since this is horizontally oriented.
        """
        self.vertexMatrixh = int[len(vertices)][len(vertices)]
        self.vertexMatrixv = int[len(vertices)][len(vertices)]
        self.edges = edges
        self.zeroDimensionList = []



    def __init__(self, name1, name2):
        """
        Default constructor
        """
        #self.vertexMatrixh = None
        #self.vertexMatrixv = None
        #self.vertexMatrixh = int[][len(vertices)]
        #self.vertexMatrixv = int[len(vertices)][len(vertices)]
        self.edgesv = []
        self.edgesh = []
        # self.zeroDimensionList = []
        self.zeroDimensionListh = []
        self.zeroDimensionListv = []

        self.name1 = name1
        self.name2 = name2
        self.paths_h=[]
        self.paths_v=[]
    '''
    def getVertexMatrixh(self):
        return self.vertexMatrixh
    def getVertexMatrixv(self):
        return self.vertexMatrixv
    '''
    def getNeighbors(self, vertex):
        """
        return the edge types and neighbors of the vertex passed in
        vertexMatrix shows the connectivity between the vertices, it is a 2d list n vertices long
        edges is just a set of edges
        zeroDimensionList is where, independent of orientation, the list index corresponds to the graph's orientation
        zero dimension representation. For example, in a very simple horizontally oriented 30 x30 plane,
        where the only cell has a lower left corner of 5,15 and an upper right corner of 10, 25, zeroDimensionList will 
        be as follows: [0]:0, [1]:5, [2]:10, [3]:30. Notice that it is arranged in increasing order, and we are only 
        concerned with the x values, since this is horizontally oriented.

        """
        return

    def getEdgeType(self, v1, v2):
        """
        return the edge type from v1 to v2. If negative, then the edge type is from v2 to v1
        """
        return

    def graphFromLayer(self, cornerStitch_h,cornerStitch_v):
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        """
        self.dimListFromLayer(cornerStitch_h,cornerStitch_v)
        #self.matrixFromDimList()
        self.setEdgesFromLayer(cornerStitch_h,cornerStitch_v)

    '''
    def matrixFromDimList(self):
        """
        initializes a N x N matrix of 0's as self's matrix object
        """
        #if cornerStitch.orientation == 'v':
        #n = len(self.zeroDimensionList)

        n1 = len(self.zeroDimensionListh)
        n2= len(self.zeroDimensionListv)
        self.vertexMatrixh=[[[] for i in range(n1)] for j in range(n1)]
        self.vertexMatrixv = [[[] for i in range(n2)] for j in range(n2)]
        #self.vertexMatrixh = np.zeros((n1, n1), np.int8)
        #self.vertexMatrixv = np.zeros((n2, n2), np.int8)

   
    def printVM(self,name):
        f = open(name, 'w')

        for i in self.vertexMatrixh:
            print >> f, i
        return
     '''
    def printVM(self,name1,name2):
        f1 = open(name1, 'w')
        #for k, v in self.vertexMatrixh.iteritems():
            #print >>f1,k, v
        for i in self.vertexMatrixh:
            print >> f1, i

        f2 = open(name2, 'w')
        #for k, v in self.vertexMatrixv.iteritems():
            #print >>f2,k, v
        for i in self.vertexMatrixv:
            print >> f2, i
        return

    
    def printZDL(self):
        index = 0
        for i in self.zeroDimensionList:
            print index, ": ", i
            index += 1

    '''
    def merge_dicts(self, dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        #print result
        return result
    '''
    """
    def setEdgesFromLayer(self, cornerStitch):
        
        #given a cornerStitch and orientation, set the connectivity matrix of this constraint graph
        
        
        if cornerStitch.orientation == 'v':
            print"stitchlist"
            for rect in cornerStitch.stitchList:
                origin = self.zeroDimensionList.index(rect.cell.y)
                # print"origin-",origin
                dest = self.zeroDimensionList.index(rect.getNorth().cell.y)
                self.vertexMatrix[origin][dest] = rect.getHeight()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                elif rect.cell.getType() == "SOLID":

                    self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))


        elif cornerStitch.orientation == 'h':
            print"stitchlist-h"
            for rect in cornerStitch.stitchList:
                origin = self.zeroDimensionList.index(rect.cell.x)
                # print"origin-",origin
                dest = self.zeroDimensionList.index(rect.getEast().cell.x)
                self.vertexMatrix[origin][dest] = rect.getWidth()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                elif rect.cell.getType() == "SOLID":
                    self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
            #####draw graph
    """
        #print"stitchList=", cornerStitch.stitchList


    def setEdgesFromLayer(self, cornerStitch_h,cornerStitch_v):
        #self.vertexMatrixh=defaultdict(lambda: defaultdict(list))
        #self.vertexMatrixv = defaultdict(lambda: defaultdict(list))
        n1 = len(self.zeroDimensionListh)
        n2 = len(self.zeroDimensionListv)
        self.vertexMatrixh = [[[] for i in range(n1)] for j in range(n1)]
        self.vertexMatrixv = [[[] for i in range(n2)] for j in range(n2)]
        for rect in cornerStitch_v.stitchList:

            if rect.cell.type=="SOLID":
                origin = self.zeroDimensionListh.index(rect.cell.x)
                dest = self.zeroDimensionListh.index(rect.getEast().cell.x)
                e=Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest))
                print"e=", Edge.getEdgeWeight(e,origin,dest)
                #self.edgesv.append(e)
                self.edgesh.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
                #self.vertexMatrixh[origin][dest].append((rect.getWidth()))
                self.vertexMatrixh[origin][dest].append(Edge.getEdgeWeight(e,origin,dest))

                #self.edgesh.append(Edge(origin, dest, constraint.constraint(rect.getWidth(), origin, dest)))#
            elif rect.cell.type=="EMPTY":
                origin = self.zeroDimensionListv.index(rect.cell.y)
                dest = self.zeroDimensionListv.index(rect.getNorth().cell.y)
                e = Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest))
                #self.edgesv.append(e)
                self.edgesv.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                self.vertexMatrixv[origin][dest].append(Edge.getEdgeWeight(e,origin,dest))
                #self.edgesv.append(Edge(origin, dest, constraint.constraint( rect.getHeight(), origin, dest)))

        for rect in cornerStitch_h.stitchList:
            if rect.cell.type == "SOLID":
                origin = self.zeroDimensionListv.index(rect.cell.y)
                dest = self.zeroDimensionListv.index(rect.getNorth().cell.y)
                e = Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest))
                #self.edgesh.append(e)
                self.edgesv.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
                #self.vertexMatrixv[origin][dest] = rect.getHeight()
                self.vertexMatrixv[origin][dest].append(e.getEdgeWeight(origin,dest))
                #self.edgesv.append(Edge(origin, dest, constraint.constraint(rect.getHeight() , origin, dest)))#

            elif rect.cell.type == "EMPTY":
                origin = self.zeroDimensionListh.index(rect.cell.x)
                dest = self.zeroDimensionListh.index(rect.getEast().cell.x)
                e = Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest))
                #self.edgesh.append(e)
                self.edgesh.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                #self.vertexMatrixh[origin][dest] = rect.getWidth()
                self.vertexMatrixh[origin][dest].append(e.getEdgeWeight(origin,dest))
                ##'minWidth'

                #self.edgesh.append(Edge(origin, dest, constraint.constraint( rect.getWidth(), origin, dest)))
        #print "verh=",dict(self.vertexMatrixh)
        #print(dict.__repr__(self.vertexMatrixh))
        #print "verv=", self.vertexMatrixv
    '''
    def dimListFromLayer(self, cornerStitch):
        """
        generate the zeroDimensionList from a cornerStitch         
        """
        pointSet = Set()  # this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
            for rect in cornerStitch.stitchList:
                pointSet.add(rect.cell.y)
            pointSet.add(cornerStitch.northBoundary.cell.y)

        elif cornerStitch.orientation == 'h':  # same for horizontal orientation
            for rect in cornerStitch.stitchList:
                pointSet.add(rect.cell.x)

            pointSet.add(cornerStitch.eastBoundary.cell.x)
        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionList = setToList
    
        ####

        # print"ZDL=",len(setToList)
     '''
    '''####final
    def dimListFromLayer(self, cornerStitch_h,cornerStitch_v):
        """
        generate the zeroDimensionList from a cornerStitch         
        """
        pointSet = Set() #this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        #if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
        for rect in cornerStitch_v.stitchList:
                pointSet.add(rect.cell.y)

        pointSet.add(cornerStitch_v.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionListvy = setToList
        print"vy=", setToList
        pointSet = Set()
        for rect in cornerStitch_v.stitchList:
                pointSet.add(rect.cell.x)

        pointSet.add(cornerStitch_v.eastBoundary.cell.x)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()
        self.zeroDimensionListvx = setToList
        print"vx=", setToList
        pointSet = Set()
        #elif cornerStitch.orientation == 'h':  # same for horizontal orientation
        for rect in cornerStitch_h.stitchList:
                pointSet.add(rect.cell.x)
        pointSet.add(cornerStitch_h.eastBoundary.cell.x)
        setToList = list(pointSet)
        setToList.sort()
        self.zeroDimensionListhx = setToList  # setting the list of orientation values to an ordered list
        print"hx=", setToList


        pointSet = Set()
        for rect in cornerStitch_h.stitchList:
                pointSet.add(rect.cell.y)

        pointSet.add(cornerStitch_h.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionListhy = setToList
        print"hy=", setToList


    '''
    def dimListFromLayer(self, cornerStitch_h,cornerStitch_v):
        """
        generate the zeroDimensionList from a cornerStitch
        """
        pointSet1 = Set() #this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        #if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
        for rect in cornerStitch_v.stitchList:
                pointSet1.add(rect.cell.y)

        pointSet1.add(cornerStitch_v.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        for rect in cornerStitch_h.stitchList:
                pointSet1.add(rect.cell.y)

        pointSet1.add(cornerStitch_h.northBoundary.cell.y)
        setToList = list(pointSet1)
        setToList.sort()
        #self.zeroDimensionListvy = setToList
        self.zeroDimensionListv = setToList
        #print"vy=", setToList
        pointSet = Set()
        for rect in cornerStitch_v.stitchList:
                pointSet.add(rect.cell.x)
        pointSet.add(cornerStitch_v.eastBoundary.cell.x)  # this won't be included in the normal list, so we do it here
        for rect in cornerStitch_h.stitchList:
                pointSet.add(rect.cell.x)
        pointSet.add(cornerStitch_h.eastBoundary.cell.x)
        setToList = list(pointSet)
        setToList.sort()
        self.zeroDimensionListh = setToList
        #print"vx=", setToList
    '''
    def toposort(self,graph):


        data = defaultdict(set)
        for x, y in graph.items():
            for z in y:
                data[z[0]].add(x)

        # Ignore self dependencies.
        for k, v in data.items():
            v.discard(k)
        # Find all items that don't depend on anything.
        extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
        # Add empty dependences where needed
        data.update({item: set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.items() if not dep)
            if not ordered:
                break
            yield ordered
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                    if item not in ordered}
        assert not data, "Cyclic dependencies exist among these items:\n%s" % '\n'.join(repr(x) for x in data.items())
    '''


    def cgToGraph_h(self,name):
        G2 = nx.MultiDiGraph()
        dictList1 = []
        print self.edgesh
        for foo in self.edgesh:
            dictList1.append(foo.getEdgeDict())
        print dictList1
        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1=d
        #print max(edge_labels1[(0,7)])

        nodes=[x for x in range(len(self.zeroDimensionListh))]
        G2.add_nodes_from(nodes)

        #print G2.nodes()
        #print G2.edges()
        #print"label=", edge_labels1
        label=[]
        for branch in edge_labels1:
            lst_branch=list(branch)
            data=[]


            for internal_edge in edge_labels1[branch]:
                #print lst_branch[0], lst_branch[1]
                #print internal_edge
                #if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})
                '''
                if (lst_branch[0], lst_branch[1], {'route': internal_edge}) not in data:
                data.append((lst_branch[0], lst_branch[1], {'route': internal_edge}))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})
                '''
            print data
            G2.add_weighted_edges_from(data)

        d = defaultdict(list)

        for i in label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        z = [(u, v, d['weight']) for u, v, d in G2.edges(data=True)]
        for n in G2.edges():
            n=list(n)
            print n
            print G2[n[0]][n[1]]

        edgeList = G2.edges()
        print "D",G2.get_edge_data(1,2)
        print"edgeList", edgeList
        A=nx.adjacency_matrix(G2)
        print "A=",A
        print(A.todense())
        ######
        '''
        N = G2.nodes()
        for x in N:
            for y in N:
                for z in N:
                    # print("(%d,%d,%d)" % (x,y,z))
                    if (x, y) != (y, z) and (x, y) != (x, z):
                        e1=(x,y)
                        e2=(y,z)
                        e3=(x,z)
                        #if G2.get_edge_data(*e1)== G2.get_edge_data(*e1)
                        if (x, y) in G2.edges and (y, z) in G2.edges and (x, z) in G2.edges() and G2.get_edge_data(*e1)== G2.get_edge_data(*e2)==G2.get_edge_data(*e3):
                            G2.remove_edge(x, z)
        '''
        #print"edgeList", edgeList
        '''
        for k in edge_labels1.keys():
            if k not in edgeList:
                del edge_labels1[k]
        '''
        f1 = open(name, 'w')
        #for i in edge_labels1:
        for i in z:
            print >> f1,i
            #print >> f1, i, edge_labels1[i]
        print list(nx.topological_sort(G2))
        n=list(G2.nodes())
        print "n=",n
        paths_h = self.FindingAllPaths_h(G2, n[0], n[-1])
        print "paths_h",paths_h
        f2 = open("paths_h.txt", "rb")
        for line in f2.read().splitlines():  # considering each line in file
            self.paths_h.append(line)
        #Route=[]
        #Route.append(list(self.paths_h[0]))


        paths=[json.loads(y) for y in self.paths_h]

        print paths
        '''
        dist = {}  # stores [node, distance] pair
        for node in nx.topological_sort(G2):
            # pairs of dist,node for all incoming edges

            # pairs = [(dist[v][0] + 1, v) for v in G1.pred[node]]
            #pairs = [(dist[v][0] + (edge_labels1[(v, node)][0]), v) for v in G2.pred[node]]
            pairs = [(dist[v][0]+max(edge_labels1[(v,node)]),v)  for v in G2.pred[node]]
            #print [[dist[v][0] + d['weight'], v] for v, u, d in G2.edges(data=True) for v in G2.pred[node]]
            print "node=", node, v
            value= [self.vertexMatrixh[v][node]for v in G2.pred[node]]
            print value
            #print "pred=", dict(G2.pred[node])
            #print "pred=", list(G2.pred[node][0]['weight'])

            print "pairs=", pairs
            if pairs:
                dist[node] = max(pairs, key=lambda x: x[0])
                print "dist[node]=", dist[node]
            else:
                dist[node] = (0, node)
            print "dist=", dist
            print dist.items()
            node, (length, _) = max(dist.items(), key=lambda x: x[1])
            print node, (length, _)
            path = []
            while length > 0:
                path.append(node)
                length, node = dist[node]

            print "list=",list(reversed(path))
        '''

        l=[]
        for path in paths:
            l.append (len(path))
        L=max(l)
        for path in paths:
            if(len(path))==L:
                p=path
        print"p=",p

        longest_path = [p]

        for j in range(len(paths)):
            print paths[j]

            if (not (set(paths[j]).issubset(set(p)))):

                if (paths[j] not in longest_path):
                    longest_path.append(paths[j])

        print "long=", longest_path
        #### finding new location of each vertex in longest paths (begin)########
        l = []
        for path in paths:
            l.append(len(path))
        L = max(l)
        for path in paths:
            if (len(path)) == L:
                p = path
        print"p=", p

        longest_path = [p]

        for j in range(len(paths)):
            print paths[j]

            if (not (set(paths[j]).issubset(set(p)))):

                if (paths[j] not in longest_path):
                    longest_path.append(paths[j])
        # print "LONG=",longest_path

        print "edge_labels", edge_labels1
        print "long=", longest_path
        dist = {}
        distance = set()
        for i in range(len(longest_path)):
            path = longest_path[i]
            print path
            for j in range(len(path)):
                node = path[j]
                if j > 0:
                    pred = path[j - 1]
                else:
                    pred = node
                print node, pred
                if node == 0:
                    dist[node] = (0, pred)
                    # distance.append((pred,node,0))
                    distance.add((pred, node, 0))
                else:
                    pairs = (dist[pred][0] + max(edge_labels1[(pred, node)]), pred)
                    print  max(edge_labels1[(pred, node)])
                    dist[node] = pairs
                    print dist[node][0]

                    distance.add((pred, node, pairs[0]))
                    # distance.append((pred,node,pairs[0]))

                    print "PAIR+", pairs
            print dist
            print "DISTANCE=",list(distance)
        #### finding new location of each vertex in longest paths (end)########


        self.drawGraph_h(name,G2,edge_labels1)

    def FindingAllPaths_h(self, G, start, end):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its
        minimum form
        """
        f1 = open("paths_h.txt", 'w')
        visited = [False] * (len(G.nodes()))
        path = []

        self.printAllPaths_h(G, start, end, visited, path,f1)


    def printAllPaths_h(self, G, start, end, visited, path,f1):
        visited[start] = True
        path.append(start)

        # If current vertex is same as destination, then print
        # current path[]

        if start == end:

            # for i in edge_labels1:
            print >> f1, path



            #self.paths_h.append(path)
            #print "self.paths_h",self.paths_h

            # paths.append(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex

            for i in G.neighbors(start):
                if visited[i] == False:
                    self.printAllPaths_h(G, i, end, visited, path,f1)

        # Remove current vertex from path[] and mark it as unvisited
        #print"PATHS=", paths
        path.pop()
        visited[start] = False


    def cgToGraph_v(self, name):
        G1 = nx.MultiDiGraph()
        dictList = []
        # print "checking edges"
        for foo in self.edgesv:
            dictList.append(foo.getEdgeDict())
            # print foo.getEdgeDict()
        print"dictlist=", dictList
        # print dictList
        ######
        d = defaultdict(list)
        for i in dictList:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels = d
        print "edge_labels",d
        nodes = [x for x in range(len(self.zeroDimensionListv))]
        G1.add_nodes_from(nodes)

        print G1.nodes()
        print G1.edges()

        label = []
        for branch in edge_labels:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels[branch]:
                print lst_branch[0], lst_branch[1]
                print internal_edge
                # if internal_edge not in label:
                # label.append(internal_edge)
                #if (lst_branch[0], lst_branch[1],  internal_edge) not in data:
                data.append((lst_branch[0],lst_branch[1],internal_edge))
                #data.append((lst_branch[0], lst_branch[1], {'route': internal_edge}))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})
            print"data=", data
            G1.add_weighted_edges_from(data)
            #G1.add_edges_from(data)
        print"label_=", label
        d = defaultdict(list)

        for i in label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels = d
        for n in G1.edges():
            n = list(n)
            print n
            print"w=", G1[n[0]]

        edgeList = G1.edges()
        z=[(u, v, d['weight'])for u, v, d in G1.edges(data=True)]
        print z
        #print "we=",[((u, v,), d['weight']) for u, v, d in G1.edges(data=True)]
        # edge_labels=
        print"label=", edge_labels
        # f1 = open(self.name1, 'w')


        A = nx.adjacency_matrix(G1)
        print "A=", A
        print(A.todense())

        f1 = open(name, 'w')

        #for i in edge_labels:
        for i in z:
            print >> f1, i
            #print >> f1, i, edge_labels[i]
        #print edge_labels

        self.drawGraph_v(name, G1, edge_labels)

        n=list(G1.nodes())
        self.FindingAllPaths_v(G1, n[0], n[-1],edge_labels)
        f = open("paths_v.txt", "rb")
        for line in f.read().splitlines():  # considering each line in file
            self.paths_v.append(line)
        print "PATHS_V+",self.paths_v
        paths = [json.loads(y) for y in self.paths_v]
        #print"paths=",(list(paths))
        #visited = [False]*(G1.nodes())
        #print G1.nodes
        '''
        for node in G1.nodes():
            print [v for u,v in G1.edges(node)]
            tree = nx.dfs_tree(G1,node)
            print"tree=",tree.edges()
        '''
        '''
        dist = {}  # stores {v : (length, u)}
        for v in nx.topological_sort(G1):
            print  G1.pred[v]
            #us = [(dist[u][0] + data.get(weight, default_weight), u)for u, data in G1.pred[v].items()]
            print  G1.pred[v].items()
            # Use the best predecessor if there is one and its distance is non-negative, otherwise terminate.
            maxu = max(us, key=lambda x: x[0]) if us else (0, v)
            dist[v] = maxu if maxu[0] >= 0 else (0, v)
        u = None
        v = max(dist, key=lambda x: dist[x][0])
        path = []
        while u != v:
            path.append(v)
            u = v
            v = dist[v][1]
        path.reverse()
       
        '''
        #### finding new location of each vertex in longest paths (begin)########
        l = []
        for path in paths:
            l.append(len(path))
        L = max(l)
        for path in paths:
            if (len(path)) == L:
                p = path
        print"p=", p

        longest_path = [p]

        for j in range(len(paths)):
            print paths[j]

            if (not (set(paths[j]).issubset(set(p)))):

                if (paths[j] not in longest_path):
                    longest_path.append(paths[j])
        #print "LONG=",longest_path

        print "edge_labels",edge_labels
        print "long=", longest_path
        dist = {}
        distance =set()
        for i in range(len(longest_path)):
            path=longest_path[i]
            print path
            for j in range(len(path)):
                node=path[j]
                if j>0:
                    pred=path[j-1]
                else:
                    pred=node
                print node,pred
                if node==0:
                    dist[node]=(0,pred)
                    #distance.append((pred,node,0))
                    distance.add((pred, node, 0))
                else:
                    pairs = (dist[pred][0] + max(edge_labels[(pred, node)]), pred)
                    print  max(edge_labels[(pred, node)])
                    dist[node]=pairs
                    print dist[node][0]

                    distance.add((pred, node, pairs[0]))
                    #distance.append((pred,node,pairs[0]))

                    print "PAIR+",pairs
            print dist
            print list(distance)
            #### finding new location of each vertex in longest paths (end)########
            '''
            for node in path:
                print "node=",node
                pairs = [(dist[v][0] + max(edge_labels[(v, node)], v) for v in path.pred[node]]
                print pairs
                if pairs:
                    dist[node] = max(pairs, key=lambda x: x[0])
                else:
                    dist[node] = (0, node)
            print dist
            '''
        '''
        dist = {}  # stores [node, distance] pair
        distance={}
        for node in nx.topological_sort(G1):
            # pairs of dist,node for all incoming edges
            # pairs = [(dist[v][0] + 1, v) for v in G1.pred[node]]
            pairs = [(dist[v][0] + max(edge_labels[(v, node)]), v) for v in G1.pred[node]]
            #pairs=[(dist[v][0]+max(edge_labels[(v, node)],v) for v in path]
            print "node=", node, v
            print "pairs=", pairs
            if pairs:
                l=[]
                for j,k in pairs:
                    l.append(j)

                maxv=max(l)
                y= [item for item in pairs if item[0] == maxv]
                print "Y=",y
                dist[node] =max(pairs, key=lambda x: x[0])
                distance[node]= y
               
                #dist[node].append(x)
                print distance[node]
            else:
                dist[node] = (0, node)
                distance[node]=[(0, node)]
                print "1"
                print dist[0][0]
            print "dist=", dist
            print"distance=",distance
            print dist.items()
            #node, (length, _) = max(dist.items(), key=lambda x: x[1])
            #print node, (length, _)
        '''

        #"""
        #print nx.algorithms.dag.dag_longest_path(G1)


    '''
    G = nx.Graph()

        it = np.nditer(self.vertexMatrixh, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G.add_edges_from([it.multi_index], weight = it[0])
#               # print it[0]
            it.iternext()
        return G
    def cgToGraph2(self):
        G = nx.Graph()

        it = np.nditer(self.vertexMatrixv, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G.add_edges_from([it.multi_index], weight=it[0])
                ## print it[0]
            it.iternext()
        return G
    '''
    '''
    def drawGraph(self):

        G1 = nx.DiGraph()

        it = np.nditer(self.vertexMatrix, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G1.add_edges_from([it.multi_index], weight = it[0])
                print it[0]
            it.iternext()

        dictList = []
        print "checking edges"
        for foo in self.edges:
            dictList.append(foo.getEdgeDict())
            print foo.getEdgeDict()
        print dictList
            #print dir(foo.getEdgeDict())
        # edge_labels[(foo.source, foo.dest): foo.constraint.getConstraintVal()]
        #for foo in self.edges:
        #    dictList.append(foo.getEdgeDict())

        edge_labels = self.merge_dicts(dictList)
        print "checking edge labels"
        print edge_labels
        for foo in edge_labels:
            print foo
#        edge_labels = dict([((u, v,), d)
#                            for u, v, d in self.edges])

        edge_colors = ['black' for edge in G1.edges()]
        #edge_colors1 = ['black' for edge in G.edges()]
        #for edge in G.edges():
           # print"constraint=", edge.getConstraint()

        #, edge_cmap = plt.cm.Reds - goes with nx.draw if needed
        pos = nx.shell_layout(G1)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        #nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name)
        #pylab.show()

   '''
    def FindingAllPaths_v(self,G,start,end,edge_labels):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its
        minimum form
        """
        f1 = open("paths_v.txt", 'w')

        # for i in edge_labels:

        visited = [False] * (len(G.nodes()))
        path=[]

        paths = []
        self.printAllPaths_v(G,start, end, visited, path,f1,edge_labels)
        #print "PATHS+",paths

    def printAllPaths_v(self,G, start,end, visited, path,f1,edge_labels):
        visited[start] = True
        path.append(start)

        # If current vertex is same as destination, then print
        # current path[]

        if start == end:
             print >> f1, path
            #paths.append(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            sum=0
            for i in G.neighbors(start):

                if visited[i] == False:
                    #sum += max(edge_labels[start][i])

                    self.printAllPaths_v(G,i,end, visited, path,f1,edge_labels)

            print "sum=",sum
        # Remove current vertex from path[] and mark it as unvisited

        path.pop()
        visited[start] = False



    def drawGraph_h(self,name,G2,edge_labels1):



        #edge_labels1 = self.merge_dicts(dictList1)
        edge_colors1 = ['black' for edge in G2.edges()]
        pos = nx.shell_layout(G2)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw_networkx_labels(G2, pos)
        nx.draw(G2, pos, node_color='red', node_size=300, edge_color=edge_colors1)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        #plt.show()
        plt.savefig(self.name1)
        plt.close()
        #pylab.show()


    def drawGraph_v(self,name2,G1,edge_labels):

        #######
        edge_colors = ['black' for edge in G1.edges()]
        pos = nx.shell_layout(G1)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        #app = Viewer(G1)
        #app.mainloop()
        plt.savefig(self.name2)
        plt.close()
        #pylab.show()




class multiCG():
    """
    Same as a constraint graph class, except this allows for multiple edges between nodes. Necessary for
    inserting custom constraints. 
    """
    def __init__(self, sourceGraph):
        """
        given a source graph, copy vertices and all existing nodes into a multigraph
        """
        self.diGraph1 = nx.MultiDiGraph()
        self.diGraph1.add_nodes_from(sourceGraph.cgToGraph1().nodes(data = True))
        self.diGraph1.add_edges_from(sourceGraph.cgToGraph1().edges(data = True))
        self.diGraph2 = nx.MultiDiGraph()
        self.diGraph2.add_nodes_from(sourceGraph.cgToGraph2().nodes(data=True))
        self.diGraph2.add_edges_from(sourceGraph.cgToGraph2().edges(data=True))
    def addEdge(self, source, dest, constraint):
        self.diGraph.add_edge(source, dest, constraint, weight = constraint.getConstraintVal())

    def drawGraph1(self):
        G = self.diGraph1
        edge_Labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])
        #for foo in list(edge_Labels):
            #print foo

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(self.diGraph1)
        nx.draw_networkx_edge_labels(self.diGraph1, pos, edge_labels = edge_Labels)
        nx.draw_networkx_labels(self.diGraph1, pos)
        nx.draw(self.diGraph1, pos, node_color='white', node_size=300, edge_color=edge_colors,arrows=True)

        pylab.show()
    def drawGraph2(self):
        G = self.diGraph2
        edge_Labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])
        #for foo in list(edge_Labels):
            #print foo

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(self.diGraph2)
        nx.draw_networkx_edge_labels(self.diGraph2, pos, edge_labels = edge_Labels)
        nx.draw_networkx_labels(self.diGraph2, pos)
        nx.draw(self.diGraph2, pos, node_color='white', node_size=300, edge_color=edge_colors,arrows=True)

        pylab.show()

    def edgeReduce(self):
        """Eliminate redundant edges"""

    def vertexReduce(self):
        """Eliminate redundant vertices"""
        return

class Edge():


    def __init__(self, source, dest, constraint):
        self.source = source
        self.dest = dest
        self.constraint = constraint
        self.setEdgeDict()

    def getConstraint(self):
        return self.constraint

    def setEdgeDict(self):
        self.edgeDict = {(self.source, self.dest): self.constraint.getConstraintVal()}
        #self.edgeDict = {(self.source, self.dest): self.constraint.constraintval}

    def getEdgeDict(self):
        return self.edgeDict
    def getEdgeWeight(self,source,dest):
        return self.getEdgeDict()[(self.source, self.dest)]

    def printEdge(self):
        print "s: ", self.source, "d: ", self.dest, "con = ", self.constraint.printCon()
