'''
Created on Dec 23, 2012

@author: shook
'''

import xml.dom.minidom as xml

from powercad.util import Rect
from matplotlib.pyplot import plot

class LayoutError(Exception):
    def __init__(self, msg):
        self.args = [msg]

class LayoutLine(object):
    def __init__(self, path_id, pt1, pt2, vertical):
        self.path_id = path_id
        self.pt1 = pt1
        self.pt2 = pt2
        self.vertical = vertical #sxm - get rid of this attribute OR see next line
        #self.orientation = "vertical"/"horizontal"/"positive_slope"/"negative_slope" 
        
class LayoutPoint(object):
    def __init__(self, path_id, pt):
        self.path_id = path_id
        self.pt = pt

def load_svg(svg_path):
    print "load_svg() started"
    f = open(svg_path, 'r')
    dom = xml.parse(f) # sxm - document object model
    print dom #sxm
    '''
    1. Build up list of path objects
    2. Apply transforms to path objects
    3. Build up list of line segs, circles, and rects
    '''
    
    # Build up set of path objects
    path_trans_dict = {}
    paths = dom.getElementsByTagName("path")
    print "paths: ", paths #sxm
    # for every path, create a dictionary with paths as keys, and values empty (to be populated later).
    for path in paths:
        path_trans_dict[path] = []
    
    # Deal with groups and transformations
    groups = dom.getElementsByTagName("g")
    print "groups: ", groups #sxm
    for group in groups:
        trans_tuple = get_translation(group)
    
        if trans_tuple is not None:
            # Go through each path element in the group element and add the transformation to the dictionary at the right path key
            ele_paths = group.getElementsByTagName("path")
            for path in ele_paths:
                path_trans_dict[path].append(trans_tuple)
    print "path_trans_dict[]", path_trans_dict #sxm
    
    # start building layout
    layout = []
    for path in path_trans_dict:
        trans_list = path_trans_dict[path]        
        # Get path's local translation
        trans = get_translation(path)
        if trans is not None:
            trans_list.append(trans)        
        objs = handle_circle(path, trans_list)        
        if len(objs) <= 0:
            # Object may be a series of line paths
            objs = handle_linepath(path, trans_list)            
        if len(objs) > 0:
            for t in objs:
                layout.append(t)
    print "layout", layout #sxm
                
    # Check if anything was loaded in layout       
    if len(layout) < 1:
        raise LayoutError("No layout objects were loaded! (Blank layout)")
                
    # Normalize and return the layout #sxm- you are not actually normalizing it here.
    print "load_svg() completed."
    return layout

def get_translation(ele):
    print "get_translation() started"
    trans_tuple = None
    try:
        trans = ele.attributes["transform"]
        print "trans:", trans
        trans_lc = trans.value.lower()
        print "trans.value:", trans.value
        print "trans_lc:", trans_lc
        print "trans_lc.count():", trans_lc.count('translate')
        
        if trans_lc.count('rotate') > 0:
            raise Exception('SVG Rotation not supported!')
        elif trans_lc.count('scale') > 0:
            raise Exception('SVG Scaling not supported!')
        elif trans_lc.count('matrix') > 0:
            raise Exception('SVG Matrix not supported!')
        elif trans_lc.count('translate') > 1:
            raise Exception('Multiple SVG Translations not supported!')
        
        if trans_lc.count('translate') > 0:
            lp = trans_lc.find('(') #left parenthesis
            rp = trans_lc.find(')') #right parenthesis
            nums = trans_lc[lp+1:rp].split(',')
            trans_tuple = (float(nums[0]), float(nums[1]))
    except KeyError:
        # group has no transform
        pass
    
    print "get_translation() completed."
    return trans_tuple

def normalize_layout(layout, tol): #done
    print "normalize_layout() started"
    xlist = []
    ylist = []
    
    # Build Coord Lists #sxm - this is independent of line orientation
    for obj in layout:
        if isinstance(obj, LayoutLine):
            xlist.append(obj.pt1[0])
            ylist.append(obj.pt1[1])
            xlist.append(obj.pt2[0])
            ylist.append(obj.pt2[1])
        elif isinstance(obj, LayoutPoint):
            xlist.append(obj.pt[0])
            ylist.append(obj.pt[1])
    
    # sxm - sort all x-coordinates and y-coordinates to ease normalization process (needs ordered list)    
    xlist.sort()
    ylist.sort()
    print "xlist", xlist
    print "ylist", ylist
    
    # Organize Lists in dicts of normalized coordinate points (dict key = original coordinate, dict value = normalized coordinate)
    xlen, xdict = norm_dict(xlist, tol)
    ylen, ydict = norm_dict(ylist, tol)
    
    # sxm - convert every line/point from original coordinates to normalized coordinates    
    for obj in layout:
        if isinstance(obj, LayoutLine):
            x0 = xdict[obj.pt1[0]]
            y0 = ydict[obj.pt1[1]]
            x1 = xdict[obj.pt2[0]]
            y1 = ydict[obj.pt2[1]]
            
            obj.pt1 = (x0, y0)
            obj.pt2 = (x1, y1)
        elif isinstance(obj, LayoutPoint):
            x0 = xdict[obj.pt[0]]
            y0 = ydict[obj.pt[1]]
            obj.pt = (x0, y0)
    
    # sxm - increment length of graph to leave room for margin        
    xlen = xlen+1 
    ylen = ylen+1
    print "normalize_layout() completed."
    return xlen, ylen

