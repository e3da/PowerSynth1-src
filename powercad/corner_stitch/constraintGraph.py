from sets import Set
import numpy as np
import constraint
import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt

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
        self.vertexMatrix = int[len(vertices)][len(vertices)]
        self.edges = edges
        self.zeroDimensionList = []


    def __init__(self,name1,name2):
        """
        Default constructor
        """
        self.vertexMatrixh = None
        self.vertexMatrixv = None
        self.edgesv = []
        self.edgesh = []
        #self.zeroDimensionList = []
        self.zeroDimensionListhx = []
        self.zeroDimensionListhy = []
        self.zeroDimensionListvx = []
        self.zeroDimensionListvy = []
        self.name1 = name1
        self.name2 = name2

    def getVertexMatrixh(self):
        return self.vertexMatrixh
    def getVertexMatrixv(self):
        return self.vertexMatrixv

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
    '''
    def graphFromLayer(self, cornerStitch):
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        """
        self.dimListFromLayer(cornerStitch)
        self.matrixFromDimList()
        self.setEdgesFromLayer(cornerStitch)
    '''
    def graphFromLayer(self, cornerStitch1,cornerStitch2):
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        """
        self.dimListFromLayer(cornerStitch1,cornerStitch2)
        self.matrixFromDimList()
        self.setEdgesFromLayer(cornerStitch1,cornerStitch2)
    '''
    def matrixFromDimList(self):
        """
        initializes a N x N matrix of 0's as self's matrix object
        """
        #if cornerStitch.orientation == 'v':
        n = len(self.zeroDimensionList)

        #n1 = len(self.zeroDimensionListhx)
        #n2= len(self.zeroDimensionListhy)
        #n=max(n1,n2)
        # self.vertexMatrix = np.zeros((n, n), np.int8)

        self.vertexMatrix = np.zeros((n, n), np.int8)

    '''
    def matrixFromDimList(self):
        """
        initializes a N x N matrix of 0's as self's matrix object
        """
        #if cornerStitch.orientation == 'v':
        #n = len(self.zeroDimensionList)

        n1 = len(self.zeroDimensionListhx)
        n2= len(self.zeroDimensionListhy)
        #n=max(n1,n2)
        # self.vertexMatrix = np.zeros((n, n), np.int8)

        self.vertexMatrixh = np.zeros((n1, n1), np.int8)
        self.vertexMatrixv = np.zeros((n2, n2), np.int8)
    '''
    def printVM(self,name):
        f = open(name, 'w')

        for i in self.vertexMatrixh:
            print >> f, i
        return
    '''
    def printVM(self,name1,name2):
        f1 = open(name1, 'w')

        for i in self.vertexMatrixh:
            print >> f1, i
        f2 = open(name2, 'w')

        for i in self.vertexMatrixv:
            print >> f2, i
        return

    def printZDL(self):
        index = 0
        for i in self.zeroDimensionList:
            print index, ": ", i
            index += 1

    def merge_dicts(self, dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

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


    def setEdgesFromLayer(self, cornerStitch1,cornerStitch2):
        #if cornerStitch.orientation == 'v':
        for rect in cornerStitch2.stitchList:
            #rect.cell.printCell(True,True)
            if rect.cell.type=="SOLID":
                origin = self.zeroDimensionListvx.index(rect.cell.x)
                #print"origin-",origin
                dest = self.zeroDimensionListvx.index(rect.getEast().cell.x)
                self.vertexMatrixh[origin][dest] = rect.getWidth()
                self.edgesh.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
            elif rect.cell.type=="EMPTY":
                origin = self.zeroDimensionListvy.index(rect.cell.y)
                #print"origin-",origin
                dest = self.zeroDimensionListvy.index(rect.getNorth().cell.y)
                self.vertexMatrixv[origin][dest] = rect.getHeight()
                self.edgesv.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
            #print"origin-", rect.getHeight()
            #if rect.cell.getType() == "EMPTY":
                #self.edges.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
            #elif rect.cell.getType() == "SOLID":
                #self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
        #elif cornerStitch.orientation == 'h':
        print"stitchlist-h"

        for rect in cornerStitch1.stitchList:
            if rect.cell.type == "SOLID":
                origin = self.zeroDimensionListhy.index(rect.cell.y)
                print"origins-",origin
                dest = self.zeroDimensionListhy.index(rect.getNorth().cell.y)
                print"dests-", dest
                self.vertexMatrixv[origin][dest] = rect.getHeight()
                self.edgesv.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))
            elif rect.cell.type == "EMPTY":
                print"rect=",rect.cell.x
                origin = self.zeroDimensionListhx.index(rect.cell.x)
                print"origine-",origin
                dest = self.zeroDimensionListhx.index(rect.getEast().cell.x)
                print"deste-", dest
                self.vertexMatrixh[origin][dest] = rect.getWidth()
                self.edgesh.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
            #if rect.cell.getType() == "EMPTY":

            #elif rect.cell.getType() == "SOLID":
                #self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))



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
    def dimListFromLayer(self, cornerStitch1,cornerStitch2):
        """
        generate the zeroDimensionList from a cornerStitch         
        """
        pointSet = Set() #this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        #if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
        for rect in cornerStitch2.stitchList:
                pointSet.add(rect.cell.y)

        pointSet.add(cornerStitch2.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionListvy = setToList
        print"vy=", setToList
        pointSet = Set()
        for rect in cornerStitch2.stitchList:
                pointSet.add(rect.cell.x)

        pointSet.add(cornerStitch2.eastBoundary.cell.x)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()
        self.zeroDimensionListvx = setToList
        print"vx=", setToList
        pointSet = Set()
        #elif cornerStitch.orientation == 'h':  # same for horizontal orientation
        for rect in cornerStitch1.stitchList:
                pointSet.add(rect.cell.x)
        pointSet.add(cornerStitch1.eastBoundary.cell.x)
        setToList = list(pointSet)
        setToList.sort()
        self.zeroDimensionListhx = setToList  # setting the list of orientation values to an ordered list
        print"hx=", setToList


        pointSet = Set()
        for rect in cornerStitch1.stitchList:
                pointSet.add(rect.cell.y)

        pointSet.add(cornerStitch1.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionListhy = setToList
        print"hy=", setToList



    def reduce(self):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its 
        minimum form
        """
        return

    def cgToGraph(self):
        G = nx.Graph()

        it = np.nditer(self.vertexMatrix, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G.add_edges_from([it.multi_index], weight = it[0])
#                print it[0]
            it.iternext()
        return G
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

    def drawGraph1(self):

        G2 = nx.DiGraph()

        it = np.nditer(self.vertexMatrixv, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G2.add_edges_from([it.multi_index], weight=it[0])
                print it[0]
            it.iternext()

        dictList1 = []
        print "checking edges"
        for foo in self.edgesv:
            dictList1.append(foo.getEdgeDict())
            print foo.getEdgeDict()
        print dictList1
        edge_labels1 = self.merge_dicts(dictList1)
        print "checking edge labels"
        print edge_labels1
        for foo in edge_labels1:
            print foo

        edge_colors1 = ['black' for edge in G2.edges()]
        # edge_colors1 = ['black' for edge in G.edges()]
        # for edge in G.edges():
        # print"constraint=", edge.getConstraint()

        # , edge_cmap = plt.cm.Reds - goes with nx.draw if needed
        pos = nx.shell_layout(G2)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw_networkx_labels(G2, pos)
        nx.draw(G2, pos, node_color='red', node_size=300, edge_color=edge_colors1)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name2)
        plt.close()
        #pylab.show()


    def drawGraph2(self):
        G1 = nx.DiGraph()
        it = np.nditer(self.vertexMatrixh, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G1.add_edges_from([it.multi_index], weight=it[0])
                print it[0]
            it.iternext()

        dictList = []
        print "checking edges"
        for foo in self.edgesh:
            dictList.append(foo.getEdgeDict())
            # print foo.getEdgeDict()
        print"dictlist=", dictList

        edge_labels = self.merge_dicts(dictList)
        print "checking edge labels"
        print edge_labels
        for foo in edge_labels:
            print foo
        edge_colors = ['black' for edge in G1.edges()]
        pos = nx.shell_layout(G1)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name1)
        #pylab.show()
        # edge_colors1 = ['black' for edge in G.edges()]
        # for edge in G.edges():
        # print"constraint=", edge.getConstraint()

        # , edge_cmap = plt.cm.Reds - goes with nx.draw if needed

class multiCG():
    """
    Same as a constraint graph class, except this allows for multiple edges between nodes. Necessary for
    inserting custom constraints. 
    """
    def __init__(self, sourceGraph):
        """
        given a source graph, copy vertices and all existing nodes into a multigraph
        """
        self.diGraph = nx.MultiDiGraph()
        self.diGraph.add_nodes_from(sourceGraph.cgToGraph().nodes(data = True))
        self.diGraph.add_edges_from(sourceGraph.cgToGraph().edges(data = True))

    def addEdge(self, source, dest, constraint):
        self.diGraph.add_edge(source, dest, constraint, weight = constraint.getConstraintVal())

    def drawGraph(self):
        G = self.diGraph
        edge_Labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])
        for foo in list(edge_Labels):
            print foo

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(self.diGraph)
        nx.draw_networkx_edge_labels(self.diGraph, pos, edge_labels = edge_Labels)
        nx.draw_networkx_labels(self.diGraph, pos)
        nx.draw(self.diGraph, pos, node_color='white', node_size=300, edge_color=edge_colors,arrows=True)

        pylab.show()

    def edgeReduce(self):
        """Eliminate redundant edges"""
        return

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

    def getEdgeDict(self):
        return self.edgeDict

    def printEdge(self):
        print "s: ", self.source, "d: ", self.dest, "con = ", self.constraint.printCon()
