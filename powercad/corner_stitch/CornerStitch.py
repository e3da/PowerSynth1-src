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
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def printCell(self, printX = False, printY = False, printType = False):
        if printX: print "x = ", self.x
        if printY: print "y = ", self.y
        if printType: print "type = ", self.type
        return

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getType(self):
        return self.type

class tile:
    """
    Abstract class of cells, there eventually will be multiple
    implementations of cells with different physical properties
    We're using the bare minimum four pointer configuration 
    presented in the paper. As per the paper, only the left and bottom sides
    are explicitly defined, everything else being implicitly defined by neighbors
    """

    def __init__(self, north, east, south, west, hint, cell):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.HINT = hint #this is the pointer to the hint tile of where to start looking for location
        self.cell = cell

    def printNeighbors(self, printX = False, printY = False, printType = False):
        if self.NORTH is not None: print "N", self.NORTH.cell.printCell(printX, printY, printType)
        if self.EAST is not None: print "E", self.EAST.cell.printCell(printX, printY, printType)
        if self.SOUTH is not None: print "S", self.SOUTH.cell.printCell(printX, printY, printType)
        if self.WEST is not None: print "W", self.WEST.cell.printCell(printX, printY, printType)


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
        while cc.cell.x > center.cell.x + center.getWidth():
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

    #returns a list of neighbors
    def findNeighbors(self):
        """
        find all cells, empty or not, touching the starting tile
        """
        neighbors = []

        cc = self.EAST  #Walk downwards along the topright (NE) corner
        while (cc.cell.y + cc.getHeight() > self.cell.y):
            print "1 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.SOUTH is not None:
                cc = cc.SOUTH
            else:
                break

        cc = self.SOUTH #Walk eastwards along the bottomLeft (SW) corner
        while (cc.cell.x  < self.cell.x + self.getWidth()):
            print "2 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.EAST is not None:
                cc = cc.EAST
            else:
                break

        cc = self.WEST #Walk northwards along the bottomLeft (SW) corner
        while (cc.cell.y < self.cell.y + self.getHeight()):
            print "3 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.NORTH is not None:
                cc = cc.NORTH
            else:
                break

        cc = self.NORTH #Walk westwards along the topright (NE) corner
        while (cc.cell.x + cc.getWidth() > self.cell.x):
            print "4 appending" , cc.cell.x , " ", cc.cell.y
            neighbors.append(cc)
            if cc.WEST is not None:
                cc = cc.WEST
            else:
                break

        return neighbors

