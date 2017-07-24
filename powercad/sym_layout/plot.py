'''
Created on Nov 6, 2012

@author: shook

# test commit.
'''

import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib.patches import Rectangle, PathPatch, Circle, Arc
from matplotlib.path import Path

from powercad.sym_layout.svg import LayoutLine, LayoutPoint, find_layout_bounds
#from powercad.sym_layout.symbolic_layout import Corner

from powercad.util import Rect
from _sqlite3 import Row

# sxm - This function is only used in svg.py's main().
def plot_svg_objs(layout):
    print "plot_svg_objs() started"
    ax = plt.subplot('111', adjustable='box', aspect=1.0)
    bounds = Rect(*find_layout_bounds(layout)) #sxm edit originally: bounds = Rect(*find_layout_bounds(layout))
    
    for element in layout:
        if isinstance(element, LayoutLine):
            verts = [(element.pt1), (element.pt2)]
            codes = [Path.MOVETO, Path.LINETO]
            path = Path(verts, codes)
            col = '#A4A3A8'
            patch = PathPatch(path, edgecolor=col, lw=10)
            ax.add_patch(patch)
            
    for element in layout:
        if isinstance(element, LayoutPoint):
            patch = Circle(element.pt, radius=bounds.width()/30.0)
            ax.add_patch(patch)
            
    ax.axis([bounds.left, bounds.right, bounds.bottom, bounds.top])
    plt.show()
    print "plot_svg_objs() completed."

def plot_layout(sym_layout, filletFlag, ax = plt.subplot('111', adjustable='box', aspect=1.0), new_window=True, plot_row_col=False):
    print "plot_layout() started."
    hlist = sym_layout.h_rowcol_list
    vlist = sym_layout.v_rowcol_list
    traces = sym_layout.all_trace_lines
    sub_dim = sym_layout.sub_dim
    
    # Plot substrate boundary first
    sub_w, sub_l = sym_layout.module.substrate.dimensions
    ledge = sym_layout.module.substrate.ledge_width
    sub_rect = Rect(sub_l, 0.0, 0.0, sub_w)
    sub_rect.translate(-ledge, -ledge)
    r = Rectangle((sub_rect.left, sub_rect.bottom), sub_rect.width(), sub_rect.height(), facecolor='#E6E6E6', edgecolor='#616161')
    ax.add_patch(r)

    # Detect corners for filleting
    if filletFlag:
        sym_layout2 = copy.deepcopy(sym_layout) # create a deepcopy of sym_layout so that phantom traces can be removed
        fillets, supertraces = detect_corners_90(sym_layout2, ax) # detect 90 degree inner corners for intersecting traces
        detect_corners_270(sym_layout2, ax, fillets, supertraces) # detect 270 degree outer corners for all traces

    # Setup viewing bounds
    ax.set_xlim(sub_rect.left - 1.0, sub_rect.right + 1.0)
    ax.set_ylim(sub_rect.bottom - 1.0, sub_rect.top + 1.0)
    ax.set_axis_on()  # sxm: originally ax.set_axis_off()

    for sym in traces:
        plot = True
        if sym.is_supertrace():
            plot = sym.has_rect

        if plot:
            color = '#B6C2CF'
            rect = sym.trace_rect
            r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor=color,
                          edgecolor='None')
            ax.add_patch(r)

    for lead in sym_layout.leads:
        rect = lead.footprint_rect
        r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor='#4DFF64',
                      edgecolor=color)
        ax.add_patch(r)
        patch = Circle(lead.center_position, radius=0.1)
        ax.add_patch(patch)
    x_pos = []
    y_pos = []

    for dev in sym_layout.devices:  # collect position data
        dev_center = dev.center_position
        x_pos.append(dev_center[0])
        y_pos.append(dev_center[1])
    x_num = x_pos.count(x_pos[0])
    y_num = y_pos.count(y_pos[0])

    '''
    for row in np.arange(1,x_num,1):
        print row
        print enumerate(x_pos)
    '''
    for dev in sym_layout.devices:
        # die_label='die%s'%(sym_layout.devices[die_count].dv_index)
        rect = dev.footprint_rect
        r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor='#2A3569',
                      edgecolor=color)
        ax.add_patch(r)
        patch = Circle(dev.center_position, radius=0.1)
        ax.add_patch(patch)
        # ax.text(rect.left, rect.bottom,die_label)
        # die_count+=1
    for wire in sym_layout.bondwires:
        for pt_index in xrange(len(wire.start_pts)):
            pt1 = wire.start_pts[pt_index]
            pt2 = wire.end_pts[pt_index]
            verts = [(pt1), (pt2)]
            codes = [Path.MOVETO, Path.LINETO]
            path = Path(verts, codes)
            col = '#FFFFBA'
            patch = PathPatch(path, edgecolor=col, lw=2)
            ax.add_patch(patch)

            #    for col in hlist:
            #        if col.phantom:
            #            color = '#0000FF'
            #        else:
            #            color = '#000000'
            #            r = Rectangle((col.left, 0.0), col.right-col.left, sub_dim[1], alpha=1.0, facecolor='None', edgecolor=color)
            #            ax.add_patch(r)
            #
            #    for row in vlist:
            #        if row.phantom:
            #            color = '#0000FF'
            #        else:
            #            color = '#000000'
            #            r = Rectangle((0.0, row.left), sub_dim[0], row.right-row.left, alpha=1.0, facecolor='None', edgecolor=color)
            #            ax.add_patch(r)

    if new_window:
        plt.show()

    print "plot_layout() completed."
    return ax

