'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''
import os
import sys
import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import pylab
from sets import Set
from abc import ABCMeta, abstractmethod
import networkx as nx
import numpy as np
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import PatchCollection
import constraintGraph as cg
import CSCG
import constraint


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

    def __init__(self, north, east, south, west, hint, cell,name=None,nodeId=None):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.HINT = hint #this is the pointer to the hint tile of where to start looking for location
        self.cell = cell
        self.nodeId=nodeId

    def printNeighbors(self, printX = False, printY = False, printType = False):
        if self.NORTH is not None: print "N", self.NORTH.cell.printCell(printX, printY, printType)
        if self.EAST is not None: print "E", self.EAST.cell.printCell(printX, printY, printType)
        if self.SOUTH is not None: print "S", self.SOUTH.cell.printCell(printX, printY, printType)
        if self.WEST is not None: print "W", self.WEST.cell.printCell(printX, printY, printType)

    def printTile(self):
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

    def northWest(self, center):
        cc = center.WEST
        while cc.cell.y + cc.getHeight() < center.cell.y + center.getHeight():
            cc = cc.NORTH
        return cc

    def westNorth(self, center):
        cc = center.NORTH
        while cc.cell.x > center.cell.x :#+ center.getWidth():
            cc = cc.WEST
        return cc

    def southEast(self, center):
        cc = center.EAST
        while cc.cell.y > center.cell.y:
            cc = cc.SOUTH
        return cc

    def eastSouth(self, center):
        cc = center.SOUTH
        while cc.cell.x + cc.getWidth() < center.cell.x + center.getWidth():
            cc = cc.EAST
        return cc

    def getNorth(self):
        return self.NORTH

    def getEast(self):
        return self.EAST

    def getSouth(self):
        return self.SOUTH

    def getWest(self):
        return self.WEST

    def getNodeId(self):
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
            #print "1 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.SOUTH is not None:
                #print "1"
                cc = cc.SOUTH
            else:
                break

        cc = self.SOUTH #Walk eastwards along the bottomLeft (SW) corner
        while (cc.EAST!=None and cc.cell.x  < self.cell.x + self.getWidth()):
           # print "2 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.EAST is not None:
                cc = cc.EAST
            else:
                break

        cc = self.WEST #Walk northwards along the bottomLeft (SW) corner
        while (cc.NORTH!=None and cc.cell.y < self.cell.y + self.getHeight()):
            #print "3 appending" , cc.cell.x , " ", cc.cell.y
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
class cornerStitch(object):
    """
    A cornerStitch is a collection of tilees all existing on the same plane. I'm not sure how we're going to handle
    cornerStitchs connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of tiles or anything involving coordinates being passed in instead of a tile
    """
    __metaclass__ = ABCMeta
    def __init__(self, stitchList, level,max_x=None,max_y=None):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.level=level
        if self.level==0:
            self.northBoundary = tile(None, None, None, None, None, cell(0, max_y, "EMPTY"))
            self.eastBoundary = tile(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
            self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
            self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
            self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        else:
            self.boundaries=boundaries



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
            if basis.name!=None:
                Name=basis.name
            else:
                Name=upper.name
            basis.name=Name

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
            if basis.name!=None:
                Name=basis.name
            else:
                Name=eastMost.name
            basis.name=Name


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

    def setEmptyTiles(self, alignment):
        """
        reset all empty tiles according to the algorithm laid out in the paper. alignment should equal "H" or "V" 
        could be optimized
        """
        cellListCopy = copy.copy(self.stitchList)
        accountedCells = []

        accountedCells.append(cellListCopy[cornerStitch.lowestCell(cellListCopy)]) #adding to accounted cells
        del cellListCopy[cornerStitch.lowestCell(cellListCopy)] #removing from the original list so we don't double count

        #print len(cellListCopy)
        #print len(accountedCells)
        return

    def findLayerDimensions(self, boundaries):
        return [self.eastBoundary.cell.x, self.northBoundary.cell.y]

    def deleteTile(self, tile):
        return

    def directedAreaEnumeration(self, x1, y1, x2, y2):
        """
        returns all solid tiles in the rectangle specified. x1y1 = top left corner, x2y2 = topright
        """
        return

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
                   #print("out of bounds 1")
                   return "Failed"
            elif y < cc.cell.y:#y <= cc.cell.y
                if(cc.SOUTH is not None):
                    cc = cc.SOUTH
                else:
                    #print("out of bounds 2")
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
                    #print("out of bounds 4")
                    return "Failed"
        if not ((cc.cell.x <= x and cc.cell.x + cc.getWidth() > x) and (cc.cell.y <= y and cc.cell.y + cc.getHeight() > y)):#(cc.cell.x <= x and cc.cell.x + cc.getWidth() >= x) and (cc.cell.y <= y and cc.cell.y + cc.getHeight() >= y)
            return self.findPoint(x, y, cc)

        return cc

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
        if x < splitCell.cell.x or x > splitCell.cell.x + splitCell.getWidth():
            print "out of bounds, x = ", x
            return
        if splitCell.cell.type!="EMPTY":
            newCell = tile(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type),name=splitCell.name,level=splitCell.level)## level
            self.stitchList.append(newCell) #figure out how to fix this and pass in by reference*
        else:
            newCell = tile(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type))  ## level
            self.stitchList.append(newCell)  # figure out how to fix this and pass in by reference*

        #print newCell, self.stitchList[-1]
        #print "****VSPLIT", newCell is self.stitchList[-1]

        #assign newCell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x
        if cc not in self.boundaries:
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
        if cc not in self.boundaries:
            while cc.cell.x >= x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        if cc not in self.boundaries:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the NORTH pointers for the bottom edge
        if cc not in self.boundaries:
            #cc.SOUTH.cell.printCell(True, True)
            ccWidth = cc.getWidth() #I don't know why, but this solves getWidth() throwing an error otherwise
            while cc not in self.boundaries and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
                cc.NORTH = newCell
                cc = cc.EAST
                if cc not in self.boundaries:
                    ccWidth = cc.getWidth()  # I don't know why, but this solves getWidth() throwing an error otherwise

        return newCell

    def vSplit_2(self, splitCell, x):
        if x < splitCell.cell.x or x > splitCell.cell.x + splitCell.getWidth():
            print "out of bounds, x = ", x
            return
        if splitCell.cell.type!="EMPTY":
            newCell = tile(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type),name=splitCell.name,level=splitCell.level)## level
            self.stitchList.append(newCell) #figure out how to fix this and pass in by reference*
        else:
            newCell = tile(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type))  ## level
            self.stitchList.append(newCell)  # figure out how to fix this and pass in by reference*

        #print newCell, self.stitchList[-1]
        #print "****VSPLIT", newCell is self.stitchList[-1]

        #assign newCell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x
        #if cc not in self.boundaries:
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
        while cc.cell.x >= x:
            cc.SOUTH = newCell
            cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        #if cc not in self.boundaries:
        while cc.cell.y >= newCell.cell.y:
            cc.WEST = newCell
            cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the NORTH pointers for the bottom edge
        #if cc not in self.boundaries:
            #cc.SOUTH.cell.printCell(True, True)
        ccWidth = cc.getWidth() #I don't know why, but this solves getWidth() throwing an error otherwise
        while (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
            cc.NORTH = newCell
            cc = cc.EAST
            if cc not in self.boundaries:
                ccWidth = cc.getWidth()  # I don't know why, but this solves getWidth() throwing an error otherwise

        return newCell

    def hSplit(self, splitCell, y):
        """
        newCell is the top half of the split
        """
        if y < splitCell.cell.y or y > splitCell.cell.y + splitCell.getHeight():
           # print "out of bounds, y = ", y
            return
        if splitCell.cell.type!="EMPTY":
            newCell = tile(None, None, None, None, None, cell(splitCell.cell.x, y, splitCell.cell.type),name=splitCell.name,level=splitCell.level)
            self.stitchList.append(newCell)

        else:
            newCell = tile(None, None, None, None, None, cell(splitCell.cell.x, y, splitCell.cell.type))
            self.stitchList.append(newCell)

            #assign new cell directions
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH = splitCell


        cc = splitCell.WEST
        if cc not in self.boundaries:
            #cc.cell.printCell(True, True)
            while cc.cell.y + cc.getHeight() <= y: #Walk upwards along the old west
                cc = cc.NORTH
        newCell.WEST = cc

        #reassign splitCell N
        splitCell.NORTH = newCell
        #reassign splitCell E
        cc = newCell.EAST
        while cc.cell.y >= newCell.cell.y: #Walk down the right (eastward)edge
            cc = cc.SOUTH
        splitCell.EAST = cc

        #reassign the neighboring cells directional poitners
        cc = newCell.NORTH #reassign the SOUTH pointers for the top edge along the split half

        if cc not in self.boundaries:
            while cc.cell.x >= newCell.cell.x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        if cc not in self.boundaries:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.WEST#reassign the EAST pointers for the right edge

        if cc not in self.boundaries:
            while cc not in self.boundaries and cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
                cc.EAST = newCell
                cc = cc.NORTH

        return newCell

    def hSplit_2(self, splitCell, y):
        """
        newCell is the top half of the split
        """

        if y < splitCell.cell.y or y > splitCell.cell.y + splitCell.getHeight():
            # print "out of bounds, y = ", y
            return
        if splitCell.cell.type != "EMPTY":
            newCell = tile(None, None, None, None, None, cell(splitCell.cell.x, y, splitCell.cell.type),name=splitCell.name,level=splitCell.level)
            self.stitchList.append(newCell)



            # assign new cell directions
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH = splitCell

        cc = splitCell.WEST
        #if cc not in self.boundaries:
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
        while cc.cell.x >= newCell.cell.x:
            print cc.SOUTH.cell.x,cc.SOUTH.cell.y
            cc.SOUTH = newCell
            #print "in",cc.cell.x,cc.cell.y,cc.SOUTH.cell.x,cc.SOUTH.cell.y
            cc = cc.WEST

        cc = newCell.EAST  # reassign the WEST pointers for the right edge
        #if cc not in self.boundaries:
        while cc.cell.y>=newCell.cell.y and cc.cell.y < newCell.cell.y+newCell.getHeight():
            cc.WEST = newCell
            cc = cc.SOUTH

        cc = newCell.WEST  # reassign the EAST pointers for the right edge

        #if cc not in self.boundaries:
        while cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
            cc.EAST = newCell
            cc = cc.NORTH

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
class Node(object):
    """
    Group of tiles .Part of Tree
    """
    __metaclass__ = ABCMeta
    def __init__(self,boundaries,child, stitchList,parent=None,id=None,):
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

    def setEmptyTiles(self, alignment):
        """
        reset all empty tiles according to the algorithm laid out in the paper. alignment should equal "H" or "V"
        could be optimized
        """
        cellListCopy = copy.copy(self.stitchList)
        accountedCells = []

        accountedCells.append(cellListCopy[cornerStitch.lowestCell(cellListCopy)]) #adding to accounted cells
        del cellListCopy[cornerStitch.lowestCell(cellListCopy)] #removing from the original list so we don't double count

        #print len(cellListCopy)
        #print len(accountedCells)
        return

    def findLayerDimensions(self, boundaries):
        return [self.eastBoundary.cell.x, self.northBoundary.cell.y]

    def deleteTile(self, tile):
        return

    def directedAreaEnumeration(self, x1, y1, x2, y2):
        """
        returns all solid tiles in the rectangle specified. x1y1 = top left corner, x2y2 = bottomright
        """


        return

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
            print "out of bounds, x = ", x
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
            # print "out of bounds, y = ", y
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

    #########
class Vnode(Node):
    def __init__(self, boundaries,child,stitchList,parent,id):

        self.stitchList=stitchList
        self.boundaries=boundaries
        self.child=[]
        self.parent=parent
        self.id=id
    def Final_Merge(self):
        #for node in nodelist:
        changeList = []
        changeList1=[]
        # for cell in self.stitchList:

        for rect in self.stitchList:

            #if rect.cell.type == "Type_1":
            #if rect.cell.type=="EMPTY":
            changeList.append(rect)
            #else:
                #changeList1.append(rect)

        list_len = len(changeList)
        c = 0
        #print"LEN",list_len
        #for i in changeList:
            #print "R",i.printTile()
        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                # print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    # print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    # top.cell.type = type
                    # low.cell.type = type
                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
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
                        # print"x=",x
                        mergedcell.type = 'Type_1'
                        changeList.insert(x, mergedcell)
                        #self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
                '''
        list_len1= len(changeList1)
        c = 0
        # print"LEN",list_len
        # for i in changeList:
        # print "R",i.printTile()
        while (len(changeList1) > 1):
            i = 0
            c += 1

            while i < len(changeList1) - 1:
                # print"i=", i, len(changeList)
                j = 0
                while j < len(changeList1):
                    # j=i+1
                    # print"j=", j

                    top = changeList1[j]
                    low = changeList1[i]
                    # top.cell.type = type
                    # low.cell.type = type
                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList1):
                            j += 1

                    else:

                        del changeList1[j]
                        if i > j:
                            del changeList1[i - 1]
                        else:
                            del changeList1[i]
                        x = min(i, j)
                        # print"x=",x
                        mergedcell.type = 'EMPTY'
                        changeList1.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len1:
                break
        #print"len_1", len(changeList)
        #for i in range(len(changeList)):
            #print"Rect", changeList[i].printTile()
            #self.rectifyShadow(changeList[i])
            '''
        return self.stitchList
    def insert(self, start,x1, y1, x2, y2, type,end):
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
        #for rect in self.stitchList:
            #print "I",rect.nodeId
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


        if bottomRight.cell.x == x2:  ## and bottomRight.cell.y==y2 has been added to consider overlapping
            bottomRight = bottomRight.WEST
            # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH
        #print topLeft.cell.x, topLeft.cell.y, bottomRight.cell.x, bottomRight.cell.y
        splitList = []
        splitList.append(bottomRight)
        # print"x=",bottomRight.cell.x, bottomRight.cell.y
        # if bottomRight.SOUTH != self.southBoundary and bottomRight.SOUTH.cell.type == "SOLID" and bottomRight.SOUTH.cell.y+bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type=="SOLID":
        if start!='/':
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
                # print"1"

                if cc not in splitList:
                    splitList.append(cc)
                cc = cc.NORTH
                while cc.cell.x >= x2:
                    cc = cc.WEST
            #print"splitListx2=", len(splitList)
            # if cc.cell.type=="SOLID" and cc.cell.y==y1 or tr.cell.type=="SOLID"  :
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
            #print rect.cell.x,rect.cell.y
            if x2 != rect.cell.x and x2 != rect.EAST.cell.x:

                self.vSplit(rect, x2)

        splitList = []
        splitList.append(topLeft)
        #print "TP",topLeft.cell.y,topLeft.cell.type
        # if topLeft.NORTH != self.northBoundary and topLeft.NORTH.cell.type == "SOLID" and topLeft.NORTH.cell.y == y1 or topLeft.cell.type=="SOLID":
        if start!='/':
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
            #print"in",cc.cell.x,cc.cell.y
            #print"splitListx1=", len(splitList)
            # if cc.cell.type == "SOLID" and cc.cell.y+cc.getHeight() == y2 or bl.cell.type == "SOLID":
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


        #print"splitListx1=", len(splitList)
        for rect in splitList:

            if x1 != rect.cell.x and x1 != rect.EAST.cell.x:
                #print"1", rect.cell.x,rect.cell.y
                self.vSplit(rect, x1)

        ### Horizontal split

        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0])
        if cc.cell.y == y1:
            cc = cc.SOUTH
        # print "xco2=", cc.cell.x
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
        #print"chlen=", len(changeList)
        for rect in changeList:

            i = self.stitchList.index(rect)
            if not rect.NORTH.cell.y == y1:

                self.hSplit(i, y1)

            if not rect.cell.y == y2:
                #print rect.cell.x, rect.cell.y
                self.hSplit(i, y2) # order is vital, again

        if start!='/':
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
            # cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
            cc = self.findPoint(x1, y2, self.stitchList[0])
            # print"resplit1=", cc.cell.x, cc.cell.y, cc.cell.x+cc.getWidth()
            while cc.cell.x + cc.getWidth() <= x2:
                # if cc.SOUTH.cell.type == "SOLID" and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH != self.southBoundary and cc.SOUTH.cell.x+cc.SOUTH.getWidth() != cc.cell.x+cc.getWidth():
                if cc.SOUTH.cell.type == type and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH not in self.boundaries and cc.SOUTH.cell.x + cc.SOUTH.getWidth() != cc.cell.x + cc.getWidth():
                    resplit.append(cc.SOUTH)
                    resplit.append(cc.SOUTH.SOUTH)

                for rect in resplit:
                    # flag = True
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
        # print "xco2=", cc.cell.x
        while cc.cell.x + cc.getWidth() <= x2:
            # if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1:
            if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and start!='/':
                changeList.append(cc.NORTH)
            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH

        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        #print "t",t.cell.y
        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        # print"t.x,y=", t.cell.x, t.cell.y
        # if t.NORTH.cell.type == "SOLID" and t.NORTH.cell.y == y1:
        # changeList.append(t.NORTH)
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
                        # if t.WEST.cell.type == "SOLID" and t.WEST.cell.x + t.WEST.getWidth() == x1:
                        # changeList.append(t.WEST)
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
        #print "cc",cc1.cell.x,cc1.cell.y
        while cc1.cell.x + cc1.getWidth() <= x2:
            # if cc1.SOUTH.cell.type == "SOLID" and cc1.SOUTH.cell.y +cc1.SOUTH.getHeight()== y2:
            if cc1.SOUTH.cell.type == type and cc1.SOUTH.cell.y + cc1.SOUTH.getHeight() == y2 and start!='/':
                changeList.append(cc1.SOUTH)
            cc1 = cc1.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH
        #print"arealistv=", len(changeList)
        if start != '/':
            for i in changeList:
                #print"i",i.cell.x,i.cell.y,i.getHeight(),i.getWidth()
                N=i.findNeighbors()
                for j in N:
                    if j.cell.type==type and j not in changeList:
                        RESP=1
                        changeList.append(j)
                    elif j.nodeId!=0 and j.cell.type==type:
                        RESP=1
        changeList.sort(key=lambda cc: cc.cell.x)
        #print "RESP",RESP
        ##### Merge Algorithm:

        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            if top.cell.y == low.cell.y + low.getHeight() or top.cell.y + top.getHeight() == low.cell.y:
                top.cell.type = type
                low.cell.type = type

                mergedcell = self.merge(top, low)
                if mergedcell == "Tiles are not alligned":
                    # print"-i=", i
                    i += 1
                else:
                    del changeList[i + 1]
                    del changeList[i]
                    # print mergedcell.name
                    changeList.insert(i, mergedcell)
                    # print"i=",i
            else:
                i += 1

        list_len = len(changeList)
        #print"len=", list_len
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                # print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    # print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type

                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
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
                        # print"x=",x
                        changeList.insert(x, mergedcell)

                        self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break

        for x in range(0, len(changeList)):
            #print changeList[x].cell.x,changeList[x].cell.y,changeList[x].getHeight()
            changeList[x].cell.type = type

            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:
            #print "l", len(changeList)

            changeList[0].cell.type = type
            if len(changeList)==1 and RESP==0:
                changeList[0].nodeId=None
            self.rectifyShadow(changeList[0])

            self.set_id_V()

            tile_list=[]
            tile_list.append(changeList[0])
            if start=='/' and end =='/':
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
                            #print "1",i.nodeId
                            N2 = i.findNeighbors()
                            for j in N2:
                                if j not in tile_list:
                                    tile_list.append(j)
                        if i not in tile_list:
                            tile_list.append(i)
            #for rect in tile_list:
                #print "iv",rect.cell.printCell(True,True,True),rect.nodeId



            self.addChild(start,tile_list,Parent,type,RESP,end)

        return self.stitchList
    def addChild(self,start, tile_list, parent, type,RESP,end):

        #if parent==Vtree.vNodeList[0]:
        if start=='/' and end =='/':
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:
                #print "R", rect.cell.x, rect.cell.y

                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            parent.child.append(node)
            Vtree.vNodeList.append(node)
        elif start == '/' and end != '/':
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:
                # print "R", rect.cell.x, rect.cell.y

                if rect.cell.type == type and rect.nodeId==None:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            parent.child.append(node)
            Vtree.vNodeList.append(node)
        elif start!='/' and end !='/':
            ID = 0
            for rect in tile_list:
                # if rect.cell.type == type:
                if rect.cell.type != "EMPTY":
                    if rect.nodeId > ID:
                        ID = rect.nodeId
            #print ID
            for N in Vtree.vNodeList:

                if N.id == ID:
                    #print "N",ID
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
                # print "T",rect.cell.type
                if rect.cell.type == type:
                    rect.nodeId = id
            for rect in tile_list:
                # print "T",rect.cell.type

                # if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.nodeId == id:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    # if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries :
                        boundaries.append(copy.copy(rect))
        elif start != '/' and end == '/':
            ID = 0
            for rect in tile_list:
                # if rect.cell.type == type:
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
                # print "T",rect.cell.type
                if rect.cell.type == type:
                    rect.nodeId = id
            for rect in tile_list:
                # print "T",rect.cell.type

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
            parent.child.append(Node)
            Vtree.vNodeList.append(Node)
        '''
        else:
            Flag = 0
            Flag2 = 0
            counter = 0
            ID = 0
            # print "LEN",len(tile_list)
            for rect in tile_list:
                if rect.cell.type == type:
                    counter += 1
                    if rect.nodeId > ID:
                        ID = rect.nodeId

            if counter > 1 or RESP == 1:
                Flag = 1

            if Flag == 1:
                if ID != 0:
                    for N in Vtree.vNodeList:

                        if N.id == ID:
                            node = N
                            Flag2 = 1
            # print "F",Flag,Flag2
            if Flag2 == 1:

                # Htree.hNodeList.remove(node)

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

                    if rect.cell.type == type and rect not in stitchList:
                        rect.nodeId = id

                        stitchList.append(rect)
                    else:
                        if rect not in boundaries and rect.cell.type != type:
                            boundaries.append(copy.copy(rect))
                if end == '/':
                    Vtree.vNodeList.remove(node)
                    Node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id,
                                 boundaries=boundaries)
                    Parent.child.append(Node)
                    Vtree.vNodeList.append(Node)

                # node = Hnode(parent=ParentH, child=[], stitchList=stitchList, id=id, boundaries=boundaries)
                # parent.child.append(node)
                # Htree.hNodeList.append(node)
            if Flag == 0:
                stitchList = []
                boundaries = []
                id = len(Vtree.vNodeList) + 1
                for rect in tile_list:

                    if rect.cell.type == type:
                        rect.nodeId = id

                        stitchList.append(rect)
                    else:

                        boundaries.append(copy.copy(rect))
                # node = Vnode(parent=Parent, child=[], stitchList=stitchList, id=id, boundaries=boundaries)
                node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id,
                             boundaries=boundaries)
                Parent.child.append(node)
                Vtree.vNodeList.append(node)
        '''
    '''

    def addChild(self, tile_list, parent, type,RESP,end):

        Flag = 0
        Flag2 = 0
        counter = 0
        ID = 0
        # print "LEN",len(tile_list)
        for rect in tile_list:
            if rect.cell.type == type:
                counter += 1
                if rect.nodeId > ID:
                    ID = rect.nodeId


        if counter > 1 or RESP==1:
            Flag = 1

        if Flag == 1:
            if ID != 0:
                for N in Vtree.vNodeList:

                    if N.id == ID:
                        node = N
                        Flag2 = 1
        #print "F",Flag,Flag2
        if Flag2 == 1:

            #Htree.hNodeList.remove(node)

            id = node.id
            stitchList=node.stitchList
            boundaries=node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries or rect.cell.type==type:
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)


            for rect in tile_list:

                if rect.cell.type == type and rect not in stitchList:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    if rect not in boundaries and rect.cell.type!=type:

                        boundaries.append(copy.copy(rect))
            if end == '/':
                Vtree.vNodeList.remove(node)
                Node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id,boundaries=boundaries)
                Parent.child.append(Node)
                Vtree.vNodeList.append(Node)

            #node = Hnode(parent=ParentH, child=[], stitchList=stitchList, id=id, boundaries=boundaries)
            #parent.child.append(node)
            #Htree.hNodeList.append(node)
        if Flag == 0:
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))
            #node = Vnode(parent=Parent, child=[], stitchList=stitchList, id=id, boundaries=boundaries)
            node = Vnode(parent=Parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            Parent.child.append(node)
            Vtree.vNodeList.append(node)
    '''

    """
    def addChild(self,tile_list,parent,type):
        #print parent.id
        Flag = 0
        Flag2 = 0
        counter = 0

        ID=0
        for rect in tile_list:

            if rect.cell.type == type:

                counter += 1
                if rect.nodeId>ID:
                    ID=rect.nodeId
        print "ID",ID

        if counter > 1:
            Flag = 1
        if Flag == 1:
            if ID!=0:
                for N in Vtree.vNodeList:

                    if N.id == ID:
                        node = N
                        Flag2 = 1

            '''
            for rect in tile_list:
                print "NODE", rect.nodeId


                if rect.nodeId != 0:

                    for N in Vtree.vNodeList:
                        print "N", N.id, rect.cell.x, rect.cell.y, rect.nodeId
                        if N.id == ID:
                            node = N
                            Flag2 = 1
                            #print "!"
                            #print node

                            for rect in node.boundaries:
                                print "RR1", rect.cell.x, rect.cell.y, rect.getHeight(), rect.getWidth()
                            break
            '''
        print"F", Flag,Flag2
        if Flag2 == 1:
            #print "1"
            #for i in node.stitchList:
                #print "i", i.cell.printCell(True, True,True)
            Vtree.vNodeList.remove(node)
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList) + 1
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id


                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))
            node = Vnode(parent=parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            #NODE = copy.deepcopy(node)
            parent.child.append(node)
            Vtree.vNodeList.append(node)
        if Flag == 0:
            stitchList = []
            boundaries = []
            id = len(Vtree.vNodeList)+1
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId =id
                    print "id", id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Vnode(parent=parent, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            #NODE = copy.deepcopy(node)

            parent.child.append(node)
            Vtree.vNodeList.append(node)

        '''
        Flag=0
        for rect in tile_list:
            if rect.cell.type!="EMPTY":
                if rect.cell.type!=type:
                    Flag2=1
            else:
                Flag2=0
        if Flag2==0:
            for rect in tile_list:

                if rect.nodeId != None:

                    for N in  Vtree.vNodeList:
                        #print "N",N
                        if N.id==rect.nodeId:
                            node = N
                            Flag = 1

            #if Flag==1:
                    #if node!=None:
                            for rect in node.stitchList:
                                if rect not in self.stitchList:
                                    node.stitchList.remove(rect)
                            for rect in tile_list:
                                if rect.cell.type == type:
                                    if rect not in node.stitchList:
                                        node.stitchList.append(rect)
                                        rect.nodeId = node.id

                                else:
                                    #print type(node.boundaries)
                                    if rect not in node.boundaries:
                                        node.boundaries.append(rect)

        if Flag==0 or Flag2==1:
            stitchList=[]
            boundaries=[]
            id=len(Vtree.vNodeList)+1
            for rect in tile_list:
                if rect.cell.type==type:
                    rect.nodeId=id
                    RECT=copy.copy(rect)

                    stitchList.append(RECT)
                else:
                    RECT=copy.copy(rect)
                    boundaries.append(RECT)
            node=Vnode(parent=Parent,child=[],stitchList=stitchList,id=id,boundaries=boundaries)
            parent.child.append(node)
            Vtree.vNodeList.append(node)
        '''


        """


    def rectifyShadow(self, caster):
        """
        this checks the NORTH and SOUTH of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        """
        changeSet = []

        cc = caster.NORTH  # recitfy north side, walking downwards

        while (cc not in self.boundaries and cc.cell.x >= caster.cell.x):
            # if cc.NORTH==self.northBoundary or cc.NORTH.cell.type=="EMPTY":
            changeSet.append(cc)
            cc = cc.WEST
        #print "len=", len(changeSet)
        i = 0
        j = 1
        while j < len(changeSet):  # merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            #if topCell.NORTH == lowerCell.NORTH:
            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                if j < len(changeSet):  # there was a '-1'
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell
            # if j < len(changeSet) -1:
            # j += 1
            '''
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1
            '''

        cc = caster.SOUTH  # recitfy SOUTH side, walking eastwards
        changeSet = []
        # print"caster=",caster.cell.x+caster.getHeight()

        while (cc not in self.boundaries and cc.cell.x < caster.cell.x + caster.getWidth()):
            # if cc.SOUTH == self.southBoundary or cc.SOUTH.cell.type == "EMPTY":
            changeSet.append(cc)
            cc = cc.EAST
        # print "lenr=", len(changeSet)

        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet):  # merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            #if topCell.SOUTH == lowerCell.SOUTH:
            mergedCell = self.merge(topCell, lowerCell)

            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                # print "i = ", i
                if j < len(changeSet) - 1:
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell
                # if j < len(changeSet) - 1:
                # j += 1
            '''
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1
            '''

        return

    """
    def areaSearch(self, x1, y1, x2, y2):

        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)        
        this is designed with vertically aligned space assumptions in mind

        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(bottom right) corner

        if cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        #elif secondCorner.cell.type == "SOLID":
            #return True
        elif cc.cell.y >y2:
            return True

        #elif cc.cell.y + cc.getHeight() < y1:
            #return True  # the corner cell is empty but touches a solid cell within the search area


        while(cc.EAST.cell.x < x2):
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.y + cc.getHeight() < y1:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.EAST #check the next rightmost cell
            while (cc.cell.y + cc.getHeight() < y2): #making sure that the CurrentCell's right edge lays within the area
                cc = cc.NORTH # if it doesn't, traverse the top right stitch to find the next cell of interest

        return False
    """

    ### NEW AREA SEARCH
    def areaSearch(self, x1, y1, x2, y2,type):
        cc = self.findPoint(x1, y1, self.stitchList[0])  # the tile that contains the first corner point

        sc = self.findPoint(x2, y2, self.stitchList[0])  # the tile that contains the second(bottom right) corner
        if cc.cell.y == y1:
            cc = cc.SOUTH

            while cc.cell.x + cc.getWidth() < x1:  # and cc.cell.type=="SOLID"
                cc = cc.EAST
        #print "CC", cc.cell.x, cc.cell.y, cc.cell.type
        # if cc.cell.type == "SOLID":
        if cc.cell.type == type:

            #print"TR"
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.y > y2:
            return True  # the corner cell is empty but touches a solid cell within the search area

        cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.x < x2):
            # if cc.cell.y<y1 and cc.cell.type=="SOLID":
            # return True ## these 2 lines have been commented out
            while (cc.cell.y + cc.getHeight() > y2):
                # if cc.cell.y<y1 and cc.cell.type=="SOLID":
                if cc.cell.y < y1 and cc.cell.type == type:
                    return True
                if cc.SOUTH not in self.boundaries:
                    cc = cc.SOUTH
                else:
                    break
            cc = cc.EAST
        return False



    def set_id_V(self):  ########## Setting id for all type 1 blocks
        global VID
        for rect in self.stitchList:
            if rect.cell.id==None and rect.cell.type!="EMPTY":

                rect.cell.id=VID+1

                VID+=1
        return
