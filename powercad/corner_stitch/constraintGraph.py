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


    def __init__(self,name):
        """
        Default constructor
        """
        self.vertexMatrix = None
        self.edges = []
        self.zeroDimensionList = []
        self.name = name

    def getVertexMatrix(self):
        return self.vertexMatrix

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

    def graphFromLayer(self, cornerStitch):
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        """
        self.dimListFromLayer(cornerStitch)
        self.matrixFromDimList()
        self.setEdgesFromLayer(cornerStitch)

    def matrixFromDimList(self):
        """
        initializes a N x N matrix of 0's as self's matrix object
        """
        n = len(self.zeroDimensionList)
        self.vertexMatrix = np.zeros((n, n), np.int8)

    def printVM(self):
        for i in self.vertexMatrix:
            print i
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

    def setEdgesFromLayer(self, cornerStitch):
        """
        given a cornerStitch and orientation, set the connectivity matrix of this constraint graph
        """
        if cornerStitch.orientation == 'v':
            print"stitchlist"
            for rect in cornerStitch.stitchList:

                rect.cell.printCell(True,True)
                origin = self.zeroDimensionList.index(rect.cell.y)
                #print"origin-",origin
                dest = self.zeroDimensionList.index(rect.getNorth().cell.y)
                self.vertexMatrix[origin][dest] = rect.getHeight()
                #print"origin-", rect.getHeight()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                elif rect.cell.getType() == "SOLID":

                    self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))

        elif cornerStitch.orientation == 'h':
            print"stitchlist-h"
            for rect in cornerStitch.stitchList:
                rect.cell.printCell(True, True)
                origin = self.zeroDimensionList.index(rect.cell.x)
                dest = self.zeroDimensionList.index(rect.getEast().cell.x)
                print "origin = ", origin, "dest = ", dest, "val = ", rect.getWidth()
                self.vertexMatrix[origin][dest] = rect.getWidth()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0, 'minWidth', origin, dest)))
                elif rect.cell.getType() == "SOLID":
                    self.edges.append(Edge(origin, dest, constraint.constraint(1, 'minWidth', origin, dest)))

    def dimListFromLayer(self, cornerStitch):
        """
        generate the zeroDimensionList from a cornerStitch         
        """
        pointSet = Set() #this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)

        if cornerStitch.orientation == 'v': #if orientation is vertical, add all unique y values for cells
            for rect in cornerStitch.stitchList:

                pointSet.add(rect.cell.y)
            pointSet.add(cornerStitch.northBoundary.cell.y) # this won't be included in the normal list, so we do it here
        elif cornerStitch.orientation == 'h': #same for horizontal orientation
            for rect in cornerStitch.stitchList:
                pointSet.add(rect.cell.x)
            pointSet.add(cornerStitch.eastBoundary.cell.x)

        setToList = list(pointSet)
        setToList.sort()

        self.zeroDimensionList =  setToList#setting the list of orientation values to an ordered list
        #print"ZDL=",len(setToList)

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

    def drawGraph(self):
        G = nx.DiGraph()

        it = np.nditer(self.vertexMatrix, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G.add_edges_from([it.multi_index], weight = it[0])
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

        edge_colors = ['black' for edge in G.edges()]

        #, edge_cmap = plt.cm.Reds - goes with nx.draw if needed
        pos = nx.shell_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name)
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
