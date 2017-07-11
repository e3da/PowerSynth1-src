'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''

import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import pylab
from sets import Set
from abc import ABCMeta, abstractmethod

class cell:
    """
    This is the basis for a cell, with only internal information being stored. information pertaining to the 
    structure of a layer or the relative position of a cell is stored in a cornerStitch obj.
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


class cornerStitch:
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

    def getWidth(self): #returns the width
        return (self.EAST.cell.x - self.cell.x)

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

class layer(object):
    """
    A layer is a collection of cornerStitches all existing on the same plane. I'm not sure how we're going to handle
    layers connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of cornerStitches or anything involving coordinates being passed in instead of a cornerStitch
    """
    __metaclass__ = ABCMeta
    def __init__(self, stitchList, max_x, max_y):
        """
        northBoundary and eastBoundary should be integer values, the upper and right edges of the editable rectangle
        """
        self.stitchList = stitchList
        self.northBoundary = cornerStitch(None, None, None, None, None, cell(0, max_y, "EMPTY"))
        self.eastBoundary = cornerStitch(None, None, None, None, None, cell(max_x, 0, "EMPTY"))
        self.southBoundary = cornerStitch(None, None, None, None, None, cell(0, -1000, "EMPTY"))
        self.westBoundary = cornerStitch(None, None, None, None, None, cell(-1000, 0, "EMPTY"))
        self.boundaries = [self.northBoundary, self.eastBoundary, self.westBoundary, self.southBoundary]

    def merge(self, tile1, tile2):
        """
        merge two tiles into one, reassign neighborhood, and return the merged tile in case a reference is needed

        """
        if(tile1.cell.type != tile2.cell.type):
            print "Types are not the same"
            return

        if tile1.cell.x == tile2.cell.x and tile1.cell.y == tile2.cell.y:
            return ("Tiles are not alligned")

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
            return ("Tiles are not alligned")

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

        accountedCells.append(cellListCopy[layer.lowestCell(cellListCopy)]) #adding to accounted cells
        del cellListCopy[layer.lowestCell(cellListCopy)] #removing from the original list so we don't double count

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
        while (y < cc.cell.y or y > (cc.cell.y + cc.getHeight())):
            if (y >= cc.cell.y + cc.getHeight()):
               if(cc.NORTH is not None):
                   cc = cc.NORTH
               else:
                   print("out of bounds 1")
                   return "Failed"
            elif y <= cc.cell.y:
                if(cc.SOUTH is not None):
                    cc = cc.SOUTH
                else:
                    print("out of bounds 2")
                    return "Failed"
        while(x < cc.cell.x or x > (cc.cell.x + cc.getWidth())):
            if(x <= cc.cell.x ):
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
        if not ((cc.cell.x <= x and cc.cell.x + cc.getWidth() >= x) and (cc.cell.y <= y and cc.cell.y + cc.getHeight() >= y)):
            return self.findPoint(x, y, cc)

        return cc

    def plow(self, cornerStitch, destX, destY):
        """
        the cornerStitch cell is moved so that its lower left corner is dextX, destY, and all tiles in the way 
        are moved out of the way. They are in turn moved by recursive calls to plow. 
        """
        return

    def compaction(self, dimension):
        """
        reduce all possible empty space in the dimension specified ("H", or "V"), while still maintaining any 
        design constraints and the relative structure of the layer
        """
        return

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

    #add checking pinter related to location fn

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
        Draw all cells in this layer with stitches pointing to their stitch neighbors
        TODO:
         fix the hardcoded epsilon value of .5, this might lead to improper pointers when the differnce between
         a cell's height and its EAST pointer is less than epsilon. Eventually, we should probably find a way
         to determine epsilon from the layer, but this should handle 90 percent of cases for now. Also should probably
         change the dimensions of the object window depending on the layer size.
        """
        fig1 = matplotlib.pyplot.figure()

        for cell in self.stitchList:

            ax1 = fig1.add_subplot(111, aspect='equal')
            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''

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
                cell.cell.printCell(True, True)
                print cell.SOUTH, cell.SOUTH.cell.x,cell.SOUTH.cell.y, dx, dy
                print cell.getHeight(), "h"
                print cell.getWidth(), "w"
                if cell.SOUTH != self.southBoundary:
                    print cell.SOUTH.getHeight(), "sh"
                    print cell.SOUTH.getWidth(), "sw"
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
        newCell = cornerStitch(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type))
        self.stitchList.append(newCell) #figure out how to fix this and pass in by reference*

        print newCell, self.stitchList[-1]
        print "****VSPLIT", newCell is self.stitchList[-1]

        #assign newCell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x
        if cc != self.southBoundary:
            while cc.cell.x + cc.getWidth() < x:
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
            ccWidth = cc.getWidth() #I don't know why, but this solves getWidth() throwing an error otherwise
            while cc != self.southBoundary and (cc.cell.x + ccWidth <= newCell.cell.x + newCell.getWidth()):
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
        newCell = cornerStitch(None, None, None, None, None, cell(splitCell.cell.x, y, splitCell.cell.type))
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
        while cc.cell.y > newCell.cell.y: #Walk down the right (eastward)edge
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

        cc = newCell.WEST#reassign the SOUTH pointers for the right edge
        if not cc == self.westBoundary:
            while cc != self.northBoundary and cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
                cc.EAST = newCell
                cc = cc.NORTH

        return newCell