class Hnode(Node):
    def __init__(self, boundaries, child, stitchList, parent, id):

        self.stitchList = stitchList
        self.boundaries = boundaries
        self.child = []
        self.parent = parent
        self.id = id

    def Final_Merge(self):
        #for node in nodelist:
        changeList = []
        #changeList1=[]
        # for cell in self.stitchList:

        for rect in self.stitchList:

            #if rect.cell.type == "Type_1":
            #if rect.cell.type=="EMPTY":
            changeList.append(rect)
            #else:
                #changeList1.append(rect)

        list_len = len(changeList)
        c = 0
        #print"LEN",list_len
        #for i in changeList:
            #print "R",i.printTile()
        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                #print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    #print"j=", j

                    top = changeList[j]
                    if changeList[i] !=None:
                        low = changeList[i]
                    # top.cell.type = type
                    # low.cell.type = type
                    #print"topx=", top.cell.x, top.cell.y
                    #print"lowx=", low.cell.x, low.cell.y
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
                        #print"x=",x
                        mergedcell.type = 'Type_1'
                        #print"11"
                        changeList.insert(x, mergedcell)
                        #self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1

                i += 1

            if c == list_len:
                break
        '''
        list_len1= len(changeList1)
        c = 0
        # print"LEN",list_len
        # for i in changeList:
        # print "R",i.printTile()
        while (len(changeList1) > 1):
            i = 0
            c += 1

            while i < len(changeList1) - 1:
                # print"i=", i, len(changeList)
                j = 0
                while j < len(changeList1):
                    # j=i+1
                    # print"j=", j

                    top = changeList1[j]
                    low = changeList1[i]
                    # top.cell.type = type
                    # low.cell.type = type
                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j < len(changeList1):
                            j += 1

                    else:

                        del changeList1[j]
                        if i > j:
                            del changeList1[i - 1]
                        else:
                            del changeList1[i]
                        x = min(i, j)
                        # print"x=",x
                        mergedcell.type = 'EMPTY'
                        changeList1.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len1:
                break
        #print"len_1", len(changeList)
        #for i in range(len(changeList)):
            #print"Rect", changeList[i].printTile()
            #self.rectifyShadow(changeList[i])
            '''
        return self.stitchList

    def insert(self,start, x1, y1, x2, y2, type,end):

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
            #print"1"
            RESP=1


        # step 1: hsplit y1 and y2
        #print "IN",x1,y1,x2,y2
        #print "start",start
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

        # if cc.WEST != self.westBoundary and cc.WEST.cell.type=="SOLID" and cc.WEST.cell.x+cc.WEST.getWidth()==x1 or cc.cell.type=="SOLID":
        if start!='/':
            if cc.WEST not in self.boundaries and cc.WEST.cell.type == type and cc.WEST.cell.x + cc.WEST.getWidth() == x1 or cc.cell.type == type:
                cc1 = cc.WEST
                while cc1.cell.y + cc1.getHeight() < y1:
                    cc1 = cc1.NORTH
                # print "testwx", cc1.cell.x
                splitList.append(cc1)
                # if cc1.cell.type=="SOLID" and cc1.cell.x+cc1.getWidth()==x1:
                cc2 = cc1.WEST
                # print"cc2=",cc2.cell.y+cc2.getHeight()
                while cc2 not in self.boundaries and cc2.cell.y + cc2.getHeight() < y1:
                    cc2 = cc2.NORTH
                if cc2 not in self.boundaries:
                    splitList.append(cc2)
        # print"cc.x",cc.cell.x

            while cc.cell.x <= tr.cell.x and cc not in self.boundaries:  # it was only <x2
                if cc not in splitList:
                    # print "testx",cc.cell.x+cc.getWidth()
                    splitList.append(cc)

                cc = cc.EAST
                # print"cc.x2", cc.cell.y
                while cc.cell.y >= y1 and cc not in self.boundaries:  # previously it was >y1
                    cc = cc.SOUTH
        #print"splitListy1=", len(splitList),splitList[0].cell.x,splitList[0].cell.y
        # if cc.cell.type=="SOLID" and cc.cell.x==x2 and cc!=self.eastBoundary or tr.cell.type=="SOLID" :##and tr.cell.y!=y1 and cc!=self.eastBoundary)
            if cc.cell.type == type and cc.cell.x == x2 and cc not in self.boundaries or tr.cell.type == type:  ##and tr.cell.y!=y1 and cc!=self.eastBoundary)
                # print "testex", cc.cell.x
                splitList.append(cc)

                if cc.EAST not in self.boundaries:
                    cc = cc.EAST

                    while cc.cell.y >= y1:  # previously it was >y1
                        cc = cc.SOUTH

                    splitList.append(cc)



        for rect in splitList:
            #print "y",rect.cell.y
            i = self.stitchList.index(rect)
            if y1 != rect.cell.y and y1 != rect.NORTH.cell.y: self.hSplit(i, y1)



        if bottomRight.cell.x == x2:  ## this part has been corrected (reinserted to consider overlap)
            bottomRight = bottomRight.WEST
            # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH
        # print"bot=", bottomRight.cell.y
        splitList = []
        splitList.append(bottomRight)
        cc = bottomRight
        if start!='/':
        # if cc.EAST!= self.eastBoundary and cc.EAST.cell.type=="SOLID" and cc.EAST.cell.x==x2 or cc.cell.type=="SOLID":
            if cc.EAST not in self.boundaries and cc.EAST.cell.type == type and cc.EAST.cell.x == x2 or cc.cell.type == type:
                cc1 = cc.EAST
                while cc1.cell.y > y2:
                    cc1 = cc1.SOUTH
                splitList.append(cc1)
                # if cc1.cell.type=="SOLID" and cc1.cell.x==x2:
                if cc1.cell.type == type and cc1.cell.x == x2:
                    cc2 = cc1.EAST
                    while cc2.cell.y > y2:
                        cc2 = cc2.SOUTH
                    splitList.append(cc2)

            while cc.cell.x >= x1 and cc not in self.boundaries:  # it was cc.WEST!= (previously >x1)
                cc = cc.WEST

                if cc not in self.boundaries:
                    while cc.cell.y + cc.getHeight() <= y2:  # previously it was <y2
                        cc = cc.NORTH
                if cc not in splitList and cc.cell.type==type: ########################### added  and cc.cell.type==type
                    splitList.append(cc)
        #print "L", len(splitList)
        #print"cc2.x", cc.cell.x
        # if cc.cell.type=="SOLID" and cc.cell.x+cc.getWidth()>=x1 or bl.cell.type=="SOLID"   :#previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
            if cc.cell.type == type and cc.cell.x + cc.getWidth() >= x1 or bl.cell.type == type:  # previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
                if cc not in splitList:
                    splitList.append(cc)

                if cc.WEST not in self.boundaries:
                    cc1 = cc.WEST
                    while cc1.cell.y + cc1.getHeight() <= y2:  # previously it was <y2
                        cc1 = cc1.NORTH
                    splitList.append(cc1)


        #print"splitListy2=", len(splitList),splitList[0].cell.x,splitList[0].cell.y
        for rect in splitList:
            # print "height=",rect.cell.y+rect.getHeight()
            #print rect.cell.x,rect.cell.y
            i=self.stitchList.index(rect)
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y: self.hSplit(i, y2)


        #print"splitListy1=", len(self.stitchList)

        changeList = []
        # step 2: vsplit x1 and x2
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        # print x1,y1

        while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
            cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH
        # print"vlistx1=", len(changeList)

        # changeList = []
        # step 2: vsplit x1 and x2
        cc = self.findPoint(x2, y1, self.stitchList[0]).SOUTH

        if cc.cell.x == x2:
            cc = cc.WEST
        while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
            cc = cc.EAST

        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH
            #print "CC", cc.cell.y

        #changeList=self.AreaSearch(x1,y1,x2,y2)
        #print"vlistx2=", len(changeList),changeList[0].cell.x,changeList[0].cell.y,changeList[0].getWidth(),changeList[0].getHeight()

        for rect in changeList:  # split vertically
            #print rect.cell.x, rect.cell.y, rect.getHeight(), rect.getWidth()
            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2)  # do not reorder these lines

            #print len(self.stitchList)

            if not rect.cell.x == x1: self.vSplit(rect, x1)  # do not reorder these lines


        #print"splitListy1=", len(self.stitchList)
        ### Re-Splitting for overlapping cases
        #for foo in self.stitchList:
            #if foo.cell.type!="EMPTY":
                #print "foo",foo.cell.x,foo.cell.y,foo.getWidth(),foo.getHeight()
        if start!='/':
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
                    if cc1.cell.x == x1 and cc1.WEST.cell.type==type :##########3and cc1.WEST.cell.type==type added
                        resplit.append(cc1.WEST)
                        # if cc1.WEST.cell.type=="SOLID":
                        if cc1.WEST.cell.type == type:
                            resplit.append(cc1.WEST.WEST)
                    if cc1.EAST.cell.x == x2 :#####and cc1.EAST.cell.type==type
                        resplit.append(cc1.EAST)
                        # if cc1.EAST.cell.type=="SOLID":
                        if cc1.EAST.cell.type == type:
                            resplit.append(cc1.EAST.EAST)

                    cc1 = cc1.WEST


                if len(resplit) > 1:
                    for foo in resplit:
                        #print"foo", foo.cell.x,foo.cell.y
                        if foo.cell.y + foo.getHeight() > min_y:
                            # if foo.cell.y+foo.getHeight()!= min_y:
                            #print"split"
                            if min_y != foo.cell.y and min_y != foo.NORTH.cell.y:
                                #RESP=1
                                k=self.stitchList.index(foo)
                                self.hSplit(k, min_y)
                #print cc.cell.x,cc.cell.y
                if cc.NORTH not in self.boundaries:
                    cc = cc.NORTH
                     #print"1"
                else:
                    break

        # changeList = []

        changeList = []
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        #print t.cell.printCell(True,True)
        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        # if t.WEST.cell.type=="SOLID" and t.WEST.cell.x+t.WEST.getWidth()==x1:
        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1:
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
                    if child.cell.type == type and child.cell.x == x2:
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
                        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1 and start!='/':
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
        print "arealist=", len(changeList)
        for foo in changeList:
            print "fpp",foo.cell.x,foo.cell.y,foo.cell.type
        if start!='/':
            for i in changeList:
                #print"i",i.cell.x,i.cell.y,i.getHeight(),i.getWidth(),i.cell.type
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
            # print"topx=", top.cell.x, top.cell.y
            # print"lowx=", low.cell.x, low.cell.y
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
        #print"len=",list_len
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                # print"i=",i,len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    # print"j=", j

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
                        # print"x=",x
                        changeList.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        #print"len_1",len(changeList)

        ######
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            #print"topx=", top.cell.x, top.cell.y
            #print"lowx=", low.cell.x, low.cell.y
            # if top.cell.x == low.cell.x + low.getWidth() or top.cell.x + top.getWidth() == low.cell.x:
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

        #for foo in changeList:
            #foo.cell.printCell(True, True)
        for x in range(0, len(changeList)):
            changeList[x].cell.type = type
            # print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:

            changeList[0].cell.type = type
            #if start!='/':
            if len(changeList)==1 and RESP==0:
                changeList[0].nodeId = None
            #changeList[0].nodeId=None
            #print changeList[0].cell.x
            self.rectifyShadow(changeList[0])
            self.set_id()
            rect = changeList[0]

            tile_list = []
            tile_list.append(changeList[0])
            if start == '/' and end == '/':
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
            '''
            for rect in changeList:
                N = rect.findNeighbors()
                for i in N:
                    if i.cell.type==type:

                        N2=i.findNeighbors()
                        for j in N2:
                            if j not in tile_list:
                                tile_list.append(j)
                    if i not in tile_list:
                        tile_list.append(i)
            '''
            #for i in tile_list:
                #print"i", i.cell.x, i.cell.y, i.getHeight(), i.getWidth(),i.cell.type

            self.addChild(start,tile_list, ParentH, type,RESP,end)



        return self.stitchList

    def addChild(self,start, tile_list, parent, type,RESP,end):

        for i in tile_list:
            print "i", i.cell.printCell(True,True,True),i.nodeId
        if start=='/' and end =='/':
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

            parent.child.append(node)
            Htree.hNodeList.append(node)
        elif start == '/' and end != '/':
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

            parent.child.append(node)
            Htree.hNodeList.append(node)
        elif start!='/' and end !='/':
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
        elif start != '/' and end == '/':
            ID=0
            for rect in tile_list:
                # if rect.cell.type == type:
                if rect.cell.type != "EMPTY":
                    if rect.nodeId>ID:
                        ID=rect.nodeId

            print ID
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
            parent.child.append(Node)
            Htree.hNodeList.append(Node)
        '''
        else:
            Flag = 0
            Flag2 = 0
            counter = 0
            ID = 0
            # print "LEN",len(tile_list)

            for rect in tile_list:
                if rect.cell.type == type:
                    # if rect.cell.type !="EMPTY":
                    # print "R",rect.cell.x,rect.cell.y
                    counter += 1
                    if rect.nodeId > ID:
                        ID = rect.nodeId
            # print "RES",RESP
            if counter > 1 or RESP == 1:
                # if counter > 1 or end!='/':
                Flag = 1

            if Flag == 1:
                if ID != 0:
                    for N in Htree.hNodeList:

                        if N.id == ID:
                            node = N
                            Flag2 = 1
            # print "F",Flag,Flag2

            # if end!=None:
            if Flag2 == 1:
                # i=Htree.hNodeList.index(node)
                # Htree.hNodeList.remove(node)

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
                    # print "T",rect.cell.type

                    # if rect.cell.type == type and rect not in stitchList:
                    if rect not in stitchList and rect.cell.type != "EMPTY":
                        rect.nodeId = id

                        stitchList.append(rect)
                    else:
                        # if rect not in boundaries and rect.cell.type!=type:
                        if rect not in boundaries and rect.cell.type != type:
                            boundaries.append(copy.copy(rect))
                if end == '/':
                    Htree.hNodeList.remove(node)
                    Node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id,
                                 boundaries=boundaries)
                    parent.child.append(Node)
                    Htree.hNodeList.append(Node)

                # node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
                # parent.child.append(node)
                # Htree.hNodeList.insert(i,node)
            if Flag == 0:
                stitchList = []
                boundaries = []
                id = len(Htree.hNodeList) + 1
                for rect in tile_list:
                    print "R", rect.cell.x, rect.cell.y

                    if rect.cell.type == type:
                        rect.nodeId = id

                        stitchList.append(rect)
                    else:

                        boundaries.append(copy.copy(rect))

                node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id,
                             boundaries=boundaries)

                parent.child.append(node)
                Htree.hNodeList.append(node)
        '''





    '''
    def addChild(self, tile_list, parent, type):
            Flag = 0
        Flag2 = 0
        counter = 0
        ID = 0
        #print "LEN",len(tile_list)

        for rect in tile_list:
            if rect.cell.type == type:
            #if rect.cell.type !="EMPTY":
                #print "R",rect.cell.x,rect.cell.y
                counter += 1
                if rect.nodeId > ID:
                    ID = rect.nodeId
        #print "RES",RESP
        if counter > 1 or RESP==1:
        #if counter > 1 or end!='/':
            Flag = 1

        if Flag == 1:
            if ID != 0:
                for N in Htree.hNodeList:

                    if N.id == ID:
                        node = N
                        Flag2 = 1
        #print "F",Flag,Flag2


        #if end!=None:
        if Flag2 == 1:
            #i=Htree.hNodeList.index(node)
            #Htree.hNodeList.remove(node)

            id = node.id
            stitchList=node.stitchList
            boundaries=node.boundaries
            for rect in boundaries:
                if rect not in self.boundaries or rect.cell.type==type:
                    boundaries.remove(rect)
            for rect in stitchList:
                if rect not in self.stitchList:
                    stitchList.remove(rect)

            for rect in tile_list:
                #print "T",rect.cell.type

                #if rect.cell.type == type and rect not in stitchList:
                if rect not in stitchList and rect.cell.type!="EMPTY":
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    #if rect not in boundaries and rect.cell.type!=type:
                    if rect not in boundaries and rect.cell.type != type:

                        boundaries.append(copy.copy(rect))
            if end=='/':
                Htree.hNodeList.remove(node)
                Node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id,boundaries=boundaries)
                parent.child.append(Node)
                Htree.hNodeList.append(Node)

            #node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            #parent.child.append(node)
            #Htree.hNodeList.insert(i,node)
        if Flag == 0:
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:
                print "R",rect.cell.x,rect.cell.y

                if rect.cell.type == type:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:

                    boundaries.append(copy.copy(rect))

            node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)

            parent.child.append(node)
            Htree.hNodeList.append(node)
        ################################################################################################################


        Flag = 0
        Flag2=0
        counter=0
        ID=0
        #print "LEN",len(tile_list)
        for rect in tile_list:
            if rect.cell.type==type:
                counter+=1
                if rect.nodeId>ID:
                    ID=rect.nodeId

        if counter>1:
            Flag=1

        if Flag == 1:
            if ID != 0:
                for N in Htree.hNodeList:

                    if N.id == ID:
                        node = N
                        Flag2 = 1


        if Flag2==1:

            Htree.hNodeList.remove(node)
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:
                
                if rect.cell.type == type:
                    rect.nodeId = id
                   
                    stitchList.append(rect)
                else:
                  
                    boundaries.append(copy.copy(rect))

         

           
            node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            parent.child.append(node)
            Htree.hNodeList.append(node)
        if Flag == 0:
            stitchList = []
            boundaries = []
            id = len(Htree.hNodeList) + 1
            for rect in tile_list:

                if rect.cell.type == type:
                    rect.nodeId = id

                    stitchList.append(rect)
                else:
                    
                    boundaries.append(copy.copy(rect))

            node = Hnode(parent=ParentH, child=[], stitchList=copy.deepcopy(stitchList), id=id, boundaries=boundaries)
            
            parent.child.append(node)
            Htree.hNodeList.append(node)

        '''


    def rectifyShadow(self, caster):
        """
                this checks the EAST and WEST of caster, to see if there are alligned empty cells that could be merged.
                Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other

                Re-write this to walk along the E and W edges and try to combine neighbors sequentially
                """
        changeSet = []

        cc = caster.EAST  # recitfy east side, walking downwards

        while (cc not in self.boundaries and cc.cell.y >= caster.cell.y):
            # if cc.EAST==self.eastBoundary or cc.EAST.cell.type=="EMPTY":#this condition has been added here
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
                if j < len(changeSet):  # there was a '-1'
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell
            '''
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1

                # print "len3=", len(changeSet)
                # if j < len(changeSet) -1:## these 2 lines have been commented out
                # j += 1
            '''

        cc = caster.WEST  # recitfy west side, walking upwards
        changeSet = []
        #print "CC",cc.cell.x,cc.cell.y

        while (cc not in self.boundaries and cc.cell.y < caster.cell.y + caster.getHeight()):
            # while cc.cell.type=="SOLID":## 2 lines have been included here
            # cc=cc.NORTH
        #while (cc.cell.type!=None and cc.cell.y < caster.cell.y + caster.getHeight()):
            # if cc.WEST==self.westBoundary or cc.WEST.cell.type=="EMPTY" :#this condition has been added here (or cc.WEST.cell.y!=cc.cell.y and cc.WEST.cell.type=="SOLID")
            changeSet.append(cc)
            cc = cc.NORTH
        #print "lenw=", len(changeSet)

        #for foo in changeSet:
            #foo.cell.printCell(True, True)
            #print"w=",foo.getWidth()

        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet):  # merge all cells with the same width along the eastern side
            topCell = changeSet[i]
            #topCell.cell.printCell(True, True)
            lowerCell = changeSet[j]
            #lowerCell.cell.printCell(True, True)
            #if topCell.WEST == lowerCell.WEST:
            #if topCell.EAST == lowerCell.EAST:
            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned":  # the tiles couldn't merge because they didn't line up
                i += 1
                # print "i = ", i
                if j < len(changeSet) - 1:
                    j += 1
            else:
                changeSet[i] = mergedCell
                del changeSet[j]
                # if j < len(changeSet) -1: ## these 2 lines have been commented out
                # j += 1
            '''
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1
            '''

        return

    def areaSearch(self, x1, y1, x2, y2,type):

        cc = self.findPoint(x1, y1, self.stitchList[0])  # the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2,self.stitchList[0])  # the tile that contains the second(bottom right)corner

        # if  cc.cell.type == "SOLID" and cc.cell.y!=y1 :## cc.cell.x!=x1 and cc.cell.y!=y1 have been added ## cc.cell.x!=x has been deleted
        if cc.cell.type == type and cc.cell.y != y1:  ## cc.cell.x!=x1 and cc.cell.y!=y1 have been added ## cc.cell.x!=x has been deleted
            return True
        elif cc.cell.x + cc.getWidth() < x2 and cc.cell.y != y1 and cc.cell.x != x1:  ## cc.cell.x!=x1 and cc.cell.y!=y1 have been added
            return True
        cc = cc.SOUTH
        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while (
                    cc.cell.x + cc.getWidth() <= x1):  ## = has been inserted after changing point finding  # making sure that the CurrentCell's right edge lays within the area
                cc = cc.EAST  # if it doesn't, traverse the top right stitch to find the next cell of interest
            # if cc.cell.type == "SOLID":
            if cc.cell.type == type:
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x + cc.getWidth() < x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH  # check the next lowest cell
        return False
    '''
    def Final_Merge(self):
        changeList = []
        # for cell in self.stitchList:

        for rect in self.stitchList:
            #if rect.cell.type == "Type_1":
            if rect.cell.type !="EMPTY":
                changeList.append(rect)
        # print len(changeList)
        list_len = len(changeList)

        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1
            while i < len(changeList) - 1:
                # print"i=",i,len(changeList)
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
                        # print"x=",x
                        changeList.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        # print"len_1",len(changeList)

        #for i in range(len(changeList)):
            #self.rectifyShadow(changeList[i])
        return
    '''
    def set_id(self):  ########## Setting id for all type 1 blocks
        global HID
        for rect in self.stitchList:
            #print "H",rect.cell.x,rect.cell.y,rect.cell.type
            if  rect.cell.type!="EMPTY":

                #print rect.cell.x,rect.cell.y
                rect.cell.id=HID+1
                #print"THID", rect.cell.id
                HID+=1
        return


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