class cornerStitch(object):
    """
    A cornerStitch is a collection of tilees all existing on the same plane. I'm not sure how we're going to handle
    cornerStitchs connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of tiles or anything involving coordinates being passed in instead of a tile
    """
    __metaclass__ = ABCMeta
    def __init__(self, stitchList, max_x, max_y):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.northBoundary = tile(None, None, None, None, None, cell(0, max_y, "EMPTY"))
        self.eastBoundary = tile(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
        self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
        self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
        self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        orientation = ''

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
        cellListCopy = copy.deepcopy(self.stitchList)
        accountedCells = []

        accountedCells.append(cellListCopy[cornerStitch.lowestCell(cellListCopy)]) #adding to accounted cells
        del cellListCopy[cornerStitch.lowestCell(cellListCopy)] #removing from the original list so we don't double count

        print len(cellListCopy)
        print len(accountedCells)
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

        if y > self.northBoundary.cell.y:
            return self.northBoundary
        if y < 0:
            return self.southBoundary
        if x > self.eastBoundary.cell.x:
            return self.eastBoundary
        if x < 0:
            return self.westBoundary

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

    def drawLayer(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """
        fig1 = matplotlib.pyplot.figure()

        for cell in self.stitchList:

            ax1 = fig1.add_subplot(111, aspect='equal')
            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''
            print "type of cell in this loop", type(cell)
            ax1.add_patch(
                matplotlib.patches.Rectangle(
                    (cell.cell.x, cell.cell.y),  # (x,y)
                    cell.getWidth(),  # width
                    cell.getHeight(),  # height
                    hatch = pattern,
                    fill=False
                )
            )
            #NORTH pointer
            if cell.NORTH == self.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.NORTH.cell.x + (.5 * cell.NORTH.getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.NORTH.cell.y + (.5 * cell.NORTH.getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx =  0
                dy = .75

            ax1.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight()- .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #EAST pointer
            if cell.EAST == self.eastBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.EAST.cell.x + (.5 * cell.EAST.getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.EAST.cell.y + (.5 * cell.EAST.getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx = .75
                dy = 0
            ax1.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight()- .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #SOUTH pointer
            if cell.SOUTH == self.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.SOUTH.cell.x + (.5 * cell.SOUTH.getWidth()) - (cell.cell.x + .5)
                dy = cell.SOUTH.cell.y + (.5 * cell.SOUTH.getHeight()) - (cell.cell.y + .5)
            else:
                dx =  0
                dy = -.5
            ax1.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #WEST pointer
            if cell.WEST == self.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.WEST.cell.x + (.5 * cell.WEST.getWidth()) - (cell.cell.x + .5)
                dy = cell.WEST.cell.y + (.5 * cell.WEST.getHeight()) - (cell.cell.y + .5)
            else:
                dx =  -.5
                dy = 0
            ax1.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )

        plt.xlim(0, self.eastBoundary.cell.x)
        plt.ylim(0, self.northBoundary.cell.y)
        fig1.show()
        pylab.pause(11000)  # figure out how to do this better

    def vSplit(self, splitCell, x):
        if x < splitCell.cell.x or x > splitCell.cell.x + splitCell.getWidth():
            print "out of bounds, x = ", x
            return
        newCell = tile(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type))
        self.stitchList.append(newCell) #figure out how to fix this and pass in by reference*

        #print newCell, self.stitchList[-1]
        #print "****VSPLIT", newCell is self.stitchList[-1]

        #assign newCell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x
        if cc != self.southBoundary:
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
        if cc != self.northBoundary:
            while cc.cell.x >= x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        if cc != self.eastBoundary:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the NORTH pointers for the bottom edge
        if cc != self.southBoundary:
            cc.SOUTH.cell.printCell(True, True)
            ccWidth = cc.getWidth() #I don't know why, but this solves getWidth() throwing an error otherwise
            while cc != self.eastBoundary and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
                cc.NORTH = newCell
                cc = cc.EAST
                if cc != self.eastBoundary:
                    ccWidth = cc.getWidth()  # I don't know why, but this solves getWidth() throwing an error otherwise

        return newCell

    def hSplit(self, splitCell, y):
        """
        newCell is the top half of the split
        """
        if y < splitCell.cell.y or y > splitCell.cell.y + splitCell.getHeight():
            print "out of bounds, y = ", y
            return
        newCell = tile(None, None, None, None, None, cell(splitCell.cell.x, y, splitCell.cell.type))
        self.stitchList.append(newCell)

        #assign new cell directions
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH = splitCell

        cc = splitCell.WEST
        if cc != self.westBoundary and cc != self.northBoundary:
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
        if not cc == self.northBoundary:
            while cc.cell.x >= newCell.cell.x:
                cc.SOUTH = newCell
                cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        if not cc == self.eastBoundary:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        cc = newCell.WEST#reassign the EAST pointers for the right edge

        if not cc == self.westBoundary:
            while cc != self.northBoundary and cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
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

class vLayer(cornerStitch):
    def __init__(self, stitchList, max_x, max_y):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """

        self.stitchList = stitchList
        self.northBoundary = tile(None, None, None, None, None, cell(0,max_y, "EMPTY"))
        self.eastBoundary = tile(None, None, None, None, None, cell(max_x,0, "EMPTY"))
        self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
        self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
        self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        self.orientation = 'v'



    def insert(self, x1, y1, x2, y2, type):
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
        #1. vsplit x1, x2
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])
        if topLeft.cell.y==y1:
            topLeft=topLeft.SOUTH
            while topLeft.cell.x+topLeft.getWidth()<x1 :
                topLeft=topLeft.EAST

        #don't change the order of these, it won't work otherwise

        if x2 != bottomRight.cell.x and x2 != bottomRight.EAST.cell.x:  # vertically split the bottom edge
            bottomRight = self.vSplit(bottomRight, x2)

        if x1 != topLeft.cell.x and x1 != topLeft.EAST.cell.x: #vertically split the top edge
            topLeft = self.vSplit(topLeft, x1) #topleft will be the first cell below the split line

        #2. hsplit y1, y2
        cc = self.findPoint(x2, y2, self.stitchList[0])

        #print "xco2=", cc.cell.x


        while(cc.cell.x + cc.getWidth()> x1 ) :############## + cc.getWidth() has been added
            if cc.cell.x==x2:
                cc=cc.WEST
                #print "xco2=", cc.cell.x
                    #changeList.append(cc)
            else:
                while cc.cell.y + cc.getHeight() <= y2:
                    cc = cc.NORTH
                changeList.append(cc)
                cc = cc.WEST
                #if cc.cell.x>=x1 and cc.cell.y<=y2 and cc.cell.y+cc.getHeight()>=y1:# >= is inserted
                    #changeList.append(cc)
                #if cc.WEST!=self.westBoundary and cc.cell.type!="SOLID" and cc.cell.x+cc.getWidth()<x1:
                    #cc = cc.WEST
        print"chlen=", len(changeList)
        for rect in changeList:

            if not rect.NORTH.cell.y == y1: self.hSplit(rect, y1)
            if not rect.cell.y == y2: self.hSplit(rect, y2)#order is vital, again


        #3. merge cells affected by 2
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0])
        #print "xco2=", cc.cell.x
        #cc = cc.EAST
        while cc.cell.y >= y1:
            cc = cc.SOUTH
        #print "cc = "
        #cc.cell.printCell(True, True)

        while cc.cell.x < x2: #find cells to be merged horizontally
            if cc.cell.x>=x1:
                changeList.append(cc)
            cc = cc.EAST

       # if direction=True:
        print "chl=", len(changeList)
        """
        """
        while len(changeList) > 1:
                print "in second loop"
                leftCell = changeList.pop(0)
                rightCell = changeList.pop(0)
                mergedCell = self.merge(leftCell, rightCell)
                changeList.insert(0, mergedCell)
        """
        """
        #print"len=", len(changeList)
       # else:
        while len(changeList) > 1:
               # print " in first loop", len(changeList)
                topCell = changeList.pop(0)
                lowerCell = changeList.pop(0)
                mergedCell = self.merge(topCell, lowerCell)
                changeList.insert(0, mergedCell)
        #print " bf second loop",len(changeList)

        #print"mlen=", len(changeList)
        if len(changeList) > 0:
            print"Type=",type
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0]) #correcting empty cells that might be incorrectly split east of newCell

        return changeList
        """
        """
        New algorithm
        """
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])
        tr= self.findPoint(x2, y1, self.stitchList[0])
        bl= self.findPoint(x1, y2, self.stitchList[0])
        if topLeft.cell.y == y1:
            topLeft = topLeft.SOUTH
            while topLeft.cell.x + topLeft.getWidth() <= x1:
                topLeft = topLeft.EAST

        if bottomRight.cell.x==x2  :  ## and bottomRight.cell.y==y2 has been added to consider overlapping
            bottomRight = bottomRight.WEST
                # bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
            while (bottomRight.cell.y + bottomRight.getHeight() < y2):
                bottomRight = bottomRight.NORTH

        splitList = []
        splitList.append(bottomRight)
        #print"x=",bottomRight.NORTH.cell.y
        if bottomRight.SOUTH != self.southBoundary and bottomRight.SOUTH.cell.type == "SOLID" and bottomRight.SOUTH.cell.y+bottomRight.SOUTH.getHeight() == y2 or bottomRight.cell.type=="SOLID":
            cc1 = bottomRight.SOUTH
            while cc1.cell.x+cc1.getWidth()<x2:
                cc1 = cc1.EAST
            if cc1 not in splitList:
                splitList.append(cc1)
            if cc1.cell.type == "SOLID" and cc1.cell.y+cc1.getHeight() == y2:
                cc2 = cc1.SOUTH
                while cc2.cell.x+cc2.getWidth()<x2:
                    cc2 = cc2.EAST
                if cc2 not in splitList:
                    splitList.append(cc2)
        cc= bottomRight
        while cc.cell.y<=y1 and cc!=self.northBoundary:

            if cc not in splitList:
                splitList.append(cc)
            cc = cc.NORTH
            while cc.cell.x > x2:
                cc = cc.WEST
        if cc.cell.type=="SOLID" and cc.cell.y==y1 or tr.cell.type=="SOLID":
            if cc not in splitList and cc!=self.northBoundary:
                splitList.append(cc)
            if cc.NORTH !=self.northBoundary:
                cc=cc.NORTH
                while cc.cell.x > x2:
                    cc = cc.WEST
                splitList.append(cc)

        print"splitListx2=", len(splitList)
        for rect in splitList:
            if x2 != rect.cell.x and x2 != rect.EAST.cell.x:
                self.vSplit(rect, x2)

        splitList = []
        splitList.append(topLeft)

        if topLeft.NORTH != self.northBoundary and topLeft.NORTH.cell.type == "SOLID" and topLeft.NORTH.cell.y == y1 or topLeft.cell.type=="SOLID":
            cc = topLeft.NORTH
            while cc.cell.x>x1:
                cc=cc.WEST
            splitList.append(cc)

            if cc.cell.type == "SOLID" and cc.cell.y == y1:
                cc1 = cc.NORTH
                while cc1.cell.x > x1:
                    cc1 = cc1.WEST
                if cc1 not in splitList and cc !=self.westBoundary:
                    splitList.append(cc1)
        cc=topLeft
        while cc!=self.southBoundary and cc.cell.y+cc.getHeight() >=y2 :
            if cc not in splitList:
                splitList.append(cc)

            cc=cc.SOUTH
            while cc!=self.southBoundary and cc.cell.x+cc.getWidth()<=x1:
                cc=cc.EAST

        if cc.cell.type == "SOLID" and cc.cell.y+cc.getHeight() == y2 or bl.cell.type == "SOLID":
            if cc not in splitList and cc!=self.southBoundary:
                splitList.append(cc)
            if cc.cell.type=="SOLID" and cc.cell.y+cc.getHeight() == y2:
                if cc.SOUTH != self.southBoundary:
                    cc = cc.SOUTH
                while cc.cell.x + cc.getWidth() <= x1:
                    cc = cc.EAST
                splitList.append(cc)

        print"splitListx1=", len(splitList)
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
        print"chlen=", len(changeList)
        for rect in changeList:

            if not rect.NORTH.cell.y == y1: self.hSplit(rect, y1)
            if not rect.cell.y == y2: self.hSplit(rect, y2)  # order is vital, again

        resplit = []
        # cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        cc = self.findPoint(x1, y2, self.stitchList[0])
        print"resplit1=", cc.cell.x, cc.cell.y, cc.cell.x+cc.getWidth()
        while cc.cell.x+cc.getWidth() <= x2:
            if cc.SOUTH.cell.type == "SOLID" and cc.SOUTH.cell.y + cc.SOUTH.getHeight() == y2 and cc.SOUTH != self.southBoundary and cc.SOUTH.cell.x+cc.SOUTH.getWidth() != cc.cell.x+cc.getWidth():
                resplit.append(cc.SOUTH)
                resplit.append(cc.SOUTH.SOUTH)
            #if cc.EAST.cell.type == "SOLID" and cc.EAST.cell.x == x2 and cc.EAST != self.eastBoundary and cc.EAST.cell.y != cc.cell.y:
                #resplit.append(cc.EAST)
                #resplit.append(cc.EAST.EAST)
            print"resplit=", len(resplit)
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
           if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1 and cc.NORTH != self.northBoundary and cc.NORTH.cell.x+cc.NORTH.getWidth() != cc.cell.x+cc.getWidth():
               resplit.append(cc.NORTH)
               resplit.append(cc.NORTH.NORTH)
               print"resplit=", len(resplit)
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
            if cc.NORTH.cell.type == "SOLID" and cc.NORTH.cell.y == y1:
                changeList.append(cc.NORTH)
            cc = cc.EAST
            while cc.cell.y >= y1:
                cc = cc.SOUTH
        print"list=", len(changeList)
        done = False
        dirn = 1  # to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH

        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y >= y1:
            t = t.SOUTH
        print"t.x,y=", t.cell.x, t.cell.y
        #if t.NORTH.cell.type == "SOLID" and t.NORTH.cell.y == y1:
            #changeList.append(t.NORTH)
        changeList.append(t)

        while (done == False):
            if dirn == 1:
                child = t.EAST
                while child.cell.y >= y1:  # t.cell.y
                    child = child.SOUTH
                if child.WEST == t and child.cell.x < x2 and child.cell.y >= y2:  # = inserted later
                    print"entry"

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
            if cc1.SOUTH.cell.type == "SOLID" and cc1.SOUTH.cell.y +cc1.SOUTH.getHeight()== y2:
                changeList.append(cc1.SOUTH)
            cc1 = cc1.EAST
            while cc1.cell.y > y2:
                cc1 = cc1.SOUTH
        print"arealist=", len(changeList)
        changeList.sort(key=lambda cc: cc.cell.x)

        for foo in changeList:
            foo.cell.printCell(True, True)
            print "\n\n"

        ##### Merge Algorithm:


        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            if top.cell.y == low.cell.y + low.getHeight() or top.cell.y + top.getHeight() == low.cell.y:
                top.cell.type = type
                low.cell.type = type
                print"topx=", top.NORTH.cell.x, top.NORTH.cell.y, top.cell.x + top.getWidth()
                print"lowx=", low.cell.x, low.cell.y, low.cell.x + low.getWidth()
                mergedcell = self.merge(top, low)
                if mergedcell == "Tiles are not alligned":
                    print"-i=", i
                    i += 1
                else:
                    del changeList[i + 1]
                    del changeList[i]
                    changeList.insert(i, mergedcell)
                    print"i=",i
            else:
                i += 1

        list_len = len(changeList)
        print"len=", list_len
        c = 0

        while (len(changeList) > 1):
            i = 0
            c += 1

            while i < len(changeList) - 1:
                print"i=", i, len(changeList)
                j = 0
                while j < len(changeList):
                    # j=i+1
                    print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type
                    print"topx=", top.cell.x, top.cell.y
                    print"lowx=", low.cell.x, low.cell.y
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
        print"len_1", len(changeList)

        """
        i = 0
        while i < len(changeList) - 1:

            top = changeList[i + 1]
            low = changeList[i]
            # if top.cell.x == low.cell.x + low.getWidth() or top.cell.x + top.getWidth() == low.cell.x:
            top.cell.type = type
            low.cell.type = type
            mergedcell = self.merge(top, low)
            if mergedcell == "Tiles are not alligned":
                i += 1
            else:
                del changeList[i + 1]
                del changeList[i]
                changeList.insert(i, mergedcell)
        """
        for foo in changeList:
            foo.cell.printCell(True, True)
        for x in range(0, len(changeList)):
            changeList[x].cell.type = type
            print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x += 1

        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0])

        for x in range(0,len(changeList)):
            changeList[x].cell.type = type
            print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x+=1
        return changeList


        ####

        """
        while (cc.cell.x + cc.getWidth() > x1):  ############## + cc.getWidth() has been added
            if cc.cell.x == x2:
                cc = cc.WEST
               # print "xco2=", cc.cell.y+cc.getHeight()
                # changeList.append(cc)
            else:
                while cc.cell.y + cc.getHeight() <= y2:
                    cc = cc.NORTH
                changeList.append(cc)
                cc = cc.WEST
                # if cc.cell.x>=x1 and cc.cell.y<=y2 and cc.cell.y+cc.getHeight()>=y1:# >= is inserted
                # changeList.append(cc)
                # if cc.WEST!=self.westBoundary and cc.cell.type!="SOLID" and cc.cell.x+cc.getWidth()<x1:
                # cc = cc.WEST
        print"chlen=", changeList[0].cell.x
        for rect in changeList:

            if not rect.NORTH.cell.y == y1: self.hSplit(rect, y1)
            if not rect.cell.y == y2: self.hSplit(rect, y2)  # order is vital, again
        """
        """
        ## New Merge Algorithm

        flag= False
        changeList = []
        changeList1 = []
        #flag = False
        cc = self.findPoint(x1, y2, self.stitchList[0])
        print"x1y2=", cc.cell.y
        while cc.cell.x + cc.getWidth() <= x2:
            if (cc.NORTH.cell.type == "SOLID"):
                flag = True
                changeList1.append(cc)
                changeList1.append(cc.NORTH)
            if cc.SOUTH.cell.type == "SOLID":
                flag = True
                if (cc not in changeList1):
                    changeList1.append(cc)
                #changeList1.append(cc)
                # print"x1y2=", cc.cell.y
                changeList1.append(cc.SOUTH)
                # print"x1y2=", cc.EAST.cell.y
            if (cc not in changeList1):
                changeList.append(cc)
            print"clist1=", len(changeList1)
            cc = cc.EAST
            while len(changeList1) > 1:
                topCell = changeList1.pop(0)
                lowerCell = changeList1.pop(0)
                # print topCell.__class__, ",", lowerCell.__class__
                topCell.cell.type=type
                lowerCell.cell.type = type
                mergedCell = self.merge(topCell, lowerCell)

                changeList1.insert(0, mergedCell)
            if len(changeList1) > 0:
                #changeList1[0].cell.type = type
                self.rectifyShadow(changeList1[0])
            changeList1 = []

        print"clist=", len(changeList)
     
        k=1
        if (flag == True):
            while len(changeList)>1:
                topCell = changeList.pop(0)
                lowerCell = changeList.pop(0)
                if lowerCell.cell.x == topCell.cell.x + topCell.getWidth():
                    topCell.cell.type = type
                    lowerCell.cell.type = type
                    mergedCell = self.merge(topCell, lowerCell)
                    changeList.insert(0, mergedCell)
                    #changeList[0].cell.type = type
                    k=0
                else:
                    changeList.append(topCell)
                    changeList.append(lowerCell)
                    break



            print"clist=", len(changeList)
            if k==1 and len(changeList)>0:
                for i in (0,len(changeList)-1):

                    changeList[i].cell.type = type
                #changeList[i + 1].cell.type = type

            if len(changeList) > 0:
                # changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])

            if len(changeList) > 0:
                changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])


        else:
            print "k=", k
            print"clist=", len(changeList)
            while len(changeList) > 1:
                topCell = changeList.pop(0)
                lowerCell = changeList.pop(0)
                # print topCell.__class__, ",", lowerCell.__class__

                mergedCell = self.merge(topCell, lowerCell)

                changeList.insert(0, mergedCell)
            if len(changeList) > 0:
                changeList[0].cell.type = type
                self.rectifyShadow(changeList[0])
    """
    def rectifyShadow(self, caster):
        """
        this checks the NORTH and SOUTH of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        """
        changeSet = []

        cc = caster.NORTH #recitfy north side, walking downwards

        while (cc != self.northBoundary and cc != self.westBoundary and cc.cell.x >= caster.cell.x):
            #if cc.NORTH==self.northBoundary or cc.NORTH.cell.type=="EMPTY":
            changeSet.append(cc)
            cc = cc.WEST
        print "len=", len(changeSet)
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

        while (cc != self.southBoundary and cc != self.eastBoundary and cc.cell.x < caster.cell.x + caster.getWidth()):
            if cc.SOUTH == self.southBoundary or cc.SOUTH.cell.type == "EMPTY":
                changeSet.append(cc)
            cc = cc.EAST
        print "len=", len(changeSet)
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
                    print "i = ", i
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

        if   cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.y >y2:
            return True  # the corner cell is empty but touches a solid cell within the search area

        cc=cc.EAST
        while (cc!=self.eastBoundary and cc.cell.x< x2):
            #if cc.cell.y<y1 and cc.cell.type=="SOLID":
                #return True ## these 2 lines have been commented out
            while(cc.cell.y+cc.getHeight()>y2):
                if cc.cell.y<y1 and cc.cell.type=="SOLID":
                    return True
                if cc.SOUTH!=self.southBoundary:
                    cc=cc.SOUTH
                else:
                    break
            cc=cc.EAST


        return False

class hLayer(cornerStitch):
    def __init__(self, stitchList, max_x, max_y):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.northBoundary = tile(None, None, None, None, None, cell(0, max_y, "EMPTY"))
        self.eastBoundary = tile(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
        self.southBoundary = tile(None, None, None, None, None, cell(0, -1000, "EMPTY"))
        self.westBoundary = tile(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
        self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]
        self.orientation = 'h'

    def insert(self, x1, y1, x2, y2, type):
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
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])
        tr=self.findPoint(x2, y1, self.stitchList[0])
        bl=self.findPoint(x1, y2, self.stitchList[0])

        if topLeft.cell.y==y1:
            cc=topLeft
            if topLeft.SOUTH!=self.southBoundary:
                cc=topLeft.SOUTH
            while cc.EAST!=self.eastBoundary and cc.cell.x+cc.getWidth()<=x1: ## 2 lines have been added
                    cc=cc.EAST
            #while cc.cell.y >= y2: #find all cells that need to be vsplit
            topLeft=cc
        print"topx=",topLeft.cell.x
        print"topy=", topLeft.cell.y
        splitList=[]
        splitList.append(topLeft)
        cc=topLeft
        if cc.WEST != self.westBoundary and cc.WEST.cell.type=="SOLID" and cc.WEST.cell.x+cc.WEST.getWidth()==x1 or cc.cell.type=="SOLID":
            cc1 = cc.WEST
            while cc1.cell.y + cc1.getHeight() < y1:
                cc1 = cc1.NORTH
            print "testwx", cc1.cell.x
            splitList.append(cc1)
           # if cc1.cell.type=="SOLID" and cc1.cell.x+cc1.getWidth()==x1:
            cc2=cc1.WEST
            #print"cc2=",cc2.cell.y+cc2.getHeight()
            while cc2!=self.westBoundary and cc2.cell.y + cc2.getHeight() < y1:
                cc2 = cc2.NORTH
            if cc2!=self.westBoundary:
                splitList.append(cc2)
        print"cc.x",cc.cell.x

        while cc.cell.x<=x2 and cc!=self.eastBoundary:#it was only <x2
            if cc not in splitList:
                print "testx",cc.cell.x+cc.getWidth()
                splitList.append(cc)

            cc=cc.EAST
            print"cc.x2", cc.cell.y
            while cc.cell.y >= y1:#previously it was >y1
                cc= cc.SOUTH
        if cc.cell.type=="SOLID" and cc.cell.x==x2 and cc!=self.eastBoundary or (tr.cell.type=="SOLID" and tr.cell.y!=y1 and cc!=self.eastBoundary):
            print "testex", cc.cell.x
            splitList.append(cc)
            if cc.EAST!=self.eastBoundary:
                cc=cc.EAST

                while cc.cell.y >= y1:#previously it was >y1
                    cc= cc.SOUTH
            #print "testsx", cc.cell.x
                splitList.append(cc)

        print"splitListy1=",len(splitList)
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
        print"bot=", bottomRight.cell.y
        splitList = []
        splitList.append(bottomRight)
        cc=bottomRight
        if cc.EAST!= self.eastBoundary and cc.EAST.cell.type=="SOLID" and cc.EAST.cell.x==x2 or cc.cell.type=="SOLID":
            cc1 = cc.EAST
            while cc1.cell.y >  y2:
                cc1 = cc1.SOUTH
            splitList.append(cc1)
            if cc1.cell.type=="SOLID" and cc1.cell.x==x2:
                cc2=cc1.EAST
                while cc1.cell.y > y2:
                    cc2 = cc2.SOUTH
                splitList.append(cc2)
        while cc.cell.x>=x1 and cc!=self.westBoundary:#it was cc.WEST!= (previously >x1)
            cc = cc.WEST

            if cc!=self.westBoundary:
                while cc.cell.y+cc.getHeight() <= y2  :#previously it was <y2
                    cc= cc.NORTH
            if cc not in splitList:
                splitList.append(cc)


        print"cc2.x", cc.cell.x
        if cc.cell.type=="SOLID" and cc.cell.x+cc.getWidth()>=x1 or bl.cell.type=="SOLID"   :#previously it was ==x1 or bl.cell.x+bl.getWidth()>x1
            if cc not in splitList:
                splitList.append(cc)
            if cc.WEST!=self.westBoundary:
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
        print"splitListy2=", len(splitList)
        for rect in splitList:
            if y2 != rect.cell.y and y2 != rect.NORTH.cell.y:
                self.hSplit(rect, y2)






        """
        #do not change the order of either the hsplit or vpslit sections, this will break it
        if y1 != topLeft.cell.y and y1 != topLeft.NORTH.cell.y: #horizontally split the top edge
            topLeft = self.hSplit(topLeft, y1).SOUTH #topleft will be the first cell below the split line
        
        if y2 != bottomRight.cell.y and y2 != bottomRight.NORTH.cell.y:#horizontally split the bottom edge
            if bottomRight.cell.type=="SOLID": ## this part has been corrected
                bottomRight = bottomRight.WEST
                #bottomRight= self.findPoint(x2,y2, self.stitchList[0]).WEST
                while(bottomRight.cell.y+bottomRight.getHeight()<y2):
                    bottomRight = bottomRight.NORTH

            bottomRight = self.hSplit(bottomRight, y2)
        """
        changeList=[]
        #step 2: vsplit x1 and x2
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
            cc = cc.EAST
        while (cc!=self.southBoundary and cc.cell.y+cc.getHeight()>y2):
            while cc.cell.x + cc.getWidth() <= x1:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc=cc.SOUTH
        print"vlistx1=", len(changeList)

        #changeList = []
        # step 2: vsplit x1 and x2
        cc = self.findPoint(x2, y1, self.stitchList[0]).SOUTH
        if cc.cell.x==x2:
            cc=cc.WEST
        while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
            cc = cc.EAST

        while (cc!=self.southBoundary and cc.cell.y+cc.getHeight()>y2):
            while cc.cell.x + cc.getWidth() < x2:  ## 2 lines have been added
                cc = cc.EAST
            if cc not in changeList:
                changeList.append(cc)
            cc = cc.SOUTH
        print"vlistx2=", len(changeList)
        for rect in changeList:  # split vertically
            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2)  # do not reorder these lines
            if not rect.cell.x == x1: self.vSplit(rect, x1)  # do not reorder these lines
        """
        cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH  ##Changed according to pointfind #first cell under y1
        print"top1=", cc.cell.x
        while(cc!=self.southBoundary and cc.cell.y+cc.getHeight()>y2):     ##has been added +cc.getHeight()
            while cc.cell.x+cc.getWidth()<=x1: ## 2 lines have been added
                cc=cc.EAST
        #while cc.cell.y >= y2: #find all cells that need to be vsplit
            changeList.append(cc)
            cc1=cc
            while(cc1.cell.x+cc1.getWidth()<x2 and cc1.EAST!=self.eastBoundary):##While loop has been added to consider overlapping
                cc1=cc1.EAST
                while cc1.cell.y >y1:  # this condition has been added
                    cc1= cc1.SOUTH
                if cc1 not in changeList:
                    changeList.append(cc1)

            cc = cc.SOUTH
            while cc.cell.x>x1 and cc.WEST!=self.westBoundary:
                cc=cc.WEST

            #while cc != self.southBoundary and cc != self.eastBoundary and cc.cell.x + cc.getWidth() < x2:#it was <=x2 (commented out for overlapping)
                #cc = cc.EAST

        print"vlist=",len(changeList)
        for foo in changeList:
            foo.cell.printCell(True, True)

        for rect in changeList: #split vertically
            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2) #do not reorder these lines
            if not rect.cell.x == x1: self.vSplit(rect, x1)#do not reorder these lines
        """
        #flag = False
        #### resplitting is required for those cases, where horizontal splitting is required other than top edge or bottom edge
        """
        resplit=[]
        #cc = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        cc=topLeft
        print"resplit1=",cc.cell.x
        while cc.cell.y >= y2:
            if cc.WEST.cell.type == "SOLID" and cc.WEST.cell.x + cc.WEST.getWidth() == x1 and cc.WEST != self.westBoundary and cc.WEST.cell.y != cc.cell.y:
                resplit.append(cc.WEST)
                resplit.append(cc.WEST.WEST)
            if cc.EAST.cell.type == "SOLID" and cc.EAST.cell.x == x2 and cc.EAST != self.eastBoundary and cc.EAST.cell.y != cc.cell.y:
                resplit.append(cc.EAST)
                resplit.append(cc.EAST.EAST)
            print"resplit=", len(resplit)
            for rect in resplit:
                flag = True
                self.hSplit(rect, cc.cell.y)
            resplit=[]
            cc = cc.SOUTH
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
        cc = topLeft.SOUTH
        while cc!=self.southBoundary and cc.cell.x<x1:
            cc=cc.EAST
        print"resplit1=", cc.cell.x

        while cc.cell.y >= y2:
            cc1 = cc
            resplit = []
            min_y=0
            while cc1.cell.x + cc1.getWidth() <= x2:
                if cc1.cell.y>min_y:
                    min_y=cc1.cell.y
                resplit.append(cc1)
                if cc1.cell.x==x1 and cc1.WEST!=self.westBoundary:
                    resplit.append(cc1.WEST)
                cc1=cc1.EAST
            if len(resplit)>1:
                for foo in resplit:
                    if foo.cell.y<min_y:
                        if foo.cell.y!=min_y:
                            self.hSplit(foo,min_y)
            cc=cc.SOUTH

            """
                if cc1.EAST.cell.x<x2:
                    if cc1.cell.y < cc1.EAST.cell.y:
                    resplit.append(cc1)
                else:
                    resplit.append(cc)
                cc1 = cc1.EAST
                while cc1.cell.y > cc.cell.y:
                    cc1 = cc1.SOUTH
            
            print"resplit=", len(resplit)
            for rect in resplit:
                #flag = True
                self.hSplit(rect, y)
            resplit = []
            cc = cc.SOUTH
        """

        #changeList = []


        changeList=[]
        done = False
        dirn =1# to_leaves
        t = self.findPoint(x1, y1, self.stitchList[0]).SOUTH
        while t.cell.x + t.getWidth() <= x1:  ## 2 lines have been added
            t = t.EAST
        while t.cell.y>=y1:
            t=t.SOUTH
        if t.WEST.cell.type=="SOLID" and t.WEST.cell.x+t.WEST.getWidth()==x1:
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
                    if child.cell.type == "SOLID" and child.cell.x == x2:
                        if child not in changeList:
                            changeList.append(child)
                    dirn = 2#to_root
            else:
                if t.cell.x <= x1 or t.cell.y <= y2:
                    if t.cell.y > y2:
                        t = t.SOUTH
                        while t.cell.x + t.getWidth() <= x1:
                            t = t.EAST
                        if t.WEST.cell.type == "SOLID" and t.WEST.cell.x + t.WEST.getWidth() == x1:
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
        print"arealist=", len(changeList)
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




        #for foo in changeList1:
            #foo.cell.printCell(True, True)

        ## New Merge Algorithm v2


        i=0
        while i<len(changeList)-1:

            top=changeList[i+1]
            low=changeList[i]
            print"topx=", top.cell.x, top.cell.y
            print"lowx=", low.cell.x, low.cell.y
            if top.cell.x==low.cell.x+low.getWidth() or top.cell.x+top.getWidth()==low.cell.x:
                top.cell.type=type
                low.cell.type=type
                mergedcell=self.merge(top,low)
                if mergedcell=="Tiles are not alligned":
                    i+=1
                else:
                    del changeList[i+1]
                    del changeList[i]
                    print"arealist=", len(changeList)
                    if len(changeList)==0:
                        changeList.append(mergedcell)
                    else:
                        changeList.insert(i,mergedcell)
                    self.rectifyShadow(changeList[i])
            else:
                i+=1

 
            
        list_len= len(changeList)
        print"len=",list_len
        c=0

        while(len(changeList)>1):
            i=0
            c+=1

            while i< len(changeList)-1:
                print"i=",i,len(changeList)
                j=0
                while j<len(changeList):
                    #j=i+1
                    print"j=", j

                    top = changeList[j]
                    low = changeList[i]
                    top.cell.type = type
                    low.cell.type = type
                    print"topx=", top.cell.x, top.cell.y
                    print"lowx=", low.cell.x, low.cell.y
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
        print"len_1",len(changeList)
        
        ######
        
        

        for foo in changeList:
            foo.cell.printCell(True, True)
        for x in range(0,len(changeList)):
            changeList[x].cell.type = type
            print"x=", changeList[x].cell.x, changeList[x].cell.y
            self.rectifyShadow(changeList[x])
            x+=1

        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0])


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

        while (cc != self.eastBoundary and cc != self.southBoundary and cc.cell.y >= caster.cell.y):
            #if cc.EAST==self.eastBoundary or cc.EAST.cell.type=="EMPTY":#this condition has been added here
            changeSet.append(cc)
            cc = cc.SOUTH
        print "len4=", len(changeSet)
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

        while (cc != self.westBoundary and cc != self.northBoundary and cc.cell.y < caster.cell.y + caster.getHeight()):
            #while cc.cell.type=="SOLID":## 2 lines have been included here
                #cc=cc.NORTH

            #if cc.WEST==self.westBoundary or cc.WEST.cell.type=="EMPTY" :#this condition has been added here (or cc.WEST.cell.y!=cc.cell.y and cc.WEST.cell.type=="SOLID")
            changeSet.append(cc)
            cc = cc.NORTH
        print "lenw=", len(changeSet)
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
                    print "i = ", i
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

    """
    def areaSearch(self, x1, y1, x2, y2):
        
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)    
        this is designed with horizontally aligned space assumptions in mind
        
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(top right) corner

        if cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.x + cc.getWidth() < x2:
            return True# the corner cell is empty but touches a solid cell within the search area
  
        while(cc.SOUTH.cell.y > y2):
            
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x + cc.getWidth() < x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH #check the next lowest cell
            while (cc.cell.x + cc.getWidth() < x1):  # making sure that the CurrentCell's right edge lays within the area
                cc = cc.EAST# if it doesn't, traverse the top right stitch to find the next cell of interest

        return False
    """
    def areaSearch(self, x1, y1, x2, y2):
       
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0])# the tile that contains the second(bottom right)corner


        if  cc.cell.type == "SOLID" and cc.cell.y!=y1 :## cc.cell.x!=x1 and cc.cell.y!=y1 have been added ## cc.cell.x!=x has been deleted
            return True
        elif cc.cell.x + cc.getWidth() < x2 and cc.cell.y!=y1 and cc.cell.x!=x1 :## cc.cell.x!=x1 and cc.cell.y!=y1 have been added
            return True
        cc=cc.SOUTH
        while(cc!= self.southBoundary and cc.cell.y+cc.getHeight()> y2):
            while (cc.cell.x + cc.getWidth() <= x1):## = has been inserted after changing point finding  # making sure that the CurrentCell's right edge lays within the area
                cc = cc.EAST  # if it doesn't, traverse the top right stitch to find the next cell of interest
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x+cc.getWidth()<x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH #check the next lowest cell
        return False

