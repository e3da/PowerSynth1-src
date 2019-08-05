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
import numpy as np
import math


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
        self.H_NODELIST = []
        self.V_NODELIST = []
        self.vertexMatrixh = {}
        self.vertexMatrixv = {}
        self.ZDL_H = {}
        self.ZDL_V = {}
        self.edgesv = {}  ### saves initial vertical constraint graph edges (without adding missing edges)
        self.edgesh = {}  ### saves initial horizontal constraint graph edges (without adding missing edges)
        self.edgesv_new = {}  ###saves vertical constraint graph edges (with adding missing edges)
        self.edgesh_new = {}  ###saves horizontal constraint graph edges (with adding missing edges)
        self.remove_nodes_h = {}
        self.remove_nodes_v = {}
        self.seed_h=[]
        self.seed_v=[]

        self.minLocationH = {}
        self.minLocationV = {}
        self.minX = {}
        self.minY = {}
        self.W_T =W
        self.H_T =H
        self.XLoc = XLocation
        self.YLoc= YLocation
        self.Tbeval = []  # Tob to bottom evaluation member list
        self.TbevalV = []
        self.LocationH = {}
        self.LocationV = {}
        # self.Loc_X=XLocation
        # self.Loc_Y=YLocation



    def graphFromLayer(self, H_NODELIST, V_NODELIST, level,N=None,seed=None,individual=None,Types=None,rel_cons=None):
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
            self.H_NODELIST.append(node)
            if node.child == []:
                continue
            else:
                self.HorizontalNodeList.append(node) # only appending all horizontal tree nodes which have children. Nodes having no children are not included

        for node in V_NODELIST:
            self.V_NODELIST.append(node)
            if node.child == []:
                continue
            else:
                self.VerticalNodeList.append(node)# only appending all vertical tree nodes which have children. Nodes having no children are not included
        """
        print "Horizontal NodeList"
        for i in self.HorizontalNodeList:

            print i.id, i, len(i.stitchList)

            # i=Htree.hNodeList[0]
            for j in i.stitchList:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.voltage,j.current,j.bw, j.name
                print k

            if i.parent == None:
                print 0
            else:
                print i.parent.id, i.id
            for j in i.boundaries:
                if j.cell.type != None:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.bw, j.name

                else:
                    k = j.cell.x, j.cell.y, j.cell.type, j.nodeId
                print "B", i.id, k
        
        print "Vertical NodeList"
        for i in self.VerticalNodeList:
            print i.id, i, len(i.stitchList)
            for j in i.stitchList:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId,j.voltage j.bw, j.name
                print k

            if i.parent == None:
                print 0
            else:
                print i.parent.id, i.id
            for j in i.boundaries:
                if j.cell.type != None:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.bw, j.name

                else:
                    k = j.cell.x, j.cell.y, j.cell.type, j.nodeId
        
        """

        



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

        for k,v in self.ZDL_H.items():
            v=list(set(v))
            v.sort()
            self.ZDL_H[k]=v
        for k, v in self.ZDL_V.items():
            v = list(set(v))
            v.sort()
            self.ZDL_V[k]=v
        #print"BH", self.ZDL_H
        #print"BV", self.ZDL_V

        # setting up edges for constraint graph from corner stitch tiles using minimum constraint values
        for i in range(len(self.HorizontalNodeList)):
            self.setEdgesFromLayer(self.HorizontalNodeList[i], self.VerticalNodeList[i],Types,rel_cons)

        # _new are after adding missing edges
        self.edgesh_new = collections.OrderedDict(sorted(self.edgesh_new.items()))
        self.edgesv_new = collections.OrderedDict(sorted(self.edgesv_new.items()))
        # print "K",self.edgesh_new.keys()
        #print "RE",self.remove_nodes_h
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

            self.cgToGraph_h(ID, self.edgesh_new[ID], parent, level)

        for k, v in list(self.edgesv_new.iteritems())[::-1]:
            ID, edgev = k, v
            for i in self.VerticalNodeList:
                if i.id == ID:
                    if i.parent != None:
                        parent = i.parent.id
                    else:
                        parent = None


            # Function to create vertical constraint graph using edge information

            if individual!=None:
                #print len(individual), len(self.ZDL_H[ID]), len(self.ZDL_V[ID])
                individual_v = individual[len(self.ZDL_H[ID]):]
                #print "ind",individual_v
            else:
                individual_v=None
            self.cgToGraph_v(ID, self.edgesv_new[ID], parent, level)
        if level != 0:
            self.HcgEval(level,individual_h,seed, N)
            self.VcgEval(level,individual_v,seed, N)
    #####  constraint graph evaluation after randomization to determine each node new location
    def minValueCalculation(self, hNodeList, vNodeList, level):
        """

        :param hNodeList: horizontal node list
        :param vNodeList: vertical node list
        :param level: mode of operation
        :return: evaluated X and Y locations for mode-0
        """
        if level == 0:
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
            XLOCATIONS = []
            Value = []
            Key = []
            # print"LOC", self.LocationH
            for k, v in self.LocationH.items():
                # print k, v
                Key.append(k)
                Value.append(v)
            # print"VAL",Key, Value
            for k in range(len(Value[0])):
                xloc = {}
                for i in range(len(Value)):
                    xloc[Key[i]] = Value[i][k]
                XLOCATIONS.append(xloc)
            # print "X", XLOCATIONS
            YLOCATIONS = []
            Value_V = []
            Key_V = []
            for k, v in self.LocationV.items():
                # print k, v
                Key_V.append(k)
                Value_V.append(v)
            # print Value
            for k in range(len(Value_V[0])):
                yloc = {}
                for i in range(len(Value_V)):
                    yloc[Key_V[i]] = Value_V[i][k]
                YLOCATIONS.append(yloc)
            # print XLOCATIONS, YLOCATIONS
            return XLOCATIONS, YLOCATIONS


    # only minimum x location evaluation
    def set_minX(self, node):
        if node.id in self.minLocationH.keys():
            L = self.minLocationH[node.id]
            P_ID = node.parent.id
            # print"P", P_ID
            ZDL_H = []
            for n in self.H_NODELIST:
                if n.id == P_ID:
                    PARENT = n
            # if P_ID == 1:
            for rect in PARENT.stitchList:
                if rect.nodeId == node.id:
                    # print rect.cell.x
                    if rect.nodeId == node.id:
                        if rect.cell.x not in ZDL_H:
                            ZDL_H.append(rect.cell.x)
                            ZDL_H.append(rect.EAST.cell.x)
                        if rect.EAST.cell.x not in ZDL_H:
                            ZDL_H.append(rect.EAST.cell.x)


            P = set(ZDL_H)
            ZDL_H = list(P)
            ZDL_H.sort()
            '''
            else:
                ZDL_H = self.ZDL_H[P_ID]
            '''

            # print "ZDL_H",node.id,ZDL_H
            # print "L",L
            K = L.keys()

            V = L.values()
            # print K, V
            L1 = {}
            for i in range(len(K)):
                # if K[i] not in self.ZDL_H[P_ID]:
                if K[i] not in ZDL_H:
                    V2 = V[i]
                    V1 = V[i - 1]
                    L1[K[i]] = V2 - V1
            # print"L1", L1
            final = {}
            for k in range(len(K)):
                if K[k] not in L1.keys():
                    final[K[k]] = self.minX[P_ID][K[k]]
                    L1[K[k]] = self.minX[P_ID][K[k]]
                else:
                    final[K[k]] = final[K[k - 1]] + L1[K[k]]
            #print"H", final
            self.minX[node.id] = final


    # only minimum y location evaluation
    def set_minY(self, node):
        #print self.minLocationV
        if node.id in self.minLocationV.keys():
            L = self.minLocationV[node.id]

            P_ID = node.parent.id
            ZDL_V = []
            for n in self.V_NODELIST:
                if n.id == P_ID:
                    PARENT = n

            for rect in PARENT.stitchList:
                if rect.nodeId == node.id:
                    if rect.cell.y not in ZDL_V:
                        ZDL_V.append(rect.cell.y)
                        ZDL_V.append(rect.NORTH.cell.y)
                    if rect.NORTH.cell.y not in ZDL_V:
                        ZDL_V.append(rect.NORTH.cell.y)

            P = set(ZDL_V)
            ZDL_V = list(P)
            ZDL_V.sort()
            #print "ZDL_V", ZDL_V
            '''
            else:
                ZDL_V=self.ZDL_V[P_ID]
            '''
            #print node.id,ZDL_V
            K = L.keys()
            V = L.values()
            #print"L", K,V
            L1 = {}
            for i in range(len(K)):
                # if K[i] not in self.ZDL_V[P_ID]:
                if K[i] not in ZDL_V:
                    V2 = V[i]
                    V1 = V[i - 1]
                    L1[K[i]] = V2 - V1
            #print"L1", L1
            final = {}
            for k in range(len(K)):
                if K[k] not in L1.keys():
                    final[K[k]] = self.minY[P_ID][K[k]]
                    L1[K[k]] = self.minY[P_ID][K[k]]
                else:
                    final[K[k]] = final[K[k - 1]] + L1[K[k]]
            #print "F",final
            self.minY[node.id] = final
        # print "V", L

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

    # calculates maximum voltage difference
    def find_voltage_difference(self,voltage1, voltage2,rel_cons):
        '''
        :param voltage1: a dictionary of voltage components:{'DC': , 'AC': , 'Freq': , 'Phi': }
        :param voltage2: a dictionary of voltage components:{'DC': , 'AC': , 'Freq': , 'Phi': }
        :param rel_cons: 1: worst case, 2: average case
        :return: voltage difference between voltage 1 and voltage 2
        '''

        # there are 3 cases: 1. voltage1 is DC, voltage2 is also DC, 2. voltage1 is DC, voltage2 is AC, 3. voltage1 is AC and voltage2 is AC.
        if (voltage1['Freq']!=0 and voltage2['Freq']==0): #swaps if first one is AC
            voltage3=voltage1
            voltage1=voltage2
            voltage2=voltage3

        # need to be handled based on net (connectivity checking)
        if voltage1==voltage2:
            return 0
        else:
            # Average case
            if rel_cons==2:
                # DC-DC voltage difference
                if voltage1['Freq']==0 and voltage2['Freq']==0:
                    return abs(voltage1['DC'] - voltage2['DC'])
                # DC-AC voltage difference
                elif (voltage1['Freq']==0 and voltage2['Freq']!=0):
                    return abs(voltage1['DC']-voltage2['DC'])
                # AC-AC voltage difference
                elif (voltage1['Freq']!=0 and voltage2['Freq']!=0):
                    if voltage1['Freq']==voltage2['Freq']:
                        if voltage1['Phi']!=voltage2['Phi']:
                            v_diff=abs(voltage1['DC']-voltage2['DC'])+math.sqrt(voltage1['AC']**2+voltage2['AC']**2-2*voltage1['AC']*voltage2['AC']*math.cos(voltage1['Phi'])*math.cos(voltage2['Phi'])-2*voltage1['AC']*voltage2['AC']*math.sin(voltage1['Phi'])*math.sin(voltage2['Phi']))
                            return v_diff
                        elif voltage1['Phi']==voltage2['Phi']:
                            return abs(voltage1['DC']-voltage2['DC'])+abs(voltage2['AC']-voltage1['AC'])
                    else:
                        return abs(voltage1['DC']-voltage2['DC'])+abs(voltage1['AC']+voltage2['AC'])
            # Worst case
            elif rel_cons==1:
                # DC-DC voltage difference
                if voltage1['Freq'] == 0 and voltage2['Freq'] == 0:
                    return abs(voltage1['DC'] - voltage2['DC'])
                # DC-AC voltage difference
                elif (voltage1['Freq'] == 0 and voltage2['Freq'] != 0):
                    v1=abs(voltage1['DC']-voltage2['DC']+voltage2['AC'])
                    v2=abs(voltage1['DC']-voltage2['DC']-voltage2['AC'])
                    return max(v1,v2)
                elif (voltage1['Freq'] != 0 and voltage2['Freq'] != 0):
                    return  abs(voltage1['DC']-voltage2['DC'])+abs(voltage1['AC']+voltage2['AC'])







    ## creating edges from corner stitched tiles
    def setEdgesFromLayer(self, cornerStitch_h, cornerStitch_v,Types,rel_cons):

        #print "Voltage",constraint.constraint.voltage_constraints
        #print "Current",constraint.constraint.current_constraints
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
            if rect.nodeId != ID:
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
                if rect.rotation_index==1 or rect.rotation_index==3:
                    index=0 # index=0 means minwidth constraint
                else:
                    index=4 # index=4 means minheight constraint
                c = constraint.constraint(index)
                #index = 4
                # getting appropriate constraint value
                value1 = constraint.constraint.getConstraintVal(c,type=rect.cell.type,Types=Types)
                if rect.current!=None:
                    if rect.current['AC']!=0 or rect.current['DC']!=0:
                        current_rating=rect.current['AC']+rect.current['DC']
                    current_ratings=constraint.constraint.current_constraints.keys()
                    current_ratings.sort()
                    if len(current_ratings)>1:
                        range_c=current_ratings[1]-current_ratings[0]
                        index=math.ceil(current_rating/range_c)*range_c
                        if index in constraint.constraint.current_constraints:
                            value2=constraint.constraint.current_constraints[index]
                        else:
                            print "ERROR!!!Constraint for the Current Rating is not defined"
                    else:
                        value2=constraint.constraint.current_constraints[current_rating]

                else:
                    value2=None
                if value2!=None:
                    if value2>value1:
                        value=value2
                    else:
                        value=value1
                else:
                    value=value1

                Weight = 2 * value
                for k, v in constraint.constraint.comp_type.items():
                    if str(Types.index(rect.cell.type)) in v:
                        comp_type = k
                        break
                    else:
                        comp_type = None
                e = Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id,
                         Weight, comp_type, East,
                         West, northWest, southEast)

                edgesv.append(
                    Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id,
                         Weight, comp_type, East, West, northWest, southEast)) # appending edge for vertical constraint graph

                self.vertexMatrixv[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest)) # updating vertical constraint graph adjacency matrix


                if Extend_h==1: # if its a horizontal extension
                    c = constraint.constraint(3) # index=3 means minextension type constraint
                    index = 3
                    rect.vertex1 = origin
                    rect.vertex2 = dest
                    #value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                    value1 = constraint.constraint.getConstraintVal(c, type=rect.cell.type, Types=Types)
                    if rect.current != None:
                        if rect.current['AC'] != 0 or rect.current['DC'] != 0:
                            current_rating = rect.current['AC'] + rect.current['DC']
                        current_ratings = constraint.constraint.current_constraints.keys()
                        current_ratings.sort()
                        if len(current_ratings) > 1:
                            range_c = current_ratings[1] - current_ratings[0]
                            index = math.ceil(current_rating / range_c) * range_c
                            if index in constraint.constraint.current_constraints:
                                value2 = constraint.constraint.current_constraints[index]
                            else:
                                print "ERROR!!!Constraint for the Current Rating is not defined"
                        else:
                            value2=constraint.constraint.current_constraints[current_rating]

                    else:
                        value2 = None
                    if value2 != None:
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:
                        value = value1

                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, Weight,East,West, northWest, southEast)
                    edgesh.append(Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight, East,West, northWest, southEast)) # appending in horizontal constraint graph edges
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest)) # updating horizontal constraint graph matrix

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

                    t2 = Types.index(rect.NORTH.cell.type)
                    t1 = Types.index(rect.SOUTH.cell.type)

                    c = constraint.constraint(1)  # index=1 means min spacing constraint
                    index = 1

                    # Applying I-V constraints
                    value1 = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)

                    if rect.NORTH.voltage!=None and rect.SOUTH.voltage!=None:
                        #voltage_diff1=abs(rect.NORTH.voltage[0]-rect.SOUTH.voltage[1])
                        #voltage_diff2=abs(rect.NORTH.voltage[1]-rect.SOUTH.voltage[0])
                        #voltage_diff=max(voltage_diff1,voltage_diff2)
                        print "N",rect.NORTH.voltage,rect.NORTH.cell.x,rect.NORTH.cell.y
                        print "S",rect.SOUTH.voltage,rect.SOUTH.cell.x,rect.SOUTH.cell.y
                        print rel_cons
                        voltage_diff=self.find_voltage_difference(rect.NORTH.voltage,rect.SOUTH.voltage,rel_cons)

                        # tolerance is considered 10%

                        if voltage_diff-0.1*voltage_diff>100:
                            voltage_diff=voltage_diff-0.1*voltage_diff
                        else:
                            voltage_diff=0
                        #print "V_DIFF", voltage_diff
                        voltage_differences = constraint.constraint.voltage_constraints.keys()
                        voltage_differences.sort()

                        if len(voltage_differences) > 1:
                            range_v = voltage_differences[1] - voltage_differences[0]
                            index = math.ceil(voltage_diff / range_v) * range_v
                            if index in constraint.constraint.voltage_constraints:
                                value2 = constraint.constraint.voltage_constraints[index]

                            else:
                                print "ERROR!!!Constraint for the Voltage difference is not defined",voltage_diff
                                print voltage_differences
                        else:
                            value2 = constraint.constraint.voltage_constraints[voltage_diff]

                    else:
                        value2 = None
                    if value2 != None:
                        #print"value", value2
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:

                        value = value1
                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id, Weight,North,
                             South, westNorth, eastSouth)
                    edgesv.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # checking for minimum enclosure constraint: if current tile is bottom tile its north tile should be foreground tile and south tile should be boundary tile and not in stitchlist

                elif rect.NORTH.nodeId != ID and rect.SOUTH not in cornerStitch_v.stitchList and rect.NORTH in cornerStitch_v.stitchList:
                #elif rect.NORTH.nodeId != ID and (rect.SOUTH.cell.type == "EMPTY" or rect.SOUTH not in cornerStitch_v.stitchList):


                    t2 = Types.index(rect.NORTH.cell.type)
                    t1 = Types.index(rect.cell.type)
                    c = constraint.constraint(2)  # index=2 means enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth)
                    edgesv.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # checking for minimum enclosure constraint: if current tile is top tile its south tile should be foreground tile and north tile should be boundary tile and not in stitchlist
                elif rect.SOUTH.nodeId != ID and rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH in cornerStitch_v.stitchList:
                #elif rect.SOUTH.nodeId != ID and (rect.NORTH.cell.type == "EMPTY" or rect.NORTH not in cornerStitch_v.stitchList):
                    t2 = Types.index(rect.SOUTH.cell.type)
                    t1 =Types.index(rect.cell.type)
                    c = constraint.constraint(2)  # index=2 means min enclosure constraint
                    index = 2
                    value =constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

                # if current tile is stretched from bottom to top, it's a complete background tile and should be a min height constraint generator. It's redundant actually as this tile will be considered
                # as foreground tile in its background plane's cornerstitched layout, there it will be again considered as min height constraint generator.
                elif rect.NORTH not in cornerStitch_v.stitchList and rect.SOUTH not in cornerStitch_v.stitchList:
                    if rect.rotation_index == 1 or rect.rotation_index == 3:
                        index = 0  # index=0 means minheight constraint
                    else:
                        index = 4  # index=4 means minheight constraint
                    c = constraint.constraint(index)

                    value1 = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                    # Applying I-V constraints
                    if rect.current != None:
                        if rect.current['AC'] != 0 or rect.current['DC'] != 0:
                            current_rating = rect.current['AC'] + rect.current['DC']
                        current_ratings = constraint.constraint.current_constraints.keys()
                        current_ratings.sort()
                        if len(current_ratings) > 1:
                            range_c = current_ratings[1] - current_ratings[0]
                            index = math.ceil(current_rating / range_c) * range_c
                            if index in constraint.constraint.current_constraints:
                                value2 = constraint.constraint.current_constraints[index]
                            else:
                                print "ERROR!!!Constraint for the Current Rating is not defined"
                        else:
                            value2=constraint.constraint.current_constraints[current_rating]

                    else:
                        value2 = None
                    if value2 != None:
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:
                        value = value1

                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth)
                    edgesv.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             North, South, westNorth, eastSouth))
                    self.vertexMatrixv[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))






        '''
        creating edges for horizontal constraint graph from horizontal cornerstitched tiles. index=0: min width, index=1: min spacing, index=2: min Enclosure, index=3: min extension
        same as vertical constraint graph edge generation. all north are now east, south are now west. if vertical extension rule is applicable to any tile vertical constraint graph is generated.
        voltage dependent spacing for empty tiles and current dependent widths are applied for foreground tiles.
        
        '''
        for rect in cornerStitch_h.stitchList:
            Extend_v = 0
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

                if rect.rotation_index==1 or rect.rotation_index==3:
                    index=4 # index=4 means minheight constraint
                else:
                    index=0 # index=0 means minwidth constraint
                c = constraint.constraint(index)

                #value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                # applying I-V constraint values
                value1 = constraint.constraint.getConstraintVal(c, type=rect.cell.type, Types=Types)
                if rect.current != None:
                    if rect.current['AC']!=0 or rect.current['DC']!=0:
                        current_rating=rect.current['AC']+rect.current['DC']
                    current_ratings = constraint.constraint.current_constraints.keys()
                    current_ratings.sort()
                    if len(current_ratings) > 1:
                        range_c = current_ratings[1] - current_ratings[0]
                        index = math.ceil(current_rating / range_c) * range_c # finding the nearest upper limit in the current ratings
                        if index in constraint.constraint.current_constraints:
                            value2 = constraint.constraint.current_constraints[index]
                        else:
                            print "ERROR!!!Constraint for the Current Rating is not defined"
                    else:
                        value2=constraint.constraint.current_constraints[current_rating]

                else:
                    value2 = None
                if value2 != None:
                    if value2 > value1:
                        value = value2
                    else:
                        value = value1
                else:
                    value = value1



                Weight = 2 * value
                for k, v in constraint.constraint.comp_type.items():
                    if str(Types.index(rect.cell.type)) in v:
                        comp_type = k
                        break
                    else:
                        comp_type = None
                e = Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id,
                         Weight, comp_type, North, South, westNorth, eastSouth)

                edgesh.append(
                    Edge(origin1, dest1, value, index, str(Types.index(rect.cell.type)), id,
                         Weight, comp_type, North, South, westNorth, eastSouth))
                self.vertexMatrixh[ID][origin1][dest1].append(Edge.getEdgeWeight(e, origin, dest))


                if Extend_v==1:
                    c = constraint.constraint(3)
                    index = 3 # min extension
                    rect.vertex1 = origin
                    rect.vertex2 = dest
                    #value = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)

                    value1 = constraint.constraint.getConstraintVal(c, type=rect.cell.type, Types=Types)
                    if rect.current != None:
                        if rect.current['AC'] != 0 or rect.current['DC'] != 0:
                            current_rating = rect.current['AC'] + rect.current['DC']
                        current_ratings = constraint.constraint.current_constraints.keys()
                        current_ratings.sort()
                        if len(current_ratings) > 1:
                            range_c = current_ratings[1] - current_ratings[0]
                            index = math.ceil(current_rating / range_c) * range_c
                            if index in constraint.constraint.current_constraints:
                                value2 = constraint.constraint.current_constraints[index]
                            else:
                                print "ERROR!!!Constraint for the Current Rating is not defined"
                        else:
                            value2=constraint.constraint.current_constraints[current_rating]

                    else:
                        value2 = None
                    if value2 != None:
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:
                        value = value1

                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight, North,
                             South, westNorth, eastSouth)

                    edgesv.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight, North,
                             South, westNorth, eastSouth))
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
                    t2 = Types.index(rect.EAST.cell.type)
                    t1 = Types.index(rect.WEST.cell.type)

                    c = constraint.constraint(1)
                    index = 1
                    #value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    # Applying I-V constraints
                    value1 = constraint.constraint.getConstraintVal(c, source=t1, dest=t2, Types=Types)

                    if rect.EAST.voltage != None and rect.WEST.voltage != None:
                        #voltage_diff1 = abs(rect.EAST.voltage[0] - rect.WEST.voltage[1])
                        #voltage_diff2 = abs(rect.EAST.voltage[1] - rect.WEST.voltage[0])
                        #voltage_diff = max(voltage_diff1, voltage_diff2)
                        #print "E",rect.EAST.voltage,rect.EAST.cell.x,rect.EAST.cell.y
                        #print "W",rect.WEST.voltage,rect.WEST.cell.x,rect.WEST.cell.y
                        voltage_diff=self.find_voltage_difference(rect.EAST.voltage,rect.WEST.voltage,rel_cons)
                        # tolerance is considered 10%
                        if voltage_diff - 0.1 * voltage_diff > 100:
                            voltage_diff = voltage_diff - 0.1 * voltage_diff
                        else:
                            voltage_diff=0
                        #print "V_DIFF", voltage_diff
                        voltage_differences = constraint.constraint.voltage_constraints.keys()
                        voltage_differences.sort()
                        voltage_differences = constraint.constraint.voltage_constraints.keys()
                        voltage_differences.sort()
                        if len(voltage_differences) > 1:
                            range_v = voltage_differences[1] - voltage_differences[0]
                            index = math.ceil(voltage_diff / range_v) * range_v
                            if index in constraint.constraint.voltage_constraints:
                                value2 = constraint.constraint.voltage_constraints[index]

                            else:
                                print "ERROR!!!Constraint for the Voltage difference is not defined"
                        else:
                            value2 = constraint.constraint.voltage_constraints[voltage_diff]

                    else:
                        value2 = None
                    if value2 != None:
                        #print"value", value2
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:
                        value = value1


                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight, East,
                             West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST.nodeId != ID and rect.WEST not in cornerStitch_h.stitchList and rect.EAST in cornerStitch_h.stitchList:
                #elif rect.EAST.nodeId != ID and (rect.WEST.cell.type == "EMPTY" or rect.WEST not in cornerStitch_h.stitchList):

                    t2 = Types.index(rect.EAST.cell.type)
                    t1 = Types.index(rect.cell.type)
                    c = constraint.constraint(2)  # min enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.WEST.nodeId != ID and rect.EAST not in cornerStitch_h.stitchList and rect.WEST in cornerStitch_h.stitchList:
                #elif rect.WEST.nodeId != ID and (rect.EAST.cell.type == "EMPTY" or rect.EAST not in cornerStitch_h.stitchList):
                    t2 = Types.index(rect.WEST.cell.type)
                    t1 = Types.index(rect.cell.type)
                    c = constraint.constraint(2)  # min enclosure constraint
                    index = 2
                    value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
                    Weight = 2 * value
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))
                elif rect.EAST not in cornerStitch_h.stitchList and rect.WEST not in cornerStitch_h.stitchList:

                    if rect.rotation_index == 1 or rect.rotation_index == 3:
                        index = 4  # index=4 means minheight  constraint
                    else:
                        index = 0  # index=0 means minWidth constraint
                    c = constraint.constraint(index)

                    value1 = constraint.constraint.getConstraintVal(c, type=rect.cell.type,Types=Types)
                    # Applying I-V constraints
                    if rect.current != None:
                        if rect.current['AC'] != 0 or rect.current['DC'] != 0:
                            current_rating = rect.current['AC'] + rect.current['DC']
                        current_ratings = constraint.constraint.current_constraints.keys()
                        current_ratings.sort()
                        if len(current_ratings) > 1:
                            range_c = current_ratings[1] - current_ratings[0]
                            index = math.ceil(current_rating / range_c) * range_c
                            if index in constraint.constraint.current_constraints:
                                value2 = constraint.constraint.current_constraints[index]
                            else:
                                print "ERROR!!!Constraint for the Current Rating is not defined"
                        else:
                            value2=constraint.constraint.current_constraints[current_rating]

                    else:
                        value2 = None
                    if value2 != None:
                        if value2 > value1:
                            value = value2
                        else:
                            value = value1
                    else:
                        value = value1


                    Weight = 2 * value
                    # print "val",value
                    for k, v in constraint.constraint.comp_type.items():
                        if str(Types.index(rect.cell.type)) in v:
                            comp_type = k
                            break
                        else:
                            comp_type = None
                    e = Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,
                             Weight, comp_type,
                             East, West, northWest, southEast)

                    edgesh.append(
                        Edge(origin, dest, value, index, str(Types.index(rect.cell.type)), id,Weight,comp_type,
                             East, West, northWest, southEast))
                    self.vertexMatrixh[ID][origin][dest].append(Edge.getEdgeWeight(e, origin, dest))

        ## adding missing edges for shared coordinate patterns
        for i in Horizontal_patterns:
            r1=i[0]
            r2=i[1]
            origin=self.ZDL_H[ID].index(r1.EAST.cell.x)
            dest=self.ZDL_H[ID].index(r2.cell.x)
            t2 = Types.index(r2.cell.type)
            t1 = Types.index(r1.cell.type)
            c = constraint.constraint(1) #sapcing constraints
            index = 1
            #value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)
            # Applying I-V constraints
            value1 = constraint.constraint.getConstraintVal(c, source=t1, dest=t2, Types=Types)

            if r1.voltage != None and r2.voltage != None:
                # voltage_diff1 = abs(rect.EAST.voltage[0] - rect.WEST.voltage[1])
                # voltage_diff2 = abs(rect.EAST.voltage[1] - rect.WEST.voltage[0])
                # voltage_diff = max(voltage_diff1, voltage_diff2)
                voltage_diff = self.find_voltage_difference(rect.EAST.voltage, rect.WEST.voltage, rel_cons)
                voltage_differences = constraint.constraint.voltage_constraints.keys()
                voltage_differences.sort()
                if len(voltage_differences) > 1:
                    range_v = voltage_differences[1] - voltage_differences[0]
                    index = math.ceil(voltage_diff / range_v) * range_v
                    if index in constraint.constraint.voltage_constraints:
                        value2 = constraint.constraint.voltage_constraints[index]
                    else:
                        print "ERROR!!!Constraint for the Voltage difference is not defined"
                else:
                    value2 = constraint.constraint.voltage_constraints[voltage_diff]

            else:
                value2 = None
            if value2 != None:
                if value2 > value1:
                    value = value2
                else:
                    value = value1
            else:
                value = value1





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
            #value = constraint.constraint.getConstraintVal(c, source=t1, dest=t2,Types=Types)

            # Applying I-V constraints
            value1 = constraint.constraint.getConstraintVal(c, source=t1, dest=t2, Types=Types)

            if r1.voltage != None and r2.voltage != None:
                # voltage_diff1 = abs(rect.EAST.voltage[0] - rect.WEST.voltage[1])
                # voltage_diff2 = abs(rect.EAST.voltage[1] - rect.WEST.voltage[0])
                # voltage_diff = max(voltage_diff1, voltage_diff2)
                voltage_diff = self.find_voltage_difference(rect.EAST.voltage, rect.WEST.voltage, rel_cons)
                voltage_differences = constraint.constraint.voltage_constraints.keys()
                voltage_differences.sort()
                if len(voltage_differences) > 1:
                    range_v = voltage_differences[1] - voltage_differences[0]
                    index = math.ceil(voltage_diff / range_v) * range_v
                    if index in constraint.constraint.voltage_constraints:
                        value2 = constraint.constraint.voltage_constraints[index]
                    else:
                        print "ERROR!!!Constraint for the Voltage difference is not defined"
                else:
                    value2 = constraint.constraint.voltage_constraints[voltage_diff]

            else:
                value2 = None
            if value2 != None:
                if value2 > value1:
                    value = value2
                else:
                    value = value1
            else:
                value = value1


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
                edgesh_new.append(Edge(source, destination, value, index, type='missing', Weight=2 * value, id=None))

                ########### Fixed dimension handling algorithm################

        # creating a dictionary of HCG edges where key=(src,dest) and value=[constraint value,type,index of constraint, weight, component type("Device")]
        for foo in edgesh_new:
            dictList1.append(foo.getEdgeDict())
        dict_edge_h = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]
            dict_edge_h[k].append(v)

        # finding all removable vertices in the HCG # All fixed edge destination are removable candidate
        for i in range(len(self.vertexMatrixh[ID])):
            for j in range(len(self.vertexMatrixh[ID])):
                for k in self.vertexMatrixh[ID][i][j]:
                    if k[4] == 'Device':
                        remove_node = self.node_remove_check(i, j, ID, dict_edge_h,h=1)  # calling function to check if the node is removable
                        if remove_node != None:
                            key = ID
                            self.remove_nodes_h.setdefault(key, [])
                            if remove_node not in self.remove_nodes_h[ID]:
                                self.remove_nodes_h[ID].append(remove_node)  # maintaining a dictionary of removable vertices where key= node ID of the tree and value=list of removable vertices
                                edgesh_new,dict_edge_h=self.node_remove_h(ID,dict_edge_h,edgesh_new)
                                # on that node of the tree
        # print"Removed",ID, self.remove_nodes_h






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
                edgesv_new.append(Edge(source, destination, value, index, type='missing', Weight=2 * value, id=None))

        dictList2 = []
        for foo in edgesv_new:
            dictList2.append(foo.getEdgeDict())
            # print"F", foo.getEdgeDict()
        dict_edge_v = defaultdict(list)
        for i in dictList2:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            dict_edge_v[k].append(v)
        # print "D",ID,dict_edge_v
        for i in range(len(self.vertexMatrixv[ID])):
            for j in range(len(self.vertexMatrixv[ID])):
                for k in self.vertexMatrixv[ID][i][j]:
                    if k[4] == 'Device':

                        remove_node = self.node_remove_check(i, j, ID, dict_edge_v, h=0)


                        if remove_node != None:
                            key = ID
                            self.remove_nodes_v.setdefault(key, [])
                            if remove_node not in self.remove_nodes_v[ID]:
                                self.remove_nodes_v[ID].append(remove_node)
                                edgesv_new,dict_edge_v=self.node_remove_v(ID,dict_edge_v,edgesv_new)

        #print"RemovedV", ID, self.remove_nodes_v
        '''
        if ID in self.remove_nodes_v.keys():
            for j in self.remove_nodes_v[ID]:
                for key, value in dict_edge_v.items():
                    for v in value:
                        if v[4] == 'Device' and key[1] == j:
                            k = key[0]

                targets = {}

                for i in range(j, len(self.vertexMatrixv[ID])):

                    if len(dict_edge_v[(j, i)]) > 0:

                        values = []
                        for v in dict_edge_v[(j, i)]:
                            values.append(v[0])
                        max_value = max(values)
                        targets[i] = max_value
                # print"T",targets
                for i in targets.keys():
                    src = k
                    dest = i
                    for v in dict_edge_v[(k, j)]:
                        value = v[0] + targets[i]
                        index = 1
                        # print"VB",v[0] ,src,dest,value

                        edgesv_new.append(Edge(src, dest, value, index, type='bypassed', Weight=2 * value, id=None))
                        # dict_edge_v[(src,dest)]=[value,index,2*value,'bypassed']
                for edge in edgesv_new:
                    if edge.source == j:
                        edgesv_new.remove(edge)
        '''
        ################### Fixed edge handling end###########################################


        self.edgesh_new[ID] = edgesh_new
        self.edgesv_new[ID] = edgesv_new

        self.edgesh[ID] = edgesh
        self.edgesv[ID] = edgesv

        # if removable vertices are found, all outgoinf edge from that node need to be deleted but bypassed with constraint value
    def node_remove_h(self, ID, dict_edge_h, edgesh_new):
        for j in self.remove_nodes_h[ID]:
            for key, value in dict_edge_h.items():
                for v in value:
                    if v[4] == 'Device' and key[1] == j:
                        k = key[
                            0]  # k is the source of that fixed edge which causes the destination node to be removable

            targets = {}
            # if there are multiple edges from a removable vertex to others, the maximum constraint value is detected and stored with that vertex
            for i in range(j, len(self.vertexMatrixh[ID])):
                if len(dict_edge_h[(j, i)]) > 0:
                    values = []
                    for v in dict_edge_h[(j, i)]:
                        values.append(v[0])
                    max_value = max(values)
                    targets[
                        i] = max_value  # dictionary, where key=new target vertex after bypassing removable vertex and value= maximum constraint value from removable vertex to that vertex

            # Adding bypassed edges to the node's edgelist
            for i in targets.keys():
                src = k
                dest = i
                for v in dict_edge_h[(k, j)]:
                    value = v[0] + targets[
                        i]  # calculating new constraint value from k to i (k=source,i=new target)
                    index = 1
                    edgesh_new.append(Edge(src, dest, value, index, type='bypassed', Weight=2 * value,
                                           id=None))  # adding the new edge
            # since all edges are bypassed which are generated from removable vertex, those edges are noe removed.
            for edge in edgesh_new:
                if edge.source == j:
                    edgesh_new.remove(edge)
        dictList1 = []
        for foo in edgesh_new:
            dictList1.append(foo.getEdgeDict())
        dict_edge_h = defaultdict(list)
        for i in dictList1:
            k, v = list(i.items())[0]
            dict_edge_h[k].append(v)
        return edgesh_new,dict_edge_h

    def node_remove_v(self,ID,dict_edge_v,edgesv_new):
        for j in self.remove_nodes_v[ID]:
            for key, value in dict_edge_v.items():
                for v in value:
                    if v[4] == 'Device' and key[1] == j:
                        k = key[0]

            targets = {}

            for i in range(j, len(self.vertexMatrixv[ID])):

                if len(dict_edge_v[(j, i)]) > 0:

                    values = []
                    for v in dict_edge_v[(j, i)]:
                        values.append(v[0])
                    max_value = max(values)
                    targets[i] = max_value
            # print"T",targets
            for i in targets.keys():
                src = k
                dest = i
                for v in dict_edge_v[(k, j)]:
                    value = v[0] + targets[i]
                    index = 1
                    #print"VB",ID,v[0] ,src,dest,value

                    edgesv_new.append(Edge(src, dest, value, index, type='bypassed', Weight=2 * value, id=None))
                    # dict_edge_v[(src,dest)]=[value,index,2*value,'bypassed']
            for edge in edgesv_new:
                if edge.source == j:
                    #print "removed",edge.source,edge.dest,edge.constraint,edge.type
                    edgesv_new.remove(edge)
        dictList2 = []
        for foo in edgesv_new:
            dictList2.append(foo.getEdgeDict())
            # print"F", foo.getEdgeDict()
        dict_edge_v = defaultdict(list)
        for i in dictList2:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            dict_edge_v[k].append(v)
        return edgesv_new,dict_edge_v

    def node_remove_check(self,src,dest,ID,dict_edge,h):
        """

        :param src: source of fixed edge
        :param dest: potential removable vertex (destination of fixed edge)
        :param ID: node ID of the tree
        :param dict_edge: dictionary of edges for that node of the tree
        :param h: h=0: VCG,1: HCG
        :return: whether destination vertex is removable or not
        """
        flag=False
        i=src
        j=dest

        if h==1:
            n=len(self.vertexMatrixh[ID])-1
        else:
            n = len(self.vertexMatrixv[ID])-1

        allowed=[0,i,j,n] # if any incoming edge from source vertex or fixed edge src vertex it should be ok



        for m in range(0,n):

            #,ID,m,j, dict_edge[(m,j)]

            if len(dict_edge[(m,j)])!=0 and m not in allowed :

                flag=False
                break
            else:
                flag=True


        if flag==True:
            return j
        else:
            return None

    def HcgEval(self, level,Random,seed, N):
        """

        :param level: mode of operation
        :param N: number of layouts to be generated
        :return: evaluated HCG for N layouts
        """
        if level == 1:
            #TBeval is Top_Bottom evaluation class object, where all constraint graphs with propagated room from child are stored
            for element in reversed(self.Tbeval):
                if element.parentID == None:
                    G2 = element.graph # extracting graph for root node of the tree

                    label4 = copy.deepcopy(element.labels)

                    d3 = defaultdict(list)
                    for i in label4:
                        (k1), v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
                        d3[(k1)].append(v)
                    # print d3
                    edgelabels = {}
                    edge_label = {}
                    edge_weight = {}
                    for (k), v in d3.items():
                        values = []
                        for j in range(len(v)):
                            values.append(v[j][0])
                        value = max(values)
                        for j in range(len(v)):
                            if v[j][0] == value:
                                edgelabels[(k)] = v[j]
                                edge_label[k] = value
                                edge_weight[k] = v[j][3]


                    H_all=[]
                    s = seed
                    for i in range(N):
                        seed = s + i * 1000
                        count = 0
                        H = []

                        for (k), v in edgelabels.items():
                            #print k,v
                            count += 1
                            if v[2] == 2 and v[1] == '0':  # ledge width
                                val = v[0]
                            elif v[2] == 1 and v[1] == '0':  # white spacing
                                val = v[0]
                            else:
                                if (N < 150):
                                    SD = N * 3000  # standard deviation for randomization
                                else:
                                    SD = 10000
                                random.seed(seed + count * 1000)
                                val = int(min(1000 * v[0], max(v[0], random.gauss(v[0], SD))))
                            # print (k),v[0],val
                            H.append((k[0], k[1], val))
                        H_all.append(H)
                    # print len(D_3), D_3
                    #print H_all

                    G_all = []
                    for i in range(len(H_all)):
                        G = nx.MultiDiGraph()
                        n = list(G2.nodes())
                        G.add_nodes_from(n)
                        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                        G.add_weighted_edges_from(H_all[i])
                        G_all.append(G)
                    # print G_all
                    loct = []
                    for i in range(len(G_all)):
                        new_Xlocation = []
                        A = nx.adjacency_matrix(G_all[i])
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
                            new_Xlocation.append(loc_i[key])
                        loct.append(loc_i)
                        # print"LOCT",locta
                        # print new_Xlocation
                        self.NEWXLOCATION.append(new_Xlocation)


                    n = list(G2.nodes())
                    Location = {}
                    key = element.ID
                    Location.setdefault(key, [])

                    for i in range(len(self.NEWXLOCATION)):
                        loct = {}
                        for j in range(len(self.ZDL_H[element.ID])):
                            loct[self.ZDL_H[element.ID][j]] = self.NEWXLOCATION[i][j]
                        Location[element.ID].append(loct)
                        # print Location
                    self.LocationH = Location


                    #
                else:
                    # continue
                    if element.parentID in self.LocationH.keys():

                        # if element.parentID==1:
                        for node in self.H_NODELIST:
                            if node.id == element.parentID:
                                PARENT = node
                        ZDL_H = []
                        for rect in PARENT.stitchList:
                            if rect.nodeId == element.ID:
                                if rect.cell.x not in ZDL_H:
                                    ZDL_H.append(rect.cell.x)
                                    ZDL_H.append(rect.EAST.cell.x)
                                if rect.EAST.cell.x not in ZDL_H:
                                    ZDL_H.append(rect.EAST.cell.x)
                            # print ZDL_V



                        P = set(ZDL_H)
                        ZDL_H = list(P)

                        V = self.LocationH[element.parentID]
                        #print "V",V
                        loct = []
                        count=0
                        for location in V:

                            seed=seed + count * 1000
                            count+=1
                            self.Loc_X = {}

                            for coordinate in self.ZDL_H[element.ID]:

                                # if element.parentID==1:
                                for k, v in location.items():
                                    if k == coordinate and k in ZDL_H:
                                        self.Loc_X[self.ZDL_H[element.ID].index(coordinate)] = v
                                        # print "v",self.Loc_X
                                    else:
                                        continue
                                '''
                                else:
                                    for k, v in location.items():
                                        if k==coordinate:
                                            self.Loc_X[self.ZDL_H[element.ID].index(coordinate)]=v
                                            #print "v",self.Loc_X
                                        else:
                                            continue
                                '''

                            #print"LOC",self.Loc_X
                            d3 = defaultdict(list)
                            W = defaultdict(list)
                            d4 = defaultdict(list) # tracking fixed width components
                            for i in element.labels:
                                #print i
                                k, v = list(i.items())[0]
                                # print v[0]
                                d3[k].append(v[0])

                                W[k].append(v[3])

                                if v[4]=="Device":
                                    d4[k].append(v[0])

                                '''
                                if v[3]==None:
                                    W[k].append(1)
                                else:
                                    W[k].append(v[3])
                                '''

                            X = {}
                            H = []
                            Fix={}
                            #Fixed=[]
                            Weights = {}
                            for i, j in d3.items():
                                X[i] = max(j)
                            #print "XX",element.ID,X


                            for i, j in d4.items():
                                Fix[i] = max(j)
                            for i, j in W.items():
                                Weights[i] = max(j)
                            #print"X", X,Fix
                            for k, v in X.items():
                                H.append((k[0], k[1], v))
                            #for k, v in Fix.items():
                                #Fixed.append((k[0], k[1], v))
                                #Fixed
                            # print "H", H
                            #print "Fix",Fix
                            G = nx.MultiDiGraph()
                            n = list(element.graph.nodes())
                            G.add_nodes_from(n)
                            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                            G.add_weighted_edges_from(H)
                            #self.drawGraph_h("new",G,None)
                            self.FUNCTION(G,element.ID,Random,sid=seed)
                            # print"FINX",self.Loc_X
                            loct.append(self.Loc_X)
                        #print "loct", loct
                        xloc = []
                        for k in range(len(loct)):
                            loc = {}
                            for k, v in loct[k].items():
                                loc[self.ZDL_H[element.ID][k]] = v
                            xloc.append(loc)
                        self.LocationH[element.ID] = xloc
                        #print "N",self.LocationH

        elif level == 2 or level == 3:
            for element in reversed(self.Tbeval):
                if element.parentID == None:

                    loct = []
                    s = seed
                    for i in range(N):
                        self.seed_h.append(s + i * 1000)
                    for m in range(N):  ### No. of outputs

                        d3 = defaultdict(list)
                        W = defaultdict(list)
                        for i in element.labels:
                            k, v = list(i.items())[0]
                            # print v[0]
                            d3[k].append(v[0])
                            W[k].append(v[3])
                            '''
                            if v[3]==None:
                                W[k].append(1)
                            else:
                                W[k].append(v[3])
                            '''
                        # print "D3", d3,W
                        X = {}
                        H = []
                        Weights = {}
                        for i, j in d3.items():
                            X[i] = max(j)
                        for i, j in W.items():
                            Weights[i] = max(j)
                        # print"X",Weights
                        for k, v in X.items():
                            H.append((k[0], k[1], v))
                        # print "H", H
                        G = nx.MultiDiGraph()
                        n = list(element.graph.nodes())
                        G.add_nodes_from(n)
                        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                        G.add_weighted_edges_from(H)
                        if level == 2:
                            self.Loc_X = {}
                            for k, v in self.XLoc.items():
                                if k in n:
                                    self.Loc_X[k] = v
                        elif level == 3:
                            self.Loc_X = {}

                            for i, j in self.XLoc.items():
                                # print j
                                if i == 1:
                                    for k, v in j.items():
                                        self.Loc_X[k] = v

                                        # print v
                        #print"XLoc_before", self.Loc_X

                        self.FUNCTION(G, element.ID,Random,sid=self.seed_h[m])
                        #print"FINX_after",self.Loc_X
                        loct.append(self.Loc_X)

                    self.NEWXLOCATION = loct

                    # print "N",self.ZDL_H[element.ID],self.NEWXLOCATION
                    Location = {}
                    key = element.ID
                    Location.setdefault(key, [])

                    for i in range(len(self.NEWXLOCATION)):
                        loct = {}
                        for j in range(len(self.ZDL_H[element.ID])):
                            loct[self.ZDL_H[element.ID][j]] = self.NEWXLOCATION[i][j]
                        Location[element.ID].append(loct)
                        # print Location
                    self.LocationH = Location
                    #print"L", self.LocationH
                    #
                else:
                    # continue
                    if element.parentID in self.LocationH.keys():

                        # if element.parentID == 1:
                        for node in self.H_NODELIST:
                            if node.id == element.parentID:
                                PARENT = node
                        ZDL_H = []
                        for rect in PARENT.stitchList:
                            if rect.nodeId == element.ID:
                                if rect.cell.x not in ZDL_H:
                                    ZDL_H.append(rect.cell.x)
                                    ZDL_H.append(rect.EAST.cell.x)
                                if rect.EAST.cell.x not in ZDL_H:
                                    ZDL_H.append(rect.EAST.cell.x)



                        P = set(ZDL_H)
                        ZDL_H = list(P)
                        ZDL_H.sort()

                        V = self.LocationH[element.parentID]
                        # print "V",V
                        loct = []
                        for location in V:
                            self.Loc_X = {}

                            # print NLIST
                            for coordinate in self.ZDL_H[element.ID]:

                                # if element.parentID == 1:

                                for k, v in location.items():
                                    if k == coordinate and k in ZDL_H:
                                        # if self.ZDL_H[element.ID].index(coordinate) not in self.Loc_X:
                                        # if self.ZDL_H[element.ID].index(coordinate) not in NLIS
                                        self.Loc_X[self.ZDL_H[element.ID].index(coordinate)] = v


                                    else:
                                        continue


                            NLIST = []
                            for k, v in self.Loc_X.items():
                                NLIST.append(k)
                            # NODES = reversed(NLIST)
                            # print NODES
                            if level == 3:
                                for i, j in self.XLoc.items():
                                    if i == element.ID:
                                        for k, v in j.items():
                                            # self.Loc_X[k]=self.Loc_X[0]+v

                                            for node in NLIST[::-1]:

                                                if node >= k:
                                                    continue
                                                else:
                                                    # print node, k, v, self.Loc_X[node]
                                                    p = self.Loc_X[node]
                                                    # print p + v
                                                    self.Loc_X[k] = p + v
                                                    break

                            # print "v2", self.Loc_X
                            d3 = defaultdict(list)
                            d4 = defaultdict(list)
                            W = defaultdict(list)
                            for i in element.labels:
                                k, v = list(i.items())[0]
                                # print v[0]
                                d3[k].append(v[0])
                                W[k].append(v[3])
                                #print k,v
                                if v[4]=="Device":
                                    d4[k].append(v[0])
                                '''
                                if v[3]==None:
                                    W[k].append(1)
                                else:
                                    W[k].append(v[3])
                                '''
                            # print "D3", d3,W
                            X = {}
                            H = []
                            Fix={}
                            Weights = {}

                            for i, j in d3.items():
                                X[i] = max(j)
                                if i[0] in self.Loc_X.keys() and i[1] in self.Loc_X.keys():
                                    # print self.Loc_Y[i[0]],self.Loc_Y[i[1]]
                                    if (self.Loc_X[i[1]] - self.Loc_X[i[0]]) < max(j):
                                        print "ERROR", i, max(j), self.Loc_X[i[1]] - self.Loc_X[i[0]]

                                        # distance=max(j)-abs((self.Loc_X[i[1]]-self.Loc_X[i[0]]))
                                        # self.Loc_X[i[1]]+=distance

                                    else:
                                        continue
                            # print "v3", self.Loc_X,X
                            for i, j in d4.items():
                                Fix[i] = max(j)
                            #print Fix
                            for i, j in W.items():
                                Weights[i] = max(j)
                            # print"X",Weights
                            for k, v in X.items():
                                H.append((k[0], k[1], v))
                            #print "H", Fix
                            G = nx.MultiDiGraph()
                            n = list(element.graph.nodes())
                            G.add_nodes_from(n)
                            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                            G.add_weighted_edges_from(H)
                            self.FUNCTION(G,element.ID, Random,sid=seed)
                            # print"FINX",self.Loc_X
                            loct.append(self.Loc_X)
                        #print "loct", loct
                        xloc = []
                        for k in range(len(loct)):
                            loc = {}
                            for k, v in loct[k].items():
                                loc[self.ZDL_H[element.ID][k]] = v
                            xloc.append(loc)
                        self.LocationH[element.ID] = xloc
                    #print"Final_H", self.LocationH




    def cgToGraph_h(self, ID, edgeh, parentID, level):
        '''
        :param ID: Node ID
        :param edgeh: horizontal edges for that node's constraint graph
        :param parentID: node id of it's parent
        :param level: mode of operation
        :param N: number of layouts to be generated
        :return: constraint graph and solution for different modes
        '''

        G2 = nx.MultiDiGraph()
        G3 = nx.MultiDiGraph()
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
        # print "d",ID, edge_labels1
        nodes = [x for x in range(len(self.ZDL_H[ID]))]
        G2.add_nodes_from(nodes)
        G3.add_nodes_from(nodes)

        label = []

        edge_label = []
        edge_weight = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            weight = []

            for internal_edge in edge_labels1[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[
                    1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}
                edge_weight.append({(lst_branch[0], lst_branch[1]): internal_edge[3]})
                weight.append((lst_branch[0], lst_branch[1], internal_edge[3]))

            # print data,label

            G2.add_weighted_edges_from(data)
            G3.add_weighted_edges_from(weight)

        if level == 3:
            if parentID != None:
                for node in self.H_NODELIST:
                    if node.id == parentID:
                        PARENT = node
                ZDL_H = []
                for rect in PARENT.stitchList:
                    if rect.nodeId == ID:
                        if rect.cell.x not in ZDL_H:
                            ZDL_H.append(rect.cell.x)
                            ZDL_H.append(rect.EAST.cell.x)
                        if rect.EAST.cell.x not in ZDL_H:
                            ZDL_H.append(rect.EAST.cell.x)
                P = set(ZDL_H)
                ZDL_H = list(P)
                # print "before",ID,label

                # NODES = reversed(NLIST)
                # print NODES
                ZDL_H.sort()
                # print"ID",ID, ZDL_H
                for i, j in self.XLoc.items():
                    if i == ID:

                        for k, v in j.items():
                            for l in range(len(self.ZDL_H[ID])):
                                if l < k and self.ZDL_H[ID][l] in ZDL_H:
                                    start = l
                                else:
                                    break

                            label.append({(start, k): [v, 'fixed', 0, v, None]})
                            edge_label.append({(start, k): v})
        d = defaultdict(list)
        # print label
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        d1 = defaultdict(list)
        # print label
        for i in edge_weight:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d1[k].append(v)
        edge_labels2 = d1
        # print "D",ID,edge_labels1
        #self.drawGraph_h(name, G2, edge_labels1)
        # self.drawGraph_h(name+'w', G3, edge_labels2)
        #print "HC",ID,parentID
        mem = Top_Bottom(ID, parentID, G2, label)  # top to bottom evaluation purpose
        self.Tbeval.append(mem)

        ############## (weifht sum calculation)
        d4 = defaultdict(list)
        for i in edge_weight:
            k, v = list(i.items())[
                0]  # an alternative to the single-iterating inner loop from the previous solution
            d4[k].append(v)
        # print d3
        X1 = {}
        H1 = []
        for i, j in d4.items():
            X1[i] = max(j)
        # print"X", X
        for k, v in X1.items():
            H1.append((k[0], k[1], v))
        GW = nx.MultiDiGraph()
        n = list(G2.nodes())

        GW.add_nodes_from(n)
        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
        GW.add_weighted_edges_from(H1)

        w, h = len(n), len(n);
        B1 = [[0 for x in range(w)] for y in range(h)]
        for i in H1:
            B1[i[0]][i[1]] = i[2]

        # A1 = nx.adjacency_matrix(GW)
        # B1 = A1.toarray()
        # print B
        Location_w = {}
        for i in range(len(n)):
            if n[i] == 0:
                Location_w[n[i]] = 0
            else:
                k = 0
                val = []
                for j in range(len(B1)):
                    if B1[j][i] > k:
                        # k=B[j][i]
                        pred = j
                        # print n[pred],Location_w
                        val.append(Location_w[n[pred]] + B1[j][i])
                # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                # loc2=Location[n[pred]]+k
                Location_w[n[i]] = max(val)
        # print Location
        # Graph_pos_h = []

        dist1 = {}
        for node in Location_w:
            key = node

            dist1.setdefault(key, [])
            dist1[node].append(node)
            dist1[node].append(Location_w[node])
        # Graph_pos_h.append(dist)
        # print Graph_pos_h
        # print"LOC=",Graph_pos_h
        # print "D",Location
        LOC_W = {}
        for i in Location_w.keys():
            # print i,self.ZDL_H[ID][i]
            LOC_W[self.ZDL_H[ID][i]] = Location_w[i]
        #####################################################
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
        # print"X", X
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
                # for j in range(len(B)):
                for j in range(0, i):
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
        # print "D",Location
        LOC_H = {}
        for i in Location.keys():
            # print i,self.ZDL_H[ID][i]
            LOC_H[self.ZDL_H[ID][i]] = Location[i]
        # print"WW", LOC_H

        # if level == 0:
        odH = collections.OrderedDict(sorted(LOC_H.items()))

        self.minLocationH[ID] = odH
        #print "MIN", ID, odH

        if level == 0:
            '''
            # self.drawGraph_h_new(name, G2, edge_labels1, dist)

            # location_file=open(location_file,'wb')
            if parentID != None:

                # location_file = self.name1 + 'Fixed_Loc.csv'
                # if location_file.closed:

                with open(location_file, 'a') as csv_file:
                    writer = csv.writer(csv_file, lineterminator='\n')
                    writer.writerow(["Group", "Input Coordinate", "XNode", "Min Loc", 'xLoc'])

                    for key, value in Location.items():
                        writer.writerow([ID, self.ZDL_H[ID][key], key, value])



            else:
                # location_file = self.name1 + 'Fixed_Loc.csv'
                csvfile = self.name1 + 'Min_X_Location.csv'

                with open(csvfile, 'wb') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["XNode", "Min Loc"])
                    for key, value in Location.items():
                        writer.writerow([key, value])
                with open(location_file, 'a') as csv_file:
                    writer = csv.writer(csv_file, lineterminator='\n')
                    # writer.writerow(["XNode", "Min Loc", 'xLoc'])
                    # writer = csv.writer(csv_file)
                    # writer.writerow(["Group",ID])
                    writer.writerow(["Group", "Input Coordinate", "XNode", "Min Loc", "xLoc"])
                    for key, value in Location.items():
                        writer.writerow([ID, self.ZDL_H[ID][key], key, value])
            '''

            odH = collections.OrderedDict(sorted(LOC_H.items()))

            self.minLocationH[ID] = odH
            #print "MIN", ID, self.minLocationH[ID]

        if parentID != None:
            # N=len(self.ZDL_H[parentID])
            KEYS = list(LOC_H.keys())
            parent_coord = []
            # print"P_ID", parentID
            # if parentID==1:
            for node in self.H_NODELIST:
                # print "ID",node.id
                if node.id == parentID:
                    PARENT = node

            #print"COH", ID, parent_coord, self.ZDL_H[ID]

            for rect in PARENT.stitchList:
                if rect.nodeId == ID:
                    # print rect.cell.x,rect.EAST.cell.x,rect.nodeId
                    # if rect.cell.x not in parent_coord or rect.EAST.cell.x not in parent_coord:
                    if rect.cell.x not in parent_coord:
                        parent_coord.append(rect.cell.x)
                        parent_coord.append(rect.EAST.cell.x)
                    if rect.EAST.cell.x not in parent_coord:
                        parent_coord.append(rect.EAST.cell.x)

            P = set(parent_coord)
            parent_coord = list(P)
            parent_coord.sort()


            SRC = self.ZDL_H[parentID].index(min(KEYS))
            DST = self.ZDL_H[parentID].index(max(KEYS))

            for i in range(len(parent_coord)):
                for j in range(len(parent_coord)):
                    if i < j:
                        source = parent_coord[i]
                        destination = parent_coord[j]

                        s = self.ZDL_H[ID].index(source)
                        t = self.ZDL_H[ID].index(destination)

                        if ID in self.remove_nodes_h:
                            if s in self.remove_nodes_h[ID] or t in self.remove_nodes_h[ID]:
                                continue
                            else:
                                x = self.minLocationH[ID][destination] - self.minLocationH[ID][source]
                                w = 2 * x
                                origin = self.ZDL_H[parentID].index(source)
                                dest = self.ZDL_H[parentID].index(destination)
                                edge1 = (Edge(source=origin, dest=dest, constraint=x, index=0, type=ID, Weight=w,
                                              id=None))  # propagating an edge from child to parent with minimum room for child in the parnet HCG

                                edgelist = self.edgesh_new[parentID]
                                edgelist.append(edge1)
                        else:

                            #print self.minLocationH[ID]
                            x = self.minLocationH[ID][destination] - self.minLocationH[ID][source]

                            w = 2 * x
                            origin = self.ZDL_H[parentID].index(source)
                            dest = self.ZDL_H[parentID].index(destination)
                            # print Count
                            # print"H",parentID, origin,dest,Count
                            # if origin!=SRC and dest!=DST:
                            # print "XX",x
                            edge1 = (Edge(source=origin, dest=dest, constraint=x, index=0, type=ID, Weight=w,
                                          id=None))  # propagating an edge from child to parent with minimum room for child in the parnet HCG

                            edgelist = self.edgesh_new[parentID]
                            edgelist.append(edge1)

                # if propagated edge's destination vertex is in removable vertex list, then that edge should by pass that removable node and pass to it's successors.
                if parentID in self.remove_nodes_h.keys():

                    if dest in self.remove_nodes_h[parentID]:
                        for edge in self.edgesh_new[parentID]:
                            if edge.comp_type == "Device" and edge.source == origin:
                                v0 = edge.constraint
                            if edge.type == 'bypassed' and edge.source == origin:
                                dest1 = edge.dest
                                v = edge.constraint
                                value = x + (v - v0)  # retreiving constraint value from removable vertex to new target vertex by (v-v0)
                                edge = (Edge(source=origin, dest=dest1, constraint=value, index=0, type=ID, Weight=2 * value,
                                     id=None))  # creating new edge bypassing removable node
                                if edge not in edgelist:
                                    edgelist.append(edge)
                self.edgesh_new[parentID] = edgelist

            '''
            source = self.ZDL_H[parentID].index(min(KEYS))
            dest = self.ZDL_H[parentID].index(max(KEYS))
            # print self.edgesh_new[parentID]
            W = LOC_W[dest] - LOC_W[source]
            #if Count != 0:
            edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=0, type=ID, Weight=W,id=None))

            #edge = (Edge(source=source, dest=dest, constraint=Location[n[-1]], index=1, type=ID, id=None,Weight=Count))
            # print edge.source,edge.dest,edge.constraint
            edgelist = self.edgesh_new[parentID]
            edgelist.append(edge)
            self.edgesh_new[parentID] = edgelist
            '''

    def VcgEval(self, level,Random,seed, N):

        # for i in reversed(Tbelement):
        if level == 1:
            for element in reversed(self.TbevalV):

                if element.parentID == None:

                    G2 = element.graph
                    # label=i.labels
                    label3 = copy.deepcopy(element.labels)
                    # print "l3",len(label4),label4
                    d3 = defaultdict(list)
                    for i in label3:
                        (k1), v = list(i.items())[
                            0]  # an alternative to the single-iterating inner loop from the previous solution
                        d3[(k1)].append(v)
                    # print "D3", d3
                    edgelabels = {}
                    for (k), v in d3.items():
                        values = []
                        for j in range(len(v)):
                            values.append(v[j][0])
                        value = max(values)
                        for j in range(len(v)):
                            if v[j][0] == value:
                                edgelabels[(k)] = v[j]
                    # print"VED", edgelabels
                    H_all=[]
                    s = seed
                    for i in range(N):
                        seed = s + i * 1000
                        count = 0
                        V = []
                        for (k), v in edgelabels.items():
                            count += 1

                            if v[2] == 2 and v[1] == '0':  # ledge width
                                val = v[0]
                            elif v[2] == 1 and v[1] == '0':  # white spacing
                                val = v[0]
                            else:
                                if (N < 150):
                                    SD = N * 3000  # standard deviation for randomization
                                else:
                                    SD = 10000  # 7000
                                random.seed(seed + count * 1000)
                                val = int(min(1000 * v[0], max(v[0], random.gauss(v[0], SD))))
                            # print (k),v[0],val
                            V.append((k[0], k[1], val))
                        H_all.append(V)



                    G_all = []
                    for i in range(len(H_all)):
                        G = nx.MultiDiGraph()
                        n = list(G2.nodes())
                        G.add_nodes_from(n)
                        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                        G.add_weighted_edges_from(H_all[i])
                        G_all.append(G)

                    loct = []
                    for i in range(len(G_all)):
                        new_Ylocation = []
                        A = nx.adjacency_matrix(G_all[i])
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
                        loct.append(loc_i)
                        # print"LOCT",locta
                        # print new_Xlocation
                        self.NEWYLOCATION.append(new_Ylocation)

                    n = list(G2.nodes())
                    Location = {}
                    key = element.ID
                    Location.setdefault(key, [])

                    for i in range(len(self.NEWYLOCATION)):
                        loct = {}
                        for j in range(len(self.ZDL_V[element.ID])):
                            loct[self.ZDL_V[element.ID][j]] = self.NEWYLOCATION[i][j]
                        Location[element.ID].append(loct)
                        # print Location
                    self.LocationV = Location
                    #print"VCG",N,len(self.LocationV.values()),self.LocationV

                        #
                else:
                    # continue
                    if element.parentID in self.LocationV.keys():

                        # if element.parentID==1:
                        for node in self.V_NODELIST:
                            if node.id == element.parentID:
                                PARENT = node

                        ZDL_V = []
                        for rect in PARENT.stitchList:
                            if rect.nodeId == element.ID:
                                if rect.cell.y not in ZDL_V:
                                    ZDL_V.append(rect.cell.y)
                                    ZDL_V.append(rect.NORTH.cell.y)
                                if rect.NORTH.cell.y not in ZDL_V:
                                    ZDL_V.append(rect.NORTH.cell.y)


                        P = set(ZDL_V)
                        ZDL_V = list(P)

                        V = self.LocationV[element.parentID]

                        # print V
                        loct = []
                        count=0
                        for location in V:

                            seed = s + count * 1000
                            count+=1
                            self.Loc_Y = {}
                            for coordinate in self.ZDL_V[element.ID]:
                                # if element.parentID == 1:
                                for k, v in location.items():
                                    if k == coordinate and k in ZDL_V:
                                        self.Loc_Y[self.ZDL_V[element.ID].index(coordinate)] = v
                                        # print "v",self.Loc_X
                                    else:
                                        continue

                            d3 = defaultdict(list)
                            WV = defaultdict(list)
                            d4 = defaultdict(list)
                            for i in element.labels:
                                k, v = list(i.items())[0]
                                # print v[0]
                                d3[k].append(v[0])
                                WV[k].append(v[3])
                                if v[4] == "Device":
                                    d4[k].append(v[0])
                                '''
                                if v[3] == None:
                                    W[k].append(1)
                                else:
                                    W[k].append(v[3])
                                '''
                            # print "D3", d3, W
                            Y = {}
                            V = []
                            Fix = {}
                            Weights_V = {}
                            for i, j in d3.items():
                                Y[i] = max(j)
                            for i, j in d4.items():
                                Fix[i] = max(j)
                            # print"X", X
                            for i, j in WV.items():
                                Weights_V[i] = max(j)
                            # print Y,Weights
                            for k, v in Y.items():
                                V.append((k[0], k[1], v))
                            # print "H", Fix
                            GV = nx.MultiDiGraph()
                            nV = list(element.graph.nodes())
                            GV.add_nodes_from(n)
                            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                            GV.add_weighted_edges_from(V)
                            self.FUNCTION_V(GV, element.ID, Random,sid=seed)
                            # print"FINX",self.Loc_X
                            loct.append(self.Loc_Y)
                        # print loct
                        yloc = []
                        for k in range(len(loct)):
                            loc = {}
                            for k, v in loct[k].items():
                                loc[self.ZDL_V[element.ID][k]] = v
                            yloc.append(loc)
                        self.LocationV[element.ID] = yloc
                    #print "VLOC",self.LocationV

        elif level == 2 or level == 3:
            for element in reversed(self.TbevalV):
                # print element.ID,element.parentID

                if element.parentID == None:
                    loct = []
                    s = seed
                    for i in range(N):
                        self.seed_v.append(s + i * 1000)
                    for i in range(N):

                        d3 = defaultdict(list)
                        d4 = defaultdict(list)
                        WV = defaultdict(list)
                        for i in element.labels:
                            k, v = list(i.items())[0]
                            # print v[0]
                            d3[k].append(v[0])
                            WV[k].append(v[3])
                            '''
                            if v[3] == None:
                                W[k].append(1)
                            else:
                                W[k].append(v[3])
                            '''
                        # print "D3", d3, W
                        Y = {}
                        V = []
                        Weights_V = {}
                        for i, j in d3.items():
                            Y[i] = max(j)
                        # print"X", X
                        for i, j in WV.items():
                            Weights_V[i] = max(j)
                        # print Y,Weights
                        for k, v in Y.items():
                            V.append((k[0], k[1], v))
                        # print "H", Fix
                        GV = nx.MultiDiGraph()
                        nV = list(element.graph.nodes())
                        GV.add_nodes_from(nV)
                        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                        GV.add_weighted_edges_from(V)
                        if level == 2:
                            self.Loc_Y = {}
                            for k, v in self.YLoc.items():
                                if k in nV:
                                    self.Loc_Y[k] = v
                            # print "Y",self.Loc_Y
                        elif level == 3:
                            self.Loc_Y = {}

                            for i, j in self.YLoc.items():
                                # print j
                                if i == 1:
                                    for k, v in j.items():
                                        self.Loc_Y[k] = v
                        self.FUNCTION_V(GV, element.ID, Random,sid=i)
                        # print"FINX",self.Loc_V
                        loct.append(self.Loc_Y)

                    self.NEWYLOCATION = loct

                    n = list(GV.nodes())
                    Location = {}
                    key = element.ID
                    Location.setdefault(key, [])

                    for i in range(len(self.NEWYLOCATION)):
                        loct = {}
                        for j in range(len(self.ZDL_V[element.ID])):
                            loct[self.ZDL_V[element.ID][j]] = self.NEWYLOCATION[i][j]
                        Location[element.ID].append(loct)
                        # print Location
                    self.LocationV = Location
                    # print "LV",self.LocationV
                    #
                else:
                    # continue

                    if element.parentID in self.LocationV.keys():
                        loct = []
                        for node in self.V_NODELIST:
                            if node.id == element.parentID:
                                PARENT = node
                        # if element.parentID==1:
                        ZDL_V = []
                        for rect in PARENT.stitchList:
                            if rect.nodeId == element.ID:
                                if rect.cell.y not in ZDL_V:
                                    ZDL_V.append(rect.cell.y)
                                    ZDL_V.append(rect.NORTH.cell.y)
                                if rect.NORTH.cell.y not in ZDL_V:
                                    ZDL_V.append(rect.NORTH.cell.y)


                        # print"After", ZDL_V, element.ID
                        P = set(ZDL_V)
                        ZDL_V = list(P)
                        ZDL_V.sort()

                        V = self.LocationV[element.parentID]

                        # print V

                        for location in V:
                            self.Loc_Y = {}

                            for coordinate in self.ZDL_V[element.ID]:
                                # if element.parentID == 1:

                                for k, v in location.items():
                                    if k == coordinate and k in ZDL_V:
                                        # if self.ZDL_V[element.ID].index(coordinate) not in self.Loc_Y:
                                        # if self.ZDL_V[element.ID].index(coordinate) not in NLIST:
                                        self.Loc_Y[self.ZDL_V[element.ID].index(coordinate)] = v

                                    else:
                                        continue

                                '''
                                else:
                                    for k, v in location.items():
                                        if k==coordinate:
                                            #if self.ZDL_V[element.ID].index(coordinate) not in NLIST:
                                            self.Loc_Y[self.ZDL_V[element.ID].index(coordinate)]=v
                                            #print "v",self.Loc_X
                                        else:
                                            continue
                                '''

                            # print "Y",element.ID,self.Loc_Y
                            # print"LOC", self.Loc_Y
                            d3 = defaultdict(list)
                            d4 = defaultdict(list)
                            WV = defaultdict(list)
                            for i in element.labels:
                                k, v = list(i.items())[0]
                                # print v[0]
                                d3[k].append(v[0])
                                WV[k].append(v[3])
                                if v[4] == "Device":
                                    d4[k].append(v[0])

                            NLIST = []
                            for k, v in self.Loc_Y.items():
                                NLIST.append(k)
                            # NODES=reversed(NLIST)
                            # print NODES
                            if level == 3:
                                for i, j in self.YLoc.items():
                                    if i == element.ID:
                                        for k, v in j.items():
                                            # self.Loc_Y[k]=self.Loc_Y[0]+v

                                            for node in NLIST[::-1]:

                                                if node >= k:
                                                    continue
                                                else:

                                                    p = self.Loc_Y[node]
                                                    # print p+v
                                                    self.Loc_Y[k] = p + v
                                                    break

                            # print "Y2", element.ID, self.Loc_Y

                            # print "D3", d3
                            Y = {}
                            V = []
                            Weights_V = {}
                            Fix = {}


                            for i, j in d3.items():
                                Y[i] = max(j)
                                if i[0] in self.Loc_Y.keys() and i[1] in self.Loc_Y.keys():
                                    # print self.Loc_Y[i[0]],self.Loc_Y[i[1]]
                                    if (self.Loc_Y[i[1]] - self.Loc_Y[i[0]]) < max(j):
                                        print "ERROR", i, max(j), self.Loc_Y[i[1]] - self.Loc_Y[i[0]]

                                        # distance=max(j)-abs((self.Loc_X[i[1]]-self.Loc_X[i[0]]))
                                        # self.Loc_X[i[1]]+=distance

                                    else:
                                        continue

                            # print "v3", self.Loc_Y
                            for i, j in d4.items():
                                Fix[i] = max(j)
                            for i, j in WV.items():
                                Weights_V[i] = max(j)
                            # print Y,Weights_V

                            for k, v in Y.items():
                                V.append((k[0], k[1], v))
                            # print "H", Fix
                            GV = nx.MultiDiGraph()
                            nV = list(element.graph.nodes())
                            GV.add_nodes_from(nV)
                            # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
                            GV.add_weighted_edges_from(V)
                            self.FUNCTION_V(GV, element.ID, Random,sid=seed)
                            # print"FINX",self.Loc_X
                            loct.append(self.Loc_Y)
                        # print"L", loct
                        yloc = []
                        for k in range(len(loct)):
                            loc = {}
                            for k, v in loct[k].items():
                                loc[self.ZDL_V[element.ID][k]] = v
                            yloc.append(loc)
                        self.LocationV[element.ID] = yloc
                    # print "VLOC",self.LocationV


    def cgToGraph_v(self,ID, edgev, parentID, level):

        '''
                :param ID: Node ID
                :param edgev: vertical edges for that node's constraint graph
                :param parentID: node id of it's parent
                :param level: mode of operation
                :param N: number of layouts to be generated
                :return: constraint graph and solution for different modes
                '''


        GV = nx.MultiDiGraph()
        GV2 = nx.MultiDiGraph()
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
        GV2.add_nodes_from(nodes)
        label = []

        edge_label = []
        edge_weight = []
        for branch in edge_labels1:
            lst_branch = list(branch)
            data = []
            weight = []

            for internal_edge in edge_labels1[branch]:
                # print lst_branch[0], lst_branch[1]
                # print internal_edge
                # if (lst_branch[0], lst_branch[1], internal_edge) not in data:
                data.append((lst_branch[0], lst_branch[1], internal_edge))
                label.append({(lst_branch[0], lst_branch[
                    1]): internal_edge})  #####{(source,dest):[weight,type,id,East cell id,West cell id]}
                edge_label.append({(lst_branch[0], lst_branch[1]): internal_edge[0]})  ### {(source,dest):weight}
                edge_weight.append({(lst_branch[0], lst_branch[1]): internal_edge[3]})
                weight.append((lst_branch[0], lst_branch[1], internal_edge[3]))
                # print data,label

            GV.add_weighted_edges_from(data)
            GV2.add_weighted_edges_from(weight)
        if level == 3:
            # print "before",ID,label
            if parentID != None:
                for node in self.V_NODELIST:
                    if node.id == parentID:
                        PARENT = node
                ZDL_V = []
                for rect in PARENT.stitchList:
                    if rect.nodeId == ID:
                        if rect.cell.y not in ZDL_V:
                            ZDL_V.append(rect.cell.y)
                            ZDL_V.append(rect.NORTH.cell.y)
                        if rect.NORTH.cell.y not in ZDL_V:
                            ZDL_V.append(rect.NORTH.cell.y)
                P = set(ZDL_V)
                ZDL_V = list(P)
                # print "before",ID,label
                # NODES = reversed(NLIST)
                # print NODES
                ZDL_V.sort()
                # print ZDL_H
                for i, j in self.YLoc.items():
                    if i == ID:

                        for k, v in j.items():
                            for l in range(len(self.ZDL_V[ID])):
                                if l < k and self.ZDL_V[ID][l] in ZDL_V:
                                    start = l
                                else:
                                    break

                            label.append({(start, k): [v, 'fixed', 0, v, None]})
                            edge_label.append({(start, k): v})
                # print "after", label

        d = defaultdict(list)
        # print label
        for i in edge_label:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d[k].append(v)
        edge_labels1 = d
        # print "d",label
        #self.drawGraph_v(name, GV, edge_labels1)
        d1 = defaultdict(list)
        # print label
        for i in edge_weight:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d1[k].append(v)
        edge_labels2 = d1
        # self.drawGraph_v(name + 'w', GV2, edge_labels2)
        #print "VC",ID,parentID
        mem = Top_Bottom(ID, parentID, GV, label)  # top to bottom evaluation purpose
        self.TbevalV.append(mem)

        # else:
        d4 = defaultdict(list)
        for i in edge_weight:
            k, v = list(i.items())[0]  # an alternative to the single-iterating inner loop from the previous solution
            d4[k].append(v)

        X1 = {}
        H1 = []
        for i, j in d4.items():
            X1[i] = max(j)

        for k, v in X1.items():
            H1.append((k[0], k[1], v))

        GW = nx.MultiDiGraph()
        n = list(GV.nodes())

        GW.add_nodes_from(n)
        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
        GW.add_weighted_edges_from(H1)
        w, h = len(n), len(n);
        B1 = [[0 for x in range(w)] for y in range(h)]
        for i in H1:
            B1[i[0]][i[1]] = i[2]
        # A1 = nx.adjacency_matrix(GW)
        # B1 = A1.toarray()
        # print B
        Location_w = {}
        for i in range(len(n)):
            if n[i] == 0:
                Location_w[n[i]] = 0
            else:
                k = 0
                val = []
                # for j in range(len(B1)):
                for j in range(0, i):
                    if B1[j][i] > k:
                        # k=B[j][i]
                        pred = j
                        val.append(Location_w[n[pred]] + B1[j][i])
                # loc1=Location[n[i-1]]+X[(n[i-1],n[i])]
                # loc2=Location[n[pred]]+k
                Location_w[n[i]] = max(val)
        # print Location
        # Graph_pos_h = []

        dist1 = {}
        for node in Location_w:
            key = node

            dist1.setdefault(key, [])
            dist1[node].append(node)
            dist1[node].append(Location_w[node])
        # Graph_pos_h.append(dist)
        # print Graph_pos_h
        # print"LOC=",Graph_pos_h
        # print "D",Location
        LOC_W = {}
        for i in Location_w.keys():
            # print i,self.ZDL_H[ID][i]
            LOC_W[self.ZDL_V[ID][i]] = Location_w[i]
        #####################################################

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
        # print"Y",ID, Y
        for k, v in Y.items():
            V.append((k[0], k[1], v))
        G = nx.MultiDiGraph()
        n = list(GV.nodes())
        G.add_nodes_from(n)
        # G.add_weighted_edges_from([(0,1,2),(1,2,3),(2,3,4),(3,4,4),(4,5,3),(5,6,2),(1,4,15),(2,5,16),(1,5,20)])
        G.add_weighted_edges_from(V)
        A = nx.adjacency_matrix(G)
        B = A.toarray()
        # print"ID",ID, B
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
        LOC_V = {}
        for i in Location.keys():
            # print i, self.ZDL_V[ID][i]
            LOC_V[self.ZDL_V[ID][i]] = Location[i]
        # Graph_pos_h.append(dist)
        # print Graph_pos_h
        # print"LOC=",Graph_pos_h

        # if level == 0:  # changed for mode-2 evaluation
        odV = collections.OrderedDict(sorted(LOC_V.items()))

        self.minLocationV[ID] = odV
        # print"ID",ID,self.minLocationV[ID]

        if level == 0:
            # self.drawGraph_v_new(name, GV, edge_labels1, dist)


            odV = collections.OrderedDict(sorted(LOC_V.items()))
            self.minLocationV[ID] = odV
            # print"ID", ID, self.minLocationV[ID]

        # print ID,self.minLocationV[ID]

        if parentID != None:
            # N=len(self.ZDL_H[parentID])
            KEYS = list(LOC_V.keys())
            # print "KE", KEYS
            parent_coord = []

            # if parentID==1:
            for node in self.V_NODELIST:
                if node.id == parentID:
                    PARENT = node

            # for coord in parent_coord:

            for rect in PARENT.stitchList:
                if rect.nodeId == ID:
                    if rect.cell.y not in parent_coord:
                        parent_coord.append(rect.cell.y)
                        parent_coord.append(rect.NORTH.cell.y)
                    if rect.NORTH.cell.y not in parent_coord:
                        parent_coord.append(rect.NORTH.cell.y)

            # print"CO", parent_coord
            # parent_coord = []
            P = set(parent_coord)

            # SRC = self.ZDL_V[parentID].index(min(KEYS))
            # DST = self.ZDL_V[parentID].index(max(KEYS))
            parent_coord = list(P)
            parent_coord.sort()


            for i in range(len(parent_coord)):
                for j in range(len(parent_coord)):
                    if i < j:
                        source = parent_coord[i]
                        destination = parent_coord[j]

                        s = self.ZDL_V[ID].index(source)
                        t = self.ZDL_V[ID].index(destination)

                        #print"S", ID, s, source
                        #print t, destination

                        # y = self.longest_distance(B, s, t)
                        if ID in self.remove_nodes_v:
                            if s in self.remove_nodes_v[ID] or t in self.remove_nodes_v[ID]:
                                continue
                            else:
                                y = self.minLocationV[ID][destination] - self.minLocationV[ID][source]

                                w = 2 * y
                                origin = self.ZDL_V[parentID].index(source)
                                dest = self.ZDL_V[parentID].index(destination)
                                # if origin!=SRC and dest!=DST:
                                edgelist = self.edgesv_new[parentID]
                                edge1 = (Edge(source=origin, dest=dest, constraint=y, index=4, type=ID, Weight=w,
                                              id=None))  # propagating an edge from child to parent with minimum room for child in the parnet HCG
                                edgelist.append(edge1)
                        else:
                            y = self.minLocationV[ID][destination] - self.minLocationV[ID][source]

                            w = 2 * y

                            origin = self.ZDL_V[parentID].index(source)
                            dest = self.ZDL_V[parentID].index(destination)
                            # if origin!=SRC and dest!=DST:
                            edgelist = self.edgesv_new[parentID]
                            edge1 = (Edge(source=origin, dest=dest, constraint=y, index=4, type=ID, Weight=w,
                                          id=None))  # propagating an edge from child to parent with minimum room for child in the parnet HCG
                            edgelist.append(edge1)

                # propagating minimum room to new target if destination is in removable vertex list.
                if parentID in self.remove_nodes_v.keys():
                    if dest in self.remove_nodes_v[parentID]:
                        for edge in self.edgesv_new[parentID]:
                            if edge.comp_type == "Device" and edge.source == origin:
                                v0 = edge.constraint
                        for edge in self.edgesv_new[parentID]:

                            if edge.type == 'bypassed' and edge.source == origin:

                                dest1 = edge.dest
                                v = edge.constraint
                                value = y + (v - v0)
                                edge = (
                                Edge(source=origin, dest=dest1, constraint=value, index=4, type=ID, Weight=2 * value,
                                     id=None))
                                if edge not in edgelist:
                                    edgelist.append(edge)

                self.edgesv_new[parentID] = edgelist


    # Applies algorithms for evaluating mode-2 and mode-3 solutions
    def FUNCTION(self, G,ID,Random,sid):
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
        '''
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
        '''
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
        if len(Connected_List) > 0:
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
                if ID in self.remove_nodes_h.keys():
                    for i in nodes:
                        if i in self.remove_nodes_h[ID]:
                            j = i
                            for k in nodes:
                                if B[k][j] != 0 and k in self.Loc_X:
                                    self.Loc_X[j] = self.Loc_X[k] + B[k][j]
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
                    self.FUNCTION(G,ID,Random,sid)

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
                if ID in self.remove_nodes_h.keys():
                    for i in n:
                        if i in self.remove_nodes_h[ID]:
                            j=i
                            for k in n:
                                if B[k][j]!=0 and k in self.Loc_X:
                                    self.Loc_X[j]=self.Loc_X[k]+B[k][j]
            Fixed_Node = self.Loc_X.keys()
            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)

            if len(G.edges()) == 0:

                return

            else:
                self.FUNCTION(G,ID, Random,sid)


    # randomize uniformly edge weights within fixed minimum and maximum locations
    def randomvaluegenerator(self, Range, value,Random,sid):
        #print "R",Random,sid


        if Random!=None:
            Range = Range / 1000
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
            #D_V_Newval = [0]

            V = copy.deepcopy(value)
            # print "value", value
            W = [i for i in V]
            # print "R",Range

            # print "R_a",Range
            Total = sum(W)
            Prob = []
            Range = Range / 1000
            for i in W:
                Prob.append(i / float(Total))
            # print W,Prob
            # D_V_Newval = [i*Range for i in Prob]
            random.seed(sid)
            D_V_Newval = list(np.random.multinomial(Range, Prob))


            for i in range(len(V)):
                x = V[i] + (D_V_Newval[i])*1000
                variable.append(x)
            return variable
            '''
            variable = []
            D_V_Newval = [0]
            V=copy.deepcopy(value)

            while (len(value) > 1):
                i = 0
                n = len(value)
                v = Range - sum(D_V_Newval)
                if ((2 * v) / n) > 0:

                    #random.seed(self.seed_h[sid])
                    random.seed(sid)
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
                random.seed(sid)
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
    def FUNCTION_V(self, G,ID,Random,sid):
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
        '''
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
                        self.FUNCTION_V(G,ID,Random,sid)
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
        '''

        if len(Connected_List) > 0:
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
                # print Weights
                self.Location_finding_V(B, start, end,ID,Random, SOURCE, TARGET, flag=True,sid=sid)
                if ID in self.remove_nodes_v.keys():
                    for i in nodes:
                        if i in self.remove_nodes_v[ID]:
                            j = i
                            for k in nodes:
                                if B[k][j] != 0 and k in self.Loc_Y:
                                    self.Loc_Y[j] = self.Loc_Y[k] + B[k][j]
                Fixed_Node = self.Loc_Y.keys()
                for i in Fixed_Node:
                    for j in Fixed_Node:
                        if G.has_edge(i, j):
                            G.remove_edge(i, j)
                if len(G.edges()) == 0:
                    return
                else:
                    self.FUNCTION_V(G,ID, Random, sid)
        else:
            H = []
            for i in range(len(Node_List)):
                H.append(G.subgraph(Node_List[i]))
            for graph in H:
                n = list(graph.nodes())
                n.sort()
                start = n[0]
                end = n[-1]
                self.Location_finding_V(B, start, end,ID,Random, SOURCE=None, TARGET=None, flag=False,sid=sid)
                if ID in self.remove_nodes_v.keys():
                    for i in n:
                        if i in self.remove_nodes_v[ID]:
                            j=i
                            for k in n:
                                if B[k][j]!=0 and k in self.Loc_Y:
                                    self.Loc_Y[j]=self.Loc_Y[k]+B[k][j]

            Fixed_Node = self.Loc_Y.keys()

            for i in Fixed_Node:
                for j in Fixed_Node:
                    if G.has_edge(i, j):
                        G.remove_edge(i, j)

            if len(G.edges()) == 0:

                return
            else:
                self.FUNCTION_V(G,ID,Random,sid)


    def randomvaluegenerator_V(self, Range, value,Random,sid):
        """

        :param Range: Randomization room excluding minimum constraint values
        :param value: list of minimum constraint values associated with the room
        :return: list of randomized value corresponding to each minimum constraint value
        """



        if Random!=None:
            Range = Range / 1000
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
            # D_V_Newval = [0]

            V = copy.deepcopy(value)
            # print "value", value
            W = [i for i in V]
            # print "R",Range

            # print "R_a",Range
            Total = sum(W)
            Prob = []

            for i in W:
                Prob.append(i / float(Total))
            # print W,Prob
            # D_V_Newval = [i*Range for i in Prob]
            Range = Range / 1000
            random.seed(sid)
            D_V_Newval = list(np.random.multinomial(Range, Prob))


            for i in range(len(V)):
                x = V[i] + (D_V_Newval[i])*1000
                variable.append(x)







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
                    #random.seed(self.seed_v[sid])
                    random.seed(sid)

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
                random.seed(sid)
                self.Loc_Y[i] = randrange(v1, v2)
            else:
                self.Loc_Y[i] = max(v1, v2)
            SOURCE.append(i)
            TARGET.append(i)

    def Location_finding_V(self, B, start, end,ID,Random, SOURCE, TARGET, flag,sid):
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
    def __init__(self, source, dest, constraint, index, type, id,Weight=None,comp_type=None, East=None, West=None, North=None, South=None,northWest=None,
                 westNorth=None, southEast=None, eastSouth=None):
        self.source = source
        self.dest = dest
        self.constraint = constraint
        self.index = index
        self.type = type
        self.id = id
        self.Weight = Weight
        self.comp_type = comp_type
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
        self.edgeDict = {(self.source, self.dest): [self.constraint, self.type, self.index, self.Weight, self.comp_type]}
        # self.edgeDict = {(self.source, self.dest): self.constraint.constraintval}

    def getEdgeDict(self):
        return self.edgeDict

    def getEdgeWeight(self, source, dest):
        return self.getEdgeDict()[(self.source, self.dest)]

    def printEdge(self):
        print "s: ", self.source, "d: ", self.dest, "con = ", self.constraint.printCon()

class Top_Bottom():
    def __init__(self, ID, parentID, graph, labels):
        self.ID = ID
        self.parentID = parentID
        self.graph = graph
        self.labels = labels

    def getID(self):
        return self.ID

    def getgraph(self):
        return self.graph

    def getlabels(self):
        return self.labels