class vLayer(layer):
    def insert(self, x1, y1, x2, y2, type):
        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the layer's stitchList, then corrects empty space vertically
        Four steps:
        1. vsplit x1, x2
        2. hsplit y1, y2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = [] #list of empty tiles that contain the area to be effected

        if x2 < x1:
            holder = x2
            x2 = x1
            x1 = holder
        if y2 > y1:
            holder = y2
            y2 = y1
            y1 = holder

        print "x1 = ", x1
        print "x2 = ", x2
        print "y1 = ", y1
        print "y2 = ", y2

        if self.areaSearch(x1, y1, x2, y2): #check to ensure that the area is empty
            return "Area is not empty"

        #1. vsplit x1, x2
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        #don't change the order of these, it won't work otherwise
        if x2 != bottomRight.cell.x and x2 != bottomRight.NORTH.cell.x:  # vertically split the bottom edge
            bottomRight = self.vSplit(bottomRight, x2)
            print "bottomRight = "
            bottomRight.cell.printCell(True, True)
        if x1 != topLeft.cell.x and x1 != topLeft.EAST.cell.x: #vertically split the top edge
            topLeft = self.vSplit(topLeft, x1).SOUTH #topleft will be the first cell below the split line

        #while cc.cell.x < x2: #find all cells that need to be hsplit
        #    changeList.append(cc)
        #    cc = cc.EAST

        #2. hsplit y1, y2
        cc = self.findPoint(x2, y2, self.stitchList[0])
        foo = cc.cell
        while cc.cell.x >= x1:
            print "cc = "
            cc.cell.printCell(True, True)
            if not cc.cell.y == y2: cc = self.hSplit(cc, y2) #order is vital, again
            #self.drawLayer(truePointer=True)
            if not cc.NORTH.cell.y == y1: cc = self.hSplit(foo, y1)
