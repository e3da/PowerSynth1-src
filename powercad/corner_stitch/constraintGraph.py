from sets import Set
import numpy as np
import constraint
import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import copy
from random import randint
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
        self.edgesv_new = []
        self.edgesh_new = []
        # self.zeroDimensionList = []
        self.zeroDimensionListh = []
        self.zeroDimensionListv = []
        #self.newXlocation=[]
        #self.newYlocation = []
        self.NEWXLOCATION=[] ####OPTIMIZATIioN
        self.NEWYLOCATION =[]####OPTIMIZATION
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
                #print"e=", Edge.getEdgeWeight(e,origin,dest)
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
        dictList1 = []
        #print self.edgesh
        self.edgesh_new=copy.deepcopy(self.edgesh)
        #print self.edgesh_new
        for foo in self.edgesh_new:
            # print foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        # print dictList1

        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        # print d.keys()
        # for u,v in d.keys():
        # print u,v

        nodes = [x for x in range(len(self.zeroDimensionListh))]
        #G2.add_nodes_from(nodes)
        ### adding missing edges for evaluation
        for i in range(len(nodes) - 1):
            if (nodes[i], nodes[i + 1]) not in d.keys():
                #d[nodes[i], nodes[i + 1]] = [1]
                self.edgesh_new.append(Edge(nodes[i], nodes[i+1], constraint.constraint(0, 'minWidth', nodes[i], nodes[i+1])))
        dictList = []
        self.edgesv_new = copy.deepcopy(self.edgesv)
        for foo in self.edgesv_new:
            dictList.append(foo.getEdgeDict())
        d1 = defaultdict(list)
        for i in dictList:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d1[k].append(v)
        edge_labels = d1
        nodes_v = [x for x in range(len(self.zeroDimensionListv))]
        #G1.add_nodes_from(nodes)
        ### adding missing edges for evaluation
        for i in range(len(nodes_v) - 1):
            if (nodes_v[i], nodes_v[i + 1]) not in d1.keys():
                #d[nodes[i], nodes[i + 1]] = [1]
                self.edgesv_new.append(Edge(nodes_v[i], nodes_v[i+1], constraint.constraint(0, 'minWidth', nodes_v[i], nodes_v[i+1])))
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

        pointSet_v = Set() #this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        #if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
        for rect in cornerStitch_v.stitchList:
                pointSet_v.add(rect.cell.y)

        pointSet_v.add(cornerStitch_v.northBoundary.cell.y)  # this won't be included in the normal list, so we do it here
        for rect in cornerStitch_h.stitchList:
                pointSet_v.add(rect.cell.y)

        pointSet_v.add(cornerStitch_h.northBoundary.cell.y)
        setToList_v = list(pointSet_v)
        setToList_v.sort()
        #self.zeroDimensionListvy = setToList
        self.zeroDimensionListv = setToList_v
        #print self.zeroDimensionListv
        #print"vy=", setToList
        pointSet_h = Set()
        for rect in cornerStitch_v.stitchList:
                pointSet_h.add(rect.cell.x)
        pointSet_h.add(cornerStitch_v.eastBoundary.cell.x)  # this won't be included in the normal list, so we do it here
        for rect in cornerStitch_h.stitchList:
                pointSet_h.add(rect.cell.x)
        pointSet_h.add(cornerStitch_h.eastBoundary.cell.x)
        setToList_h = list(pointSet_h)
        setToList_h.sort()
        self.zeroDimensionListh = setToList_h
        #print self.zeroDimensionListh
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
        #print self.edgesh
        for foo in self.edgesh:
            #print foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        #print dictList1

        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1=d
        #print d.keys()
        #for u,v in d.keys():
            #print u,v

        nodes=[x for x in range(len(self.zeroDimensionListh))]
        G2.add_nodes_from(nodes)
        '''
        ### adding missing edges for evaluation
        for i in range(len(nodes)-1):
            if (nodes[i],nodes[i+1]) not in d.keys():
                d[nodes[i],nodes[i+1]]=[1]
                #self.edgesh.append(Edge(nodes[i], nodes[i+1], constraint.constraint(0, 'minWidth', nodes[i], nodes[i+1])))
        '''
            #print nodes[i],nodes[i+1]
        ####
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
            #print data
            G2.add_weighted_edges_from(data)
        d = defaultdict(list)

        for i in label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        self.drawGraph_h(name, G2, edge_labels1)
        #### New graph
        G3 = nx.MultiDiGraph()
        dictList3 = []
        # print self.edgesh
        for foo in self.edgesh_new:
            # print foo.getEdgeDict()
            dictList3.append(foo.getEdgeDict())
        # print dictList1

        ######
        d3 = defaultdict(list)
        for i in dictList3:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d3[k].append(v)
        edge_labels3 = d3
        # print d.keys()
        # for u,v in d.keys():
        # print u,v

        nodes = [x for x in range(len(self.zeroDimensionListh))]
        G3.add_nodes_from(nodes)
        '''
        ### adding missing edges for evaluation
        for i in range(len(nodes)-1):
            if (nodes[i],nodes[i+1]) not in d.keys():
                d[nodes[i],nodes[i+1]]=[1]
                #self.edgesh.append(Edge(nodes[i], nodes[i+1], constraint.constraint(0, 'minWidth', nodes[i], nodes[i+1])))
        '''
        # print nodes[i],nodes[i+1]
        ####
        # print G2.nodes()
        # print G2.edges()
        # print"label=", edge_labels1
        label3 = []
        for branch in edge_labels3:
            lst_branch = list(branch)
            data = []

            for internal_edge in edge_labels3[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label3.append({(lst_branch[0], lst_branch[1]): internal_edge})
                '''
                if (lst_branch[0], lst_branch[1], {'route': internal_edge}) not in data:
                data.append((lst_branch[0], lst_branch[1], {'route': internal_edge}))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})
                '''
            # print data
            G3.add_weighted_edges_from(data)
        #############################################################
        label4=copy.deepcopy(label3)
        D=[]
        #print label3
        for i in label4:
            if i.values()[0]==2:
                D.append(i)

        #print D, len(D)
        W_total=[]
        for i in range(20):
            W=[]
            for i in range(len(D)):
                #W.append(randint(2, 10))
                W.append(randint(2, 5))
            W_total.append(W)
        #print W_total

        NewD=[]
        for i in range(len(D)):
            NewD.append(D[i].keys()[0])
        Space = []
        for i in label4:
            if i.values()[0] == 1:
                Space.append(i)
        #print Space
        ############################ Varying Spacing
        S_total = []
        for i in range(20):
            S = []
            for i in range(len(Space)):
                S.append(randint(1, 3))
            S_total.append(S)
        NewS = []
        for i in range(len(Space)):
            NewS.append(Space[i].keys()[0])
        #print "NEWD=", NewS
        new_labelw = []
        for j in range(len(W_total)):
            labelnew = []
            for i in range(len(NewD)):
                newdict = {NewD[i]: W_total[j][i]}
                labelnew.append(newdict)
                # labelnew.extend(Space)
            new_labelw.append(labelnew)
        #print new_labelw
        new_labels = []
        for j in range(len(S_total)):
            labelnew = []
            for i in range(len(NewS)):
                newdict = {NewS[i]: S_total[j][i]}
                labelnew.append(newdict)
            new_labels.append(labelnew)

        #print new_labels
        new_label = []
        for i in range(len(new_labels)):
            new_labels[i].extend(new_labelw[i])
            new_label.append(new_labels[i])
        #print new_label
        #print "l4=", label4
        for i in range(len(new_label)):
            #
            new_label[i].extend(label4)
            #print new_label[i]

        #print new_label
        ################################
        '''
        new_label=[]
        for j in range(len(W_total)):
            labelnew=[]
            for i in range(len(NewD)):
                newdict = {NewD[i]:W_total[j][i]}
                labelnew.append(newdict)
                labelnew.extend(Space)
            new_label.append(labelnew)
        '''
        #print len(new_label)
        #for i in new_label:
            #print i
        D_3=[]
        for j in range(len(new_label)):
            d[j]= defaultdict(list)
            #print d[j]
            #print"N=", new_label[j]
            for i in new_label[j]:
                #print i
                #print new_label[j]
                k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution

                #print k,v
                d[j][k].append(v)
            #print d[j]
            #print "d[j]",d[j]


            D_3.append(d[j])

        #print len(D_3),D_3

        '''
        NewD = []
        for i in range(len(D)):
            NewD.append(D[i].keys()[0])
        for j in range(len(W_total)):
            labelnew = []
            for i in range(len(NewD)):
                newdict = {NewD[i]: W_total[0][i]}
                labelnew.append(newdict)
        Space = []
        for i in label4:
            if i.values()[0] == 1:
                Space.append(i)
        #print Space
        labelnew.extend(Space)
        print "labelnew", labelnew
        d_3 = defaultdict(list)
        for i in labelnew:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d_3[k].append(v)
        edge_labels_3 = d_3
        print d_3
        #print len(edge_labels_3)
        '''






        ###############################################################
        d3 = defaultdict(list)
        for i in label3:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d3[k].append(v)
        edge_labels3 = d3
        #print len(edge_labels3)


        #### Storing edge data in (u,v,w) format in a file(begin)
        z = [(u, v, d['weight']) for u, v, d in G3.edges(data=True)]
        f1 = open(name, 'w')
        for i in z:
            #print i
            print >> f1,i
        ######## Storing edge data in (u,v,w) format in a file(end)

        ######## Finds all possible paths from start vertex to end vertex(begin)
        n=list(G3.nodes())
        self.FindingAllPaths_h(G3, n[0], n[-1])
        '''
        f2 = open("paths_h.txt", "rb")
        for line in f2.read().splitlines():  # considering each line in file
            self.paths_h.append(line)
        paths=[json.loads(y) for y in self.paths_h]
        '''
        paths=self.paths_h
        print paths
        #### (end)
        #### finding new location of each vertex in longest paths (begin)########
        '''
        l = []
        for path in paths:
            l.append(len(path))
        L = max(l)
        for path in paths:
            if (len(path)) == L:
                p = path
        longest_path = [p] ###finds the path which one has maximum nodes
        for j in range(len(paths)):
            if (not (set(paths[j]).issubset(set(p)))):
                if (paths[j] not in longest_path):
                    longest_path.append(paths[j])
        print "LONG=",longest_path ### Finds all unique paths so that all nodes are covered.
        '''


        ##############TESTING
        #NEWXLOCATION=[]
        loct = []
        for k in range(len(D_3)):
            new_Xlocation=[]

            dist = {}
            distance =set()###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
            location=set()###No use
            position_k={}## stores {node:location}
            for i in range(len(paths)):
                path = paths[i]
                #print path
                for j in range(len(path)):
                    node = path[j]
                    if j > 0:
                        pred = path[j - 1]
                    else:
                        pred = node
                    #print node, pred
                    if node == 0:
                        dist[node] = (0, pred)
                        # distance.append((pred,node,0))
                        distance.add((pred, node, 0))
                        #location.add((node,0))
                        key=node
                        position_k.setdefault(key,[])
                        position_k[key].append(0)
                    else:

                        pairs = (dist[pred][0] + max(D_3[k][(pred, node)]), pred)
                        #print  max(edge_labels1[(pred, node)])
                        dist[node] = pairs
                        #print dist[node][0]

                        distance.add((pred, node, pairs[0]))
                        #print pairs[0]
                        #if location[node]<pairs[0]:
                        location.add((node,pairs[0]))
                        key = node
                        position_k.setdefault(key, [])
                        position_k[key].append(pairs[0])
                #print position
            loc_i={}
            for key in position_k:
                loc_i[key]=max(position_k[key])
                new_Xlocation.append(loc_i[key])
            loct.append(loc_i)

            self.NEWXLOCATION.append(new_Xlocation)
        f3 = open(name+"location_x.txt", 'wb')
        for i in loct:
            # print i
            print >> f3, i
        print"LOC=",loct, self.NEWXLOCATION
        '''

        ###############       Without optimization
        dist = {}
        distance =set()###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
        location=set()###No use
        position={}## stores {node:location}
        for i in range(len(paths)):
            path = paths[i]
            #print path
            for j in range(len(path)):
                node = path[j]
                if j > 0:
                    pred = path[j - 1]
                else:
                    pred = node
                #print node, pred
                if node == 0:
                    dist[node] = (0, pred)
                    # distance.append((pred,node,0))
                    distance.add((pred, node, 0))
                    #location.add((node,0))
                    key=node
                    position.setdefault(key,[])
                    position[key].append(0)
                else:

                    pairs = (dist[pred][0] + max(edge_labels3[(pred, node)]), pred)
                    #print  max(edge_labels1[(pred, node)])
                    dist[node] = pairs
                    #print dist[node][0]

                    distance.add((pred, node, pairs[0]))
                    #print pairs[0]
                    #if location[node]<pairs[0]:
                    location.add((node,pairs[0]))
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])
            #print position
        loc={}
        for key in position:
            loc[key]=max(position[key])
            self.newXlocation.append(loc[key])
        print"LOC=", loc,self.newXlocation
        dist={}
        for node in loc:
            key = node

            dist.setdefault(key, [])
            dist[node].append(node)
            dist[node].append(loc[node])
        self.drawGraph_h_new(name, G3, edge_labels3, dist)  ### Drawing HCG

        #print dist
        '''
        '''
        #####Final Plot to show locations of new position(No need)
        G = nx.DiGraph()
        keys = [(0, node) for node in G2.nodes()]
        nodelist = [node for node in G2.nodes()]
        zeros = np.zeros(len(nodelist))
        values = [loc[node] for node in loc]
        data = map(lambda x, y, z: (x, y, z), zeros, nodelist, values)
        G.add_weighted_edges_from(data)
        val = map(lambda x, y: (x, y), G2.nodes(), values)
        pos = nx.shell_layout(G)
        labels = dict(zip(keys, values))
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw_networkx_labels(G, pos)
        nx.draw(G, pos, node_color='red', node_size=300, edge_color='black')
        plt.savefig(self.name1 + 'loc_h.png')
        plt.close()
        '''
        
        #### finding new location of each vertex in longest paths (end)########


    def FindingAllPaths_h(self, G, start, end):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its
        minimum form
        """
        #f1 = open("paths_h.txt", 'w')
        visited = [False] * (len(G.nodes()))
        path = []

        self.printAllPaths_h(G, start, end, visited, path)


    def printAllPaths_h(self, G, start, end, visited, path):
        visited[start] = True
        path.append(start)

        # If current vertex is same as destination, then print
        # current path[]

        if start == end:
            saved_path = path[:]
            self.paths_h.append(saved_path)
            # for i in edge_labels1:
            #print >> f1, path



            #self.paths_h.append(path)
            #print "self.paths_h",self.paths_h

            # paths.append(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex

            for i in G.neighbors(start):
                if visited[i] == False:
                    self.printAllPaths_h(G, i, end, visited, path)

        # Remove current vertex from path[] and mark it as unvisited

        path.pop()
        visited[start] = False


    def cgToGraph_v(self, name):
        G1 = nx.MultiDiGraph()
        dictList = []
        for foo in self.edgesv:
            dictList.append(foo.getEdgeDict())
        d = defaultdict(list)
        for i in dictList:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels = d
        nodes = [x for x in range(len(self.zeroDimensionListv))]
        G1.add_nodes_from(nodes)
        '''
        ### adding missing edges for evaluation
        for i in range(len(nodes)-1):
            if (nodes[i],nodes[i+1]) not in d.keys():
                d[nodes[i],nodes[i+1]]=[1]
                #self.edgesv.append(Edge(nodes[i], nodes[i+1], constraint.constraint(0, 'minWidth', nodes[i], nodes[i+1])))
        ######
        '''
        label = []
        for branch in edge_labels:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels[branch]:
                #if (lst_branch[0], lst_branch[1],  internal_edge) not in data:
                data.append((lst_branch[0],lst_branch[1],internal_edge))
                #data.append((lst_branch[0], lst_branch[1], {'route': internal_edge}))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})
            G1.add_weighted_edges_from(data)


        d = defaultdict(list)
        for i in label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels = d
        print len(d)
        self.drawGraph_v(name, G1, edge_labels)
        G4 = nx.MultiDiGraph()
        dictList4= []
        for foo in self.edgesv_new:
            dictList4.append(foo.getEdgeDict())
        d4 = defaultdict(list)
        for i in dictList4:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d4[k].append(v)
        edge_labels4 = d4
        #print edge_labels4
        nodes = [x for x in range(len(self.zeroDimensionListv))]
        G4.add_nodes_from(nodes)
        '''
        ### adding missing edges for evaluation
        for i in range(len(nodes)-1):
            if (nodes[i],nodes[i+1]) not in d.keys():
                d[nodes[i],nodes[i+1]]=[1]
                #self.edgesv.append(Edge(nodes[i], nodes[i+1], constraint.constraint(0, 'minWidth', nodes[i], nodes[i+1])))
        ######
        '''
        label4 = []
        for branch in edge_labels4:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels4[branch]:
                # if (lst_branch[0], lst_branch[1],  internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                # data.append((lst_branch[0], lst_branch[1], {'route': internal_edge}))
                label4.append({(lst_branch[0], lst_branch[1]): internal_edge})
            G4.add_weighted_edges_from(data)
        #############################################################
        '''(One output figure with variable Y)
        label_4 = copy.deepcopy(label4)
        D = []
        # print label3
        for i in label_4:
            if i.values()[0] == 2:
                D.append(i)

        # print D, len(D)
        W_total = []
        for i in range(10):
            W = []
            for i in range(len(D)):
                W.append(randint(2, 10))
            W_total.append(W)
        print W_total
        NewD = []
        for i in range(len(D)):
            NewD.append(D[i].keys()[0])
        labelnew = []

        for i in range(len(NewD)):
            newdict = {NewD[i]: W_total[0][i]}
            labelnew.append(newdict)

        Space = []
        for i in label4:
            if i.values()[0] == 1:
                Space.append(i)
        print Space
        labelnew.extend(Space)
        print "labelnew", labelnew
        d_3 = defaultdict(list)
        for i in labelnew:
            k, v = list(i.items())[
                0]  # an alternative to the single-iterating inner loop from the previous solution
            d_3[k].append(v)
        edge_labels_3 = d_3
        print len(edge_labels_3)
        '''

        ###############################################################
        ##############################           OPTIMIZATION
        label_4 = copy.deepcopy(label4)
        D = []
        # print label3
        for i in label_4:
            if i.values()[0] == 2:
                D.append(i)

        # print D, len(D)
        W_total = []
        for i in range(20):
            W = []
            for i in range(len(D)):
                W.append(randint(2, 10))
            W_total.append(W)
        #print W_total

        NewD = []
        for i in range(len(D)):
            NewD.append(D[i].keys()[0])
        #print "NEWD=",NewD
        Space = []
        for i in label_4:
            if i.values()[0] == 1:
                Space.append(i)
        ################### Varying spacing
        S_total = []
        for i in range(20):
            S = []
            for i in range(len(Space)):
                S.append(randint(1, 4))
            S_total.append(S)
        NewS = []
        for i in range(len(Space)):
            NewS.append(Space[i].keys()[0])
        #print "NEWD=", NewS
        new_labelw = []
        for j in range(len(W_total)):
            labelnew = []
            for i in range(len(NewD)):
                newdict = {NewD[i]: W_total[j][i]}
                labelnew.append(newdict)
                #labelnew.extend(Space)
            new_labelw.append(labelnew)
        #print new_labelw
        new_labels = []
        for j in range(len(S_total)):
            labelnew = []
            for i in range(len(NewS)):
                newdict = {NewS[i]: S_total[j][i]}
                labelnew.append(newdict)
            new_labels.append(labelnew)


        #print new_labels
        new_label=[]
        for i in range(len(new_labels)):
            new_labels[i].extend(new_labelw[i])
            new_label.append(new_labels[i])
        #print new_label
        #print "l4=",label4

        for i in range(len(new_label)):
            #
            new_label[i].extend(label4)
            #print new_label[i]

        #print new_label





        ###########################
        # print Space
        '''
        new_label = []
        for j in range(len(W_total)):
            labelnew = []
            for i in range(len(NewD)):
                newdict = {NewD[i]: W_total[j][i]}
                labelnew.append(newdict)
                labelnew.extend(Space)
            new_label.append(labelnew)
        '''
        #print len(new_label)
        #for i in new_label:
            #print i
        D_3 = []
        for j in range(len(new_label)):
            d[j] = defaultdict(list)
            # print d[j]
            #print"N=", new_label[j]
            for i in new_label[j]:
                # print i
                # print new_label[j]
                k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
                # print k,v
                d[j][k].append(v)
            # print d[j]
            #print "d[j]", d[j]

            D_3.append(d[j])

        #print "V=",len(D_3), D_3

        ############################
        d4 = defaultdict(list)
        for i in label4:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d4[k].append(v)
        edge_labels4 = d4
        #print len(d4)

        z=[(u, v, d['weight'])for u, v, d in G4.edges(data=True)]
        f1 = open(name, 'w')
        for i in z:
            print >> f1, i
        #A = nx.adjacency_matrix(G1)


        #self.drawGraph_v(name, G1, edge_labels)### Drawing VCG
        #### Finding all possible paths from start vertex to end vertex
        n=list(G4.nodes())
        self.FindingAllPaths_v(G4, n[0], n[-1])
        '''
        f = open("paths_v.txt", "rb")
        for line in f.read().splitlines():  # considering each line in file
            self.paths_v.append(line)
        paths = [json.loads(y) for y in self.paths_v]
        '''
        paths=self.paths_v
        print paths
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
        '''
        l = []
        for path in paths:
            l.append(len(path))
        L = max(l)
        for path in paths:
            if (len(path)) == L:
                p = path
        longest_path = [p]
        for j in range(len(paths)):
            if (not (set(paths[j]).issubset(set(p)))):
                if (paths[j] not in longest_path):
                    longest_path.append(paths[j])
        print "long=", longest_path
        '''
        '''
        ########### Without optimization
        dist = {}
        distance =set()
        position = {}  ## stores {node:location}
        for i in range(len(paths)):
            path=paths[i]
            #print path
            for j in range(len(path)):
                node=path[j]
                if j>0:
                    pred=path[j-1]
                else:
                    pred=node
                if node==0:
                    dist[node]=(0,pred)
                    distance.add((pred, node, 0))
                    key = node
                    position.setdefault(key, [])
                    position[key].append(0)
                else:
                    pairs = (dist[pred][0] + max(edge_labels4[(pred, node)]), pred)
                    dist[node]=pairs
                    distance.add((pred, node, pairs[0]))
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])
            #print position
        loc = {}
        for key in position:
            loc[key] = max(position[key])
            self.newYlocation.append(loc[key])
        print"LOC=", loc,self.newYlocation

        dist = {}
        for node in loc:
            key = node

            dist.setdefault(key, [])
            dist[node].append(node)
            dist[node].append(loc[node])
        #print dist

        #### finding new location of each vertex in longest paths (end)########
        #### redraw graph with new position
        #print loc
        self.drawGraph_v_new(name, G4, edge_labels4, dist)  ### Drawing VCG
        ####################################
        '''
        ##############TESTING optimization
        # NEWXLOCATION=[]
        loct = []
        for k in range(len(D_3)):
            new_Ylocation = []

            dist = {}
            distance = set()  ###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
            location = set()  ###No use
            position_k = {}  ## stores {node:location}
            for i in range(len(paths)):
                path = paths[i]
                # print path
                for j in range(len(path)):
                    node = path[j]
                    if j > 0:
                        pred = path[j - 1]
                    else:
                        pred = node
                    # print node, pred
                    if node == 0:
                        dist[node] = (0, pred)
                        # distance.append((pred,node,0))
                        distance.add((pred, node, 0))
                        # location.add((node,0))
                        key = node
                        position_k.setdefault(key, [])
                        position_k[key].append(0)
                    else:

                        pairs = (dist[pred][0] + max(D_3[k][(pred, node)]), pred)
                        # print  max(edge_labels1[(pred, node)])
                        dist[node] = pairs
                        # print dist[node][0]

                        distance.add((pred, node, pairs[0]))
                        # print pairs[0]
                        # if location[node]<pairs[0]:
                        location.add((node, pairs[0]))
                        key = node
                        position_k.setdefault(key, [])
                        position_k[key].append(pairs[0])
                # print position
            loc_i = {}
            for key in position_k:
                loc_i[key] = max(position_k[key])
                new_Ylocation.append(loc_i[key])
            loct.append(loc_i)

            self.NEWYLOCATION.append(new_Ylocation)
        f4 = open(name+'location_y.txt', 'w')
        for i in loct:
            # print i
            print >> f4, i
        print"LOC=", loct, self.NEWYLOCATION

        '''
        G = nx.DiGraph()
        keys=[(0,node)for node in G1.nodes()]

        nodelist = [node for node in G1.nodes()]
        zeros = np.zeros(len(nodelist))
        values = [loc[node] for node in loc]
        print "values",values
        data=map(lambda x,y,z:(x,y,z),zeros,nodelist,values)
        G.add_weighted_edges_from(data)


        pos = nx.shell_layout(G)
        labels=dict(zip(keys, values))
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw_networkx_labels(G, pos)

        nx.draw(G, pos, node_color='red', node_size=300, edge_color='black')
        plt.savefig(self.name2 + 'loc_v.png')
        plt.close()
        '''




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
    def FindingAllPaths_v(self,G,start,end):
        """
        This should call subroutines for edge and vertex reduction, to pare the constraint graph down to its
        minimum form
        """
        #f1 = open("paths_v.txt", 'w')
        visited = [False] * (len(G.nodes()))
        path=[]
        self.printAllPaths_v(G,start, end, visited, path)
    def printAllPaths_v(self,G, start,end, visited, path):
        visited[start] = True
        path.append(start)
        # If current vertex is same as destination, then print
        # current path[]
        if start == end:
            saved_path = path[:]
            self.paths_v.append(saved_path)
             #print >> f1, path
        else:
            for i in G.neighbors(start):

                if visited[i] == False:
                    self.printAllPaths_v(G,i,end, visited, path)
        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[start] = False

    def drawGraph_h(self, name, G2, edge_labels1):

        # edge_labels1 = self.merge_dicts(dictList1)
        edge_colors1 = ['black' for edge in G2.edges()]
        pos = nx.shell_layout(G2)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw_networkx_labels(G2, pos)
        nx.draw(G2, pos, node_color='red', node_size=300, edge_color=edge_colors1)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        # plt.show()
        plt.savefig(self.name1 + 'gh.png')
        plt.close()

    def drawGraph_h_new(self,name,G2,edge_labels1,loc):



        #edge_labels1 = self.merge_dicts(dictList1)
        edge_colors1 = ['black' for edge in G2.edges()]
        pos = nx.shell_layout(G2)



        nx.draw_networkx_labels(G2, pos, labels=loc)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw(G2, pos, node_color='red', node_size=900, edge_color=edge_colors1)
        plt.savefig(self.name2 + 'location_h.png')
        plt.close()
        #pylab.show()


    def drawGraph_v(self,name2,G1,edge_labels):

        #######
        edge_colors = ['black' for edge in G1.edges()]
        pos = nx.shell_layout(G1)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name2 + 'gv.png')
        plt.close()


        '''
        nlist = map(list, loc.items())
        pos = nx.circular_layout(loc)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        #nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name2 + 'locv.png')
        '''
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        #app = Viewer(G1)
        #app.mainloop()


        #pylab.show()

    def drawGraph_v_new(self,name2,G1,edge_labels,loc):

            #######
            edge_colors = ['black' for edge in G1.edges()]
            pos = nx.shell_layout(G1)


            nx.draw_networkx_labels(G1, pos, labels=loc)
            nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
            nx.draw(G1, pos, node_color='red', node_size=900, edge_color=edge_colors)
            plt.savefig(self.name2 + 'location_v.png')
            plt.close()



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
