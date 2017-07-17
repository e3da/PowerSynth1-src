from sets import Set
import numpy as np
import constraint

class constraintGraph:
    """
    the graph representation of constraints pertaining to cells and variables, informed by several different 
    sources
    """

    def __init__(self, vertices, edges):
        """
        create from a given set of edges and vertices
        vertexMatrix shows the connectivity between the vertices, it is a 2d list n vertices long
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

    def __init__(self):
        """
        Default constructor
        """
        self.vertexMatrix = None
        self.edges = []
        self.zeroDimensionList = []

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

    def setEdgesFromLayer(self, cornerStitch):
        """
        given a cornerStitch and orientation, set the connectivity matrix of this constraint graph
        """
        if cornerStitch.orientation == 'v':
            for rect in cornerStitch.stitchList:
                origin = self.zeroDimensionList.index(rect.cell.y)
                dest = self.zeroDimensionList.index(rect.getNorth().cell.y)
                self.vertexMatrix[origin][dest] = rect.getHeight()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0)))
                elif rect.cell.getType() == "SOLID":
                    self.edges.append(Edge(origin, dest, constraint.constraint(1)))

        elif cornerStitch.orientation == 'h':
            for rect in cornerStitch.stitchList:
                origin = self.zeroDimensionList.index(rect.cell.x)
                dest = self.zeroDimensionList.index(rect.getEast().cell.x)
                print "origin = ", origin, "dest = ", dest, "val = ", rect.getWidth()
                self.vertexMatrix[origin][dest] = rect.getWidth()
                if rect.cell.getType() == "EMPTY":
                    self.edges.append(Edge(origin, dest, constraint.constraint(0)))
                elif rect.cell.getType() == "SOLID":
                    self.edges.append(Edge(origin, dest, constraint.constraint(1)))


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

        self.zeroDimensionList =  setToList#setting the list of orientation values to an ordered list

    def reduce(self):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its 
        minimum form
        """
        return

    def edgeReduce(self):
        """Eliminate redundant edges"""
        return

    def vertexReduce(self):
        """Eliminate redundant vertices"""
        return

    def drawGraph(self):
        G = nx.DiGraph()

        it = np.nditer(self.vertexMatrix, flags=['multi_index'])
        while not it.finished:
            if it[0] != 0:
                G.add_edges_from([it.multi_index], weight = it[0])
                print it[0]
            it.iternext()

        edge_labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(G)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw(G, pos, node_color='white', node_size=300, edge_color=edge_colors, edge_cmap=plt.cm.Reds)
        pylab.show()

class Edge():

    def __init__(self, source, dest, constraint):
        self.source = source
        self.dest = dest
        self.constraint = constraint

    def getConstraint(self):
        return self.constraint

    def printEdge(self):
        print "s: ", self.source, "d: ", self.dest, "con: ", self.constraint.printCon()