class Trace(object):
    def __init__(self, t):
        self.top = round(t.trace_rect.top, 2)
        self.bottom = round(t.trace_rect.bottom, 2)
        self.left = round(t.trace_rect.left, 2)
        self.right = round(t.trace_rect.right, 2)

class InnerCorner(object):
    def __init__(self, t1, t2):
        self.x = None
        self.y = None
        self.trace1 = t1
        self.trace2 = t2

class OuterCorner(object):
    def __init__(self, t):
        self.x = None
        self.y = None
        self.concavityQuadrant = None
        self.trace = t

class Fillet(object):
    def __init__(self, corner, quadrant):
        self.corner = corner # coordinates of the corner (object of class InnerCorner or OuterCorner)
        self.concavityQuadrant = quadrant # 1= concave in 1st quadrant, 2= conc n 2nd quad, 3= conc in 3rd quad, 4= conc in 4th quad
        self.radius = 2 # default fillet depth
        self.centerX = None
        self.centerY = None
        self.theta1 = None
        self.theta2 = None

    def calcOuterFilletSpecs(self):
        """Calculate an outer corner's fillet specifications such as fillet arc center coordinates and sector starting angle and ending angle based on the concavity quadrant."""
        self.radius = (round(min(self.corner.trace.trace_rect.top-self.corner.trace.trace_rect.bottom, self.corner.trace.trace_rect.right-self.corner.trace.trace_rect.left, 2), 2))/2
        if self.concavityQuadrant == 1:
            self.centerX = self.corner.x + self.radius
            self.centerY = self.corner.y + self.radius
            self.theta1 = 180.0
            self.theta2 = 270.0
        elif self.concavityQuadrant == 2:
            self.centerX = self.corner.x - self.radius
            self.centerY = self.corner.y + self.radius
            self.theta1 = 270.0
            self.theta2 = 360.0
        elif self.concavityQuadrant == 3:
            self.centerX = self.corner.x - self.radius
            self.centerY = self.corner.y - self.radius
            self.theta1 = 0.0
            self.theta2 = 90.0
        elif self.concavityQuadrant == 4:
            self.centerX = self.corner.x + self.radius
            self.centerY = self.corner.y - self.radius
            self.theta1 = 90.0
            self.theta2 = 180.0

    def calcInnerFilletSpecs(self):
        """Calculate an inner corner's fillet specifications such as fillet arc center coordinates and sector starting angle and ending angle based on the concavity quadrant."""
        self.radius = (round(min(self.corner.trace1.top-self.corner.trace1.bottom, self.corner.trace1.right-self.corner.trace1.left, \
                                self.corner.trace2.top-self.corner.trace2.bottom, self.corner.trace2.right-self.corner.trace2.left, 2), 2))/2
        if self.concavityQuadrant == 1:
            self.centerX = self.corner.x + self.radius
            self.centerY = self.corner.y + self.radius
            self.theta1 = 180.0
            self.theta2 = 270.0
        elif self.concavityQuadrant == 2:
            self.centerX = self.corner.x - self.radius
            self.centerY = self.corner.y + self.radius
            self.theta1 = 270.0
            self.theta2 = 360.0
        elif self.concavityQuadrant == 3:
            self.centerX = self.corner.x - self.radius
            self.centerY = self.corner.y - self.radius
            self.theta1 = 0.0
            self.theta2 = 90.0
        elif self.concavityQuadrant == 4:
            self.centerX = self.corner.x + self.radius
            self.centerY = self.corner.y - self.radius
            self.theta1 = 90.0
            self.theta2 = 180.0