def find_layout_bounds(layout):
    print "find_layout_bounds() started"
    print "sxm debug"
    print layout
    print layout[0]
    xlist = []
    ylist = []
    
    for obj in layout:
        print obj
        if isinstance(obj, LayoutLine):
            print "line"
            xlist.append(obj.pt1[0])
            ylist.append(obj.pt1[1])
            xlist.append(obj.pt2[0])
            ylist.append(obj.pt2[1])
            print "corner 1: ", obj.pt1[0], obj.pt1[2], "corner 2: ", obj.pt2[0], obj.pt2[1] #sxm
            print "directory:", obj.dir() #sxm
        elif isinstance(obj, LayoutPoint):
            print "point"
            xlist.append(obj.pt[0])
            print xlist #sxm
            ylist.append(obj.pt[1])
            print ylist #sxm
            
    xlist.sort()
    ylist.sort()
    print xlist
    print ylist
    print "find_layout_bounds() completed."
    return ylist[-1], ylist[0], xlist[0], xlist[-1]

def get_id(ele):
    print "get_id() started"
    try:
        path_id = ele.attributes["id"].value
        return path_id
    except:
        raise Exception('Path object has no id!')
    print "get_id() completed."
    
def translate_circle(trans_list, cxy):
    print "translate_circle() started"
    tx = cxy[0]
    ty = cxy[1]
    
    for trans in trans_list:
        tx += trans[0]
        ty += trans[1]
    
    print "translate_circle() completed."
    return invert_y((tx,ty))

def handle_circle(path, trans_list):
    print "handle_circle() started"
    try:
        path_type = path.attributes["sodipodi:type"].value
        if path_type == 'arc':
            try:
                cx = float(path.attributes["sodipodi:cx"].value)
                cy = float(path.attributes["sodipodi:cy"].value)
                cxy = translate_circle(trans_list, (cx, cy))
                
                path_id = get_id(path)
                pt_obj = LayoutPoint(path_id, cxy)
                print "handle_circle() completed."
                return [pt_obj]
            except KeyError:
                raise Exception('Failed to retrieve arc\'s center!')
    except KeyError:
        # this isn't a circle
        print "handle_circle() completed."
        return []

def translate_pt(pt, trans_list):
    print "translate_pt() started"
    #print 'pt:'
    for trans in trans_list:
        pt = (pt[0] + trans[0], pt[1] + trans[1])
    
    print "translate_pt() completed."    
    return pt

def invert_y(xy):
    print "invert_y() started"
    print "invert_y() completed."
    return (xy[0], -xy[1])

def org_line(pt1, pt2):
    print "org_line() started"
    vertical = True
    if pt1[0] == pt2[0]:
        vertical = True
    elif pt1[1] == pt2[1]:
        vertical = False
    else:
        raise Exception('Only Manhattan line types supported!')
    
    if vertical:
        t0 = pt1[1]
        t1 = pt2[1]
    else:
        t0 = pt1[0]
        t1 = pt2[0]
    
    # always go from lower to higher point
    if t0 > t1:
        tmp = t1
        t1 = t0
        t0 = tmp
    
    if vertical:
        npt1 = (pt1[0], t0)
        npt2 = (pt2[0], t1)
    else:
        npt1 = (t0, pt1[1])
        npt2 = (t1, pt1[1])
        
    print "org_line() completed."
    return npt1,npt2,vertical

def handle_linepath(path, trans_list): #sxm- returns the end points of a line and its path id as a LayoutLine object.
    print "handle_linepath() started"
    objs = []
    
    path_id = get_id(path)
    
    try:
        d = path.attributes["d"].value
        
        pts = []
        for g in d.split(' '):
            if len(g) > 1:
                pt_str = g.split(',') # sxm - point string in the form x,y
                pts.append((float(pt_str[0]), float(pt_str[1]))) # sxm - separate x and y coordinates and save them both in pts[] list.
        print "pts:", pts #sxm
        rel = True
        if d.count('m') == 1:
            rel = True
        elif d.count('M') == 1:
            rel = False
        elif d.count('m') > 1 or d.count('M') > 1:
            raise Exception('No support for multiple moves within draw command!')
        
        if d.count('c') > 0 or d.count('C') > 0:
            raise Exception('No support for curved paths!')
        
        if d.count('z') > 0 or d.count('Z') > 0:
            raise Exception('No support for closed line paths!') #sxm - closed line path is an area; 2D areas are not supported. Only 0D points and 1D lines are. 

        last_pt = translate_pt(pts[0], trans_list)
        print "last_pt", last_pt #sxm
        for pt in pts[1:]:
            if rel:
                tpt = (last_pt[0] + pt[0], last_pt[1] + pt[1])
            else:
                tpt = translate_pt(pt, trans_list)
            print "tpt", tpt
                
            pt1, pt2, vert = org_line(invert_y(last_pt), invert_y(tpt))
            print "pt1=", pt1, "pt2=", pt2, "vertical?", vert #sxm 
            line_obj = LayoutLine(path_id, pt1, pt2, vert) #sxm - to do - find out if/how pt1,pt2,vert special case is used. 
            objs.append(line_obj)
            last_pt = tpt
        print "new last_pt", last_pt #sxm
        print objs #sxm
        print "handle_linepath() completed."    
        return objs
    except KeyError:
        raise Exception('Path object has no drawing information!')

