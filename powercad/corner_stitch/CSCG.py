import numpy as np
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import PatchCollection
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import pylab
import copy

class CSCG:
    """
    a cornerstitch representation with edges corresponding to constraint graph edges bolded
    """
    def __init__(self, CS, CG,name):
        self.CS = CS
        self.CG = CG
        self.name=name
    #def drawCGLines(self, figure):

    def drawZeroDimsVertices(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        if self.CS.orientation == 'v':
            for point in self.CG.zeroDimensionList:
                wedgeList.append(Wedge((0, point), .5, 0, 360, width = 1))
        elif self.CS.orientation == 'h':
            for point in self.CG.zeroDimensionList:
                wedgeList.append(Wedge((point, 0), .5, 0, 360, width = 1))

        return wedgeList

    #figure this out later
    def findGraphEdges(self):
        matrixCopy = np.copy(self.CG.getVertexMatrix())
        print matrixCopy[0][1]
        arrowList = []#contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

        edgeList = copy.deepcopy(getattr(self.CG, "edges"))

        if self.CS.orientation == 'h':
            for stitch in self.CS.stitchList:
                for edge in edgeList:
                    if (self.CG.zeroDimensionList[edge.source] == stitch.cell.getX()
                            and self.CG.zeroDimensionList[edge.dest] == stitch.cell.getX() + stitch.getWidth()):
                        if edge.getConstraint().getConstraintName() == "Empty":
                            color = "red"
                        elif edge.getConstraint().getConstraintName() == "type1":
                            color = "blue"
                        arrowList.append((stitch.cell.getX(), stitch.cell.getY(), stitch.getWidth(), 0, color))
                        edgeList.remove(edge)
        elif self.CS.orientation == 'v':
            for stitch in self.CS.stitchList:
                for edge in edgeList:
                    if (self.CG.zeroDimensionList[edge.source] == stitch.cell.getY()
                             and self.CG.zeroDimensionList[edge.dest] == stitch.cell.getY() + stitch.getHeight()):
                        if edge.getConstraint().getConstraintName() == "Empty":
                            color = "red"
                        elif edge.getConstraint().getConstraintName() == "type1":
                            color = "blue"
                        arrowList.append((stitch.cell.getX(), stitch.cell.getY(), 0, stitch.getHeight(), color))
                        edgeList.remove(edge)

        for foo in arrowList:
            print foo
        return arrowList
    """
    def setAxisLabels(self, plt):
        if self.CS.orientation == 'v':
            labels = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionList)))
            plt.yticks(self.CG.zeroDimensionList, list(labels))
        elif self.CS.orientation == 'h':
            labels = ('X' + str(i) for i in range(0, len(self.CG.zeroDimensionList)))
            plt.xticks(self.CG.zeroDimensionList, list(labels))
    """
    def drawLayer(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        fig1 = matplotlib.pyplot.figure()

        for cell in self.CS.stitchList:



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
            if cell.getNorth() == self.CS.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.5 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getNorth().cell.y + (.5 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
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
            if cell.getEast() == self.CS.eastBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getEast().cell.x + (.5 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getEast().cell.y + (.5 * cell.getEast().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
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
            if cell.getSouth() == self.CS.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.5 * cell.getSouth().getWidth()) - (cell.cell.x + .5)
                dy = cell.getSouth().cell.y + (.5 * cell.getSouth().getHeight()) - (cell.cell.y + .5)
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
            if cell.getWest() == self.CS.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.5 * cell.getWest().getWidth()) - (cell.cell.x + .5)
                dy = cell.getWest().cell.y + (.5 * cell.getWest().getHeight()) - (cell.cell.y + .5)
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
        p = PatchCollection(self.drawZeroDimsVertices())
        ax1.add_collection(p)

        #handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        #automatically handle orientation
        #self.setAxisLabels(plt)

        for arr in self.findGraphEdges():
            ax1.arrow(arr[0], arr[1], arr[2], arr[3], head_width = .30, head_length = .3,  color =arr[4] )#

        plt.xlim(0, self.CS.eastBoundary.cell.x)
        plt.ylim(0, self.CS.northBoundary.cell.y)

        if self.name:
            fig1.savefig(self.name,bbox_inches='tight')
            matplotlib.pyplot.close(fig1)
        else:
            fig1.show()
            pylab.pause(11000)  # figure out how to do this better

    def drawRectangle(self,list=[],*args):
        fig = plt.figure()
        ax3 = fig.add_subplot(111, aspect='equal')
        for p in list:
            ax3.add_patch(p)
        plt.xlim(0,60)
        plt.ylim(0,60)
        fig.savefig(self.name+'-1.png',bbox_inches='tight')
