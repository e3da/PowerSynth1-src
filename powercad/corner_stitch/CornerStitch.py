'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''

import copy

class cell:
    """
    This is the basis for a cell, with only internal information being stored. information pertaining to the 
    structure of a layer or the relative position of a cell is stored in a cornerStitch obj.
    """
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type


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
    def __init__(self, stitchList, northBoundary, eastBoundary):
        self.stitchList = stitchList
        self.NORTH_BOUNDARY = northBoundary
        self.EAST_BOUNDARY = eastBoundary
        self.SOUTH_BOUNDARY = 0
        self.WEST_BOUNDARY = 0

    def createTile(self, x1, y1, x2, y2):
        return


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

    def findLayerDimensions(self):
        """
        ***possibly depreciated, talk to Dr. Peng***
        this should be called after all solid tiles are declared, to find out the horizontal and vertical dimensions
        of this layer. After this is called, then you can call setEmptyTiles, which needs to know the layer dims.
        """
        rightExtreme = 0
        topExtreme = 0

        for cell in self.stitchList:
            print dir(cell)
            if cell.cell.x + cell.getWidth() > rightExtreme:
                rightExtreme = cell.cell.x
            if cell.cell.y + cell.getHeight() > topExtreme:
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

    def findPoint(self, x, y):
        """
        find the tile that contains the coordinates x, y
        """
        cc = self.stitchList[0] #current cell
        while (y < cc.cell.y or y > (cc.cell.y + cc.getHeight())):
            if (y > cc.cell.y + cc.getHeight()):
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
        while(x < cc.cell.x or x > (cc.cell.x + cc.getWidth())):
            if(x < cc.cell.x ):
                if(cc.WEST is not None):
                    cc = cc.WEST
                else:
                    print("out of bounds 3")
                    return "Failed"
            if(x > (cc.cell.x + cc.getWidth())):
                if(cc.EAST is not None):
                    cc = cc.EAST
                else:
                    print("out of bounds 4")
                    return "Failed"

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

    a = cornerStitch(None, None, None, None, None, cell(0, 20, "SOLID"))
    b = cornerStitch(None, None, None, None, None, cell(0, 10, "EMPTY"))
    c = cornerStitch(None, None, None, None, None, cell(0, 0, "SOLID"))
    d = cornerStitch(None, None, None, None, None, cell(10, 20, "EMPTY"))
    e = cornerStitch(None, None, None, None, None, cell(10, 10, "SOLID"))
    f = cornerStitch(None, None, None, None, None, cell(10, 0, "SOLID"))
    g = cornerStitch(None, None, None, None, None, cell(20, 15, "SOLID"))
    h = cornerStitch(None, None, None, None, None, cell(20, 0, "EMPTY"))
    northBoundary = cornerStitch(None, None, None, None, None, cell(0, 30, "EMPTY"))
    eastBoundary = cornerStitch(None, None, None, None, None, cell(30, 0, "EMPTY"))
    southBoundary = cornerStitch(None, None, None, None, None, cell(0, -1000, "EMPTY"))
    westBoundary = cornerStitch(None, None, None, None, None, cell(-1000, 0, "EMPTY"))

    a.EAST = d
    a.SOUTH = b
    a.NORTH = northBoundary
    a.WEST = westBoundary

    b.NORTH = a
    b.EAST = e
    b.SOUTH = c
    b.WEST = westBoundary

    c.NORTH = b
    c.EAST = f
    c.SOUTH = southBoundary
    c.WEST = westBoundary

    d.WEST = a
    d.SOUTH = e
    d.EAST = g
    d.NORTH = northBoundary

    e.NORTH = d
    e.EAST = g
    e.SOUTH = f
    e.WEST = b

    f.NORTH = e
    f.EAST = h
    f.WEST = c
    f.SOUTH = southBoundary

    g.SOUTH = h
    g.WEST = d
    g.NORTH = northBoundary
    g.EAST = eastBoundary

    h.NORTH = g
    h.WEST = e
    h.EAST = eastBoundary
    g.SOUTH = southBoundary

    stitchList = [a,b,c,d,e,f,g,h]
    layer = layer(stitchList, 30, 30)

    print layer.setEmptyTiles('H')