def getOuterCorners(t):
    """For a given trace, return the top-left, top-right, bottom-left, bottom-right corner coordinates."""
    oc1 = OuterCorner(t)
    oc1.x = round(t.trace_rect.left, 2)
    oc1.y = round(t.trace_rect.top, 2)
    oc1.concavityQuadrant = 4
    oc2 = OuterCorner(t)
    oc2.x = round(t.trace_rect.right, 2)
    oc2.y = round(t.trace_rect.top, 2)
    oc2.concavityQuadrant = 3
    oc3 = OuterCorner(t)
    oc3.x = round(t.trace_rect.left, 2)
    oc3.y = round(t.trace_rect.bottom, 2)
    oc3.concavityQuadrant = 1
    oc4 = OuterCorner(t)
    oc4.x = round(t.trace_rect.right, 2)
    oc4.y = round(t.trace_rect.bottom, 2)
    oc4.concavityQuadrant = 2
    return oc1, oc2, oc3, oc4

def addFillet(fillets, corner, temp_x, temp_y, concavityQuadrant):
    """Creates a Fillet object using the given InnerCorner(OuterCorner) object and the given concavity quadrant, and then adds it to the given fillets[] list"""
    corner.x = temp_x
    corner.y = temp_y
    fillets.append(Fillet(corner, concavityQuadrant))

def searchCorner(trace1, trace2, corneredTraces):
    """Search if the combination of trace1 and trace2 exist in the corneredTraces[] list. Return True if so, False otherwise."""
    for c in corneredTraces:
        if ((trace1.top, trace1.bottom, trace1.left, trace1.right) == (c.trace1.top, c.trace1.bottom, c.trace1.left, c.trace1.right) and \
                (trace2.top, trace2.bottom, trace2.left, trace2.right) == (c.trace2.top, c.trace2.bottom, c.trace2.left, c.trace2.right)) or \
                        ((trace2.top, trace2.bottom, trace2.left, trace2.right) == (c.trace1.top, c.trace1.bottom, c.trace1.left, c.trace1.right) and \
                                (trace1.top, trace1.bottom, trace1.left, trace1.right) == (c.trace2.top, c.trace2.bottom, c.trace2.left, c.trace2.right)):
            return True
    return False

