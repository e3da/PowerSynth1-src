'''
Updated from December,2017
@ author: Imam Al Razi(ialrazi)
'''

from sets import Set
import constraint
import networkx as nx
from collections import defaultdict
import collections
import copy
import random
from random import randrange


#########################################################################################################################


class constraintGraph:
    """
    the graph representation of constraints pertaining to cells and variables, informed by several different
    sources
    """

    def __init__(self,W=None,H=None,XLocation=None,YLocation=None,path=None,name=None):
        """
        Default constructor
        """

        self.zeroDimensionListh = []  ### All X cuts of tiles
        self.zeroDimensionListv = []  ### All Y cuts of tiles
        self.NEWXLOCATION = []  ####Array of all X locations after optimization
        self.NEWYLOCATION = []  ####Array of all Y locations after optimization
        self.path = path
        self.name = name
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
        self.W_T =W
        self.H_T =H
        self.XLoc = XLocation
        self.YLoc= YLocation
        self.voltage_constraint={}
        self.current_constraint = {}
        self.seed_h=[]
        self.seed_v=[]



    def graphFromLayer(self, H_NODELIST, V_NODELIST, level,N=None,seed=None,individual=None,Types=None):
        """

        :param H_NODELIST: Horizontal node list from horizontal tree
        :param V_NODELIST: Vertical node list from vertical tree
        :param level: mode of operation
        :param N: Number of layout solutions to be generated
        :return:
        """
        """
        given a cornerStitch, construct a constraint graph detailing the dependencies of
        one dimension point to another
        self.dimListFromLayer(cornerStitch_h, cornerStitch_v)
        self.setEdgesFromLayer(cornerStitch_h, cornerStitch_v)
        """

        # Here only those nodes are considered which have children in the tree
        self.HorizontalNodeList = []
        self.VerticalNodeList = []
        for node in H_NODELIST:
            if node.child == []:
                continue
            else:
                self.HorizontalNodeList.append(node) # only appending all horizontal tree nodes which have children. Nodes having no children are not included

        for node in V_NODELIST:
            if node.child == []:
                continue
            else:
                self.VerticalNodeList.append(node)# only appending all vertical tree nodes which have children. Nodes having no children are not included



        Key = []
        ValueH = []
        ValueV = []
        for i in range(len(self.HorizontalNodeList)):
            Key.append(self.HorizontalNodeList[i].id)
            k, j = self.dimListFromLayer(self.HorizontalNodeList[i], self.VerticalNodeList[i])
            ValueH.append(k)
            ValueV.append(j)

        # All horizontal cut coordinates combined from both horizontal and vertical corner stitch
        ZDL_H = dict(zip(Key, ValueH))

        # All vertical cut coordinates combined from both horizontal and vertical corner stitch
        ZDL_V = dict(zip(Key, ValueV))

        # Ordered dictionary of horizontal cuts where key is node id and value is a list of coordinates
        self.ZDL_H = collections.OrderedDict(sorted(ZDL_H.items()))

        # Ordered dictionary of vertical cuts where key is node id and value is a list of coordinates
        self.ZDL_V = collections.OrderedDict(sorted(ZDL_V.items()))


        # setting up edges for constraint graph from corner stitch tiles using minimum constraint values
        for i in range(len(self.HorizontalNodeList)):
            self.setEdgesFromLayer(self.HorizontalNodeList[i], self.VerticalNodeList[i],Types)

        # _new are after adding missing edges
        self.edgesh_new = collections.OrderedDict(sorted(self.edgesh_new.items()))
        self.edgesv_new = collections.OrderedDict(sorted(self.edgesv_new.items()))


        for k, v in list(self.edgesh_new.iteritems())[::-1]:

            ID, edgeh = k, v
            for i in self.HorizontalNodeList:
                if i.id == ID:
                    if i.parent != None:
                        parent = i.parent.id
                    else:
                        parent = None

            # Function to create horizontal constraint graph using edge information
            #print "ind", individual
            if individual!=None:
                individual_h = individual[:len(self.ZDL_H[ID])]
            else:
                individual_h=None

            self.cgToGraph_h(ID, self.edgesh_new[ID], parent, level,N,seed,individual_h)

        for k, v in list(self.edgesv_new.iteritems())[::-1]:
            ID, edgev = k, v
            for i in self.VerticalNodeList:
                if i.id == ID:
                    if i.parent != None:
                        parent = i.parent.id

            # Function to create vertical constraint graph using edge information

            if individual!=None:
                #print len(individual), len(self.ZDL_H[ID]), len(self.ZDL_V[ID])
                individual_v = individual[len(self.ZDL_H[ID]):]
                #print "ind",individual_v
            else:
                individual_v=None
            self.cgToGraph_v(ID, self.edgesv_new[ID], parent, level,N,seed,individual_v)

    #####  constraint graph evaluation after randomization to determine each node new location
    def minValueCalculation(self, hNodeList, vNodeList, level):
        """

        :param hNodeList: horizontal node list
        :param vNodeList: vertical node list
        :param level: mode of operation
        :return: evaluated X and Y locations for mode-0
        """
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
            return self.minX, self.minY

    # only minimum x location evaluation
    def set_minX(self, node):
        """

        :param node: node of the tree
        :return: minimum x locations for that node(mode-0)
        """
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


    # only minimum y location evaluation
    def set_minY(self, node):
        """

        :param node: node of a tree
        :return: minimum Y locations for that node(mode-0)
        """
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


    def dimListFromLayer(self, cornerStitch_h, cornerStitch_v):
        """

        :param cornerStitch_h: horizontal corner stitch for a node
        :param cornerStitch_v: vertical corner stitch for a node
        :return:
        """
        """
        generate the zeroDimensionList from a cornerStitch (horizontal and vertical cuts)
        """

        pointSet_v = Set()  # this is a set of zero dimensional line coordinates, (e.g. x0, x1, x2, etc.)
        max_y = 0
        for rect in cornerStitch_v.stitchList:
            pointSet_v.add(rect.cell.y)
            pointSet_v.add(rect.cell.y + rect.getHeight())
            if max_y < rect.cell.y + rect.getHeight():
                max_y = rect.cell.y + rect.getHeight()

        pointSet_v.add(max_y)

        for rect in cornerStitch_h.stitchList:
            pointSet_v.add(rect.cell.y)
            pointSet_v.add(rect.cell.y + rect.getHeight())
            if max_y < rect.cell.y + rect.getHeight():
                max_y = rect.cell.y + rect.getHeight()

        pointSet_v.add(max_y)
        setToList_v = list(pointSet_v)
        setToList_v.sort()

        pointSet_h = Set()
        max_x = 0
        for rect in cornerStitch_v.stitchList:
            pointSet_h.add(rect.cell.x)
            pointSet_h.add(rect.cell.x + rect.getWidth())
            if max_x < rect.cell.x + rect.getWidth():
                max_x = rect.cell.x + rect.getWidth()

        pointSet_h.add(max_x)
        for rect in cornerStitch_h.stitchList:
            pointSet_h.add(rect.cell.x)
            pointSet_h.add(rect.cell.x + rect.getWidth())
            if max_x < rect.cell.x + rect.getWidth():
                max_x = rect.cell.x + rect.getWidth()
        pointSet_h.add(max_x)
        setToList_h = list(pointSet_h)
        setToList_h.sort()

        return setToList_h, setToList_v

    # finding patterns for shared x,y coordinates tiles, where to foreground and one background tile is associated with same coordinate
    def shared_coordinate_pattern(self,cornerStitch_h,cornerStitch_v,ID):
        """

        :param cornerStitch_h: horizontal corner stitch for a node
        :param cornerStitch_v: vertical corner stitch for a node
        :param ID: node Id
        :return: patterns for both horizontal and vertical corner stitch which has either shared X or Y coordinate. List of tuples of pairs of those tiles
        """

        # to hold tiles which share same y coordinate in the form: [{'bottom':[T1,T2,..],'top':[T3,T4,...],'back':[T5,T6,...]},{}]
        # 'bottom' holds those tiles which bottom edge is shared at Y, 'top' holds those tiles which top edge is shared at Y, 'back' holds those tiles which are background and either top or bottom edge is shared at Y
        init_list_H = []
        for y in self.ZDL_V[ID]:

            dict_y={}
            rects=[]
            fore=0
            for rect in cornerStitch_h.stitchList:
                if rect.cell.y==y or rect.NORTH.cell.y==y:
                    rects.append(rect)
                    if rect.nodeId!=ID:
                        fore+=1
            if fore>1: # if there are atleast two foreground tiles we may need to think of pattern finding
                bottom=[]
                top=[]
                back=[]
                for r in rects:
                    if r.cell.y==y and r.nodeId!=ID:
                        bottom.append(r)
                    elif r.NORTH.cell.y==y and r.nodeId!=ID:
                        top.append(r)
                    elif r.nodeId==ID:
                        back.append(r)
                dict_y['bottom']=bottom
                dict_y['top']=top
                dict_y['back']=back
            else:
                continue
            init_list_H.append(dict_y)

         # to hold tiles which share same y coordinate in the form: [{'bottom':[T1,T2,..],'top':[T3,T4,...],'back':[T5,T6,...]},{..}]
        # 'bottom' holds those tiles which bottom edge is shared at Y, 'top' holds those tiles which top edge is shared at Y, 'back' holds those tiles which are background and either top or bottom edge is shared at Y
        init_list_V = []
        for x in self.ZDL_H[ID]:
            dict_x = {}
            rects = []
            fore = 0
            for rect in cornerStitch_v.stitchList:
                if rect.cell.x == x or rect.EAST.cell.x == x:
                    rects.append(rect)
                    if rect.nodeId != ID:
                        fore += 1
            if fore > 1:  # if there are atleast two foreground tiles we may need to think of pattern finding
                right = []
                left = []
                back = []
                for r in rects:
                    if r.cell.x == x and r.nodeId != ID:
                        left.append(r)
                    elif r.EAST.cell.x == x and r.nodeId != ID:
                        right.append(r)
                    elif r.nodeId == ID:
                        back.append(r)
                dict_x['right'] = right
                dict_x['left'] = left
                dict_x['back'] = back
            else:
                continue
            init_list_V.append(dict_x)

        Final_List_H = []
        for i in init_list_H:
            for j in i['bottom']:
                for k in i['top']:
                    if j.eastSouth(j) == k.northWest(k) and j.eastSouth(j) in i['back']:
                        if j.cell.x<k.cell.x:
                            Final_List_H.append((j, k))
                        else:
                            Final_List_H.append((k, j))
                    elif j.SOUTH == k.EAST and j.SOUTH in i['back']:
                        if j.cell.x < k.cell.x:
                            Final_List_H.append((j, k))
                        else:
                            Final_List_H.append((k, j))
                    else:
                        continue
        Final_List_V=[]
        for i in init_list_V:
            for j in i['right']:
                for k in i['left']:
                    if j.southEast(j)==k.westNorth(k) and j.southEast(j) in i['back']:
                        if j.cell.y < k.cell.y:
                            Final_List_V.append((j, k))
                        else:
                            Final_List_V.append((k, j))
                    elif j.EAST==k.SOUTH and j.EAST in i['back']:
                        if j.cell.y < k.cell.y:
                            Final_List_V.append((j, k))
                        else:
                            Final_List_V.append((k, j))
                    else:
                        continue
        return Final_List_H,Final_List_V

    ## creating edges from corner stitched tiles
    def setEdgesFromLayer(self, cornerStitch_h, cornerStitch_v,Types):


        ID = cornerStitch_h.id # node id
        Horizontal_patterns, Vertical_patterns = self.shared_coordinate_pattern(cornerStitch_h, cornerStitch_v, ID)
        n1 = len(self.ZDL_H[ID])
        n2 = len(self.ZDL_V[ID])
        self.vertexMatrixh[ID] = [[[] for i in range(n1)] for j in range(n1)]
        self.vertexMatrixv[ID] = [[[] for i in range(n2)] for j in range(n2)]
        edgesh = []
        edgesv = []

        # creating vertical constraint graph edges
        """
        for each tile in vertical corner-stitched layout find the constraint depending on the tile's position. If the tile has a background tile, it's node id is different than the background tile.
        So that tile is a potential min height candidate.index=0:min width,1: min spacing, 2:min enclosure,3:min extension,4:minheight. For vertical corner-stitched layout min height is associated
        with tiles, min width is for horizontal corner stitched tile. 
        
        """
        for rect in cornerStitch_v.stitchList:
            Extend_h = 0 # to find if horizontal extension is there
            #if rect.nodeId != ID:
            origin = self.ZDL_H[ID].index(rect.cell.x) # if horizontal extension needs to set up node in horizontal constraint graph
            dest = self.ZDL_H[ID].index(rect.getEast().cell.x) # if horizontal extension needs to set up node in horizontal constraint graph
            origin1=self.ZDL_V[ID].index(rect.cell.y) # finding origin node in vertical constraint graph for min height constraned edge
            dest1=self.ZDL_V[ID].index(rect.getNorth().cell.y)# finding destination node in vertical constraint graph for min height constraned edge
            id = rect.cell.id
            # if a tile has completely shared right edge with another tile of same type it should be a horizontal extension
            if rect.getEast().nodeId == rect.nodeId:
                East = rect.getEast().cell.id
                if rect.southEast(rect).nodeId == rect.nodeId:
                    if rect.southEast(rect).cell==rect.getEast().cell and rect.NORTH.nodeId==ID and rect.SOUTH.nodeId==ID:
                        Extend_h=1
            else:
                East = None

            # if a tile has completely shared left edge with another tile of same type it should be a horizontal extension
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

            # this tile has a minheight constraint between it's bottom and top edge
            c = constraint.constraint(4) # index=4 means minheight constraint
            index = 4


            value = constraint.constraint.getConstraintVal(c,type=rect.cell.type,Types=Types)


            e = Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id, East,West, northWest, southEast)

            edgesv.append(Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id, East,West, northWest, southEast)) # appending edge for vertical constraint graph

            self.vertexMatrixv[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest)) # updating vertical constraint graph adjacency matrix


            if Extend_h==1: # if its a horizontal extension
                c = constraint.constraint(3) # index=3 means minextension type constraint
                index = 3
                rect.vertex1 = origin
                rect.vertex2 = dest
                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, East,West, northWest, southEast)
                edgesh.append(Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, East,West, northWest, southEast)) # appending in horizontal constraint graph edges
                self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest)) # updating horizontal constraint graph matrix

            origin = origin1
            dest = dest1
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

            # checking if its min spacing or not: if its spacing current tile's north and south tile should be foreground tiles (nodeid should be different)
            if rect.NORTH.nodeId != ID and rect.SOUTH.nodeId != ID and rect.NORTH in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:

                t2 = Types.index(rect.NORTH.cell.type)
                t1 = Types.index(rect.SOUTH.cell.type)

                c = constraint.constraint(1)  # index=1 means min spacing constraint
                index = 1
                value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, North,
                         South, westNorth, eastSouth)
                edgesv.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth))
                self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

            # checking for minimum enclosure constraint: if current tile is bottom tile its north tile should be foreground tile and south tile should be boundary tile and not in stitchlist

            #elif rect.NORTH.nodeId != ID and rect.SOUTH not in cornerStitch_v.stitchList and rect.NORTH in cornerStitch_v.stitchList:
            elif rect.NORTH.nodeId != ID and (rect.SOUTH.cell.type == "EMPTY" or rect.SOUTH not in cornerStitch_v.stitchList):


                t2 = Types.index(rect.NORTH.cell.type)
                t1 = Types.index(rect.cell.type)
                c = constraint.constraint(2)  # index=2 means enclosure constraint
                index = 2
                value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth)
                edgesv.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth))
                self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

            # checking for minimum enclosure constraint: if current tile is top tile its south tile should be foreground tile and north tile should be boundary tile and not in stitchlist
            #elif rect.SOUTH.nodeId != ID and rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
            elif rect.SOUTH.nodeId != ID and (rect.NORTH.cell.type == "EMPTY" or rect.NORTH not in cornerStitch_v.stitchList):
                t2 = Types.index(rect.SOUTH.cell.type)
                t1 =Types.index(rect.cell.type)
                c = constraint.constraint(2)  # index=2 means min enclosure constraint
                index = 2
                value =constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth)

                edgesv.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth))
                self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

            # if current tile is stretched from bottom to top, it's a complete background tile and should be a min height constraint generator. It's redundant actually as this tile will be considered
            # as foreground tile in its background plane's cornerstitched layout, there it will be again considered as min height constraint generator.
            elif rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH not in cornerStitch_v.stitchList:
                c = constraint.constraint(4)  # index=4 means minheight constraint
                index = 4

                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth)
                edgesv.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         North, South, westNorth, eastSouth))
                self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))




            '''
            else: # if current tile has same id as current node: means current tile is a background tile. for a background tile there are 2 options:1.min spacing,2.min enclosure
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

                # checking if its min spacing or not: if its spacing current tile's north and south tile should be foreground tiles (nodeid should be different)
                if rect.NORTH.nodeId != ID and rect.SOUTH.nodeId != ID and rect.NORTH in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
                    t2 = constraint.Types.index(rect.NORTH.cell.type)
                    t1 = constraint.Types.index(rect.SOUTH.cell.type)

                    c = constraint.constraint(1) # index=1 means min spacing constraint
                    index = 1
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id, North, South, westNorth, eastSouth)
                    edgesv.append(Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # checking for minimum enclosure constraint: if current tile is bottom tile its north tile should be foreground tile and south tile should be boundary tile and not in stitchlist
                elif rect.NORTH.nodeId != ID and rect.SOUTH not in cornerStitch_v.stitchList and rect.NORTH in cornerStitch_v.stitchList:
                    t2 = constraint.Types.index(rect.NORTH.cell.type)
                    t1 = constraint.Types.index(rect.cell.type)
                    c = constraint.constraint(2) # index=2 means enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)
                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # checking for minimum enclosure constraint: if current tile is top tile its south tile should be foreground tile and north tile should be boundary tile and not in stitchlist
                elif rect.SOUTH.nodeId != ID and rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
                    t2 = constraint.Types.index(rect.SOUTH.cell.type)
                    t1 = constraint.Types.index(rect.cell.type)
                    c = constraint.constraint(2) # index=2 means min enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # if current tile is stretched from bottom to top, it's a complete background tile and should be a min height constraint generator. It's redundant actually as this tile will be considered
                # as foreground tile in its background plane's cornerstitched layout, there it will be again considered as min height constraint generator.
                elif rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH not in cornerStitch_v.stitchList:
                    c = constraint.constraint(4) # index=4 means minheight constraint
                    index = 4

                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth)
                    edgesv.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

            
            '''

        '''
        creating edges for horizontal constraint graph from horizontal cornerstitched tiles. index=0: min width, index=1: min spacing, index=2: min Enclosure, index=3: min extension
        same as vertical constraint graph edge generation. all north are now east, south are now west. if vertical extension rule is applicable to any tile vertical constraint graph is generated.
        voltage dependent spacing for empty tiles and current dependent widths are applied for foreground tiles.
        
        '''
        for rect in cornerStitch_h.stitchList:
            Extend_v = 0
            #if rect.nodeId != ID:
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
            index = 0 # min width constraint

            value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
            e = Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id, North,
                     South, westNorth, eastSouth)

            edgesh.append(Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id, North,South, westNorth, eastSouth))
            self.vertexMatrixh[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest))


            if Extend_v==1:
                c = constraint.constraint(3)
                index = 3 # min extension
                rect.vertex1 = origin
                rect.vertex2 = dest
                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, North,
                         South, westNorth, eastSouth)

                edgesv.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, North,
                         South, westNorth, eastSouth))
                self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

            origin = origin1
            dest = dest1
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
                t2 = Types.index(rect.EAST.cell.type)
                t1 = Types.index(rect.WEST.cell.type)

                c = constraint.constraint(1)
                index = 1
                value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, East,
                         West, northWest, southEast)

                edgesh.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast))
                self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
            #elif rect.EAST.nodeId != ID and rect.WEST not in cornerStitch_h.stitchList and rect.EAST in cornerStitch_h.stitchList:
            elif rect.EAST.nodeId != ID and (rect.WEST.cell.type == "EMPTY" or rect.WEST not in cornerStitch_h.stitchList):

                t2 = Types.index(rect.EAST.cell.type)
                t1 = Types.index(rect.cell.type)
                c = constraint.constraint(2)  # min enclosure constraint
                index = 2
                value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast)

                edgesh.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast))
                self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
            #elif rect.WEST.nodeId != ID and rect.EAST not in cornerStitch_h.stitchList and rect.WEST in cornerStitch_h.stitchList:
            elif rect.WEST.nodeId != ID and (rect.EAST.cell.type == "EMPTY" or rect.EAST not in cornerStitch_h.stitchList):
                t2 = Types.index(rect.WEST.cell.type)
                t1 = Types.index(rect.cell.type)
                c = constraint.constraint(2)  # min enclosure constraint
                index = 2
                value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast)

                edgesh.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast))
                self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
            elif rect.EAST not in cornerStitch_h.stitchList and rect.WEST not in cornerStitch_h.stitchList:

                c = constraint.constraint(0)
                index = 0

                value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast)

                edgesh.append(
                    Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                         East, West, northWest, southEast))
                self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
            '''
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
                    t2 = constraint.Types.index(rect.EAST.cell.type)
                    t1 = constraint.Types.index(rect.WEST.cell.type)

                    c = constraint.constraint(1)
                    index = 1
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id, East, West, northWest, southEast)

                    edgesh.append( Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST.nodeId != ID and rect.WEST not in cornerStitch_h.stitchList and rect.EAST in cornerStitch_h.stitchList:
                    t2 = constraint.Types.index(rect.EAST.cell.type)
                    t1 = constraint.Types.index(rect.cell.type)
                    c = constraint.constraint(2) # min enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.WEST.nodeId != ID and rect.EAST not in cornerStitch_h.stitchList and rect.WEST in cornerStitch_h.stitchList:
                    t2 = constraint.Types.index(rect.WEST.cell.type)
                    t1 = constraint.Types.index(rect.cell.type)
                    c = constraint.constraint(2) #min enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST not in cornerStitch_h.stitchList and rect.WEST not in cornerStitch_h.stitchList:

                    c = constraint.constraint(0)
                    index = 0

                    value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                    e = Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(constraint.Types.index(rect.cell.type)), id,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
            '''
        ## adding missing edges for shaed coordinate patterns
        for i in Horizontal_patterns:
            r1=i[0]
            r2=i[1]
            origin=self.ZDL_H[ID].index(r1.EAST.cell.x)
            dest=self.ZDL_H[ID].index(r2.cell.x)
            t2 = Types.index(r2.cell.type)
            t1 = Types.index(r1.cell.type)
            c = constraint.constraint(1) #sapcing constraints
            index = 1

            value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
            e = Edge(origin, dest, value, index, type=None,id=None)
            edgesh.append(Edge(origin, dest, value, index, type=None,id=None))
            self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

        for i in Vertical_patterns:
            r1 = i[0]
            r2 = i[1]
            origin = self.ZDL_V[ID].index(r1.NORTH.cell.y)
            dest = self.ZDL_V[ID].index(r2.cell.y)
            t2 = Types.index(r2.cell.type)
            t1 = Types.index(r1.cell.type)
            c = constraint.constraint(1)
            index = 1

            value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
            e = Edge(origin, dest, value, index,type=None,id=None)

            edgesv.append(
                Edge(origin, dest, value, index,type=None,id=None))
            self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))


        dictList1 = []
        types = [str(i) for i in range(len(Types))]
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
                        t1 = types.index(edge.type)
                    elif (edge.source == destination or edge.dest == destination) and edge.index == 0:
                        t2 = types.index(edge.type)
                c = constraint.constraint(1)
                index = 1
                value = 1000      # still there maybe some missing edges .Adding a value of spacing to maintain relative  location
                edgesh_new.append(Edge(source, destination, value, index, type=None, id=None))

        dictList2 = []
        edgesv_new = copy.deepcopy(edgesv)
        for foo in edgesv_new:
            dictList2.append(foo.getEdgeDict())
        d2 = defaultdict(list)
        for i in dictList2:
            k, v = list(i.items())[0]
            d2[k].append(v)


        nodes = [x for x in range(len(self.ZDL_V[ID]))]
        for i in range(len(nodes) - 1):
            if (nodes[i], nodes[i + 1]) not in d2.keys():
                source = nodes[i]
                destination = nodes[i + 1]
                for edge in edgesv:
                    if (edge.dest == source or edge.source == source) and edge.index == 0:
                        t1 = types.index(edge.type)
                    elif (edge.source == destination or edge.dest == destination) and edge.index == 0:
                        t2 = types.index(edge.type)
                c = constraint.constraint(1)
                index = 1
                value = 1000 # still there maybe some missing edges .Adding a value of spacing to maintain relative  location
                edgesv_new.append(Edge(source, destination, value, index, type=None, id=None))
        self.edgesh_new[ID] = edgesh_new
        self.edgesv_new[ID] = edgesv_new

        self.edgesh[ID] = edgesh
        self.edgesv[ID] = edgesv


    def cgToGraph_h(self, ID, edgeh, parentID, level,N,seed,individual):
        '''
        :param ID: Node ID
        :param edgeh: horizontal edges for that node's constraint graph
        :param parentID: node id of it's parent
        :param level: mode of operation
        :param N: number of layouts to be generated
        :return: constraint graph and solution for different modes
        '''

        G2 = nx.MultiDiGraph() # initializing a multigraph
        dictList1 = []
        for foo in edgeh:
            dictList1.append(foo.getEdgeDict())

        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]
            d[k].append(v)
        edge_labels1 = d # creating edge labels in dictionary format, where key is the tuple of edge source and destination vertices and value is the list of edges in between the key vertices
        nodes = [x for x in range(len(self.ZDL_H[ID]))] # list of vertices for a node's horizontal constraint graph
        G2.add_nodes_from(nodes)
        label = []
        edge_label = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels1[branch]:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}
            G2.add_weighted_edges_from(data)

        d = defaultdict(list)
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d

        ######## Mode based evaluation

        #################################################################

        # mode-1: variable floorplan size
        if level == 1:
            label4 = copy.deepcopy(label)
            d3 = defaultdict(list)
            for i in label4:
                (k1), v = list(i.items())[0]
                d3[(k1)].append(v)
            edgelabels={}
            for (k),v in d3.items():
                values=[]
                for j in range(len(v)):
                    values.append(v[j][0])
                value=max(values)
                for j in range(len(v)):
                    if v[j][0]==value:
                        edgelabels[(k)]=v[j] # among multiple edges the highest edge weight is dominated for evaluation

            # Added to perform optimization on mode-1
            d4 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d4[k].append(v)
            X = {}
            H = []
            for i, j in d4.items():
                X[i] = max(j)  # keeping dominating edge weights among multiple edges

            for k, v in X.items():
                H.append((k[0], k[1], v))

            # print "LEN",H
            G = nx.MultiDiGraph()
            n = list(G2.nodes())
            G.add_nodes_from(n)
            G.add_weighted_edges_from(H)
            A = nx.adjacency_matrix(G)
            B = A.toarray()
            start = n[0]
            end = n[-1]
            LONGESTPATH, Value, Sum = self.LONGEST_PATH(B, start, end)
            # print LONGESTPATH, Value, Sum

            # if the longest path does not consist of all nodes, distribute the weights in such a way so that longest path has all nodes.
            split_candidates = []
            for i in range(len(LONGESTPATH) - 1):
                if LONGESTPATH[i + 1] - LONGESTPATH[i] > 1:
                    split_candidates.append([LONGESTPATH[i], LONGESTPATH[i + 1]])
            # print split_candidates
            if len(split_candidates) > 0:
                for i in range(len(split_candidates)):
                    pair = split_candidates[i]
                    parts = [0 for j in range(pair[1] - pair[0])]
                    weight = B[pair[0]][pair[1]]
                    ind_weight = float(weight / len(parts))

                    nodes = [pair[0] + i for i in range(len(parts) + 1)]
                    for k in range(len(nodes) - 1):
                        B[nodes[k]][nodes[k + 1]] = ind_weight
                        B[pair[0]][pair[1]] = 0
                        for (k1), v in edgelabels.items():
                            if (k1) == (nodes[k], nodes[k + 1]):
                                v[0] = ind_weight
                            if (k1) == (pair[0], pair[1]):
                                v[0] = 0
                LONGESTPATH, Value, Sum = self.LONGEST_PATH_V(B, start, end)

            h_edges = {}
            for i in range(len(LONGESTPATH) - 1):
                h_edges[(i, i + 1)] = Value[i]
            for (k1), v in edgelabels.items():
                if k1 in h_edges:
                    if v[0] == h_edges[k1]:
                        h_edges[k1] = v
            # print h_edges
            H_all = []
            vertices_list = h_edges.keys()
            vertices_list.sort()

            if individual!=None:
                H=[]
                individual = [int(round(i,4) * 10000) for i in individual]
                for (k), v in h_edges.items():
                    for i in range(len(vertices_list)):
                        if vertices_list[i]==k:
                            if v[2]==2 and v[1]=='0': # ledge width
                                val=v[0]
                            elif v[2] == 1 and v[1] == '0':  # white spacing
                                val = v[0]
                            elif v[2] == 0 and int(v[1]) > 1:
                                val = v[0]
                            else:

                                val = individual[i] + v[0]
                        else:
                            continue
                        H.append((k[0], k[1], val))

                H_all.append(H)
            else:
                s = seed
                for i in range(N):
                    seed = s + i * 1000
                    count = 0
                    H = []
                    for (k), v in h_edges.items():
                        count += 1
                        if v[2] == 2 and v[1] == '0':  # ledge width
                            val = v[0]
                        elif v[2] == 1 and v[1] == '0':  # white spacing
                            val = v[0]
                        elif v[2] == 0 and int(v[1]) > 1:
                            val = v[0]
                        else:
                            if (N < 150):
                                SD = N * 300  # standard deviation for randomization
                            else:
                                SD = 10000
                            random.seed(seed + count * 1000)
                            val = int(min(100 * v[0], max(v[0], random.gauss(v[0], SD))))
                        # print (k),v[0],val
                        H.append((k[0], k[1], val))
                    H_all.append(H)
            """
            # In the HCG (horizontal constraint graph), all edge weights are randomized based on different type of tiles
            D = []
            for i in range(N):
                seed = seed + i * 1000
                count=0
                EDGEH = []
                if (N<150):
                    SD=N*300 # standard deviation for randomization
                else:
                    SD=N*100
                for (k1), v in edgelabels.items():

                    count+=1
                    edge = {}
                    random.seed(seed + count * 1000)
                    val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))

                    '''
                    if v[2] == 0:
                        
                        if v[1] == '1':
                            random.seed(seed + count * 1000)
                            val = int(min(10* v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '2':
                            random.seed(seed + count * 1000)
                            val = int(min(2 * v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '3':
                            random.seed(seed + count * 1000)
                            val = int(min(v[0] * 2, max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '4':
                            random.seed(seed + count * 1000)
                            val = int(min(2 * v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '0':
                            random.seed(seed + count * 1000)
                            val = int(min(v[0] * 10, max(v[0], random.gauss(v[0], SD))))
                        elif (isinstance(v[1], int)):
                            random.seed(seed + count * 1000)
                            val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                    elif v[2] == 1:
                        if v[1] == 'missing':
                            random.seed(seed + count * 1000)
                            val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                        else:
                            random.seed(seed + count * 1000)
                            val = int(min(10* v[0], max(v[0], random.gauss(v[0], SD))))
                    elif v[2] == 2:
                        random.seed(seed + count * 1000)
                        val=int(min(10 * v[0], max(v[0], random.gauss(v[0], SD/50))))
                    else:
                        random.seed(seed + count * 1000)
                        val = int(min(10* v[0], max(v[0], random.gauss(v[0], SD))))
                    
                    
                    '''


                    edge[(k1)] = val
                    EDGEH.append(edge)
                D.append(EDGEH)

            # Creating N number of new graphs based on the edges after randomization
            D_3 = []
            for j in range(len(D)):
                d[j] = defaultdict(list)
                for i in D[j]:
                    k, v = list(i.items())[0]
                    d[j][k].append(v)
                D_3.append(d[j])
            H_all = []
            for i in range(len(D_3)):
                H = []
                for k, v in D_3[i].items():
                    H.append((k[0],k[1],v[0]))
                H_all.append(H)
            """
            G_all=[]
            for i in range(len(H_all)):
                G = nx.MultiDiGraph()
                n = list(G2.nodes())
                G.add_nodes_from(n)
                G.add_weighted_edges_from(H_all[i])
                G_all.append(G)
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
                        if B[i][j] != 0:
                            X[(i, j)] = B[i][j]

                Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
                for i in range(source, target + 1):
                    j = source
                    while j != target:
                        if B[j][i] != 0:
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        if i == source and j == source:
                            key = i
                            Pred.setdefault(key, [])
                            Pred[key].append(j)
                        j += 1

                n = list(Pred.keys())  ## list of all predecessors
                dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
                position = {}
                for j in range(source, target + 1):
                    node = j
                    for i in range(len(Pred[node])):
                        pred = Pred[node][i]

                        if j == source:
                            dist[node] = (0, pred)
                            key = node
                            position.setdefault(key, [])
                            position[key].append(0)
                        else:
                            pairs = (max(position[pred]) + (X[(pred, node)]), pred)

                            f = 0
                            for x, v in dist.items():
                                if node == x:
                                    if v[0] > pairs[0]:
                                        f = 1
                            if f == 0:
                                dist[node] = pairs
                            key = node
                            position.setdefault(key, [])
                            position[key].append(pairs[0])
                loc_i = {}
                for key in position:
                    loc_i[key] = max(position[key])

                    new_Xlocation.append(loc_i[key])
                loct.append(loc_i)
                self.NEWXLOCATION.append(new_Xlocation) # evaluation result for each graph. Each vertices new location is calculated

            n = list(G2.nodes())
            Location = {}
            key = ID
            Location.setdefault(key, [])
            for i in range(len(self.NEWXLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_H[ID])):
                    loct[self.ZDL_H[ID][j]] = self.NEWXLOCATION[i][j]
                Location[ID].append(loct)
            self.minLocationH = Location # updating all graph's evaluated location for each node in the tree

        # evaluation for mode-2(Fixed floorplan) and mode-3(fixed floorplan with fixed component locations)
        elif level == 2 or level ==3:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d3[k].append(v)
            X = {}
            H = []
            for i, j in d3.items():
                X[i] = max(j) # keeping dominating edge weights among multiple edges

            for k, v in X.items():
                H.append((k[0], k[1], v))
            loct = []
            #setting up seed
            s=seed
            for i in range(N):
                self.seed_h.append(s+i*1000)
            for i in range(N):
                self.Loc_X={}
                G = nx.MultiDiGraph()
                n = list(G2.nodes())
                G.add_nodes_from(n)
                G.add_weighted_edges_from(H)
                for k, v in self.XLoc.items():
                    if k in n:
                        self.Loc_X[k] = v # a dictionary where vertices are keys and evaluated locations are values. As it's fixed floorplan already source and sink vertex location
                        #is given. So those are set here. Rest of the vertices locations are evaluated using FUNCTION and the self.Loc_X is updated from that function.
                self.FUNCTION(G,individual,sid=i)#added individual for optimization
                loct.append(self.Loc_X) # after evaluation a new floorplan locations are found. There are N number of location sets

            for i in loct:
                new_x_loc = []
                for j, k in i.items():
                    new_x_loc.append(k)
                self.NEWXLOCATION.append(new_x_loc)
            n = list(G2.nodes())
            Location = {}
            key = ID
            Location.setdefault(key, [])
            for i in range(len(self.NEWXLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_H[ID])):
                    loct[self.ZDL_H[ID][j]] = self.NEWXLOCATION[i][j]
                Location[ID].append(loct)
            self.minLocationH = Location # updated location sets for each node in the tree

        # mode-0(minimum floorplan size layout generation)
        else:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d3[k].append(v)
            X = {}
            H = []
            for i, j in d3.items():
                X[i] = max(j)   # keeping dominated edge values

            for k, v in X.items():
                H.append((k[0], k[1], v))
            G = nx.MultiDiGraph()
            n = list(G2.nodes())
            G.add_nodes_from(n)
            G.add_weighted_edges_from(H)
            A = nx.adjacency_matrix(G)
            B = A.toarray()
            Location = {}
            # longest path evaluation
            for i in range(len(n)):
                if n[i] == 0:
                    Location[n[i]] = 0
                else:
                    k = 0
                    val = []
                    for j in range(len(B)):
                        if B[j][i] > k:
                            pred = j
                            val.append(Location[n[pred]] + B[j][i])
                    Location[n[i]] = max(val)
            dist = {}
            for node in Location:
                key = node

                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(Location[node])


            LOC_H = {}
            for i in Location.keys():
                LOC_H[self.ZDL_H[ID][i]] = Location[i]
            odH = collections.OrderedDict(sorted(LOC_H.items()))

            self.minLocationH[ID] = odH # minimum size floorplan locations are stored

            # if current node is not a root node of the tree then it's evaluated minimum locations(mode-0 result) is propagated to its parent node (this part is for hierarchy. But in this version we are not implementing hierarchy)
            if parentID != None:
                KEYS = list(LOC_H.keys())
                parent_coord = []
                for k in self.ZDL_H[ID]:
                    if k in self.ZDL_H[parentID]:
                        parent_coord.append(k)
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
                edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=None, id=None))
                edgelist = self.edgesh_new[parentID]
                edgelist.append(edge)
                self.edgesh_new[parentID] = edgelist


    def cgToGraph_v(self,ID, edgev, parentID, level,N,seed,individual):

        '''
                :param ID: Node ID
                :param edgev: vertical edges for that node's constraint graph
                :param parentID: node id of it's parent
                :param level: mode of operation
                :param N: number of layouts to be generated
                :return: constraint graph and solution for different modes
                '''

        GV = nx.MultiDiGraph()  # initialize Vertical constraint graph as a multigraph
        dictList1 = []
        for foo in edgev:
            dictList1.append(foo.getEdgeDict())
        d = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]
            d[k].append(v)
        edge_labels1 = d
        nodes = [x for x in range(len(self.ZDL_V[ID]))] # vertices for VCG, all vertical cuts from corner stotch layout
        GV.add_nodes_from(nodes)
        label = []
        edge_label = []

        # creating graph
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            for internal_edge in edge_labels1[branch]:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}
            GV.add_weighted_edges_from(data)
        d = defaultdict(list)
        for i in edge_label:
            k, v = list(i.items())[0]
            d[k].append(v)
        edge_labels1 = d

        ######## Different Modes of operation are performed . Similar as horizontal graph evaluation

        #################################################################

        # mode-1(variable size floorplan) evaluation
        if level == 1:
            label4 = copy.deepcopy(label)
            d3 = defaultdict(list)
            for i in label4:
                (k1), v = list(i.items())[0]
                d3[(k1)].append(v)
            edgelabels = {}
            for (k), v in d3.items():
                values = []
                for j in range(len(v)):
                    values.append(v[j][0])
                value = max(values)
                for j in range(len(v)):
                    if v[j][0] == value:
                        edgelabels[(k)] = v[j]

            # Added to perform optimization on mode-1
            d4 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d4[k].append(v)
            Y = {}
            V = []
            for i, j in d4.items():
                Y[i] = max(j)  # keeping dominating edge weights among multiple edges

            for k, v in Y.items():
                V.append((k[0], k[1], v))


            G = nx.MultiDiGraph()
            n = list(GV.nodes())
            n.sort()
            G.add_nodes_from(n)
            G.add_weighted_edges_from(V)


            A = nx.adjacency_matrix(G)
            B = A.toarray()
            start = n[0]
            end = n[-1]
            LONGESTPATH, Value, Sum = self.LONGEST_PATH_V(B, start, end)
            #print Sum,len(LONGESTPATH),LONGESTPATH
            LONGESTPATH.sort()


            # if the longest path does not consist of all nodes, distribute the weights in such a way so that longest path has all nodes.
            split_candidates=[]
            for i in range(len(LONGESTPATH)-1):
                if LONGESTPATH[i+1]-LONGESTPATH[i]>1:
                    split_candidates.append([LONGESTPATH[i],LONGESTPATH[i+1]])
            #print split_candidates
            if len(split_candidates)>0:
                for i in range(len(split_candidates)):
                    pair=split_candidates[i]
                    parts=[0 for j in range(pair[1]-pair[0])]
                    weight=B[pair[0]][pair[1]]
                    ind_weight=float(weight/len(parts))

                    nodes=[pair[0]+i for i in range(len(parts)+1)]
                    for k in range(len(nodes)-1):
                        B[nodes[k]][nodes[k+1]]=ind_weight
                        B[pair[0]][pair[1]]=0
                        for (k1), v in edgelabels.items():
                            if (k1)==(nodes[k],nodes[k+1]):
                                v[0]=ind_weight
                            if (k1)==(pair[0],pair[1]):
                                v[0]=0
                LONGESTPATH, Value, Sum = self.LONGEST_PATH_V(B, start, end)
            #print Sum, len(LONGESTPATH), LONGESTPATH




            v_edges = {}
            for i in range(len(LONGESTPATH)-1):
                v_edges[(LONGESTPATH[i], LONGESTPATH[i + 1])] = Value[i]
            for (k1), v in edgelabels.items():

                if (k1) in v_edges:
                    if v[0] == v_edges[k1]:
                        v_edges[k1] = v




            V_all = []
            vertices_list = v_edges.keys()
            vertices_list.sort()

            if individual!=None:
                H=[]
                individual = [int(round(i, 4) * 10000) for i in individual]


                for (k), v in v_edges.items():
                    for i in range(len(vertices_list)):
                        if vertices_list[i]==k:

                            if v[2]==2 and v[1]=='0': # ledge width
                                val=v[0]
                            elif v[2] == 1 and v[1] == '0':  # white spacing
                                val = v[0]
                            elif v[2] == 4 and int(v[1]) > 1:
                                val = v[0]
                            else:
                                val = individual[i] + v[0]
                        else:
                            continue
                        H.append((k[0], k[1], val))
                V_all.append(H)
            else:

                s = seed
                for i in range(N):
                    seed = s + i * 1000
                    count = 0
                    V = []
                    for (k), v in v_edges.items():
                        count += 1

                        if v[2] == 2 and v[1] == '0':  # ledge width
                            val = v[0]
                        elif v[2] == 1 and v[1] == '0':  # white spacing
                            val = v[0]
                        elif v[2] == 4 and int(v[1]) > 1:
                            val = v[0]
                        else:
                            if (N < 150):
                                SD = N * 300  # standard deviation for randomization
                            else:
                                SD = 10000  # 7000
                            random.seed(seed + count * 1000)
                            val = int(min(100 * v[0], max(v[0], random.gauss(v[0], SD))))
                        # print (k),v[0],val
                        V.append((k[0], k[1], val))
                    V_all.append(V)
                
                
                



            """
            D = []
            for i in range(N):
                seed = seed + i * 1000
                count = 0
                EDGEV = []
                if (N<150):
                    SD=N*300
                else:
                    SD=N*100
                for (k1), v in edgelabels.items():
                    count+=1
                    edge = {}
                    random.seed(seed + count * 1000)
                    val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                    '''
                    if v[2] == 4:
                        if v[1] == '1':
                            random.seed(seed + count * 1000)
                            val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '2':
                            random.seed(seed + count * 1000)
                            val = int(min(2 * v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '3':
                            random.seed(seed + count * 1000)
                            val = int(min(v[0] * 2, max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '4':
                            random.seed(seed + count * 1000)
                            val = int(min(2 * v[0], max(v[0], random.gauss(v[0], SD))))
                        elif v[1] == '0':
                            random.seed(seed + count * 1000)
                            val = int(min(v[0] * 10, max(v[0], random.gauss(v[0],SD))))
                        elif (isinstance(v[1], int)):
                            random.seed(seed + count * 1000)
                            val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                    elif v[2] == 1:
                        if v[1] == 'missing':
                            random.seed(seed + count * 1000)
                            val = int(min(10* v[0], max(v[0], random.gauss(v[0], SD))))
                        else:
                            random.seed(seed + count * 1000)

                            val = int(min( 10*v[0], max(v[0], random.gauss(v[0], SD))))

                    elif v[2] == 2:
                        random.seed(seed + count * 1000)
                        val=int(min(10 * v[0], max(v[0], random.gauss(v[0], SD/50))))
                    else:
                        random.seed(seed + count * 1000)
                        val = int(min(10 * v[0], max(v[0], random.gauss(v[0], SD))))
                    '''
                    edge[(k1)] = val
                    EDGEV.append(edge)
                D.append(EDGEV)

            D_3 = []
            for j in range(len(D)):
                d[j] = defaultdict(list)
                for i in D[j]:
                    k, v = list(i.items())[0]
                    d[j][k].append(v)

                D_3.append(d[j])

            V_all = []
            for i in range(len(D_3)):
                V = []
                for k, v in D_3[i].items():
                    V.append((k[0], k[1], v[0]))
                V_all.append(V)
            """
            GV_all = []
            for i in range(len(V_all)):
                G = nx.MultiDiGraph()
                n = list(GV.nodes())
                G.add_nodes_from(n)
                G.add_weighted_edges_from(V_all[i])
                GV_all.append(G)
            locta = []
            for i in range(len(GV_all)):
                new_Ylocation = []
                A = nx.adjacency_matrix(GV_all[i])
                B = A.toarray()
                source = n[0]
                target = n[-1]
                X = {}

                # Longest path algorithm is performed
                for i in range(len(B)):
                    for j in range(len(B[i])):
                        if B[i][j] != 0:
                            X[(i, j)] = B[i][j]

                Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
                for i in range(source,target+1):

                        j = source

                        while j != target:
                            if B[j][i] != 0:
                                key = i
                                Pred.setdefault(key, [])
                                Pred[key].append(j)
                            if i == source and j == source:
                                key = i
                                Pred.setdefault(key, [])
                                Pred[key].append(j)
                            j += 1

                n = list(Pred.keys())  ## list of all nodes

                dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
                position = {}
                for j in range(source, target + 1):
                    node = j

                    for i in range(len(Pred[node])):
                        pred = Pred[node][i]
                        if j == source:
                            dist[node] = (0, pred)
                            key = node
                            position.setdefault(key, [])
                            position[key].append(0)
                        else:
                            pairs = (max(position[pred]) + (X[(pred, node)]), pred)
                            f = 0
                            for x, v in dist.items():
                                if node == x:
                                    if v[0] > pairs[0]:
                                        f = 1
                            if f == 0:
                                dist[node] = pairs
                            key = node
                            position.setdefault(key, [])
                            position[key].append(pairs[0])

                loc_i = {}
                for key in position:
                    loc_i[key] = max(position[key])
                    new_Ylocation.append(loc_i[key])
                locta.append(loc_i)
                self.NEWYLOCATION.append(new_Ylocation)
            Location = {}
            key = ID
            Location.setdefault(key, [])

            for i in range(len(self.NEWYLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_V[ID])):
                    loct[self.ZDL_V[ID][j]] = self.NEWYLOCATION[i][j]
                Location[ID].append(loct)
            self.minLocationV = Location

        # mode-2(Fixed floorplan) and mode-3(Fixed floorplan with fixed component locations)
        elif level == 2 or level ==3:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d3[k].append(v)
            Y = {}
            V = []
            for i, j in d3.items():
                Y[i] = max(j)
            for k, v in Y.items():
                V.append((k[0], k[1], v))
            loct = []
            s = seed
            for i in range(N):
                self.seed_v.append(s + i*1000)
            for i in range(N):
                self.Loc_Y = {}
                G = nx.MultiDiGraph()
                n = list(GV.nodes())
                G.add_nodes_from(n)
                G.add_weighted_edges_from(V)
                for k, v in self.YLoc.items():
                    if k in n:
                        self.Loc_Y[k] = v
                #print self.Loc_Y
                self.FUNCTION_V(G,individual,sid=i)
                #print self.Loc_Y
                loct.append(self.Loc_Y)
            for i in loct:
                new_y_loc = []
                for j, k in i.items():
                    new_y_loc.append(k)
                self.NEWYLOCATION.append(new_y_loc)
            Location = {}
            key = ID
            Location.setdefault(key, [])


            for i in range(len(self.NEWYLOCATION)):
                loct = {}
                for j in range(len(self.ZDL_V[ID])):
                    loct[self.ZDL_V[ID][j]] = self.NEWYLOCATION[i][j]
                Location[ID].append(loct)
            self.minLocationV = Location

        #mode-0(minimum size floorplan evaluation)
        else:
            d3 = defaultdict(list)
            for i in edge_label:
                k, v = list(i.items())[0]
                d3[k].append(v)
            Y = {}
            V = []
            for i, j in d3.items():
                Y[i] = max(j)

            for k, v in Y.items():
                V.append((k[0], k[1], v))
            G = nx.MultiDiGraph()
            n = list(GV.nodes())
            G.add_nodes_from(n)
            G.add_weighted_edges_from(V)
            A = nx.adjacency_matrix(G)
            B = A.toarray()
            Location = {}

            #performing Longest path algorithm
            for i in range(len(n)):
                if n[i] == 0:
                    Location[n[i]] = 0
                else:
                    k = 0
                    val = []
                    for j in range(len(B)):
                        if B[j][i] > k:
                            pred = j
                            val.append(Location[n[pred]] + B[j][i])
                    Location[n[i]] = max(val)
            dist = {}
            for node in Location:
                key = node
                dist.setdefault(key, [])
                dist[node].append(node)
                dist[node].append(Location[node])

            LOC_V = {}
            for i in Location.keys():

                LOC_V[self.ZDL_V[ID][i]] = Location[i]

            odV = collections.OrderedDict(sorted(LOC_V.items()))
            self.minLocationV[ID] = odV

            # again for hierarchy(Not applicable for this version)
            if parentID != None:
                KEYS = list(LOC_V.keys())
                parent_coord = []
                for k in self.ZDL_V[ID]:
                    if k in self.ZDL_V[parentID]:
                        parent_coord.append(k)
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
                edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=None, id=None))
                edgelist = self.edgesv_new[parentID]
                edgelist.append(edge)
                self.edgesv_new[parentID] = edgelist


    # Applies algorithms for evaluating mode-2 and mode-3 solutions
    def FUNCTION(self, G,Random,sid):
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        Fixed_Node = self.Loc_X.keys() # list of vertices which are given from user as fixed vertices (vertices with user defined locations)
        Fixed_Node.sort()

        #trying to split all possible edges
        Splitlist = [] # list of edges which are split candidate. Edges which has either source or destination as fixed vertex and bypassing a fixed vertex
        for i, j in G.edges():
            for node in G.nodes():
                if node in self.Loc_X.keys() and node > i and node < j:
                    edge = (i, j)
                    if edge not in Splitlist:
                        Splitlist.append(edge)
        med = {} # finding all possible splitting points
        for i in Splitlist:
            start = i[0]
            end = i[1]
            for node in Fixed_Node:
                if node > start and node < end:
                    key = (start, end)
                    med.setdefault(key, [])
                    med[key].append(node)
        for i, v in med.items():
            start = i[0]
            end = i[-1]
            succ = v
            s = start
            e = end
            if s in Fixed_Node or e in Fixed_Node:
                for i in range(len(succ)):
                    B=self.edge_split(s, succ[i], e, Fixed_Node, B)
                    if len(succ) > 1:
                        s = succ[i]

        # after edge splitting trying to remove edges which are associated with fixes vertices as both source and destination
        for i in Fixed_Node:
            for j in Fixed_Node:
                if G.has_edge(i, j):
                    G.remove_edge(i, j)


        nodes = list(G.nodes())
        nodes.sort()


        # Creates all possible disconnected subgraph vertices
        Node_List = []
        for i in range(len(Fixed_Node) - 1):
            node = [Fixed_Node[i]]
            for j in nodes:
                if j not in node and j >= Fixed_Node[i] and j <= Fixed_Node[i + 1]:
                    node.append(j)
            if len(node) > 2:
                Node_List.append(node)

        nodes.sort()

        start = nodes[0]
        end = nodes[-1]
        LONGESTPATH, Value, Sum = self.LONGEST_PATH(B, start, end)
        if (len(LONGESTPATH)) == len(nodes):
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))  # finds all subgraphs according to node list
            for graph in H:
                n = list(graph.nodes())
                n.sort()
                start = n[0]
                end = n[-1]
                self.Location_finding(B, start, end,Random, SOURCE=None, TARGET=None, flag=False,sid=sid)  # evaluates each subgraph (Random is added to test optimization)
            Fixed_Node = self.Loc_X.keys()
            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)
            if len(G.edges()) == 0:
                return
            else:
                self.FUNCTION(G,Random,sid)
        else:
            Connected_List = []
            for k in range(len(Node_List)):
                for m in range(len(Node_List)):
                    LIST = []
                    for i in range(len(B)):
                        for j in range(len(B)):
                            if i in Node_List[k] and j in Node_List[m]:
                                if i not in Node_List[m] and j not in Node_List[k]:
                                    if B[i][j] != 0:
                                        LIST = Node_List[k] + Node_List[m]

                    if len(LIST) > 0:
                        Connected_List.append(list(set(LIST)))

        '''
        # Checks whether those subgraph vertices are connected among themselves
        List=[] # This list
        for i in range(len(B)):
            for j in range(len(B)):
                for k in range(len(Node_List)):
                    if i in Node_List[k] and j not in Node_List[k] and B[i][j]!=0:
                        for m in range(len(Node_List)):
                            if j in Node_List[m]:
                                if Node_List[k] not in List:
                                    List.append(Node_List[k])
                                if Node_List[m] not in List:
                                    List.append(Node_List[m])

        Connected_List = []

        # if they are connected among themselves then essentially graph splitting is not possible
        if len(List) > 0:
            L = []
            for i in List:
                L += i
            Connected_List.append(list(set(L)))

        # if there are connected subgraphs but not the whole graph is connected. then finds subgraphs which are disconnected
        else:
            for k in range(len(Node_List)):
                for m in range(len(Node_List)):
                    LIST = []
                    for i in range(len(B)):
                        for j in range(len(B)):
                            if i in Node_List[k] and j in Node_List[m]:
                                if i not in Node_List[m] and j not in Node_List[k]:
                                    if B[i][j] != 0:
                                        LIST = Node_List[k] + Node_List[m]

                    if len(LIST) > 0:
                        Connected_List.append(list(set(LIST)))


        # if the whole graph is connected and all vertices are on the longest path, then the graph can be split into subgraphs at fixed vertices.
        if len(Connected_List)==1:
            PATH = Connected_List[0]
            start = PATH[0]
            end = PATH[-1]
            LONGESTPATH, Value, Sum = self.LONGEST_PATH(B, start, end)
            if LONGESTPATH == PATH:
                H = []
                for i in range(len(Node_List)):
                    H.append(G.subgraph(Node_List[i])) # finds all subgraphs according to node list
                for graph in H:
                    n = list(graph.nodes())
                    n.sort()
                    start = n[0]
                    end = n[-1]
                    self.Location_finding(B, start, end, SOURCE=None, TARGET=None, flag=False) # evaluates each subgraph
                Fixed_Node = self.Loc_X.keys()
                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION(G)
        '''
        if len(Connected_List) > 1:
            for i in range(len(Connected_List)):
                PATH = Connected_List[i]
                start = PATH[0]
                end = PATH[-1]
                SOURCE = []
                for i in range(len(PATH) - 1):
                    if PATH[i] in self.Loc_X.keys():
                        SOURCE.append(PATH[i])

                TARGET = []
                for i in range(1, len(PATH)):
                    if PATH[i] in self.Loc_X.keys():
                        TARGET.append(PATH[i])
                self.Location_finding(B, start, end,Random, SOURCE, TARGET, flag=True,sid=sid) # if split into subgraph is not possible and there is edge in the longest path which is bypassing a fixed vertex,
                # then evaluation with flag=true is performed
                Fixed_Node = self.Loc_X.keys()

                # after evaluation tries to remove edges if possible
                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION(G,Random,sid)

        # if the whole graph can be split into disconnected subgraphs
        else:
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))
            for graph in H:
                n = list(graph.nodes())
                n.sort()
                start = n[0]
                end = n[-1]
                self.Location_finding(B, start, end,Random, SOURCE=None, TARGET=None, flag=False,sid=sid)
            Fixed_Node = self.Loc_X.keys()
            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)

            if len(G.edges()) == 0:

                return

            else:
                self.FUNCTION(G, Random,sid)


    # randomize uniformly edge weights within fixed minimum and maximum locations
    def randomvaluegenerator(self, Range, value,Random,sid):
        #print "R",Random,sid
        Range=Range/1000

        if Random!=None:
            Sum=sum(Random)

            if Sum>0:
                Vi=[]
                for i in Random:

                    Vi.append(Range*(i/Sum))
            else:
                Vi = [0 for i in Random]
            #print Random
            Vi = [int(round(i, 3) * 1000) for i in Vi]
            
            variable=[]
            for i in range(len(value)):
                variable.append(value[i]+Vi[i])

            #print "var", variable

        #print "Vy",len(Vy_s),sum(Vy_s),Vy_s



        else:
            '''
            variable = []
            Total = sum(value)
            V = copy.deepcopy(value)
            Prob = []

            for i in value:
                Prob.append(i / float(Total))
            
            random.seed(self.seed_h[sid])
            D_V_Newval = list(np.random.multinomial(Range, Prob))
            '''
            variable = []
            D_V_Newval = [0]
            V=copy.deepcopy(value)

            while (len(value) > 1):
                i = 0
                n = len(value)
                v = Range - sum(D_V_Newval)
                if ((2 * v) / n) > 0:
                    random.seed(self.seed_h[sid])
                    x =  random.randint(0, (int(2 * v) / n))
                else:
                    x = 0
                p = value.pop(i)
                D_V_Newval.append(x)

            del D_V_Newval[0]
            D_V_Newval.append(Range - sum(D_V_Newval))

            random.shuffle(D_V_Newval)
            for i in range(len(V)):
                x=V[i]+D_V_Newval[i]
                variable.append(x) # randomized edge weights without violating minimum constraint values

        return variable

    #longest path evaluation function
    def LONGEST_PATH(self, B, source, target):
        X = {}
        for i in range(len(B)):
            for j in range(len(B[i])):
                if B[i][j] != 0:
                    X[(i, j)] = B[i][j]
        for i in range(source, target):  ### adding missing edges between 2 fixed nodes (due to edge removal)
            j = i + 1
            if B[i][j] == 0 and i in self.Loc_X.keys() and j in self.Loc_X.keys():
                X[(i, i + 1)] = self.Loc_X[i + 1] - self.Loc_X[i]
                B[i][j] = self.Loc_X[i + 1] - self.Loc_X[i]
        Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
        for i in range(source, target + 1):
            j = source
            while j != target:
                if B[j][i] != 0:
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                if i == source and j == source:
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                j += 1
        n = list(Pred.keys())  ## list of all nodes
        dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
        position = {}
        for j in range(source, target + 1):
            node = j
            for i in range(len(Pred[node])):
                pred = Pred[node][i]
                if j == source:
                    dist[node] = (0, pred)
                    key = node
                    position.setdefault(key, [])
                    position[key].append(0)
                else:
                    pairs = (max(position[pred]) + (X[(pred, node)]), pred)
                    f = 0
                    for x, v in dist.items():
                        if node == x:
                            if v[0] > pairs[0]:
                                f = 1
                    if f == 0:
                        dist[node] = pairs
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])
        i = target
        path = []
        while i > source:
            if i not in path:
                path.append(i)
            i = dist[i][1]
            path.append(i)
        PATH = list(reversed(path))  ## Longest path
        Value = []
        for i in range(len(PATH) - 1):
            if (PATH[i], PATH[i + 1]) in X.keys():
                Value.append(X[(PATH[i], PATH[i + 1])])
        #print "Val",Value
        Max = sum(Value)

        # returns longest path, list of minimum constraint values in that path and summation of the values
        return PATH, Value, Max

    # function that splits edge into parts, where med is the list of fixed nodes in between source and destination of the edge
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
        if f == 1:
            B[start][end] = 0
        return B


    # this function evaluates the case where the connected whole graph has edges bypassing fixed node in the longest path
    def Evaluation_connected(self, B, PATH, SOURCE, TARGET,sid):
        """

        :param B: Adjacency matrix
        :param PATH: longest path to be evaluated
        :param SOURCE: list of all possible sources on the longest path
        :param TARGET: list of all possible targets on the longest path
        :return: evaluated locations for the non-fixed vertices on the longest path
        """
        Fixed = self.Loc_X.keys()
        UnFixed = []
        for i in PATH:
            if i not in Fixed:
                UnFixed.append(i)  # making list of all non-fixed nodes
        while (len(UnFixed)) > 0:
            Min_val = {}  # incrementally updates minimum distances from source to each non-fixed vertex
            for i in SOURCE:
                for j in UnFixed:
                    key = j
                    Min_val.setdefault(key, [])
                    Val = self.LONGEST_PATH(B, i, j)

                    if Val[2] != 0:
                        x = (self.Loc_X[i] + Val[2])
                        Min_val[key].append(x)

            Max_val = {} # incrementally updates minimum distances from each non-fixed vertex to target
            for i in UnFixed:
                for j in TARGET:
                    key = i
                    Max_val.setdefault(key, [])
                    Val = self.LONGEST_PATH(B, i, j)
                    if Val[2] != 0:
                        x = (self.Loc_X[j] - Val[2])
                        Max_val[key].append(x)
            i = UnFixed.pop(0)
            v_low = max(Min_val[i])
            v_h2 = min(Max_val[i])
            v1 = v_low
            v2 = v_h2

            # finds randomized location for each non-fixed node between minimum and maximum possible location
            if v1 < v2:
                random.seed(self.seed_h[sid])
                self.Loc_X[i] = randrange(v1, v2)
            else:
                self.Loc_X[i] = max(v1, v2)
            SOURCE.append(i) # when a non-fixed vertex location is determined it becomes a fixed vertex and may treat as source to others
            TARGET.append(i) # when a non-fixed vertex location is determined it becomes a fixed vertex and may treat as target to others



    def Location_finding(self, B, start, end,Random, SOURCE, TARGET, flag,sid):
        """

        :param B: Adjacency matrix
        :param start: source vertex of the path to be evaluated
        :param end: sink vertex of the path to be evaluated
        :param SOURCE: list of possible sources (mode-3 case)
        :param TARGET: list of possible targets (mode-3 case)
        :param flag: to check whether it has bypassing fixed vertex in the path (mode-3 case)
        :return:
        """

        PATH, Value, Sum = self.LONGEST_PATH(B, start, end)

        if flag == True:
            self.Evaluation_connected(B, PATH, SOURCE, TARGET,sid)
        else:
            Max = self.Loc_X[end] - self.Loc_X[start]

            Range = Max - Sum
            variable = self.randomvaluegenerator(Range, Value,Random,sid)
            loc = {}
            for i in range(len(PATH)):
                if PATH[i] in self.Loc_X:
                    loc[PATH[i]] = self.Loc_X[PATH[i]]
                else:
                    loc[PATH[i]] = self.Loc_X[PATH[i - 1]] + variable[i - 1]
                    self.Loc_X[PATH[i]] = self.Loc_X[PATH[i - 1]] + variable[i - 1]
        return

    ###########################################################


    # this function has the same purpose and algorithms as for horizontal FUNCTION(G). It's just for VCG evaluation
    def FUNCTION_V(self, G,Random,sid):
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        Fixed_Node = self.Loc_Y.keys()
        Fixed_Node.sort()
        Splitlist = []
        for i, j in G.edges():
            for node in G.nodes():
                if node in self.Loc_Y.keys() and node > i and node < j:
                    edge = (i, j)
                    if edge not in Splitlist:
                        Splitlist.append(edge)
        med = {}
        for i in Splitlist:
            start = i[0]
            end = i[1]

            for node in Fixed_Node:
                if node > start and node < end:
                    key = (start, end)
                    med.setdefault(key, [])
                    med[key].append(node)

        for i, v in med.items():
            start = i[0]
            end = i[-1]
            succ = v
            s = start
            e = end
            if s in Fixed_Node or e in Fixed_Node:
                for i in range(len(succ)):
                    B=self.edge_split_V(s, succ[i], e, Fixed_Node, B)
                    if len(succ) > 1:
                        s = succ[i]
        for i in Fixed_Node:
            for j in Fixed_Node:
                if G.has_edge(i, j):
                    G.remove_edge(i, j)

        nodes = list(G.nodes())
        nodes.sort()
        Node_List = []
        for i in range(len(Fixed_Node) - 1):
            node = [Fixed_Node[i]]
            for j in nodes:
                if j not in node and j >= Fixed_Node[i] and j <= Fixed_Node[i + 1]:
                    node.append(j)
            if len(node) > 2:
                Node_List.append(node)

        List = []
        for i in range(len(B)):
            for j in range(len(B)):
                for k in range(len(Node_List)):
                    if i in Node_List[k] and j not in Node_List[k] and B[i][j] != 0:
                        for m in range(len(Node_List)):
                            if j in Node_List[m]:
                                if Node_List[k] not in List:
                                    List.append(Node_List[k])
                                if Node_List[m] not in List:
                                    List.append(Node_List[m])

        Connected_List = []
        if len(List) > 0:
            L = []
            for i in List:
                L += i
            Connected_List.append(list(set(L)))

        else:
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

        #print Connected_List

        if len(Connected_List)==1:
            flag=True
            while(flag):
                PATH = Connected_List[0]
                start = PATH[0]
                end = PATH[-1]
                LONGESTPATH, Value, Sum = self.LONGEST_PATH(B, start, end)

                if LONGESTPATH == PATH:
                    flag=False
                    H = []
                    for i in range(len(Node_List)):
                        H.append(G.subgraph(Node_List[i]))

                    for graph in H:
                        n = list(graph.nodes())
                        n.sort()
                        start = n[0]
                        end = n[-1]
                    self.Location_finding_V(B, start, end,Random, SOURCE=None, TARGET=None, flag=False,sid=sid)  # evaluates each subgraph (Random is added tot est optimization)
                    Fixed_Node = self.Loc_Y.keys()
                    for i in Fixed_Node:
                        for j in Fixed_Node:
                            if G.has_edge(i, j):
                                G.remove_edge(i, j)



                    if len(G.edges()) == 0:
                        return
                    else:
                        self.FUNCTION_V(G,Random,sid)
                else:
                    split_candidates = []
                    for i in range(len(LONGESTPATH) - 1):
                        if LONGESTPATH[i + 1] - LONGESTPATH[i] > 1:
                            split_candidates.append([LONGESTPATH[i], LONGESTPATH[i + 1]])
                    # print split_candidates
                    if len(split_candidates) > 0:
                        for i in range(len(split_candidates)):
                            pair = split_candidates[i]
                            parts = [0 for j in range(pair[1] - pair[0])]
                            weight = B[pair[0]][pair[1]]
                            ind_weight = float(weight / len(parts))

                            nodes = [pair[0] + i for i in range(len(parts) + 1)]
                            for k in range(len(nodes) - 1):
                                B[nodes[k]][nodes[k + 1]] = ind_weight
                                B[pair[0]][pair[1]] = 0


        elif len(Connected_List) > 1:
            for i in range(len(Connected_List)):
                PATH = Connected_List[i]

                start = PATH[0]
                end = PATH[-1]
                SOURCE = []
                for i in range(len(PATH) - 1):
                    if PATH[i] in self.Loc_Y.keys():
                        SOURCE.append(PATH[i])
                SOURCE.sort()
                TARGET = []
                for i in range(1, len(PATH)):
                    if PATH[i] in self.Loc_Y.keys():
                        TARGET.append(PATH[i])
                TARGET.sort()
                self.Location_finding_V(B, start, end,Random, SOURCE, TARGET, flag=True,sid=sid)
                Fixed_Node = self.Loc_Y.keys()
                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION_V(G, Random, sid)
        else:
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))
            for graph in H:
                n = list(graph.nodes())
                n.sort()
                start = n[0]
                end = n[-1]
                self.Location_finding_V(B, start, end,Random, SOURCE=None, TARGET=None, flag=False,sid=sid)


            Fixed_Node = self.Loc_Y.keys()

            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)

            if len(G.edges()) == 0:

                return
            else:
                self.FUNCTION_V(G,Random,sid)


    def randomvaluegenerator_V(self, Range, value,Random,sid):
        """

        :param Range: Randomization room excluding minimum constraint values
        :param value: list of minimum constraint values associated with the room
        :return: list of randomized value corresponding to each minimum constraint value
        """

        Range=Range/1000

        if Random!=None:
            Sum = sum(Random)

            if Sum>0:
                Vi=[]
                for i in Random:

                    Vi.append(Range*(i/Sum))
            else:
                Vi = [0 for i in Random]
            '''
            Vi = []
            for i in Random:
                Vi.append(Range * (i / Sum))
            '''
            Vi = [int(round(i, 3) * 1000) for i in Vi]

            variable = []
            for i in range(len(value)):
                variable.append(value[i] + Vi[i])
            #print variable


        else:
            '''
            variable = []
            Total = sum(value)
            V = copy.deepcopy(value)
            Prob = []

            for i in value:
                Prob.append(i / float(Total))
            random.seed(self.seed_v[sid])
            D_V_Newval = list(np.random.multinomial(Range, Prob))

            '''
            variable = []
            D_V_Newval = [0]
            V = copy.deepcopy(value)
            #print "Range",Range
            #print "value",value
            while (len(value) > 1):

                i = 0
                n = len(value)

                v = Range - sum(D_V_Newval)

                if ((2 * v) / n) > 0:
                    random.seed(self.seed_v[sid])

                    x = random.randint(0, (int(2 * v) / n))
                else:
                    x = 0
                p = value.pop(i)

                D_V_Newval.append(x)

            del D_V_Newval[0]
            #print "Var", D_V_Newval
            D_V_Newval.append(Range - sum(D_V_Newval))

            random.shuffle(D_V_Newval)

            for i in range(len(V)):
                x = V[i] + D_V_Newval[i]
                variable.append(x)
            #print "Var", variable
        return variable


    def LONGEST_PATH_V(self, B, source, target):
        """

        :param B: Adjacency Matrix
        :param source: source of the path to be evaluated
        :param target: sink of the path to be evaluated
        :return: list of vertices which are on the longest path, list of minimum constraint values on the longest path and sum of those minimum values
        """
        X = {}
        for i in range(len(B)):

            for j in range(len(B[i])):
                if B[i][j] != 0:
                    X[(i, j)] = B[i][j]
        for i in range(source, target):
            j = i + 1
            if B[i][j] == 0 and i in self.Loc_Y.keys() and j in self.Loc_Y.keys():
                X[(i, i + 1)] = self.Loc_Y[i + 1] - self.Loc_Y[i]
                B[i][j] = self.Loc_Y[i + 1] - self.Loc_Y[i]

        Pred = {}  ## Saves all predecessors of each node{node1:[p1,p2],node2:[p1,p2..]}
        for i in range(source, target + 1):
            j = source
            while j != target:
                if B[j][i] != 0:

                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                if i == source and j == source:
                    key = i
                    Pred.setdefault(key, [])
                    Pred[key].append(j)
                j += 1


        n = list(Pred.keys())  ## list of all nodes
        dist = {}  ## Saves each node's (cumulative maximum weight from source,predecessor) {node1:(cum weight,predecessor)}
        position = {}
        for j in range(source, target + 1):
            node = j
            for i in range(len(Pred[node])):
                pred = Pred[node][i]
                if j == source:
                    dist[node] = (0, pred)
                    key = node
                    position.setdefault(key, [])
                    position[key].append(0)
                else:
                    pairs = (max(position[pred]) + (X[(pred, node)]), pred)
                    f = 0
                    for x, v in dist.items():
                        if node == x:
                            if v[0] > pairs[0]:
                                f = 1
                    if f == 0:
                        dist[node] = pairs
                    key = node
                    position.setdefault(key, [])
                    position[key].append(pairs[0])

        i = target
        path = []
        while i > source:
            if i not in path:
                path.append(i)
            i = dist[i][1]
            path.append(i)
        PATH = list(reversed(path))  ## Longest path
        Value = []
        for i in range(len(PATH) - 1):
            if (PATH[i], PATH[i + 1]) in X.keys():
                Value.append(X[(PATH[i], PATH[i + 1])])
        Max = sum(Value)

        return PATH, Value, Max

    def edge_split_V(self, start, med, end, Fixed_Node, B):
        """

        :param start:source vertex of the edge to be split
        :param med: list of fixed vertices which are bypassed by the edge
        :param end: destination vertex of the edge to be split
        :param Fixed_Node: list of fixed nodes
        :param B: Adjacency Matrix
        :return: Updated adjacency matrix after splitting edge
        """
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

        if f == 1:
            B[start][end] = 0

        return B

    def Evaluation_connected_V(self, B, PATH, SOURCE, TARGET,sid):
        """

        :param B: Adjacency matrix
        :param PATH: longest path to be evaluated
        :param SOURCE: list of all possible sources on the longest path
        :param TARGET: list of all possible targets on the longest path
        :return: evaluated locations for the non-fixed vertices on the longest path
        """
        Fixed = self.Loc_Y.keys()
        UnFixed = []
        for i in PATH:
            if i not in Fixed:
                UnFixed.append(i)
        while len(UnFixed) > 0:
            Min_val = {}
            for i in SOURCE:

                for j in UnFixed:
                    key = j
                    Min_val.setdefault(key, [])
                    Val = self.LONGEST_PATH_V(B, i, j)
                    if Val[2] != 0:
                        x = (self.Loc_Y[i] + Val[2])
                        Min_val[key].append(x)
            Max_val = {}
            for i in UnFixed:
                for j in TARGET:
                    key = i
                    Max_val.setdefault(key, [])
                    Val = self.LONGEST_PATH_V(B, i, j)
                    if Val[2] != 0:
                        x = (self.Loc_Y[j] - Val[2])
                        Max_val[key].append(x)

            i = UnFixed.pop(0)

            v_low = max(Min_val[i])
            v_h2 = min(Max_val[i])
            v1 = v_low
            v2 = v_h2
            if v1 < v2:
                random.seed(self.seed_v[sid])
                self.Loc_Y[i] = randrange(v1, v2)
            else:
                self.Loc_Y[i] = max(v1, v2)
            SOURCE.append(i)
            TARGET.append(i)

    def Location_finding_V(self, B, start, end,Random, SOURCE, TARGET, flag,sid):
        """

           :param B: Adjacency matrix
           :param start: source vertex of the path to be evaluated
           :param end: sink vertex of the path to be evaluated
           :param SOURCE: list of possible sources (mode-3 case)
           :param TARGET: list of possible targets (mode-3 case)
           :param flag: to check whether it has bypassing fixed vertex in the path (mode-3 case)
           :return: Updated location table
        """
        PATH, Value, Sum = self.LONGEST_PATH_V(B, start, end)
        if flag == True:
            self.Evaluation_connected_V(B, PATH, SOURCE, TARGET,sid)
        else:
            Max = self.Loc_Y[end] - self.Loc_Y[start]

            Range = Max - Sum
            variable = self.randomvaluegenerator_V(Range, Value,Random,sid)
            loc = {}
            for i in range(len(PATH)):
                if PATH[i] in self.Loc_Y:
                    loc[PATH[i]] = self.Loc_Y[PATH[i]]
                else:
                    loc[PATH[i]] = self.Loc_Y[PATH[i - 1]] + variable[i - 1]
                    self.Loc_Y[PATH[i]] = self.Loc_Y[PATH[i - 1]] + variable[i - 1]
        return


class Edge():
    """
    Edge class having following members:
        source: starting vertex of an edge
        dest: ending vertex of an edge
        constraint: weight of the edge
        index: type of constraint of the edge
        type: type of corresponding tile
        id: id of corresponding tile
        East: east tile
        West: west tile
        North: North tile
        South: South tile
        nortWest,westNorth,southEast, eastSouth: four other neighbors

    """
    def __init__(self, source, dest, constraint, index, type, id, East=None, West=None, North=None, South=None,northWest=None,
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