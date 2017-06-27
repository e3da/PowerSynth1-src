'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''

import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import pylab

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

class layer:
    """
    A layer is a collection of cornerStitches all existing on the same plane. I'm not sure how we're going to handle
    layers connecting to one another yet so I'm leaving it unimplemented for now. Layer-level operations involve
    collections of cornerStitches or anything involving coordinates being passed in instead of a cornerStitch
    """
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

    def insert(self, x1, y1, x2, y2, type):
        """
        insert a new solid cell into the rectangle defined by the top left corner(x1, y1) and the bottom right corner
        (x2, y2) and adds the new cell to the layer's stitchList
        """
        changeList = [] #list of empty tiles that contain the area to be affected

        if self.areaSearch(x1, y1, x2, y2): #check to ensure that the area is empty
            return "Area is not empty"

        topLeft = self.findPoint(x1, y1)
        bottomRight = self.findPoint(x2, y2)

        if y1 != topLeft.cell.y and y1 != topLeft.NORTH.cell.y: #horizontally split the top edge
            topLeft = self.hSplit(topLeft, y1).SOUTH
        if y2 != bottomRight.cell.y and y2 != bottomRight.NORTH.cell.y:#horizontally split the bottom edge
            bottomRight = self.hSplit(topLeft, y2)

        cc = topLeft
        while cc.cell.y >= y2:
            print cc.cell.y, "inside while"
            print cc.SOUTH.cell.y, "south y"
            changeList.append(cc)
            cc = cc.SOUTH
        return changeList

    def split(self):
        """
        """
        return

    def merge(self, tile1, tile2):
        """
        merge two tiles into one, reassign neighborhood, and return the merged tile in case a reference is needed
        """
        if(tile1.cell.type != tile2.cell.type):
            print "Types are not the same"
            return

        print tile1.getWidth()
        print tile2.getWidth()

        print tile1.cell.x
        print tile2.cell.x

        if tile1.cell.x == tile2.cell.x and (tile1.NORTH == tile2 or tile1.SOUTH == tile2) and tile1.getWidth() == tile2.getWidth():
            print "insid efirst if"
            basis = tile1 if tile1.cell.y < tile2.cell.y else tile2
            upper = tile1 if tile1.cell.y > tile2.cell.y else tile2

            #reassign the newly merged tile's neighbors. We're using the lower of the tiles as the basis tile.
            basis.NORTH = upper.NORTH
            basis.EAST = upper.EAST

            #reasign the neighboring tile's directional pointers
            cc = upper.NORTH
            while cc not in self.boundaries and cc.cell.x > basis.cell.x: #reset northern neighbors
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
        """
        ***possibly depreciated, talk to Dr. Peng***
        this should be called after all solid tiles are declared, to find out the horizontal and vertical dimensions
        of this layer. After this is called, then you can call setEmptyTiles, which needs to know the layer dims.
        """
        rightExtreme = 0
        topExtreme = 0

        for cell in self.stitchList + boundaries:
            if cell.EAST is None:
                if cell.cell.x > rightExtreme:
                    rightExtreme = cell.cell.x
            elif cell.cell.x + cell.getWidth() > rightExtreme :
                rightExtreme = cell.cell.x

            if cell.NORTH is None:
                 if cell.cell.y > topExtreme:
                     topExtreme = cell.cell.y
            elif cell.cell.y + cell.getHeight() > topExtreme :
                topExtreme = cell.cell.y

        return [rightExtreme, topExtreme]

    def deleteTile(self, tile):
        return

    def directedAreaEnumeration(self, x1, y1, x2, y2):
        """
        returns all solid tiles in the rectangle specified. x1y1 = top left corner, x2y2 = topright
        """
        return

    def areaSearch(self, x1, y1, x2, y2):
        """
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the upper left corner, x2y2 = bottom right corner (as per the paper's instructions)        
        """
        cc = self.findPoint(x1, y1) #the tile that contains the first corner point
        secondCorner = self.findPoint(x2, y2) #the tile that contains the second(top right) corner

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
        print "cc = ", cc.cell.x, cc.cell.y
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

    def drawLayer(self):
        """
        Draw all cells in this layer with stitches pointing to their stitch neighbors
        TODO:
         fix the hardcoded epsilon value of .5, this might lead to improper pointers when the differnce between
         a cell's height and its EAST pointer is less than epsilon. Eventually, we should probably find a way
         to determine epsilon from the layer, but this should handle 90 percent of cases for now. Also should probably
         change the dimensions of the object window depending on the layer size.
        """
        fig1 = matplotlib.pyplot.figure()

        for cell in stitchList:

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
        newCell = cornerStitch(None, None, None, None, None, cell(x, splitCell.cell.y, splitCell.cell.type))
        self.stitchList.append(newCell)

        #assign newCell neighbors
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.WEST = splitCell

        cc = splitCell.SOUTH #Walk along the bottom edge until you find the cell that encompases x
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
        while cc.cell.x >= x:
            cc.SOUTH = newCell
            cc = cc.WEST

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        while cc.cell.y >= newCell.cell.y:
            cc.WEST = newCell
            cc = cc.SOUTH

        cc = newCell.SOUTH#reassign the SOUTH pointers for the right edge
        while cc.cell.x + cc.getWidth() <= newCell.cell.x + newCell.getWidth():
            cc.NORTH = newCell
            cc = cc.EAST

        print "vsplit", newCell.cell.x, newCell.cell.y
        return newCell

    def hSplit(self, splitCell, y):
        """
        newCell is the top half of the split
        """
        newCell = cornerStitch(None, None, None, None, None, cell(splitCell.cell.x, y,  splitCell.cell.type))
        self.stitchList.append(newCell)
        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        #assign new cell directions
        newCell.NORTH = splitCell.NORTH
        newCell.EAST = splitCell.EAST
        newCell.SOUTH = splitCell

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        cc = splitCell.WEST
        if not cc == self.westBoundary:
            while cc.cell.y + cc.getHeight() < y: #Walk upwards along the old west
                cc = cc.NORTH
        newCell.WEST = cc

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        #reassign splitCell N
        splitCell.NORTH = newCell
        #reassign splitCell E
        cc = newCell.EAST
        while cc.cell.y > newCell.cell.y: #Walk down the right (eastward)edge
            cc = cc.SOUTH
        splitCell.EAST = cc

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        #reassign the neighboring cells directional poitners
        cc = newCell.NORTH #reassign the SOUTH pointers for the top edge along the split half
        if not cc == self.northBoundary:
            while cc.cell.x >= newCell.cell.x:
                print "inside reassign NORTH", cc.cell.x, cc.cell.y
                cc.SOUTH = newCell
                cc = cc.WEST

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        cc = newCell.EAST #reassign the WEST pointers for the right edge
        if not cc == self.eastBoundary:
            while cc.cell.y >= newCell.cell.y:
                cc.WEST = newCell
                cc = cc.SOUTH

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y


        cc = newCell.WEST#reassign the SOUTH pointers for the right edge
        if not cc == self.westBoundary:
            while cc.cell.y + cc.getHeight() <= newCell.cell.y + newCell.getHeight():
                cc.EAST = newCell
                cc = cc.NORTH

        print "SPLITCELL.SOUTH = ", splitCell.SOUTH.cell.x, splitCell.SOUTH.cell.y

        return newCell


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
    exampleLayer = layer(stitchList, 30, 30)

    a.NORTH = d
    a.EAST = exampleLayer.eastBoundary
    a.SOUTH = exampleLayer.southBoundary
    a.WEST = exampleLayer.westBoundary

    b.NORTH = h
    b.EAST = c
    b.SOUTH = a
    b.WEST = exampleLayer.westBoundary

    c.NORTH = h
    c.EAST = e
    c.SOUTH = a
    c.WEST = b

    d.NORTH = g
    d.EAST = exampleLayer.eastBoundary
    d.SOUTH = a
    d.WEST = c

    e.NORTH = h
    e.EAST = f
    e.SOUTH = d
    e.WEST = c

    f.NORTH = exampleLayer.northBoundary
    f.EAST = g
    f.SOUTH = d
    f.WEST = e

    g.NORTH = exampleLayer.northBoundary
    g.EAST = exampleLayer.eastBoundary
    g.WEST = f
    g.SOUTH = d

    h.NORTH = k
    h.EAST = f
    h.SOUTH = b
    h.WEST = exampleLayer.westBoundary

    i.NORTH = exampleLayer.northBoundary
    i.EAST = k
    i.SOUTH = h
    i.WEST = exampleLayer.westBoundary

    k.NORTH = exampleLayer.northBoundary
    k.EAST = f
    k.SOUTH = h
    k.WEST = i

    #l.NORTH = exampleLayer.northBoundary
    #l.EAST = exampleLayer.eastBoundary
    #l.SOUTH = f
    #l.WEST = k

    foo = exampleLayer.findPoint(15, 8, exampleLayer.stitchList[0])
    print "BEgin test\n\n"
    foo.printNeighbors(printX=True, printY=True)


    #print layer.findLayerDimensions([northBoundary, eastBoundary, southBoundary, westBoundary])
    #foo = exampleLayer.areaSearch(2, 10, 3, 20)
    #print foo
    exampleLayer.drawLayer()

    #print layer.directedAreaEnumeration(5, 25, 15, 15)