#            cc = cc.NORTH
#            cc = cc.WEST


        #3. merge cells affected by 2
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0])
        cc = cc.EAST
        cc = cc.SOUTH

        while cc.cell.x < x2: #find cells to be merged horizontally
            changeList.append(cc)
            cc = cc.EAST

        for cell in changeList:
            cell.cell.printCell(True, True)
        print "\n\n"
        
        while len(changeList) > 1:
            leftCell = changeList.pop(0)
            rightCell = changeList.pop(0)
            print "leftCell "
            leftCell.cell.printCell(True, True)
            print "rightCell"
            rightCell.cell.printCell(True, True)
            mergedCell = self.merge(leftCell, rightCell)
            changeList.insert(0, mergedCell)

        print changeList[0]
        if len(changeList) > 0:
            self.rectifyShadow(changeList[0]) #correcting empty cells that might be incorrectly split east of newCell

        return changeList

    def rectifyShadow(self, caster):
        """
        this checks the NORTH and SOUTH of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        """
        changeSet = Set()
        cc = caster.NORTH
        lastCell = caster.NORTH
        count = 0
        while (cc != self.northBoundary
               and cc != self.westBoundary
               and cc.cell.y == lastCell.cell.y
               and cc.cell.x >= caster.cell.x):
            if (lastCell.cell.y + lastCell.getHeight() == cc.cell.y + cc.getHeight() and lastCell.cell.x != cc.cell.x):
                changeSet.add(cc)
                changeSet.add(lastCell)
            cc = cc.WEST
            count += 1
            if count != 1:
                lastCell = lastCell.WEST

        while len(changeSet) > 1:
            rightCell = changeSet.pop()
            leftCell = changeSet.pop()
            mergedCell = self.merge(rightCell, leftCell)
            changeSet.add(mergedCell)

        changeSet = Set()
        cc = caster.SOUTH
        lastCell = caster.SOUTH
        count = 0
        while (cc != self.southBoundary
               and cc!=self.eastBoundary
               and cc.cell.y + cc.getHeight() == lastCell.cell.y + lastCell.getHeight()
               and (cc.cell.x + cc.getWidth() <= caster.cell.x + caster.getWidth())):
            if (lastCell.cell.y  == cc.cell.y  and lastCell.cell.x != cc.cell.x):
                changeSet.add(cc)
                changeSet.add(lastCell)

            cc = cc.EAST
            count += 1
            if count != 1:
                lastCell = lastCell.EAST

        #for foo in changeSet:
        #    foo.cell.printCell(True, True)
        while len(changeSet) > 1:
            rightCell = changeSet.pop()
            leftCell = changeSet.pop()
            mergedCell = self.merge(rightCell, leftCell)
            changeSet.add(mergedCell)

        return
    def areaSearch(self, x1, y1, x2, y2):
        """
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)        
        this is designed with vertically aligned space assumptions in mind
        """
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(top right) corner

        if cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.y + cc.getHeight() < y1:
            return True  # the corner cell is empty but touches a solid cell within the search area

        while(cc.EAST.cell.x < x2):
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.y + cc.getHeight() < y1:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.EAST #check the next rightmost cell
            while (cc.cell.y + cc.getHeight() < y2): #making sure that the CurrentCell's right edge lays within the area
                cc = cc.NORTH # if it doesn't, traverse the top right stitch to find the next cell of interest

        return False

