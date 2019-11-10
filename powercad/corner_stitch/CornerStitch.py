#!/usr/bin/python
'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba

Updated from Aug,2017
@ author: Imam Al Razi(ialrazi)
'''
import os
import matplotlib
import matplotlib.patches as patches
from abc import ABCMeta
from constraintGraph_Dev import *
import constraint as ct
import collections
import networkx as nx
from powercad.general.data_struct.util import *
from API_PS import draw_rect_list_cs

global VID,HID,Schar,EChar,Cchar,Htree,Vtree
Schar='+'
Cchar='%'
EChar='-'
VID=0
HID=0

class Cell:
    """
    This is the basis for a cell, with only internal information being stored. information pertaining to the 
    structure of a cornerStitch or the relative position of a cell is stored in a cornerStitch obj.
    """
    def __init__(self, x, y, type,id=None):
        self.x = x
        self.y = y
        self.type = type
        self.id = id


    def printCell(self, printX = False, printY = False, printType = False,printID=False):
        if printX: print "x = ", self.x
        if printY: print "y = ", self.y
        if printType: print "type = ", self.type
        if printID: print "id=",self.id
        return

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getType(self):
        return self.type

    def getId(self):
        return self.id

class Tile:
    """
    Abstract class of cells, there eventually will be multiple
    implementations of cells with different physical properties
    We're using the bare minimum four pointer configuration 
    presented in the paper. As per the paper, only the left and bottom sides
    are explicitly defined, everything else being implicitly defined by neighbors
    """

    def __init__(self, north, east, south, west, hint, cell,name=None,nodeId=None,voltage=None,current=None):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.HINT = hint #this is the pointer to the hint tile of where to start looking for location
        self.cell = cell # to get x,y,type information
        self.name=name # to give a unique id of tile
        self.nodeId=nodeId # in hierarchical tree which node it belongs to
        self.voltage=voltage # to keep voltage information
        self.current=current # to keep current value
        self.bw = []  # list of bondwire objects which have source in the tile
        self.parent_name=None # name of the parent component
        self.rotation_index=0 # default is no rotation



    def printNeighbors(self, printX = False, printY = False, printType = False): #debugging function to print tile neighbors
        if self.NORTH is not None: print "N", self.NORTH.cell.printCell(printX, printY, printType)
        if self.EAST is not None: print "E", self.EAST.cell.printCell(printX, printY, printType)
        if self.SOUTH is not None: print "S", self.SOUTH.cell.printCell(printX, printY, printType)
        if self.WEST is not None: print "W", self.WEST.cell.printCell(printX, printY, printType)

    def printTile(self): #debugging function to print tile properties
        self.cell.printCell(True,True,True)
        print "WIDTH=",self.getWidth()
        print "Height=",self.getHeight()
        print "NORTH=",self.NORTH.cell.printCell(True,True,True)
        print "EAST=", self.EAST.cell.printCell(True, True, True)
        print "WEST=", self.WEST.cell.printCell(True, True, True)
        print "SOUTH=", self.SOUTH.cell.printCell(True, True, True)
        print "node_id=",self.nodeId

    def getHeight(self): #returns the height
        return (self.NORTH.cell.y - self.cell.y)

    def getWidth(self):#returns the width
            return (self.EAST.cell.x - self.cell.x)

    def northWest(self, center): # returns left-top neighbor of a tile
        cc = center.WEST
        if cc.cell.type != None:
            while cc.cell.y + cc.getHeight() < center.cell.y + center.getHeight():
                cc = cc.NORTH
        return cc

    def westNorth(self, center):# returns top-left neighbor of a tile
        cc = center.NORTH
        if cc.cell.type != None:
            while cc.cell.x > center.cell.x :#+ center.getWidth():
                cc = cc.WEST
        return cc

    def southEast(self, center):# returns right-bottom neighbor of a tile
        cc = center.EAST
        if cc.cell.type != None:
            while cc.cell.y > center.cell.y:
                cc = cc.SOUTH
        return cc

    def eastSouth(self, center):# returns bottom-right neighbor of a tile
        cc = center.SOUTH
        if cc.cell.type!=None:
            while cc.cell.x + cc.getWidth() < center.cell.x + center.getWidth():
                cc = cc.EAST
        return cc

    def getNorth(self): # returns top-right neighbor of the tile
        return self.NORTH

    def getEast(self):# returns right-top neighbor of a tile
        return self.EAST

    def getSouth(self):# returns bottom-left neighbor of a tile
        return self.SOUTH

    def getWest(self):# returns left-bottom neighbor of a tile
        return self.WEST

    def getNodeId(self):# returns nodeID of the tile
        return self.nodeId

    def getParentNode(self,nodeList): #Finding parent node of a tile from node list
        for group in nodeList:
            if group.id==self.nodeId:
                return group
            else:
                print"node not found"
                return


    #returns a list of neighbors
    def findNeighbors(self):
        """
        find all cells, empty or not, touching the starting tile
        """
        neighbors = []

        cc = self.EAST  #Walk downwards along the topright (NE) corner

        while (cc.SOUTH!=None and cc.cell.y + cc.getHeight() > self.cell.y):
            neighbors.append(cc)
            if cc.SOUTH is not None:
                cc = cc.SOUTH
            else:
                break

        cc = self.SOUTH #Walk eastwards along the bottom-Left (SW) corner
        while (cc.EAST!=None and cc.cell.x  < self.cell.x + self.getWidth()):
            neighbors.append(cc)
            if cc.EAST is not None:
                cc = cc.EAST
            else:
                break

        cc = self.WEST #Walk northwards along the bottomLeft (SW) corner
        while (cc.NORTH!=None and cc.cell.y < self.cell.y + self.getHeight()):
            neighbors.append(cc)
            if cc.NORTH is not None:
                cc = cc.NORTH
            else:
                break

        cc = self.NORTH #Walk westwards along the topright (NE) corner
        while (cc.WEST!=None and cc.cell.x + cc.getWidth() > self.cell.x):
            neighbors.append(cc)
            if cc.WEST is not None:
                cc = cc.WEST
            else:
                break

        return neighbors

class BondWire():
    def __init__(self,type=None,name=None,num_of_bw=None,src_coordinate=None,dest_coordinate=None,src_nodeID=None,dest_nodeID=None,direction=None):
        """
        :param type:Connection type (0: flexible, 1: fixed(either horizontal or vertical), 2: fixed in both direction(3-D via))
        :param name:Name of bondwire(id)
        :param num_of_bw:Number of bondwires in a group
        :param src_coordinate:coordinate of source point for cneter bondwire (if there are multiple bondwires)
        :param dest_coordinate:coordinate of destination point for cneter bondwire (if there are multiple bondwires)
        :param src_nodeID: src_tile's node ID
        :param dest_node_ID: dest_tile's nodeID
        :param direction: direction of bondwire (-1:horizontal,1:vertical)
        """
        self.type=type
        self.name=name
        self.num_of_bw=num_of_bw
        self.src_coordinate=src_coordinate
        self.dest_coordinate=dest_coordinate
        self.src_nodeID=src_nodeID
        self.dest_nodeID=dest_nodeID
        self.src_tile=None
        self.dest_tile=None
        self.direction=direction



    def printBondWire(self):
        print"Type",self.type
        print "Name",self.name
        print "Num",self.num_of_bw
        print "src_coordinate",self.src_coordinate
        print"dest_coordinate",self.dest_coordinate
        print "src_tile", self.src_tile.nodeId,self.src_tile.cell.x,self.src_tile.cell.y,self.src_tile.cell.type
        print "dest_tile", self.dest_tile.nodeId, self.dest_tile.cell.x, self.dest_tile.cell.y, self.dest_tile.cell.type
        print "src_nodeID", self.src_nodeID
        print "dest_nodeID", self.dest_nodeID
        print "src_tile_ID", self.src_tile.nodeId
        print "dest_tile_ID", self.dest_tile.nodeId
        if self.direction==-1:
            print "direction: Horizontal"
        if self.direction==1:
            print "direction: Vertical"
        if self.direction==0:
            print "direction: Diagonal"

########################################################################################################################
class CornerStitchAlgorithms(object):
    """
    A cornerStitch is a collection of tiles all existing on the same plane. I'm not sure how we're going to handle
    cornerStitchs connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of tiles or anything involving coordinates being passed in instead of a tile
    """
    __metaclass__ = ABCMeta

    def __init__(self, stitchList, level, max_x=None, max_y=None,boundaries=None):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.level=level
        if self.level == 0:
            self.northBoundary = Tile(None, None, None, None, None, Cell(0, max_y, "EMPTY"))
            self.eastBoundary = Tile(None, None, None, None, None, Cell(max_x, 0, "EMPTY"))
            self.southBoundary = Tile(None, None, None, None, None, Cell(0, -1000, "EMPTY"))
            self.westBoundary = Tile(None, None, None, None, None, Cell(-1000, 0, "EMPTY"))
            self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        else:
            self.boundaries = boundaries

    def merge(self, tile1, tile2):
        """
        merge two tiles into one, reassign neighborhood, and return the merged tile in case a reference is needed

        """
        if(tile1.cell.type != tile2.cell.type):
            return "Tiles are not alligned"

        if tile1.cell.x == tile2.cell.x and tile1.cell.y == tile2.cell.y:
            return "Tiles are not alligned"

        if tile1.cell.x == tile2.cell.x and (tile1.NORTH == tile2 or tile1.SOUTH == tile2) and tile1.getWidth() == tile2.getWidth():
            basis = tile1 if tile1.cell.y < tile2.cell.y else tile2
            upper = tile1 if tile1.cell.y > tile2.cell.y else tile2

            #reassign the newly merged tile's neighbors. We're using the lower of the tiles as the basis tile.
            basis.NORTH = upper.NORTH
            basis.EAST = upper.EAST
            if basis.cell.id==None:
                basis.cell.id=upper.cell.id
            if basis.nodeId==None:
                basis.nodeId=upper.nodeId


            #reasign the neighboring tile's directional pointers
            cc = upper.NORTH
            while cc not in self.boundaries and cc.cell.x >= basis.cell.x: #reset northern neighbors
                cc.SOUTH = basis
                cc = cc.WEST
            cc = upper.EAST
            while cc.cell.y >= basis.cell.y: #reset eastern neighbors
                cc.WEST = basis
                if cc.cell.y == basis.cell.y: break # a gross hack to prevent weird behavior when both cells are along the bottom edge
                cc = cc.SOUTH
            cc = basis.WEST
            while cc not in self.boundaries and cc.cell.y + cc.getHeight() <= basis.cell.y + basis.getHeight(): #reset western nieghbors
                cc.EAST = basis
                cc = cc.NORTH

            if(tile1 == upper):
                self.stitchList.remove(tile1)
            else:
                self.stitchList.remove(tile2)

        elif tile1.cell.y == tile2.cell.y and (tile1.EAST == tile2 or tile1.WEST == tile2) and tile1.getHeight() == tile2.getHeight():
            basis = tile1 if tile1.cell.x < tile2.cell.x else tile2
            eastMost = tile1 if tile1.cell.x > tile2.cell.x else tile2 #assign symbolic left and right tiles

            #reassign the newly merged tile's neighbors. We're using the leftMost of the tiles as the basis tile.
            basis.NORTH = eastMost.NORTH
            basis.EAST = eastMost.EAST
            if basis.cell.id == None:
                basis.cell.id = eastMost.cell.id
            if basis.nodeId == None:
                basis.nodeId = eastMost.nodeId


            #reasign the neighboring tile's directional pointers
            cc = eastMost.NORTH
            while cc not in self.boundaries and cc.cell.x >= basis.cell.x: #reset northern neighbors
                cc.SOUTH = basis
                cc = cc.WEST
            cc = eastMost.EAST
            while cc.cell.y >= basis.cell.y: #reset eastern neighbors
                cc.WEST = basis
                if cc.cell.y == basis.cell.y:break # a gross hack to prevent weird behavior when both cells are along the bottom edge
                cc = cc.SOUTH
            cc = eastMost.SOUTH
            while cc not in self.boundaries and cc.cell.x + cc.getWidth() <= basis.cell.x + basis.getWidth(): #reset souther nieghbors
                cc.NORTH = basis
                cc = cc.EAST

            if(tile1 == eastMost):
                self.stitchList.remove(tile1)
            else:
                self.stitchList.remove(tile2)
        else:
            return "Tiles are not alligned"

        return basis


    def findPoint(self, x, y, startCell):
        """
        find the tile that contains the coordinates x, y. if a point is inside or on the left or bottom edge of a tile, then that point is considered as on that tile.
         A point on right edge is on east tile and point on top edge is on north tile
        """
        cc = startCell #current cell


        while (y < cc.cell.y or y >=(cc.cell.y + cc.getHeight())): # finding y range

            if (y >= cc.cell.y + cc.getHeight()):
               if(cc.NORTH is not None):
                   cc = cc.NORTH
               else:
                   print("out of bounds 1")
                   return "Failed"
            elif y < cc.cell.y:
                if(cc.SOUTH is not None):
                    cc = cc.SOUTH
                else:
                    print("out of bounds 2")
                    return "Failed"
        while(x < cc.cell.x or x >=(cc.cell.x + cc.getWidth())): #finding x range

            if(x < cc.cell.x ):#x <= cc.cell.x
                if(cc.WEST is not None):
                    cc = cc.WEST
                else:
                    print("out of bounds 3")
                    return "Failed"
            if(x >= (cc.cell.x + cc.getWidth())):
                if(cc.EAST is not None):
                    cc = cc.EAST
                else:
                    print("out of bounds 4")
                    return "Failed"

        # recursive call
        if not ((cc.cell.x <= x and cc.cell.x + cc.getWidth() > x) and (cc.cell.y <= y and cc.cell.y + cc.getHeight() > y)):#(cc.cell.x <= x and cc.cell.x + cc.getWidth() >= x) and (cc.cell.y <= y and cc.cell.y + cc.getHeight() >= y)

            return self.findPoint(x, y, cc)

        return cc

    ## returns the list of tiles those are in the rectangular region surrounded by x1,y1 and x2,y2
    def AreaSearch(self,x1,y1,x2,y2):
        changeList = []
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1,y1,self.stitchList[0])
        if t.cell.y == y1:
            t = t.SOUTH
            while t.cell.x + t.getWidth() <= x1:
                t = t.EAST

        changeList.append(t)
        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:
                    t = child
                    if child not in changeList:
                        changeList.append(child)
                else:
                    dirn = 2  # to_root
            else:
                if t.cell.x <= x1 or t.cell.y <= y2:
                    if t.cell.y > y2:
                        t = t.SOUTH
                        while t.cell.x + t.getWidth() <= x1:
                            t = t.EAST

                        dirn = 1
                    elif t.cell.x + t.getWidth() < x2:
                        t = t.EAST

                        while t.cell.y > y2:
                            t = t.SOUTH
                        dirn = 1
                    else:
                        done = True
                elif t.WEST == t.SOUTH.WEST and t.SOUTH.WEST.cell.y >= y2:
                    t = t.SOUTH
                    dirn = 1
                else:
                    t = t.WEST
                if t not in changeList:
                    changeList.append(t)
        return changeList


    def vSplit(self, splitCell, x):
        """

        Vertically splits a cell into two parts at x coordinate. New cell is right half of the cell

        """

        if x < splitCell.cell.x or x > splitCell.cell.x + splitCell.getWidth(): # checking if x is inside the tile
            return
        if splitCell.cell.type!="EMPTY":
            newCell = Tile(None, None, None, None, None, Cell(x, splitCell.cell.y, splitCell.cell.type, id=splitCell.cell.id), nodeId=splitCell.nodeId)
        else:
            newCell = Tile(None, None, None, None, None, Cell(x, splitCell.cell.y, splitCell.cell.type, id=splitCell.cell.id))
        self.stitchList.append(newCell)

        #assigning new cell neigbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x

        if cc.cell.type != None:
            while cc.cell.x + cc.getWidth() <= x:
                cc = cc.EAST

        newCell.SOUTH = cc

        #reassign splitCell N and E
        splitCell.EAST = newCell

        cc = splitCell.NORTH
        while cc.cell.x >= splitCell.cell.x + splitCell.getWidth(): # Walk along the top edge until we reach the correct tile
            cc = cc.WEST

        splitCell.NORTH = cc

        #reassign surrounding cells neighbors
        cc = newCell.NORTH #reassign the SOUTH pointers for the top edge along the split half

        if cc.cell.type != None:
            while cc.cell.x >= x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge

        if cc.cell.type != None:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the NORTH pointers for the bottom edge

        if cc.cell.type != None:

            ccWidth = cc.getWidth()
            while cc.cell.type!=None and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
                cc.NORTH = newCell
                cc = cc.EAST
                if cc.cell.type!=None:
                    ccWidth = cc.getWidth()

        return newCell

    def hSplit(self, splitCell_id, y):

        """
        Horizontally splits a cell into two parts at y coordinate. NewCell is the top half of the split
        """
        splitCell=self.stitchList[splitCell_id]

        if y < splitCell.cell.y or y > splitCell.cell.y + splitCell.getHeight():
            return
        if splitCell.cell.type!="EMPTY":
            newCell = Tile(None, None, None, None, None, Cell(splitCell.cell.x, y, splitCell.cell.type, id=splitCell.cell.id), nodeId=splitCell.nodeId)
        else:
            newCell = Tile(None, None, None, None, None, Cell(splitCell.cell.x, y, splitCell.cell.type, id=splitCell.cell.id))

        self.stitchList.append(newCell)

        # assign new cell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH =splitCell

        cc = splitCell.WEST

        if cc.cell.type != None:
            while cc.cell.y + cc.getHeight() <= y:  # Walk upwards along the old west
                cc = cc.NORTH
        newCell.WEST = cc

        # reassign splitCell N
        splitCell.NORTH = newCell
        # reassign splitCell E
        cc = newCell.EAST
        while cc.cell.y >= newCell.cell.y:  # Walk down the right (eastward)edge
            cc = cc.SOUTH
        splitCell.EAST = cc

        # reassign the neighboring cells directional poitners

        cc = newCell.NORTH  # reassign the SOUTH pointers for the top edge along the split half


        if cc.cell.type!=None:
            while cc.cell.x >= newCell.cell.x:
                cc.SOUTH = newCell
                cc = cc.WEST


        cc = newCell.EAST  # reassign the WEST pointers for the right edge

        if cc.cell.type!=None:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.WEST  # reassign the EAST pointers for the right edge


        if cc.cell.type != None:

            while cc.cell.type!=None and cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
                cc.EAST = newCell
                cc = cc.NORTH
        self.stitchList[splitCell_id]=splitCell
        return newCell

    def orderInput(self, x1, y1, x2, y2):
        """
        Takes two input poitns and orders them so that x1, y1 correspond to the top left corner, and x2, y2
        correspond to the lower right corner. Called in insert functions to make sure that the input is properly
        ordered, as out of order coordinates can cause weird behavior.
        """
        if x2 < x1:
            holder = x2
            x2 = x1
            x1 = holder
        if y2 > y1:
            holder = y2
            y2 = y1
            y1 = holder

        return [x1, y1, x2, y2]
########################################################################################################################

class Node(CornerStitchAlgorithms):
    """
    Group of tiles .Part of hierarchical Tree
    """
    __metaclass__ = ABCMeta
    def __init__(self,boundaries,stitchList,parent=None,id=None,):
        self.parent=parent  # parent node
        self.child=[]       # child node list
        self.stitchList=stitchList # tile list in the node
        self.id=id  # node id
        self.boundaries=boundaries # boundary tiles list

    def getParent(self):
        return self.parent

    def getChild(self):
        return self.child

    def getId(self):
        return self.id

    def getstitchList(self):
        return self.stitchList

    def getboundaries(self):
        return self.boundaries

    def printNodeComponents(self):
        print "Parent Node="
        if self.parent!=None:
            print self.parent.id,self.parent
        else:
            print "ROOT"

        print "Node ID=",self.id
        print"STITCHLIST:"
        for rect in self.stitchList:
            print rect.printTile()

        print"BOUNDARIES:"
        for rect in self.boundaries:
            print rect.printTile()



##Node object for vertical corner stitched tree element
class Vnode(Node):
    def __init__(self, boundaries, stitchList, parent, id):

        self.stitchList=stitchList
        self.boundaries=boundaries
        self.child=[]
        self.parent=parent
        self.id=id

    # merge function to merge empty tiles(to maintain corner stitch property)
    def Final_Merge(self):
        changeList = []


        for rect in self.stitchList:

            if rect.nodeId==self.id:
                changeList.append(rect)


        list_len = len(changeList)
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                j = 0
                while j < len(changeList):
                    top = changeList[j]
                    low = changeList[i]
                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList):
                            j += 1

                    else:

                        del changeList[j]
                        if i > j:
                            del changeList[i - 1]
                        else:
                            del changeList[i]
                        x = min(i, j)
                        mergedcell.type = 'Type_1'
                        changeList.insert(x, mergedcell)

                i += 1

            if c == list_len:
                break

        return self.stitchList
    def insert(self, start,x1, y1, x2, y2, type,end,Vtree,Parent,rotate_angle=None,bw=None):
        """

              :param start: starting charsacter
              :param x1: top left corner's x coordinate
              :param y1: top left corner's y coordinate
              :param x2: bottom right corner's x coordinate
              :param y2: bottom right corner's y coordinate
              :param type: type of tile
              :param end: end character(Global variable)
              :param Vtree: Vertical tree structure
              :param Parent: Parent node from the tree
              :param Rotate_angle: rotation angle for parts
              :return: Updated tree with inserting new tile
              """
        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the cornerStitch's stitchList, then corrects empty space vertically
        Four steps:
        1. vsplit x1, x2
        2. hsplit y1, y2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = []  # list of empty tiles that contain the area to be effected

        foo = self.orderInput(x1, y1, x2, y2)
        x1 = foo[0]
        y1 = foo[1]
        x2 = foo[2]
        y2 = foo[3]
        RESP=0 # flag to check empty area
        #if self.areaSearch(x1, y1, x2, y2,type):#check to ensure that the area is empty
            #RESP=1

        # finding top left and bottom right coordinate containing tiles of the new tile
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        tr = self.findPoint(x2, y1, self.stitchList[0])
        if tr.cell.x == x2:
            tr = tr.WEST
            while (tr.cell.y + tr.getHeight() < y1):
                tr = tr.NORTH
        bl = self.findPoint(x1, y2, self.stitchList[0])
        if topLeft.cell.y == y1:
            topLeft = topLeft.SOUTH
            while topLeft.cell.x + topLeft.getWidth() <= x1:
                topLeft = topLeft.EAST

        if tr.cell.y == y1:
            tr = tr.SOUTH
            while tr.cell.x + tr.getWidth() <= x1:
                tr = tr.EAST

        if bottomRight.cell.x == x2:
            bottomRight = bottomRight.WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH

        # list of tiles which should be split vertically  at x2 (creating right edge of new tile)
        splitList = []
        splitList.append(bottomRight)

        # if the tile is continuing tile of a group look for top or bottom tiles if they should also be merged
        if start != Schar:
            if bottomRight.SOUTH not in self.boundaries and bottomRight.SOUTH.cell.type == type and bottomRight.SOUTH.cell.y + bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type == type:
                cc1 = bottomRight.SOUTH
                while cc1.cell.x + cc1.getWidth() < x2:
                    cc1 = cc1.EAST
                if cc1 not in splitList:
                    splitList.append(cc1)

                if cc1.cell.type == type and cc1.cell.y + cc1.getHeight() == y2:
                    cc2 = cc1.SOUTH
                    while cc2.cell.x + cc2.getWidth() < x2:
                        cc2 = cc2.EAST
                    if cc2 not in splitList and cc2.cell.type=="EMPTY" :
                        splitList.append(cc2)


            cc = bottomRight.NORTH

            while cc.cell.y <= tr.cell.y and cc not in self.boundaries:
                while cc.cell.x>=x2:
                    cc=cc.WEST
                if cc not in splitList:
                    splitList.append(cc)
                cc = cc.NORTH
                while cc.cell.x >= x2:
                    cc = cc.WEST

            if cc.cell.type == type and cc.cell.y == y1 or tr.cell.type == type:
                if cc not in splitList and cc not in self.boundaries:
                    splitList.append(cc)
                if cc not in self.boundaries:
                    cc = cc.NORTH
                    while cc.cell.x > x2:
                        cc = cc.WEST
                    if cc not in self.boundaries and cc.cell.type=="EMPTY":
                        splitList.append(cc)

        # splitting tiles vertically at x2 coordinate
        for rect in splitList:
            if x2 != rect.cell.x and x2 != rect.EAST.cell.x:

                self.vSplit(rect, x2)

        # list of tiles those should be split vertically at x1 coordinate(creating left edge of new tile)
        splitList = []
        splitList.append(topLeft)

        #if the tile is continuing tile of a group look for top or bottom tiles if they should also be merged
        if start != Schar:
            if topLeft.NORTH not in self.boundaries and topLeft.NORTH.cell.type == type and topLeft.NORTH.cell.y == y1 or topLeft.cell.type == type:
                cc = topLeft.NORTH
                while cc.cell.x > x1:
                    cc = cc.WEST

                splitList.append(cc)


                if cc.cell.type == type and cc.cell.y == y1:
                    cc1 = cc.NORTH
                    while cc1.cell.x > x1:
                        cc1 = cc1.WEST
                    if cc1 not in splitList and cc not in self.boundaries and cc1.cell.type=="EMPTY":
                        splitList.append(cc1)
            cc = topLeft
            while cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2:
                if cc not in splitList:
                    splitList.append(cc)

                cc = cc.SOUTH
                while cc not in self.boundaries and cc.cell.x + cc.getWidth() <= x1:
                    cc = cc.EAST

            if cc.cell.type == type and cc.cell.y + cc.getHeight() == y2 or bl.cell.type == type:
                if cc not in splitList and cc not in self.boundaries:

                    splitList.append(cc)
                # if cc.cell.type=="SOLID" and cc.cell.y+cc.getHeight() == y2:

                if cc.cell.type == type and cc.cell.y + cc.getHeight() == y2 :
                    if cc.SOUTH not in self.boundaries:
                        cc = cc.SOUTH
                    while cc.cell.x + cc.getWidth() <= x1:
                        cc = cc.EAST
                    if cc.cell.type=="EMPTY":
                        splitList.append(cc)

        # splitting tiles vertically at x1 coordinate
        for rect in splitList:
            if x1 != rect.cell.x and x1 != rect.EAST.cell.x:
                self.vSplit(rect, x1)

        ### Horizontal split
        # list of tiles which should be split horizontally at y1 and y2 coordinate(creating top and bottom edge of new tile)
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0])

        if cc.cell.y == y1:
            cc = cc.SOUTH
            while cc.cell.x+cc.getWidth()<=x1:
                cc=cc.EAST


        while cc.cell.x + cc.getWidth() <= x2:
            if cc not in changeList:
                changeList.append(cc)

            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH

        cc1 = self.findPoint(x1, y2, self.stitchList[0])
        while cc1.cell.x + cc1.getWidth() <= x2:
            if cc1 not in changeList:
                changeList.append(cc1)
            cc1 = cc1.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH

        for rect in changeList:
            i = self.stitchList.index(rect)
            if not rect.NORTH.cell.y == y1:
                self.hSplit(i, y1)
            if not rect.cell.y == y2:
                self.hSplit(i, y2)


        if start != Schar:
            cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
            while cc not in self.boundaries and cc.cell.x < x1:
                cc = cc.EAST

            ## Re-splitting for overlapping cases

            while cc.cell.x < x2:
                cc1 = cc
                resplit = []
                min_x = 1000000000000
                while cc1.cell.y >= y2:
                    if cc1.cell.x + cc1.getWidth() < min_x:
                        min_x = cc1.cell.x + cc1.getWidth()
                    resplit.append(cc1)
                    cc1 = cc1.SOUTH
                if len(resplit) > 1:
                    for foo in resplit:
                        if foo.cell.x + foo.getWidth() > min_x:
                            if foo.cell.x != min_x:
                                self.vSplit(foo, min_x)
                cc = cc.EAST

            ##### checking for potential resplitting tiles to deal with overlapping tiles
            resplit = []

            cc = self.findPoint(x1, y2, self.stitchList[0])
            while cc.cell.x + cc.getWidth() <= x2:
                if cc.SOUTH.cell.type == type and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH not in self.boundaries and cc.SOUTH.cell.x + cc.SOUTH.getWidth() != cc.cell.x + cc.getWidth():
                    resplit.append(cc.SOUTH)
                    resplit.append(cc.SOUTH.SOUTH)

                for rect in resplit:
                    self.vSplit(rect, cc.cell.x + cc.getWidth())
                cc = cc.EAST

            resplit = []
            cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
            while cc.cell.x + cc.getWidth() <= x2:
                if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and cc.NORTH not in self.boundaries and cc.NORTH.cell.x + cc.NORTH.getWidth() != cc.cell.x + cc.getWidth():
                    resplit.append(cc.NORTH)
                    resplit.append(cc.NORTH.NORTH)

                    for rect in resplit:
                        self.vSplit(rect, cc.cell.x + cc.getWidth())
                cc = cc.EAST

        # list of tiles which should be merged. (Tiles which are inside new tile area)
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while cc.cell.x + cc.getWidth() <= x2:
            # if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1:
            if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and start!= Schar:
                changeList.append(cc.NORTH)
            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH

        # area search is performed to find all tiles inside the new tile area
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH

        changeList.append(t)
        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:
                    t = child
                    if child not in changeList:
                        changeList.append(child)

                else:

                    dirn = 2  # to_root

            else:
                oldt = t
                if t.cell.x <= x1 or t.cell.y <= y2:
                    if t.cell.y > y2:
                        t = t.SOUTH
                        while t.cell.x + t.getWidth() <= x1:
                            t = t.EAST

                        dirn = 1
                    elif t.cell.x + t.getWidth() < x2:
                        t = t.EAST
                        while t.cell.y > y2:
                            t = t.SOUTH
                        dirn = 1
                    else:
                        done = True
                elif t.WEST == t.SOUTH.WEST and t.SOUTH.WEST.cell.y >= y2:
                    t = t.SOUTH
                    dirn = 1
                else:
                    t = t.WEST
                if t not in changeList:
                    changeList.append(t)

        cc1 = self.findPoint(x1, y2, self.stitchList[0])

        while cc1.cell.x + cc1.getWidth() <= x2:
            if cc1.SOUTH.cell.type == type and cc1.SOUTH.cell.y + cc1.SOUTH.getHeight() == y2 and start!= Schar:
                changeList.append(cc1.SOUTH)
            cc1 = cc1.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH

        if start != Schar:
            for i in changeList:
                N=i.findNeighbors()
                for j in N:
                    if j.cell.type==type and j not in changeList:
                        RESP=1
                        changeList.append(j)
                    elif j.nodeId!=0 and j.cell.type==type:
                        RESP=1
        changeList.sort(key=lambda cc: cc.cell.x)

        # merging tiles inside new tile area
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            if top.cell.y == low.cell.y + low.getHeight() or top.cell.y + top.getHeight() == low.cell.y:
                top.cell.type = type
                low.cell.type = type

                mergedcell = self.merge(top, low)
                if mergedcell == "Tiles are not alligned":

                    i += 1
                else:
                    del changeList[i + 1]
                    del changeList[i]

                    changeList.insert(i, mergedcell)

            else:
                i += 1

        list_len = len(changeList)

        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                j = 0
                while j < len(changeList):
                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type
                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList):
                            j += 1

                    else:

                        del changeList[j]
                        if i > j:
                            del changeList[i - 1]
                        else:
                            del changeList[i]
                        x = min(i, j)
                        changeList.insert(x, mergedcell)

                        self.rectifyShadow(changeList[x])

                i += 1

            if c == list_len:
                break

        for x in range(0, len(changeList)):

            changeList[x].cell.type = type
            changeList[x].rotation_index=rotate_angle # adding rotation index 0:0 deg, 1: 90 deg, 2: 180 deg, 3: 270 deg

            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:

            changeList[0].cell.type = type
            if len(changeList)==1 and RESP==0:
                changeList[0].nodeId=None
            self.rectifyShadow(changeList[0])


            self.set_id_V()

            tile_list=[]
            tile_list.append(changeList[0])
            if start== Schar and end == Schar:
                for rect in changeList:
                    N = rect.findNeighbors()
                    for i in N:
                        if i not in tile_list:
                            tile_list.append(i)
            else:
                for rect in changeList:
                    N = rect.findNeighbors()
                    for i in N:
                        if i.cell.type == type:

                            N2 = i.findNeighbors()
                            for j in N2:
                                if j not in tile_list:
                                    tile_list.append(j)
                        if i not in tile_list:
                            tile_list.append(i)
            self.addChild(start,tile_list,type,end,Vtree,Parent)  # after creating a tile it's parent should be updated
            if bw!=None:
                Connections = [bw[x:x + 3] for x in xrange(0, len(bw), 3)]

                #print Connections
                for w in Connections:

                    parent_tile = None
                    for wire in v_bondwire_objects:
                        #print"PRe", wire.src_coordinate, wire.dest_coordinate
                        if wire.name==w[0]:

                            if wire.src_coordinate==None:

                                wire.src_coordinate=(int(w[1]),int(w[2]))
                                x = wire.src_coordinate[0]
                                y = wire.src_coordinate[1]
                                if x >= x1 and y >= y2 and x <= x2 and y <= y1:
                                    parent_tile = self.findPoint(x1, y2, tile_list[0])
                                    wire.src_tile = parent_tile
                                    wire.src_nodeID = Parent.id
                                    #wire.src_nodeID = parent_tile.nodeId
                            elif wire.dest_coordinate==None:

                                wire.dest_coordinate = (int(w[1]), int(w[2]))

                                x3 = wire.dest_coordinate[0]
                                y3 = wire.dest_coordinate[1]
                                if x3 >= x1 and y3 >= y2 and x3 <= x2 and y3 <= y1:
                                    parent_tile = self.findPoint(x1, y2, tile_list[0])
                                    wire.dest_tile = parent_tile
                                    wire.dest_nodeID = Parent.id
                                    #wire.dest_nodeID =  parent_tile.nodeId


                            #print "Pr",parent_tile.cell.x,parent_tile.cell.y,parent_tile.cell.type,wire.src_coordinate,wire.dest_coordinate
                            parent_tile.bw.append(wire)
        return self.stitchList


    # adding new child in the tree
    def addChild(self,start, tile_list, type,end,Vtree,Parent):
        """

               :param start: start character for finding whetehr new group is started
               :param tile_list: list of tiles to be considered in group creation
               :param type: type of newly inserted tile
               :param end: end character to find if the group is closed or not
               :param Vtree: Vertical cornerstitched tree
               :param Parent: Parent of the current tile
               :return: updated vtree by appending new tile into appropriate group
               """
        # if it's a new isolated tile its a new group member
        if start== Schar and end == Schar:
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:
                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Vnode(parent=Parent,stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            Parent.child.append(node)
            Vtree.vNodeList.append(node)

        # if it's a group's starting member and not the only member
        elif start == Schar and end != Schar:
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:


                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Vnode(parent=Parent,stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            Parent.child.append(node)
            Vtree.vNodeList.append(node)

        # if it's neither starting nor ending but a continuing member of a group
        elif start!= Schar and end != Schar:
            ID = 0
            for rect in tile_list:

                if rect.cell.type != "EMPTY":
                    if rect.nodeId > ID:
                        ID = rect.nodeId

            for N in Vtree.vNodeList:

                if N.id == ID:
                    node = N
            id = node.id
            stitchList = node.stitchList
            boundaries = node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries or rect.cell.type == type:
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id
            for rect in tile_list:
                if rect not in stitchList and rect.nodeId == id:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))

        # if it's an ending member of a group
        elif start != Schar and end == Schar:
            ID = 0
            for rect in tile_list:

                if rect.cell.type != "EMPTY":
                    if rect.nodeId > ID:
                        ID = rect.nodeId
            for N in Vtree.vNodeList:

                if N.id == ID:
                    node = N
            id = node.id
            stitchList = node.stitchList
            boundaries = node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries or rect.cell.type == type:
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id
            for rect in tile_list:


                # if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.nodeId==id:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    # if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))
            Vtree.vNodeList.remove(node)
            Node = Vnode(parent=Parent,stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            Parent.child.append(Node)
            Vtree.vNodeList.append(Node)




    def rectifyShadow(self, caster):
        """
        this checks the NORTH and SOUTH of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        """
        changeSet = []

        cc = caster.NORTH  # recitfy north side, walking downwards

        while (cc not in self.boundaries and cc.cell.x >= caster.cell.x):

            changeSet.append(cc)
            cc = cc.WEST

        i = 0
        j = 1
        while j < len(changeSet):  # merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]

            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                if j < len(changeSet):
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell


        cc = caster.SOUTH  # recitfy SOUTH side, walking eastwards
        changeSet = []


        while (cc not in self.boundaries and cc.cell.x < caster.cell.x + caster.getWidth()):

            changeSet.append(cc)
            cc = cc.EAST

        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet):  # merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]

            mergedCell = self.merge(topCell, lowerCell)

            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                if j < len(changeSet) - 1:
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell



        return



    ### NEW AREA SEARCH : finds if there is any given type tile in the area covered by x1,y1 and x2,y2
    def areaSearch(self, x1, y1, x2, y2,type):
        cc = self.findPoint(x1, y1, self.stitchList[0])  # the tile that contains the first corner point

        sc = self.findPoint(x2, y2, self.stitchList[0])  # the tile that contains the second(bottom right) corner
        if cc.cell.y == y1:
            cc = cc.SOUTH

            while cc.cell.x + cc.getWidth() < x1:
                cc = cc.EAST

        if cc.cell.type == type:
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.y > y2:
            return True  # the corner cell is empty but touches a solid cell within the search area

        cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.x < x2):

            while (cc.cell.y + cc.getHeight() > y2):

                if cc.cell.y < y1 and cc.cell.type == type:
                    return True
                if cc.SOUTH not in self.boundaries:
                    cc = cc.SOUTH
                else:
                    break
            cc = cc.EAST
        return False

    def set_id_V(self):  ########## Setting id for all tiles other than empty
        global VID
        for rect in self.stitchList:
            if  rect.cell.type!="EMPTY":
                rect.cell.id=VID+1
                VID+=1
        return

## Horizontal corner stitch tree element
class Hnode(Node):
    def __init__(self, boundaries,stitchList, parent, id):

        self.stitchList = stitchList
        self.boundaries = boundaries
        self.child = []
        self.parent = parent
        self.id = id

    # merge all possible tiles to maintain corner stitch property
    def Final_Merge(self):

        changeList = []


        for rect in self.stitchList:


            if rect.nodeId==self.id:
                changeList.append(rect)


        list_len = len(changeList)
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:

                j = 0
                while j < len(changeList):

                    top = changeList[j]
                    if changeList[i] !=None:
                        low = changeList[i]

                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList):
                            j += 1

                    else:

                        del changeList[j]
                        if i > j:
                            del changeList[i - 1]
                        else:
                            del changeList[i]
                        x = min(i, j)

                        mergedcell.type = 'Type_1'

                        changeList.insert(x, mergedcell)


                i += 1

            if c == list_len:
                break

        return self.stitchList

    def insert(self,start, x1, y1, x2, y2, type,end,Htree,Parent,rotate_angle=None,bw=None):
        """

        :param start: starting charsacter
        :param x1: top left corner's x coordinate
        :param y1: top left corner's y coordinate
        :param x2: bottom right corner's x coordinate
        :param y2: bottom right corner's y coordinate
        :param type: type of tile
        :param end: end character(Global variable)
        :param Htree: Horizontal tree structure
        :param Parent: Parent node from the tree
        :return: Updated tree with inserting new tile
        """

        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the cornerStitch's stitchList, then corrects empty space horizontally
        1. hsplit y1, y2
        2. vsplit x1, x2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = []  # list of empty tiles that contain the area to be effected

        foo = self.orderInput(x1, y1, x2, y2)
        x1 = foo[0]
        y1 = foo[1]
        x2 = foo[2]
        y2 = foo[3]
        RESP = 0
        #if self.areaSearch(x1, y1, x2, y2,type): #check to ensure that the area is empty

            #RESP=1
        #print"ENTRY",x1,y1,x2,y2
        # finds top left and bottom right coordinate containing tile and then start for finding all tiles which should be split
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        tr = self.findPoint(x2, y1, self.stitchList[0])
        bl = self.findPoint(x1, y2, self.stitchList[0])

        if topLeft.cell.y == y1:
            cc = topLeft
            if topLeft.SOUTH not in self.boundaries:
                cc = topLeft.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() <= x1:
                cc = cc.EAST
            topLeft = cc

        if tr.cell.y == y1:
            cc = tr
            if tr.SOUTH not in self.boundaries:
                cc = tr.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() < x2:
                cc = cc.EAST
            tr = cc


        # list of tiles which should be split horizontally at y1 coordinate(creating top edge of new tile)
        splitList = []
        splitList.append(topLeft)
        cc = topLeft
        #print "TL",cc.cell.x, cc.cell.y, cc.cell.type,cc.getWidth(),cc.getHeight(),cc.cell.type
        #print"TR",tr.cell.x,tr.cell.y, tr.cell.type,tr.getWidth(),tr.getHeight(),tr.cell.type

        if start!=Schar:
            if cc.WEST not in self.boundaries and cc.WEST.cell.type == type and cc.WEST.cell.x + cc.WEST.getWidth() == x1 or cc.cell.type == type:
                cc1 = cc.WEST
                while cc1.cell.y + cc1.getHeight() < y1:
                    cc1 = cc1.NORTH

                splitList.append(cc1)

                cc2 = cc1.WEST

                while cc2 not in self.boundaries and cc2.cell.y + cc2.getHeight() < y1:
                    cc2 = cc2.NORTH
                if cc2 not in self.boundaries:
                    splitList.append(cc2)

            #print "HSP", len(splitList)
            while cc.cell.x <= tr.cell.x and cc not in self.boundaries:
                if cc not in splitList:
                    splitList.append(cc)

                cc = cc.EAST

                while cc.cell.y >= y1 and cc not in self.boundaries:
                    cc = cc.SOUTH


            if cc.cell.type == type and cc.cell.x == x2 and cc not in self.boundaries or tr.cell.type == type:

                splitList.append(cc)

                if cc.EAST not in self.boundaries : # added cc.cell.type==type
                    cc = cc.EAST

                    while cc.cell.y >= y1:
                        cc = cc.SOUTH
                    if cc.cell.type==type:
                        splitList.append(cc)


        # splitting tiles at y1 coordinate
        #print "HSP",len(splitList)
        for rect in splitList:
            #print rect.cell.x,rect.cell.y,rect.cell.type
            i = self.stitchList.index(rect)
            if y1 != rect.cell.y and y1 != rect.NORTH.cell.y:
                self.hSplit(i, y1)



        if bottomRight.cell.x == x2:
            bottomRight = bottomRight.WEST

            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH

        # list of tiles which need to be split horizontally at y2 coordinate(creating bottom edge of new tile)
        splitList = []
        splitList.append(bottomRight)
        cc = bottomRight
        if start!=Schar:

            if cc.EAST not in self.boundaries and cc.EAST.cell.type == type and cc.EAST.cell.x == x2 or cc.cell.type == type:
                cc1 = cc.EAST
                while cc1.cell.y > y2:
                    cc1 = cc1.SOUTH
                splitList.append(cc1)

                if cc1.cell.type == type and cc1.cell.x == x2:
                    cc2 = cc1.EAST
                    while cc2.cell.y > y2:
                        cc2 = cc2.SOUTH
                    splitList.append(cc2)

            while cc.cell.x >= x1 and cc not in self.boundaries:
                cc = cc.WEST

                if cc not in self.boundaries:
                    while cc.cell.y + cc.getHeight() <= y2:
                        cc = cc.NORTH
                if cc not in splitList:
                    splitList.append(cc)

            if cc.cell.type == type and cc.cell.x + cc.getWidth() >= x1 or bl.cell.type == type:
                if cc not in splitList:
                    splitList.append(cc)

                if cc.WEST not in self.boundaries:
                    cc1 = cc.WEST
                    while cc1.cell.y + cc1.getHeight() <= y2:
                        cc1 = cc1.NORTH
                    splitList.append(cc1)


        # splitting tiles at y2 coordinate
        #print"v_split",len(splitList)
        for rect in splitList:
            #print"s",rect.cell.x,rect.cell.y,rect.cell.type,rect.getWidth(),rect.getHeight()
            i=self.stitchList.index(rect)
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y: self.hSplit(i, y2)


        # step 2: vsplit x1 and x2
        #list of tiles which need to be split vertically at x1 and x2
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        # print x1,y1

        while cc.cell.x + cc.getWidth() <= x1:
            cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while cc.cell.x + cc.getWidth() <= x1:
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH

        cc = self.findPoint(x2, y1, self.stitchList[0]).SOUTH

        if cc.cell.x == x2:
            cc = cc.WEST
        while cc.cell.x + cc.getWidth() < x2:
            cc = cc.EAST

        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while cc.cell.x + cc.getWidth() < x2:
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH


        for rect in changeList:  # split vertically

            if not rect.EAST.cell.x == x2:
                self.vSplit(rect, x2)
            if not rect.cell.x == x1:
                self.vSplit(rect, x1)

        if start!=Schar:
            cc = self.findPoint(x2, y2, self.stitchList[0]).WEST
            while cc not in self.boundaries and cc.cell.y + cc.getHeight() <= y1:
                cc1 = cc

                # resplitting tiles for dealing with overlapping cases
                resplit = []
                min_y = 1000000000000
                while cc1 not in self.boundaries and cc1.cell.x >= x1:
                    if cc1.cell.y + cc1.getHeight() < min_y:
                        min_y = cc1.cell.y + cc1.getHeight()
                    resplit.append(cc1)
                    if cc1.cell.x == x1 and cc1.WEST.cell.type==type :
                        resplit.append(cc1.WEST)

                        if cc1.WEST.cell.type == type:
                            resplit.append(cc1.WEST.WEST)
                    if cc1.EAST.cell.x == x2 :
                        resplit.append(cc1.EAST)

                        if cc1.EAST.cell.type == type:
                            resplit.append(cc1.EAST.EAST)

                    cc1 = cc1.WEST


                if len(resplit) > 1:
                    for foo in resplit:

                        if foo.cell.y + foo.getHeight() > min_y:

                            if min_y != foo.cell.y and min_y != foo.NORTH.cell.y:
                                #RESP=1
                                k=self.stitchList.index(foo)
                                self.hSplit(k, min_y)

                if cc.NORTH not in self.boundaries:
                    cc = cc.NORTH

                else:
                    break


        # list of tiles which are potential merge candidate inside new tile area
        changeList = []

        # performing area search
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1 and start!=Schar:
            changeList.append(t.WEST)
        changeList.append(t)
        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:
                    t = child
                    if child not in changeList:
                        changeList.append(child)
                else:
                    if child.cell.type == type and child.cell.x == x2 and start!=Schar:
                        if child not in changeList:
                            changeList.append(child)
                    dirn = 2  # to_root
            else:
                if t.cell.x <= x1 or t.cell.y <= y2:
                    if t.cell.y > y2:
                        t = t.SOUTH
                        while t.cell.x + t.getWidth() <= x1:
                            t = t.EAST
                        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1 and start!=Schar:
                            changeList.append(t.WEST)
                        dirn = 1
                    elif t.cell.x + t.getWidth() < x2:
                        t = t.EAST
                        while t.cell.y > y2:
                            t = t.SOUTH
                        dirn = 1
                    else:
                        done = True
                elif t.WEST == t.SOUTH.WEST and t.SOUTH.WEST.cell.y >= y2:
                    t = t.SOUTH
                    dirn = 1
                else:
                    t = t.WEST
                if t not in changeList:
                    changeList.append(t)

        if start!=Schar:
            for i in changeList:
                N=i.findNeighbors()
                for j in N:
                    if j.cell.type==type and j not in changeList:
                        RESP=1
                        changeList.append(j)
                    elif j.nodeId!=0 and j.cell.type==type:
                        RESP=1


        # Merging tiles inside new tile area and creating new tile
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]

            if top.cell.x == low.cell.x + low.getWidth() or top.cell.x + top.getWidth() == low.cell.x:
                top.cell.type = type
                low.cell.type = type
                mergedcell = self.merge(top, low)
                if mergedcell == "Tiles are not alligned":
                    i += 1
                else:
                    del changeList[i + 1]
                    del changeList[i]
                    # print"arealist=", len(changeList)
                    if len(changeList) == 0:
                        changeList.append(mergedcell)
                    else:
                        changeList.insert(i, mergedcell)
                    self.rectifyShadow(changeList[i])
            else:
                i += 1

        list_len = len(changeList)

        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:

                j = 0
                while j < len(changeList):


                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type

                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList):
                            j += 1

                    else:

                        del changeList[j]
                        if i > j:
                            del changeList[i - 1]
                        else:
                            del changeList[i]
                        x = min(i, j)

                        changeList.insert(x, mergedcell)

                i += 1

            if c == list_len:
                break

        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]

            top.cell.type = type
            low.cell.type = type
            mergedcell = self.merge(top, low)
            if mergedcell == "Tiles are not alligned":
                i += 1
            else:
                del changeList[i + 1]
                del changeList[i]
                # print"arealist=", len(changeList)
                if len(changeList) == 0:
                    changeList.append(mergedcell)
                else:
                    changeList.insert(i, mergedcell)
                self.rectifyShadow(changeList[i])



        for x in range(0, len(changeList)):
            changeList[x].cell.type = type
            changeList[x].rotation_index=rotate_angle

            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:

            changeList[0].cell.type = type

            if len(changeList)==1 and RESP==0:
                changeList[0].nodeId = None

            self.rectifyShadow(changeList[0])
            self.set_id()
            rect = changeList[0]

            tile_list = []
            tile_list.append(changeList[0])
            if start == Schar and end == Schar:
                for rect in changeList:
                    N = rect.findNeighbors()
                    for i in N:
                        if i not in tile_list:
                            tile_list.append(i)
            else:
                for rect in changeList:
                    N = rect.findNeighbors()
                    for i in N:
                        if i.cell.type == type:
                            # print "1",i.nodeId
                            N2 = i.findNeighbors()
                            for j in N2:
                                if j not in tile_list:
                                    tile_list.append(j)
                        if i not in tile_list:
                            tile_list.append(i)

            self.addChild(start,tile_list, type,end,Htree,Parent)
            if bw!=None:
                Connections = [bw[x:x + 3] for x in xrange(0, len(bw), 3)]


                #print Connections
                for w in Connections:

                    parent_tile = None
                    for wire in h_bondwire_objects:
                        if wire.name==w[0]:
                            if wire.src_coordinate==None:
                                wire.src_coordinate=(int(w[1]),int(w[2]))
                                x = wire.src_coordinate[0]
                                y = wire.src_coordinate[1]
                                if x >= x1 and y >= y2 and x <= x2 and y <= y1:
                                    parent_tile = self.findPoint(x1, y2, tile_list[0])
                                    wire.src_tile = parent_tile
                                    wire.src_nodeID = ParentH.id
                                    #wire.src_nodeID = parent_tile.nodeId
                            elif wire.dest_coordinate==None:
                                wire.dest_coordinate = (int(w[1]), int(w[2]))
                                x3 = wire.dest_coordinate[0]
                                y3 = wire.dest_coordinate[1]
                                if x3 >= x1 and y3 >= y2 and x3 <= x2 and y3 <= y1:
                                    parent_tile = self.findPoint(x1, y2, tile_list[0])
                                    wire.dest_tile = parent_tile
                                    wire.dest_nodeID = ParentH.id
                                    #wire.dest_nodeID = parent_tile.nodeId
                            parent_tile.bw.append(wire)


        return self.stitchList

    def addChild(self,start, tile_list, type,end,Htree,ParentH):
        """

        :param start: start character for finding whetehr new group is started
        :param tile_list: list of tiles to be considered in group creation
        :param type: type of newly inserted tile
        :param end: end character to find if the group is closed or not
        :param Htree: Horizontal cornerstitched tree
        :param ParentH: Parent of the current tile
        :return: updated htree by appending new tile into appropriate group
        """
        # if it's the only tile in the group
        if start== Schar and end == Schar:
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:
                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Hnode(parent=ParentH,stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            ParentH.child.append(node)
            Htree.hNodeList.append(node)

        # if it's a starting group member
        elif start == Schar and end != Schar:
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:
                # print "R", rect.cell.x, rect.cell.y

                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Hnode(parent=ParentH, stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            ParentH.child.append(node)
            Htree.hNodeList.append(node)

        # if it's neither starting nor ending but continuing group member
        elif start!= Schar and end != Schar:
            ID = 0
            for rect in tile_list:

                if rect.cell.type != "EMPTY":
                    if rect.nodeId > ID:
                        ID = rect.nodeId

            for N in Htree.hNodeList:

                if N.id == ID:
                    node = N
            id = node.id
            stitchList = node.stitchList
            boundaries = node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries:
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)

            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id

                if rect not in stitchList and rect.nodeId == id:

                    stitchList.append(rect)
                else:

                    if rect not in boundaries:
                        boundaries.append(copy.copy(rect))

        # if it's an ending group member
        elif start != Schar and end == Schar:
            ID=0
            for rect in tile_list:
                if rect.cell.type != "EMPTY":
                    if rect.nodeId>ID:
                        ID=rect.nodeId


            for N in Htree.hNodeList:

                if N.id == ID:
                    node = N
            id = node.id
            stitchList = node.stitchList
            boundaries = node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries :
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)

            for rect in tile_list:

                if rect.cell.type==type:
                    rect.nodeId=id

                if rect not in stitchList and rect.nodeId==id:

                    stitchList.append(rect)
                else:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))
            Htree.hNodeList.remove(node)
            Node = Hnode(parent=ParentH,stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            ParentH.child.append(Node)
            Htree.hNodeList.append(Node)



    def rectifyShadow(self, caster):
        """
                this checks the EAST and WEST of caster, to see if there are alligned empty cells that could be merged.
                Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other

                Re-write this to walk along the E and W edges and try to combine neighbors sequentially
                """
        changeSet = []

        cc = caster.EAST  # recitfy east side, walking downwards

        while (cc not in self.boundaries and cc.cell.y >= caster.cell.y):

            changeSet.append(cc)
            cc = cc.SOUTH
        i = 0
        j = 1
        while j < len(changeSet):  # merge all cells with the same width along the eastern side

            topCell = changeSet[i]
            lowerCell = changeSet[j]

            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                if j < len(changeSet):
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell


        cc = caster.WEST  # recitfy west side, walking upwards
        changeSet = []


        while (cc not in self.boundaries and cc.cell.y < caster.cell.y + caster.getHeight()):

            changeSet.append(cc)
            cc = cc.NORTH


        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet):  # merge all cells with the same width along the eastern side
            topCell = changeSet[i]

            lowerCell = changeSet[j]

            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                # print "i = ", i
                if j < len(changeSet) - 1:
                    j += 1
            else:
                changeSet[i] = mergedCell
                del changeSet[j]

        return

    def areaSearch(self, x1, y1, x2, y2,type):

        cc = self.findPoint(x1, y1, self.stitchList[0])  # the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2,self.stitchList[0])  # the tile that contains the second(bottom right)corner


        if cc.cell.type == type and cc.cell.y != y1:
            return True
        elif cc.cell.x + cc.getWidth() < x2 and cc.cell.y != y1 and cc.cell.x != x1:
            return True
        cc = cc.SOUTH
        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while (
                    cc.cell.x + cc.getWidth() <= x1):
                cc = cc.EAST
            if cc.cell.type == type:
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x + cc.getWidth() < x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH  # check the next lowest cell
        return False

    def set_id(self):  ########## Setting id for all type 1 blocks
        global HID
        for rect in self.stitchList:
            if  rect.cell.type!="EMPTY":

                rect.cell.id=HID+1

                HID+=1
        return

# tree class to make hierarchical tree structure
class Tree():
    def __init__(self,hNodeList,vNodeList):
        self.hNodeList=hNodeList
        self.vNodeList=vNodeList

    def setNodeId(self,nodelist):
        for node in nodelist:
            for rect in node.stitchList:
                rect.nodeId=node.id
            for rect in node.boundaries:
                rect.nodeId=node.id

    def setNodeId1(self,nodelist):

        node = nodelist[0]

        for n in nodelist:
            if len(n.child)==0 and n.parent.id==node.id:

                for rect1 in n.stitchList:
                    for rect in node.stitchList:
                        if rect1.cell.x==rect.cell.x and rect1.cell.y==rect.cell.y and rect1.getWidth()==rect.getWidth() and rect1.getHeight()==rect.getHeight() and rect1.cell.type==rect.cell.type:
                            rect.nodeId=node.id


        for rect in node.stitchList:
            if rect.nodeId==None:
                rect.nodeId=node.id
        for rect in node.boundaries:
            rect.nodeId=node.id






###################################################
class Rectangle(Rect):
    def __init__(self, type=None, x=None, y=None, width=None, height=None, name=None, Schar=None, Echar=None,hier_level=None,Netid=None,rotate_angle=None):
        '''

        Args:
            type: type of each component: Trace=Type_1, MOS= Type_2, Lead=Type_3, Diode=Type_4
            x: bottom left corner x coordinate of a rectangle
            y: bottom left corner y coordinate of a rectangle
            width: width of a rectangle
            height: height of a rectangle
            Netid: id of net, in which component is connected to
            name: component path_id (from sym_layout object)
            Schar: Starting character of each input line for input processing:'/'
            Echar: Ending character of each input line for input processing: '/'
        '''
        # inheritence member variables

        self.type=type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.Schar = Schar
        self.Echar = Echar
        self.Netid = Netid
        self.name = name
        self.hier_level=hier_level
        self.rotate_angle=rotate_angle # to handle rotation of components ):0 degree, 1:90 degree, 2:180 degree, 3:270 degree

        Rect.__init__(self, top=self.y + self.height, bottom=self.y, left=self.x, right=self.x + self.width)


    def __str__(self):
        return 'x: '+str(self.x) + ', y: ' + str(self.y) + ', w: ' + str(self.width) + ', h: ' + str(self.height)

    def __repr__(self):
        return self.__str__()
    def contains(self, b):
        return not (self.x1 > b.x2 or b.x1 > self.x2 or b.y1 > self.y2 or self.y1 > b.y2)

    def getParent(self):
        return self.parent

    def print_rectangle(self):
        print "Schar:",self.Schar,"Type",self.type, "x",self.x, "y",self.y,"width",self.width,"height",self.height,"name",self.name,"Echar:",self.Echar
        if self.hier_level!=None:
            print"hier_level:",self.hier_level
        if self.rotate_angle!=None:
            print"rotate_angle:",self.rotate_angle
        if self.Netid!=None:
            print self.Netid


class Baseplate():
    def __init__(self,w,h,type):
        '''

        Args:
            w: Initial layout width (Background Tile)
            h: Initial layout height (Background Tile)
            type: type of Background Tile
        '''
        self.w=w
        self.h=h
        self.type=type
        self.Initialize()


    # defining root tile of the tree
    def Initialize(self):
        Tile1 = Tile(None, None, None, None, None, Cell(0, 0, self.type), nodeId=1)
        TN = Tile(None, None, None, None, None, Cell(0, self.h, None))
        TE = Tile(None, None, None, None, None, Cell(self.w, 0, None))
        TW = Tile(None, None, None, None, None, Cell(-1000, 0, None))
        TS = Tile(None, None, None, None, None, Cell(0, -1000, None))
        Tile1.NORTH = TN
        Tile1.EAST = TE
        Tile1.WEST = TW
        Tile1.SOUTH = TS
        Boundaries = []
        Stitchlist = []
        Stitchlist.append(Tile1)
        Boundaries.append(TN)
        Boundaries.append(TE)
        Boundaries.append(TW)
        Boundaries.append(TS)
        Vnode0 = Vnode(boundaries=Boundaries,stitchList=Stitchlist, parent=None, id=1)
        Tile2 = Tile(None, None, None, None, None, Cell(0, 0, self.type), nodeId=1)
        TN2 = Tile(None, None, None, None, None, Cell(0, self.h, None))
        TE2 = Tile(None, None, None, None, None, Cell(self.w, 0, None))
        TW2 = Tile(None, None, None, None, None, Cell(-1000, 0, None))
        TS2 = Tile(None, None, None, None, None, Cell(0, -1000, None))
        Tile2.NORTH = TN2
        Tile2.EAST = TE2
        Tile2.WEST = TW2
        Tile2.SOUTH = TS2
        Boundaries_H = []
        Stitchlist_H = []
        Stitchlist_H.append(Tile2)
        Boundaries_H.append(TN2)
        Boundaries_H.append(TE2)
        Boundaries_H.append(TW2)
        Boundaries_H.append(TS2)
        Hnode0 = Hnode(boundaries=Boundaries_H,stitchList=Stitchlist_H, parent=None, id=1)
        return Hnode0, Vnode0


class CornerStitch():
    '''
    Initial corner-stitched layout creation
    '''
    def __init__(self):

        self.level=None


    def read_input(self,input_mode,testfile=None,Rect_list=None):
        if input_mode=='file':
            f = open(testfile, "rb")  # opening file in binary read mode
            index_of_dot = testfile.rindex('.')  # finding the index of (.) in path

            testbase = os.path.basename(testfile[:index_of_dot])  # extracting basename from path
            testdir = os.path.dirname(testfile)  # returns the directory name of file
            Input = []

            i = 0
            for line in f.read().splitlines():  # considering each line in file

                c = line.split(',')  # splitting each line with (,) and inserting each string in c

                if len(c) > 4:
                    In = line.split(',')
                    Input.append(In)
        elif input_mode=='list':
            Modified_input=[]

            for i in range(len(Rect_list)):
                R=Rect_list[i]
                if R.hier_level==0:
                   Modified_input.append([R.Schar,R.x,R.y,R.width,R.height,R.type,R.Echar,R.name,R.rotate_angle])
                elif R.hier_level==1:
                    Modified_input.append([R.Schar,'.', R.x, R.y, R.width, R.height, R.type, R.Echar, R.name,R.rotate_angle])
                elif R.hier_level==2:
                    Modified_input.append([R.Schar,'.','.', R.x, R.y, R.width, R.height, R.type, R.Echar, R.name,R.rotate_angle])

        #print "M", Modified_input
        return Modified_input


    # function to generate initial layout
    def draw_layout(self,rects=None,Htree=None,Vtree=None):
        colors = ['green', 'red', 'blue', 'yellow','purple', 'pink','magenta','orange','violet']
        type = ['Type_1', 'Type_2', 'Type_3', 'Type_4','Type_5','Type_6','Type_7','Type_8','Type_9']
        #zorders = [1,2,3,4,5]
        Patches={}

        for r in rects:
            i = type.index(r.type)
            #print i,r.name
            P=matplotlib.patches.Rectangle(
                    (r.x, r.y),  # (x,y)
                    r.width,  # width
                    r.height,  # height
                    facecolor=colors[i],
                    alpha=0.5,
                    #zorder=zorders[i],
                    edgecolor='black',
                    linewidth=1,
                )
            Patches[r.name]=P
        CG = constraintGraph()
        ZDL_H, ZDL_V = constraintGraph.dimListFromLayer(CG, Htree.hNodeList[0], Vtree.vNodeList[0])
        ZDL = []
        for rect in rects:

            ZDL.append((rect.x, rect.y))
            ZDL.append((rect.x + rect.width, rect.y))
            ZDL.append((rect.x, rect.y + rect.height))
            ZDL.append((rect.x + rect.width, rect.y + rect.height))
        #print len(ZDL)
        ZDL_UP=[]
        for i in ZDL:
            if i[0]in ZDL_H or i[1] in ZDL_V:
                if i[0] in ZDL_H:
                    ZDL_H.remove(i[0])
                elif i[1]in ZDL_V:
                    ZDL_V.remove(i[1])
                ZDL_UP.append(i)


        G = nx.Graph()
        Nodes = {}
        id = 1
        lbls = {}

        for i in ZDL_UP:
            if i not in Nodes.values():
                Nodes[id] = (i)

                G.add_node(id, pos=i)
                lbls[id] = str(id)
                id += 1


        pos = nx.get_node_attributes(G, 'pos')
        Graph = [G, pos, lbls]

        return Patches,Graph



    # input tile coordinates and type are passed to create corner stitched layout
    def input_processing(self,Input,Base_W,Base_H):
        """

        Input: Input Rectangles in the form: '/',x,y,width,height,type,'/'
        Base_W: Baseplate Width
        Base_H: Baseplate Height
        :return: Corner stitched layout
        """

        Baseplate1 = Baseplate(Base_W, Base_H, "EMPTY")
        Hnode0, Vnode0 = Baseplate1.Initialize()
        Htree = Tree(hNodeList=[Hnode0], vNodeList=None)
        Vtree = Tree(hNodeList=None, vNodeList=[Vnode0])

        while (len(Input) > 0):
            inp=Input.pop(0)


            #print "H",inp
            if inp[1] == "." and inp[2] != ".": ## determining hierarchy level (2nd level):Device insertion
                start = inp[0]
                x1 = int(inp[2])
                y1 = int(inp[3]) + int(inp[5])
                x2 = int(inp[2]) + int(inp[4])
                y2 = int(inp[3])
                for i in reversed(Htree.hNodeList):
                    if i.parent.id == 1:
                        # print"ID", i.id
                        ParentH = i
                        break
                CHILDH = ParentH
                CHILDH.insert(start, x1,y1,x2,y2, inp[6], inp[7],Htree,ParentH,rotate_angle=inp[-1]) #rotate_angle=inp[-1]

                for i in reversed(Vtree.vNodeList):
                    if i.parent.id == 1:
                        # print"ID", i.id
                        Parent = i
                        break
                CHILD = Parent
                CHILD.insert(start, x1,y1,x2,y2, inp[6], inp[7],Vtree,Parent,rotate_angle=inp[-1])

            if inp[1] == "." and inp[2] == ".":##determining hierarchy level (3rd level):Pin insertion

                start = inp[0]
                x1 = int(inp[3])
                y1 = int(inp[4]) + int(inp[6])
                x2 = int(inp[3]) + int(inp[5])
                y2 = int(inp[4])
                for i in reversed(Htree.hNodeList):
                    if i.parent.id == 1:

                        med = i
                        break

                ParentH = med.child[-1]
                CHILDH = ParentH

                #print x1, y1, x2, y2
                CHILDH.insert(start,x1,y1,x2,y2, inp[7], inp[8],Htree,ParentH,rotate_angle=inp[-1])

                for i in reversed(Vtree.vNodeList):
                    if i.parent.id == 1:

                        med = i
                        break

                Parent = med.child[-1]
                CHILD = Parent

                CHILD.insert(start, x1,y1,x2,y2, inp[7], inp[8],Vtree,Parent,rotate_angle=inp[-1])

            if inp[1] != ".":#determining hierarchy level (1st level):Tile insertion

                start = inp[0]
                Parent = Vtree.vNodeList[0]

                x1 = int(inp[1])
                y1 = int(inp[2]) + int(inp[4])
                x2 = int(inp[1]) + int(inp[3])
                y2 = int(inp[2])

                Parent.insert(start, x1, y1, x2, y2, inp[5],inp[6],Vtree,Parent,rotate_angle=inp[-1])


                ParentH = Htree.hNodeList[0]

                x1 = int(inp[1])
                y1 = int(inp[2]) + int(inp[4])
                x2 = int(inp[1]) + int(inp[3])
                y2 = int(inp[2])

                ParentH.insert(start, x1, y1, x2, y2, inp[5],inp[6],Htree,ParentH,rotate_angle=inp[-1])

        Htree.setNodeId1(Htree.hNodeList)
        Vtree.setNodeId1(Vtree.vNodeList)

        '''
        print "Horizontal NodeList"

        for i in Htree.hNodeList:

            print i.id, i, len(i.stitchList)
            rectlist=[]
            # i=Htree.hNodeList[0]
            if len(i.child)>0:
                for j in i.stitchList:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.bw, j.name
                    rectlist.append(k)
                fig,ax=plt.subplots()
                draw_rect_list_cs(rectlist,ax=ax,x_max=57,y_max=51)

        for i in Vtree.vNodeList:

            print i.id, i, len(i.stitchList)
            rectlist=[]
            # i=Htree.hNodeList[0]
            if len(i.child)>0:
                for j in i.stitchList:
                    k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.bw, j.name
                    rectlist.append(k)
                fig,ax=plt.subplots()
                draw_rect_list_cs(rectlist,ax=ax,x_max=57,y_max=51)
        
        for i in Htree.hNodeList:

            print i.id, i, len(i.stitchList)

            # i=Htree.hNodeList[0]
            for j in i.stitchList:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId, j.bw, j.name
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

        
        '''





        return Htree, Vtree

# creating constraint graph from corner-stitched layout
class CS_to_CG():
    def __init__(self,level):
        '''
        Args:
            level: Mode of operation
        '''
        self.level=level

    def getConstraints(self,constraint_file,sigs=3):
        '''
        :param constraint_file: data frame for constraints
        :param sigs: multiplier of significant digits (converts float to integer)
        :return: set up constraint values for layout engine
        '''
        mult = 10** sigs
        #print "layout multiplier", mult
        data = constraint_file

        Types=len(data.columns)

        SP = []
        EN = []
        width = [int(math.floor(float(w)* mult)) for w in ((data.iloc[0, 1:]).values.tolist())]
        height = [int(math.floor(float(h) * mult)) for h in ((data.iloc[1, 1:]).values.tolist())]
        extension = [int(math.floor(float(ext) * mult)) for ext in ((data.iloc[2, 1:]).values.tolist())]


        for j in range(len(data)):
            if j >3 and j < (3+Types):
                SP1 = [int(math.floor(float(spa) * mult)) for spa in (data.iloc[j, 1:(Types)]).values.tolist()]
                SP.append(SP1)

            elif j > (3+Types) and j < (3+2*Types):
                EN1 = [int(math.floor(float(enc) * mult)) for enc in (data.iloc[j, 1:(Types)]).values.tolist()]
                EN.append(EN1)

            else:
                continue


        minWidth = map(int, width)
        minExtension = map(int, extension)
        minHeight = map(int, height)
        minSpacing = [map(int, i) for i in SP]
        minEnclosure = [map(int, i) for i in EN]
        #print minWidth
        #print minExtension
        #print minHeight
        #print minSpacing
        #print minEnclosure
        CONSTRAINT = ct.constraint()
        CONSTRAINT.setupMinWidth(minWidth)
        CONSTRAINT.setupMinHeight(minHeight)
        CONSTRAINT.setupMinExtension(minExtension)
        CONSTRAINT.setupMinSpacing(minSpacing)
        CONSTRAINT.setupMinEnclosure(minEnclosure)

        start_v = None
        end_v = None
        start_c = None
        end_c = None
        for index,row in data.iterrows():
            if row[0]=='Voltage Difference':
                start_v=index+1
            elif row[0]=='Current Rating':
                end_v=index-1
                start_c=index+1
            if index==len(data)-1:
                end_c=index

        if start_v!=None and end_v!=None:
            voltage_constraints=[]
            current_constraints=[]
            for index, row in data.iterrows():
                if index in range(start_v, end_v + 1):
                    voltage_constraints.append([float(row[0]),float(row[1])*mult]) # voltage rating,minimum spacing
                if index in range(start_c,end_c + 1):
                    current_constraints.append([float(row[0]), float(row[1])*mult]) #current rating,minimum width

            CONSTRAINT.setup_I_V_constraints(voltage_constraints,current_constraints)


        


    def Sym_to_CS(self,Input_rects, Htree, Vtree):
        '''

        Args:
            Input_rects: Modified input rectangles from symbolic layout
            Htree: Horizontal CS tree
            Vtree: Vertical CS tree

        Returns:Mapped rectangles from CS to Sym {T1:[[R1],[R2],....],T2:[....]}

        '''
        ALL_RECTS = {}
        DIM = []

        for j in Htree.hNodeList[0].stitchList:

            p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
            DIM.append(p)
        ALL_RECTS['H'] = DIM
        DIM = []
        for j in Vtree.vNodeList[0].stitchList:
            p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
            DIM.append(p)
        ALL_RECTS['V'] = DIM

        SYM_CS = {}
        for rect in Input_rects:
            x1 = rect.x
            y1 = rect.y
            x2 = rect.x + rect.width
            y2 = rect.y + rect.height
            type = rect.type
            name = rect.name
            for k, v in ALL_RECTS.items():
                if k == 'H':
                    key = name
                    SYM_CS.setdefault(key, [])
                    for i in v:
                        if i[0] >= x1 and i[1] >= y1 and i[0] + i[2] <= x2 and i[1] + i[3] <= y2 and i[4] == type:
                            SYM_CS[key].append(i)
                        else:
                            continue
        return SYM_CS

    ## Evaluates constraint graph depending on modes of operation
    def evaluation(self,Htree,Vtree,bondwires,N,cs_islands,W,H,XLoc,YLoc,seed,individual,Types,rel_cons,flexible):
        '''
        :param Htree: Horizontal tree
        :param Vtree: Vertical tree
        :param N: No. of layouts to be generated
        :param W: Width of floorplan
        :param H: Height of floorplan
        :param XLoc: Location of horizontal nodes
        :param YLoc: Location of vertical nodes
        :return: Updated x,y locations of nodes
        '''
        if self.level==1:
            CG = constraintGraph( W=None, H=None,XLocation=None, YLocation=None)
            CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList,bondwires,self.level,cs_islands, N,seed,individual,Types=Types,flexible=flexible,rel_cons=rel_cons)
        elif self.level==2 or self.level==3:
            if W==None or H ==None:
                print"Please enter Width and Height of the floorplan"
            if N==None:
                print"Please enter Number of layouts to be generated"
            else:
                CG = constraintGraph(W, H, XLoc, YLoc)
                CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList,bondwires, self.level,cs_islands,N,seed,individual,Types=Types,flexible=flexible,rel_cons=rel_cons)
        else:

            CG = constraintGraph( W=None, H=None,XLocation=None, YLocation=None)
            CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList,bondwires, self.level,cs_islands,Types=Types,flexible=flexible,rel_cons=rel_cons)
        MIN_X, MIN_Y = CG.minValueCalculation(Htree.hNodeList, Vtree.vNodeList, self.level)
        return MIN_X, MIN_Y
        '''
        if self.level == 0:

            R = self.UPDATE_min(MIN_X, MIN_Y, Htree, Vtree)
            Results = []
            for i in R:
                Rectangles = {}
                for k, v in i.items():
                    # print"Size", k, len(v)
                    key = k
                    Rectangles.setdefault(key, [])
                    val = []
                    value = {}
                    for rect in v:
                        # print "N",rect.name

                        value[rect.name] = [rect.top, rect.bottom, rect.left, rect.right]
                        # val.append(value)

                        # rect.print_rect()
                    Rectangles[key].append(value)
                Results.append(Rectangles)

        else:


            DIM_H = {}

            keys = MIN_X[0].keys()
            # print keys
            for i in range(len(keys)):
                key = keys[i]
                for k in range(len(Htree.hNodeList)):
                    if Htree.hNodeList[k].id == key:

                        coord = []
                        for j in Htree.hNodeList[k].stitchList:
                            x_y = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y, j.name, j.cell.type,j.nodeId]
                            coord.append(x_y)

                DIM_H[key] = coord
            # print"DIM", DIM_H
            DIM_V = {}
            keysv = MIN_Y[0].keys()
            # print keys
            for i in range(len(keysv)):
                key = keysv[i]
                for k in range(len(Vtree.vNodeList)):
                    if Vtree.vNodeList[k].id == key:
                        coord = []
                        for j in Vtree.vNodeList[k].stitchList:
                            x_y = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y, j.name, j.cell.type,j.nodeId]
                            coord.append(x_y)
                DIM_V[key] = coord
            # print"DIM", DIM_V

            floorplan_results = []
            for i in range(len(MIN_X)):
                # print MIN_X[i],MIN_Y[i]

                MINX = collections.OrderedDict(sorted(MIN_X[i].items()))
                MINY = collections.OrderedDict(sorted(MIN_Y[i].items()))

                HCS, VCS, HCS1, VCS1 = self.UPDATED_Location(MINX, MINY, DIM_H, DIM_V)

            Results = []

            for i in HCS:  # need to double check
                Rectangles = {}
                for k, v in i.items():
                    # print"Size", k, len(v)
                    key = k
                    Rectangles.setdefault(key, [])
                    val = []
                    value = {}
                    for rect in v:
                        # print "N",rect.name

                        value[rect.name] = [rect.top, rect.bottom, rect.left, rect.right]
                        # val.append(value)

                        # rect.print_rect()
                    Rectangles[key].append(value)
                Results.append(Rectangles)

        return Results
        '''


    def update_min_hv(self,minx,miny,Htree,Vtree,sym_to_cs,s=1000.0):
        all_init_rects_h = []
        all_init_rects_v= []
        #print "h", sym_to_cs
        length=len(sym_to_cs['H'])
        sym_to_cs_h=sym_to_cs['H']
        sym_to_cs_v=sym_to_cs['V']
        #print length
        #print "h",sym_to_cs_h
        #print "v",sym_to_cs_v
        #cs_sym_info = [0 for i in range(len(length))]
        cs_sym_info_h=[0 for i in range(length)]
        cs_sym_info_v=[0 for i in range(length)]

        for i in range(len(sym_to_cs_h)):
            for k, v in sym_to_cs_h[i].items():
                rect = v[0]
                if rect.parent_name == None:
                    init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                 rect.cell.type, rect.name, rect.parent_name]
                    all_init_rects_h.append(init_rect)
                    cs_sym_info_h[i] = {k: [init_rect, v[1]]}

        for i in range(len(sym_to_cs_h)):
            for k, v in sym_to_cs_h[i].items():
                rect = v[0]
                if rect.parent_name != None:
                    parent = rect.parent_name
                    for j in range(len(sym_to_cs_h)):
                        for k1, v1 in sym_to_cs_h[j].items():
                            rect1 = v1[0]

                            if rect1.name == parent:
                                nodeId = rect1.nodeId
                                init_rect = [nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                             rect.cell.type, rect.name, rect.parent_name]
                                all_init_rects_h.append(init_rect)
                                cs_sym_info_h[i] = {k: [init_rect, v[1]]}
                            else:
                                continue
                                # break
        for i in range(len(sym_to_cs_v)):
            for k, v in sym_to_cs_v[i].items():
                rect = v[0]
                if rect.parent_name == None:
                    init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                 rect.cell.type, rect.name, rect.parent_name]
                    all_init_rects_v.append(init_rect)
                    cs_sym_info_v[i] = {k: [init_rect, v[1]]}

        for i in range(len(sym_to_cs_v)):
            for k, v in sym_to_cs_v[i].items():
                rect = v[0]
                if rect.parent_name != None:
                    parent = rect.parent_name
                    for j in range(len(sym_to_cs_v)):
                        for k1, v1 in sym_to_cs_v[j].items():
                            rect1 = v1[0]

                            if rect1.name == parent:
                                nodeId = rect1.nodeId
                                init_rect = [nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                             rect.cell.type, rect.name, rect.parent_name]
                                all_init_rects_v.append(init_rect)
                                cs_sym_info_v[i] = {k: [init_rect, v[1]]}
                            else:
                                continue


        for rect in Htree.hNodeList[0].stitchList:
            if rect.cell.type == "EMPTY" and (
                    rect.WEST in Htree.hNodeList[0].boundaries or rect.NORTH in Htree.hNodeList[
                0].boundaries or rect.SOUTH in Htree.hNodeList[0].boundaries or rect.EAST in Htree.hNodeList[
                        0].boundaries):
                rect.name = "EMPTY"
                init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y, rect.cell.type,
                             rect.name, rect.parent_name]
                all_init_rects_h.append(init_rect)
                cs_sym_info_h[i] = {k: [init_rect, v[1]]}

        for rect in Vtree.vNodeList[0].stitchList:
            if rect.cell.type == "EMPTY" and (
                    rect.WEST in Htree.hNodeList[0].boundaries or rect.NORTH in Htree.hNodeList[
                0].boundaries or rect.SOUTH in Htree.hNodeList[0].boundaries or rect.EAST in Htree.hNodeList[
                        0].boundaries):
                rect.name = "EMPTY"
                init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y, rect.cell.type,
                             rect.name, rect.parent_name]
                all_init_rects_v.append(init_rect)
                cs_sym_info_v[i] = {k: [init_rect, v[1]]}

        minx_nodes = minx.keys()
        all_layout_rects= {}
        #all_layout_rects_v = {}
        layout_rects_h = []
        layout_rects_v=[]
        new_rects_h = {}
        new_rects_v={}
        for i in range(len(all_init_rects_h)):
            rect = all_init_rects_h[i]
            if rect[0] in minx and rect[0] in miny and rect[1] in minx and rect[2] in miny:
                node = rect[0]
                x = minx[node][rect[1]]
                y = miny[node][rect[2]]
                w = minx[node][rect[3]] - minx[node][rect[1]]
                h = miny[node][rect[4]] - miny[node][rect[2]]
                type = rect[5]
                name = rect[6]
                new_rect = [x / s, y / s, w / s, h / s, type]
                layout_rects_h.append(new_rect)
                new_rects_h[name] = [node, x, y, w, h, type, rect[7]]
            else:
                for k in ((minx_nodes)):
                    # print minx[k],miny[k]
                    # print rect
                    if rect[1] in minx[k] and rect[2] in miny[k] and rect[3] in minx[k] and rect[4] in miny[k]:
                        node = k
                        x = minx[node][rect[1]]
                        y = miny[node][rect[2]]
                        w = minx[node][rect[3]] - minx[node][rect[1]]
                        h = miny[node][rect[4]] - miny[node][rect[2]]
                        type = rect[5]
                        name = rect[6]
                        new_rect = [x / s, y / s, w / s, h / s, type]
                        layout_rects_h.append(new_rect)
                        new_rects_h[name] = [node, x, y, w, h, type, rect[7]]

        all_layout_rects['H'] = layout_rects_h
        # print "N",new_rects

        for i in range(len(all_init_rects_v)):
            rect = all_init_rects_v[i]
            if rect[0] in minx and rect[0] in miny and rect[1] in minx and rect[2] in miny:
                node = rect[0]
                x = minx[node][rect[1]]
                y = miny[node][rect[2]]
                w = minx[node][rect[3]] - minx[node][rect[1]]
                h = miny[node][rect[4]] - miny[node][rect[2]]
                type = rect[5]
                name = rect[6]
                new_rect = [x / s, y / s, w / s, h / s, type]
                layout_rects_v.append(new_rect)
                new_rects_v[name] = [node, x, y, w, h, type, rect[7]]
            else:
                for k in ((minx_nodes)):
                    # print minx[k],miny[k]
                    # print rect
                    if rect[1] in minx[k] and rect[2] in miny[k] and rect[3] in minx[k] and rect[4] in miny[k]:
                        node = k
                        x = minx[node][rect[1]]
                        y = miny[node][rect[2]]
                        w = minx[node][rect[3]] - minx[node][rect[1]]
                        h = miny[node][rect[4]] - miny[node][rect[2]]
                        type = rect[5]
                        name = rect[6]
                        new_rect = [x / s, y / s, w / s, h / s, type]
                        layout_rects_v.append(new_rect)
                        new_rects_v[name] = [node, x, y, w, h, type, rect[7]]

        all_layout_rects['V'] = layout_rects_v



        for i in range(len(cs_sym_info_h)):

            comp = cs_sym_info_h[i]
            for k, v in comp.items():
                if v[1] == None:
                    v[0] = new_rects_h[k]
                    v[1] = None
                else:
                    v[0] = new_rects_h[k]

                    stitchList = []
                    for rect in v[1].stitchList:

                        init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                     rect.cell.type]

                        if init_rect[0] in minx and init_rect[0] in miny:
                            node = init_rect[0]
                            x = minx[node][init_rect[1]]
                            y = miny[node][init_rect[2]]
                            w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                            h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                            type = init_rect[5]

                            new_rect = Rectangle(x=x, y=y, width=w, height=h, type=type)
                            stitchList.append(new_rect)
                        else:
                            for k in ((minx_nodes)):
                                if init_rect[1] in minx[k] and init_rect[2] in miny[k] and init_rect[3] in minx[k] and \
                                        init_rect[4] in miny[k]:
                                    node = k
                                    x = minx[node][init_rect[1]]
                                    y = miny[node][init_rect[2]]
                                    w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                                    h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                                    type = init_rect[5]
                                    new_rect = Rectangle(x=x, y=y, width=w, height=h, type=type)
                                    stitchList.append(new_rect)

                    v[1] = stitchList


        for i in range(len(cs_sym_info_v)):
            print cs_sym_info_v
            comp = cs_sym_info_v[i]
            print comp
            for k, v in comp.items():
                if v[1] == None:
                    v[0] = new_rects_v[k]
                    v[1] = None
                else:
                    v[0] = new_rects_v[k]

                    stitchList = []
                    for rect in v[1].stitchList:

                        init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                     rect.cell.type]

                        if init_rect[0] in minx and init_rect[0] in miny:
                            node = init_rect[0]
                            x = minx[node][init_rect[1]]
                            y = miny[node][init_rect[2]]
                            w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                            h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                            type = init_rect[5]

                            new_rect = Rectangle(x=x, y=y, width=w, height=h, type=type)
                            stitchList.append(new_rect)
                        else:
                            for k in ((minx_nodes)):
                                if init_rect[1] in minx[k] and init_rect[2] in miny[k] and init_rect[3] in minx[k] and \
                                        init_rect[4] in miny[k]:
                                    node = k
                                    x = minx[node][init_rect[1]]
                                    y = miny[node][init_rect[2]]
                                    w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                                    h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                                    type = init_rect[5]
                                    new_rect = Rectangle(x=x, y=y, width=w, height=h, type=type)
                                    stitchList.append(new_rect)

                    v[1] = stitchList

        # print all_layout_rects
        # print cs_sym_info
        cs_sym_info={}
        cs_sym_info['H']=cs_sym_info_h
        cs_sym_info['V']=cs_sym_info_v
        #print cs_sym_info
        return cs_sym_info, all_layout_rects






    """
    
    # without island implementation
    def update_min(self,minx,miny,Htree,sym_to_cs,s=1000.0):
    '''

    :param minx: Evaluated minimum x coordinates
    :param miny: Evaluated minimum y coordinates
    :param sym_to_cs: initial input to initial cornerstitch mapped information
    :param s: divider
    :return:
    '''

    all_init_rects=[]
    cs_sym_info=[0 for i in range(len(sym_to_cs))]
    for i in range(len(sym_to_cs)):
        for k,v in sym_to_cs[i].items():
            rect=v[0]
            if rect.parent_name==None:
                init_rect=[rect.nodeId,rect.cell.x,rect.cell.y,rect.EAST.cell.x,rect.NORTH.cell.y,rect.cell.type,rect.name,rect.parent_name]
                all_init_rects.append(init_rect)
                cs_sym_info[i] = {k: [init_rect, v[1]]}

    for i in range(len(sym_to_cs)):
        for k, v in sym_to_cs[i].items():
            rect = v[0]
            if rect.parent_name!=None:
                parent = rect.parent_name
                for j in range(len(sym_to_cs)):
                    for k1, v1 in sym_to_cs[j].items():
                        rect1=v1[0]

                        if rect1.name==parent:
                            nodeId=rect1.nodeId
                            init_rect = [nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                         rect.cell.type, rect.name, rect.parent_name]
                            all_init_rects.append(init_rect)
                            cs_sym_info[i] = {k: [init_rect, v[1]]}
                        else:
                            continue
                            #break

    for rect in Htree.hNodeList[0].stitchList:
        if rect.cell.type=="EMPTY" and (rect.WEST in Htree.hNodeList[0].boundaries or rect.NORTH in Htree.hNodeList[0].boundaries or rect.SOUTH in Htree.hNodeList[0].boundaries or rect.EAST in Htree.hNodeList[0].boundaries):
            rect.name="EMPTY"
            init_rect=[rect.nodeId,rect.cell.x,rect.cell.y,rect.EAST.cell.x,rect.NORTH.cell.y,rect.cell.type,rect.name,rect.parent_name]
            all_init_rects.append(init_rect)
            cs_sym_info[i] = {k: [init_rect, v[1]]}




    minx_nodes=minx.keys()
    all_layout_rects={}
    layout_rects=[]
    new_rects={}
    for i in range(len(all_init_rects)):
        rect=all_init_rects[i]
        if rect[0] in minx and rect[0] in miny and rect[1] in minx and rect[2] in miny:
            node=rect[0]
            x=minx[node][rect[1]]
            y=miny[node][rect[2]]
            w=minx[node][rect[3]] - minx[node][rect[1]]
            h=miny[node][rect[4]] - miny[node][rect[2]]
            type=rect[5]
            name=rect[6]
            new_rect=[x/s,y/s,w/s,h/s,type]
            layout_rects.append(new_rect)
            new_rects[name]=[node,x,y,w,h,type,rect[7]]
        else:
            for k in ((minx_nodes)):
                #print minx[k],miny[k]
                #print rect
                if rect[1] in minx[k] and rect[2] in miny[k] and rect[3] in minx[k] and rect[4] in miny[k]:
                    node=k
                    x = minx[node][rect[1]]
                    y = miny[node][rect[2]]
                    w = minx[node][rect[3]] - minx[node][rect[1]]
                    h = miny[node][rect[4]] - miny[node][rect[2]]
                    type = rect[5]
                    name = rect[6]
                    new_rect = [x/s, y/s, w/s, h/s, type]
                    layout_rects.append(new_rect)
                    new_rects[name] = [node, x, y, w, h, type, rect[7]]



    all_layout_rects['H']=layout_rects
    #print "N",new_rects
    for i in range(len(cs_sym_info)):

        comp=cs_sym_info[i]
        for k,v in comp.items():
            if v[1]==None:
                v[0]=new_rects[k]
                v[1]=None
            else:
                v[0] = new_rects[k]

                stitchList = []
                for rect in v[1].stitchList:

                    init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y,
                                 rect.cell.type]

                    if init_rect[0] in minx and init_rect[0] in miny:
                        node=init_rect[0]
                        x = minx[node][init_rect[1]]
                        y = miny[node][init_rect[2]]
                        w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                        h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                        type = init_rect[5]

                        new_rect=Rectangle(x=x,y=y,width=w,height=h,type=type)
                        stitchList.append(new_rect)
                    else:
                        for k in ((minx_nodes)):
                            if init_rect[1] in minx[k] and init_rect[2] in miny[k] and init_rect[3] in minx[k] and init_rect[4] in miny[k]:
                                node = k
                                x = minx[node][init_rect[1]]
                                y = miny[node][init_rect[2]]
                                w = minx[node][init_rect[3]] - minx[node][init_rect[1]]
                                h = miny[node][init_rect[4]] - miny[node][init_rect[2]]
                                type = init_rect[5]
                                new_rect = Rectangle(x=x, y=y, width=w, height=h, type=type)
                                stitchList.append(new_rect)

                v[1]=stitchList



    #print all_layout_rects
    #print cs_sym_info
    return cs_sym_info,all_layout_rects








    """
    def final_merge(self,node,h=False):
        if h==True:
            Hnode.Final_Merge(node)
        else:
            Vnode.Final_Merge(node)


    def update_min(self,minx,miny,sym_to_cs,bondwires,s=1000.0):
        '''

        :param minx: Evaluated minimum x coordinates
        :param miny: Evaluated minimum y coordinates
        :param sym_to_cs: initial input to initial cornerstitch mapped information
        :param s: divider
        :return:
        '''


        layout_rects=[]
        cs_sym_info={}

        sub_width=max(minx[1].values())
        sub_length=max(miny[1].values())
        updated_wires=[]
        if bondwires!=None:
            for wire in bondwires:
                #wire2=BondingWires()
                if wire.source_node_id!=None and wire.dest_node_id!=None:
                    wire2=copy.deepcopy(wire)
                    ##print wire.source_coordinate
                    #print wire.dest_coordinate
                    if wire.source_node_id in minx and wire.dest_node_id in minx:
                        wire2.source_coordinate[0]=minx[wire.source_node_id][wire.source_coordinate[0]]
                        wire2.dest_coordinate[0] = minx[wire.dest_node_id][wire.dest_coordinate[0]]
                    if wire.source_node_id in miny and wire.dest_node_id in miny:
                        wire2.source_coordinate[1]=miny[wire.source_node_id][wire.source_coordinate[1]]
                        wire2.dest_coordinate[1] = miny[wire.dest_node_id][wire.dest_coordinate[1]]
                    #print"A", wire2.source_coordinate
                    #print"AD", wire2.dest_coordinate
                    updated_wires.append(wire2)
                    wire_1=[wire2.source_coordinate[0]/float(s),wire2.source_coordinate[1]/float(s),0.5,0.5,"Type_3",3,0]
                    wire_2 = [wire2.dest_coordinate[0]/float(s), wire2.dest_coordinate[1]/float(s), 0.5, 0.5, "Type_3", 3, 0]
                    if wire_1[0]<wire_2[0]:
                        x=wire_1[0]
                    else:
                        x=wire_2[0]
                    if wire_1[1]<wire_2[1]:
                        y=wire_1[1]
                    else:
                        y = wire_2[1]
                    #wire=[x,y,abs(wire_2[1]-wire_1[1]),abs(wire_2[2]-wire_1[2]),wire_1[-2],wire_1[-1]]
                    wire=[wire_1[0],wire_1[1],wire_2[0],wire_2[1],wire_1[-3],wire_1[-2]]#xA,yA,xB,yB,type,zorder
                    #print "final_wire", wire
                    #layout_rects.append(wire_1)
                    #layout_rects.append(wire_2)
                    layout_rects.append(wire)

            #for k, v in sym_to_cs.items():
                #print k,v

            #raw_input()


        for k, v in sym_to_cs.items():

            coordinates=v[0] # x1,y1,x2,y2 (bottom left and top right)
            left=coordinates[0]
            bottom=coordinates[1]
            right=coordinates[2]
            top=coordinates[3]
            nodeids = v[1]
            type=v[2]
            hier_level=v[3]
            rotation_index=v[4]
            #print "UP",k,rect.cell.x,rect.cell.y,rect.EAST.cell.x,rect.NORTH.cell.y
            for nodeid in nodeids:
                if left in minx[nodeid] and bottom in miny[nodeid] and top in miny[nodeid] and right in minx[nodeid]:
                    x = minx[nodeid][left]
                    y = miny[nodeid][bottom]
                    w = minx[nodeid][right] - minx[nodeid][left]
                    h = miny[nodeid][top] - miny[nodeid][bottom]
                    break
                else:
                    continue

            name = k
            #print x,y,w,h
            new_rect = [float(x) / s, float(y) / s, float(w) / s, float(h) / s, type,hier_level+1,rotation_index]
            #print "NN",new_rect,name
            layout_rects.append(new_rect)
            cs_sym_info[name]=[type,x,y,w,h]

        for wire in updated_wires:
            if wire.dest_comp[0]=='B':
                x=wire.dest_coordinate[0]
                y=wire.dest_coordinate[1]
                w=1
                h=1
                name=wire.dest_comp
                type=wire.cs_type
                cs_sym_info[name] = [type, x, y, w, h]
            if wire.source_comp[0]=='B':
                x=wire.source_coordinate[0]
                y=wire.source_coordinate[1]
                w=1
                h=1
                name=wire.source_comp
                type=wire.cs_type
                cs_sym_info[name] = [type, x, y, w, h]



        substrate_rect = ["EMPTY",0,0,sub_width,sub_length]
        cs_sym_info['Substrate'] = substrate_rect
        new_rect = [0, 0, float(sub_width)/s, float(sub_length) / s, "EMPTY", 0,0] # z_order,rotation_index
        layout_rects.append(new_rect)


        return cs_sym_info,layout_rects


    def update(self,minx,miny,Htree,sym_to_cs,s=1000):

        all_init_rects = []
        cs_sym_info = [0 for i in range(len(sym_to_cs))]
        for i in range(len(sym_to_cs)):
            for k, v in sym_to_cs[i].items():
                rect = v[0]
                init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y, rect.cell.type,
                             rect.name, rect.parent_name]
                all_init_rects.append(init_rect)
                cs_sym_info[i] = {k: [init_rect, v[1]]}

        for rect in Htree.hNodeList[0].stitchList:
            if rect.cell.type == "EMPTY" and (
                    rect.WEST in Htree.hNodeList[0].boundaries or rect.NORTH in Htree.hNodeList[
                0].boundaries or rect.SOUTH in Htree.hNodeList[0].boundaries or rect.EAST in Htree.hNodeList[
                        0].boundaries):
                rect.name = "EMPTY"
                init_rect = [rect.nodeId, rect.cell.x, rect.cell.y, rect.EAST.cell.x, rect.NORTH.cell.y, rect.cell.type,
                             rect.name, rect.parent_name]
                all_init_rects.append(init_rect)
                cs_sym_info[i] = {k: [init_rect, v[1]]}


        all_cs_sym_info=[]
        print len(minx)
        print len(miny)




    def UPDATE_min(self,MINX, MINY,Htree,Vtree,sym_to_cs,s=1000):
        '''

        Args:
            MINX: Evaluated minimum x coordinates
            MINY: Evaluated minimum y coordinates
            Htree: Horizontal CS tree structure
            Vtree: Vertical CS tree structure
            path: path to save figure
            name: name of the figure
            Sym_to_CS: dictionary to map symbolic object to CS

        Returns: Updated Symbolic objects (Minimum sized layout)

        '''
        for node in Htree.hNodeList:
            Hnode.Final_Merge(node)
        for node in Vtree.vNodeList:
            Vnode.Final_Merge(node)
        Recatngles_H = {}
        RET_H = {}

        ALL_HRECTS={}   # used for mapping symbolic layout objects with corner stitch resultant rectangles.
        #s = 1000  # scaler
        for i in Htree.hNodeList:
            if i.child != []:
                Dimensions = []
                DIM = []

                #for d in range(len(i.stitchList)):
                    #j=i.stitchList[d]
                for j in i.stitchList:
                    p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(),j.cell.type, j.nodeId]

                    DIM.append(p)

                    k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y,j.nodeId]


                    if k[0] in MINX[i.id].keys() and k[1] in MINY[i.id].keys() and k[2] in MINX[i.id].keys() and k[3] in \
                            MINY[i.id].keys():
                        rect = [(MINX[i.id][k[0]]), (MINY[i.id][k[1]]), (MINX[i.id][k[2]]) - (MINX[i.id][k[0]]),
                               (MINY[i.id][k[3]]) - (MINY[i.id][k[1]]), j.cell.type,j.nodeId]
                        r1=Rectangle(x=rect[0],y=rect[1],width=rect[2],height=rect[3],type=rect[4],name=j.name)
                        r2 = [float(MINX[i.id][k[0]]) / s, float(MINY[i.id][k[1]]) / s,
                                float(MINX[i.id][k[2]]) / s - float(MINX[i.id][k[0]]) / s,
                                float(MINY[i.id][k[3]]) / s - float(MINY[i.id][k[1]]) / s, j.cell.type,j.nodeId]

                    for k1,v in sym_to_cs[0].items():

                        key=k1
                        #ALL_HRECTS.setdefault(key,[])
                        item=[]
                        for r in v:
                            if isinstance (r, Tile):
                                if r.cell.x==k[0] and r.cell.y==k[1]:
                                    item.append(r1)
                            elif r==None:
                                item.append(None)
                            ALL_HRECTS[key]=item

                    Dimensions.append(r2)


                Recatngles_H[i.id] = Dimensions
                RET_H[i.id] = DIM

        for k1, v in sym_to_cs[0].items():
            for r in v:
                if isinstance(r,Hnode):
                    rects=[]
                    for node in Htree.hNodeList:
                        if r.id==node.id:
                            for j in node.stitchList:
                                k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y, j.nodeId]
                                if k[0] in MINX[i.id].keys() and k[1] in MINY[i.id].keys() and k[2] in MINX[i.id].keys() and k[3] in MINY[i.id].keys():
                                    rect = [(MINX[i.id][k[0]]), (MINY[i.id][k[1]]),
                                            (MINX[i.id][k[2]]) - (MINX[i.id][k[0]]),
                                            (MINY[i.id][k[3]]) - (MINY[i.id][k[1]]), j.cell.type, j.nodeId]
                                    r1 = Rectangle(x=rect[0], y=rect[1], width=rect[2], height=rect[3], type=rect[4])
                                    rects.append(r1)


        Recatngles_V = {}
        RET_V = {}
        for i in Vtree.vNodeList:

            if i.child != []:
                Dimensions = []
                DIM_V = []

                #for d in range(len(i.stitchList)):
                    #j=i.stitchList[d]
                for j in i.stitchList:
                    p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.voltage, j.current, j.cell.type,j.nodeId]
                    DIM_V.append(p)
                    k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y]
                    if k[0] in MINX[i.id].keys() and k[1] in MINY[i.id].keys() and k[2] in MINX[i.id].keys() and k[3] in \
                            MINY[i.id].keys():
                        rect = [float(MINX[i.id][k[0]])/s, float(MINY[i.id][k[1]])/s, float(MINX[i.id][k[2]])/s - float(MINX[i.id][k[0]])/s,
                                float(MINY[i.id][k[3]])/s - float(MINY[i.id][k[1]])/s, j.cell.type,j.nodeId]




                    Dimensions.append(rect)
                Recatngles_V[i.id] = Dimensions
                RET_V[i.id] = DIM_V

        ALL_RECTS = {}

        Recatngles_H = collections.OrderedDict(sorted(Recatngles_H.items()))
        for k, v in Recatngles_H.items():
            ALL_RECTS['H'] = v

        Recatngles_V = collections.OrderedDict(sorted(Recatngles_V.items()))
        for k, v in Recatngles_V.items():
            ALL_RECTS['V'] = v
        return ALL_HRECTS,ALL_RECTS

    def UPDATED_Location(self,MINX, MINY, DIM_H, DIM_V):

        DIM_H_up = {}
        HCS = {}
        VCS = {}
        DIM_V_up = {}

        for k, v in DIM_H.items():

            Rects = []
            Plot_rect = []
            for i in v:
                if i[0] in MINX[k].keys() and i[2] in MINX[k].keys() and i[1] in MINY[k].keys() and i[3] in MINY[k].keys():

                    rect = [MINX[k][i[0]], MINY[k][i[1]], MINX[k][i[2]], MINY[k][i[3]], i[-2], i[-1],i[-4]]
                    rect_to_plot = [rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1],rect[6],rect[4],
                                    rect[5]]  # x,y,width,height

                Rects.append(rect)
                Plot_rect.append(rect_to_plot)
            DIM_H_up[k] = Rects
            HCS[k] = Plot_rect
        # print"UP", DIM_H_up
        for k, v in DIM_V.items():

            Rects = []
            Plot_rect = []
            for i in v:
                if i[0] in MINX[k].keys() and i[2] in MINX[k].keys() and i[1] in MINY[k].keys() and i[3] in MINY[
                    k].keys():
                    '''
                    bw = None
                    if len(i[-3]) > 0:
                        if i[-2] != "Type_1":
                            num_bw = 0
                            for j in i[-3]:
                                if j.num_of_bw > num_bw:
                                    num_bw = j.num_of_bw
                                    bw = j
                    '''
                    bw = None
                    if len(i[-3]) > 0:
                        if i[-2] != "Type_1":
                            bw = []
                            for j in i[-3]:
                                bw.append({(j.name,j.direction,j.num_of_bw):(MINX[k][j.src_coordinate[0]],MINY[k][j.src_coordinate[1]]) })
                    rect = [MINX[k][i[0]], MINY[k][i[1]], MINX[k][i[2]], MINY[k][i[3]], i[-2], i[-1],i[-4]]
                    rect_to_plot = [rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1],rect[6],bw, rect[4],
                                    rect[5]]  # x,y,width,height
                Rects.append(rect)
                Plot_rect.append(rect_to_plot)
            DIM_V_up[k] = Rects
            VCS[k] = Plot_rect
        Total_H = []
        Total_V = []
        # print HCS,VCS
        HCS = collections.OrderedDict(sorted(HCS.items()))
        VCS = collections.OrderedDict(sorted(VCS.items()))
        # print"HCS", HCS
        # print "VCS",VCS
        for k, v in HCS.items():
            Total_H.append(v)
            # plotrectH(k,v,format)

        # print"TOT", Total_H
        for k, v in VCS.items():
            Total_V.append(v)
            # plotrectV(k,v,format)
        return Total_H, Total_V, HCS, VCS





    def UPDATE(self,MINX,MINY,Htree, Vtree, sym_to_cs,s=1000):
        '''

           Args:
               MINX: Evaluated  x coordinates
               MINY: Evaluated  y coordinates
               Htree: Horizontal CS tree structure
               Vtree: Vertical CS tree structure
               Sym_to_CS: dictionary to map symbolic object to CS

           Returns: Updated Symbolic objects (for all modes results except mode 0)

               '''
        MIN_X=MINX.values()[0]
        MIN_Y=MINY.values()[0]
        #print "L",len(MIN_X)
        #print MIN_Y
        DIM = []
        Recatngles_H={}
        key=MINX.keys()[0]
        Recatngles_H.setdefault(key,[])
        ALL_HRECTS = {}  # used for mapping symbolic layout objects with corner stitch resultant rectangles.key=MINX.keys()[0]
        key2='H'
        ALL_HRECTS.setdefault(key2,[])

        #s=1000 #scaler
        for d in range(len(Htree.hNodeList[0].stitchList)):
            j=Htree.hNodeList[0].stitchList[d]
            k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y,j.cell.type,j.nodeId]

            DIM.append(k)

        for i in range(len(MIN_X)):
            Dimensions = []
            UP_Dim={}
            for j in range(len(DIM)):
                k=DIM[j]
                #if k[0] in MIN_X[i].keys() and k[1] in MIN_Y[i].keys() and k[2] in MIN_X[i].keys() and k[3] in MIN_Y[i].keys():
                rect = [MIN_X[i][k[0]], MIN_Y[i][k[1]], MIN_X[i][k[2]] - MIN_X[i][k[0]],MIN_Y[i][k[3]] - MIN_Y[i][k[1]]]
                r1 = Rectangle(type=k[4],x=rect[0], y=rect[1], width=rect[2], height=rect[3])
                #r2 = [float(MIN_X[i][k[0]]) / s, float(MIN_Y[i][k[1]]) / s, float(MIN_X[i][k[2]]) / s - float(MIN_X[i][k[0]]) / s,float(MIN_Y[i][k[3]]) / s - float(MIN_Y[i][k[1]]) / s, k[4]]
                r2=[d/float(s) for d in rect]
                r2.append(k[4])
                for k1,v in sym_to_cs.items():

                    key1=k1
                    UP_Dim.setdefault(key1,[])
                    for r in v:

                        if r[0]==k[0] and r[1]==k[1]:
                            UP_Dim[key1].append(r1)
                Dimensions.append(r2)
                W = max(MIN_X[i].values())
                H = max(MIN_Y[i].values())
                KEY = (W, H)
                Size={}
                Size[KEY]=UP_Dim

            Recatngles_H[key].append(Dimensions)
            ALL_HRECTS[key2].append(Size)


        '''
        DIM = []
        Recatngles_V = {}
        key = MINX.keys()[0]
        Recatngles_V.setdefault(key, [])
        for j in Vtree.vNodeList[0].stitchList:
            k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y,j.cell.type]
            DIM.append(k)
        for i in range(len(MIN_X)):
            print "i",i
            Dimensions = []
            for j in range(len(DIM)):

                k=DIM[j]


                if k[0] in MIN_X[i].keys() and k[1] in MIN_Y[i].keys() and k[2] in MIN_X[i].keys() and k[3] in MIN_Y[i].keys():
                    #rect3 = [float(MIN_X[i][k[0]])/s, float(MIN_Y[i][k[1]])/s, float(MIN_X[i][k[2]])/s - float(MIN_X[i][k[0]])/s,float(MIN_Y[i][k[3]])/s - float(MIN_Y[i][k[1]])/s,k[4]]
                    rect3 = [float(MIN_X[i][k[0]]) / s, float(MIN_Y[i][k[1]]) / s,
                          float(MIN_X[i][k[2]]) / s - float(MIN_X[i][k[0]]) / s,
                          float(MIN_Y[i][k[3]]) / s - float(MIN_Y[i][k[1]]) / s, k[4]]
                    #print rect
                    Dimensions.append(rect3)
            #print "Dim",len(Dimensions),Dimensions
            Recatngles_V[key].append(Dimensions)
        '''
        #print Recatngles_V

        ALL_RECTS = {} # to plot resultatnt layouts
        for k, v in Recatngles_H.items():
            ALL_RECTS['H']=v
        '''
        Recatngles_V = collections.OrderedDict(sorted(Recatngles_V.items()))
        for k, v in Recatngles_V.items():
            ALL_RECTS['V']=v
        #print"Key", len(ALL_RECTS.values())
        '''

        return ALL_HRECTS,ALL_RECTS









       ###################################################################################################################