def detect_corners_90(sym_layout2, ax):
    '''INNER CORNER DETECTION
    @author: Shilpi Mukherjee 
    @date: 30-JUN-2017
    This function detects inner corners on traces that connect orthogonally for a selected solution layout.
    It marks the corners with a fillet in the layout preview and saved solution window,
    and displays (x,y),q for each corner,
    where (x,y) is the cartesian coordinate of the corner,
    and q is the quandrant in which the corner is concave.
    :param sym_layout: Symbolic Layout object
    :param ax: subplot specifications'''

    # START WITH EMPTY LISTS FOR STORING CORNERED TRACES AND SUPERTRACES
    cornered_traces = [] # create an empty list of pairs of traces meeting at a corner
    supertraces = [] # create an empty list of supertraces

    # POPULATE CORNERED_TRACES LIST BY ITERATING THROUGH ALL TRACE LINES AND FINDING TRACE-PAIRS THAT ARE TOUCHING AND ORTHOGONAL
    for i in sym_layout2.all_trace_lines:
        # AT THE SAME TIME, SAVE SUPERTRACES SEPARATELY IN THE SUPERTRACES LIST AS YOU COME ACROSS THEM WHILE ITERATING THROUGH THE LIST OF ALL TRACES
        if i.intersecting_trace is not None: # supertrace found
            supertraces.append(i) # add to supertraces list
        if len(i.trace_connections) > 0: # potential cornered trace-pair found
            trace_rectangle = Trace(i) # copy the top,bottom,left,right edges of the trace rectangle
            for j in i.trace_connections:
                connecting_trace_rectangle = Trace(j) # copy the top,bottom,left,right edges of the connecting trace rectangle
                if (searchCorner(trace_rectangle, connecting_trace_rectangle, cornered_traces) == False):
                    corner1 = InnerCorner(trace_rectangle, connecting_trace_rectangle)  # create an InnerCorner object using the two traces
                    cornered_traces.append(corner1) # append only if the pair doesn't already exist in the cornered_traces list

    # ITERATE THROUGH ALL SUPERTRACES AND ALL TRACE LINES FINDING PAIRS BETWEEN A SUPERTRACE AND A REGULAR TRACE
    # THAT ARE TOUCHING AND ORTHOGONAL, THAT MAY NOT HAVE BEEN DETECTED BEFORE, FURTHER POPULATING CORNERED_TRACES LIST
    for i in supertraces:
        for j in sym_layout2.all_trace_lines:
            if j.intersecting_trace is not None: # supertrace found
                continue
            else: # regular (non-supertrace) trace found
                if round(i.trace_rect.top,2) == round(j.trace_rect.bottom,2) or round(i.trace_rect.right,2) == round(j.trace_rect.left,2) or \
                                round(i.trace_rect.bottom,2) == round(j.trace_rect.top,2) or round(i.trace_rect.left,2) == round(j.trace_rect.right,2):
                    trace_rectangle = Trace(i) # trace rectangle converted to a Trace object
                    connecting_trace_rectangle = Trace(j) # connecting trace rectangle converted to a Trace object
                    corner1 = InnerCorner(trace_rectangle, connecting_trace_rectangle)  # create an InnerCrner object using the two traces
                    cornered_traces.append(corner1) # append the corner only if the pair of traces making the corner don't already exist in the cornered_traces list

    fillets = [] # create an empty list of Fillet objects

    # FOR EACH ITEM IN CORNERED_TRACES LIST, CHECK WHICH EDGE IS IN COMMON AND SAVE THAT AS ONE OF THE CORNER COORDINATES.
    for i in cornered_traces:
        temp_x = None
        temp_y = None
        concavityQuadrant = None
        if i.trace1.top == i.trace2.bottom: # common y (top of one matching bottom of the other)
            temp_y = i.trace1.top
        elif i.trace1.bottom == i.trace2.top: # common y (top of one matching bottom of the other)
            temp_y = i.trace1.bottom
        elif i.trace1.left == i.trace2.right: # common x (left of one matching right of the other)
            temp_x = i.trace1.left
        elif i.trace1.right == i.trace2.left: # common x (left of one matching right of the other)
            temp_x = i.trace1.right
        if ((temp_x is None) and (temp_y is None)): # If both x and y are blank, it's not a valid corner. If so, go to next item in list.
            continue

        # FIND THE OTHER COORDINATE (L-JUNCTION) BY COMPARING EDGE LOCATIONS OF THE PAIR OF TRACES BEING ASSESSED
        elif temp_x is None: # Find x-coordinate of the corner
            if i.trace1.left == i.trace2.left: # if left side is common, select right side of the lower width box as the corner-x.
                if i.trace1.right < i.trace2.right:
                    temp_x = i.trace1.right
                    if temp_y == i.trace1.bottom:
                        concavityQuadrant = 1
                    elif temp_y == i.trace2.bottom:
                        concavityQuadrant = 4
                elif i.trace1.right > i.trace2.right: # explicit condition used here to avoid phantom traces from being counted as valid.
                    temp_x = i.trace2.right
                    if temp_y == i.trace2.bottom:
                        concavityQuadrant = 1
                    elif temp_y == i.trace1.bottom:
                        concavityQuadrant = 4
            elif i.trace1.right == i.trace2.right: # if right side is common, select left side of the lower width box as the corner-x.
                if i.trace1.left > i.trace2.left:
                    temp_x = i.trace1.left
                    if temp_y == i.trace1.bottom:
                        concavityQuadrant = 2
                    elif temp_y == i.trace2.bottom:
                        concavityQuadrant = 3
                elif i.trace1.left < i.trace2.left: # explicit condition used here to avoid phantom traces from being counted as valid.
                    temp_x = i.trace2.left
                    if temp_y == i.trace2.bottom:
                        concavityQuadrant = 2
                    elif temp_y == i.trace1.bottom:
                        concavityQuadrant = 3
        elif temp_y is None: # Find y-coordinate of the corner
            if i.trace1.top == i.trace2.top:  # if top side is common, select bottom side of the lower height box as the corner-y.
                if i.trace1.bottom > i.trace2.bottom:
                    temp_y = i.trace1.bottom
                    if temp_x == i.trace1.right:
                        concavityQuadrant = 3
                    elif temp_x == i.trace2.right:
                        concavityQuadrant = 4
                elif i.trace1.bottom < i.trace2.bottom: # explicit condition used here to avoid phantom traces from being counted as valid.
                    temp_y = i.trace2.bottom
                    if temp_x == i.trace2.right:
                        concavityQuadrant = 3
                    elif temp_x == i.trace1.right:
                        concavityQuadrant = 4
            elif i.trace1.bottom == i.trace2.bottom: # if bottom side is common, select top side of the lower height box as the corner-y.
                if i.trace1.top < i.trace2.top:
                    temp_y = i.trace1.top
                    if temp_x == i.trace1.right:
                        concavityQuadrant = 2
                    elif temp_x == i.trace2.right:
                        concavityQuadrant = 1
                elif i.trace1.top > i.trace2.top: # explicit condition used here to avoid phantom traces from being counted as valid.
                    temp_y = i.trace2.top
                    if temp_x == i.trace2.right:
                        concavityQuadrant = 2
                    elif temp_x == i.trace1.right:
                        concavityQuadrant = 1
        if ((temp_x is not None) and (temp_y is not None)):
            addFillet(fillets, i, temp_x, temp_y, concavityQuadrant)

        # FIND THE OTHER COORDINATE (T-JUNCTION) BY COMPARING EDGE LOCATIONS OF THE PAIR OF TRACES BEING ASSESSED
        elif temp_x is None and temp_y is not None: # if temp_x is still None (but temp_y has been found), this is a T-junction.
            if (((i.trace1.left > i.trace2.left) & (i.trace1.left < i.trace2.right))) & (((i.trace1.right > i.trace2.left) & (i.trace1.right < i.trace2.right))):
                temp_x = i.trace1.left
                if temp_y == i.trace1.bottom:
                    concavityQuadrant = 2
                elif temp_y == i.trace2.bottom:
                    concavityQuadrant = 3
                addFillet(fillets, i, temp_x, temp_y, concavityQuadrant)
                temp_x = i.trace1.right
                if temp_y == i.trace2.bottom:
                    concavityQuadrant = 4
                elif temp_y == i.trace1.bottom:
                    concavityQuadrant = 1
                c = InnerCorner(i.trace1, i.trace2) # create a new InnerCorner object so as not to overwite the previous InnerCorner object
                addFillet(fillets, c, temp_x, temp_y, concavityQuadrant)
            elif (((i.trace2.left > i.trace1.left) & (i.trace2.left < i.trace1.right))) & (((i.trace2.right > i.trace1.left) & (i.trace2.right < i.trace1.right))):
                temp_x = i.trace2.left
                if temp_y == i.trace2.bottom:
                    concavityQuadrant = 2
                elif temp_y == i.trace1.bottom:
                    concavityQuadrant = 3
                addFillet(fillets, i, temp_x, temp_y, concavityQuadrant)
                temp_x = i.trace2.right
                if temp_y == i.trace1.bottom:
                    concavityQuadrant = 4
                elif temp_y == i.trace2.bottom:
                    concavityQuadrant = 1
                c = InnerCorner(i.trace1, i.trace2)  # create a new InnerCorner object so as not to overwite the previous InnerCorner object
                addFillet(fillets, c, temp_x, temp_y, concavityQuadrant)
        elif temp_y is None and temp_x is not None: # if temp_y is still None (but temp_x has been found), this is a sideways T-junction.
            if (((i.trace1.top > i.trace2.bottom) & (i.trace1.top < i.trace2.top))) & (((i.trace1.bottom > i.trace2.bottom) & (i.trace1.bottom < i.trace2.top))):
                temp_y = i.trace1.top
                if temp_x == i.trace1.right:
                    concavityQuadrant = 2
                elif temp_x == i.trace2.right:
                    concavityQuadrant = 1
                addFillet(fillets, i, temp_x, temp_y, concavityQuadrant)
                temp_y = i.trace1.bottom
                if temp_x == i.trace1.right:
                    concavityQuadrant = 3
                elif temp_x == i.trace2.right:
                    concavityQuadrant = 4
                c = InnerCorner(i.trace1, i.trace2)  # create a new InnerCorner object so as not to overwite the previous InnerCorner object
                addFillet(fillets, c, temp_x, temp_y, concavityQuadrant)
            elif (((i.trace2.top > i.trace1.bottom) & (i.trace2.top < i.trace1.top))) & ((i.trace2.bottom > i.trace1.bottom) & (i.trace2.bottom < i.trace1.top)):
                temp_y = i.trace2.top
                if temp_x == i.trace2.right:
                    concavityQuadrant = 2
                elif temp_x == i.trace1.right:
                    concavityQuadrant = 1
                addFillet(fillets, i, temp_x, temp_y, concavityQuadrant)
                temp_y = i.trace2.bottom
                if temp_x == i.trace2.right:
                    concavityQuadrant = 3
                elif temp_x == i.trace1.right:
                    concavityQuadrant = 4
                c = InnerCorner(i.trace1, i.trace2)  # create a new InnerCorner object so as not to overwite the previous InnerCorner object
                addFillet(fillets, c, temp_x, temp_y, concavityQuadrant)

    # OUTPUT THE fillets[] LIST AND MARK THE FILLETS ON THE LAYOUT PREVIEW AND SOLUTION WINDOW
    print "Inner Corners (90 degrees): "
    print "Format: (x, y), fillet concavity quadrant"
    for i in fillets:
        i.calcInnerFilletSpecs() # Find fillet/arc specifications
        print (i.corner.x, i.corner.y), i.concavityQuadrant
        a = Arc((i.centerX, i.centerY), i.radius*2, i.radius*2, theta1=i.theta1, theta2=i.theta2, facecolor='#E6E6E6', edgecolor='red', linewidth=2)
        #ax.add_patch(r) # toggle comment to enable/disable rectangle markings
        ax.add_patch(a) # toggle comment to enable/disable fillet markings

    return fillets, supertraces

