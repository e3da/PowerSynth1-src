#!/usr/bin/python
'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
Updated from Aug,2017
@ author: Imam Al Razi, ialrazi
'''
import os
import matplotlib
#matplotlib.use('Agg')
import matplotlib.patches as patches
from abc import ABCMeta
from constraintGraph_Dev import *
import constraint as ct
import collections
import csv
import networkx as nx
from powercad.general.data_struct.util import *


global VID,HID,Schar,Cchar,Htree,Vtree
Schar='/'
Cchar='%'
VID=0
HID=0

class cell:
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

class tile:
    """
    Abstract class of cells, there eventually will be multiple
    implementations of cells with different physical properties
    We're using the bare minimum four pointer configuration 
    presented in the paper. As per the paper, only the left and bottom sides
    are explicitly defined, everything else being implicitly defined by neighbors
    """

    def __init__(self, north, east, south, west, hint, cell,name=None,nodeId=None,voltage=None,current=None,vertex1=None,vertex2=None):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.HINT = hint #this is the pointer to the hint tile of where to start looking for location
        self.cell = cell # to get x,y,type information
        self.name=name # to give a unique id of tile
        self.nodeId=nodeId # in hierarchical tree which node it belongs to
        self.voltage=voltage # voltage value assigned to it for reliability constraint
        self.current=current # current value assigned to it for reliability constraint
        self.vertex1=vertex1
        self.vertex2=vertex2


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
        #print cc.getHeight(),cc.cell.y

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
           # print "4 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.WEST is not None:
                cc = cc.WEST
            else:
                break

        return neighbors
########################################################################################################################
class cornerStitch_algorithms(object):
    """
    A cornerStitch is a collection of tiles all existing on the same plane. I'm not sure how we're going to handle
    cornerStitchs connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of tiles or anything involving coordinates being passed in instead of a tile
    """
    __metaclass__ = ABCMeta
    def __init__(self, stitchList, level):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.level=level

    def merge(self, tile1, tile2):
        """
        merge two tiles into one, reassign neighborhood, and return the merged tile in case a reference is needed

        """
        if(tile1.cell.type != tile2.cell.type):
            #print "Types are not the same"
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

    def lowestCell(self, cellList):
        min = 10000000
        for i in cellList:
            if i.cell.y < min:
                min = i

        return cellList.index(min)



    def findPoint(self, x, y, startCell):
        """
        find the tile that contains the coordinates x, y
        """
        """
        if y > self.northBoundary.cell.y:
            return self.northBoundary
        if y < 0:
            return self.southBoundary
        if x > self.eastBoundary.cell.x:
            return self.eastBoundary
        if x < 0:
            return self.westBoundary
        """

        cc = startCell #current cell


        while (y < cc.cell.y or y >=(cc.cell.y + cc.getHeight())):#y >(cc.cell.y + cc.getHeight()

            if (y >= cc.cell.y + cc.getHeight()):
               if(cc.NORTH is not None):
                   cc = cc.NORTH
               else:
                   print("out of bounds 1")
                   return "Failed"
            elif y < cc.cell.y:#y <= cc.cell.y
                if(cc.SOUTH is not None):
                    cc = cc.SOUTH
                else:
                    print("out of bounds 2")
                    return "Failed"
        while(x < cc.cell.x or x >=(cc.cell.x + cc.getWidth())):#x >(cc.cell.x + cc.getWidth()

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
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later
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
                        #print "t", t.cell.x, t.cell.y
                        dirn = 1
                    elif t.cell.x + t.getWidth() < x2:  # it was <=
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


    def plow(self, tile, destX, destY):
        """
        the tile cell is moved so that its lower left corner is dextX, destY, and all tiles in the way
        are moved out of the way. They are in turn moved by recursive calls to plow.
        """
        return

    def compaction(self, dimension):
        """
        reduce all possible empty space in the dimension specified ("H", or "V"), while still maintaining any
        design constraints and the relative structure of the cornerStitch
        """
        return

    def findChannel(self, startCell, endCell, minWidth):
        """
        find a channel through empty cells from startCell to endCell, subject to minWidth.
        """
        return

    def findNeighor(self, inputCell, direction):
        """
        Probably a better way to do this, ask Dr. Peng.
        Direction should be the first character of a direction, i.e. ('n', 'e', 's', 'w')
        Returns the cell epsilon to the direction of the relevant corner
        """
        if direction == 'n':
            return self.findPoint()
        if direction == 'e':
            return self.findPoint((inputCell.cell.x + inputCell.getWidth() + .0001), inputCell.cell.y + inputCell.getHeight())
        if direction == 's':
            return self.findPoint((inputCell.cell.x + inputCell.getWidth()), inputCell.cell.y + inputCell.getHeight() - .0001)
        if direction == 'w':
            return self.findPoint((inputCell.cell.x + inputCell.getWidth() - .0001), inputCell.cell.y + inputCell.getHeight())

    def vSplit(self, splitCell, x):
        """

        New cell is right half of the cell

        """

        if x < splitCell.cell.x or x > splitCell.cell.x + splitCell.getWidth():

            return
        if splitCell.cell.type!="EMPTY":
            newCell = tile(None, None, None, None, None,cell(x, splitCell.cell.y, splitCell.cell.type, id=splitCell.cell.id),nodeId=splitCell.nodeId)
        else:
            newCell = tile(None, None, None, None, None,
                           cell(x, splitCell.cell.y, splitCell.cell.type, id=splitCell.cell.id))
        self.stitchList.append(newCell)
          # figure out how to fix this and pass in by reference*
        #assign newCell neighbors
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
        #if cc not in self.boundaries:
        if cc.cell.type != None:
            while cc.cell.x >= x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        #if cc not in self.boundaries:
        if cc.cell.type != None:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the NORTH pointers for the bottom edge
        #if cc not in self.boundaries:
        if cc.cell.type != None:
            #cc.SOUTH.cell.printCell(True, True)
            ccWidth = cc.getWidth() #I don't know why, but this solves getWidth() throwing an error otherwise
            #while cc not in self.boundaries and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
            while cc.cell.type!=None and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
                cc.NORTH = newCell
                cc = cc.EAST
                #if cc not in self.boundaries:
                if cc.cell.type!=None:
                    ccWidth = cc.getWidth()  # I don't know why, but this solves getWidth() throwing an error otherwise

        return newCell

    def hSplit(self, splitCell_id, y):

        """
        newCell is the top half of the split
        """
        splitCell=self.stitchList[splitCell_id]

        if y < splitCell.cell.y or y > splitCell.cell.y + splitCell.getHeight():

            return
        if splitCell.cell.type!="EMPTY":
            newCell = tile(None, None, None, None, None,cell(splitCell.cell.x, y, splitCell.cell.type, id=splitCell.cell.id),nodeId=splitCell.nodeId)
        else:
            newCell = tile(None, None, None, None, None,
                           cell(splitCell.cell.x, y, splitCell.cell.type, id=splitCell.cell.id))

        self.stitchList.append(newCell)

        # assign new cell directions
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH =splitCell

        cc = splitCell.WEST
        #if cc not in self.boundaries:
        if cc.cell.type != None:
            # cc.cell.printCell(True, True)
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

        #if cc not in self.boundaries:
        if cc.cell.type!=None:
            while cc.cell.x >= newCell.cell.x:
                cc.SOUTH = newCell
                cc = cc.WEST


        cc = newCell.EAST  # reassign the WEST pointers for the right edge
        #if cc not in self.boundaries:
        if cc.cell.type!=None:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.WEST  # reassign the EAST pointers for the right edge

        #if cc not in self.boundaries:
        if cc.cell.type != None:
            #while cc not in self.boundaries and  cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
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

class Node(cornerStitch_algorithms):
    """
    Group of tiles .Part of hierarchical Tree
    """
    __metaclass__ = ABCMeta
    def __init__(self,boundaries,stitchList,parent=None,id=None,):
        self.parent=parent
        self.child=[]
        self.stitchList=stitchList
        self.id=id
        self.boundaries=boundaries

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
    def __init__(self, boundaries,child,stitchList,parent,id):

        self.stitchList=stitchList
        self.boundaries=boundaries
        self.child=[]
        self.parent=parent
        self.id=id

    # merge function to merge empty tiles(to show corner stitch property)
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
    def insert(self, start,x1, y1, x2, y2, type,end,Htree,Vtree,Parent):
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
        RESP=0
        if self.areaSearch(x1, y1, x2, y2,type):#check to ensure that the area is empty
            RESP=1
        # return "Area is not empty"

        """
        New algorithm
        """
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
        ###############################################################(added on 2.19.2018)
        if tr.cell.y == y1:
            tr = tr.SOUTH
            while tr.cell.x + tr.getWidth() <= x1:
                tr = tr.EAST
        ################################################################


        if bottomRight.cell.x == x2:
            bottomRight = bottomRight.WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH
        splitList = []
        splitList.append(bottomRight)
        if start != Schar:
            if bottomRight.SOUTH not in self.boundaries and bottomRight.SOUTH.cell.type == type and bottomRight.SOUTH.cell.y + bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type == type:
                cc1 = bottomRight.SOUTH
                while cc1.cell.x + cc1.getWidth() < x2:
                    cc1 = cc1.EAST
                if cc1 not in splitList:
                    splitList.append(cc1)
                # if cc1.cell.type == "SOLID" and cc1.cell.y+cc1.getHeight() == y2:
                if cc1.cell.type == type and cc1.cell.y + cc1.getHeight() == y2:
                    cc2 = cc1.SOUTH
                    while cc2.cell.x + cc2.getWidth() < x2:
                        cc2 = cc2.EAST
                    if cc2 not in splitList and cc2.cell.type=="EMPTY" :#and cc2.cell.type==type
                        splitList.append(cc2)


            cc = bottomRight.NORTH

            while cc.cell.y <= tr.cell.y and cc not in self.boundaries:  # has been added
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


        for rect in splitList:

            if x2 != rect.cell.x and x2 != rect.EAST.cell.x:

                self.vSplit(rect, x2)

        splitList = []
        splitList.append(topLeft)



        if start != Schar:
            if topLeft.NORTH not in self.boundaries and topLeft.NORTH.cell.type == type and topLeft.NORTH.cell.y == y1 or topLeft.cell.type == type:
                cc = topLeft.NORTH
                while cc.cell.x > x1:
                    cc = cc.WEST
                #if cc.cell.type==type or cc.cell.type=="EMPTY":
                splitList.append(cc)

                # if cc.cell.type == "SOLID" and cc.cell.y == y1:
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


        for rect in splitList:

            if x1 != rect.cell.x and x1 != rect.EAST.cell.x:
                #print"1", rect.cell.x,rect.cell.y
                self.vSplit(rect, x1)

        ### Horizontal split

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

                self.hSplit(i, y2) # order is vital, again

        #if start!='/':
        if start != Schar:
            cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
            while cc not in self.boundaries and cc.cell.x < x1:
                cc = cc.EAST

            ## Re-splitting for overlapping cases

            while cc.cell.x < x2:
                cc1 = cc
                resplit = []
                min_x = 1000000
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
            #####
            resplit = []

            cc = self.findPoint(x1, y2, self.stitchList[0])

            while cc.cell.x + cc.getWidth() <= x2:
                # if cc.SOUTH.cell.type == "SOLID" and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH != self.southBoundary and cc.SOUTH.cell.x+cc.SOUTH.getWidth() != cc.cell.x+cc.getWidth():
                if cc.SOUTH.cell.type == type and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH not in self.boundaries and cc.SOUTH.cell.x + cc.SOUTH.getWidth() != cc.cell.x + cc.getWidth():
                    resplit.append(cc.SOUTH)
                    resplit.append(cc.SOUTH.SOUTH)

                for rect in resplit:

                    self.vSplit(rect, cc.cell.x + cc.getWidth())
                cc = cc.EAST

            resplit = []
            cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
            while cc.cell.x + cc.getWidth() <= x2:
                # if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1 and cc.NORTH != self.northBoundary and cc.NORTH.cell.x+cc.NORTH.getWidth() != cc.cell.x+cc.getWidth():
                if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and cc.NORTH not in self.boundaries and cc.NORTH.cell.x + cc.NORTH.getWidth() != cc.cell.x + cc.getWidth():
                    resplit.append(cc.NORTH)
                    resplit.append(cc.NORTH.NORTH)

                    for rect in resplit:
                        # flag = True

                        self.vSplit(rect, cc.cell.x + cc.getWidth())
                cc = cc.EAST

        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while cc.cell.x + cc.getWidth() <= x2:
            # if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1:
            if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and start!= Schar:
                changeList.append(cc.NORTH)
            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH

        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH

        changeList.append(t)


        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later


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
                    elif t.cell.x + t.getWidth() < x2:  # it was <=
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




            self.addChild(start,tile_list,type,end,Vtree,Parent)

        return self.stitchList
    def addChild(self,start, tile_list, type,end,Vtree,Parent):

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

            node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            Parent.child.append(node)
            Vtree.vNodeList.append(node)
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

            node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            Parent.child.append(node)
            Vtree.vNodeList.append(node)
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


                # if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.nodeId == id:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    # if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))
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
            Node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
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
                if j < len(changeSet):  # there was a '-1'
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
                # print "i = ", i
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

            #print"TR"
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
    def __init__(self, boundaries, child, stitchList, parent, id):

        self.stitchList = stitchList
        self.boundaries = boundaries
        self.child = []
        self.parent = parent
        self.id = id

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

    def insert(self,start, x1, y1, x2, y2, type,end,Htree,Vtree,Parent):

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
        if self.areaSearch(x1, y1, x2, y2,type): #check to ensure that the area is empty

            RESP=1


        topLeft = self.findPoint(x1, y1, self.stitchList[0])


        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        tr = self.findPoint(x2, y1, self.stitchList[0])
        bl = self.findPoint(x1, y2, self.stitchList[0])

        if topLeft.cell.y == y1:
            cc = topLeft
            if topLeft.SOUTH not in self.boundaries:
                cc = topLeft.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
                cc = cc.EAST
            topLeft = cc

        if tr.cell.y == y1:
            cc = tr
            if tr.SOUTH not in self.boundaries:
                cc = tr.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            tr = cc



        splitList = []
        splitList.append(topLeft)
        cc = topLeft


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


            while cc.cell.x <= tr.cell.x and cc not in self.boundaries:
                if cc not in splitList:

                    splitList.append(cc)

                cc = cc.EAST

                while cc.cell.y >= y1 and cc not in self.boundaries:
                    cc = cc.SOUTH


            if cc.cell.type == type and cc.cell.x == x2 and cc not in self.boundaries or tr.cell.type == type:  ##and tr.cell.y!=y1 and cc!=self.eastBoundary)

                splitList.append(cc)

                if cc.EAST not in self.boundaries:
                    cc = cc.EAST

                    while cc.cell.y >= y1:
                        cc = cc.SOUTH

                    splitList.append(cc)


        for rect in splitList:

            i = self.stitchList.index(rect)
            if y1 != rect.cell.y and y1 != rect.NORTH.cell.y: self.hSplit(i, y1)



        if bottomRight.cell.x == x2:
            bottomRight = bottomRight.WEST

            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH

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
                if cc not in splitList: ###########################
                    splitList.append(cc)

            if cc.cell.type == type and cc.cell.x + cc.getWidth() >= x1 or bl.cell.type == type:  # previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
                if cc not in splitList:
                    splitList.append(cc)

                if cc.WEST not in self.boundaries:
                    cc1 = cc.WEST
                    while cc1.cell.y + cc1.getHeight() <= y2:
                        cc1 = cc1.NORTH
                    splitList.append(cc1)


        for rect in splitList:

            i=self.stitchList.index(rect)
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y: self.hSplit(i, y2)


        changeList = []
        # step 2: vsplit x1 and x2
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

            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2)  # do not reorder these lines



            if not rect.cell.x == x1: self.vSplit(rect, x1)  # do not reorder these lines

        if start!=Schar:
            cc = self.findPoint(x2, y2, self.stitchList[0]).WEST  ##There was topLeft.SOUTH
            #
            #print "CC", cc.cell.x,cc.cell.y+cc.getHeight(),y1
            while cc not in self.boundaries and cc.cell.y + cc.getHeight() <= y1:
                cc1 = cc
                #print"resplitsouth=", cc.cell.x, cc.cell.y
                resplit = []
                min_y = 100000
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



        changeList = []
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        # if t.WEST.cell.type=="SOLID" and t.WEST.cell.x+t.WEST.getWidth()==x1:
        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1 and start!=Schar:
            changeList.append(t.WEST)
        changeList.append(t)
        #print "L",len(changeList)
        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later

                    t = child
                    if child not in changeList:
                        changeList.append(child)
                else:
                    # if child.cell.type == "SOLID" and child.cell.x == x2:
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
                        # if t.WEST.cell.type == "SOLID" and t.WEST.cell.x + t.WEST.getWidth() == x1:
                        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1 and start!=Schar:
                            changeList.append(t.WEST)
                        dirn = 1
                    elif t.cell.x + t.getWidth() < x2:  # it was <=
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

        ## New Merge Algorithm v2

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


        ######
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

        #for i in tile_list:
            #print "i", i.cell.printCell(True,True,True),i.nodeId
        if start== Schar and end == Schar:
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:
                #print "R", rect.cell.x, rect.cell.y

                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            ParentH.child.append(node)
            Htree.hNodeList.append(node)
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

            node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            ParentH.child.append(node)
            Htree.hNodeList.append(node)
        elif start!= Schar and end != Schar:
            ID = 0
            for rect in tile_list:
                # if rect.cell.type == type:
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
                # print "T",rect.cell.type
                if rect.cell.type == type:
                    rect.nodeId = id
                # if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.nodeId == id:
                    # rect.nodeId = id

                    stitchList.append(rect)
                else:
                    # if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries:
                        boundaries.append(copy.copy(rect))
        elif start != Schar and end == Schar:
            ID=0
            for rect in tile_list:
                # if rect.cell.type == type:
                if rect.cell.type != "EMPTY":
                    if rect.nodeId>ID:
                        ID=rect.nodeId

            #print ID
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
                # print "T",rect.cell.type
                if rect.cell.type==type:
                    rect.nodeId=id
                # if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.nodeId==id:
                    #rect.nodeId = id

                    stitchList.append(rect)
                else:
                    # if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))
            Htree.hNodeList.remove(node)
            Node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
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
        # print "len4=", len(changeSet)
        i = 0
        j = 1
        while j < len(changeSet):  # merge all cells with the same width along the eastern side
            # print "test",len(changeSet),i,j
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            #if topCell.EAST == lowerCell.EAST:
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

    def setNodeId1(self,node):
        #for node in nodelist:
        for rect in node.stitchList:
            if rect.nodeId==None:
                rect.nodeId=node.id
        for rect in node.boundaries:
            rect.nodeId=node.id




###################################################
class Rectangle(Rect):
    def __init__(self, type=None, x=None, y=None, width=None, height=None, name=None, Schar=None, Echar=None,
                 Netid=None):
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
        Rect.__init__(self, top=self.y + self.height, bottom=self.y, left=self.x, right=self.x + self.width)
    def __str__(self):
        return 'x: '+str(self.x) + ', y: ' + str(self.y) + ', w: ' + str(self.width) + ', h: ' + str(self.height)

    def __repr__(self):
        return self.__str__()
    def contains(self, b):
        return not (self.x1 > b.x2 or b.x1 > self.x2 or b.y1 > self.y2 or self.y1 > b.y2)

    def getParent(self):
        return self.parent


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
        Tile1 = tile(None, None, None, None, None, cell(0, 0, self.type), nodeId=1)
        TN = tile(None, None, None, None, None, cell(0, self.h, None))
        TE = tile(None, None, None, None, None, cell(self.w, 0, None))
        TW = tile(None, None, None, None, None, cell(-1000, 0, None))
        TS = tile(None, None, None, None, None, cell(0, -1000, None))
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
        Vnode0 = Vnode(boundaries=Boundaries, child=None, stitchList=Stitchlist, parent=None, id=1)
        #Vtree = Tree(hNodeList=None, vNodeList=[Vnode0])
        Tile2 = tile(None, None, None, None, None, cell(0, 0, self.type), nodeId=1)
        TN2 = tile(None, None, None, None, None, cell(0, self.h, None))
        TE2 = tile(None, None, None, None, None, cell(self.w, 0, None))
        TW2 = tile(None, None, None, None, None, cell(-1000, 0, None))
        TS2 = tile(None, None, None, None, None, cell(0, -1000, None))
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
        Hnode0 = Hnode(boundaries=Boundaries_H, child=None, stitchList=Stitchlist_H, parent=None, id=1)
        #Htree = Tree(hNodeList=[Hnode0], vNodeList=None)
        return Hnode0, Vnode0

    # Reliability constraint purpose: To assign I-V values to the tiles # No use in this version
    def I_V_Constraints(Enable=False):
        if Enable == True:
            Voltage = {}
            # self.voltage_constraint = {}
            with open(testdir + '/' + 'Voltage-info.csv', 'rb') as csvfile:
                csvreader = csv.reader(csvfile)

                # extracting field names through first row
                fields = csvreader.next()

                # extracting each data row one by one
                i = 0
                for row in csvreader:
                    i += 1
                    if row[0] in (None, ""):
                        break
                    # if row[2]!=
                    else:
                        Voltage[(int(row[0]), int(row[1]))] = int(row[2])


            Current = {}
            # self.voltage_constraint = {}
            with open(testdir + '/' + 'Current-info.csv', 'rb') as csvfile:
                csvreader = csv.reader(csvfile)

                # extracting field names through first row
                fields = csvreader.next()

                # extracting each data row one by one
                i = 0
                for row in csvreader:
                    i += 1
                    if row[0] in (None, ""):
                        break
                    # if row[2]!=
                    else:
                        Current[(int(row[0]), int(row[1]))] = int(row[2])
            # print "Current", Current
            # print i,j,Voltage,self.voltage_constraint
            # RECT_H=[]

            ################################################# (Finding connected components)
            Rectangles_H = []
            # for i in Htree.hNodeList[0]:
            for j in Htree.hNodeList[0].stitchList:
                # k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                if j.cell.type != "EMPTY":
                    Rect = Rectangle(j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type)
                    if Rect not in Rectangles_H:
                        Rectangles_H.append(Rect)
                        # print Rect.type

            # print len(Rectangles_H)
            Rectangles_H.sort(key=lambda cc: cc.y1)
            # Rectangles_H.reverse()
            # Rectangles_H.sort(key=lambda cc: cc.x1)
            for i in range(len(Rectangles_H)):
                for j in range(len(Rectangles_H)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_H[i].contains(Rectangles_H[j]) and Rectangles_H[i].type == Rectangles_H[j].type:
                        if Rectangles_H[i].parent == None and Rectangles_H[j].parent == None:
                            Rectangles_H[i].parent = Rectangles_H[i]
                            Rectangles_H[j].parent = Rectangles_H[i]
                        elif Rectangles_H[i].parent == None and Rectangles_H[j].parent != None:
                            Rectangles_H[i].parent = Rectangles_H[j].parent
                        elif Rectangles_H[i].parent != None and Rectangles_H[j].parent == None:
                            Rectangles_H[j].parent = Rectangles_H[i].parent
                    # else:
                    # Rectangles_H[i].parent = Rectangles_H[i]
            # print len(Rectangles_H)

            Parent_List = []
            for i in range(len(Rectangles_H)):
                if Rectangles_H[i].parent not in Parent_List:
                    Parent_List.append(Rectangles_H[i].parent)
            # print len(Parent_List)
            ALL_CONNECTED = {}
            for i in range(len(Parent_List)):
                Connected = []
                for j in range(len(Rectangles_H)):
                    if Rectangles_H[j].parent == Parent_List[i]:
                        Connected.append(Rectangles_H[j])
                    else:
                        continue
                ALL_CONNECTED[Parent_List[i]] = Connected
            Rectangles_H.sort(key=lambda cc: cc.x1)
            for i in range(len(Rectangles_H)):
                for j in range(len(Rectangles_H)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_H[i].contains(Rectangles_H[j]) and Rectangles_H[i].type == Rectangles_H[j].type:
                        if Rectangles_H[i].parent != Rectangles_H[j].parent:
                            # print"xy", Rectangles_H[i].x1, Rectangles_H[i].y1, Rectangles_H[j].x1, Rectangles_H[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_H[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_H[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[i].parent:
                                        Rectangles_H[j].parent = Rectangles_H[i].parent
                                        v.append(Rectangles_H[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[j].parent:
                                        Rectangles_H[i].parent = Rectangles_H[j].parent
                                        v.append(Rectangles_H[i])
            Rectangles_H.sort(key=lambda cc: cc.y2)
            for i in range(len(Rectangles_H)):
                for j in range(len(Rectangles_H)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_H[i].contains(Rectangles_H[j]) and Rectangles_H[i].type == Rectangles_H[j].type:
                        if Rectangles_H[i].parent != Rectangles_H[j].parent:
                            # print"xy", Rectangles_H[i].x1, Rectangles_H[i].y1, Rectangles_H[j].x1, Rectangles_H[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_H[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_H[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[i].parent:
                                        Rectangles_H[j].parent = Rectangles_H[i].parent
                                        v.append(Rectangles_H[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[j].parent:
                                        Rectangles_H[i].parent = Rectangles_H[j].parent
                                        v.append(Rectangles_H[i])
            Rectangles_H.sort(key=lambda cc: cc.x2)
            for i in range(len(Rectangles_H)):
                for j in range(len(Rectangles_H)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_H[i].contains(Rectangles_H[j]) and Rectangles_H[i].type == Rectangles_H[j].type:
                        if Rectangles_H[i].parent != Rectangles_H[j].parent:
                            # print"xy", Rectangles_H[i].x1, Rectangles_H[i].y1, Rectangles_H[j].x1, Rectangles_H[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_H[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_H[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[i].parent:
                                        Rectangles_H[j].parent = Rectangles_H[i].parent
                                        v.append(Rectangles_H[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_H[j].parent:
                                        Rectangles_H[i].parent = Rectangles_H[j].parent
                                        v.append(Rectangles_H[i])

            ALL_CONNECTED_H = []
            Parent_List2 = []
            for i in range(len(Rectangles_H)):
                if Rectangles_H[i].parent not in Parent_List2:
                    Parent_List2.append(Rectangles_H[i].parent)
            # print len(Parent_List2), len(Parent_List)
            for i in range(len(Parent_List2)):
                Connected = []
                for j in range(len(Rectangles_H)):
                    if Rectangles_H[j].parent == Parent_List2[i]:
                        Connected.append(Rectangles_H[j])
                    else:
                        continue
                ALL_CONNECTED_H.append(Connected)

            Rectangles_V = []
            # for i in Htree.hNodeList[0]:
            for j in Vtree.vNodeList[0].stitchList:
                # k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                if j.cell.type != "EMPTY":
                    Rect = Rectangle(j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type)
                    if Rect not in Rectangles_V:
                        Rectangles_V.append(Rect)
                        # print Rect.type

            # print"V", len(Rectangles_V)
            Rectangles_V.sort(key=lambda cc: cc.x1)
            # Rectangles_V.sort(key=lambda cc: cc.y1)
            for i in range(len(Rectangles_V)):
                for j in range(len(Rectangles_V)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_V[i].contains(Rectangles_V[j]) and Rectangles_V[i].type == Rectangles_V[j].type:
                        if Rectangles_V[i].parent == None and Rectangles_V[j].parent == None:
                            Rectangles_V[i].parent = Rectangles_V[i]
                            Rectangles_V[j].parent = Rectangles_V[i]
                        elif Rectangles_V[i].parent == None and Rectangles_V[j].parent != None:
                            Rectangles_V[i].parent = Rectangles_V[j].parent
                        elif Rectangles_V[i].parent != None and Rectangles_V[j].parent == None:
                            Rectangles_V[j].parent = Rectangles_V[i].parent
                    # else:
                    # Rectangles_H[i].parent = Rectangles_H[i]
            # print len(Rectangles_V)
            Parent_List = []
            for i in range(len(Rectangles_V)):
                if Rectangles_V[i].parent not in Parent_List:
                    Parent_List.append(Rectangles_V[i].parent)
            # print len(Parent_List)
            ALL_CONNECTED = {}
            for i in range(len(Parent_List)):
                Connected = []
                for j in range(len(Rectangles_V)):
                    if Rectangles_V[j].parent == Parent_List[i]:
                        Connected.append(Rectangles_V[j])
                    else:
                        continue
                ALL_CONNECTED[Parent_List[i]] = Connected
            Rectangles_V.sort(key=lambda cc: cc.y1)
            for i in range(len(Rectangles_V)):
                for j in range(len(Rectangles_V)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_V[i].contains(Rectangles_V[j]) and Rectangles_V[i].type == Rectangles_V[j].type:
                        if Rectangles_V[i].parent != Rectangles_V[j].parent:
                            # print"xy", Rectangles_V[i].x1, Rectangles_V[i].y1, Rectangles_V[j].x1, Rectangles_V[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_V[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_V[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[i].parent:
                                        Rectangles_V[j].parent = Rectangles_V[i].parent
                                        v.append(Rectangles_V[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[j].parent:
                                        Rectangles_V[i].parent = Rectangles_V[j].parent
                                        v.append(Rectangles_V[i])
            Rectangles_V.sort(key=lambda cc: cc.y2)
            for i in range(len(Rectangles_V)):
                for j in range(len(Rectangles_V)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_V[i].contains(Rectangles_V[j]) and Rectangles_V[i].type == Rectangles_V[j].type:
                        if Rectangles_V[i].parent != Rectangles_V[j].parent:
                            # print"xy", Rectangles_V[i].x1, Rectangles_V[i].y1, Rectangles_V[j].x1, Rectangles_V[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_V[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_V[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[i].parent:
                                        Rectangles_V[j].parent = Rectangles_V[i].parent
                                        v.append(Rectangles_V[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[j].parent:
                                        Rectangles_V[i].parent = Rectangles_V[j].parent
                                        v.append(Rectangles_V[i])
            Rectangles_V.sort(key=lambda cc: cc.x2)
            for i in range(len(Rectangles_V)):
                for j in range(len(Rectangles_V)):
                    # if Rectangles_H[i]==Rectangles_H[j]:
                    # continue
                    # else:
                    if Rectangles_V[i].contains(Rectangles_V[j]) and Rectangles_V[i].type == Rectangles_V[j].type:
                        if Rectangles_V[i].parent != Rectangles_V[j].parent:
                            # print"xy", Rectangles_V[i].x1, Rectangles_V[i].y1, Rectangles_V[j].x1, Rectangles_V[j].y1
                            for k, v in ALL_CONNECTED.items():
                                if k == Rectangles_V[i].parent:
                                    L1 = len(v)
                                elif k == Rectangles_V[j].parent:
                                    L2 = len(v)
                            if L1 >= L2:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[i].parent:
                                        Rectangles_V[j].parent = Rectangles_V[i].parent
                                        v.append(Rectangles_V[j])
                            else:
                                for k, v in ALL_CONNECTED.items():
                                    if k == Rectangles_V[j].parent:
                                        Rectangles_V[i].parent = Rectangles_V[j].parent

                                        v.append(Rectangles_V[i])

            Parent_List_V = []
            for i in range(len(Rectangles_V)):
                if Rectangles_V[i].parent not in Parent_List_V:
                    Parent_List_V.append(Rectangles_V[i].parent)
            # print len(Parent_List_V)
            ALL_CONNECTED_V = []
            for i in range(len(Parent_List_V)):
                Connected = []
                for j in range(len(Rectangles_V)):
                    if Rectangles_V[j].parent == Parent_List_V[i]:
                        Connected.append(Rectangles_V[j])
                    else:
                        continue
                ALL_CONNECTED_V.append(Connected)


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
            # a = ["blue","red","green","yellow","black","orange"]
            i = 0
            for line in f.read().splitlines():  # considering each line in file

                c = line.split(',')  # splitting each line with (,) and inserting each string in c
                # print"C",c
                if len(c) > 4:
                    In = line.split(',')
                    Input.append(In)
        elif input_mode=='list':
            Modified_input=[]

            for R in Rect_list:
               Modified_input.append([R.Schar,R.x,R.y,R.width,R.height,R.type,R.Echar,R.name])

        return Modified_input


    # function to generate initial layout
    def draw_layout(self,rects=None,Htree=None,Vtree=None):
        colors = ['green', 'red', 'blue', 'yellow', 'pink']
        type = ['Type_1', 'Type_2', 'Type_3', 'Type_4','Type_5']
        zorders = [1,2,3,4,5]
        Patches={}

        for r in rects:
            i = type.index(r.type)
            P=matplotlib.patches.Rectangle(
                    (r.x, r.y),  # (x,y)
                    r.width,  # width
                    r.height,  # height
                    facecolor=colors[i],
                    alpha=0.5,
                    zorder=zorders[i],
                    edgecolor='black',
                    linewidth=2,
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



            if inp[1] == "." and inp[2] != ".": ## determining hierarchy level (2nd level):Device insertion

                for i in reversed(Htree.hNodeList):
                    if i.parent.id == 1:
                        # print"ID", i.id
                        ParentH = i
                        break
                CHILDH = ParentH
                CHILDH.insert(inp[0], int(inp[2]), int(inp[3]), int(inp[4]), int(inp[5]), inp[6], inp[7])

                for i in reversed(Vtree.vNodeList):
                    if i.parent.id == 1:
                        # print"ID", i.id
                        Parent = i
                        break
                CHILD = Parent
                CHILD.insert(inp[0], int(inp[2]), int(inp[3]), int(inp[4]), int(inp[5]), inp[6], inp[7])

            if inp[1] == "." and inp[2] == ".":##determining hierarchy level (3rd level):Pin insertion


                for i in reversed(Htree.hNodeList):
                    if i.parent.id == 1:

                        med = i
                        break

                ParentH = med.child[-1]
                CHILDH = ParentH

                x1 = int(inp[3])
                y1 = int(inp[4]) + int(inp[6])
                x2 = int(inp[3]) + int(inp[5])
                y2 = int(inp[4])

                CHILDH.insert(inp[0], int(inp[3]), int(inp[4]), int(inp[5]), int(inp[6]), inp[7], inp[8])

                for i in reversed(Vtree.vNodeList):
                    if i.parent.id == 1:

                        med = i
                        break

                Parent = med.child[-1]
                CHILD = Parent

                x1 = int(inp[3])
                y1 = int(inp[4]) + int(inp[6])
                x2 = int(inp[3]) + int(inp[5])
                y2 = int(inp[4])

                CHILD.insert(inp[0], int(inp[3]), int(inp[4]), int(inp[5]), int(inp[6]), inp[7], inp[8])

            if inp[1] != ".":#determining hierarchy level (1st level):Tile insertion

                start = inp[0]
                Parent = Vtree.vNodeList[0]

                x1 = int(inp[1])
                y1 = int(inp[2]) + int(inp[4])
                x2 = int(inp[1]) + int(inp[3])
                y2 = int(inp[2])

                Parent.insert(start, x1, y1, x2, y2, inp[5],inp[6], Htree, Vtree,Parent)


                ParentH = Htree.hNodeList[0]

                x1 = int(inp[1])
                y1 = int(inp[2]) + int(inp[4])
                x2 = int(inp[1]) + int(inp[3])
                y2 = int(inp[2])

                ParentH.insert(start, x1, y1, x2, y2, inp[5],inp[6],Htree,Vtree,ParentH)

        Htree.setNodeId1(Htree.hNodeList[0])
        Vtree.setNodeId1(Vtree.vNodeList[0])
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
        extension = [int(math.floor(float(ext) * mult)) for ext in ((data.iloc[1, 1:]).values.tolist())]
        height = [int(math.floor(float(h) * mult)) for h in ((data.iloc[2, 1:]).values.tolist())]

        for j in range(len(data)):
            # print i
            # print data.nrows[i]
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

        #print minWidth,minEnclosure,minExtension,minHeight,minSpacing

        # print minWidth,minSpacing,minEnclosure
        # setting up constraint values
        CONSTRAINT = ct.constraint()
        CONSTRAINT.setupMinWidth(minWidth)
        CONSTRAINT.setupMinHeight(minHeight)
        CONSTRAINT.setupMinExtension(minExtension)
        CONSTRAINT.setupMinSpacing(minSpacing)
        CONSTRAINT.setupMinEnclosure(minEnclosure)

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
            # for j in i.stitchList:
            p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
            DIM.append(p)
        ALL_RECTS['H'] = DIM
        DIM = []
        for j in Vtree.vNodeList[0].stitchList:
            # for j in i.stitchList:
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
    def evaluation(self,Htree,Vtree,N,W,H,XLoc,YLoc):
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
            CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList,self.level, N)
        elif self.level==2 or self.level==3:
            if W==None or H ==None:
                print"Please enter Width and Height of the floorplan"
            if N==None:
                print"Please enter Number of layouts to be generated"
            else:
                CG = constraintGraph(W, H, XLoc, YLoc)
                CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList, self.level, N)
        else:
            CG = constraintGraph( W=None, H=None,XLocation=None, YLocation=None)
            CG.graphFromLayer(Htree.hNodeList, Vtree.vNodeList, self.level,N=None)
        MIN_X, MIN_Y = CG.minValueCalculation(Htree.hNodeList, Vtree.vNodeList, self.level)
        return MIN_X, MIN_Y




    def UPDATE_min(self,MINX, MINY,Htree,Vtree,sym_to_cs):
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
        for i in Htree.hNodeList:
            if i.child != []:
                Dimensions = []
                DIM = []

                for j in i.stitchList:
                    p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(),j.cell.type]

                    DIM.append(p)

                    k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y]


                    if k[0] in MINX[i.id].keys() and k[1] in MINY[i.id].keys() and k[2] in MINX[i.id].keys() and k[3] in \
                            MINY[i.id].keys():
                        rect = [MINX[i.id][k[0]], MINY[i.id][k[1]], MINX[i.id][k[2]] - MINX[i.id][k[0]],
                                MINY[i.id][k[3]] - MINY[i.id][k[1]], j.cell.type]
                        r1=Rectangle(x=rect[0],y=rect[1],width=rect[2],height=rect[3],type=rect[4])
                    for k1,v in sym_to_cs.items():

                        key=k1
                        ALL_HRECTS.setdefault(key,[])
                        for r in v:

                            if r[0]==k[0] and r[1]==k[1]:
                                ALL_HRECTS[key].append(r1)


                    Dimensions.append(rect)


                Recatngles_H[i.id] = Dimensions
                RET_H[i.id] = DIM



        Recatngles_V = {}
        RET_V = {}
        for i in Vtree.vNodeList:

            if i.child != []:
                Dimensions = []
                DIM_V = []

                for j in i.stitchList:
                    p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.voltage, j.current, j.cell.type]
                    DIM_V.append(p)
                    k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y]
                    if k[0] in MINX[i.id].keys() and k[1] in MINY[i.id].keys() and k[2] in MINX[i.id].keys() and k[3] in \
                            MINY[i.id].keys():
                        rect = [MINX[i.id][k[0]], MINY[i.id][k[1]], MINX[i.id][k[2]] - MINX[i.id][k[0]],
                                MINY[i.id][k[3]] - MINY[i.id][k[1]], j.cell.type]



                    Dimensions.append(rect)
                Recatngles_V[i.id] = Dimensions
                RET_V[i.id] = DIM_V

        ALL_RECTS = {}

        Recatngles_H = collections.OrderedDict(sorted(Recatngles_H.items()))
        for k, v in Recatngles_H.items():
            ALL_RECTS['H'] = v
        #Total_V = []
        Recatngles_V = collections.OrderedDict(sorted(Recatngles_V.items()))
        for k, v in Recatngles_V.items():
            ALL_RECTS['V'] = v
        #print "ALL",ALL_HRECTS
        return ALL_HRECTS,ALL_RECTS

    def UPDATE(self,MINX,MINY,Htree, Vtree, sym_to_cs):
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
        DIM = []
        Recatngles_H={}
        key=MINX.keys()[0]
        Recatngles_H.setdefault(key,[])
        ALL_HRECTS = {}  # used for mapping symbolic layout objects with corner stitch resultant rectangles.key=MINX.keys()[0]
        key2='H'
        ALL_HRECTS.setdefault(key2,[])


        for j in Htree.hNodeList[0].stitchList:
            k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y,j.cell.type]
            #print k
            DIM.append(k)
        #print DIM
        for i in range(len(MIN_X)):
            Dimensions = []
            UP_Dim={}
            for j in range(len(DIM)):

                k=DIM[j]
                if k[0] in MIN_X[i].keys() and k[1] in MIN_Y[i].keys() and k[2] in MIN_X[i].keys() and k[3] in MIN_Y[i].keys():
                    rect = [MIN_X[i][k[0]], MIN_Y[i][k[1]], MIN_X[i][k[2]] - MIN_X[i][k[0]],MIN_Y[i][k[3]] - MIN_Y[i][k[1]],k[4]]
                    r1 = Rectangle(x=rect[0], y=rect[1], width=rect[2], height=rect[3], type=rect[4])

                    for k1,v in sym_to_cs.items():
                        #print k,v
                        key1=k1
                        UP_Dim.setdefault(key1,[])
                        for r in v:

                            if r[0]==k[0] and r[1]==k[1]:
                                UP_Dim[key1].append(r1)
                    Dimensions.append(rect)
                W = max(MIN_X[i].values())
                H = max(MIN_Y[i].values())
                KEY = (W, H)
                Size={}
                Size[KEY]=UP_Dim

            Recatngles_H[key].append(Dimensions)
            ALL_HRECTS[key2].append(Size)


        DIM = []
        Recatngles_V = {}
        key = MINX.keys()[0]
        Recatngles_V.setdefault(key, [])
        for j in Vtree.vNodeList[0].stitchList:
            k = [j.cell.x, j.cell.y, j.EAST.cell.x, j.NORTH.cell.y,j.cell.type]
            DIM.append(k)
        for i in range(len(MIN_X)):
            Dimensions = []
            for j in range(len(DIM)):

                k=DIM[j]
                if k[0] in MIN_X[i].keys() and k[1] in MIN_Y[i].keys() and k[2] in MIN_X[i].keys() and k[3] in MIN_Y[i].keys():
                    rect = [MIN_X[i][k[0]], MIN_Y[i][k[1]], MIN_X[i][k[2]] - MIN_X[i][k[0]],MIN_Y[i][k[3]] - MIN_Y[i][k[1]],k[4]]
                    Dimensions.append(rect)
            Recatngles_V[key].append(Dimensions)

        ALL_RECTS = {} # to plot resultatnt layouts
        for k, v in Recatngles_H.items():
            ALL_RECTS['H']=v

        Recatngles_V = collections.OrderedDict(sorted(Recatngles_V.items()))
        for k, v in Recatngles_V.items():
            ALL_RECTS['V']=v

        return ALL_HRECTS,ALL_RECTS









       ###################################################################################################################