'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''

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

    def __init__(self, north, east, south, west, hint):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.HINT = hint #this is the pointer to the hint tile of where to start looking for location

    def getHeight(self): #returns the height
        return
    def getWidth(self): #returns the width
        return
    def findNeighbors(self):
        """
        find all cells, empty or not, touching the starting tile
        """
        neighbors = []

        cc = self.EAST  #Walk downwards along the topright (NE) corner
        while (cc.y + cc.height > self.y):
            print "1 appending" , cc.x , " ", cc.y
            neighbors.append(cc)
            if cc.SOUTH is not None:
                cc = cc.SOUTH
            else:
                break

        cc = self.SOUTH #Walk eastwards along the bottomLeft (SW) corner
        while (cc.x  < self.x + self.width):
            print "2 appending" , cc.x , " ", cc.y
            neighbors.append(cc)
            if cc.EAST is not None:
                cc = cc.EAST
            else:
                break

        cc = self.WEST #Walk northwards along the bottomLeft (SW) corner
        while (cc.y < self.y + self.height):
            print "3 appending" , cc.x , " ", cc.y
            neighbors.append(cc)
            if cc.NORTH is not None:
                cc = cc.NORTH
            else:
                break

        cc = self.NORTH #Walk westwards along the topright (NE) corner
        while (cc.x + cc.width > self.x):
            print "4 appending" , cc.x , " ", cc.y
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

    def __init__(self, stitchList):
        self.stitchList = stitchList

    def createTile(self, x1, y1, x2, y2):
        return

    def setEmptyTiles(self, allignment):
        """
        reset all empty tiles according to the algorithm laid out in the paper. allignment should equal "H" or "V", to 
         specify horizontal or vertical allignment, respectively. 
        """
        return

    def findLayerDimensions(self):
        """
        this should be called after all solid tiles are declared, to find out the horizontal and vertical dimensions
        of this layer. After this is called, then you can call setEmptyTiles, which needs to know the layer dims.
        """
        return

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
        x1y1 = the top left corner, x2y2 = bottom right corner        

        firstCornerCell = self.FindPoint(x1, y1) #the tile that contains the first corner point

        if firstCornerCell.type == "SOLID":
            return True #the corner is in a solid cell
        elif firstCornerCell.x + firstCornerCell.width < x2:
            return True #the corner cell is empty but touches a solid cell within the search area
        #elif :
        """
        return

    def findPoint(self, x, y):
        """
        find the tile that contains the coordinates x, y
        """
        cc = self #current cell
        while (y < cc.y or y > (cc.y + cc.height)):
            if (y < cc.y):
               if(cc.NORTH is not None):
                   cc = cc.NORTH
               else:
                   print("out of bounds 1")
                   return "Failed"
            elif(y > (cc.y + cc.height)):
                if(cc.SOUTH is not None):
                    cc = cc.SOUTH
                else:
                    print("out of bounds 2")
                    return "Failed"
        while(x < cc.x or x > (cc.x + cc.width)):
            if(x < cc.x ):
                if(cc.WEST is not None):
                    cc = cc.WEST
                else:
                    print("out of bounds 3")
                    return "Failed"
            if(x > (cc.x + cc.width)):
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
        this should call subroutines for simple and complex reduction, to pare the constraint graph down to its 
        minimum form
        """
        return

    def simpleReduce(self):
        return

    def complexReduce(self):
        return

    def minSpanTree(self, vertex):
        """
        returns a min spanning tree starting from vertex
        """
        return