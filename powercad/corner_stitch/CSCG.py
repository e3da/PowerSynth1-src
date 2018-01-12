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
    '''
    def __init__(self, CS, CG,name):
        self.CS = CS
        self.CG = CG
        self.name=name
    #def drawCGLines(self, figure):
    '''
    def __init__(self, cornerStitch_h,cornerStitch_v, CG,name1,name2):
        self.cornerStitch_h = cornerStitch_h
        self.cornerStitch_v = cornerStitch_v
        self.CG = CG
        self.name1=name1
        self.name2 = name2
    def drawZeroDimsVertices1(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        #if self.CS.orientation == 'v':
        #elif self.CS.orientation == 'h':
        for point in self.CG.zeroDimensionListh:
            #print self.CG.zeroDimensionListh.index(point)
            wedgeList.append(Wedge((point, 0), .5, 0, 360, width = 1))

        return wedgeList

    def drawZeroDimsVertices2(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        # if self.CS.orientation == 'v':
        for point in self.CG.zeroDimensionListv:
            wedgeList.append(Wedge((0, point), .5, 0, 360, width=1))


        return wedgeList
    #figure this out later

    ###final
    def findGraphEdges_h(self):
        #matrixCopy = np.copy(self.CG.getVertexMatrixh())
       # print matrixCopy[0][1]
        arrowList1 = []#contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

        edgeList = copy.deepcopy(getattr(self.CG, "edgesh"))
        #if self.CS.orientation == 'h':
        for rect in self.cornerStitch_h.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "SOLID":
                color = "blue"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(),  0,rect.getHeight(), color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

        return arrowList1
        #elif self.CS.orientation == 'v':
    def findGraphEdges_v(self):
        #matrixCopy = np.copy(self.CG.getVertexMatrixv())
        #print matrixCopy[0][1]
        edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        #print "EDGE=",edgeList
        arrowList2 = []
        for rect in self.cornerStitch_v.stitchList:
            #rect.cell.printCell(True,True)
            if rect.cell.type=="SOLID":
                color = "blue"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

            elif rect.cell.type=="EMPTY":
                color = "red"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))


        #for foo in arrowList:
            #print foo
        return arrowList2

    """
                for stitch in self.cornerStitch_h.stitchList:
            print edgeList
            for edge in edgeList:
                if edge.getConstraint().getConstraintName() == "Empty":
                    if (self.CG.zeroDimensionListhx[edge.source] == stitch.cell.getX() and self.CG.zeroDimensionListhx[edge.dest] == stitch.cell.getX() + stitch.getWidth()):
                        color = "red"
                        arrowList1.append((stitch.cell.getX(), stitch.cell.getY(), stitch.getWidth(), 0, color))
                        edgeList.remove(edge)
                elif edge.getConstraint().getConstraintName() == "type1":
                    if (self.CG.zeroDimensionListvy[edge.source] == stitch.cell.getY() and self.CG.zeroDimensionListvy[edge.dest] == stitch.cell.getY() + stitch.getHeight()):
                        color = "blue"
                        arrowList1.append((stitch.cell.getX(), stitch.cell.getY(),  0,stitch.getHeight(), color))
                        edgeList.remove(edge)
        ###### original
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
        ######
        """


    """
    def setAxisLabels(self, plt):
        if self.CS.orientation == 'v':
            labels = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionList)))
            plt.yticks(self.CG.zeroDimensionList, list(labels))
        elif self.CS.orientation == 'h':
            labels = ('X' + str(i) for i in range(0, len(self.CG.zeroDimensionList)))
            plt.xticks(self.CG.zeroDimensionList, list(labels))
        
    def setAxisLabels(self, plt):
        #if self.CS.orientation == 'v':
        labels_y = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        #plt.tick_params(self.CG.zeroDimensionListv, list(labels_y), axis='y', which='both', labelleft='off',labelright='on')
        plt.yticks(self.CG.zeroDimensionListv, list(labels_y))

        #elif self.CS.orientation == 'h':
        labels_h = ('X' + str(i) for i in range(0, len(self.CG.zeroDimensionListh)))
        #plt.tick_params(self.CG.zeroDimensionListh, list(labels_h),axis='x', which='both', labelbottom='off', labeltop='on')
        plt.xticks(self.CG.zeroDimensionListh, list(labels))
    """

    def drawLayer1(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        #fig1 = matplotlib.pyplot.figure()
        #ax1 = fig1.add_subplot(111, aspect='equal')
        fig1,ax1=plt.subplots()

        for cell in self.cornerStitch_h.stitchList:





            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''
            #print cell.cell.x, cell.cell.y
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
            if cell.getNorth() == self.cornerStitch_h.northBoundary:
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
            if cell.getEast() == self.cornerStitch_h.eastBoundary:
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
            if cell.getSouth() == self.cornerStitch_h.southBoundary:
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
            if cell.getWest() == self.cornerStitch_h.westBoundary:
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
        p = PatchCollection(self.drawZeroDimsVertices1())
        ax1.add_collection(p)

        #handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        #automatically handle orientation
        #self.setAxisLabels(plt)

        for arr in self.findGraphEdges_h():
            ax1.arrow(arr[0], arr[1], arr[2], arr[3], head_width = .30, head_length = .3,  color =arr[4] )#

        #plt.tick_params(axis="x2", labelcolor="b",labeltop=True)
        #plt.xlim(0, self.cornerStitch_h.eastBoundary.cell.x)

        ####Setting axis labels(begin)

        ax1.set_ylim(0, self.cornerStitch_h.northBoundary.cell.y)
        limit = np.arange(0, self.cornerStitch_h.eastBoundary.cell.x+10,10)
        ax1.set_xticks(limit)
        ax2 = ax1.twiny()
        ax2.set_xticks(self.CG.zeroDimensionListh)
        #limit=range(0,self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = (str(i) for i in range(0, len(self.CG.zeroDimensionListh)))
        ax2.xaxis.set_ticklabels(list(labels_h))
        ax6 = ax1.twinx()
        ax6.set_yticks(self.CG.zeroDimensionListv)
        labels_h = (str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        ax6.yaxis.set_ticklabels(list(labels_h))

        ####Setting axis labels(end)


        if self.name1:
            fig1.savefig(self.name1,bbox_inches='tight')
            matplotlib.pyplot.close(fig1)
        else:
            fig1.show()
            pylab.pause(11000)  # figure out how to do this better
    def drawLayer2(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        #fig2 = matplotlib.pyplot.figure()
        fig2,ax4 = plt.subplots()
        for cell in self.cornerStitch_v.stitchList:



            #ax4 = fig2.add_subplot(111, aspect='equal')
            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''

            ax4.add_patch(
                matplotlib.patches.Rectangle(
                    (cell.cell.x, cell.cell.y),  # (x,y)
                    cell.getWidth(),  # width
                    cell.getHeight(),  # height
                    hatch = pattern,
                    fill=False
                )
            )
            #NORTH pointer
            if cell.getNorth() == self.cornerStitch_v.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.5 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getNorth().cell.y + (.5 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx =  0
                dy = .75

            ax4.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight()- .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #EAST pointer
            if cell.getEast() == self.cornerStitch_v.eastBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getEast().cell.x + (.5 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getEast().cell.y + (.5 * cell.getEast().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx = .75
                dy = 0
            ax4.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight()- .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #SOUTH pointer
            if cell.getSouth() == self.cornerStitch_v.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.5 * cell.getSouth().getWidth()) - (cell.cell.x + .5)
                dy = cell.getSouth().cell.y + (.5 * cell.getSouth().getHeight()) - (cell.cell.y + .5)
            else:
                dx =  0
                dy = -.5
            ax4.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
            #WEST pointer
            if cell.getWest() == self.cornerStitch_v.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.5 * cell.getWest().getWidth()) - (cell.cell.x + .5)
                dy = cell.getWest().cell.y + (.5 * cell.getWest().getHeight()) - (cell.cell.y + .5)
            else:
                dx =  -.5
                dy = 0
            ax4.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width = .25,
                      head_length = .25,
                      fc = 'k',
                      ec = 'k'
                    )
        p = PatchCollection(self.drawZeroDimsVertices2())
        ax4.add_collection(p)

        #handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        #automatically handle orientation
        #self.setAxisLabels(plt)

        for arr in self.findGraphEdges_v():
            ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width = .30, head_length = .3,  color =arr[4] )#


        ####Setting axis labels(begin)
        ax4.set_xlim(0, self.cornerStitch_v.eastBoundary.cell.x)
        limit = np.arange(0, self.cornerStitch_v.northBoundary.cell.y + 10, 10)
        ax4.set_yticks(limit)
        ax3 = ax4.twinx()
        ax3.set_yticks(self.CG.zeroDimensionListv)
        labels_h = (str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        ax3.yaxis.set_ticklabels(list(labels_h))
        ax5 = ax4.twiny()
        ax5.set_xticks(self.CG.zeroDimensionListh)
        #limit = range(0, self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = (str(i) for i in range(0, len(self.CG.zeroDimensionListh)))
        ax5.xaxis.set_ticklabels(list(labels_h))

        ####Setting axis labels(end)

        '''
        plt.xlim(0, self.cornerStitch_v.eastBoundary.cell.x)
        plt.ylim(0, self.cornerStitch_v.northBoundary.cell.y)
        labels_y = ( str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        #labels_y = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        # plt.tick_params(self.CG.zeroDimensionListv, list(labels_y), axis='y', which='both', labelleft='off',labelright = 'on')
        plt.yticks(self.CG.zeroDimensionListv, list(labels_y))
        ax2.yaxis.tick_right()
        #ax2.tick_params(labeltop=True, labelright=True)
        '''
        if self.name2:
            fig2.savefig(self.name2,bbox_inches='tight')
            matplotlib.pyplot.close(fig2)
        else:
            fig2.show()
            pylab.pause(11000)  # figure out how to do this better

    def drawRectangle(self,list=[],*args):
        fig = plt.figure()
        ax3 = fig.add_subplot(111, aspect='equal')
        for p in list:
            ax3.add_patch(p)
        plt.xlim(0,60)
        plt.ylim(0,60)
        fig.savefig(self.name1+'-1.png',bbox_inches='tight')
