'''
Created on Nov 6, 2012

@author: shook

# test commit.
'''

import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib.patches import Rectangle, PathPatch, Circle
from matplotlib.path import Path

from powercad.sym_layout.svg import LayoutLine, LayoutPoint, find_layout_bounds
#from powercad.sym_layout.symbolic_layout import Corner

from powercad.util import Rect
from _sqlite3 import Row

# class Corner(object): # sxm - marks corners that need to be filleted.
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

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

def plot_layout(sym_layout,ax = plt.subplot('111', adjustable='box', aspect=1.0), new_window=True, plot_row_col=False):
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

    # CORNER DETECTION
    sym_layout2 = copy.deepcopy(sym_layout) # create a deepcopy of sym_layout so that phantom traces can be removed
    corners, supertraces = detect_corners_90(sym_layout2, ax) # detect 90 degree inner corners for intersecting traces
    detect_corners_270(sym_layout2, ax, corners, supertraces) # detect 270 degree outer corners for all traces

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

def detect_corners_90(sym_layout2, ax):
    '''CORNER DETECTION 
    @author: Shilpi Mukherjee 
    @date: 14-JUN-2017
    This function detects 90 degree inner trace corners for a selected solution layout.
    It marks corners as a red rectangle in the layout preview and saved solution window, 
    and displays the (x,y) coordinates of each corner in the console.
    :param sym_layout: Symbolic Layout object
    :param ax: subplot specifications'''

    # ---- sxm start test block - Mark corner ----------


    # all_cornered_traces_list = [] # create an empty list of traces where each item is a tuple (top, bottom, left, right) defining a rectangle for that trace on the layout
    # trace_id = 0
    # for i in sym_layout.all_trace_lines:
    #     trace_rectangle = (i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right)
    #     trace = (trace_id, trace_rectangle)
    #     all_cornered_traces_list.append(trace)
    #     trace_id += 1
    #     # if i.trace_connections is not None:
    #     #     connecting_traces = i.trace_connections
    #
    # print "local all_cornered_traces_list: \n", all_cornered_traces_list


    # CHECK IF TWO TRACES ARE ALREADY IN TRACE_CONNECTIONS LIST (RETURN TRUE IF ALREADY IN THE LIST)
    # def already_existing(t1, t2):
    #     if (t2 in t1.trace_connections) and (t1 in t2.trace_connections):
    #         return True
    #     else:
    #         return False


    # DUPLICATE SYM LAYOUT AND MODIFY SUPERTRACE AS A TRACE
    # sym_layout2 = copy.deepcopy(sym_layout)
    # print sym_layout
    # print sym_layout2
    # for i in sym_layout2.all_trace_lines:
    #     i.trace_connections = []
    # for trace1 in sym_layout2.all_trace_lines:
    #     for trace2 in sym_layout2.all_trace_lines:
    #         if trace1 is not trace2:
    #             if trace1.trace_line.vertical == True and trace2.trace_line.vertical == False:
    #                 obj1 = trace1.trace_line  #  vertical
    #                 obj2 = trace2.trace_line  #  horizontal
    #             elif trace1.trace_line.vertical == False and trace2.trace_line.vertical == True:
    #                 obj1 = trace2.trace_line #  vertical
    #                 obj2 = trace1.trace_line #  horizontal
    #             if obj1.pt1[0] >= obj2.pt1[0] and obj1.pt1[0] <= obj2.pt2[0] and \
    #                 obj2.pt1[1] >= obj1.pt1[1] and obj2.pt1[1] <= obj1.pt2[1]: # T-junctions, L-junctions, and supertraces
    #                 if already_existing(trace1, trace2):
    #                     continue
    #                 elif trace1.intersecting_trace is not None and trace2.intersecting_trace is not None: # supertrace found
    #                     if trace1.trace_rect.top-trace1.trace_rect.bottom >= trace2.trace_rect.top-trace2.trace_rect.bottom and \
    #                         trace1.trace_rect.right-trace1.trace_rect.left >= trace2.trace_rect.right-trace2.trace_rect.left: # trace1 is bigger than trace2
    #                         sym_layout2.all_trace_lines.remove(trace2) # remove the smaller trace
    #                     else:
    #                         sym_layout2.all_trace_lines.remove(trace1) # remove the smaller trace
    #                 else:
    #                     trace1.trace_connections.append(trace2)  # Set trace 1 trace_connections value equal trace 2
    #                     trace2.trace_connections.append(trace1)  # Set trace 2 trace_connections value equal trace 1
    #
    # print len(sym_layout.all_trace_lines)
    # print len(sym_layout2.all_trace_lines)


    # START WITH EMPTY LISTS FOR STORING CORNERED TRACES AND SUPERTRACES
    cornered_traces = [] # create an empty list of pairs of traces meeting at a corner
    supertraces = [] # create an empty list of supertraces
    # corner_id = 0

    # ITERATE THROUGH ALL TRACE LINES FINDING TRACE-PAIRS THAT ARE TOUCHING AND ORTHOGONAL, POPULATING CORNERED_TRACES LIST,
    # SAVING SUPERTRACES SEPARATELY IN THE SUPERTRACES LIST
    for i in sym_layout2.all_trace_lines:
        # print i, i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right, i.trace_connections
        if i.intersecting_trace is not None: # supertrace found
            supertraces.append(i) # add to supertraces list
        if len(i.trace_connections) > 0: # potential cornered trace-pair found
            trace_rectangle = (round(i.trace_rect.top,2), round(i.trace_rect.bottom,2), round(i.trace_rect.left,2), round(i.trace_rect.right,2)) # copy the trace rectangle's dimensions
            for j in i.trace_connections:
                connecting_trace_rectangle = (round(j.trace_rect.top,2), round(j.trace_rect.bottom,2), round(j.trace_rect.left,2), round(j.trace_rect.right,2)) # copy the dimensions of the connecting trace rectangle
                # append only if the pair doesn't already exist in the cornered_traces list
                temp = (trace_rectangle, connecting_trace_rectangle)
                temp2 = (connecting_trace_rectangle, trace_rectangle)
                if ((temp not in cornered_traces) and (temp2 not in cornered_traces)):
                    cornered_traces.append(temp)

    # ITERATE THROUGH ALL SUPERTRACES AND ALL TRACE LINES FINDING PAIRS BETWEEN A SUPERTRACE AND A REGULAR TRACE
    # THAT ARE TOUCHING AND ORTHOGONAL, THAT MAY NOT HAVE BEEN DETECTED BEFORE, FURTHER POPULATING CORNERED_TRACES LIST
    for i in supertraces:
        for j in sym_layout2.all_trace_lines:
            if j.intersecting_trace is not None: # supertrace
                continue
            else: # found regular trace
                if round(i.trace_rect.top,2) == round(j.trace_rect.bottom,2) or round(i.trace_rect.right,2) == round(j.trace_rect.left,2) or \
                                round(i.trace_rect.bottom,2) == round(j.trace_rect.top,2) or round(i.trace_rect.left,2) == round(j.trace_rect.right,2):
                    trace_rectangle = (round(i.trace_rect.top,2), round(i.trace_rect.bottom,2), round(i.trace_rect.left,2), round(i.trace_rect.right,2))
                    connecting_trace_rectangle = (round(j.trace_rect.top,2), round(j.trace_rect.bottom,2), round(j.trace_rect.left,2), round(j.trace_rect.right,2))
                    temp = (trace_rectangle, connecting_trace_rectangle)
                    temp2 = (connecting_trace_rectangle, trace_rectangle)
                    if ((temp not in cornered_traces) and (temp2 not in cornered_traces)):
                        cornered_traces.append(temp)

    # print "super traces"
    # for i in supertraces:
    #     print i, i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right  # check this sxm (read out their top bottom left right coordinates)
        # compare the supertrace's top/bot/left/right to ALL the traces' T/B/L/R. If adjacency is found, but not in cornered_traces list, then add it to the list.
        # supertrace_rectangle = (i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right)
        # print supertrace_rectangle

        # if _search_corner(cornered_traces, temp, temp2):
        #     pass
        #     print "Duplicate found."
        # else:
        #     cornered_traces.append(temp)
        # corner_id += 1

    corners = [] # create an empty corners list
    FIRST = 0 # first box
    SECOND = 1 # second box
    TOP = 0 # top of rectangle
    BOTTOM = 1 # bottom of rectangle
    LEFT = 2 # left of rectangle
    RIGHT = 3 # right of rectangle
    # print "cornered traces list:"

    # FOR EACH ITEM IN CORNERED_TRACES LIST, CHECK WHICH EDGE IS IN COMMON AND SAVE THAT AS ONE OF THE CORNER COORDINATES.
    for i in cornered_traces:
        # print i
        temp_x = None
        temp_y = None
        if i[FIRST][TOP] == i[SECOND][BOTTOM]: # common y
            temp_y = i[FIRST][TOP]
        elif i[FIRST][BOTTOM] == i[SECOND][TOP]: # common y
            temp_y = i[FIRST][BOTTOM]
        elif i[FIRST][LEFT] == i[SECOND][RIGHT]: # common x
            temp_x = i[FIRST][LEFT]
        elif i[FIRST][RIGHT] == i[SECOND][LEFT]: # common x
            temp_x = i[FIRST][RIGHT]
        # super-condition: if both x and y are blank, it's not a valid corner. if so, do not continue, else continue.
        if ((temp_x is None) and (temp_y is None)):
            continue
            # print "Invalid corner found."

        # FIND THE OTHER COORDINATE (L-JUNCTION) BY COMPARING EDGE LOCATIONS OF THE PAIR OF TRACES BEING ASSESSED
        elif temp_x is None: # Find x-coordinate of the corner
            if i[FIRST][LEFT] == i[SECOND][LEFT]: # if left side is common, select right side of the lower width box as the corner-x.
                if i[FIRST][RIGHT] < i[SECOND][RIGHT]:
                    temp_x = i[FIRST][RIGHT]
                elif i[FIRST][RIGHT] > i[SECOND][RIGHT]: # use explicit condition check here with elif to avoid phantom traces from being counted as valid.
                    temp_x = i[SECOND][RIGHT]
            elif i[FIRST][RIGHT] == i[SECOND][RIGHT]: # if right side is common, select left side of the lower width box as the corner-x.
                if i[FIRST][LEFT] > i[SECOND][LEFT]:
                    temp_x = i[FIRST][LEFT]
                elif i[FIRST][LEFT] < i[SECOND][LEFT]: # use explicit condition check here with elif to avoid phantom traces from being counted as valid.
                    temp_x = i[SECOND][LEFT]
            # print "(temp_x, temp_y): ", temp_x, temp_y
        elif temp_y is None: # Find y-coordinate of the corner
            if i[FIRST][TOP] == i[SECOND][TOP]:  # if top side is common, select bottom side of the lower height box as the corner-y.
                if i[FIRST][BOTTOM] > i[SECOND][BOTTOM]:
                    temp_y = i[FIRST][BOTTOM]
                elif i[FIRST][BOTTOM] < i[SECOND][BOTTOM]: # use explicit condition check here with elif to avoid phantom traces from being counted as valid.
                    temp_y = i[SECOND][BOTTOM]
            elif i[FIRST][BOTTOM] == i[SECOND][BOTTOM]: # if bottom side is common, select top side of the lower height box as the corner-y.
                if i[FIRST][TOP] < i[SECOND][TOP]:
                    temp_y = i[FIRST][TOP]
                elif i[FIRST][TOP] > i[SECOND][TOP]: # use explicit condition check here with elif to avoid phantom traces from being counted as valid.
                    temp_y = i[SECOND][TOP]
        if ((temp_x is not None) and (temp_y is not None)):
            corners.append((temp_x, temp_y))

        # FIND THE OTHER COORDINATE (T-JUNCTION) BY COMPARING EDGE LOCATIONS OF THE PAIR OF TRACES BEING ASSESSED
        elif temp_x is None and temp_y is not None: # if temp_x is still None (but temp_y has been found), this is a T-junction.
            if ((i[FIRST][LEFT] > i[SECOND][LEFT]) & (i[FIRST][LEFT] < i[SECOND][RIGHT])):
                temp_x = i[FIRST][LEFT]
                corners.append((temp_x, temp_y))
                if ((i[FIRST][RIGHT] > i[SECOND][LEFT]) & (i[FIRST][RIGHT] < i[SECOND][RIGHT])):
                    temp_x = i[FIRST][RIGHT]
                    corners.append((temp_x, temp_y))
            elif ((i[SECOND][LEFT] > i[FIRST][LEFT]) & (i[SECOND][LEFT] < i[FIRST][RIGHT])):
                temp_x = i[SECOND][LEFT]
                corners.append((temp_x, temp_y))
                if ((i[SECOND][RIGHT] > i[FIRST][LEFT]) & (i[SECOND][RIGHT] < i[FIRST][RIGHT])):
                    temp_x = i[SECOND][RIGHT]
                    corners.append((temp_x, temp_y))
        elif temp_y is None and temp_x is not None: # if temp_y is still None (but temp_x has been found), this is a sideways T-junction.
            if ((i[FIRST][TOP] > i[SECOND][BOTTOM]) & (i[FIRST][TOP] < i[SECOND][TOP])):
                temp_y = i[FIRST][TOP]
                corners.append((temp_x, temp_y))
                if ((i[FIRST][BOTTOM] > i[SECOND][BOTTOM]) & (i[FIRST][BOTTOM] < i[SECOND][TOP])):
                    temp_y = i[FIRST][BOTTOM]
                    corners.append((temp_x, temp_y))
            elif ((i[SECOND][TOP] > i[FIRST][BOTTOM]) & (i[SECOND][TOP] < i[FIRST][TOP])):
                temp_y = i[SECOND][TOP]
                corners.append((temp_x, temp_y))
                if ((i[SECOND][BOTTOM] > i[FIRST][BOTTOM]) & (i[SECOND][BOTTOM] < i[FIRST][TOP])):
                    temp_y = i[SECOND][BOTTOM]
                    corners.append((temp_x, temp_y))

    # OUTPUT THE CORNERS LIST AND MARK THE CORNERS (WITH A RECTANGLE CENTERED AT THE CORNER) ON THE LAYOUT PREVIEW AND SOLUTION WINDOW
    print "Corners: "
    for i in corners:
        print i
        r = Rectangle((i[0]-0.5, i[1]-0.5), 1, 1, facecolor='#E6E6E6', edgecolor='#FF3339') # draw a rectangle to mark the corner
        ax.add_patch(r)

    return corners, supertraces

    # for i in all_traces_list: # for each rectangle
    #     for j in all_traces_list:  # for each other rectangle
    #         if j == i:
    #             continue
    #         else:
    #             for k in i:  # for each edge of the first rectangle
    #                 for l in j:  # for each edge in the other rectangle
    #                     print "(i, j, k, l): ", (i, j, k, l)



    # print "sym_layout.corners: ", sym_layout.corners
    # for i in sym_layout.corners:
    #     r = Rectangle(i, 1, 1, facecolor='#E6E6E6', edgecolor='#f44259')
    #     ax.add_patch(r)

    # ------ sxm end test block (Mark corner) ------------

    #sxm - add corner markers
    # c1 = Corner(7,10)
    # sym_layout.corners.append(c1)
    # c2 = Corner(6,21)
    # sym_layout.corners.append(c2)
    # for corner in sym_layout.corners:
    #     r = Rect(corner.y+0.5, corner.y-0.5, corner.x-0.5, corner.x+0.5) # populate corners in SymbolicLayout class
    #     ax.add_patch(r)

    #sxm - test2 - add corner markers as tuple coordinates instead of Corner objects
    # c1 = (7,10)
    # sym_layout.corners.append(c1)
    # c2 = (6,21)
    # sym_layout.corners.append(c2)
    # for corner in sym_layout.corners:
    #     r = Rect(corner[1]+0.5, corner[1]-0.5, corner[0]-0.5, corner[0]+0.5) # populate corners in SymbolicLayout class
    #     ax.add_patch(r)