class hLayer(layer):
    def insert(self, x1, y1, x2, y2, type):
        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the layer's stitchList, then corrects empty space horizontally
        1. hsplit y1, y2
        2. vsplit x1, x2
        3. merge cells affected by 2
        4. rectify shadows outside of the inserted cell
        """
        changeList = [] #list of empty tiles that contain the area to be effected

        if x2 < x1:
            holder = x2
            x2 = x1
            x1 = holder
        if y2 > y1:
            holder = y2
            y2 = y1
            y1 = holder

        if self.areaSearch(x1, y1, x2, y2): #check to ensure that the area is empty
            return "Area is not empty"

        #step 1: hsplit y1 and y2
        topLeft = self.findPoint(x1, y1, self.stitchList[0])
        bottomRight = self.findPoint(x2, y2, self.stitchList[0])

        #do not change the order of either the hsplit or vpslit sections, this will break it
        if y1 != topLeft.cell.y and y1 != topLeft.NORTH.cell.y: #horizontally split the top edge
            topLeft = self.hSplit(topLeft, y1).SOUTH #topleft will be the first cell below the split line
        if y2 != bottomRight.cell.y and y2 != bottomRight.NORTH.cell.y:#horizontally split the bottom edge
            bottomRight = self.hSplit(bottomRight, y2)

        #step 2: vsplit x1 and x2
        cc = self.findPoint(x1, y1, self.stitchList[0]) #first cell under y1

        while cc.cell.y >= y2: #find all cells that need to be vsplit
            changeList.append(cc)
            cc = cc.SOUTH
            while cc.cell.x + cc.getWidth() <= x2:
                cc = cc.EAST

        for rect in changeList: #split vertically
            if not rect.EAST.cell.x == x2: self.vSplit(rect, x2) #do not reorder these lines
            if not rect.cell.x == x1: self.vSplit(rect, x1)#do not reorder these lines

        #step 3: merge cells affected by 2
        changeList = []
        cc = self.findPoint(x1, y1, self.stitchList[0])

        while cc.cell.y >= y2: #find cells to be merged vertically
            changeList.append(cc)
            cc = cc.SOUTH

        while len(changeList) > 1:
            topCell = changeList.pop(0)
            lowerCell = changeList.pop(0)
            mergedCell = self.merge(topCell, lowerCell)
            changeList.insert(0, mergedCell)

        #step 4: rectify shadows
        if len(changeList) > 0:
            changeList[0].cell.type = type
            self.rectifyShadow(changeList[0]) #correcting empty cells that might be incorrectly split east of newCell

        return changeList
    def rectifyShadow(self, caster):
        """
        this checks the EAST and WEST of caster, to see if there are alligned empty cells that could be merged.
        Primarily called after insert, but for simplicity and OOP's sake, I'm separating this from the other
        
        Re-write this to walk along the E and W edges and try to combine neighbors sequentially
        """
        changeSet = []

        cc = caster.EAST #recitfy east side, walking downwards

        while (cc != self.eastBoundary and cc != self.southBoundary and cc.cell.y >= caster.cell.y):
            changeSet.append(cc)
            cc = cc.SOUTH

        i = 0
        j = 1
        while j < len(changeSet): #merge all cells with the same width along the eastern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                i += 1
                if j < len(changeSet) - 1:
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell
                if j < len(changeSet) - 1:
                    j += 1

        cc = caster.WEST#recitfy west side, walking upwards
        changeSet = []

        while (cc != self.westBoundary and cc != self.northBoundary and cc.cell.y < caster.cell.y + caster.getHeight()):
            changeSet.append(cc)
            cc = cc.NORTH

        for foo in changeSet:
            foo.cell.printCell(True, True)

        i = 0
        j = 1
        while j < len(changeSet) and i < len(changeSet): #merge all cells with the same width along the eastern side
            topCell = changeSet[i]
            lowerCell = changeSet[j]
            mergedCell = self.merge(topCell, lowerCell)
            if mergedCell == "Tiles are not alligned": #the tiles couldn't merge because they didn't line up
                i += 1
                print "i = ", i
                if j < len(changeSet) - 1:
                    j += 1
            else:
                del changeSet[j]
                changeSet[i] = mergedCell
                if j < len(changeSet) - 1:
                    j += 1
        return

    def areaSearch(self, x1, y1, x2, y2):
        """
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)    
        this is designed with horizontally aligned space assumptions in mind
        """
        cc = self.findPoint(x1, y1, self.stitchList[0]) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2, self.stitchList[0]) #the tile that contains the second(top right) corner

        if cc.cell.type == "SOLID":
            return True  # the bottom left corner is in a solid cell
        elif cc.cell.x + cc.getWidth() < x2:
            return True  # the corner cell is empty but touches a solid cell within the search area

        while(cc.SOUTH.cell.y > y2):
            if cc.cell.type == "SOLID":
                return True  # the bottom left corner is in a solid cell
            elif cc.cell.x + cc.getWidth() < x2:
                return True  # the corner cell is empty but touches a solid cell within the search area
            cc = cc.SOUTH #check the next lowest cell
            while(cc.cell.x + cc.getWidth() < x1): #making sure that the CurrentCell's right edge lays within the area
                cc = cc.EAST # if it doesn't, traverse the top right stitch to find the next cell of interest

        return False

class constraintGraph:
    """
    the graph representation of constraints pertaining to cells and variables, informed by several different 
    sources
    """

    def __init__(self, vertices, edges):
        self.vertexMatrix = int[len(vertices)][len(vertices)]
        self.edges = edges

    def getNeighbors(self, vertex):
        """
        return the edge types and neighbors of the vertex passed in
        """
        return

    def getEdgeType(self, v1, v2):
        """
        return the edge type from v1 to v2. If negative, then the edge type is from v2 to v1
        """
        return

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

if __name__ == '__main__':

    a = cornerStitch(None, None, None, None, None, cell(0, 0, "EMPTY"))
    b = cornerStitch(None, None, None, None, None, cell(0, 5, "EMPTY"))
    c = cornerStitch(None, None, None, None, None, cell(5, 5, "SOLID"))
    d = cornerStitch(None, None, None, None, None, cell(10, 5, "EMPTY"))
    e = cornerStitch(None, None, None, None, None, cell(10, 8, "EMPTY"))
    f = cornerStitch(None, None, None, None, None, cell(15, 8, "SOLID"))
    g = cornerStitch(None, None, None, None, None, cell(20, 8, "EMPTY"))
    h = cornerStitch(None, None, None, None, None, cell(0, 10, "EMPTY"))
    i = cornerStitch(None, None, None, None, None, cell(0, 12, "EMPTY"))
    # j = cornerStitch(None, None, None, None, None, cell(0, 17, "EMPTY"))
    k = cornerStitch(None, None, None, None, None, cell(7, 12, "SOLID"))
    #l = cornerStitch(None, None, None, None, None, cell(15, 15, "EMPTY"))

    stitchList = [a,b,c,d,e,f,g,h,i,k]

    emptyVPlane = cornerStitch(None, None, None, None, None, cell(0, 0, "EMPTY"))
    emptyHPlane = cornerStitch(None, None, None, None, None, cell(0, 0, "EMPTY"))

    emptyVStitchList = [emptyVPlane]
    emptyHStitchList = [emptyHPlane]
    exampleVLayer = vLayer(stitchList, 30, 30)
    exampleHLayer = hLayer(stitchList, 30, 30)
    emptyVExample = vLayer(emptyVStitchList, 30, 30)
    emptyHExample = hLayer(emptyHStitchList, 30, 30)

    emptyVPlane.NORTH = emptyVExample.northBoundary
    emptyVPlane.EAST = emptyVExample.eastBoundary
    emptyVPlane.SOUTH = emptyVExample.southBoundary
    emptyVPlane.WEST = emptyVExample.westBoundary

    emptyHPlane.NORTH = emptyHExample.northBoundary
    emptyHPlane.EAST = emptyHExample.eastBoundary
    emptyHPlane.SOUTH = emptyHExample.southBoundary
    emptyHPlane.WEST = emptyHExample.westBoundary

    #emptyVExample.insert(11, 15, 20, 5, "SOLID")
    #emptyVExample.insert(15, 25, 25, 20, "SOLID")
    #emptyVExample.insert(5, 17, 27, 16, "SOLID")

    #emptyVExample.insert(15, 20, 20, 15, "SOLID")
    #emptyVExample.insert(10, 5, 17, 10, "SOLID")

    emptyHExample.insert(10, 10, 13, 5, "SOLID")
    emptyHExample.insert(20, 13, 25, 8, "SOLID")
    emptyHExample.insert(15, 20, 17, 3, "SOLID")

    """
    emptyVExample.vSplit(emptyVExample.stitchList[0], 15)
    foo = emptyVExample.findPoint(20, 1, emptyVExample.stitchList[0])
    emptyVExample.vSplit(foo, 20)
    foo = emptyVExample.findPoint(16, 21, emptyVExample.stitchList[0])
    emptyVExample.hSplit(foo, 20)
    foo = emptyVExample.findPoint(16, 21, emptyVExample.stitchList[0])
    emptyVExample.hSplit(foo, 21)
    foo = emptyExample.findPoint(6, 19)
    print foo
 

    for cell in emptyHExample.stitchList:
        cell.cell.printCell(True, True, True)
        print cell
        print cell.getWidth(), " width"
        print cell.getHeight(), "Height "
    """
    foo = emptyHExample.findPoint(18.5, 10.5, emptyHExample.stitchList[0])
    print "*****************************testing directions"
    emptyHExample.eastSouth(foo).cell.printCell(True, True)
    emptyHExample.southEast(foo).cell.printCell(True, True)
    emptyHExample.westNorth(foo).cell.printCell(True, True)
    emptyHExample.northWest(foo).cell.printCell(True, True)
    emptyHExample.drawLayer(truePointer=True)
    #print layer.directedAreaEnumeration(5, 25, 15, 15)
