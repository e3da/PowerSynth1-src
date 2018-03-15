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

    def __init__(self, cornerStitch_h, cornerStitch_v, CG, name1, name2):
        self.cornerStitch_h = cornerStitch_h
        self.cornerStitch_v = cornerStitch_v
        self.CG = CG
        self.name1 = name1
        self.name2 = name2
        self.Newcornerstitch_h = cornerStitch_h
        self.Newcornerstitch_v = cornerStitch_v
        self.Newcornerstitch_H = []  ##### Optimization
        self.Newcornerstitch_V = []  #### Optimization

        self.Special_stitchlist_h = []
        self.Special_stitchlist_v = []
        self.Special_stitchlist = []
        self.Special_id = []
        self.Special_id_v = []
        self.Special_id_h = []

    def drawZeroDimsVertices1(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        # if self.CS.orientation == 'v':
        # elif self.CS.orientation == 'h':
        for point in self.CG.zeroDimensionListh:
            # print self.CG.zeroDimensionListh.index(point)
            wedgeList.append(Wedge((point, 0), .5, 0, 360, width=1))

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

    # figure this out later

    ###final
    def findGraphEdges_h(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixh())
        # print matrixCopy[0][1]
        arrowList1 = []  # contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

        edgeList = copy.deepcopy(getattr(self.CG, "edgesh"))
        # if self.CS.orientation == 'h':
        for rect in self.cornerStitch_h.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "Type_1":
                color = "blue"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

        return arrowList1
        # elif self.CS.orientation == 'v':

    def findGraphEdges_v(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList
        arrowList2 = []
        for rect in self.cornerStitch_v.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "SOLID":
                color = "blue"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))


                # for foo in arrowList:
                # print foo
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

    def drawLayer1(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig1 = matplotlib.pyplot.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal')
        fig1, ax1 = plt.subplots()

        for cell in self.cornerStitch_h.stitchList:

            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''

            ax1.add_patch(
                matplotlib.patches.Rectangle(
                    (cell.cell.x, cell.cell.y),  # (x,y)
                    cell.getWidth(),  # width
                    cell.getHeight(),  # height
                    hatch=pattern,
                    fill=False
                )
            )

            # NORTH pointer
            if cell.getNorth() == self.cornerStitch_h.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.5 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getNorth().cell.y + (.5 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx = 0
                dy = .75

            ax1.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight() - .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # EAST pointer
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
                      (cell.cell.y + cell.getHeight() - .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # SOUTH pointer
            if cell.getSouth() == self.cornerStitch_h.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.5 * cell.getSouth().getWidth()) - (cell.cell.x + .5)
                dy = cell.getSouth().cell.y + (.5 * cell.getSouth().getHeight()) - (cell.cell.y + .5)
            else:
                dx = 0
                dy = -.5
            ax1.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # WEST pointer
            if cell.getWest() == self.cornerStitch_h.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.5 * cell.getWest().getWidth()) - (cell.cell.x + .5)
                dy = cell.getWest().cell.y + (.5 * cell.getWest().getHeight()) - (cell.cell.y + .5)
            else:
                dx = -.5
                dy = 0
            ax1.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
        p = PatchCollection(self.drawZeroDimsVertices1())
        ax1.add_collection(p)

        # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        # automatically handle orientation
        # self.setAxisLabels(plt)

        for arr in self.findGraphEdges_h():
            ax1.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.30, head_length=.3, color=arr[4])  #

        # plt.tick_params(axis="x2", labelcolor="b",labeltop=True)
        # plt.xlim(0, self.cornerStitch_h.eastBoundary.cell.x)

        ####Setting axis labels(begin)
        '''
        font = {'family': 'normal',
                
                'size':15}

        matplotlib.rc('font', **font)
        '''
        ax1.set_ylim(0, self.cornerStitch_h.northBoundary.cell.y)
        limit = np.arange(0, self.cornerStitch_h.eastBoundary.cell.x + 10, 10)
        ax1.set_xticks(limit)
        ax2 = ax1.twiny()
        ax2.set_xticks(self.CG.zeroDimensionListh)
        # limit=range(0,self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = ('X' + str(i) for i in range(0, len(self.CG.zeroDimensionListh)))
        ax2.xaxis.set_ticklabels(list(labels_h))
        ax6 = ax1.twinx()
        ax6.set_yticks(self.CG.zeroDimensionListv)
        labels_h = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        ax6.yaxis.set_ticklabels(list(labels_h))
        for item in (ax2.get_xticklabels() + ax2.get_yticklabels()+ax6.get_xticklabels() + ax6.get_yticklabels()):
            item.set_fontsize(15)

        ####Setting axis labels(end)


        if self.name1:
            fig1.savefig(self.name1 + 'h.png', bbox_inches='tight')
            matplotlib.pyplot.close(fig1)
        else:
            fig1.show()
            pylab.pause(11000)  # figure out how to do this better


            # elif self.CS.orientation == 'v':

    def findGraphEdges_v(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList
        arrowList2 = []
        for rect in self.cornerStitch_v.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "Type_1":
                color = "blue"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))


                # for foo in arrowList:
                # print foo
        return arrowList2

    def drawLayer2(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig2 = matplotlib.pyplot.figure()
        fig2, ax4 = plt.subplots()
        for cell in self.cornerStitch_v.stitchList:

            # ax4 = fig2.add_subplot(111, aspect='equal')
            if not cell.cell.type == "EMPTY":
                pattern = '\\'
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
            # NORTH pointer
            if cell.getNorth() == self.cornerStitch_v.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.5 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .5
                dy = cell.getNorth().cell.y + (.5 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .5
            else:
                dx = 0
                dy = .75

            ax4.arrow((cell.cell.x + cell.getWidth() - .5),
                      (cell.cell.y + cell.getHeight() - .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # EAST pointer
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
                      (cell.cell.y + cell.getHeight() - .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # SOUTH pointer
            if cell.getSouth() == self.cornerStitch_v.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.5 * cell.getSouth().getWidth()) - (cell.cell.x + .5)
                dy = cell.getSouth().cell.y + (.5 * cell.getSouth().getHeight()) - (cell.cell.y + .5)
            else:
                dx = 0
                dy = -.5
            ax4.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
            # WEST pointer
            if cell.getWest() == self.cornerStitch_v.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.5 * cell.getWest().getWidth()) - (cell.cell.x + .5)
                dy = cell.getWest().cell.y + (.5 * cell.getWest().getHeight()) - (cell.cell.y + .5)
            else:
                dx = -.5
                dy = 0
            ax4.arrow((cell.cell.x + .5),
                      (cell.cell.y + .5),
                      dx,
                      dy,
                      head_width=.25,
                      head_length=.25,
                      fc='k',
                      ec='k'
                      )
        p = PatchCollection(self.drawZeroDimsVertices2())
        ax4.add_collection(p)

        # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        # automatically handle orientation
        # self.setAxisLabels(plt)

        for arr in self.findGraphEdges_v():
            ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.30, head_length=.3, color=arr[4])  #

        ####Setting axis labels(begin)
        '''
        font = {'family': 'normal',
                'weight': 'bold',
                'size': 20}

        matplotlib.rc('font', **font)
        '''

        ax4.set_xlim(0, self.cornerStitch_v.eastBoundary.cell.x)
        limit = np.arange(0, self.cornerStitch_v.northBoundary.cell.y + 10, 10)
        ax4.set_yticks(limit)
        ax3 = ax4.twinx()
        ax3.set_yticks(self.CG.zeroDimensionListv)
        labels_h = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        ax3.yaxis.set_ticklabels(list(labels_h))
        ax5 = ax4.twiny()
        ax5.set_xticks(self.CG.zeroDimensionListh)
        # limit = range(0, self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = ('X' + str(i) for i in range(0, len(self.CG.zeroDimensionListh)))
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
            fig2.savefig(self.name2 + 'v.png', bbox_inches='tight')
            matplotlib.pyplot.close(fig2)
        else:
            fig2.show()
            pylab.pause(11000)  # figure out how to do this better

    def ID_Conversion(
            self):  ############### Determining cell id for vertical cornerstitch from horizontal cornerstitch stitchlist
        '''
        In self.CG.special_cell_id_v id's are from horizontal cornerstitch. And in self.CG.special_cell_id_h id's are from vertical cornerstitch. So to update we need to determine
        special_cell_id_v in vertical one and special_cell_id_h in horizontal one.
        '''
        # print self.CG.special_cell_id_v

        SPECIAL_ID_H = []  #### having horizontal cell info in horizontal cornerstitch
        for cell in self.Newcornerstitch_h.stitchList:
            if cell.cell.id in self.CG.special_cell_id_v:
                SPECIAL_ID_H.append({cell.cell.id: [cell.cell.x,
                                                    cell.cell.y]})  ### locating x,y position of the cell having corresponding id in horizontal stitchlist

        SPECIAL_ID_V = []  #### having vertical cell info in vertical cornerstitch
        for cell in self.Newcornerstitch_v.stitchList:
            if cell.cell.id in self.CG.special_cell_id_h:
                SPECIAL_ID_V.append({cell.cell.id: [cell.cell.x,
                                                    cell.cell.y]})  ### locating x,y position of the cell having corresponding id in vertical stitchlist
        # print "1",SPECIAL_ID_V
        # print SPECIAL_ID_H

        X_Y = []  ### stores x,y value of the cells from horizontal sitchlist
        for i in SPECIAL_ID_H:
            X_Y.append(i.values()[0])
        # print X_Y
        K = []  ## finding same cells in vertical stitchlist
        for i in X_Y:
            for cell in self.Newcornerstitch_v.stitchList:
                if i == [cell.cell.x, cell.cell.y]:
                    K.append({cell.cell.id: [cell.cell.x, cell.cell.y]})

        # cell.cell.id=i.keys()
        # print K
        H1 = []
        for i in SPECIAL_ID_H:
            H1.append(i.keys()[0])
        # print H1
        H2 = []
        for i in K:
            H2.append(i.keys()[0])

        ID_SWAP_HtoV = dict(zip(H1, H2))  #### saving {ID:[x,y]} in vertical stitchlist
        # print ID_SWAP_HtoV

        # Keys_v=[]
        # values_v = []
        special_location_ynew_all = []
        for i in range(len(self.CG.special_location_y)):
            # print "i=",self.CG.special_location_y[i]
            # special_location_ynew={}

            keys = []
            for coord in self.CG.special_location_y[i]:
                # print coord
                keys.append(coord.keys()[0])
            # Keys_v.append(keys)
            values = []
            for coord in self.CG.special_location_y[i]:
                values.append(coord.values()[0])
            # values_v.append(values)

            special_location_ynew = dict(zip(keys, values))
            special_location_ynew_all.append(special_location_ynew)
        # print special_location_ynew_all
        special_location_ynew2_all = []
        for i in range(len(special_location_ynew_all)):
            special_location_ynew2 = dict(
                (ID_SWAP_HtoV[key], value) for (key, value) in special_location_ynew_all[i].items())
            special_location_ynew2_all.append(special_location_ynew2)
        # print special_location_ynew2_all


        special_location_ynew1_all = []
        for i in range(len(special_location_ynew2_all)):
            special_location_ynew1 = []
            for k, v in special_location_ynew2_all[i].items():
                # print k, v
                special_location_ynew1.append({k: v})
            special_location_ynew1_all.append(special_location_ynew1)
        # print special_location_ynew1_all



        ############### Determining cell id for horizontal cornerstitch from vertical cornerstitch stitchlist
        SPECIAL_ID_V1 = []
        for cell in self.Newcornerstitch_v.stitchList:
            if cell.cell.id in self.CG.special_cell_id_h:
                SPECIAL_ID_V1.append({cell.cell.id: [cell.cell.x, cell.cell.y]})
        SPECIAL_ID_H1 = []
        for cell in self.Newcornerstitch_h.stitchList:
            if cell.cell.id in self.CG.special_cell_id_v:
                SPECIAL_ID_H1.append({cell.cell.id: [cell.cell.x, cell.cell.y]})
        # print "ID", SPECIAL_ID_H1
        # ID_SWAP_HtoV=[]
        X_Y_v = []
        for i in SPECIAL_ID_V1:
            X_Y_v.append(i.values()[0])
        # print X_Y_v
        # for k,v in i:
        K_v = []
        for i in X_Y_v:
            for cell in self.Newcornerstitch_h.stitchList:
                if i == [cell.cell.x, cell.cell.y]:
                    K_v.append({cell.cell.id: [cell.cell.x, cell.cell.y]})

                    # cell.cell.id=i.keys()
        # print K_v
        V1 = []
        for i in SPECIAL_ID_V1:
            V1.append(i.keys()[0])
        # print V1
        V2 = []
        for i in K_v:
            V2.append(i.keys()[0])

        ID_SWAP_VtoH = dict(zip(V1, V2))
        # print ID_SWAP_VtoH


        special_location_xnew_all = []
        for i in range(len(self.CG.special_location_x)):
            keys_v = []
            for coord in self.CG.special_location_x[i]:
                # print i
                keys_v.append(coord.keys()[0])
            # print keys_v
            values_v = []
            for coord in self.CG.special_location_x[i]:
                values_v.append(coord.values()[0])

            special_location_xnew = dict(zip(keys_v, values_v))
            special_location_xnew_all.append(special_location_xnew)
        # print "x_newall",special_location_xnew_all

        special_location_xnew2_all = []
        for i in range(len(special_location_xnew_all)):
            special_location_xnew2 = dict(
                (ID_SWAP_VtoH[key], value) for (key, value) in special_location_xnew_all[i].items())
            special_location_xnew2_all.append(special_location_xnew2)
        # print special_location_xnew2_all

        special_location_xnew1_all = []
        for i in range(len(special_location_xnew2_all)):
            special_location_xnew1 = []
            for k, v in special_location_xnew2_all[i].items():
                # print k, v
                special_location_xnew1.append({k: v})
            special_location_xnew1_all.append(special_location_xnew1)
        # print "SP", special_location_ynew1_all[0]
        # print self.CG.special_cell_id_h
        # print self.Special_id_v
        if len(special_location_ynew1_all) != 0:
            for element in special_location_ynew1_all[0]:
                # print element
                self.Special_id_v.append(element.keys()[0])
        if len(special_location_xnew1_all) != 0:
            for element in special_location_xnew1_all[0]:
                self.Special_id_h.append(element.keys()[0])

        # print self.Special_id_h

        # print self.CG.special_cell_id_h
        # print self.Special_id_v
        # print "all"
        # print special_location_xnew1_all
        # print special_location_ynew1_all

        self.Special_stitchlist_h = copy.deepcopy(special_location_xnew1_all)
        self.Special_stitchlist_v = copy.deepcopy(special_location_ynew1_all)
        # print len(self.Special_stitchlist_h),len(self.Special_stitchlist_v)
        if len(self.Special_stitchlist_h) == len(self.Special_stitchlist_v):

            for i in range(len(self.Special_stitchlist_h)):
                # print i
                Special_stitchlist = []
                for element in special_location_xnew1_all[i]:
                    # print element
                    for el in special_location_ynew1_all[i]:
                        for k1, v1 in element.items():
                            # print k1,v1
                            for k2, v2 in el.items():
                                if k1 == k2:
                                    if k1 not in self.Special_id:
                                        self.Special_id.append(k1)
                                    # print"1", {k1: [v1[0], v2[0], v1[2], v2[2]]}
                                    Special_stitchlist.append({k1: [v1[0], v2[0], v1[2], v2[2]]})
                self.Special_stitchlist.append(Special_stitchlist)
                # print self.Special_stitchlist

    def update_stitchList(self):

        # self.Newcornerstitch_h=copy.deepcopy(self.cornerStitch_h)
        # self.Newcornerstitch_v= copy.deepcopy(self.cornerStitch_v)
        # print self.CG.newXlocation
        # print self.CG.newYlocation
        X_H = []
        Y_H = []
        for cell in self.Newcornerstitch_h.stitchList:
            X_H.append(cell.cell.x)
            X_H.append(self.Newcornerstitch_h.eastBoundary.cell.x)
            Y_H.append(cell.cell.y)
            Y_H.append(self.Newcornerstitch_h.northBoundary.cell.y)

            # print cell.cell.x, cell.cell.y
        # print"H="
        X_H = list(sorted(set(X_H)))
        Y_H = list(sorted(set(Y_H)))
        # print X_H, Y_H
        '''
        #######Without optimization
        valuesX_H=self.CG.newXlocation
        valuesY_H = self.CG.newYlocation
        dictionary_X_H = dict(zip(X_H, valuesX_H))
        dictionary_Y_H = dict(zip(Y_H, valuesY_H))
        print"Horizontal New Cornerstitch", dictionary_X_H,dictionary_Y_H
        #print X_H,Y_H
        for cell in self.Newcornerstitch_h.stitchList:
            #print cell.cell.x,cell.cell.y
            cell.cell.x=dictionary_X_H[cell.cell.x]
            cell.cell.y = dictionary_Y_H[cell.cell.y]
            #print cell.cell.x,cell.cell.y
        for cell in self.Newcornerstitch_h.boundaries:
            #print cell.cell.x, cell.cell.y
            if cell.cell.x in dictionary_X_H:
                cell.cell.x = dictionary_X_H[cell.cell.x]
            if cell.cell.y in dictionary_Y_H:
                cell.cell.y = dictionary_Y_H[cell.cell.y]
            #print cell.cell.x,cell.cell.y
        ##########
        '''
        ########TESTING WITHOPT
        valuesX_H = []
        for i in range(len(self.CG.NEWXLOCATION)):
            valuesX_H.append(self.CG.NEWXLOCATION[i])
        # print valuesX_H
        valuesY_H = []
        for i in range(len(self.CG.NEWYLOCATION)):
            valuesY_H.append(self.CG.NEWYLOCATION[i])
        # valuesY_H = self.CG.newYlocation
        dictionary_X_H = []
        for i in range(len(valuesX_H)):
            dictionary_X_H.append(dict(zip(X_H, valuesX_H[i])))
        dictionary_Y_H = []
        for i in range(len(valuesY_H)):
            dictionary_Y_H.append(dict(zip(Y_H, valuesY_H[i])))
        for i in range(len(dictionary_X_H)):
            self.Newcornerstitch_H.append(copy.deepcopy(self.Newcornerstitch_h))
            # print Newcornerstitch_H[i].stitchList
        for i in range(len(self.Newcornerstitch_H)):
            # print"Horizontal New Cornerstitch", dictionary_X_H[i], dictionary_Y_H
            # print X_H,Y_H
            # print self.Newcornerstitch_H[i]
            # for cell in self.Newcornerstitch_h.stitchList:
            for cell in self.Newcornerstitch_H[i].stitchList:
                # print cell.cell.y
                cell.cell.x = dictionary_X_H[i][cell.cell.x]
                cell.cell.y = dictionary_Y_H[i][cell.cell.y]
                # print cell.cell.x,cell.cell.y
            for cell in self.Newcornerstitch_H[i].boundaries:
                # print cell.cell.x, cell.cell.y
                if cell.cell.x in dictionary_X_H[i]:
                    cell.cell.x = dictionary_X_H[i][cell.cell.x]
                if cell.cell.y in dictionary_Y_H[i]:
                    cell.cell.y = dictionary_Y_H[i][cell.cell.y]
        # print dictionary_X_H
        ############### Added for correction
        X_V = []
        Y_V = []
        for cell in self.Newcornerstitch_v.stitchList:
            X_V.append(cell.cell.x)
            X_V.append(self.Newcornerstitch_v.eastBoundary.cell.x)
            Y_V.append(cell.cell.y)
            Y_V.append(self.Newcornerstitch_v.northBoundary.cell.y)

            # print cell.cell.x, cell.cell.y
        # print"v="
        X_V = list(sorted(set(X_V)))
        Y_V = list(sorted(set(Y_V)))
        valuesX_V = []
        for i in range(len(self.CG.NEWXLOCATION)):
            valuesX_V.append(self.CG.NEWXLOCATION[i])
        # print valuesX_V
        valuesY_V = []
        for i in range(len(self.CG.NEWYLOCATION)):
            valuesY_V.append(self.CG.NEWYLOCATION[i])
        # valuesY_H = self.CG.newYlocation

        dictionary_X_V = []
        for i in range(len(valuesX_V)):
            dictionary_X_V.append(dict(zip(X_V, valuesX_V[i])))
        dictionary_Y_V = []
        for i in range(len(valuesY_V)):
            dictionary_Y_V.append(dict(zip(Y_V, valuesY_V[i])))
        # print"len=",len(dictionary_X_V),len( dictionary_Y_V)

        # Newcornerstitch_H=[]

        #### vertical
        for i in range(len(dictionary_Y_V)):
            self.Newcornerstitch_V.append(copy.deepcopy(self.Newcornerstitch_v))
            # print Newcornerstitch_H[i].stitchList
        for i in range(len(self.Newcornerstitch_V)):
            # print"Horizontal New Cornerstitch", dictionary_X_H[i], dictionary_Y_H
            # print X_H,Y_H
            # print self.Newcornerstitch_H[i]
            # for cell in self.Newcornerstitch_h.stitchList:
            for cell in self.Newcornerstitch_V[i].stitchList:
                # print cell.cell.y
                cell.cell.x = dictionary_X_V[i][cell.cell.x]
                cell.cell.y = dictionary_Y_V[i][cell.cell.y]
                # print cell.cell.x, cell.cell.y
            for cell in self.Newcornerstitch_V[i].boundaries:
                # print cell.cell.x, cell.cell.y
                if cell.cell.x in dictionary_X_V[i]:
                    cell.cell.x = dictionary_X_V[i][cell.cell.x]
                if cell.cell.y in dictionary_Y_V[i]:
                    cell.cell.y = dictionary_Y_V[i][cell.cell.y]
        # print Newcornerstitch_H[i].stitchList

        #############

        """(commented out for testing but it's ok without optimization part)
        X_V = []
        Y_V = []
        for cell in self.Newcornerstitch_v.stitchList:

            X_V.append(cell.cell.x)
            X_V.append(self.Newcornerstitch_v.eastBoundary.cell.x)
            Y_V.append(cell.cell.y)
            Y_V.append(self.Newcornerstitch_v.northBoundary.cell.y)

            #print cell.cell.x, cell.cell.y
        #print"v="
        X_V = list(sorted(set(X_V)))
        Y_V = list(sorted(set(Y_V)))
        valuesX_V = self.CG.newXlocation
        valuesY_V = self.CG.newYlocation
        dictionary_X_V = dict(zip(X_V, valuesX_V))
        dictionary_Y_V = dict(zip(Y_V, valuesY_V))
        print "Vertical New Cornerstitch",dictionary_X_V,dictionary_Y_V
        for cell in self.Newcornerstitch_v.stitchList:
            #print cell.cell.x,cell.cell.y
            cell.cell.x=dictionary_X_V[cell.cell.x]
            cell.cell.y = dictionary_Y_V[cell.cell.y]
            #print cell.cell.x,cell.cell.y
        #print "BOUND=",self.Newcornerstitch_v.northBoundary.cell.x,self.Newcornerstitch_v.northBoundary.cell.y
        for cell in self.Newcornerstitch_v.boundaries:
            #print cell.cell.x, cell.cell.y
            if cell.cell.x in dictionary_X_V:
                cell.cell.x = dictionary_X_V[cell.cell.x]
            if cell.cell.y in dictionary_Y_V:
                cell.cell.y = dictionary_Y_V[cell.cell.y]
            #print cell.cell.x,cell.cell.y
        """

    ##############################################################(Optimization testing)
    '''
    def findGraphEdges_hnew(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixh())
        # print matrixCopy[0][1]
        arrowList1 = []  # contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

        edgeList = copy.deepcopy(getattr(self.CG, "edgesh"))
        # if self.CS.orientation == 'h':
        for rect in  self. Newcornerstitch_h.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "SOLID":
                color = "blue"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

        return arrowList1
    '''
    '''(!!!!!!!!!!!!!!!!!-start)
    def drawLayer_hnew(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """
        for i in range(len(self.Newcornerstitch_H)):
            arrowList = []  # contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

            #edgeList = copy.deepcopy(getattr(self.CG, "edgesh"))
            # if self.CS.orientation == 'h':
            for rect in self.Newcornerstitch_H[i].stitchList:
                # rect.cell.printCell(True,True)
                if rect.cell.type == "SOLID":
                    color = "blue"
                    arrowList.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))

                elif rect.cell.type == "EMPTY":
                    color = "red"
                    arrowList.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))
            # fig1 = matplotlib.pyplot.figure()
            # ax1 = fig1.add_subplot(111, aspect='equal')
            fig1, ax1 = plt.subplots()

            for cell in  self.Newcornerstitch_H[i].stitchList:
                #print"latest=", cell.cell.x,cell.cell.y

                if not cell.cell.type == "EMPTY":
                    pattern = '\\'
                else:
                    pattern = ''

                ax1.add_patch(
                    matplotlib.patches.Rectangle(
                        (cell.cell.x, cell.cell.y),  # (x,y)
                        cell.getWidth(),  # width
                        cell.getHeight(),  # height
                        hatch=pattern,
                        fill=False
                    )
                )

                # NORTH pointer
                if cell.getNorth() ==  self. Newcornerstitch_H[i].northBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getNorth().cell.x + (.08 * cell.getNorth().getWidth()) - (
                    cell.cell.x + cell.getWidth()) + .08
                    dy = cell.getNorth().cell.y + (.08 * cell.getNorth().getHeight()) - (
                    cell.cell.y + cell.getHeight()) + .08
                else:
                    dx = 0
                    dy = .1

                ax1.arrow((cell.cell.x + cell.getWidth() - .08),
                          (cell.cell.y + cell.getHeight() - .08),
                          dx,
                          dy,
                          head_width=.04,
                          head_length=.04,
                          fc='k',
                          ec='k'
                          )
                # EAST pointer
                if cell.getEast() ==  self. Newcornerstitch_H[i].eastBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getEast().cell.x + (.08 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                    dy = cell.getEast().cell.y + (.08 * cell.getEast().getHeight()) - (
                    cell.cell.y + cell.getHeight()) + .08
                else:
                    dx = .1
                    dy = 0
                ax1.arrow((cell.cell.x + cell.getWidth() - .08),
                          (cell.cell.y + cell.getHeight() - .08),
                          dx,
                          dy,
                          head_width=.04,
                          head_length=.04,
                          fc='k',
                          ec='k'
                          )
                # SOUTH pointer
                if cell.getSouth() ==  self. Newcornerstitch_H[i].southBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getSouth().cell.x + (.08 * cell.getSouth().getWidth()) - (cell.cell.x + .08)
                    dy = cell.getSouth().cell.y + (.08 * cell.getSouth().getHeight()) - (cell.cell.y + .08)
                else:
                    dx = 0
                    dy = -.1
                ax1.arrow((cell.cell.x + .08),
                          (cell.cell.y + .08),
                          dx,
                          dy,
                          head_width=.04,
                          head_length=.04,
                          fc='k',
                          ec='k'
                          )
                # WEST pointer
                if cell.getWest() ==  self. Newcornerstitch_H[i].westBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getWest().cell.x + (.08 * cell.getWest().getWidth()) - (cell.cell.x + .08)
                    dy = cell.getWest().cell.y + (.08 * cell.getWest().getHeight()) - (cell.cell.y + .08)
                else:
                    dx = -.1
                    dy = 0
                ax1.arrow((cell.cell.x + .08),
                          (cell.cell.y + .08),
                          dx,
                          dy,
                          head_width=.04,
                          head_length=.04,
                          fc='k',
                          ec='k'
                          )
            #p = PatchCollection(self.drawZeroDimsVertices_h())
            #ax1.add_collection(p)

            # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
            # automatically handle orientation
            # self.setAxisLabels(plt)

            for arr in arrowList:
                ax1.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.09, head_length=.09, color=arr[4])  #

            # plt.tick_params(axis="x2", labelcolor="b",labeltop=True)
            # plt.xlim(0, self.cornerStitch_h.eastBoundary.cell.x)

            ####Setting axis labels(begin)

            ax1.set_ylim(0,  self.Newcornerstitch_H[i].northBoundary.cell.y)
            ax1.set_xlim(0, self.Newcornerstitch_H[i].eastBoundary.cell.x)
            #ax1.set_ylim(0, 60)
            #ax1.set_xlim(0, 60)
            # ax1.set_xlim(0, self.Newcornerstitch_h.eastBoundary.cell.x)
            #limit = np.arange(0,  self. Newcornerstitch_h.eastBoundary.cell.x + 1, 1)
            #ax1.set_xticks(limit)
            ax2 = ax1.twiny()
            ax2.set_xticks(self.CG.NEWXLOCATION[i])
            # limit=range(0,self.cornerStitch_h.eastBoundary.cell.x)
            labels_h = ('X'+str(i) for i in range(0, len(self.CG.NEWXLOCATION[i])))
            ax2.xaxis.set_ticklabels(list(labels_h))
            ax6 = ax1.twinx()
            ax6.set_yticks(self.CG.NEWYLOCATION[i])
            labels_h = ('Y'+str(i) for i in range(0, len(self.CG.NEWYLOCATION[i])))
            ax6.yaxis.set_ticklabels(list(labels_h))

            ####Setting axis labels(end)


            if self.name1:
                fig1.savefig(self.name1+'-'+str(i) + 'newh.png', bbox_inches='tight')
                matplotlib.pyplot.close(fig1)
            else:
                fig1.show()
                pylab.pause(11000)  # figure out how to do this better
    #################################################################################################
    def drawZeroDimsVertices_h(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        # if self.CS.orientation == 'v':
        # elif self.CS.orientation == 'h':
        for point in self.CG.newXlocation:
            # print self.CG.zeroDimensionListh.index(point)
            wedgeList.append(Wedge((point, 0), 0.01, 0, 360, width=0.4))

        return wedgeList

    def drawZeroDimsVertices_v(self):
        """
        derive and return a list of wedges which will represent vertices on the CS drawing
        """
        wedgeList = []
        # if self.CS.orientation == 'v':
        for point in self.CG.newYlocation:
            wedgeList.append(Wedge((0, point), 0.01, 0, 360, width=0.4))

        return wedgeList

        """ #########commented out for testing

    def findGraphEdges_hnew(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixh())
        # print matrixCopy[0][1]
        arrowList1 = []  # contains the information for arrows to be drawn in matplotlib (x,y,dx,dy)

        edgeList = copy.deepcopy(getattr(self.CG, "edgesh"))
        # if self.CS.orientation == 'h':
        for rect in  self. Newcornerstitch_h.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "SOLID":
                color = "blue"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList1.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

        return arrowList1
    def drawLayer_hnew(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig1 = matplotlib.pyplot.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal')
        fig1, ax1 = plt.subplots()

        for cell in  self.Newcornerstitch_h.stitchList:
            #print"latest=", cell.cell.x,cell.cell.y

            if not cell.cell.type == "EMPTY":
                pattern = '\\'
            else:
                pattern = ''

            ax1.add_patch(
                matplotlib.patches.Rectangle(
                    (cell.cell.x, cell.cell.y),  # (x,y)
                    cell.getWidth(),  # width
                    cell.getHeight(),  # height
                    hatch=pattern,
                    fill=False
                )
            )

            # NORTH pointer
            if cell.getNorth() ==  self. Newcornerstitch_h.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.08 * cell.getNorth().getWidth()) - (
                cell.cell.x + cell.getWidth()) + .08
                dy = cell.getNorth().cell.y + (.08 * cell.getNorth().getHeight()) - (
                cell.cell.y + cell.getHeight()) + .08
            else:
                dx = 0
                dy = .1

            ax1.arrow((cell.cell.x + cell.getWidth() - .08),
                      (cell.cell.y + cell.getHeight() - .08),
                      dx,
                      dy,
                      head_width=.04,
                      head_length=.04,
                      fc='k',
                      ec='k'
                      )
            # EAST pointer
            if cell.getEast() ==  self. Newcornerstitch_h.eastBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getEast().cell.x + (.08 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                dy = cell.getEast().cell.y + (.08 * cell.getEast().getHeight()) - (
                cell.cell.y + cell.getHeight()) + .08
            else:
                dx = .1
                dy = 0
            ax1.arrow((cell.cell.x + cell.getWidth() - .08),
                      (cell.cell.y + cell.getHeight() - .08),
                      dx,
                      dy,
                      head_width=.04,
                      head_length=.04,
                      fc='k',
                      ec='k'
                      )
            # SOUTH pointer
            if cell.getSouth() ==  self. Newcornerstitch_h.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.08 * cell.getSouth().getWidth()) - (cell.cell.x + .08)
                dy = cell.getSouth().cell.y + (.08 * cell.getSouth().getHeight()) - (cell.cell.y + .08)
            else:
                dx = 0
                dy = -.1
            ax1.arrow((cell.cell.x + .08),
                      (cell.cell.y + .08),
                      dx,
                      dy,
                      head_width=.04,
                      head_length=.04,
                      fc='k',
                      ec='k'
                      )
            # WEST pointer
            if cell.getWest() ==  self. Newcornerstitch_h.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.08 * cell.getWest().getWidth()) - (cell.cell.x + .08)
                dy = cell.getWest().cell.y + (.08 * cell.getWest().getHeight()) - (cell.cell.y + .08)
            else:
                dx = -.1
                dy = 0
            ax1.arrow((cell.cell.x + .08),
                      (cell.cell.y + .08),
                      dx,
                      dy,
                      head_width=.04,
                      head_length=.04,
                      fc='k',
                      ec='k'
                      )
        #p = PatchCollection(self.drawZeroDimsVertices_h())
        #ax1.add_collection(p)

        # handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        # automatically handle orientation
        # self.setAxisLabels(plt)

        for arr in self.findGraphEdges_hnew():
            ax1.arrow(arr[0], arr[1], arr[2], arr[3], head_width=.09, head_length=.09, color=arr[4])  #

        # plt.tick_params(axis="x2", labelcolor="b",labeltop=True)
        # plt.xlim(0, self.cornerStitch_h.eastBoundary.cell.x)

        ####Setting axis labels(begin)

        ax1.set_ylim(0,  self. Newcornerstitch_h.northBoundary.cell.y)
        ax1.set_xlim(0, self.Newcornerstitch_h.eastBoundary.cell.x)
        #ax1.set_ylim(0, 60)
        #ax1.set_xlim(0, 60)
        # ax1.set_xlim(0, self.Newcornerstitch_h.eastBoundary.cell.x)
        #limit = np.arange(0,  self. Newcornerstitch_h.eastBoundary.cell.x + 1, 1)
        #ax1.set_xticks(limit)
        ax2 = ax1.twiny()
        ax2.set_xticks(self.CG.newXlocation)
        # limit=range(0,self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = ('X'+str(i) for i in range(0, len(self.CG.newXlocation)))
        ax2.xaxis.set_ticklabels(list(labels_h))
        ax6 = ax1.twinx()
        ax6.set_yticks(self.CG.newYlocation)
        labels_h = ('Y'+str(i) for i in range(0, len(self.CG.newYlocation)))
        ax6.yaxis.set_ticklabels(list(labels_h))

        ####Setting axis labels(end)


        if self.name1:
            fig1.savefig(self.name1 + 'newh.png', bbox_inches='tight')
            matplotlib.pyplot.close(fig1)
        else:
            fig1.show()
            pylab.pause(11000)  # figure out how to do this better

        """
       """ ###################     OK without optimization
    def findGraphEdges_vnew(self):
        # matrixCopy = np.copy(self.CG.getVertexMatrixv())
        # print matrixCopy[0][1]
        #edgeList = copy.deepcopy(getattr(self.CG, "edgesv"))
        # print "EDGE=",edgeList
        arrowList2 = []
        for rect in self. Newcornerstitch_v.stitchList:
            # rect.cell.printCell(True,True)
            if rect.cell.type == "SOLID":
                color = "blue"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

            elif rect.cell.type == "EMPTY":
                color = "red"
                arrowList2.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))


                # for foo in arrowList:
                # print foo
        return arrowList2




    def drawLayer_vnew(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        #fig2 = matplotlib.pyplot.figure()
        fig2,ax4 = plt.subplots()
        for cell in self. Newcornerstitch_v.stitchList:


            #print "Latestv=",cell.cell.x,cell.cell.y
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
            if cell.getNorth() == self. Newcornerstitch_v.northBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getNorth().cell.x + (.08 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                dy = cell.getNorth().cell.y + (.08 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .08
            else:
                dx =  0
                dy = .1

            ax4.arrow((cell.cell.x + cell.getWidth() - .08),
                      (cell.cell.y + cell.getHeight()- .08),
                      dx,
                      dy,
                      head_width = .04,
                      head_length = .04,
                      fc = 'k',
                      ec = 'k'
                    )
            #EAST pointer
            if cell.getEast() == self. Newcornerstitch_v.eastBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getEast().cell.x + (.08 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                dy = cell.getEast().cell.y + (.08 * cell.getEast().getHeight()) - (cell.cell.y + cell.getHeight()) + .08
            else:
                dx = .1
                dy = 0
            ax4.arrow((cell.cell.x + cell.getWidth() - .08),
                      (cell.cell.y + cell.getHeight()- .08),
                      dx,
                      dy,
                      head_width = .04,
                      head_length = .04,
                      fc = 'k',
                      ec = 'k'
                    )
            #SOUTH pointer
            if cell.getSouth() == self. Newcornerstitch_v.southBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getSouth().cell.x + (.08 * cell.getSouth().getWidth()) - (cell.cell.x + .08)
                dy = cell.getSouth().cell.y + (.08 * cell.getSouth().getHeight()) - (cell.cell.y + .08)
            else:
                dx =  0
                dy = -.1
            ax4.arrow((cell.cell.x + .08),
                      (cell.cell.y + .08),
                      dx,
                      dy,
                      head_width = .04,
                      head_length = .04,
                      fc = 'k',
                      ec = 'k'
                    )
            #WEST pointer
            if cell.getWest() == self. Newcornerstitch_v.westBoundary:
                dx = 0
                dy = 0
            elif truePointer:
                dx = cell.getWest().cell.x + (.08 * cell.getWest().getWidth()) - (cell.cell.x + .08)
                dy = cell.getWest().cell.y + (.08 * cell.getWest().getHeight()) - (cell.cell.y + .08)
            else:
                dx =  -.1
                dy = 0
            ax4.arrow((cell.cell.x + .08),
                      (cell.cell.y + .08),
                      dx,
                      dy,
                      head_width = .04,
                      head_length = .04,
                      fc = 'k',
                      ec = 'k'
                    )
        #p = PatchCollection(self.drawZeroDimsVertices_v())
        #ax4.add_collection(p)

        #handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
        #automatically handle orientation
        #self.setAxisLabels(plt)

        for arr in self.findGraphEdges_vnew():
            ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width = .09, head_length = .09,  color =arr[4] )#


        ####Setting axis labels(begin)
        #ax4.set_ylim(0, 60)
        #ax4.set_xlim(0, 60)
        ax4.set_xlim(0, self. Newcornerstitch_v.eastBoundary.cell.x)
        ax4.set_ylim(0, self.Newcornerstitch_v.northBoundary.cell.y)
        #limit = np.arange(0, self. Newcornerstitch_v.northBoundary.cell.y + 1, 1)
        #ax4.set_yticks(limit)
        ax3 = ax4.twinx()
        ax3.set_yticks(self.CG.newYlocation)
        labels_h = ('Y'+str(i) for i in range(0, len(self.CG.newYlocation)))
        ax3.yaxis.set_ticklabels(list(labels_h))
        ax5 = ax4.twiny()
        ax5.set_xticks(self.CG.newXlocation)
        #limit = range(0, self.cornerStitch_h.eastBoundary.cell.x)
        labels_h = ('X'+str(i) for i in range(0, len(self.CG.newXlocation)))
        ax5.xaxis.set_ticklabels(list(labels_h))

        ####Setting axis labels(end)

        """
        plt.xlim(0, self.cornerStitch_v.eastBoundary.cell.x)
        plt.ylim(0, self.cornerStitch_v.northBoundary.cell.y)
        labels_y = ( str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        #labels_y = ('Y' + str(i) for i in range(0, len(self.CG.zeroDimensionListv)))
        # plt.tick_params(self.CG.zeroDimensionListv, list(labels_y), axis='y', which='both', labelleft='off',labelright = 'on')
        plt.yticks(self.CG.zeroDimensionListv, list(labels_y))
        ax2.yaxis.tick_right()
        #ax2.tick_params(labeltop=True, labelright=True)
        """
        if self.name2:
            fig2.savefig(self.name2+'newv.png',bbox_inches='tight')
            matplotlib.pyplot.close(fig2)
        else:
            fig2.show()
            pylab.pause(11000)  # figure out how to do this better
        """
    def drawLayer_vnew(self, truePointer = False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """
        for i in range(len(self.Newcornerstitch_V)):
            arrowList2 = []
            for rect in self.Newcornerstitch_V[i].stitchList:
                # rect.cell.printCell(True,True)
                if rect.cell.type == "SOLID":
                    color = "blue"
                    arrowList2.append((rect.cell.getX(), rect.cell.getY(), rect.getWidth(), 0, color))

                elif rect.cell.type == "EMPTY":
                    color = "red"
                    arrowList2.append((rect.cell.getX(), rect.cell.getY(), 0, rect.getHeight(), color))
            #fig2 = matplotlib.pyplot.figure()
            fig2,ax4 = plt.subplots()
            for cell in self.Newcornerstitch_V[i].stitchList:


                #print "Latestv=",cell.cell.x,cell.cell.y
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
                if cell.getNorth() == self.Newcornerstitch_V[i].northBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getNorth().cell.x + (.08 * cell.getNorth().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                    dy = cell.getNorth().cell.y + (.08 * cell.getNorth().getHeight()) - (cell.cell.y + cell.getHeight()) + .08
                else:
                    dx =  0
                    dy = .1

                ax4.arrow((cell.cell.x + cell.getWidth() - .08),
                          (cell.cell.y + cell.getHeight()- .08),
                          dx,
                          dy,
                          head_width = .04,
                          head_length = .04,
                          fc = 'k',
                          ec = 'k'
                        )
                #EAST pointer
                if cell.getEast() == self.Newcornerstitch_V[i].eastBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getEast().cell.x + (.08 * cell.getEast().getWidth()) - (cell.cell.x + cell.getWidth()) + .08
                    dy = cell.getEast().cell.y + (.08 * cell.getEast().getHeight()) - (cell.cell.y + cell.getHeight()) + .08
                else:
                    dx = .1
                    dy = 0
                ax4.arrow((cell.cell.x + cell.getWidth() - .08),
                          (cell.cell.y + cell.getHeight()- .08),
                          dx,
                          dy,
                          head_width = .04,
                          head_length = .04,
                          fc = 'k',
                          ec = 'k'
                        )
                #SOUTH pointer
                if cell.getSouth() == self.Newcornerstitch_V[i].southBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getSouth().cell.x + (.08 * cell.getSouth().getWidth()) - (cell.cell.x + .08)
                    dy = cell.getSouth().cell.y + (.08 * cell.getSouth().getHeight()) - (cell.cell.y + .08)
                else:
                    dx =  0
                    dy = -.1
                ax4.arrow((cell.cell.x + .08),
                          (cell.cell.y + .08),
                          dx,
                          dy,
                          head_width = .04,
                          head_length = .04,
                          fc = 'k',
                          ec = 'k'
                        )
                #WEST pointer
                if cell.getWest() == self.Newcornerstitch_V[i].westBoundary:
                    dx = 0
                    dy = 0
                elif truePointer:
                    dx = cell.getWest().cell.x + (.08 * cell.getWest().getWidth()) - (cell.cell.x + .08)
                    dy = cell.getWest().cell.y + (.08 * cell.getWest().getHeight()) - (cell.cell.y + .08)
                else:
                    dx =  -.1
                    dy = 0
                ax4.arrow((cell.cell.x + .08),
                          (cell.cell.y + .08),
                          dx,
                          dy,
                          head_width = .04,
                          head_length = .04,
                          fc = 'k',
                          ec = 'k'
                        )
            #p = PatchCollection(self.drawZeroDimsVertices_v())
            #ax4.add_collection(p)

            #handle relative spacing from orientation to orientation-n (X0-Xn, Y0-Yn). Remove if refactoring to
            #automatically handle orientation
            #self.setAxisLabels(plt)

            for arr in arrowList2:
                ax4.arrow(arr[0], arr[1], arr[2], arr[3], head_width = .09, head_length = .09,  color =arr[4] )#


            ####Setting axis labels(begin)
            #ax4.set_ylim(0, 60)
            #ax4.set_xlim(0, 60)
            ax4.set_xlim(0, self.Newcornerstitch_V[i].eastBoundary.cell.x)
            ax4.set_ylim(0, self.Newcornerstitch_V[i].northBoundary.cell.y)
            #limit = np.arange(0, self. Newcornerstitch_v.northBoundary.cell.y + 1, 1)
            #ax4.set_yticks(limit)
            ax3 = ax4.twinx()
            ax3.set_yticks(self.CG.NEWYLOCATION[i])
            labels_h = ('Y'+str(i) for i in range(0, len(self.CG.NEWYLOCATION[i])))
            ax3.yaxis.set_ticklabels(list(labels_h))
            ax5 = ax4.twiny()
            ax5.set_xticks(self.CG.NEWXLOCATION[i])
            #limit = range(0, self.cornerStitch_h.eastBoundary.cell.x)
            labels_h = ('X'+str(i) for i in range(0, len(self.CG.NEWXLOCATION[i])))
            ax5.xaxis.set_ticklabels(list(labels_h))

            ####Setting axis labels(end)


            if self.name2:
                fig2.savefig(self.name2+str(i)+'newv.png',bbox_inches='tight')
                matplotlib.pyplot.close(fig2)
            else:
                fig2.show()
                pylab.pause(11000)  # figure out how to do this better

        (!!!!!!!!!!!!!!!!!-end)
    '''

    def drawLayer11(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig1 = matplotlib.pyplot.figure()
        # ax1 = fig1.add_subplot(111, aspect='equal')


        # for element in self.CG.special_location_x:
        # print"elx=", element
        # for element in self.CG.special_location_y:
        # print"el=", element
        # print self.Special_id,self.Special_id_h,self.Special_id_v
        for i in range(len(self.Newcornerstitch_H)):


                
            fig1, ax1 = plt.subplots()
            #print "#"
            for cell in self.Newcornerstitch_H[i].stitchList:


                # if not cell.cell.id in self.CG.special_cell_id_h or self.CG.special_cell_id_v:
                if not cell.cell.type == "EMPTY":
                    # if  cell.cell.id in self.Special_id_h or self.CG.special_cell_id_v:
                    # pattern = ''
                    if not cell.cell.id in self.Special_id_h:
                        if not cell.cell.id in self.CG.special_cell_id_v:
                            #print "1", cell.cell.id,cell.cell.x, cell.cell.y,cell.getWidth(),cell.getHeight()
                            pattern = '\\'


                else:
                    pattern = ''

                ax1.add_patch(
                    matplotlib.patches.Rectangle(
                        (cell.cell.x, cell.cell.y),  # (x,y)
                        cell.getWidth(),  # width
                        cell.getHeight(),  # height
                        hatch=pattern,
                        fill=False,
                        linewidth=3

                    )
                )
                # for j in self.Special_id[i]:
                if cell.cell.id in self.Special_id:
                    # print "id_h", cell.cell.id
                    for element in self.Special_stitchlist[i]:
                        # print element
                        if cell.cell.id in element.keys():
                            # cell.cell.x = element[cell.cell.id][0]

                            pattern = '\\'
                            ax1.add_patch(
                                matplotlib.patches.Rectangle((element[cell.cell.id][0], element[cell.cell.id][1]),
                                                             element[cell.cell.id][2],
                                                             element[cell.cell.id][3],  # height
                                                             hatch=pattern,
                                                             fill=True,
                                                             linestyle='dotted'
                                                             )
                            )

                if cell.cell.id not in self.Special_id:
                    if cell.cell.id in self.Special_id_h:
                        for element in self.Special_stitchlist_h[i]:
                            if cell.cell.id in element.keys():
                                # cell.cell.x = element[cell.cell.id][0]

                                pattern = '\\'
                                ax1.add_patch(
                                    matplotlib.patches.Rectangle((element[cell.cell.id][0], cell.cell.y),
                                                                 element[cell.cell.id][2],
                                                                 cell.getHeight(),  # height
                                                                 hatch=pattern,
                                                                 fill=True,
                                                                 linestyle='dotted'
                                                                 )
                                )
                if cell.cell.id not in self.Special_id:
                    if cell.cell.id in self.CG.special_cell_id_v:
                        for element in self.CG.special_location_y[i]:
                            if cell.cell.id in element.keys():
                                # cell.cell.x = element[cell.cell.id][0]

                                pattern = '\\'
                                ax1.add_patch(
                                    matplotlib.patches.Rectangle((cell.cell.x, element[cell.cell.id][0]),
                                                                 cell.getWidth(),
                                                                 element[cell.cell.id][2],  # height
                                                                 hatch=pattern,
                                                                 fill=True,
                                                                 linestyle='dotted'
                                                                 )
                                )


                                ####Setting axis labels(begin)
            ax1.set_ylim(0, self.Newcornerstitch_H[i].northBoundary.cell.y)
            ax1.set_xlim(0, self.Newcornerstitch_H[i].eastBoundary.cell.x)

            if self.name1:
                fig1.savefig(self.name1 +'-'+ str(i) + 'n-h.png', bbox_inches='tight')
                matplotlib.pyplot.close(fig1)
            else:
                fig1.show()
                pylab.pause(11000)  # figure out how to do this better

                # elif self.CS.orientation == 'v':

    def drawLayer22(self, truePointer=False):
        """
        Draw all cells in this cornerStitch with stitches pointing to their stitch neighbors
        TODO:
         Also should probably change the dimensions of the object window depending on the cornerStitch size.
        """

        # fig2 = matplotlib.pyplot.figure()
        for i in range(len(self.Newcornerstitch_V)):
            fig2, ax4 = plt.subplots()
            for cell in self.Newcornerstitch_V[i].stitchList:

                if not cell.cell.type == "EMPTY":
                    # if  cell.cell.id in self.Special_id_h or self.CG.special_cell_id_v:
                    # pattern = ''
                    if not cell.cell.id in self.Special_id_v:
                        if not cell.cell.id in self.CG.special_cell_id_h:
                            # print "1", cell.cell.id
                            pattern = '\\'


                else:
                    pattern = ''

                ax4.add_patch(
                    matplotlib.patches.Rectangle(
                        (cell.cell.x, cell.cell.y),  # (x,y)
                        cell.getWidth(),  # width
                        cell.getHeight(),  # height
                        hatch=pattern,
                        fill=False,
                        linewidth=3

                    )
                )
                if cell.cell.id in self.Special_id:
                    #print "id_h", cell.cell.id
                    for element in self.Special_stitchlist[i]:
                        # print element
                        if cell.cell.id in element.keys():
                            # cell.cell.x = element[cell.cell.id][0]

                            pattern = '\\'
                            ax4.add_patch(
                                matplotlib.patches.Rectangle((element[cell.cell.id][0], element[cell.cell.id][1]),
                                                             element[cell.cell.id][2],
                                                             element[cell.cell.id][3],  # height
                                                             hatch=pattern,
                                                             fill=True,
                                                             linestyle='dotted'
                                                             )
                            )

                if cell.cell.id not in self.Special_id:
                    if cell.cell.id in self.CG.special_cell_id_h:
                        for element in self.CG.special_location_x[i]:
                            if cell.cell.id in element.keys():
                                # cell.cell.x = element[cell.cell.id][0]

                                pattern = '\\'
                                ax4.add_patch(
                                    matplotlib.patches.Rectangle((element[cell.cell.id][0], cell.cell.y),
                                                                 element[cell.cell.id][2],
                                                                 cell.getHeight(),  # height
                                                                 hatch=pattern,
                                                                 fill=True,
                                                                 linestyle='dotted'
                                                                 )
                                )
                if cell.cell.id not in self.Special_id:
                    if cell.cell.id in self.Special_id_v:
                        for element in self.Special_stitchlist_v[i]:
                            if cell.cell.id in element.keys():
                                # cell.cell.x = element[cell.cell.id][0]

                                pattern = '\\'
                                ax4.add_patch(
                                    matplotlib.patches.Rectangle((cell.cell.x, element[cell.cell.id][0]),
                                                                 cell.getWidth(),
                                                                 element[cell.cell.id][2],  # height
                                                                 hatch=pattern,
                                                                 fill=True,
                                                                 linestyle='dotted'
                                                                 )
                                )

            ax4.set_ylim(0, self.Newcornerstitch_V[i].northBoundary.cell.y)
            ax4.set_xlim(0, self.Newcornerstitch_V[i].eastBoundary.cell.x)
            if self.name2:
                fig2.savefig(self.name2 +'-'+ str(i) + 'n-v.png', bbox_inches='tight')
                matplotlib.pyplot.close(fig2)
            else:
                fig2.show()
                pylab.pause(11000)  # figure out how to do this better

    ###############################################################################################################################################











    def drawRectangle(self, list=[], *args):
        fig = plt.figure()
        ax3 = fig.add_subplot(111, aspect='equal')
        for p in list:
            ax3.add_patch(p)
        plt.xlim(0, 60)
        plt.ylim(0, 60)
        fig.savefig(self.name1 + '-input.png', bbox_inches='tight')