if __name__ == '__main__':
    emptyVPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))
    emptyHPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))

    emptyVStitchList = [emptyVPlane]
    emptyHStitchList = [emptyHPlane]
    #exampleVLayer = vLayer(stitchList, 30, 30)
    #exampleHLayer = hLayer(stitchList, 30, 30)
    emptyVExample = vLayer(emptyVStitchList, 40, 60)
    emptyHExample = hLayer(emptyHStitchList, 40, 60)

    emptyVPlane.NORTH = emptyVExample.northBoundary
    emptyVPlane.EAST = emptyVExample.eastBoundary
    emptyVPlane.SOUTH = emptyVExample.southBoundary
    emptyVPlane.WEST = emptyVExample.westBoundary

    emptyHPlane.NORTH = emptyHExample.northBoundary
    emptyHPlane.EAST = emptyHExample.eastBoundary
    emptyHPlane.SOUTH = emptyHExample.southBoundary
    emptyHPlane.WEST = emptyHExample.westBoundary




    #emptyHExample.insert(5,20,15,5,"SOLID")
    #emptyHExample.insert(8, 15, 12, 10, "SOLID")



    if len(sys.argv)>1:
        testfile=sys.argv[1] # taking input from command line
        f=open(testfile,"rb") # opening file in binary read mode
        index_of_dot = testfile.rindex('.') # finding the index of (.) in path
        testbase = os.path.basename(testfile[:index_of_dot]) # extracting basename from path
        testdir=os.path.dirname(testfile) # returns the directory name of file
        if not len(testdir):
            testdir='.'

        list = []
        for line in f.read().splitlines():  # considering each line in file
            l=1
            c = line.split(',')  # splitting each line with (,) and inserting each string in c
            if len(c) > 4:
                emptyVExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])  # taking parameters of insert function (4 coordinates as integer and type of cell as string)

                list.append(patches.Rectangle(
                    (int(c[0]), int(c[3])), (int(c[2]) - int(c[0])), (int(c[1]) - int(c[3])),

                    fill=False,



                ))
            l+=1
    else:
        exit(1)


    CG = cg.constraintGraph()
    #CG.graphFromLayer(emptyVExample)
    CG.graphFromLayer(emptyVExample)

    CG.printVM()
    CG.printZDL()
    diGraph = cg.multiCG(CG)
    con = constraint.constraint(1, "minWidth", 0, 1)
    diGraph.addEdge(con.source, con.dest, con)

    #CG.drawGraph()
    #diGraph.drawGraph()

    #CSCG = CSCG.CSCG(emptyVExample, CG,testdir+'/'+testbase+'.png')
    CSCG = CSCG.CSCG(emptyVExample, CG,testdir+'/'+testbase+'.png')
    #CSCG=CSCG.CSCG(emptyVExample, CG)
    CSCG.findGraphEdges()
    CSCG.drawLayer()
    CSCG.drawRectangle(list)
    #emptyVExample.drawLayer(truePointer=False)
    #emptyHExample.drawLayer(truePointer=False)

