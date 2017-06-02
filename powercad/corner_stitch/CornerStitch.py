'''
Created on June 1, 2017

@author: John Calvin Alumbaugh, jcalumba
'''

class cell:
    """
    Abstract class of cells, there eventually will be multiple
    implementations of cells with different physical properties
    We're using the bare minimum four pointer configuration 
    presented in the paper. As per the paper, only the left and bottom sides
    are explicitly defined, everything else being implicitly defined by neighbors
    """

    def __init__(self, north, east, south, west, x, y, height, width, type):
        self.NORTH = north #This is the right-top pointer to the rightmost cell on top of this cell
        self.EAST = east #This is the top-right pointer to the uppermost cell to the right of this cell
        self.SOUTH = south #This is the left-bottom pointer to the leftmost cell on the bottom of this cell
        self.WEST = west #This is the bottom-left pointer to the bottommost cell on the left of this cell
        self.width = width
        self.height = height
        self.x = x #length of bottom side
        self.y = y#length of left side
        self.type = type#empty, power type, etc...

    def FindPoint(self, x, y):
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

    def FindNeighbors(self):
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

    def AreaSearch(self, x1, y1, x2, y2):
        """
        Find if there are solid tiles in the rectangle defined by two diagonal points
        x1y1 = the top left corner, x2y2 = bottom right corner        
        """
        firstCornerCell = self.FindPoint(x1, y1) #the tile that contains the first corner point

        if firstCornerCell.type == "SOLID":
            return True #the corner is in a solid cell
        elif firstCornerCell.x + firstCornerCell.width < x2:
            return True #the corner cell is empty but touches a solid cell within the search area
        elif :



if __name__ == '__main__':

    a = cell(None, None, None, None, 0, 20, 10, 10,"SOLID")
    b = cell(None, None, None, None, 0, 10, 10, 10, "EMPTY")
    c = cell(None, None, None, None, 0, 0, 10, 10, "SOLID")
    d = cell(None, None, None, None, 10, 20, 10, 10, "EMPTY")
    e = cell(None, None, None, None, 10, 10, 10, 10,"SOLID")
    f = cell(None, None, None, None, 10, 0, 10, 10,"SOLID")
    g = cell(None, None, None, None, 20, 15, 15, 10,"SOLID")
    h = cell(None, None, None, None, 20, 0, 15, 10,"EMPTY")

    a.EAST = d
    a.SOUTH = b

    b.NORTH = a
    b.EAST = e
    b.SOUTH = c

    c.NORTH = b
    c.EAST = f

    d.WEST = a
    d.SOUTH = e
    d.EAST = g

    e.NORTH = d
    e.EAST = g
    e.SOUTH = f
    e.WEST = b

    f.NORTH = e
    f.EAST = h
    f.WEST = c

    g.SOUTH = h
    g.WEST = d

    h.NORTH = g
    h.WEST = e

    ret = e.FindNeighbors()
    for i in ret:
        print (i.x, i.y)