from sets import Set
import numpy as np
import constraint
import networkx as nx
from matplotlib import pylab
import matplotlib.pyplot as plt
from collections import defaultdict
import collections
import json
import copy
import random
import csv
import scipy as sp
import pandas as pd


#########################################################################################################################


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
        ####################################

    def __init__(self, name1, name2,W=None,H=None,XLocation=None,YLocation=None):
        """
        Default constructor
        """

        # self.edgesv = []  ### saves initial vertical constraint graph edges (without adding missing edges)
        # self.edgesh = []  ### saves initial horizontal constraint graph edges (without adding missing edges)
        # self.edgesv_new = []  ###saves vertical constraint graph edges (with adding missing edges)
        # self.edgesh_new = []  ###saves horizontal constraint graph edges (with adding missing edges)

        self.zeroDimensionListh = []  ### All X cuts of tiles
        self.zeroDimensionListv = []  ### All Y cuts of tiles
        # self.newXlocation=[]
        # self.newYlocation = []
        self.NEWXLOCATION = []  ####Array of all X locations after optimization
        self.NEWYLOCATION = []  ####Array of all Y locations after optimization
        self.name1 = name1
        self.name2 = name2
        self.paths_h = []  ### all paths in HCG from leftmost node to right most node
        self.paths_v = []  ### all paths in VCG from bottom most node to top most node

        self.special_location_x = []
        self.special_location_y = []
        self.special_cell_id_h = []
        self.special_cell_id_v = []
        self.special_edgev = []
        self.special_edgeh = []

        self.X = []
        self.Y = []
        self.Loc_X = {}
        self.Loc_Y = {}
        # self.W_T = [160,165,170,175,180,185,190,195,200,205]
        # self.H_T =[105,110,120,130,140,150,160,170,180,190]

        ############################

        self.vertexMatrixh = {}
        self.vertexMatrixv = {}
        self.ZDL_H = {}
        self.ZDL_V = {}

        self.edgesv = {}  ### saves initial vertical constraint graph edges (without adding missing edges)
        self.edgesh = {}  ### saves initial horizontal constraint graph edges (without adding missing edges)
        self.edgesv_new = {}  ###saves vertical constraint graph edges (with adding missing edges)
        self.edgesh_new = {}  ###saves horizontal constraint graph edges (with adding missing edges)

        self.minLocationH = {}
        self.minLocationV = {}

        self.minX = {}
        self.minY = {}
        self.W_T =W #300
        self.H_T =H#250
        self.XLoc = XLocation
        self.YLoc= YLocation
        #self.Loc_X=XLocation
        #self.Loc_Y=YLocation

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

    def graphFromLayer(self, H_NODELIST, V_NODELIST, level,N=None):
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        self.dimListFromLayer(cornerStitch_h, cornerStitch_v)
        # self.matrixFromDimList()
        self.setEdgesFromLayer(cornerStitch_h, cornerStitch_v)
        """
        HorizontalNodeList = []
        VerticalNodeList = []
        for node in H_NODELIST:
            if node.child == []:
                continue
            else:
                HorizontalNodeList.append(node)

        for node in V_NODELIST:
            if node.child == []:
                continue
            else:
                VerticalNodeList.append(node)
        #print "RESULT"
        """
        print HorizontalNodeList
        for i in HorizontalNodeList:

            print i.id, i, len(i.stitchList)

            # i=Htree.hNodeList[0]
            for j in i.stitchList:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                print k

            if i.parent == None:
                print 0
            else:
                print i.parent.id, i.id
            for j in i.boundaries:
                if j.cell.type != None:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId

                else:
                    k=j.cell.x,j.cell.y,j.cell.type,j.nodeId
                print "B", i.id, k

        print VerticalNodeList
        for i in VerticalNodeList:
            print i.id, i, len(i.stitchList)
            for j in i.stitchList:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                print k

            if i.parent == None:
                print 0
            else:
                print i.parent.id, i.id
            for j in i.boundaries:
                if j.cell.type != None:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId

                else:
                    k = j.cell.x, j.cell.y, j.cell.type,j.nodeId
                print "B", i.id, k
        """

        Key = []
        ValueH = []
        ValueV = []
        for i in range(len(HorizontalNodeList)):
            Key.append(HorizontalNodeList[i].id)
            k, j = self.dimListFromLayer(HorizontalNodeList[i], VerticalNodeList[i])
            ValueH.append(k)
            ValueV.append(j)
        # print Key,ValueH
        ZDL_H = dict(zip(Key, ValueH))
        ZDL_V = dict(zip(Key, ValueV))
        self.ZDL_H = collections.OrderedDict(sorted(ZDL_H.items()))
        # self.ZDL_H =dict(zip(Key, ValueH))
        self.ZDL_V = collections.OrderedDict(sorted(ZDL_V.items()))
        # self.ZDL_H[HorizontalNodeList[i].id]=k
        # self.ZDL_V[VerticalNodeList[i].id]=j
        #print "ZDL_H", self.ZDL_H
        #print "ZDL_V", self.ZDL_V

        for i in range(len(HorizontalNodeList)):
            # print HorizontalNodeList[i].id
            # for child in HorizontalNodeList[i].child:
            # print child.id
            self.setEdgesFromLayer(HorizontalNodeList[i], VerticalNodeList[i])

        # print self.vertexMatrixh
        # print self.vertexMatrixh
        self.edgesh_new = collections.OrderedDict(sorted(self.edgesh_new.items()))
        self.edgesv_new = collections.OrderedDict(sorted(self.edgesv_new.items()))
        # print "K",self.edgesh_new.keys()
        for k, v in list(self.edgesh_new.iteritems())[::-1]:

            ID, edgeh = k, v
            name = "Node-" + str(ID)
            # print ID

            for i in HorizontalNodeList:
                if i.id == ID:
                    if i.parent != None:
                        parent = i.parent.id
                    else:
                        parent = None
            self.cgToGraph_h(name, ID, self.edgesh_new[ID], parent, level,N)

        for k, v in list(self.edgesv_new.iteritems())[::-1]:

            ID, edgev = k, v
            name = "Node-" + str(ID)
            # print ID

            for i in VerticalNodeList:
                if i.id == ID:
                    if i.parent != None:
                        parent = i.parent.id
            self.cgToGraph_v(name, ID, edgev, parent, level,N)
        print "RESULT"
        print "Y_Locations:", self.minLocationV
        print "X_Locations:", self.minLocationH
        print "Generating Figures"
        # print self.minLocationV[2][48]

        '''
        X=[]
        Y=[]
        for i in self.ZDL_H.values():
            X.extend(i)
        X=list(set(X))
        X.sort()
        for i in self.ZDL_V.values():
            Y.extend(i)
        Y = list(set(Y))
        Y.sort()
        print "Y",Y
        '''

    '''
    def minValueCalculation(self,hNodeList,vNodeList):
        for node in hNodeList:
            if node.parent==None:
                self.minX[node.id]=self.minLocationH[node.id]

            else:
                self.set_minX(node)

        for node in vNodeList:
            if node.parent == None:
                self.minY[node.id] = self.minLocationV[node.id]

            else:
                self.set_minY(node)
        #print "minX",self.minX
        #print "minY",self.minY
        return self.minX,self.minY
    '''

    ##### for single node
    def minValueCalculation(self, hNodeList, vNodeList, level):
        if level != 0:

            for node in hNodeList:
                if node.parent == None:
                    self.minX[node.id] = self.minLocationH[node.id]

                else:
                    self.set_minX(node)

            for node in vNodeList:
                if node.parent == None:
                    self.minY[node.id] = self.minLocationV[node.id]

                else:
                    self.set_minY(node)
            # print "minX",self.minX
            # print "minY",self.minY
            return self.minX, self.minY
        else:
            for node in hNodeList:
                if node.parent == None:
                    self.minX[node.id] = self.minLocationH[node.id]

                else:
                    self.set_minX(node)

            for node in vNodeList:
                if node.parent == None:
                    self.minY[node.id] = self.minLocationV[node.id]

                else:
                    self.set_minY(node)
            #print "minX",self.minX
            #print "minY",self.minY

            return self.minX, self.minY

    def set_minX(self, node):
        if node.id in self.minLocationH.keys():
            L = self.minLocationH[node.id]
            P_ID = node.parent.id
            K = L.keys()
            V = L.values()
            L1 = {}
            for i in range(len(K)):
                if K[i] not in self.ZDL_H[P_ID]:
                    V2 = V[i]
                    V1 = V[i - 1]
                    L1[K[i]] = V2 - V1
            final = {}
            for k in range(len(K)):
                if K[k] not in L1.keys():
                    final[K[k]] = self.minX[P_ID][K[k]]
                    L1[K[k]] = self.minX[P_ID][K[k]]
                else:
                    final[K[k]] = final[K[k - 1]] + L1[K[k]]

            self.minX[node.id] = final
        # print"H", final

    def set_minY(self, node):
        if node.id in self.minLocationV.keys():
            L = self.minLocationV[node.id]
            P_ID = node.parent.id
            K = L.keys()
            V = L.values()
            L1 = {}
            for i in range(len(K)):
                if K[i] not in self.ZDL_V[P_ID]:
                    V2 = V[i]
                    V1 = V[i - 1]
                    L1[K[i]] = V2 - V1
            final = {}
            for k in range(len(K)):
                if K[k] not in L1.keys():
                    final[K[k]] = self.minY[P_ID][K[k]]
                    L1[K[k]] = self.minY[P_ID][K[k]]
                else:
                    final[K[k]] = final[K[k - 1]] + L1[K[k]]

            self.minY[node.id] = final
        # print "V", L

    def printVM(self, name1, name2):
        f1 = open(name1, 'w')
        # for k, v in self.vertexMatrixh.iteritems():
        # print >>f1,k, v
        for i in self.vertexMatrixh:
            print >> f1, i

        f2 = open(name2, 'w')
        # for k, v in self.vertexMatrixv.iteritems():
        # print >>f2,k, v
        for i in self.vertexMatrixv:
            print >> f2, i
        return

    def printZDL(self):
        index = 0
        for i in self.zeroDimensionList:
            print index, ": ", i
            index += 1

    # print"stitchList=", cornerStitch.stitchList

    def dimListFromLayer(self, cornerStitch_h, cornerStitch_v):
        """
        generate the zeroDimensionList from a cornerStitch
        """

        pointSet_v = Set()  # this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        # if cornerStitch.orientation == 'v':  # if orientation is vertical, add all unique y values for cells
        max_y = 0
        for rect in cornerStitch_v.stitchList:
            pointSet_v.add(rect.cell.y)
            pointSet_v.add(rect.cell.y + rect.getHeight())
            if max_y < rect.cell.y + rect.getHeight():
                max_y = rect.cell.y + rect.getHeight()

        pointSet_v.add(max_y)  # this won't be included in the normal list, so we do it here

        for rect in cornerStitch_h.stitchList:
            pointSet_v.add(rect.cell.y)
            pointSet_v.add(rect.cell.y + rect.getHeight())
            if max_y < rect.cell.y + rect.getHeight():
                max_y = rect.cell.y + rect.getHeight()

        pointSet_v.add(max_y)
        setToList_v = list(pointSet_v)
        setToList_v.sort()
        # self.zeroDimensionListvy = setToList
        # self.zeroDimensionListv = setToList_v

        pointSet_h = Set()
        max_x = 0
        for rect in cornerStitch_v.stitchList:
            pointSet_h.add(rect.cell.x)
            pointSet_h.add(rect.cell.x + rect.getWidth())
            if max_x < rect.cell.x + rect.getWidth():
                max_x = rect.cell.x + rect.getWidth()
        # print pointSet_h
        pointSet_h.add(max_x)  # this won't be included in the normal list, so we do it here
        for rect in cornerStitch_h.stitchList:
            pointSet_h.add(rect.cell.x)
            pointSet_h.add(rect.cell.x + rect.getWidth())
            if max_x < rect.cell.x + rect.getWidth():
                max_x = rect.cell.x + rect.getWidth()
        pointSet_h.add(max_x)
        setToList_h = list(pointSet_h)
        setToList_h.sort()
        # self.zeroDimensionListh = setToList_h
        return setToList_h, setToList_v

    def setEdgesFromLayer(self, cornerStitch_h, cornerStitch_v):
        # self.vertexMatrixh=defaultdict(lambda: defaultdict(list))
        # self.vertexMatrixv = defaultdict(lambda: defaultdict(list))

        ID = cornerStitch_h.id
        # print"ID", ID
        n1 = len(self.ZDL_H[ID])
        n2 = len(self.ZDL_V[ID])
        self.vertexMatrixh[ID] = [[[] for i in range(n1)] for j in range(n1)]
        self.vertexMatrixv[ID] = [[[] for i in range(n2)] for j in range(n2)]
        edgesh = []
        edgesv = []



        # if cornerStitch_h.parent!=None:
        for rect in cornerStitch_v.stitchList:
            Extend_h = 0
            # if rect.cell.type == "SOLID":
            if rect.nodeId != ID:
                origin = self.ZDL_H[ID].index(rect.cell.x)
                dest = self.ZDL_H[ID].index(rect.getEast().cell.x)
                origin1=self.ZDL_V[ID].index(rect.cell.y)
                dest1=self.ZDL_V[ID].index(rect.getNorth().cell.y)
                id = rect.cell.id

                if rect.getEast().nodeId == rect.nodeId:
                    East = rect.getEast().cell.id
                    if rect.southEast(rect).nodeId == rect.nodeId:
                        if rect.southEast(rect).cell==rect.getEast().cell and rect.NORTH.nodeId==ID and rect.SOUTH.nodeId==ID:
                            Extend_h=1

                else:
                    East = None
                if rect.getWest().nodeId == rect.nodeId:
                    West = rect.getWest().cell.id
                    if rect.northWest(rect).nodeId == rect.nodeId:
                        if rect.northWest(rect).cell==rect.getWest().cell and rect.NORTH.nodeId==ID and rect.SOUTH.nodeId==ID:
                            Extend_h=1

                else:
                    West = None
                if rect.northWest(rect).nodeId == rect.nodeId:
                    northWest = rect.northWest(rect).cell.id
                else:
                    northWest = None
                if rect.southEast(rect).nodeId == rect.nodeId:
                    southEast = rect.southEast(rect).cell.id
                else:
                    southEast = None

                # print id,East,West,rect.cell.x,rect.cell.y

                c = constraint.constraint(0)
                index = 0
                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                e = Edge(origin1, dest1, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, East,
                         West, northWest, southEast)
                # print "e",(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id, East, West,northWest, southEast)
                # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)
                edgesv.append(Edge(origin1, dest1, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, East,West, northWest, southEast))
                # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                # self.vertexMatrixh[origin][dest].append((rect.getWidth()))
                self.vertexMatrixv[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest))


                if Extend_h==1:
                    c = constraint.constraint(3)
                    index = 3
                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, East,
                             West, northWest, southEast)
                    # print "e",(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id, East, West,northWest, southEast)
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)
                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, East,
                             West, northWest, southEast))
                    # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    # self.vertexMatrixh[origin][dest].append((rect.getWidth()))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))


                # self.edgesh.append(Edge(origin, dest, constraint.constraint(rect.getWidth(), origin, dest)))#
            else:
                # print ID
                origin = self.ZDL_V[ID].index(rect.cell.y)
                dest = self.ZDL_V[ID].index(rect.getNorth().cell.y)
                id = rect.cell.id

                if rect.getNorth().nodeId == rect.nodeId:
                    North = rect.getNorth().cell.id

                else:
                    North = None
                if rect.getSouth().nodeId == rect.nodeId:
                    South = rect.getSouth().cell.id
                else:
                    South = None
                if rect.westNorth(rect).nodeId == rect.nodeId:
                    westNorth = rect.westNorth(rect).cell.id
                else:
                    westNorth = None
                if rect.eastSouth(rect).nodeId == rect.nodeId:
                    eastSouth = rect.eastSouth(rect).cell.id
                else:
                    eastSouth = None

                if rect.NORTH.nodeId != ID and rect.SOUTH.nodeId != ID and rect.NORTH in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
                    t2 = constraint.constraint.Type.index(rect.NORTH.cell.type)
                    t1 = constraint.constraint.Type.index(rect.SOUTH.cell.type)
                    c = constraint.constraint(1)
                    index = 1
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)

                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.NORTH.nodeId != ID and rect.SOUTH not in cornerStitch_v.stitchList and rect.NORTH in cornerStitch_v.stitchList:
                    t2 = constraint.constraint.Type.index(rect.NORTH.cell.type)
                    t1 = constraint.constraint.Type.index(rect.cell.type)
                    c = constraint.constraint(2)
                    # print t1,t2
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.SOUTH.nodeId != ID and rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
                    t2 = constraint.constraint.Type.index(rect.SOUTH.cell.type)
                    t1 = constraint.constraint.Type.index(rect.cell.type)
                    c = constraint.constraint(2)
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH not in cornerStitch_v.stitchList:
                    c = constraint.constraint(0)
                    index = 0
                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

        for rect in cornerStitch_h.stitchList:
            Extend_v = 0
            # if rect.cell.type == "SOLID":
            # print rect.cell.x,rect.cell.y,rect.EAST.cell.x,rect.WEST.cell.x
            # if rect.EAST not in cornerStitch_h.stitchList and rect.WEST  not in cornerStitch_h.stitchList:
            # print rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.WEST.cell.x
            if rect.nodeId != ID:
                origin = self.ZDL_V[ID].index(rect.cell.y)
                dest = self.ZDL_V[ID].index(rect.getNorth().cell.y)
                origin1 = self.ZDL_H[ID].index(rect.cell.x)
                dest1 = self.ZDL_H[ID].index(rect.getEast().cell.x)
                id = rect.cell.id
                if rect.getNorth().nodeId == rect.nodeId:
                    North = rect.getNorth().cell.id
                    if rect.westNorth(rect).nodeId == rect.nodeId:
                        if rect.westNorth(rect).cell==rect.getNorth().cell and rect.EAST.nodeId==ID and rect.WEST.nodeId==ID:
                            Extend_v=1
                else:
                    North = None
                if rect.getSouth().nodeId == rect.nodeId:
                    South = rect.getSouth().cell.id
                    if rect.eastSouth(rect).nodeId == rect.nodeId:
                        if rect.eastSouth(rect).cell==rect.getSouth().cell and rect.EAST.nodeId==ID and rect.WEST.nodeId==ID:
                            Extend_v=1
                else:
                    South = None
                if rect.westNorth(rect).nodeId == rect.nodeId:
                    westNorth = rect.westNorth(rect).cell.id
                else:
                    westNorth = None
                if rect.eastSouth(rect).nodeId == rect.nodeId:
                    eastSouth = rect.eastSouth(rect).cell.id
                else:
                    eastSouth = None

                c = constraint.constraint(0)
                index = 0
                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                e = Edge(origin1, dest1, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, North,
                         South, westNorth, eastSouth)

                edgesh.append(Edge(origin1, dest1, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, North,South, westNorth, eastSouth))
                # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                self.vertexMatrixh[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest))

                # print id,East,West,rect.cell.x,rect.cell.y
                if Extend_v==1:
                    c = constraint.constraint(3)
                    index = 3
                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, North,
                             South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id, North,
                             South, westNorth, eastSouth))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesv.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))


            else:
                origin = self.ZDL_H[ID].index(rect.cell.x)
                dest = self.ZDL_H[ID].index(rect.getEast().cell.x)
                id = rect.cell.id

                if rect.getEast().nodeId == rect.nodeId:
                    East = rect.getEast().cell.id
                else:
                    East = None
                if rect.getWest().nodeId == rect.nodeId:
                    West = rect.getWest().cell.id
                else:
                    West = None
                if rect.northWest(rect).nodeId == rect.nodeId:
                    northWest = rect.northWest(rect).cell.id
                else:
                    northWest = None
                if rect.southEast(rect).nodeId == rect.nodeId:
                    southEast = rect.southEast(rect).cell.id
                else:
                    southEast = None

                if rect.EAST.nodeId != ID and rect.WEST.nodeId != ID and rect.EAST in cornerStitch_h.stitchList and rect.WEST in cornerStitch_h.stitchList:
                    t2 = constraint.constraint.Type.index(rect.EAST.cell.type)
                    t1 = constraint.constraint.Type.index(rect.WEST.cell.type)
                    c = constraint.constraint(1)
                    index = 1
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)

                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST.nodeId != ID and rect.WEST not in cornerStitch_h.stitchList and rect.EAST in cornerStitch_h.stitchList:
                    t2 = constraint.constraint.Type.index(rect.EAST.cell.type)
                    t1 = constraint.constraint.Type.index(rect.cell.type)
                    c = constraint.constraint(2)
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.WEST.nodeId != ID and rect.EAST not in cornerStitch_h.stitchList and rect.WEST in cornerStitch_h.stitchList:
                    t2 = constraint.constraint.Type.index(rect.WEST.cell.type)
                    t1 = constraint.constraint.Type.index(rect.cell.type)
                    # print "W",t1,t2
                    c = constraint.constraint(2)
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2)
                    # print "val", value
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST not in cornerStitch_h.stitchList and rect.WEST not in cornerStitch_h.stitchList:

                    c = constraint.constraint(0)
                    index = 0
                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type)
                    # print "val",value
                    e = Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.constraint.Type.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    # e = Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id)

                    # edgesh.append(Edge(origin, dest, value,index, str(constraint.constraint.Type.index(rect.cell.type)), id))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))




        dictList1 = []

        edgesh_new = copy.deepcopy(edgesh)
        for foo in edgesh_new:
            dictList1.append(foo.getEdgeDict())
        d1 = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d1[k].append(v)

        nodes = [x for x in range(len(self.ZDL_H[ID]))]


        for i in range(len(nodes) - 1):
            if (nodes[i], nodes[i + 1]) not in d1.keys():
                # print (nodes[i], nodes[i + 1])
                source = nodes[i]
                destination = nodes[i + 1]
                for edge in edgesh:
                    if (edge.dest == source or edge.source == source) and edge.index == 0:
                        t1 = constraint.constraint.type.index(edge.type)
                    elif (edge.source == destination or edge.dest == destination) and edge.index == 0:
                        t2 = constraint.constraint.type.index(edge.type)
                c = constraint.constraint(1)
                index = 1
                # value = int(constraint.constraint.getConstraintVal(c, source=t1, dest=t2)/(2**0.5))
                value = 1
                # e = Edge(origin, dest, value, index,type=None, id=None)
                edgesh_new.append(Edge(source, destination, value, index, type=None, id=None))
        dictList2 = []
        edgesv_new = copy.deepcopy(edgesv)
        for foo in edgesv_new:
            dictList2.append(foo.getEdgeDict())
        d2 = defaultdict(list)
        for i in dictList2:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d2[k].append(v)

        nodes = [x for x in range(len(self.ZDL_V[ID]))]

        for i in range(len(nodes) - 1):
            if (nodes[i], nodes[i + 1]) not in d2.keys():
                source = nodes[i]
                destination = nodes[i + 1]
                for edge in edgesv:
                    if (edge.dest == source or edge.source == source) and edge.index == 0:
                        t1 = constraint.constraint.type.index(edge.type)
                    elif (edge.source == destination or edge.dest == destination) and edge.index == 0:
                        t2 = constraint.constraint.type.index(edge.type)
                c = constraint.constraint(1)
                index = 1
                # value = int(constraint.constraint.getConstraintVal(c, source=t1, dest=t2) / (2 ** 0.5))
                value = 1
                # print value
                # e = Edge(origin, dest, value, index,type=None, id=None)
                edgesv_new.append(Edge(source, destination, value, index, type=None, id=None))

        self.edgesh_new[ID] = edgesh_new
        self.edgesv_new[ID] = edgesv_new

        self.edgesh[ID] = edgesh
        self.edgesv[ID] = edgesv

    '''

    print "H"
    for foo in edgesh_new:
        print "foo",foo.getEdgeDict()

    print "V"
    for foo in edgesv_new:
        print "foo", foo.getEdgeDict()
    '''

    def cgToGraph_h(self, name, ID, edgeh, parentID, level,N):
        # print ID
        G2 = nx.MultiDiGraph()
        dictList1 = []
        # print self.edgesh
        for foo in edgeh:
            # print "EDGE",foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        # print dictList1

        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        # print edge_labels1
        nodes = [x for x in range(len(self.ZDL_H[ID]))]
        G2.add_nodes_from(nodes)

        label = []

        edge_label = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []

            for internal_edge in edge_labels1[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[
                    1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}

                # print data,label

            # print data
            G2.add_weighted_edges_from(data)

        d = defaultdict(list)
        # print label
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        self.drawGraph_h(name, G2, edge_labels1)

        ######## LEVEL-1OPTIMIZATION(variable floorplan)

        #################################################################
        if level == 1:
            #print edge_label,len(edge_label)
            label4 = copy.deepcopy(label)
            #print "l3",len(label4),label4
            d3 = defaultdict(list)
            for i in label4:
                (k1), v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[(k1)].append(v)
            #print d3
            edgelabels={}
            for (k),v in d3.items():
                values=[]
                for j in range(len(v)):
                    values.append(v[j][0])
                value=max(values)
                for j in range(len(v)):
                    if v[j][0]==value:
                        edgelabels[(k)]=v[j]
            #print edgelabels

            D = []
            for i in range(N):

                EDGEH = []
                #for i in range(len(label4)):
                #for i in range(len(edgelabels)):
                for (k1), v in edgelabels.items():
                    edge = {}

                    #print (k1),v
                    if v[2] == 0:
                        if v[1] == '1':
                            val = int(min(40, max(10, random.gauss(20, 5))))
                            #print val,(10,40)
                            #val = random.randint(10, 40)
                        elif v[1] == '2':
                            val = int(min(30, max(8, random.gauss(20, 5))))
                            #print val,(8,30)
                            #val = random.randint(8, 30)
                            # val = 8
                        elif v[1] == '3':
                            val = int(min(40, max(20, random.gauss(20, 5))))
                            #print val,(20,40)
                            #val = random.randint(20,40)

                        elif v[1] == '4':
                            val = int(min(20, max(3, random.gauss(10, 5))))
                            #print val,(3,20)
                            #val = random.randint(3, 10)


                    elif v[2] == 1:
                        val = int(min(20, max(5, random.gauss(8, 5))))
                        #print val,(5,20)
                        #val = random.randint(5, 20)
                    else:
                        val = random.randint(5,20)
                    edge[(k1)] = val
                    EDGEH.append(edge)
                D.append(EDGEH)
            #print D



            #print paths

            D_3 = []
            for j in range(len(D)):
                d[j] = defaultdict(list)
                # print d[j]
                # print"N=", new_label[j]
                for i in D[j]:
                    # print i
                    # print new_label[j]
                    k, v = list(i.items())[
                        0]  # an alternative to the single-iterating inner loop from the previous solution

                    # print k,v
                    d[j][k].append(v)
                # print d[j]
                # print "d[j]",d[j]

                D_3.append(d[j])

            #print len(D_3), D_3
            H_all = []
            for i in range(len(D_3)):
                H = []
                for k, v in D_3[i].items():
                    H.append((k[0],k[1],v[0]))
                H_all.append(H)
            #print H_all
            G_all=[]
            for i in range(len(H_all)):


                G = nx.MultiDiGraph()
                n = list(G2.nodes())
                G.add_nodes_from(n)
                # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                G.add_weighted_edges_from(H_all[i])
                G_all.append(G)
            #print G_all
            loct = []
            for i in range(len(G_all)):
                new_Xlocation = []
                A = nx.adjacency_matrix(G_all[i])
                B = A.toarray()
                source=n[0]
                target=n[-1]
                X = {}
                for i in range(len(B)):

                    for j in range(len(B[i])):
                        # print B[i][j]

                        if B[i][j] != 0:
                            X[(i, j)] = B[i][j]

                Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
                for i in range(source, target + 1):
                    j = source
                    while j != target:
                        if B[j][i] != 0:
                            # print Matrix[j][i]
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        if i == source and j == source:
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        j += 1

                # print Pred
                n = list(Pred.keys())  ## list of all nodes
                # print n

                dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
                position = {}

                for j in range(source, target + 1):
                    # print j

                    node = j
                    for i in range(len(Pred[node])):
                        pred = Pred[node][i]

                        # print node, pred

                        if j == source:
                            dist[node] = (0, pred)
                            key = node
                            position.setdefault(key, [])
                            position[key].append(0)
                        else:
                            pairs = (max(position[pred]) + (X[(pred, node)]), pred)

                            # if dist[node][0]<pairs[0]:
                            # print pairs[0]
                            f = 0
                            for x, v in dist.items():
                                # print"x", x
                                if node == x:
                                    if v[0] > pairs[0]:
                                        # print "v", v[0]
                                        f = 1
                            if f == 0:
                                dist[node] = pairs

                            # value_1.append(X[(pred, node)])
                            key = node
                            position.setdefault(key, [])
                            position[key].append(pairs[0])

                        #print "dist=", dist, position
                loc_i = {}
                for key in position:
                    loc_i[key] = max(position[key])
                    # if key==n[-2]:
                    # loc_i[key] = 19
                    # elif key==n[-1]:
                    # loc_i[key] = 20
                    new_Xlocation.append(loc_i[key])
                loct.append(loc_i)
                #print"LOCT",locta

                self.NEWXLOCATION.append(new_Xlocation)


            """
            n = list(G2.nodes())
            self.FindingAllPaths_h(G2, n[0], n[-1])

            paths = self.paths_h
            loct = []
            for k in range(len(D_3)):
                new_Xlocation = []

                dist = {}
                distance = set()  ###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
                location = set()  ###No use
                position_k = {}  ## stores {node:location}
                for i in range(len(paths)):
                    path = paths[i]
                    # print path
                    for j in range(len(path)):
                        node = path[j]
                        # print "node=",path[-1]
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
                        # elif node== path[-1]:

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
                            # print position_k
                #print "POS",position_k
                loc_i = {}
                for key in position_k:
                    loc_i[key] = max(position_k[key])
                    # if key==n[-2]:
                    # loc_i[key] = 19
                    # elif key==n[-1]:
                    # loc_i[key] = 20
                    new_Xlocation.append(loc_i[key])
                loct.append(loc_i)
                #print loct

                self.NEWXLOCATION.append(new_Xlocation)
                """

            #print"X=", self.NEWXLOCATION
            n = list(G2.nodes())
            Location = {}
            key = ID
            Location.setdefault(key, [])

            for i in range(len(self.NEWXLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_H[ID])):
                    loct[self.ZDL_H[ID][j]] = self.NEWXLOCATION[i][j]
                Location[ID].append(loct)
            #print Location
            self.minLocationH = Location


        elif level == 2 or level ==3:

            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[k].append(v)
            print d3
            X = {}
            H = []
            for i, j in d3.items():
                X[i] = max(j)
            # print"X", X
            for k, v in X.items():
                H.append((k[0], k[1], v))
            print "H",H

            loct = []

            for i in range(N):
                self.Loc_X={}
                G = nx.MultiDiGraph()
                n = list(G2.nodes())
                G.add_nodes_from(n)
                # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                G.add_weighted_edges_from(H)
                # Draw(G)
                for k, v in self.XLoc.items():
                    if k in n:
                        self.Loc_X[k] = v
                #print "LOC_X", self.Loc_X
                #self.Loc_X = {n[0]: 0, n[-1]: self.W_T}
                #self.Loc_X = {n[0]: 0, n[1]: 5, n[3]: 15, n[4]: 20, n[6]: 30, n[7]: 35, n[9]: 45, n[10]: 50, n[12]: 60,n[14]: 65, n[16]: 100, n[17]: 120, n[-1]: self.W_T}
                self.FUNCTION(G)
                #print"FINX",self.Loc_X
                loct.append(self.Loc_X)

            for i in loct:
                new_x_loc = []
                for j, k in i.items():
                    new_x_loc.append(k)
                self.NEWXLOCATION.append(new_x_loc)
            #print "X=", self.NEWXLOCATION

            n = list(G2.nodes())
            Location = {}
            key = ID
            Location.setdefault(key, [])

            for i in range(len(self.NEWXLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_H[ID])):
                    loct[self.ZDL_H[ID][j]] = self.NEWXLOCATION[i][j]
                Location[ID].append(loct)
            #print Location
            self.minLocationH = Location


        else:

            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[
                    0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[k].append(v)
            # print d3
            X = {}
            H = []
            for i, j in d3.items():
                X[i] = max(j)
            #print"X", X
            for k, v in X.items():
                H.append((k[0], k[1], v))
            G = nx.MultiDiGraph()
            n = list(G2.nodes())
            G.add_nodes_from(n)
            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
            G.add_weighted_edges_from(H)
            A = nx.adjacency_matrix(G)
            B = A.toarray()
            # print B
            Location = {}
            for i in range(len(n)):
                if n[i] == 0:
                    Location[n[i]] = 0
                else:
                    k = 0
                    val = []
                    for j in range(len(B)):
                        if B[j][i] > k:
                            # k=B[j][i]
                            pred = j
                            val.append(Location[n[pred]] + B[j][i])
                    # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                    # loc2=Location[n[pred]]+k
                    Location[n[i]] = max(val)
            # print Location
            # Graph_pos_h = []

            dist = {}
            for node in Location:
                key = node

                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(Location[node])
            # Graph_pos_h.append(dist)
            # print Graph_pos_h
            # print"LOC=",Graph_pos_h
            #print "D",Location

            self.drawGraph_h_new(name, G2, edge_labels1, dist)
            csvfile=self.name1+'Min_X_Location.csv'
            location_file=self.name1 + 'Fixed_Loc.csv'

            with open(csvfile, 'wb') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["XNode", "Min Loc"])
                for key, value in Location.items():
                    writer.writerow([key, value])
            with open(location_file, 'wb') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["XNode", "Min Loc","xLoc"])
                for key, value in Location.items():
                    writer.writerow([key, value])

            LOC_H = {}
            for i in Location.keys():
                # print i,self.ZDL_H[ID][i]
                LOC_H[self.ZDL_H[ID][i]] = Location[i]
            # print LOC_H

            odH = collections.OrderedDict(sorted(LOC_H.items()))

            self.minLocationH[ID] = odH

            if parentID != None:
                # N=len(self.ZDL_H[parentID])
                KEYS = list(LOC_H.keys())

                parent_coord = []
                for k in self.ZDL_H[ID]:
                    if k in self.ZDL_H[parentID]:
                        parent_coord.append(k)
                # print ID,parentID,parent_coord,KEYS

                for i in range(len(parent_coord) - 1):
                    source = parent_coord[i]
                    destination = parent_coord[i + 1]
                    x = LOC_H[destination] - LOC_H[source]
                    origin = self.ZDL_H[parentID].index(source)
                    dest = self.ZDL_H[parentID].index(destination)
                    edge = (Edge(source=origin, dest=dest, constraint=x, index=1, type=None, id=None))
                    edgelist = self.edgesh_new[parentID]
                    edgelist.append(edge)
                    self.edgesh_new[parentID] = edgelist

                source = self.ZDL_H[parentID].index(min(KEYS))
                dest = self.ZDL_H[parentID].index(max(KEYS))
                # print self.edgesh_new[parentID]
                edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=None, id=None))
                # print edge.source,edge.dest,edge.constraint
                edgelist = self.edgesh_new[parentID]
                edgelist.append(edge)
                self.edgesh_new[parentID] = edgelist

    def FindingAllPaths_h(self, G, start, end):

        # f1 = open("paths_h.txt", 'w')
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
            # print >> f1, path

            # self.paths_h.append(path)
            # print "self.paths_h",self.paths_h

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

    def cgToGraph_v(self, name, ID, edgev, parentID, level,N):

        GV = nx.MultiDiGraph()
        dictList1 = []
        # print self.edgesh
        for foo in edgev:
            # print foo.getEdgeDict()
            dictList1.append(foo.getEdgeDict())
        # print dictList1

        ######
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        # print edge_labels1
        nodes = [x for x in range(len(self.ZDL_V[ID]))]
        GV.add_nodes_from(nodes)

        label = []

        edge_label = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []

            for internal_edge in edge_labels1[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[
                    1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}

                # print data,label

            # print data
            GV.add_weighted_edges_from(data)

        d = defaultdict(list)
        # print label
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        self.drawGraph_v(name, GV, edge_labels1)
        ######## LEVEL-1OPTIMIZATION(variable floorplan)

        #################################################################
        if level == 1:
            label4 = copy.deepcopy(label)
            # print "l3",len(label4),label4

            d3 = defaultdict(list)
            for i in label4:
                (k1), v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[(k1)].append(v)
            # print d3
            edgelabels = {}
            for (k), v in d3.items():
                values = []
                for j in range(len(v)):
                    values.append(v[j][0])
                value = max(values)
                for j in range(len(v)):
                    if v[j][0] == value:
                        edgelabels[(k)] = v[j]
            # print edgelabels

            D = []
            for i in range(N):

                EDGEV = []
                # for i in range(len(label4)):
                # for i in range(len(edgelabels)):

                for (k1), v in edgelabels.items():
                    edge = {}

                    # print (k1),v
                    if v[2] == 0:
                        if v[1] == '1':
                            val = int(min(40, max(10, random.gauss(20, 5))))
                            # print val,(10,40)
                            # val = random.randint(10, 40)
                        elif v[1] == '2':
                            val = int(min(30, max(8, random.gauss(20, 5))))
                            # print val,(8,30)
                            # val = random.randint(8, 30)
                            # val = 8
                        elif v[1] == '3':
                            val = int(min(40, max(20, random.gauss(20, 5))))
                            # print val,(20,40)
                            # val = random.randint(20,40)

                        elif v[1] == '4':
                            val = int(min(20, max(3, random.gauss(10, 5))))
                            # print val,(3,20)
                            # val = random.randint(3, 10)

                    elif v[2] == 1:
                        val = int(min(20, max(5, random.gauss(8, 5))))
                        # print val,(5,20)
                        # val = random.randint(5, 20)
                    else:
                        val = random.randint(5, 20)
                    edge[(k1)] = val
                    EDGEV.append(edge)
                D.append(EDGEV)
            # print D

            # print paths

            D_3 = []
            for j in range(len(D)):
                d[j] = defaultdict(list)
                # print d[j]
                # print"N=", new_label[j]
                for i in D[j]:
                    # print i
                    # print new_label[j]
                    k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution

                    # print k,v
                    d[j][k].append(v)
                # print d[j]
                # print "d[j]",d[j]

                D_3.append(d[j])

            # print len(D_3), D_3
            V_all = []
            for i in range(len(D_3)):
                V = []
                for k, v in D_3[i].items():
                    V.append((k[0], k[1], v[0]))
                V_all.append(V)
            # print H_all
            GV_all = []
            for i in range(len(V_all)):
                G = nx.MultiDiGraph()
                n = list(GV.nodes())
                G.add_nodes_from(n)
                # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                G.add_weighted_edges_from(V_all[i])
                GV_all.append(G)
            # print G_all
            locta = []
            for i in range(len(GV_all)):
                new_Ylocation = []
                A = nx.adjacency_matrix(GV_all[i])
                B = A.toarray()
                source = n[0]
                target = n[-1]
                X = {}
                for i in range(len(B)):

                    for j in range(len(B[i])):
                        # print B[i][j]

                        if B[i][j] != 0:
                            X[(i, j)] = B[i][j]

                Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
                for i in range(source, target + 1):
                    j = source
                    while j != target:
                        if B[j][i] != 0:
                            # print Matrix[j][i]
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        if i == source and j == source:
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        j += 1

                # print Pred
                n = list(Pred.keys())  ## list of all nodes
                # print n

                dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
                position = {}

                for j in range(source, target + 1):
                    # print j

                    node = j
                    for i in range(len(Pred[node])):
                        pred = Pred[node][i]

                        # print node, pred

                        if j == source:
                            dist[node] = (0, pred)
                            key = node
                            position.setdefault(key, [])
                            position[key].append(0)
                        else:
                            pairs = (max(position[pred]) + (X[(pred, node)]), pred)

                            # if dist[node][0]<pairs[0]:
                            # print pairs[0]
                            f = 0
                            for x, v in dist.items():
                                # print"x", x
                                if node == x:
                                    if v[0] > pairs[0]:
                                        # print "v", v[0]
                                        f = 1
                            if f == 0:
                                dist[node] = pairs

                            # value_1.append(X[(pred, node)])
                            key = node
                            position.setdefault(key, [])
                            position[key].append(pairs[0])

                        # print "dist=", dist, position
                loc_i = {}
                for key in position:
                    loc_i[key] = max(position[key])
                    # if key==n[-2]:
                    # loc_i[key] = 19
                    # elif key==n[-1]:
                    # loc_i[key] = 20
                    new_Ylocation.append(loc_i[key])
                locta.append(loc_i)
                #print"LOCT",locta

                self.NEWYLOCATION.append(new_Ylocation)
            """
            D = []
            for i in range(N):

                EDGEV = []
                for i in range(len(label4)):

                    edge = {}

                    for (k1), v in label4[i].items():

                        # print (k1),v
                        if v[2] == 0:
                            if v[1] == '1':
                                val = random.randint(10, 30)
                            elif v[1] == '2':
                                val = random.randint(8, 30)
                                # val = 8
                            elif v[1] == '3':
                                val = random.randint(6, 30)
                            elif v[1] == '4':
                                val = random.randint(3, 30)

                        elif v[2] == 1:
                            val = random.randint(5, 30)
                        else:
                            val = random.randint(5, 20)
                    edge[(k1)] = val
                    EDGEV.append(edge)
                D.append(EDGEV)
                # print len(EDGEH)
            # for i in D[0]:
            # print i
            # print "D",len(D)

            n = list(GV.nodes())
            self.FindingAllPaths_v(GV, n[0], n[-1])

            paths = self.paths_v
            #print paths

            D_3 = []
            for j in range(len(D)):
                d[j] = defaultdict(list)
                # print d[j]
                # print"N=", new_label[j]
                for i in D[j]:
                    # print i
                    # print new_label[j]
                    k, v = list(i.items())[
                        0]  # an alternative to the single-iterating inner loop from the previous solution

                    # print k,v
                    d[j][k].append(v)
                # print d[j]
                # print "d[j]",d[j]

                D_3.append(d[j])

            #print len(D_3), D_3

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
                        # print "node=",path[-1]
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
                        # elif node== path[-1]:

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
                            # print position_k
                loc_i = {}
                for key in position_k:
                    loc_i[key] = max(position_k[key])
                    # if key==n[-2]:
                    # loc_i[key] = 19
                    # elif key==n[-1]:
                    # loc_i[key] = 20
                    new_Ylocation.append(loc_i[key])
                loct.append(loc_i)
                print loct

                self.NEWYLOCATION.append(new_Ylocation)
            #print"Y=", self.NEWYLOCATION
            """
            Location = {}
            key = ID
            Location.setdefault(key, [])

            for i in range(len(self.NEWYLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_V[ID])):
                    loct[self.ZDL_V[ID][j]] = self.NEWYLOCATION[i][j]
                Location[ID].append(loct)
            #print Location
            self.minLocationV = Location

        elif level == 2 or level ==3:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[
                    0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[k].append(v)
            # print d3
            Y = {}
            V = []
            for i, j in d3.items():
                Y[i] = max(j)
            # print"X", X
            for k, v in Y.items():
                V.append((k[0], k[1], v))
            # print "H",H

            loct = []

            #self.Loc_Y = LOC_INIT

            for i in range(N):
                self.Loc_Y = {}
                G = nx.MultiDiGraph()
                n = list(GV.nodes())
                G.add_nodes_from(n)
                # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                G.add_weighted_edges_from(V)
                # Draw(G)
                for k, v in self.YLoc.items():
                    if k in n:
                        self.Loc_Y[k] = v
                #self.Loc_Y=self.YLoc

                #self.Loc_Y = {n[0]:INIT[0], n[-1]: INIT[-1]}
                self.FUNCTION_V(G)
                #print "FIN", self.Loc_Y
                loct.append(self.Loc_Y)
                #self.Loc_Y=LOC_INIT
                #self.Loc_Y.clear()

            for i in loct:
                new_y_loc = []
                for j, k in i.items():
                    new_y_loc.append(k)
                self.NEWYLOCATION.append(new_y_loc)
            #print  self.NEWYLOCATION

            Location = {}
            key = ID
            Location.setdefault(key, [])

            for i in range(len(self.NEWYLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_V[ID])):
                    loct[self.ZDL_V[ID][j]] = self.NEWYLOCATION[i][j]
                Location[ID].append(loct)
            #print Location
            self.minLocationV = Location
        else:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[
                    0]  # an alternative to the single-iterating inner loop from the previous solution
                d3[k].append(v)
            # print d3
            Y = {}
            V = []
            for i, j in d3.items():
                Y[i] = max(j)
            # print"X", X
            for k, v in Y.items():
                V.append((k[0], k[1], v))
            G = nx.MultiDiGraph()
            n = list(GV.nodes())
            G.add_nodes_from(n)
            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
            G.add_weighted_edges_from(V)
            A = nx.adjacency_matrix(G)
            B = A.toarray()
            # print B
            Location = {}
            for i in range(len(n)):
                if n[i] == 0:
                    Location[n[i]] = 0
                else:
                    k = 0
                    val = []
                    for j in range(len(B)):
                        if B[j][i] > k:
                            # k=B[j][i]
                            pred = j
                            val.append(Location[n[pred]] + B[j][i])
                    # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                    # loc2=Location[n[pred]]+k
                    Location[n[i]] = max(val)
            # print Location
            dist = {}
            for node in Location:
                key = node

                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(Location[node])
            # Graph_pos_h.append(dist)
            # print Graph_pos_h
            # print"LOC=",Graph_pos_h
            self.drawGraph_v_new(name, GV, edge_labels1, dist)
            csvfile = self.name1 + 'Min_Y_Location.csv'

            with open(csvfile, 'wb') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["YNode", "Min Loc"])
                for key, value in Location.items():
                    writer.writerow([key, value])
            #f1 = open(self.name1 + 'Fixed_Loc.csv', "r")  # open input file for reading




            with open(self.name1 + 'Fixed_Loc.csv', 'a') as csv_file:
                writer = csv.writer(csv_file, lineterminator = '\n')
                writer.writerow(["YNode", "Min Loc",'yLoc'])
                for key, value in Location.items():
                    writer.writerow([key, value])



            LOC_V = {}
            for i in Location.keys():
                # print i, self.ZDL_V[ID][i]
                LOC_V[self.ZDL_V[ID][i]] = Location[i]
            # print LOC_H
            odV = collections.OrderedDict(sorted(LOC_V.items()))
            self.minLocationV[ID] = odV

            if parentID != None:
                # N=len(self.ZDL_H[parentID])
                KEYS = list(LOC_V.keys())
                # print "KE", KEYS

                parent_coord = []
                for k in self.ZDL_V[ID]:
                    if k in self.ZDL_V[parentID]:
                        parent_coord.append(k)
                # print parent_coord

                for i in range(len(parent_coord) - 1):
                    source = parent_coord[i]
                    destination = parent_coord[i + 1]
                    y = LOC_V[destination] - LOC_V[source]
                    origin = self.ZDL_V[parentID].index(source)
                    dest = self.ZDL_V[parentID].index(destination)
                    edge = (Edge(source=origin, dest=dest, constraint=y, index=1, type=None, id=None))
                    edgelist = self.edgesv_new[parentID]
                    edgelist.append(edge)
                    self.edgesv_new[parentID] = edgelist

                source = self.ZDL_V[parentID].index(min(KEYS))
                dest = self.ZDL_V[parentID].index(max(KEYS))
                # print self.edgesh_new[parentID]
                edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=None, id=None))
                edgelist = self.edgesv_new[parentID]
                edgelist.append(edge)
                self.edgesv_new[parentID] = edgelist

    def FindingAllPaths_v(self, G, start, end):

        # f1 = open("paths_h.txt", 'w')
        visited = [False] * (len(G.nodes()))
        path = []

        self.printAllPaths_v(G, start, end, visited, path)

    def printAllPaths_v(self, G, start, end, visited, path):
        visited[start] = True
        path.append(start)

        # If current vertex is same as destination, then print
        # current path[]

        if start == end:
            saved_path = path[:]
            self.paths_v.append(saved_path)
            # for i in edge_labels1:
            # print >> f1, path

            # self.paths_h.append(path)
            # print "self.paths_h",self.paths_h

            # paths.append(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex

            for i in G.neighbors(start):
                if visited[i] == False:
                    self.printAllPaths_v(G, i, end, visited, path)

        # Remove current vertex from path[] and mark it as unvisited

        path.pop()
        visited[start] = False

        '''
        G = nx.MultiDiGraph()
        n = list(GV.nodes())
        G.add_nodes_from(n)
        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
        G.add_weighted_edges_from(V)
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        # print B
        Location = {}
        for i in range(len(n)):
            if n[i] == 0:
                Location[n[i]] = 0
            else:
                k = 0
                val = []
                for j in range(len(B)):
                    if B[j][i] > k:
                        # k=B[j][i]
                        pred = j
                        val.append(Location[n[pred]] + B[j][i])
                # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                # loc2=Location[n[pred]]+k
                Location[n[i]] = max(val)
        # print Location
        dist = {}
        for node in Location:
            key = node

            dist.setdefault(key, [])
            dist[node].append(node)
            dist[node].append(Location[node])
        # Graph_pos_h.append(dist)
        # print Graph_pos_h
        # print"LOC=",Graph_pos_h
        self.drawGraph_v_new(name, GV, edge_labels1, dist)


        LOC_V = {}
        for i in Location.keys():
            #print i, self.ZDL_V[ID][i]
            LOC_V[self.ZDL_V[ID][i]] = Location[i]
        # print LOC_H
        odV = collections.OrderedDict(sorted(LOC_V.items()))
        self.minLocationV[ID] = odV

        if parentID != None:
            # N=len(self.ZDL_H[parentID])
            KEYS = list(LOC_V.keys())
            # print "KE", KEYS

            parent_coord=[]
            for k in self.ZDL_V[ID]:
                if k in self.ZDL_V[parentID]:
                    parent_coord.append(k)
            #print parent_coord

            for i in range(len(parent_coord)-1):
                source=parent_coord[i]
                destination=parent_coord[i+1]
                y=LOC_V[destination]-LOC_V[source]
                origin=self.ZDL_V[parentID].index(source)
                dest=self.ZDL_V[parentID].index(destination)
                edge = (Edge(source=origin, dest=dest, constraint=y, index=1, type=None, id=None))
                edgelist = self.edgesv_new[parentID]
                edgelist.append(edge)
                self.edgesv_new[parentID] = edgelist


            source = self.ZDL_V[parentID].index(min(KEYS))
            dest = self.ZDL_V[parentID].index(max(KEYS))
            # print self.edgesh_new[parentID]
            edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=None, id=None))
            edgelist = self.edgesv_new[parentID]
            edgelist.append(edge)
            self.edgesv_new[parentID] = edgelist
            '''

        '''


        dist = {}
            distance = set()  ###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
            location = set()  ###No use
            position_k = {}  ## stores {node:location}
            for i in range(len(paths)):
                path = paths[i]
                # print path
                for j in range(len(path)):
                    node = path[j]
                    # print "node=",path[-1]
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
                    # elif node== path[-1]:

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
                        # print position_k
            loc_i = {}
            for key in position_k:
                loc_i[key] = max(position_k[key])
                # if key==n[-2]:
                # loc_i[key] = 19
                # elif key==n[-1]:
                # loc_i[key] = 20
                new_Xlocation.append(loc_i[key])
            loct.append(loc_i)



















        #### New graph with missing edges
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
            k, v = list(i.items())[0]
            d3[k].append(v)
        edge_labels3 = d3
        # print d.keys()
        # for u,v in d.keys():
        # print u,v

        nodes = [x for x in range(len(self.zeroDimensionListh))]
        G3.add_nodes_from(nodes)

        # print"label=", edge_labels1
        label3 = []
        label5 = []
        for branch in edge_labels3:
            lst_branch = list(branch)
            data = []

            for internal_edge in edge_labels3[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge[0]
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label3.append({(lst_branch[0], lst_branch[
                    1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                label5.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ######{(source,dest):weight}

            G3.add_weighted_edges_from(data)
        #############################################################
        # print label5

        d3 = defaultdict(list)
        for i in label5:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d3[k].append(v)
        # print d3
        X = {}
        for i, j in d3.items():
            # print i,max(j)
            X[i] = max(j)
        # print "X=", X
        for k, v in X.items():
            self.X.append((k[0], k[1], v))
        # print self.X

        loct = []
        for i in range(10):
            G = nx.MultiDiGraph()
            n = list(G3.nodes())
            G.add_nodes_from(n)
            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
            G.add_weighted_edges_from(self.X)
             A = nx.adjacency_matrix(G)
             B = A.toarray()
            # Draw(G)
            self.Loc_X = {n[0]: 0, n[-1]: self.W_T}
            self.FUNCTION(G)
            loct.append(self.Loc_X)

        for i in loct:
            new_x_loc = []
            for j, k in i.items():
                new_x_loc.append(k)
            self.NEWXLOCATION.append(new_x_loc)
        f3 = open(name + "location_x.txt", 'wb')

        for i in loct:
            # print i
            print >> f3, i
        print"LOC=", loct, self.NEWXLOCATION
        Graph_pos_h = []
        for i in range(len(loct)):
            dist = {}
            for node in loct[i]:
                key = node

                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(loct[i][node])
            Graph_pos_h.append(dist)

        ######## LEVEL-1OPTIMIZATION
        """
        #################################################################

        label4 = copy.deepcopy(label3)
        print "l3",label3

        D = []
        # print label3
        for i in label4:
            # print i.values()[0][1]
            if i.values()[0][1] == "1":
                D.append(i)

        # print D, len(D)
        W_total = []
        for i in range(10):
            W = []
            for i in range(len(D)):
                # W.append(randint(2, 10))
                W.append(random.randint(5, 15))
            W_total.append(W)
        # print "W_T=",W_total

        NewD = []
        for i in range(len(D)):
            NewD.append(D[i].keys()[0])
        Space = []
        for i in label4:
            if i.values()[0][1] == "0":
                Space.append(i)
        # print Space
        ############################ Varying Spacing
        S_total = []
        for i in range(10):
            S = []
            for i in range(len(Space)):
                S.append(random.randint(2, 5))
            S_total.append(S)
        # print "S_T=", S_total
        NewS = []
        for i in range(len(Space)):
            NewS.append(Space[i].keys()[0])
        # print "NEWD=", NewS
        new_labelw = []
        for j in range(len(W_total)):
            labelnew = []
            for i in range(len(NewD)):
                newdict = {NewD[i]: W_total[j][i]}
                labelnew.append(newdict)
                # labelnew.extend(Space)
            new_labelw.append(labelnew)
        # print new_labelw
        new_labels = []
        for j in range(len(S_total)):
            labelnew = []
            for i in range(len(NewS)):
                newdict = {NewS[i]: S_total[j][i]}
                labelnew.append(newdict)
            new_labels.append(labelnew)

        # print new_labels
        new_label = []
        for i in range(len(new_labels)):
            new_labels[i].extend(new_labelw[i])
            new_label.append(new_labels[i])
        # new_label
        # print "l4=", label4

        for i in range(len(new_label)):
            #
            new_label[i].extend(label5)
            # print new_label[i]

        # print new_label
        ################################

        # print len(new_label)
        # for i in new_label:
        # print i
        D_3 = []
        for j in range(len(new_label)):
            d[j] = defaultdict(list)
            # print d[j]
            # print"N=", new_label[j]
            for i in new_label[j]:
                # print i
                # print new_label[j]
                k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution

                # print k,v
                d[j][k].append(v)
            # print d[j]
            # print "d[j]",d[j]


            D_3.append(d[j])

        print len(D_3),D_3
        ###############################################################
        d3 = defaultdict(list)
        for i in label3:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d3[k].append(v)
        edge_labels3 = d3
        # print len(edge_labels3)


        #### Storing edge data in (u,v,w) format in a file(begin)
        z = [(u, v, d['weight']) for u, v, d in G3.edges(data=True)]
        f1 = open(name, 'w')
        for i in z:
            # print i
            print >> f1, i
        ######## Storing edge data in (u,v,w) format in a file(end)

        ######## Finds all possible paths from start vertex to end vertex(begin)
        n = list(G3.nodes())
        self.FindingAllPaths_h(G3, n[0], n[-1])

        paths = self.paths_h
        print paths
        #### (end)
        #### finding new location of each vertex in longest paths (begin)########


        ##############TESTING
        # NEWXLOCATION=[]
        loct = []
        for k in range(len(D_3)):
            new_Xlocation = []

            dist = {}
            distance = set()  ###stores (u,v,w)where u=parent,v=child,w=cumulative weight from source to child
            location = set()  ###No use
            position_k = {}  ## stores {node:location}
            for i in range(len(paths)):
                path = paths[i]
                # print path
                for j in range(len(path)):
                    node = path[j]
                    # print "node=",path[-1]
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
                    # elif node== path[-1]:

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
                        # print position_k
            loc_i = {}
            for key in position_k:
                loc_i[key] = max(position_k[key])
                # if key==n[-2]:
                # loc_i[key] = 19
                # elif key==n[-1]:
                # loc_i[key] = 20
                new_Xlocation.append(loc_i[key])
            loct.append(loc_i)

            self.NEWXLOCATION.append(new_Xlocation)
        f3 = open(name + "location_x.txt", 'wb')
        for i in loct:
            # print i
            print >> f3, i
        print"LOC=", loct, self.NEWXLOCATION
        Graph_pos_h = []
        for i in range(len(loct)):
            dist = {}
            for node in loct[i]:
                key = node

                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(loct[i][node])
            Graph_pos_h.append(dist)
        # print Graph_pos_h
        # print"LOC=",Graph_pos_h
        self.drawGraph_h_new(name, G3, D_3, Graph_pos_h)


        #######
        """

        ######################### Handling special edges independently

        special_edge_h = []  ### list of edges which are of type"1"  and in same nodes
        # for foo in self.edgesh_new:
        # print "Y"
        # print foo.id,foo.type,foo.source,foo.dest
        for i in range(len(self.edgesh_new) - 1):
            for j in range(len(self.edgesh_new) - 1):
                if j == i:
                    continue
                if self.edgesh_new[i].source == self.edgesh_new[j].source and self.edgesh_new[i].dest == \
                        self.edgesh_new[j].dest and self.edgesh_new[i].type == self.edgesh_new[j].type == '1':
                    if self.edgesh_new[i] not in special_edge_h:
                        special_edge_h.append(self.edgesh_new[i])
                    if self.edgesh_new[j] not in special_edge_h:
                        special_edge_h.append(self.edgesh_new[j])

                        # print special_edge_h
                        # for foo in special_edge_h:
                        # print "hfo", foo.getEdgeDict()
        # for foo in special_edge_h:
        # print "hfo", foo.getEdgeDict(),foo.id,foo.East,foo.West
        ######## Removing all of those edges which have connected neighbor edges of type 1 incoming to source or outgoing of dest
        EAST = []
        WEST = []
        NORTHWEST = []
        SOUTHEAST = []
        for edge in special_edge_h:
            EAST.append(edge.East)
            WEST.append(edge.West)
            NORTHWEST.append(edge.northWest)
            SOUTHEAST.append(edge.southEast)
        # print"E=", EAST,WEST
        for edge in special_edge_h:
            if edge.West != None or edge.id in EAST or edge.id in WEST:
                special_edge_h = [x for x in special_edge_h if x != edge]
            elif edge.East != None or edge.id in EAST or edge.id in WEST:
                special_edge_h = [x for x in special_edge_h if x != edge]
            elif edge.northWest != None or edge.id in NORTHWEST or edge.id in SOUTHEAST:
                special_edge_h = [x for x in special_edge_h if x != edge]
            elif edge.southEast != None or edge.id in NORTHWEST or edge.id in SOUTHEAST:
                special_edge_h = [x for x in special_edge_h if x != edge]

        # print "len=", len(special_edge_h)
        # for edge in special_edge_h:
        # print edge.source,edge.dest,edge.id,edge.type
        # self.special_edgeh = copy.deepcopy(special_edge_h)
        self.special_edgeh = copy.deepcopy(special_edge_h)
        for i in range(len(special_edge_h)):
            self.special_cell_id_h.append(special_edge_h[i].id)

        if len(special_edge_h) > 0:
            # W_max = []
            # OFFSET=[]

            for i in range(len(loct)):
                ######### Calculating offset values and determining new location of edge's source and dest node
                # for i in loct[i]:
                # print loct[i]
                special_location_x = []
                Wmax = []
                for edge in special_edge_h:
                    w = loct[i][edge.dest] - loct[i][edge.source]
                    # print w
                    Wmax.append(w)
                min = constraint.constraint.minWidth[1]
                offset1 = []
                offset2 = []
                for j in range(len(Wmax)):
                    # print Wmax[j]
                    if Wmax[j] > min:
                        offset_1 = random.randrange(0, (Wmax[j] - min) / (3 / 2))
                        offset_2 = random.randrange(0, (Wmax[j] - offset_1 - min))
                    else:
                        offset_1 = 0
                        offset_2 = 0



                    offset1.append(offset_1)
                    offset2.append(offset_2)

                # print offset1, offset2
                # OFFSET.append([offset1, offset2])
                for j in range(len(special_edge_h)):
                    location = {}
                    key = special_edge_h[j].id
                    location.setdefault(key, [])
                    # print"id=",special_edge_h[j].id
                    # print loct[i]
                    location[key].append(loct[i][special_edge_h[j].source] + offset1[j])
                    location[key].append(loct[i][special_edge_h[j].dest] - offset2[j])
                    location[key].append(Wmax[j] - (offset1[j] + offset2[j]))
                    special_location_x.append(location)
                    # print'lo',special_location_x
                self.special_location_x.append(
                    special_location_x)  ######[[{special cell id_1:[x1,x2,width]},{special cell id_2:[x1,x2,width]}],[{special cell id_1:[x1,x2,width]},{special cell id_2:[x1,x2,width]},......]]
            # print self.special_location_x

        ##### Fixed floorplan width  #################
    '''

    def FUNCTION(self, G):
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        # print (A.todense())
        # print B
        Fixed_Node = self.Loc_X.keys()
        Fixed_Node.sort()
        # print "F", Fixed_Node

        Splitlist = []
        for i, j in G.edges():
            # print i,j
            for node in G.nodes():
                if node in self.Loc_X.keys() and node > i and node < j:
                    edge = (i, j)
                    if edge not in Splitlist:
                        Splitlist.append(edge)
        # print Splitlist
        med = {}
        for i in Splitlist:
            start = i[0]
            end = i[1]

            for node in Fixed_Node:
                if node > start and node < end:
                    key = (start, end)
                    med.setdefault(key, [])
                    med[key].append(node)
        # print med

        for i, v in med.items():
            # print i,v

            start = i[0]
            end = i[-1]
            succ = v

            # print succ
            s = start
            e = end
            # print "s,e", s, e
            # if len(succ)>1:
            if s in Fixed_Node or e in Fixed_Node:
                for i in range(len(succ)):
                    self.edge_split(s, succ[i], e, Fixed_Node, B)
                    if len(succ) > 1:
                        s = succ[i]

        # print B
        for i in Fixed_Node:
            for j in Fixed_Node:
                if G.has_edge(i, j):
                    G.remove_edge(i, j)
        # Draw(G)
        nodes = list(G.nodes())
        Node_List = []
        for i in range(len(Fixed_Node) - 1):
            node = [Fixed_Node[i]]
            for j in nodes:
                if j not in node and j >= Fixed_Node[i] and j <= Fixed_Node[i + 1]:
                    node.append(j)
            if len(node) > 2:
                Node_List.append(node)
        # print Node_List

        Connected_List = []
        for k in range(len(Node_List)):
            for m in range(len(Node_List)):
                LIST = []
                for i in range(len(B)):
                    for j in range(len(B)):
                        if i in Node_List[k] and j in Node_List[m]:
                            if i not in Node_List[m] and j not in Node_List[k]:
                                if B[i][j] != 0:
                                    # LIST.append(Node_List[k])
                                    # LIST.append(Node_List[m])
                                    LIST = Node_List[k] + Node_List[m]
                if len(LIST) > 0:
                    Connected_List.append(list(set(LIST)))
                    # if LIST not in Connected_List:
                    # Connected_List.append(LIST)
        # print Connected_List

        if len(Connected_List) > 0:
            for i in range(len(Connected_List)):
                PATH = Connected_List[i]
                # print Connected_List[0][0]
                start = PATH[0]
                end = PATH[-1]
                # print start, end
                SOURCE = []
                for i in range(len(PATH) - 1):
                    if PATH[i] in self.Loc_X.keys():
                        SOURCE.append(PATH[i])

                # print SOURCE
                TARGET = []
                for i in range(1, len(PATH)):
                    if PATH[i] in self.Loc_X.keys():
                        TARGET.append(PATH[i])

                # print TARGET
                self.Location_finding(B, start, end, SOURCE, TARGET, flag=True)
                Fixed_Node = self.Loc_X.keys()
                # print "FIXED", Fixed_Node

                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION(G)
        else:
            # print Node_List
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))
            # print H
            for graph in H:
                Fixed_Node = self.Loc_X.keys()

                n = list(graph.nodes())
                n.sort()
                start = n[0]
                end = n[-1]
                # print start, end
                self.Location_finding(B, start, end, SOURCE=None, TARGET=None, flag=False)

            Fixed_Node = self.Loc_X.keys()
            # print "FIXED", Fixed_Node

            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)
                        # B[i][j] = 0
            # Draw(G)
            # print G.edges()
            if len(G.edges()) == 0:
                # print "Y"
                return
            # if (G.edges()==None):
            # return

            else:
                self.FUNCTION(G)

    #### finding new location of each vertex in longest paths (end)########

    def randomvaluegenerator(self, Range, value, Max):
        variable = []
        D_V_Newval = [0]
        # n=len(D_V_change)

        while (len(value) > 1):
            # print value
            i = 0
            n = len(value)
            # print"n", n
            v = Range - sum(D_V_Newval)
            # print v
            if ((v) / (n / 2)) >0:
                x = random.randrange(0, ((v) / (n / 2)))
            else:
                x = 0
            # print "x", x
            D_V_Newval.append(x)
            p = value.pop(i)
            # print p
            variable.append(x + p)
            # print variable
        variable.append(Max - sum(variable))
        # random.shuffle(variable)
        return variable

    def LONGEST_PATH(self, B, source, target):
        X = {}
        for i in range(len(B)):

            for j in range(len(B[i])):
                # print B[i][j]

                if B[i][j] != 0:
                    X[(i, j)] = B[i][j]

        for i in range(source, target):  ### adding missing edges between 2 fixed nodes
            # print i, i + 1
            j = i + 1
            if B[i][j] == 0 and i in self.Loc_X.keys() and j in self.Loc_X.keys():
                X[(i, i + 1)] = self.Loc_X[i + 1] - self.Loc_X[i]
                B[i][j] = self.Loc_X[i + 1] - self.Loc_X[i]

        Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
        for i in range(source, target + 1):
            j = source
            while j != target:
                if B[j][i] != 0:
                    # print Matrix[j][i]
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                if i == source and j == source:
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                j += 1

        # print Pred
        n = list(Pred.keys())  ## list of all nodes
        # print n

        dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
        position = {}

        for j in range(source, target + 1):
            # print j

            node = j
            for i in range(len(Pred[node])):
                pred = Pred[node][i]

                # print node, pred

                if j == source:
                    dist[node] = (0, pred)
                    key = node
                    position.setdefault(key, [])
                    position[key].append(0)
                else:
                    pairs = (max(position[pred]) + (X[(pred, node)]), pred)

                    # if dist[node][0]<pairs[0]:
                    # print pairs[0]
                    f = 0
                    for x, v in dist.items():
                        # print"x", x
                        if node == x:
                            if v[0] > pairs[0]:
                                # print "v", v[0]
                                f = 1
                    if f == 0:
                        dist[node] = pairs

                    # value_1.append(X[(pred, node)])
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])

                # print "dist=", dist, position

        i = target
        path = []
        while i > source:

            if i not in path:
                path.append(i)
            i = dist[i][1]
            # print i
            path.append(i)
        # print path
        PATH = list(reversed(path))  ## Longest path
        # print PATH
        Value = []
        for i in range(len(PATH) - 1):
            # print (PATH[i],PATH[i+1])
            if (PATH[i], PATH[i + 1]) in X.keys():
                Value.append(X[(PATH[i], PATH[i + 1])])
        # print Value
        Max = sum(Value)
        # print Max

        return PATH, Value, Max

    def edge_split(self, start, med, end, Fixed_Node, B):
        f = 0
        if start in Fixed_Node and med in Fixed_Node:
            f = 1
            Diff = self.Loc_X[med] - self.Loc_X[start]
            Weight = B[start][end]
            if B[med][end] < Weight - Diff:
                B[med][end] = Weight - Diff
        elif end in Fixed_Node and med in Fixed_Node:
            f = 1
            Diff = self.Loc_X[end] - self.Loc_X[med]
            Weight = B[start][end]
            if B[start][med] < Weight - Diff:
                B[start][med] = Weight - Diff
        # print"s",start,end
        if f == 1:
            B[start][end] = 0

        return

    def Evaluation_connected(self, B, PATH, SOURCE, TARGET):
        # print B, PATH

        Fixed = self.Loc_X.keys()
        # print Fixed
        UnFixed = []
        for i in PATH:
            if i not in Fixed:
                UnFixed.append(i)
        # print UnFixed
        while (len(UnFixed)) > 0:
            Min_val = {}
            # Val=LONGEST_PATH(B,0,4)
            # print "Val",Val[2]
            for i in SOURCE:

                for j in UnFixed:
                    key = j
                    Min_val.setdefault(key, [])
                    # if B[i][j]!=0:
                    Val = self.LONGEST_PATH(B, i, j)
                    # print i,j,Val[2]
                    if Val[2] != 0:
                        x = (self.Loc_X[i] + Val[2])
                        Min_val[key].append(x)
            # print Min_val
            Max_val = {}
            for i in UnFixed:

                for j in TARGET:
                    key = i
                    Max_val.setdefault(key, [])
                    # if B[i][j]!=0:
                    Val = self.LONGEST_PATH(B, i, j)
                    # print i,j,Val[2]

                    if Val[2] != 0:
                        x = (self.Loc_X[j] - Val[2])
                        Max_val[key].append(x)
            # print Max_val

            # for i in UnFixed:
            i = UnFixed.pop(0)
            v_low = max(Min_val[i])
            # v_h1=LOC[i]
            v_h2 = min(Max_val[i])
            v1 = v_low
            # v2=max(v_h1,v_h2)
            v2 = v_h2
            # print v_low, v2
            # self.Loc_X[i] = random.randrange(v1, v2)
            if v1 < v2:
                self.Loc_X[i] = random.randrange(v1, v2)
            else:
                self.Loc_X[i] = max(v1, v2)
            SOURCE.append(i)
            TARGET.append(i)

    def Location_finding(self, B, start, end, SOURCE, TARGET, flag):

        PATH, Value, Sum = self.LONGEST_PATH(B, start, end)
        if flag == True:
            self.Evaluation_connected(B, PATH, SOURCE, TARGET)
        else:
            Max = self.Loc_X[end] - self.Loc_X[start]

            Range = Max - Sum
            variable = self.randomvaluegenerator(Range, Value, Max)
            loc = {}
            for i in range(len(PATH)):
                if PATH[i] in self.Loc_X:
                    # continue
                    loc[PATH[i]] = self.Loc_X[PATH[i]]
                else:
                    loc[PATH[i]] = self.Loc_X[PATH[i - 1]] + variable[i - 1]
                    self.Loc_X[PATH[i]] = self.Loc_X[PATH[i - 1]] + variable[i - 1]
            # print loc, self.Loc_X

        return

    ###########################################################
    # LEVEL-1 OPTMIZATION
    def FindingAllPaths_h(self, G, start, end):

        # f1 = open("paths_h.txt", 'w')
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
            # print >> f1, path

            # self.paths_h.append(path)
            # print "self.paths_h",self.paths_h

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

        ###################################################################################################################
        ##### Fixed floorplan width  #################

    def EDGE_SPLITTER(self, G, Fixed_Node, B):

        Splitlist = []
        for i, j in G.edges():
            # print i,j
            for node in G.nodes():
                if node in self.Loc_Y.keys() and node > i and node < j:
                    edge = (i, j)
                    if edge not in Splitlist:
                        Splitlist.append(edge)
        # print "SP", Splitlist
        med = {}
        for i in Splitlist:
            start = i[0]
            end = i[1]

            for node in Fixed_Node:
                if node > start and node < end:
                    key = (start, end)
                    med.setdefault(key, [])
                    med[key].append(node)
        # print med

        for i, v in med.items():
            # print i,v

            start = i[0]
            end = i[-1]
            succ = v

            # print succ
            s = start
            e = end
            # print "s,e", s, e
            # if len(succ)>1:
            if s in Fixed_Node or e in Fixed_Node:
                for i in range(len(succ)):
                    self.edge_split_V(s, succ[i], e, Fixed_Node, B)
                    if len(succ) > 1:
                        s = succ[i]

        # print B
        for i in Fixed_Node:
            for j in Fixed_Node:
                if G.has_edge(i, j):
                    G.remove_edge(i, j)
        return G

    def FUNCTION_V(self, G):
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        # print (A.todense())
        # print B

        Fixed_Node = self.Loc_Y.keys()
        Fixed_Node.sort()
        # G=self.EDGE_SPLITTER(G,Fixed_Node,B)
        # print "F1", Fixed_Node,self.Loc_Y

        Splitlist = []
        for i, j in G.edges():
            # print i,j
            for node in G.nodes():
                if node in self.Loc_Y.keys() and node > i and node < j:
                    edge = (i, j)
                    if edge not in Splitlist:
                        Splitlist.append(edge)
        # print "SP", Splitlist
        med = {}
        for i in Splitlist:
            start = i[0]
            end = i[1]

            for node in Fixed_Node:
                if node > start and node < end:
                    key = (start, end)
                    med.setdefault(key, [])
                    med[key].append(node)
        # print med

        for i, v in med.items():
            # print i,v

            start = i[0]
            end = i[-1]
            succ = v

            # print succ
            s = start
            e = end
            # print "s,e", s, e
            # if len(succ)>1:
            if s in Fixed_Node or e in Fixed_Node:
                for i in range(len(succ)):
                    self.edge_split_V(s, succ[i], e, Fixed_Node, B)
                    if len(succ) > 1:
                        s = succ[i]

        # print B
        for i in Fixed_Node:
            for j in Fixed_Node:
                if G.has_edge(i, j):
                    # print i,j
                    G.remove_edge(i, j)
                    # B[i][j]=0

        # Draw(G)
        nodes = list(G.nodes())
        # print "F",Fixed_Node,nodes
        Node_List = []
        for i in range(len(Fixed_Node) - 1):
            node = [Fixed_Node[i]]
            for j in nodes:
                if j not in node and j >= Fixed_Node[i] and j <= Fixed_Node[i + 1]:
                    # print j
                    node.append(j)
            # print node
            if len(node) > 2:
                Node_List.append(node)
        # print Node_List

        Connected_List = []
        for k in range(len(Node_List)):
            for m in range(len(Node_List)):
                LIST = []
                for i in range(len(B)):
                    for j in range(len(B)):
                        if i in Node_List[k] and j in Node_List[m]:
                            if i not in Node_List[m] and j not in Node_List[k]:
                                if B[i][j] != 0:
                                    # print i,j
                                    # LIST.append(Node_List[k])
                                    # LIST.append(Node_List[m])
                                    # print Node_List[k],Node_List[m]
                                    LIST = Node_List[k] + Node_List[m]
                if len(LIST) > 0:
                    Connected_List.append(list(set(LIST)))
                    # if LIST not in Connected_List:
                    # Connected_List.append(LIST)
        # print Connected_List

        if len(Connected_List) > 0:
            for i in range(len(Connected_List)):

                PATH = Connected_List[i]
                # print Connected_List[0][0]
                start = PATH[0]
                end = PATH[-1]
                # print start, end
                SOURCE = []
                for i in range(len(PATH) - 1):
                    if PATH[i] in self.Loc_Y.keys():
                        SOURCE.append(PATH[i])

                # print SOURCE
                SOURCE.sort()
                TARGET = []
                for i in range(1, len(PATH)):
                    if PATH[i] in self.Loc_Y.keys():
                        TARGET.append(PATH[i])

                # print TARGET
                TARGET.sort()
                self.Location_finding_V(B, start, end, SOURCE, TARGET, flag=True)
                Fixed_Node = self.Loc_Y.keys()
                # print "FIXED", Fixed_Node

                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION_V(G)
        else:
            # print Node_List
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))
            # print H
            for graph in H:
                Fixed_Node = self.Loc_Y.keys()
                # print "F", Fixed_Node
                '''
                Splitlist = []
                for i, j in graph.edges():
                    # print i,j
                    for node in G.nodes():
                        if node in Loc.keys() and node > i and node < j:
                            edge = (i, j)
                            if edge not in Splitlist:
                                Splitlist.append(edge)
                print Splitlist
                med = {}
                for i in Splitlist:
                    start = i[0]
                    end = i[1]

                    for node in Fixed_Node:
                        if node > start and node < end:
                            key = (start, end)
                            med.setdefault(key, [])
                            med[key].append(node)
                print med

                for i, v in med.items():
                    print i, v

                    start = i[0]
                    end = i[-1]
                    succ = v

                    print succ
                    s = start
                    e = end
                    print "s,e", s, e
                    # if len(succ)>1:
                    if s in Fixed_Node or e in Fixed_Node:
                        for i in range(len(succ)):
                            edge_split(s, succ[i], e, Fixed_Node, B)
                            if len(succ) > 1:
                                s = succ[i]

                print B
                '''

                # Draw(G)
                n = list(graph.nodes())
                # print n
                n.sort()
                start = n[0]
                end = n[-1]
                # print start, end
                self.Location_finding_V(B, start, end, SOURCE=None, TARGET=None, flag=False)
                '''
                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if graph.has_edge(i, j):
                            graph.remove_edge(i, j)
                '''

            Fixed_Node = self.Loc_Y.keys()
            # print "FIXED", Fixed_Node

            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)
                        # B[i][j] = 0
            # Draw(G)
            # print G.edges()
            if len(G.edges()) == 0:
                # print "Y"
                return
            # if (G.edges()==None):
            # return

            else:
                self.FUNCTION_V(G)

    #### finding new location of each vertex in longest paths (end)########

    def randomvaluegenerator_V(self, Range, value, Max):
        variable = []
        D_V_Newval = [0]
        # n=len(D_V_change)

        while (len(value) > 1):
            # print value
            i = 0
            n = len(value)
            # print"n", n
            v = Range - sum(D_V_Newval)
            # print v
            if ((v) / (n / 2)) > 0:
                x = random.randrange(0, ((v) / (n / 2)))
            else:
                x = 0
            # print "x", x
            D_V_Newval.append(x)
            p = value.pop(i)
            # print p
            variable.append(x + p)
            # print variable
        variable.append(Max - sum(variable))
        # random.shuffle(variable)
        return variable

    def LONGEST_PATH_V(self, B, source, target):
        X = {}
        for i in range(len(B)):

            for j in range(len(B[i])):
                # print B[i][j]

                if B[i][j] != 0:
                    X[(i, j)] = B[i][j]

        # print"X", X
        for i in range(source, target):
            # print i,i+1
            j = i + 1
            if B[i][j] == 0 and i in self.Loc_Y.keys() and j in self.Loc_Y.keys():
                X[(i, i + 1)] = self.Loc_Y[i + 1] - self.Loc_Y[i]
                B[i][j] = self.Loc_Y[i + 1] - self.Loc_Y[i]

        Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
        for i in range(source, target + 1):
            j = source
            # print "T",target
            # print B
            while j != target:
                # print j
                if B[j][i] != 0:
                    # print Matrix[j][i]
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                if i == source and j == source:
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                j += 1

        # print Pred,self.Loc_Y
        n = list(Pred.keys())  ## list of all nodes
        # print n

        dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
        position = {}

        for j in range(source, target + 1):
            # print"j", j,Pred[j],target
            # if j in n:
            node = j
            # else:
            # continue

            for i in range(len(Pred[node])):
                # print i,Pred[node]
                pred = Pred[node][i]

                # print node, pred

                if j == source:
                    dist[node] = (0, pred)
                    key = node
                    position.setdefault(key, [])
                    position[key].append(0)
                else:
                    pairs = (max(position[pred]) + (X[(pred, node)]), pred)

                    # if dist[node][0]<pairs[0]:
                    # print pairs[0]
                    f = 0
                    for x, v in dist.items():
                        # print"x", x
                        if node == x:
                            if v[0] > pairs[0]:
                                # print "v", v[0]
                                f = 1
                    if f == 0:
                        dist[node] = pairs

                    # value_1.append(X[(pred, node)])
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])
                    # print position

                # print "dist=", dist, position

        i = target
        path = []
        while i > source:

            if i not in path:
                path.append(i)
            i = dist[i][1]
            # print i
            path.append(i)
        # print path
        PATH = list(reversed(path))  ## Longest path
        # print PATH
        Value = []
        for i in range(len(PATH) - 1):
            # print (PATH[i],PATH[i+1])
            if (PATH[i], PATH[i + 1]) in X.keys():
                Value.append(X[(PATH[i], PATH[i + 1])])
        # print Value
        Max = sum(Value)
        # print Max

        return PATH, Value, Max

    def edge_split_V(self, start, med, end, Fixed_Node, B):
        f = 0
        if start in Fixed_Node and med in Fixed_Node:
            f = 1
            Diff = self.Loc_Y[med] - self.Loc_Y[start]
            Weight = B[start][end]
            if B[med][end] < Weight - Diff:
                B[med][end] = Weight - Diff
        elif end in Fixed_Node and med in Fixed_Node:
            f = 1
            Diff = self.Loc_Y[end] - self.Loc_Y[med]
            Weight = B[start][end]
            if B[start][med] < Weight - Diff:
                B[start][med] = Weight - Diff
        # print"s",start,end
        if f == 1:
            B[start][end] = 0

        return

    def Evaluation_connected_V(self, B, PATH, SOURCE, TARGET):
        # print B, PATH

        Fixed = self.Loc_Y.keys()
        # print Fixed
        UnFixed = []
        for i in PATH:
            if i not in Fixed:
                UnFixed.append(i)
        # print UnFixed
        while len(UnFixed) > 0:
            # Fixed = self.Loc_Y.keys()
            Min_val = {}
            # Val=LONGEST_PATH(B,0,4)
            # print "Val",Val[2]
            for i in SOURCE:

                for j in UnFixed:
                    key = j
                    Min_val.setdefault(key, [])
                    # if B[i][j]!=0:
                    Val = self.LONGEST_PATH_V(B, i, j)
                    # print i,j,Val[2]
                    if Val[2] != 0:
                        x = (self.Loc_Y[i] + Val[2])
                        Min_val[key].append(x)
            # print Min_val
            Max_val = {}
            for i in UnFixed:

                for j in TARGET:
                    key = i
                    Max_val.setdefault(key, [])
                    # if B[i][j]!=0:
                    Val = self.LONGEST_PATH_V(B, i, j)
                    # print i,j,Val[2]

                    if Val[2] != 0:
                        x = (self.Loc_Y[j] - Val[2])
                        Max_val[key].append(x)
            # print Max_val
            '''
            start=PATH[0]
            end=PATH[-1]
            PATH, Value, Sum = LONGEST_PATH(B, start, end)
            Max = Loc[end] - Loc[start]

            Range = Max - Sum
            variable = randomvaluegenerator(Range, Value, Max)
            LOC=copy.deepcopy(Loc)
            print variable,LOC

            loc = {}
            for i in range(len(PATH)):
                if PATH[i] in LOC:
                    # continue
                    loc[PATH[i]] = LOC[PATH[i]]
                else:
                    loc[PATH[i]] = LOC[PATH[i - 1]] + variable[i - 1]
                    LOC[PATH[i]] = LOC[PATH[i - 1]] + variable[i - 1]
            print loc, Loc
            '''
            i = UnFixed.pop(0)
            # for i in UnFixed:
            # if i==UnFixed[0]:
            v_low = max(Min_val[i])
            # v_h1=LOC[i]
            v_h2 = min(Max_val[i])
            v1 = v_low
            # v2=max(v_h1,v_h2)
            v2 = v_h2
            # print i,v1,v2
            if v1 < v2:
                self.Loc_Y[i] = random.randrange(v1, v2)
            else:
                self.Loc_Y[i] = max(v1, v2)
            # UnFixed.pop(i)
            SOURCE.append(i)
            TARGET.append(i)

    def Location_finding_V(self, B, start, end, SOURCE, TARGET, flag):
        # print B,start,end,self.Loc_Y.keys()

        PATH, Value, Sum = self.LONGEST_PATH_V(B, start, end)
        if flag == True:
            self.Evaluation_connected_V(B, PATH, SOURCE, TARGET)
        else:
            # print "s",start,end
            Max = self.Loc_Y[end] - self.Loc_Y[start]

            Range = Max - Sum
            variable = self.randomvaluegenerator_V(Range, Value, Max)
            loc = {}
            for i in range(len(PATH)):
                if PATH[i] in self.Loc_Y:
                    # continue
                    loc[PATH[i]] = self.Loc_Y[PATH[i]]
                else:
                    loc[PATH[i]] = self.Loc_Y[PATH[i - 1]] + variable[i - 1]
                    self.Loc_Y[PATH[i]] = self.Loc_Y[PATH[i - 1]] + variable[i - 1]
            # print loc, self.Loc_X

        return

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

    #####################################################
    # LEVEL-1 OPTIMIZATION
    def FindingAllPaths_v(self, G, start, end):

        # f1 = open("paths_v.txt", 'w')
        visited = [False] * (len(G.nodes()))
        path = []
        self.printAllPaths_v(G, start, end, visited, path)

    def printAllPaths_v(self, G, start, end, visited, path):
        visited[start] = True
        path.append(start)
        # If current vertex is same as destination, then print
        # current path[]
        if start == end:
            saved_path = path[:]
            self.paths_v.append(saved_path)
            # print >> f1, path
        else:
            for i in G.neighbors(start):

                if visited[i] == False:
                    self.printAllPaths_v(G, i, end, visited, path)
        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[start] = False

    ####################################################################

    def drawGraph_h(self, name, G2, edge_labels1):
        # print "NAME",name
        # edge_labels1 = self.merge_dicts(dictList1)
        edge_colors1 = ['black' for edge in G2.edges()]
        pos = nx.shell_layout(G2)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw_networkx_labels(G2, pos)
        nx.draw(G2, pos, node_color='red', node_size=300, edge_color=edge_colors1)
        # nx.draw(G, pos, node_color='red', node_size=300, edge_color=edge_colors)
        # plt.show()
        plt.savefig(self.name1 + name + 'gh.png')
        plt.close()

    def drawGraph_h_new(self, name, G2, edge_labels1, loc):

        # for i in range(len(loc)):
        # edge_labels1 = self.merge_dicts(dictList1)
        edge_colors1 = ['black' for edge in G2.edges()]
        pos = nx.shell_layout(G2)
        nx.draw_networkx_labels(G2, pos, labels=loc)
        nx.draw_networkx_edge_labels(G2, pos, edge_labels=edge_labels1)
        nx.draw(G2, pos, node_color='red', node_size=900, edge_color=edge_colors1)
        plt.savefig(self.name2 + '-' + name + 'location_h.png')
        plt.close()
        # pylab.show()

    def drawGraph_v(self, name2, G1, edge_labels):

        #######

        edge_colors = ['black' for edge in G1.edges()]
        pos = nx.shell_layout(G1)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw_networkx_labels(G1, pos)
        nx.draw(G1, pos, node_color='red', node_size=300, edge_color=edge_colors)
        plt.savefig(self.name2 + name2 + 'gv.png')
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
        # app = Viewer(G1)
        # app.mainloop()

        # pylab.show()

    def drawGraph_v_new(self, name2, G1, edge_labels, loc):

        #######
        # for i in range(len(loc)):
        edge_colors = ['black' for edge in G1.edges()]
        pos = nx.shell_layout(G1)

        nx.draw_networkx_labels(G1, pos, labels=loc)
        nx.draw_networkx_edge_labels(G1, pos, edge_labels=edge_labels)
        nx.draw(G1, pos, node_color='red', node_size=900, edge_color=edge_colors)
        plt.savefig(self.name2 + '-' + name2 + 'location_v.png')
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
        self.diGraph1.add_nodes_from(sourceGraph.cgToGraph1().nodes(data=True))
        self.diGraph1.add_edges_from(sourceGraph.cgToGraph1().edges(data=True))
        self.diGraph2 = nx.MultiDiGraph()
        self.diGraph2.add_nodes_from(sourceGraph.cgToGraph2().nodes(data=True))
        self.diGraph2.add_edges_from(sourceGraph.cgToGraph2().edges(data=True))

    def addEdge(self, source, dest, constraint):
        self.diGraph.add_edge(source, dest, constraint, weight=constraint.getConstraintVal())

    def drawGraph1(self):
        G = self.diGraph1
        edge_Labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])
        # for foo in list(edge_Labels):
        # print foo

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(self.diGraph1)
        nx.draw_networkx_edge_labels(self.diGraph1, pos, edge_labels=edge_Labels)
        nx.draw_networkx_labels(self.diGraph1, pos)
        nx.draw(self.diGraph1, pos, node_color='white', node_size=300, edge_color=edge_colors, arrows=True)

        pylab.show()

    def drawGraph2(self):
        G = self.diGraph2
        edge_Labels = dict([((u, v,), d['weight'])
                            for u, v, d in G.edges(data=True)])
        # for foo in list(edge_Labels):
        # print foo

        edge_colors = ['black' for edge in G.edges()]

        pos = nx.shell_layout(self.diGraph2)
        nx.draw_networkx_edge_labels(self.diGraph2, pos, edge_labels=edge_Labels)
        nx.draw_networkx_labels(self.diGraph2, pos)
        nx.draw(self.diGraph2, pos, node_color='white', node_size=300, edge_color=edge_colors, arrows=True)

        pylab.show()

    def edgeReduce(self):
        """Eliminate redundant edges"""

    def vertexReduce(self):
        """Eliminate redundant vertices"""
        return


class Edge():
    def __init__(self, source, dest, constraint, index, type, id, East=None, West=None, North=None, South=None,
                 northWest=None,
                 westNorth=None, southEast=None, eastSouth=None):
        self.source = source
        self.dest = dest
        self.constraint = constraint
        self.index = index
        self.type = type
        self.id = id
        self.East = East
        self.West = West
        self.North = North
        self.South = South
        self.northWest = northWest
        self.westNorth = westNorth
        self.southEast = southEast
        self.eastSouth = eastSouth
        self.setEdgeDict()

    def getConstraint(self):
        return self.constraint

    def setEdgeDict(self):
        self.edgeDict = {(self.source, self.dest): [self.constraint, self.type, self.index]}
        # self.edgeDict = {(self.source, self.dest): self.constraint.constraintval}

    def getEdgeDict(self):
        return self.edgeDict

    def getEdgeWeight(self, source, dest):
        return self.getEdgeDict()[(self.source, self.dest)]

    def printEdge(self):
        print "s: ", self.source, "d: ", self.dest, "con = ", self.constraint.printCon()