def detect_corners_270(sym_layout2, ax, innerCorners, supertraces):
    '''ADJACENT CORNER DETECTION
    @author: Shilpi Mukherjee
    @date: 15-JUN-2017
    This function detects 270 degree outer trace corners for a selected solution layout.
    It marks corners as a blue rectangle in the layout preview and saved solution window,
    and displays the (x,y) coordinates of each corner in the console.
    :param sym_layout: Symbolic Layout object
    :param ax: subplot specifications
    :param innerCorners: list of 90 degree inner corners'''

    # FIRST, FIND AND ISOLATE THE PHANTOM TRACES
    phantomSupertraces = []
    print "supertraces (including phantoms):"
    for i in supertraces:
        print i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right
    for i in supertraces:
        for j in supertraces:
            if i is not j:
                if j.trace_rect.top <= i.trace_rect.top and j.trace_rect.bottom >= i.trace_rect.bottom and j.trace_rect.left >= i.trace_rect.left and j.trace_rect.right <= i.trace_rect.right:
                    phantomSupertraces.append(j)
                    supertraces.remove(j)
    print "supertraces (excluding phantoms):"
    for i in supertraces:
        print i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right
    print "phantoms:"
    for i in phantomSupertraces:
        print i.trace_rect.top, i.trace_rect.bottom, i.trace_rect.left, i.trace_rect.right

    # REMOVE THE PHANTOM TRACES FROM ALL_TRACE_LINES
    print "len(sym_layout2.all_trace_lines) before removing phantoms:", len(sym_layout2.all_trace_lines)
    for i in phantomSupertraces:
        sym_layout2.all_trace_lines.remove(i)
    print "len(sym_layout2.all_trace_lines) after:", len(sym_layout2.all_trace_lines)

    # THEN, FIND AND LIST ALL THE 270 DEGREE CORNERS ON THE LAYOUT
    corners_270 = []
    print "Corners_270:"
    for i in sym_layout2.all_trace_lines:
        tempCorner1 = (round(i.trace_rect.left,2), round(i.trace_rect.top,2))
        tempCorner2 = (round(i.trace_rect.right,2), round(i.trace_rect.top,2))
        tempCorner3 = (round(i.trace_rect.left, 2), round(i.trace_rect.bottom, 2))
        tempCorner4 = (round(i.trace_rect.right, 2), round(i.trace_rect.bottom, 2))
        if tempCorner1 not in innerCorners:
            if tempCorner1 in corners_270:
                corners_270.remove(tempCorner1)
            else:
                corners_270.append(tempCorner1)
                print tempCorner1
        if tempCorner2 not in innerCorners:
            if tempCorner2 in corners_270:
                corners_270.remove(tempCorner2)
            else:
                corners_270.append(tempCorner2)
                print tempCorner2
        if tempCorner3 not in innerCorners:
            if tempCorner3 in corners_270:
                corners_270.remove(tempCorner3)
            else:
                corners_270.append(tempCorner3)
                print tempCorner3
        if tempCorner4 not in innerCorners:
            if tempCorner4 in corners_270:
                corners_270.remove(tempCorner4)
            else:
                corners_270.append(tempCorner4)
                print tempCorner4

    # MARK THE CORNERS WITH BLUE RECTANGLES
    for i in corners_270:
        r = Rectangle((i[0] - 0.5, i[1] - 0.5), 1, 1, facecolor='#E6E6E6', edgecolor='#3339FF')  # draw a rectangle to mark the corner
        ax.add_patch(r)

# test Jun 15, 2017