########################################################################################################################
if __name__ == '__main__':
    global VID,HID
    VID=0
    HID=0
    Tile1=tile(None, None, None, None, None, cell(0, 0, "EMPTY"),nodeId=1)
    TN=tile(None, None, None, None, None, cell(0, 60, None))
    TE = tile(None, None, None, None, None, cell(60, 0,  None))
    TW= tile(None, None, None, None, None, cell(-1000, 0,  None))
    TS = tile(None, None, None, None, None, cell(0,-1000,  None))
    Tile1.NORTH=TN
    Tile1.EAST=TE
    Tile1.WEST=TW
    Tile1.SOUTH=TS
    Boundaries=[]
    Stitchlist=[]
    Stitchlist.append(Tile1)
    Boundaries.append(TN)
    Boundaries.append(TE)
    Boundaries.append(TW)
    Boundaries.append(TS)
    Vnode0=Vnode(boundaries=Boundaries,child=None,stitchList=Stitchlist,parent=None,id=1)
    Vtree=Tree(hNodeList=None,vNodeList=[Vnode0])
    Tile2 = tile(None, None, None, None, None, cell(0, 0, "EMPTY"), nodeId=1)
    TN2 = tile(None, None, None, None, None, cell(0, 60, None))
    TE2 = tile(None, None, None, None, None, cell(60, 0, None))
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
    Hnode0=Hnode(boundaries=Boundaries_H,child=None,stitchList=Stitchlist_H,parent=None,id=1)
    Htree = Tree(hNodeList=[Hnode0],vNodeList=None)





    if len(sys.argv) > 1:
        testfile = sys.argv[1]  # taking input from command line

        f = open(testfile, "rb")  # opening file in binary read mode
        index_of_dot = testfile.rindex('.')  # finding the index of (.) in path

        testbase = os.path.basename(testfile[:index_of_dot])  # extracting basename from path
        testdir = os.path.dirname(testfile)  # returns the directory name of file
        #print testbase
        if not len(testdir):
            testdir = '.'

        list = []
        Input = []
        # a = ["blue","red","green","yellow","black","orange"]
        i = 0
        for line in f.read().splitlines():  # considering each line in file

            c = line.split(',')  # splitting each line with (,) and inserting each string in c
            #print"C",c
            if len(c) > 4:
                #In = [int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4]]
                In = line.split(',')
                Input.append(In)
                # emptyVExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])  # taking parameters of insert function (4 coordinates as integer and type of cell as string)
                # emptyHExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])

                #list.append(patches.Rectangle(
                    #(int(c[0]), int(c[3])), (int(c[2]) - int(c[0])), (int(c[1]) - int(c[3])),

                    ##))
    else:
        exit(1)
    print Input

    while(len(Input)>0):
        inp=Input.pop(0)

        print inp

        if inp[1] == "." and inp[2]!=".":

            for i in reversed(Htree.hNodeList):
                if i.parent.id==1:
                    #print"ID", i.id
                    ParentH = i
                    break
            CHILDH=ParentH
            #print "PAR",CHILDH.id,len(CHILDH.stitchList)

            #CHILDH=copy.copy(ParentH)
            #CHILDH=Hnode(boundaries =ParentH.boundaries, child = ParentH.child, stitchList =ParentH.stitchList , parent =ParentH.parent, id = ParentH.id)
            CHILDH.insert(inp[0],int(inp[2]), int(inp[3]), int(inp[4]), int(inp[5]), inp[6],inp[7])

            #L = len(Vtree.vNodeList)
            #print int(inp[1]), int(inp[2]), int(inp[3]), int(inp[4]), inp[5]

            for i in reversed(Vtree.vNodeList):
                if i.parent.id==1:
                    #print"ID", i.id
                    Parent = i
                    break
            CHILD=Parent
            #print "PAR",Parent.id
            #CHILD=Vnode(boundaries =Parent.boundaries, child = Parent.child, stitchList = Parent.stitchList, parent =Parent.parent, id = Parent.id)
            CHILD.insert(inp[0],int(inp[2]), int(inp[3]), int(inp[4]), int(inp[5]), inp[6],inp[7])

        if inp[1] == "." and inp[2]==".":

            #L = len(Vtree.vNodeList)
            #print int(inp[2]), int(inp[2]), int(inp[3]), int(inp[4]), inp[5]
            for i in reversed(Htree.hNodeList):
                if i.parent.id==1:
                    #print"ID", i.id
                    med = i
                    break
            print med
            ParentH=med.child[-1]
            CHILDH=ParentH
            #CHILDH = copy.copy(ParentH)
            #CHILDH=Hnode(boundaries =ParentH.boundaries[:], child = ParentH.child[:], stitchList = ParentH.stitchList[:], parent =ParentH.parent, id =ParentH.id+1)
            CHILDH.insert(inp[0],int(inp[3]), int(inp[4]), int(inp[5]), int(inp[6]), inp[7],inp[8])

            for i in reversed(Vtree.vNodeList):
                if i.parent.id==1:
                    #print"ID", i.id
                    med = i
                    break

            Parent=med.child[-1]
            CHILD=Parent
            #CHILD=Vnode(boundaries =copy.copy(Parent.boundaries), child = copy.copy(Parent.child), stitchList = copy.copy(Parent.stitchList), parent =copy.copy(Parent.parent), id =Parent.id)
            CHILD.insert(inp[0],int(inp[3]), int(inp[4]), int(inp[5]), int(inp[6]), inp[7],inp[8])

        if inp[1]!=".":
            start = inp[0]
            Parent = Vtree.vNodeList[0]
            #for i in Parent:
            #print"VL", len(Parent.stitchList)

            #Parent.insert(int(inp[0]), int(inp[1]), int(inp[2]), int(inp[3]), inp[4],inp[5])
            Parent.insert(start,int(inp[1]), int(inp[2]), int(inp[3]), int(inp[4]), inp[5], inp[6])


            ParentH = Htree.hNodeList[0]
            #print"HL", len(ParentH.stitchList)
            #ParentH.insert(int(inp[0]), int(inp[1]), int(inp[2]), int(inp[3]), inp[4],inp[5])
            ParentH.insert(start, int(inp[1]), int(inp[2]), int(inp[3]), int(inp[4]), inp[5], inp[6])

    '''
    CG = cg.constraintGraph(testdir + '/' + testbase, testdir + '/' + testbase)
    CG.cgToGraph_h(testdir + '/' + testbase + 'edgeh.txt')
    CG.cgToGraph_v(testdir + '/' + testbase + 'edgev.txt')
    CSCG = CSCG.CSCG(Htree.hNodeList, Vtree.vNodeList, CG, testdir + '/' + testbase, testdir + '/' + testbase)

    CSCG.findGraphEdges_h()
    CSCG.drawLayer1()
    CSCG.findGraphEdges_v()
    CSCG.drawLayer2()
    '''

    print "Result"
    for node in Htree.hNodeList:
        Hnode.Final_Merge(node)
    #Hnode.Final_Merge(Htree.hNodeList[0])
    for node in Vtree.vNodeList:
        Vnode.Final_Merge(node)
    #for node in Htree.hNodeList:
        #node.Final_Merge()
    #for node in Vtree.vNodeList:
        #node.Final_Merge()
    Htree.setNodeId(Htree.hNodeList)
    Vtree.setNodeId(Vtree.vNodeList)
    print Htree.hNodeList
    f1 = open(testdir + '/' + testbase + "hNode.txt", 'wb')
    print >> f1, Htree.hNodeList


    for i in Htree.hNodeList:

        print i.id,i,len(i.stitchList)
        print >> f1, i,i.id
    #i=Htree.hNodeList[0]
        for j in i.stitchList:
            k= j.cell.x, j.cell.y, j.getWidth(),j.getHeight(),j.cell.id, j.cell.type, j.nodeId
            print k
            print >> f1,k
        if i.parent == None:
            print 0
        else:
            print i.parent.id, i.id
        for j in i.boundaries:
            if j.cell.type!=None:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                print "B",i.id,k


    print Vtree.vNodeList
    for i in Vtree.vNodeList:
        print i.id,i
        for j in i.stitchList:
            k= j.cell.x, j.cell.y, j.getWidth(),j.getHeight(),j.cell.id, j.cell.type, j.nodeId
            print k
            print >> f1,k
        if i.parent == None:
            print 0
        else:
            print i.parent.id, i.id
        for j in i.boundaries:
            if j.cell.type!=None:
                k = j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.id, j.cell.type, j.nodeId
                print "B",i.id,k


    def drawLayer( nodelist,truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig2 = matplotlib.pyplot.figure()
        #node=nodelist[0]
        fig2, ax4 = plt.subplots()
        for node in nodelist:
            for cell in node.stitchList:


                # ax4 = fig2.add_subplot(111, aspect='equal')
                if not cell.cell.type == "EMPTY":


                    if cell.cell.type=="Type_1":
                        colour='green'
                        #pattern = '\\'
                    elif cell.cell.type=="Type_2":
                        colour='red'
                        #pattern='*'
                    elif cell.cell.type=="Type_3":
                        colour='blue'
                        #pattern = '+'
                    elif cell.cell.type=="Type_4":
                        colour='black'
                        #pattern = '.'


                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            color=colour,


                        )
                    )
                else:
                    pattern = ''

                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            hatch=pattern,
                            color='white'
                        )
                    )


            plt.xlim(0, 60)
            plt.ylim(0, 60)
            fig2.savefig(testdir+'/'+testbase+".png")
            plt.close()
        #pylab.pause(11000)
    def findGraphEdges2(nodeList):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        # edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList
        arrowList1 = []

        for node in nodeList:
            for cell in node.stitchList:
                #for rect in self.Newcornerstitch_v.stitchList:
                # rect.cell.printCell(True,True)
                if cell.cell.type != "EMPTY":
                    color = "blue"
                    arrowList1.append((cell.cell.getX(), cell.cell.getY() ,0,cell.getHeight(), color))


                elif cell.cell.type == "EMPTY":
                    color = "red"
                    arrowList1.append((cell.cell.getX(), cell.cell.getY(),cell.getWidth(),0,  color))

                # for foo in arrowList:
                # print foo
        return arrowList1
    def findGraphEdges3(nodeList):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        # edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList

        arrowList2=[]
        for node in nodeList:
            for cell in node.stitchList:
                #for rect in self.Newcornerstitch_v.stitchList:
                # rect.cell.printCell(True,True)
                if cell.cell.type != "EMPTY":
                    color = "blue"

                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), cell.getWidth(),0, color))

                elif cell.cell.type == "EMPTY":
                    color = "red"

                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), 0, cell.getHeight(), color))
                # for foo in arrowList:
                # print foo
        return arrowList2


    def drawLayer2(nodelist, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """
        NODE=[]
        for node in nodelist:
            N={}
            key=node.id
            N.setdefault(key,[])
            if node.child!=[]:
                for i in node.child :
                    if  i.id not in N[key]:
                        N[key].append(i.id)
                NODE.append(N)
        print NODE
        KEYS=[]
        for i in NODE:
            KEYS.append(i.keys()[0])

        print KEYS


        # arrowList2=[]
        fig5= plt.figure()
        ax5 = plt.axes(xlim=(0, 60), ylim=(0, 60))
        for node in nodelist:


            if node.id==1:
                fig4=plt.figure()
                ax4 = plt.axes(xlim=(0, 60), ylim=(0, 60))
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":

                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type == "Type_4":
                            colour = 'black'

                        ax4.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                facecolor=colour,edgecolor='blue'


                            )
                        )
                    else:
                        pattern = ''

                        ax4.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
                        ax5.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
            fig3, ax2 = plt.subplots()

            if node.parent==nodelist[0] and node.child==[]:
                #print"!!!!!!",node.id
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":
                       
                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type=="Type_4":
                            colour='black'

                        ax2.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                color=colour,


                            )
                        )
                        ax5.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                facecolor=colour,
                                edgecolor='blue'

                            )
                        )
                    else:
                        pattern = ''

                        ax2.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
                        ax5.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                edgecolor='red'
                            )
                        )
            elif node.id in KEYS:


                if node==nodelist[0]: continue
                #print "I",node.id
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":

                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type == "Type_4":
                            colour = 'black'

                        ax2.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                color=colour

                            )
                        )
                        ax5.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                facecolor=colour,
                                edgecolor='blue'

                            )
                        )
                    else:
                        pattern = ''

                        ax2.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,

                            )
                        )
                        ax5.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                edgecolor='red'
                            )
                        )
            else:
                continue

                   

            for arr1 in findGraphEdges2(nodelist):
                ax2.arrow(arr1[0], arr1[1], arr1[2], arr1[3], head_width=.09, head_length=.09, color=arr1[4])
                #ax2.arrow(arr2[0], arr2[1], arr2[2], arr2[3], head_width=.09, head_length=.09, color=arr2[4])#

            for arr2 in findGraphEdges3(nodelist):
                #ax2.arrow(arr1[0], arr1[1], arr1[2], arr1[3], head_width=.09, head_length=.09, color=arr1[4])
                ax2.arrow(arr2[0], arr2[1], arr2[2], arr2[3], head_width=.09, head_length=.09, color=arr2[4])#
            # p = PatchCollection(self.drawZeroDimsVertices2())
            # ax4.add_collection(p)

            # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
            # automatically handle orientation
            # self.setAxisLabels(plt)

            # for arr in self.findGraphEdges_v():
            # ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.30, head_length=.3, color=arr[4])  #

            ####Setting axis labels(begin)
        #print "LEN", len(ax2.patches)
            i=node.id
            plt.xlim(0, 60)
            plt.ylim(0, 60)

            fig4.savefig(testdir + '/' + testbase +'1'+ "H.png")
            fig3.savefig(testdir + '/' + testbase +str(i)+ "H.png")
            #plt.close()
        fig5.savefig(testdir + '/' + testbase + "H.png")






    def findGraphEdges1(nodeList):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        # edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList
        arrowList2 = []
        for node in nodeList:
            for cell in node.stitchList:
                #for rect in self.Newcornerstitch_v.stitchList:
                # rect.cell.printCell(True,True)
                if cell.cell.type != "EMPTY":
                    color = "blue"
                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), cell.getWidth(), 0, color))

                elif cell.cell.type == "EMPTY":
                    color = "red"
                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), 0, cell.getHeight(), color))
                # for foo in arrowList:
                # print foo
        return arrowList2


    def findGraphEdges4(nodeList):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        # edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList

        arrowList2 = []
        for node in nodeList:
            for cell in node.stitchList:
                # for rect in self.Newcornerstitch_v.stitchList:
                # rect.cell.printCell(True,True)
                if cell.cell.type != "EMPTY":
                    color = "blue"

                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), 0,cell.getHeight(), color))

                elif cell.cell.type == "EMPTY":
                    color = "red"

                    arrowList2.append((cell.cell.getX(), cell.cell.getY(), cell.getWidth(),0 , color))
                # for foo in arrowList:
                # print foo
        return arrowList2

    def drawLayer1(nodelist, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        NODE = []
        for node in nodelist:
            N = {}
            key = node.id
            N.setdefault(key, [])
            if node.child != []:
                for i in node.child:
                    if i.id not in N[key]:
                        N[key].append(i.id)
                NODE.append(N)
        print NODE
        KEYS = []
        for i in NODE:
            KEYS.append(i.keys()[0])

        print KEYS


        # arrowList2=[]
        fig6 = plt.figure()
        ax6 = plt.axes(xlim=(0, 60), ylim=(0, 60))
        for node in nodelist:

            if node.id==1:
                fig4=plt.figure()
                ax4= plt.axes(xlim=(0, 60), ylim=(0, 60))
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":

                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type == "Type_4":
                            colour = 'black'

                        ax4.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                facecolor=colour,
                                edgecolor='blue'

                            )
                        )
                    else:
                        pattern = ''

                        ax4.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
                        pattern = ''

                        ax6.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
            fig3, ax3 = plt.subplots()
            if node.parent == nodelist[0] and node.child == []:
                #print"!!!!!!",node.id
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":

                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type == "Type_4":
                            colour = 'black'

                        ax3.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                color=colour

                            )
                        )
                        ax6.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                facecolor=colour,edgecolor='blue'

                            )
                        )
                    else:
                        pattern = ''

                        ax3.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
                        ax6.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                edgecolor='blue'
                            )
                        )
            elif node.id in KEYS:

                if node == nodelist[0]: continue
                #print "IV",node.id
                for cell in node.stitchList:

                    if not cell.cell.type == "EMPTY":

                        if cell.cell.type == "Type_1":
                            colour = 'green'
                        elif cell.cell.type == "Type_2":
                            colour = 'red'
                        elif cell.cell.type == "Type_3":
                            colour = 'blue'
                        elif cell.cell.type == "Type_4":
                            colour = 'black'

                        ax3.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                color=colour

                            )
                        )
                        ax6.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height

                                facecolor=colour,edgecolor='blue'

                            )
                        )
                    else:
                        pattern = ''

                        ax3.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                fill=False
                            )
                        )
                        ax6.add_patch(
                            matplotlib.patches.Rectangle(
                                (cell.cell.x, cell.cell.y),  # (x,y)
                                cell.getWidth(),  # width
                                cell.getHeight(),  # height
                                hatch=pattern,
                                edgecolor='blue'
                            )
                        )
            else:
                continue

            for arr1 in findGraphEdges1(nodelist):
                ax3.arrow(arr1[0], arr1[1], arr1[2], arr1[3], head_width=.09, head_length=.09, color=arr1[4])
                # ax2.arrow(arr2[0], arr2[1], arr2[2], arr2[3], head_width=.09, head_length=.09, color=arr2[4])#

            for arr2 in findGraphEdges4(nodelist):
                # ax2.arrow(arr1[0], arr1[1], arr1[2], arr1[3], head_width=.09, head_length=.09, color=arr1[4])
                ax3.arrow(arr2[0], arr2[1], arr2[2], arr2[3], head_width=.09, head_length=.09, color=arr2[4])  #
            # p = PatchCollection(self.drawZeroDimsVertices2())
            # ax4.add_collection(p)

            # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
            # automatically handle orientation
            # self.setAxisLabels(plt)

            # for arr in self.findGraphEdges_v():
            # ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.30, head_length=.3, color=arr[4])  #

            ####Setting axis labels(begin)
            i=node.id
            plt.xlim(0, 60)
            plt.ylim(0, 60)
            fig4.savefig(testdir + '/' + testbase +'1'+ "V.png")
            fig3.savefig(testdir + '/' + testbase +str(i)+ "V.png")
        fig6.savefig(testdir + '/' + testbase + "V.png")
        #plt.close()
        # pylab.pause(11000)
    drawLayer1(Vtree.vNodeList)
    drawLayer2(Htree.hNodeList)
    drawLayer(Htree.hNodeList)
    #color=['black','red','green','blue']
    #for i in range(len(Vtree.vNodeList)):
        #drawLayer2(Vtree.vNodeList[i],color[i])
    def drawLayer_11( truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig2 = matplotlib.pyplot.figure()
        #node=nodelist[0]

        #for node in nodelist:
        #for i in range(len(Htree.hNodeList)):
        i = 0
        for i in range(len(Vtree.vNodeList)):
            fig2, ax4 = plt.subplots()
            node=Vtree.vNodeList[i]

            #print "LEN",len(node.stitchList)
            for cell in node.stitchList:
                #print cell.cell.x


                # ax4 = fig2.add_subplot(111, aspect='equal')
                if not cell.cell.type == "EMPTY":
                    pattern = '\\'
                    '''
                    if cell.cell.type == "Type_1":
                        colour = 'green'
                    elif cell.cell.type == "Type_2":
                        colour = 'red'
                    elif cell.cell.type == "Type_3":
                        colour = 'blue'
                    elif cell.cell.type == "Type_4":
                        colour = 'black'
                    '''

                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            hatch=pattern,
                            Fill=False


                        )
                    )
                else:
                    pattern=' '
                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            hatch=pattern,
                            Fill=False

                        )
                    )
            '''
            for cell in node.boundaries:
                #print cell.cell.x
    
    
                # ax4 = fig2.add_subplot(111, aspect='equal')
                if not cell.cell.type == "EMPTY":
                    pattern = '//'
    
    
    
    
                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            hatch=pattern,
                            Fill=False
    
    
                        )
                    )
                else:
                    pattern='//'
    
                    ax4.add_patch(
                        matplotlib.patches.Rectangle(
                            (cell.cell.x, cell.cell.y),  # (x,y)
                            cell.getWidth(),  # width
                            cell.getHeight(),  # height
                            hatch=pattern,
                            Fill=False))
                '''



            plt.xlim(0, 60)
            plt.ylim(0, 60)
            fig2.savefig(testdir+'/'+testbase+"node-"+str(i)+".png",bbox_inches='tight')
            #fig2.show()
            plt.close()


    #drawLayer_11()

########################################################################################################################
class vLayer(cornerStitch):
    def __init__(self, stitchList,level,boundaries=None,max_x=None,max_y=None):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.level = level
        if self.level == 0:
            self.northBoundary = tile(None, None, None, None, None, cell(0, max_y, "EMPTY"))
            self.eastBoundary = tile(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
            self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
            self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
            self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        else:
            self.boundaries = boundaries


    def insert(self, x1, y1, x2, y2, type,name,parent=None):
        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the cornerStitch's stitchList, then corrects empty space vertically
        Four steps:
        1. vsplit x1, x2
        2. hsplit y1, y2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = [] #list of empty tiles that contain the area to be effected

        foo = self.orderInput(x1, y1, x2, y2)
        x1 = foo[0]
        y1 = foo[1]
        x2 = foo[2]
        y2 = foo[3]

        #if self.areaSearch(x1, y1, x2, y2):#check to ensure that the area is empty
            #return "Area is not empty"

        """
        New algorithm
        """
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        tr= self.findPoint(x2, y1, self.stitchList[0])
        if tr.cell.x==x2:
            tr=tr.WEST
            while (tr.cell.y + tr.getHeight() < y1):
                tr = tr.NORTH
        bl= self.findPoint(x1, y2, self.stitchList[0])
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
            #print topLeft.cell.x, topLeft.cell.y

        if bottomRight.cell.x==x2  :  ## and bottomRight.cell.y==y2 has been added to consider overlapping
            bottomRight = bottomRight.WEST
                # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH

        splitList = []
        splitList.append(bottomRight)
        #print"x=",bottomRight.cell.x, bottomRight.cell.y
        #if bottomRight.SOUTH != self.southBoundary and bottomRight.SOUTH.cell.type == "SOLID" and bottomRight.SOUTH.cell.y+bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type=="SOLID":
        if bottomRight.SOUTH not in self.boundaries and bottomRight.SOUTH.cell.type == type and bottomRight.SOUTH.cell.y + bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type == type:
            cc1 = bottomRight.SOUTH
            while cc1.cell.x+cc1.getWidth()<x2:
                cc1 = cc1.EAST
            if cc1 not in splitList:
                splitList.append(cc1)
            #if cc1.cell.type == "SOLID" and cc1.cell.y+cc1.getHeight() == y2:
            if cc1.cell.type == type and cc1.cell.y + cc1.getHeight() == y2:
                cc2 = cc1.SOUTH
                while cc2.cell.x+cc2.getWidth()<x2:
                    cc2 = cc2.EAST
                if cc2 not in splitList:
                    splitList.append(cc2)
        cc= bottomRight.NORTH
        #print len(splitList)
        #print "bot=",tr.cell.x, tr.cell.y,cc.cell.x, cc.cell.y
        while cc.cell.y<=tr.cell.y and cc not in self.boundaries:#has been added
           # print"1"

            if cc not in splitList:
                splitList.append(cc)
            cc = cc.NORTH
            #print "bot=", cc.cell.x, cc.cell.y
            while cc.cell.x >= x2:
                cc = cc.WEST
        #if cc.cell.type=="SOLID" and cc.cell.y==y1 or tr.cell.type=="SOLID"  :
        if cc.cell.type == type and cc.cell.y == y1 or tr.cell.type == type:
            if cc not in splitList and cc not in self.boundaries:
                splitList.append(cc)
            if cc not in self.boundaries:
                cc=cc.NORTH
                while cc.cell.x > x2:
                    cc = cc.WEST
                if cc not in self.boundaries:
                    splitList.append(cc)

        #print"splitListx2=", len(splitList)

        for rect in splitList:
            #print rect.cell.x,rect.cell.y
            if x2 != rect.cell.x and x2 != rect.EAST.cell.x:
                self.vSplit(rect, x2)

        splitList = []
        splitList.append(topLeft)

        #if topLeft.NORTH != self.northBoundary and topLeft.NORTH.cell.type == "SOLID" and topLeft.NORTH.cell.y == y1 or topLeft.cell.type=="SOLID":
        if topLeft.NORTH not in self.boundaries and topLeft.NORTH.cell.type == type and topLeft.NORTH.cell.y == y1 or topLeft.cell.type == type:
            cc = topLeft.NORTH
            while cc.cell.x>x1:
                cc=cc.WEST
            splitList.append(cc)

            #if cc.cell.type == "SOLID" and cc.cell.y == y1:
            if cc.cell.type == type and cc.cell.y == y1:
                cc1 = cc.NORTH
                while cc1.cell.x > x1:
                    cc1 = cc1.WEST
                if cc1 not in splitList and cc not in self.boundaries:
                    splitList.append(cc1)
        cc=topLeft
        while cc not in self.boundaries and cc.cell.y+cc.getHeight() >y2 :
            if cc not in splitList:
                splitList.append(cc)

            cc=cc.SOUTH
            while cc not in self.boundaries and cc.cell.x+cc.getWidth()<=x1:
                cc=cc.EAST

        #if cc.cell.type == "SOLID" and cc.cell.y+cc.getHeight() == y2 or bl.cell.type == "SOLID":
        if cc.cell.type == type and cc.cell.y + cc.getHeight() == y2 or bl.cell.type == type:
            if cc not in splitList and cc not in self.boundaries:
                splitList.append(cc)
            #if cc.cell.type=="SOLID" and cc.cell.y+cc.getHeight() == y2:
            if cc.cell.type == type and cc.cell.y + cc.getHeight() == y2:
                if cc.SOUTH not in self.boundaries:
                    cc = cc.SOUTH
                while cc.cell.x + cc.getWidth() <= x1:
                    cc = cc.EAST
                splitList.append(cc)

        #print"splitListx1=", len(splitList)
        for rect in splitList:
            if x1 != rect.cell.x and x1 != rect.EAST.cell.x:
                self.vSplit(rect, x1)


        ### Horizontal split


        changeList=[]
        cc = self.findPoint(x1, y1, self.stitchList[0])
        if cc.cell.y==y1:
            cc=cc.SOUTH
       # print "xco2=", cc.cell.x
        while cc.cell.x+cc.getWidth()<=x2:
            if cc not in changeList:
                changeList.append(cc)
            cc=cc.EAST
            while cc.cell.y>=y1:
                cc=cc.SOUTH
        cc1= self.findPoint(x1, y2, self.stitchList[0])
        while cc1.cell.x+cc1.getWidth()<=x2:
            if cc1 not in changeList:
                changeList.append(cc1)
            cc1=cc1.EAST
            while cc1.cell.y>y2:
                cc1=cc1.SOUTH
        #print"chlen=", len(changeList)
        for rect in changeList:
            i = self.stitchList.index[rect]
            if not rect.NORTH.cell.y == y1: self.hSplit(i, y1)
            if not rect.cell.y == y2: self.hSplit(i, y2)  # order is vital, again
        #####
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while cc not in self.boundaries and cc.cell.x < x1:
            cc = cc.EAST
       # print"resplit1=", cc.cell.x

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
        # cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        cc = self.findPoint(x1, y2, self.stitchList[0])
       # print"resplit1=", cc.cell.x, cc.cell.y, cc.cell.x+cc.getWidth()
        while cc.cell.x+cc.getWidth() <= x2:
            #if cc.SOUTH.cell.type == "SOLID" and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH != self.southBoundary and cc.SOUTH.cell.x+cc.SOUTH.getWidth() != cc.cell.x+cc.getWidth():
            if cc.SOUTH.cell.type == type and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH not in self.boundaries and cc.SOUTH.cell.x + cc.SOUTH.getWidth() != cc.cell.x + cc.getWidth():
                resplit.append(cc.SOUTH)
                resplit.append(cc.SOUTH.SOUTH)
            #if cc.EAST.cell.type == "SOLID" and cc.EAST.cell.x == x2 and cc.EAST != self.eastBoundary and cc.EAST.cell.y != cc.cell.y:
                #resplit.append(cc.EAST)
                #resplit.append(cc.EAST.EAST)
           # print"resplit=", len(resplit)
            #for foo in resplit:
                #foo.cell.printCell(True, True)
                #print"width=", foo.cell.x+foo.getWidth()
                #print "\n\n"
            for rect in resplit:
                #flag = True
                self.vSplit(rect, cc.cell.x+cc.getWidth())
            cc = cc.EAST




        resplit = []
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while cc.cell.x + cc.getWidth() <= x2:
           #if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1 and cc.NORTH != self.northBoundary and cc.NORTH.cell.x+cc.NORTH.getWidth() != cc.cell.x+cc.getWidth():
           if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1 and cc.NORTH not in self.boundaries and cc.NORTH.cell.x + cc.NORTH.getWidth() != cc.cell.x + cc.getWidth():
               resplit.append(cc.NORTH)
               resplit.append(cc.NORTH.NORTH)
               #print"resplit=", len(resplit)
               #for foo in resplit:
                   #foo.cell.printCell(True, True)
                   #print"width=", foo.cell.x + foo.getWidth()
                   #print "\n\n"
               for rect in resplit:
                   # flag = True
                   self.vSplit(rect, cc.cell.x + cc.getWidth())
           cc = cc.EAST


        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        # print "xco2=", cc.cell.x
        while cc.cell.x + cc.getWidth() <= x2:
            #if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1:
            if cc.NORTH.cell.type == type and cc.NORTH.cell.y == y1:
                changeList.append(cc.NORTH)
            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH
        #print"list=", len(changeList)
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
       # print"t.x,y=", t.cell.x, t.cell.y
        #if t.NORTH.cell.type == "SOLID" and t.NORTH.cell.y == y1:
            #changeList.append(t.NORTH)
        changeList.append(t)

        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later
                   # print"entry"

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
                        #if t.WEST.cell.type == "SOLID" and t.WEST.cell.x + t.WEST.getWidth() == x1:
                            #changeList.append(t.WEST)
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
            #if cc1.SOUTH.cell.type == "SOLID" and cc1.SOUTH.cell.y +cc1.SOUTH.getHeight()== y2:
            if cc1.SOUTH.cell.type == type and cc1.SOUTH.cell.y + cc1.SOUTH.getHeight() == y2:
                changeList.append(cc1.SOUTH)
            cc1 = cc1.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH
       # print"arealist=", len(changeList)
        changeList.sort(key=lambda cc: cc.cell.x)



        #for foo in changeList:
            #foo.cell.printCell(True, True)
            #print "\n\n"

        ##### Merge Algorithm:


        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            if top.cell.y == low.cell.y + low.getHeight() or top.cell.y + top.getHeight() == low.cell.y:
                top.cell.type = type
                low.cell.type = type
                #print"topx=", top.cell.x, top.cell.y, top.cell.x + top.getWidth(),top.name
                #print"lowx=", low.cell.x, low.cell.y, low.cell.x + low.getWidth(),low.name
                mergedcell = self.merge(top, low)
                if mergedcell == "Tiles are not alligned":
                   # print"-i=", i
                    i += 1
                else:
                    del changeList[i + 1]
                    del changeList[i]
                    #print mergedcell.name
                    changeList.insert(i, mergedcell)
                    #print"i=",i
            else:
                i += 1

        list_len = len(changeList)
        #print"len=", list_len
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                #print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                   # print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type

                    #print"topx=", top.cell.x, top.cell.y
                    #print"lowx=", low.cell.x, low.cell.y
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
                        # print"x=",x
                        changeList.insert(x, mergedcell)

                        self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        #print"len_1", len(changeList)


        #for foo in changeList:
            #foo.cell.printCell(True, True)
        for x in range(0, len(changeList)):
            changeList[x].cell.type = type


            #print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:
            print "l",len(changeList)

            changeList[0].cell.type = type
            #changeList[0].name=name
            self.rectifyShadow(changeList[0])
            for rect in changeList:
                print "t", rect.name, rect.level, rect.cell.x, rect.cell.y

                #if rect.cell.x == x1 and rect.cell.y == y2 and rect.getWidth() == (x2 - x1) and rect.getHeight() == (y1 - y2):
                #if rect.name == None:
                    #print rect.cell.x
                #print rect.cell.
                if rect.cell.type==type:

                    rect.name = name
                if rect.level==None:
                    rect.level=self.level
                    #print "t",rect.name,rect.level,rect.cell.x,rect.cell.y


        return changeList



    def rectifyShadow(self, caster):
        """
        this checks the NORTH and SOUTH of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        """
        changeSet = []

        cc = caster.NORTH #recitfy north side, walking downwards

        while (cc not in self.boundaries and cc.cell.x >= caster.cell.x):
            #if cc.NORTH==self.northBoundary or cc.NORTH.cell.type=="EMPTY":
            changeSet.append(cc)
            cc = cc.WEST
        #print "len=", len(changeSet)
        i = 0
        j = 1
        while j < len(changeSet): #merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            if topCell.NORTH==lowerCell.NORTH:
                mergedCell = self.merge(topCell, lowerCell)
                if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                    i += 1
                    if j < len(changeSet): # there was a '-1'
                        j += 1
                else:
                    del changeSet[j]
                    changeSet[i] = mergedCell
                #if j < len(changeSet) -1:
                    #j += 1
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1


        cc = caster.SOUTH#recitfy SOUTH side, walking eastwards
        changeSet = []
        #print"caster=",caster.cell.x+caster.getHeight()

        while (cc not in self.boundaries and cc.cell.x < caster.cell.x + caster.getWidth()):
            #if cc.SOUTH == self.southBoundary or cc.SOUTH.cell.type == "EMPTY":
            changeSet.append(cc)
            cc = cc.EAST
       # print "lenr=", len(changeSet)
        """
        for foo in changeSet:
            foo.cell.printCell(True, True)
            print "\n\n"
        """
        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet): #merge all cells with the same width along the northern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            if topCell.SOUTH==lowerCell.SOUTH:
                mergedCell = self.merge(topCell, lowerCell)

                if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                    i += 1
                   # print "i = ", i
                    if j < len(changeSet) -1:
                        j += 1
                else:
                    del changeSet[j]
                    changeSet[i] = mergedCell
                    #if j < len(changeSet) - 1:
                        #j += 1
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1

        return

    """
    def areaSearch(self, x1, y1, x2, y2):
        
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)        
        this is designed with vertically aligned space assumptions in mind
        
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(bottom right) corner
        
        if cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        #elif secondCorner.cell.type == "SOLID":
            #return True
        elif cc.cell.y >y2:
            return True

        #elif cc.cell.y + cc.getHeight() < y1:
            #return True  # the corner cell is empty but touches a solid cell within the search area


        while(cc.EAST.cell.x < x2):
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.y + cc.getHeight() < y1:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.EAST #check the next rightmost cell
            while (cc.cell.y + cc.getHeight() < y2): #making sure that the CurrentCell's right edge lays within the area
                cc = cc.NORTH # if it doesn't, traverse the top right stitch to find the next cell of interest

        return False
    """

    ### NEW AREA SEARCH
    def areaSearch(self, x1, y1, x2, y2):
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        sc = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(bottom right) corner
        if cc.cell.y==y1:
            cc=cc.SOUTH
            while cc.cell.x+cc.getWidth()<x1 : #and cc.cell.type=="SOLID"
                cc=cc.EAST

        #if cc.cell.type == "SOLID":
        if cc.cell.type == type:
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.y >y2:
            return True  # the corner cell is empty but touches a solid cell within the search area

        cc=cc.EAST
        while (cc not in self.boundaries and cc.cell.x< x2):
            #if cc.cell.y<y1 and cc.cell.type=="SOLID":
                #return True ## these 2 lines have been commented out
            while(cc.cell.y+cc.getHeight()>y2):
                #if cc.cell.y<y1 and cc.cell.type=="SOLID":
                if cc.cell.y < y1 and cc.cell.type == type:
                    return True
                if cc.SOUTH not in self.boundaries:
                    cc=cc.SOUTH
                else:
                    break
            cc=cc.EAST
        return False
    def Final_Merge(self):
        changeList=[]
        #for cell in self.stitchList:

        for rect in self.stitchList:
            if rect.cell.type==type:
                changeList.append(rect)
        list_len = len(changeList)
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                # print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    # print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    #top.cell.type = type
                    #low.cell.type = type
                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
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
                        # print"x=",x
                        mergedcell.type='Type_1'
                        changeList.insert(x, mergedcell)
                        self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        # print"len_1", len(changeList)
        for i in range(len(changeList)):

            self.rectifyShadow(changeList[i])
        return self.stitchList

    def set_id(self):  ########## Setting id for all type 1 blocks

        length=len(self.stitchList)
        i=1

        #print length
        for rect in self.stitchList:
            #if rect.name!=None:
                #print "V",rect.name
            #rect.cell.id=i
            #if rect.cell.type=="SOLID":
            if rect.cell.type == type:
                rect.cell.id=i
                i+=1
        return



class hLayer(cornerStitch):
    def __init__(self, stitchList, level, boundaries=None, max_x=None, max_y=None):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.level = level
        if self.level == 0:
            self.northBoundary = tile(None, None, None, None, None, cell(0, max_y, "EMPTY"))
            self.eastBoundary = tile(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
            self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
            self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
            self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        else:
            self.boundaries = boundaries



    def h_insert(self,Tile1,Tile2,x1,y1,x2,y2,type,name,parent):

        topLeft=self.findPoint(x1, y1, self.stitchList[0])

        tr = self.findPoint(x2, y1, self.stitchList[0])
        bl = self.findPoint(x1, y2, self.stitchList[0])

        if topLeft.cell.y==y1:
            cc=topLeft
            if topLeft.SOUTH not in self.boundaries:
                cc=topLeft.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x+cc.getWidth()<=x1: ## 2 lines have been added
                    cc=cc.EAST
            topLeft = cc
        if tr.cell.y == y1:
            cc = tr
            if tr.SOUTH not in self.boundaries:
                cc = tr.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            tr=cc
        splitList = []
        splitList.append(topLeft)
        cc = topLeft

        if cc.WEST not in self.boundaries and cc.WEST.cell.type == type and cc.WEST.cell.x + cc.WEST.getWidth() == x1 or cc.cell.type == type:
            cc1 = cc.WEST
            while cc1.cell.y + cc1.getHeight() < y1:
                cc1 = cc1.NORTH
            # print "testwx", cc1.cell.x
            splitList.append(cc1)
        # if cc1.cell.type=="SOLID" and cc1.cell.x+cc1.getWidth()==x1:
        while cc.cell.x <= tr.cell.x and cc not in self.boundaries:  # it was only <x2
            if cc not in splitList:
                # print "testx",cc.cell.x+cc.getWidth()
                splitList.append(cc)

            cc = cc.EAST
            # print"cc.x2", cc.cell.y
            while cc.cell.y >= y1 and cc not in self.boundaries:  # previously it was >y1
                cc = cc.SOUTH

        for rect in splitList:
            # print "height=",rect.cell.y+rect.getHeight()
            print "SP", rect.cell.x, rect.cell.y
            if y1 != rect.cell.y and y1 != rect.NORTH.cell.y:
                self.hSplit_2(rect, y1)

        bottomRight = self.findPoint(x2, y2, self.stitchList[0])


        if bottomRight.cell.x == x2:  ## this part has been corrected (reinserted to consider overlap)
            bottomRight = bottomRight.WEST
                # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH
        #print"bot=", bottomRight.cell.y
        splitList = []
        splitList.append(bottomRight)
        cc=bottomRight
        #if cc.EAST!= self.eastBoundary and cc.EAST.cell.type=="SOLID" and cc.EAST.cell.x==x2 or cc.cell.type=="SOLID":
        if cc.EAST not in self.boundaries and cc.EAST.cell.type == type and cc.EAST.cell.x == x2 or cc.cell.type == type:
            cc1 = cc.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH
            splitList.append(cc1)
            #if cc1.cell.type=="SOLID" and cc1.cell.x==x2:

        while cc.cell.x>=x1 and cc not in self.boundaries:#it was cc.WEST!= (previously >x1)
            cc = cc.WEST

            if cc not in self.boundaries:
                while cc.cell.y+cc.getHeight() <= y2  :#previously it was <y2
                    cc= cc.NORTH
            if cc not in splitList:
                splitList.append(cc)


        #print"cc2.x", cc.cell.x
        #if cc.cell.type=="SOLID" and cc.cell.x+cc.getWidth()>=x1 or bl.cell.type=="SOLID"   :#previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
        if cc.cell.type == type and cc.cell.x + cc.getWidth() >= x1 or bl.cell.type == type:  # previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
            if cc not in splitList:
                splitList.append(cc)
            if cc.WEST not in self.boundaries:
                cc1 = cc.WEST
                while cc1.cell.y+cc1.getHeight() <= y2:#previously it was <y2
                   cc1 = cc1.NORTH
                splitList.append(cc1)

        for rect in splitList:
            #print "height=",rect.cell.y+rect.getHeight()
            #print "SP",rect.cell.x,rect.cell.y
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y:
                #print"1"
                self.hSplit_2(rect, y2)

        for foo in self.stitchList:
            print"F"
            print foo.cell.x,foo.cell.y,foo.SOUTH.cell.y







        changeList = []
        # step 2: vsplit x1 and x2
        cc = self.findPoint(x1, y2, self.stitchList[0])
        # print x1,y1
        #print "n",cc.cell.x,cc.cell.y
        while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
            cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() <= y1):
            while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
                print"cc",cc.cell.y
            cc = cc.NORTH
        print"vlistx1=", len(changeList)

        # changeList = []
        # step 2: vsplit x1 and x2
        cc =self.findPoint(x2,y1,self.stitchList[0]).SOUTH
        print "n", cc.cell.x, cc.cell.y
        if cc.cell.x == x2:
            cc = cc.WEST
        while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
            cc = cc.EAST

        while (cc not in self.boundaries and cc.cell.y + cc.getHeight() > y2):
            while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH
            print cc.cell.x,cc.cell.y
        print"vlistx2=", len(changeList)



        for rect in changeList:  # split vertically
            #print "VSP", rect.cell.x,rect.cell.y
            if not rect.EAST.cell.x == x2: self.vSplit_2(rect, x2)  # do not reorder these lines
            if not rect.cell.x == x1: self.vSplit_2(rect, x1)  # do not reorder these lines
        for foo in self.stitchList:
            print "i"
            print foo.cell.x,foo.cell.y,foo.SOUTH.cell.y

        changeList = []
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        # if t.WEST.cell.type=="SOLID" and t.WEST.cell.x+t.WEST.getWidth()==x1:
        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1:
            changeList.append(t.WEST)
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
                    # if child.cell.type == "SOLID" and child.cell.x == x2:
                    if child.cell.type == type and child.cell.x == x2:
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
                        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1:
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
        for foo in changeList:
            print "foo"
            foo.cell.printCell(True,True,True)
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            # print"topx=", top.cell.x, top.cell.y
            # print"lowx=", low.cell.x, low.cell.y
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
        # print"len=",list_len
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                # print"i=",i,len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    # print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type
                    # print"topx=", top.cell.x, top.cell.y
                    # print"lowx=", low.cell.x, low.cell.y
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
                        # print"x=",x
                        changeList.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        # print"len_1",len(changeList)

        ######
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            # print"topx=", top.cell.x, top.cell.y
            # print"lowx=", low.cell.x, low.cell.y
            # if top.cell.x == low.cell.x + low.getWidth() or top.cell.x + top.getWidth() == low.cell.x:
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

        # for foo in changeList:
        # foo.cell.printCell(True, True)
        for x in range(0, len(changeList)):
            changeList[x].cell.type = type
            # print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0])
            for rect in changeList:
                # print rect.cell.x,rect.cell.y
                # print rect.cell.x
                # if rect.cell.x==x1 and rect.cell.y==y2 and rect.getWidth()==(x2-x1) and rect.getHeight()==(y1-y2):
                # if rect.name==None:
                if rect.cell.type == type:
                    rect.name = name
                    print rect.cell.x, rect.cell.y
                    rect.parent=parent


    def insert(self, x1, y1, x2, y2, type,name):


        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the cornerStitch's stitchList, then corrects empty space horizontally
        1. hsplit y1, y2
        2. vsplit x1, x2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = [] #list of empty tiles that contain the area to be effected

        foo = self.orderInput(x1, y1, x2, y2)
        x1 = foo[0]
        y1 = foo[1]
        x2 = foo[2]
        y2 = foo[3]

        #if self.areaSearch(x1, y1, x2, y2): #check to ensure that the area is empty
            #return "Area is not empty"

        #step 1: hsplit y1 and y2
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        #print topLeft.cell.x, topLeft.cell.y
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        tr=self.findPoint(x2, y1, self.stitchList[0])
        bl=self.findPoint(x1, y2, self.stitchList[0])

        if topLeft.cell.y==y1:
            cc=topLeft
            if topLeft.SOUTH not in self.boundaries:
                cc=topLeft.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x+cc.getWidth()<=x1: ## 2 lines have been added
                    cc=cc.EAST
            topLeft = cc
            #print topLeft.cell.x,topLeft.cell.y
            #while cc.cell.y >= y2: #find all cells that need to be vsplit
        if tr.cell.y == y1:
            cc = tr
            if tr.SOUTH not in self.boundaries:
                cc = tr.SOUTH
            while cc.EAST not in self.boundaries and cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            tr=cc

        #print"topx=",topLeft.cell.x
        #print"topy=", topLeft.cell.y
        splitList=[]
        splitList.append(topLeft)
        cc=topLeft

        #if cc.WEST != self.westBoundary and cc.WEST.cell.type=="SOLID" and cc.WEST.cell.x+cc.WEST.getWidth()==x1 or cc.cell.type=="SOLID":
        if cc.WEST not in self.boundaries and cc.WEST.cell.type == type and cc.WEST.cell.x + cc.WEST.getWidth() == x1 or cc.cell.type == type:
            cc1 = cc.WEST
            while cc1.cell.y + cc1.getHeight() < y1:
                cc1 = cc1.NORTH
           # print "testwx", cc1.cell.x
            splitList.append(cc1)
           # if cc1.cell.type=="SOLID" and cc1.cell.x+cc1.getWidth()==x1:
            cc2=cc1.WEST
            #print"cc2=",cc2.cell.y+cc2.getHeight()
            while cc2 not in self.boundaries and cc2.cell.y + cc2.getHeight() < y1:
                cc2 = cc2.NORTH
            if cc2 not in self.boundaries:
                splitList.append(cc2)
        #print"cc.x",cc.cell.x

        while cc.cell.x<=tr.cell.x and cc not in self.boundaries:#it was only <x2
            if cc not in splitList:
                #print "testx",cc.cell.x+cc.getWidth()
                splitList.append(cc)

            cc=cc.EAST
            #print"cc.x2", cc.cell.y
            while cc.cell.y >= y1 and cc not in self.boundaries:#previously it was >y1
                cc= cc.SOUTH
        #if cc.cell.type=="SOLID" and cc.cell.x==x2 and cc!=self.eastBoundary or tr.cell.type=="SOLID" :##and tr.cell.y!=y1 and cc!=self.eastBoundary)
        if cc.cell.type == type and cc.cell.x == x2 and cc not in self.boundaries or tr.cell.type == type:  ##and tr.cell.y!=y1 and cc!=self.eastBoundary)
            #print "testex", cc.cell.x
            splitList.append(cc)
            if cc.EAST not in self.boundaries:
                cc=cc.EAST

                while cc.cell.y >= y1:#previously it was >y1
                    cc= cc.SOUTH
            #print "testsx", cc.cell.x
                splitList.append(cc)

        #print"splitListy1=",len(splitList)
        for rect in splitList:
            #print "height=",rect.cell.y+rect.getHeight()
            if y1 != rect.cell.y and y1 != rect.NORTH.cell.y:
                self.hSplit(rect, y1)



        #if y2 != bottomRight.cell.y and y2 != bottomRight.NORTH.cell.y:  # horizontally split the bottom edge

        if bottomRight.cell.x == x2:  ## this part has been corrected (reinserted to consider overlap)
            bottomRight = bottomRight.WEST
                # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH
        #print"bot=", bottomRight.cell.y
        splitList = []
        splitList.append(bottomRight)
        cc=bottomRight
        #if cc.EAST!= self.eastBoundary and cc.EAST.cell.type=="SOLID" and cc.EAST.cell.x==x2 or cc.cell.type=="SOLID":
        if cc.EAST not in self.boundaries and cc.EAST.cell.type == type and cc.EAST.cell.x == x2 or cc.cell.type == type:
            cc1 = cc.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH
            splitList.append(cc1)
            #if cc1.cell.type=="SOLID" and cc1.cell.x==x2:
            if cc1.cell.type == type and cc1.cell.x == x2:
                cc2=cc1.EAST
                while cc2.cell.y > y2:
                    cc2 = cc2.SOUTH
                splitList.append(cc2)
        while cc.cell.x>=x1 and cc not in self.boundaries:#it was cc.WEST!= (previously >x1)
            cc = cc.WEST

            if cc not in self.boundaries:
                while cc.cell.y+cc.getHeight() <= y2  :#previously it was <y2
                    cc= cc.NORTH
            if cc not in splitList:
                splitList.append(cc)


        #print"cc2.x", cc.cell.x
        #if cc.cell.type=="SOLID" and cc.cell.x+cc.getWidth()>=x1 or bl.cell.type=="SOLID"   :#previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
        if cc.cell.type == type and cc.cell.x + cc.getWidth() >= x1 or bl.cell.type == type:  # previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
            if cc not in splitList:
                splitList.append(cc)
            if cc.WEST not in self.boundaries:
                cc1 = cc.WEST
                while cc1.cell.y+cc1.getHeight() <= y2:#previously it was <y2
                   cc1 = cc1.NORTH
                splitList.append(cc1)


        """
        if bottomRight.WEST != self.westBoundary and bottomRight.WEST.cell.type == "SOLID" and bottomRight.WEST.cell.x + bottomRight.WEST.getWidth() >= x1 or bottomRight.cell.type=="SOLID":#it was ==x1 ,changed to handle overlap
            cc = bottomRight.WEST
            splitList.append(cc)
            cc = cc.WEST
            while cc!=self.westBoundary and cc.cell.y + cc.getHeight() < y2:
                cc = cc.NORTH
            if cc.cell.type == "EMPTY" and cc!=self.westBoundary:
                splitList.append(cc)
        if bottomRight.EAST != self.eastBoundary and bottomRight.EAST.cell.type == "SOLID" and bottomRight.EAST.cell.x <= x2 or bottomRight.cell.type=="SOLID":#it was ==x2 ,changed to handle overlap
            cc = bottomRight.EAST
            splitList.append(cc)
            cc = cc.EAST
            while cc.cell.y > y2:
                cc = cc.SOUTH
            if cc.cell.type == "EMPTY" and cc!=self.eastBoundary:
                splitList.append(cc)
        """
        #print"splitListy2=", len(splitList)
        for rect in splitList:
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y:
                self.hSplit(rect, y2)




        changeList=[]
        #step 2: vsplit x1 and x2
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        #print x1,y1
        #print "n",cc.cell.x,cc.cell.y
        while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
            cc = cc.EAST
        while (cc not in self.boundaries and cc.cell.y+cc.getHeight()>y2):
            while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc=cc.SOUTH
       # print"vlistx1=", len(changeList)

        #changeList = []
        # step 2: vsplit x1 and x2
        cc = self.findPoint(x2, y1, self.stitchList[0]).SOUTH
        if cc.cell.x==x2:
            cc=cc.WEST
        while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
            cc = cc.EAST

        while (cc not in self.boundaries and cc.cell.y+cc.getHeight()>y2):
            while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH
       # print"vlistx2=", len(changeList)

        #for foo in changeList:
           # foo.cell.printCell(True, True)
        for rect in changeList:  # split vertically
            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2)  # do not reorder these lines
            if not rect.cell.x == x1: self.vSplit(rect, x1)  # do not reorder these lines


        """
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
            cc = cc.EAST

        while cc.cell.y>=y2:
            if cc.WEST.cell.type == "SOLID" and cc.WEST.cell.x + cc.WEST.getWidth() == x1 and cc.WEST != self.westBoundary and cc.WEST.cell.y != cc.cell.y:
                self.hSplit(cc.WEST,cc.cell.y)
                self.hSplit(cc.WEST.WEST, cc.cell.y)
            cc=cc.SOUTH

        cc = self.findPoint(x2, y1, self.stitchList[0]).SOUTH
        while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
            cc = cc.EAST
        while cc.cell.y >= y2:
            while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            if cc.EAST.cell.type == "SOLID" and cc.EAST.cell.x == x2 and cc.EAST != self.eastBoundary and cc.EAST.cell.y != cc.cell.y:
                self.hSplit(cc.EAST, cc.cell.y)
                self.hSplit(cc.EAST.EAST, cc.cell.y)
            cc = cc.SOUTH

        
        # cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        cc = topLeft  ##There was topLeft.SOUTH
        while cc!=self.southBoundary and cc.cell.x<x1:
            cc=cc.EAST
        print"resplit1=", cc.cell.x, cc.cell.y

        while cc.cell.y >= y2:
            cc1 = cc
            print"resplitsouth=", cc.cell.x, cc.cell.y
            resplit = []
            min_y=0
            while cc1.cell.x + cc1.getWidth() <= x2:
                if cc1.cell.y>min_y:
                    min_y=cc1.cell.y
                resplit.append(cc1)
                if cc1.cell.x==x1 and cc1.WEST!=self.westBoundary:
                    resplit.append(cc1.WEST)
                cc1=cc1.EAST
            print"resplitlen=",len(resplit)
            for foo in resplit:
                foo.cell.printCell(True, True)
            if len(resplit)>1:
                for foo in resplit:
                    if foo.cell.y<min_y:
                        if foo.cell.y!=min_y:
                            print"split"

                            self.hSplit(foo,min_y)

            cc=cc.SOUTH

        """
        cc = self.findPoint(x2, y2, self.stitchList[0]).WEST ##There was topLeft.SOUTH

       #print"resplit1=", cc.cell.x, cc.cell.y

        while cc not in self.boundaries and cc.cell.y+cc.getHeight() <= y1:
            cc1 = cc
            #print"resplitsouth=", cc.cell.x, cc.cell.y
            resplit = []
            min_y = 100000
            while cc1 not in self.boundaries and cc1.cell.x >= x1:
                if cc1.cell.y+cc1.getHeight() < min_y:
                    min_y = cc1.cell.y+cc1.getHeight()
                resplit.append(cc1)
                if cc1.cell.x == x1:
                    resplit.append(cc1.WEST)
                    #if cc1.WEST.cell.type=="SOLID":
                    if cc1.WEST.cell.type == type:
                        resplit.append(cc1.WEST.WEST)
                if cc1.EAST.cell.x == x2:
                    resplit.append(cc1.EAST)
                    #if cc1.EAST.cell.type=="SOLID":
                    if cc1.EAST.cell.type == type:
                        resplit.append(cc1.EAST.EAST)

                cc1 = cc1.WEST
           # print"resplitlen=", len(resplit)
            #for foo in resplit:
                #foo.cell.printCell(True, True)

            if len(resplit) > 1:
                for foo in resplit:
                    if foo.cell.y+foo.getHeight() > min_y:
                        #if foo.cell.y+foo.getHeight()!= min_y:
                        #print"split"
                        self.hSplit(foo, min_y)
            if cc.NORTH not in self.boundaries:
                cc = cc.NORTH

        #changeList = []


        changeList=[]
        done = False
        dirn =1# to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y>=y1:
            t=t.SOUTH
        #if t.WEST.cell.type=="SOLID" and t.WEST.cell.x+t.WEST.getWidth()==x1:
        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1:
            changeList.append(t.WEST)
        changeList.append(t)
        while (done== False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later

                    t = child
                    if child not in changeList:
                        changeList.append(child)
                else:
                    #if child.cell.type == "SOLID" and child.cell.x == x2:
                    if child.cell.type == type and child.cell.x == x2:
                        if child not in changeList:
                            changeList.append(child)
                    dirn = 2#to_root
            else:
                if t.cell.x <= x1 or t.cell.y <= y2:
                    if t.cell.y > y2:
                        t = t.SOUTH
                        while t.cell.x + t.getWidth() <= x1:
                            t = t.EAST
                        #if t.WEST.cell.type == "SOLID" and t.WEST.cell.x + t.WEST.getWidth() == x1:
                        if t.WEST.cell.type == type and t.WEST.cell.x + t.WEST.getWidth() == x1:
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
        #print "arealist=", len(changeList)
        """
        min_Height=100000
        for foo in changeList:
            #foo.cell.printCell(True, True)
            if foo.getHeight()<min_Height:
                min_Height=foo.getHeight()

        print"min=",min_Height
        
        for foo in changeList:
            foo.cell.printCell(True, True)
            if foo.getHeight()>min_Height:
                h=foo.cell.y+min_Height
                while h<foo.cell.y+foo.getHeight():
                    self.hSplit(foo,h)
                    h+=min_Height
            #foo.cell.printCell(True, True)
        """




        #for foo in changeList:
            #foo.cell.printCell(True, True)

        ## New Merge Algorithm v2


        i=0
        while i<len(changeList)-1:

            top=changeList[i+1]
            low=changeList[i]
            #print"topx=", top.cell.x, top.cell.y
            #print"lowx=", low.cell.x, low.cell.y
            if top.cell.x==low.cell.x+low.getWidth() or top.cell.x+top.getWidth()==low.cell.x:
                top.cell.type=type
                low.cell.type=type
                mergedcell=self.merge(top,low)
                if mergedcell=="Tiles are not alligned":
                    i+=1
                else:
                    del changeList[i+1]
                    del changeList[i]
                    #print"arealist=", len(changeList)
                    if len(changeList)==0:
                        changeList.append(mergedcell)
                    else:
                        changeList.insert(i,mergedcell)
                    self.rectifyShadow(changeList[i])
            else:
                i+=1



        list_len= len(changeList)
        #print"len=",list_len
        c=0

        while(len(changeList)>1):
            i=0
            c+=1

            while i< len(changeList)-1:
                #print"i=",i,len(changeList)
                j=0
                while j<len(changeList):
                    #j=i+1
                    #print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type
                    #print"topx=", top.cell.x, top.cell.y
                    #print"lowx=", low.cell.x, low.cell.y
                    mergedcell = self.merge(top, low)
                    if mergedcell == "Tiles are not alligned":
                        if j<len(changeList):
                            j+=1

                    else:

                        del changeList[j]
                        if i>j:
                            del changeList[i-1]
                        else:
                            del changeList[i]
                        x=min(i,j)
                        #print"x=",x
                        changeList.insert(x, mergedcell)
                        #self.rectifyShadow(changeList[x])
                        #if j<len(changeList):
                              #j+=1
                i+=1


            if c==list_len:
                break
        #print"len_1",len(changeList)

        ######
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            #print"topx=", top.cell.x, top.cell.y
            #print"lowx=", low.cell.x, low.cell.y
            #if top.cell.x == low.cell.x + low.getWidth() or top.cell.x + top.getWidth() == low.cell.x:
            top.cell.type = type
            low.cell.type = type
            mergedcell = self.merge(top, low)
            if mergedcell == "Tiles are not alligned":
                i += 1
            else:
                del changeList[i + 1]
                del changeList[i]
                #print"arealist=", len(changeList)
                if len(changeList) == 0:
                    changeList.append(mergedcell)
                else:
                    changeList.insert(i, mergedcell)
                self.rectifyShadow(changeList[i])



        #for foo in changeList:
            #foo.cell.printCell(True, True)
        for x in range(0,len(changeList)):
            changeList[x].cell.type = type
            #print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x+=1

        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0])
            for rect in changeList:
                #print rect.cell.x,rect.cell.y
                #print rect.cell.x
                #if rect.cell.x==x1 and rect.cell.y==y2 and rect.getWidth()==(x2-x1) and rect.getHeight()==(y1-y2):
                #if rect.name==None:
                if rect.cell.type==type:

                    rect.name=name
                    rect.level=self.level
                    #print rect.cell.x,rect.cell.y
                    '''
                    N=rect.findNeighbors()
                    key = rect
                    Connected_H.setdefault(key, [])
                    Flag=0
                    for i in N:
                        #print i.cell.type
                        #print rect.cell.type
                        if i.cell.type==rect.cell.type:
                            for j in Connected_H.keys():
                                if i==j:
                                    Flag=1
                                    if rect not in Connected_H[rect]:
                                        Connected_H[i].append(rect)
                                else:
                                    Flag=1
                                    if rect not in Connected_H[rect]:
                                        Connected_H[rect].append(i)
                    if Flag==0:
                        if rect not in Connected_H[rect]:
                            Connected_H[rect].append(rect)


                    '''


        #print changeList
        return  changeList


        ######
        """
        while cc.cell.y+cc.getHeight()<=y1 :
            if cc.WEST.cell.type=="SOLID" or cc.WEST.cell.x == x1:#or cc.WEST.cell.x==x1 has been added overlapping issue
                flag= True
                changeList1.append(cc)
                cc1=cc.WEST
                while cc1.cell.type=="SOLID" or cc1.cell.x>=x1:#added to consider overlap
                    changeList1.append(cc1)
                    cc1=cc1.WEST
                #changeList1.append(cc.WEST)
                #if cc.WEST.WEST.cell.type=="SOLID":
                    #changeList1.append(cc.WEST.WEST)
            if cc.EAST.cell.type=="SOLID" or cc.EAST.cell.x+cc.EAST.getWidth()==x2:#or cc.EAST.cell.x+cc.EAST.getWidth()==x2 has been added overlapping issue
                flag= True
                if cc not in changeList1:
                    changeList1.append(cc)
                #print"x1y2=", cc.cell.y
                cc1=cc.EAST
                while cc1.cell.type=="SOLID" or cc1.cell.x+cc1.getWidth()<=x2:#added to consider overlap

                     changeList1.append(cc1)
                     cc1=cc1.EAST
                #changeList1.append(cc.EAST)
                #if cc.EAST.EAST.cell.type=="SOLID":
                    #changeList1.append(cc.EAST.EAST)
                #print"x1y2=", cc.EAST.cell.y
            if (cc not in changeList1):
                changeList.append(cc)
            print"clist1=", len(changeList1)
            cc = cc.NORTH
            while len(changeList1) > 1:
                topCell = changeList1.pop(0)
                print"cell0=", topCell.cell.x
                lowerCell = changeList1.pop(0)
                topCell.cell.type = type
                lowerCell.cell.type = type
                # print topCell.__class__, ",", lowerCell.__class__

                mergedCell = self.merge(topCell, lowerCell)

                changeList1.insert(0, mergedCell)
            if len(changeList1) > 0:
                #changeList1[0].cell.type = type
                self.rectifyShadow(changeList1[0])
            changeList1 = []


        print"clist=", len(changeList)

        if (flag == True):
            for i in range(0,len(changeList)-1):
                print"i in t=",i
                if changeList[i+1].cell.y==changeList[i].cell.y+changeList[i].getHeight():
                    topCell = changeList.pop(0)
                    lowerCell = changeList.pop(0)
                    topCell.cell.type = type
                    lowerCell.cell.type = type
                    mergedCell = self.merge(topCell, lowerCell)

                    changeList.insert(0, mergedCell)
                    #changeList[0].cell.type = type
                else:
                    changeList[i].cell.type=type
                    changeList[i+1].cell.type = type
            if len(changeList) > 0:
                #changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])


            if len(changeList) > 0:
                changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])


        else:
            while len(changeList) > 1:
                topCell = changeList.pop(0)
                lowerCell = changeList.pop(0)
                #print topCell.__class__, ",", lowerCell.__class__

                mergedCell = self.merge(topCell, lowerCell)

                changeList.insert(0, mergedCell)
            if len(changeList) > 0:
                changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])
        """
        """
        #step 3: merge cells affected by 2
        changeList = []
        #cc = self.findPoint(x1, y1, self.stitchList[0])
        cc = self.findPoint(x2, y2, self.stitchList[0]).WEST ##Changed according to pointfind
        while cc.cell.y<y2: ## (895-899)lines are inserted
            cc=cc.NORTH
        while cc.cell.y+cc.getHeight() <=y1 :  # find cells to be merged vertically
            changeList.append(cc)
            cc = cc.NORTH
        #print "len3=", len(changeList)
        """
        #while cc.cell.y >= y2: #find cells to be merged vertically
            #changeList.append(cc)
            #cc = cc.SOUTH
        """
        while len(changeList) > 1:
            topCell = changeList.pop(0)
            lowerCell = changeList.pop(0)
            print topCell.__class__, ",", lowerCell.__class__

            mergedCell = self.merge(topCell, lowerCell)

            changeList.insert(0, mergedCell)
            #print "len3=",len(changeList)
        
        #step 4: rectify shadows
        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0]) #correcting empty cells that might be incorrectly split east of newCell
        """


    def rectifyShadow(self, caster):
        """
                this checks the EAST and WEST of caster, to see if there are alligned empty cells that could be merged.
                Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other

                Re-write this to walk along the E and W edges and try to combine neighbors sequentially
                """
        changeSet = []

        cc = caster.EAST #recitfy east side, walking downwards

        while (cc not in self.boundaries and cc.cell.y >= caster.cell.y):
            #if cc.EAST==self.eastBoundary or cc.EAST.cell.type=="EMPTY":#this condition has been added here
            changeSet.append(cc)
            cc = cc.SOUTH
        #print "len4=", len(changeSet)
        i = 0
        j = 1
        while j < len(changeSet): #merge all cells with the same width along the eastern side
           # print "test",len(changeSet),i,j
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            if topCell.EAST==lowerCell.EAST:
                mergedCell = self.merge(topCell, lowerCell)
                if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                    i += 1
                    if j < len(changeSet) : #there was a '-1'
                        j += 1
                else:
                    del changeSet[j]
                    changeSet[i] = mergedCell
            else:
                i += 1
                if j < len(changeSet) - 1 :
                    j += 1



                #print "len3=", len(changeSet)
                #if j < len(changeSet) -1:## these 2 lines have been commented out
                    #j += 1

        cc = caster.WEST#recitfy west side, walking upwards
        changeSet = []

        while (cc not in self.boundaries and cc.cell.y < caster.cell.y + caster.getHeight()):
            #while cc.cell.type=="SOLID":## 2 lines have been included here
                #cc=cc.NORTH

            #if cc.WEST==self.westBoundary or cc.WEST.cell.type=="EMPTY" :#this condition has been added here (or cc.WEST.cell.y!=cc.cell.y and cc.WEST.cell.type=="SOLID")
            changeSet.append(cc)
            cc = cc.NORTH
        #print "lenw=", len(changeSet)
        """
        for foo in changeSet:
            foo.cell.printCell(True, True)
            #print"w=",foo.getWidth()
        """
        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet): #merge all cells with the same width along the eastern side
            topCell = changeSet[i]
            #topCell.cell.printCell(True, True)
            lowerCell = changeSet[j]
            #lowerCell.cell.printCell(True, True)
            if topCell.WEST == lowerCell.WEST:
                mergedCell = self.merge(topCell, lowerCell)
                if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                    i += 1
                    #print "i = ", i
                    if j < len(changeSet)-1 :
                        j += 1
                else:
                    changeSet[i] = mergedCell
                    del changeSet[j]
                #if j < len(changeSet) -1: ## these 2 lines have been commented out
                    #j += 1
            else:
                i += 1
                if j < len(changeSet) - 1:
                    j += 1

        return




    def areaSearch(self, x1, y1, x2, y2):

        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0])# the tile that contains the second(bottom right)corner


        #if  cc.cell.type == "SOLID" and cc.cell.y!=y1 :## cc.cell.x!=x1 and cc.cell.y!=y1 have been added ## cc.cell.x!=x has been deleted
        if cc.cell.type == type and cc.cell.y != y1:  ## cc.cell.x!=x1 and cc.cell.y!=y1 have been added ## cc.cell.x!=x has been deleted
            return True
        elif cc.cell.x + cc.getWidth() < x2 and cc.cell.y!=y1 and cc.cell.x!=x1 :## cc.cell.x!=x1 and cc.cell.y!=y1 have been added
            return True
        cc=cc.SOUTH
        while(cc not in self.boundaries and cc.cell.y+cc.getHeight()> y2):
            while (cc.cell.x + cc.getWidth() <= x1):## = has been inserted after changing point finding  # making sure that the CurrentCell's right edge lays within the area
                cc = cc.EAST  # if it doesn't, traverse the top right stitch to find the next cell of interest
            #if cc.cell.type == "SOLID":
            if cc.cell.type == type:
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x+cc.getWidth()<x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH #check the next lowest cell
        return False
    def Final_Merge(self):
        changeList=[]
        #for cell in self.stitchList:

        for rect in self.stitchList:
            if rect.cell.type==type:
                changeList.append(rect)
        #print len(changeList)
        list_len = len(changeList)

        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1
            while i < len(changeList) - 1:
                # print"i=",i,len(changeList)
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
                        # print"x=",x
                        changeList.insert(x, mergedcell)
                        # self.rectifyShadow(changeList[x])
                        # if j<len(changeList):
                        # j+=1
                i += 1

            if c == list_len:
                break
        # print"len_1",len(changeList)

        for i in range(len(changeList)):
            self.rectifyShadow(changeList[i])
        return

    def set_id(self):
        length=len(self.stitchList)
        i=1

        #print length
        for rect in self.stitchList:
            #if rect.name!=None:
                #print "H",rect.name
            #if rect.cell.type=="SOLID":
            if rect.cell.type == type:
                rect.cell.id=i
                i+=1


        return





    #####################################################################################
    '''
    emptyVPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))
    emptyHPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))


    emptyVStitchList = [emptyVPlane]
    emptyHStitchList = [emptyHPlane]

    emptyVExample = vLayer(emptyVStitchList,level=0,max_x= 60,max_y= 60)
    emptyHExample = hLayer(emptyHStitchList,level=0,max_x=60,max_y= 60)



    emptyVPlane.NORTH = emptyVExample.northBoundary
    emptyVPlane.EAST = emptyVExample.eastBoundary
    emptyVPlane.SOUTH = emptyVExample.southBoundary
    emptyVPlane.WEST = emptyVExample.westBoundary

    emptyHPlane.NORTH = emptyHExample.northBoundary
    emptyHPlane.EAST = emptyHExample.eastBoundary
    emptyHPlane.SOUTH = emptyHExample.southBoundary
    emptyHPlane.WEST = emptyHExample.westBoundary

  



    if len(sys.argv)>1:
        testfile=sys.argv[1] # taking input from command line

        f=open(testfile,"rb") # opening file in binary read mode
        index_of_dot = testfile.rindex('.') # finding the index of (.) in path

        testbase = os.path.basename(testfile[:index_of_dot]) # extracting basename from path
        testdir=os.path.dirname(testfile) # returns the directory name of file
        print testbase
        if not len(testdir):
            testdir='.'

        list = []
        Input=[]
        #a = ["blue","red","green","yellow","black","orange"]
        i = 0
        for line in f.read().splitlines():  # considering each line in file

            c = line.split(',')  # splitting each line with (,) and inserting each string in c
            if len(c) > 5:
                In = [int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4],c[5]]
                Input.append(In)
                #emptyVExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])  # taking parameters of insert function (4 coordinates as integer and type of cell as string)
                #emptyHExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])

                list.append(patches.Rectangle(
                    (int(c[0]), int(c[3])), (int(c[2]) - int(c[0])), (int(c[1]) - int(c[3])),
                    #facecolor=a[i],
                    fill=False,



            ))
    else:
        exit(1)
    print Input
    Connected_H={}
    Connected_V={}
    Group_H=[]
    Group_V=[]
    
   

    emptyVExample.Final_Merge()
    emptyHExample.Final_Merge()
    emptyHExample.set_id()
    emptyVExample.set_id()

    

    #CG = cg.constraintGraph(testdir+'/'+testbase+'gh.png',testdir+'/'+testbase+'gv.png')
    CG = cg.constraintGraph(testdir + '/' + testbase , testdir + '/' + testbase)
    #CG2 = cg.constraintGraph(testdir+'/'+testbase+'gv.png')
    CG.graphFromLayer(emptyHExample,emptyVExample)
    #CG2.graphFromLayer(emptyVExample)


    CG.printVM(testdir+'/'+testbase+'vmat_h.txt',testdir+'/'+testbase+'vmat_v.txt')
    #CG2.printVM(testdir+'/'+testbase+'vmat_v.txt')
    #CG1.printZDL()
    #CG2.printZDL()
    #diGraph1 = cg.multiCG(CG)
    #diGraph2 = cg.multiCG(CG)
    #con = constraint.constraint(1, "minWidth", 0, 1)
    #diGraph.addEdge(con.source, con.dest, con)

    #CG1.drawGraph()

    #diGraph1.drawGraph1()
    #diGraph2.drawGraph2()
   


    CG.cgToGraph_h(testdir + '/' + testbase + 'edgeh.txt')
    CG.cgToGraph_v(testdir + '/' + testbase + 'edgev.txt')
    CSCG = CSCG.CSCG(emptyHExample,emptyVExample, CG,testdir+'/'+testbase,testdir+'/'+testbase)
    
    CSCG.findGraphEdges_h()
    CSCG.drawLayer1()
    CSCG.findGraphEdges_v()
    CSCG.drawLayer2()
    
    CSCG.drawRectangle(list)
    #CSCG.update_stitchList()
    #CSCG.ID_Conversion()
    #CSCG.drawLayer11()
    #CSCG.drawLayer22()

    # CSCG.drawLayer_h()
    # CSCG.drawLayer_v()
    # CSCG.drawLayer_hnew()
    #CSCG.drawLayer_hnew()
    #CSCG.drawLayer_vnew()
    #emptyVExample.drawLayer(truePointer=False)
    #emptyHExample.drawLayer(truePointer=False)
    '''

###################################################################################################################