def searchInnerFillets(oc, innerFillets):
    '''Searches for given OuterCorner, j, in given innerFillets list and returns the list of duplicates.'''
    duplicates = [] # create an empty list to store indices where oc is found in innerFillets
    for i in innerFillets:
        if (round(oc.x, 2) == round(i.corner.x, 2)) and (round(oc.y, 2) == round(i.corner.y, 2)):
            duplicates.append(i)
    return duplicates

def searchOuterFillets(f, outerFillets):
    '''Searches for given fillet, f, in given outerFillets list and returns the list of duplicates.'''
    duplicates = []  # create an empty list to store indices where f is found in outerFillets
    for i in outerFillets:
        if (f.corner.x == i.corner.x) and (f.corner.y == i.corner.y):
            duplicates.append(i)
    return duplicates

def detect_corners_270(sym_layout2, ax, innerFillets, supertraces):
    """OUTER CORNER DETECTION
    @author: Shilpi Mukherjee
    @date: 30-JUN-2017
    This function detects 270 degree outer trace corners for a selected solution layout.
    It marks corners with a grey fillet in the layout preview and saved solution window,
    and displays ((x,y),q,r) of each corner in the console,
    where (x,y) is the cartesian coordinate of the corner,
    q is the direction of concavity of the fillet expressed in terms of quadrants (1, 2, 3, or 4), and
    r is the limit on the size of the fillet (fillet radius) for corners of narrow traces
    :param sym_layout2: Symbolic Layout object
    :param ax: subplot specifications
    :param innerFillets: list of 90 degree inner corners
    :param supertraces: list of supertraces"""

    # FIND AND ISOLATE THE PHANTOM TRACES. REMOVE THEM FROM SYM_LAYOUT2.ALL_TRACE_LINES
    phantomSupertraces = []
    for i in supertraces:
        for j in supertraces:
            if i is not j:
                if j.trace_rect.top <= i.trace_rect.top and j.trace_rect.bottom >= i.trace_rect.bottom and j.trace_rect.left >= i.trace_rect.left and j.trace_rect.right <= i.trace_rect.right:
                    phantomSupertraces.append(j)
                    supertraces.remove(j)
                    sym_layout2.all_trace_lines.remove(j) # REMOVE THE PHANTOM TRACES FROM ALL_TRACE_LINES OF THE DUPLICATE SYM_LAYOUT OBJECT

    # SEARCH ALL_TRACE_LINES FOR ALL THE 270 DEGREE CORNERS (OUTER CORNERS)
    corners_270 = []
    outerFillets = []

    for i in sym_layout2.all_trace_lines:
        oc = getOuterCorners(i) # Returns four OuterCorner objects for the given trace, i
        # REMOVE OUTERCORNERS THAT ARE CONGRUENT TO AN INNERCORNER (i.e. their x,y coordinates match)
        for j in oc:
            innerDuplicates = searchInnerFillets(j, innerFillets) # save the duplicate objects in innerFillets[] list
            if len(innerDuplicates) == 0:
                f = Fillet(j, j.concavityQuadrant)
                outerduplicates = searchOuterFillets(f, outerFillets) # save the duplicate objects in outerFillets[] list
                if len(outerduplicates) > 0:
                    for k in outerduplicates:
                        outerFillets.remove(k) # remove the duplicates
                else:
                    corners_270.append((j.x, j.y)) # add to the list of corners
                    outerFillets.append(f) # add to the list of fillets
            elif len(innerDuplicates) > 0:
                continue

    # MARK THE OUTER CORNERS WITH FILLETS WITH CUSTOMIZED ORIENTATION AND SIZE
    print "Outer Corners (270 degrees):"
    print "Format: ((x, y), fillet concavity quadrant, fillet size (default=2))"
    for i in outerFillets:
        i.calcOuterFilletSpecs() # Find fillet/arc specifications
        print ((i.corner.x, i.corner.y), i.concavityQuadrant, i.radius)
        a = Arc((i.centerX, i.centerY), i.radius*2, i.radius*2, theta1=i.theta1, theta2=i.theta2, facecolor='#E6E6E6', edgecolor='blue', linewidth=2)
        ax.add_patch(a) # toggle comment to enable/disable fillet markings

# test Jun 30, 2017