def norm_dict(clist, tol):
    print "norm_dict() started"
    cdict = {}
    
    last_c = clist[0] # sxm - point to the first element in the list
    cdict[last_c] = 0 # sxm - value for the first element is zero (normalized graph starts at zero).
    inc = 0 # sxm - start at coordinate = 0 for the normalized graph. 
    for c in clist[1:]: # thenceforth, for every element in the list:
        if c == last_c or (c > last_c-tol and c < last_c+tol): # sxm - if current element is exactly equal to or close enough to the last element,
            if c != last_c: # sxm - if current key is 'exactly' equal to the last element,
                cdict[c] = inc # sxm - add the new element as a key in the dictionary with value same as that of the previous element's.
        else: # sxm - if current element is significantly different from the previous element,
            inc += 1 # sxm - increment the value to be stored for new element in the dictionary (next unit of the normalized graph)
            cdict[c] = inc # sxm - add the new key with new normalized value (which is 1 + previous value)       
        last_c = c # sxm - point to the next element
        
    print "norm_dict() completed."
    return (inc, cdict) # Return the dictionary of original and normalized numbers along with the last normalized number.

# sxm - compares every layoutline object with every other layoutline object to see if they overlap; same for points.
def check_for_overlap(layout): #sxm Not all svg files have lines/paths labeled as pow_bw or sig_bw. This needs to be fixed without asking user to rename the path_id.
    print "check_for_overlap() started"
    for obj1 in layout:
        for obj2 in layout:
            if not(obj1 is obj2):
                if isinstance(obj1, LayoutLine)and \
                   isinstance(obj2, LayoutLine):
                    # exception for overlap check: if a line is a bondwire. Note: path_id must be edited in inkscape xml file so that overlapping bondwires can be allowed.
                    if ('pow_bw' not in obj1.path_id) and ('sig_bw' not in obj1.path_id) and \
                       ('pow_bw' not in obj2.path_id) and ('sig_bw' not in obj2.path_id):
                        check_line_overlap(obj1, obj2)
                if isinstance(obj1, LayoutPoint)and \
                   isinstance(obj2, LayoutPoint):
                    check_pt_overlapt(obj1, obj2)
    print "check_for_overlap() completed."
                    
# dummy function (instead of the real one below) incorporated so that signal bondwire overlaps can be OKAYed.
# sxm - But this would also OKAY trace overlaps.
def check_line_overlap(obj1, obj2):
    pass
# Commented to allow signal bondwire overlap.
# def check_line_overlap(obj1, obj2): #sxm This can be generalized for skew lines.  
#     print "check_line_overlap() started"
#     if obj1.vertical and obj2.vertical and obj1.pt1[0] == obj2.pt1[0]:
#         if (obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1]) or \
#         (obj2.pt2[1] > obj1.pt1[1] and obj2.pt2[1] < obj1.pt2[1]):
#             raise LayoutError('Overlapping vertical lines found!')
#     elif (not obj1.vertical) and (not obj2.vertical) and obj1.pt1[1] == obj2.pt1[1]:
#         if (obj2.pt1[0] > obj1.pt1[0] and obj2.pt1[0] < obj1.pt2[0]) or \
#         (obj2.pt2[0] > obj1.pt1[0] and obj2.pt2[0] < obj1.pt2[0]):
#             raise LayoutError('Overlapping horizontal lines found!')
#     print "check_line_overlap() completed."
                
        
def check_pt_overlapt(obj1, obj2):
    print "check_pt_overlapt() started"
    if obj1.pt[0] == obj2.pt[0] and obj1.pt[1] == obj2.pt[1]:
        raise LayoutError('Overlapping points found!')
    print "check_pt_overlapt() completed."

if __name__ == '__main__':
    import matplotlib
    from powercad.sym_layout.plot import plot_svg_objs
    #from powercad.sym_layout.svg import load_svg, normalize_layout
    layout = load_svg('../../../sym_layouts/simple.svg')
    normalize_layout(layout, 0.001)
    matplotlib.rc('font', family="Times New Roman", size=24)
    plot_svg_objs(layout)
    