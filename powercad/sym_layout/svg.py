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
        self.vertical = vertical
        
class LayoutPoint(object):
    def __init__(self, path_id, pt):
        self.path_id = path_id
        self.pt = pt

def load_svg(svg_path):
    f = open(svg_path, 'r')
    dom = xml.parse(f)
    
    '''
    1. Build up list of path objects
    2. Apply transforms to path objects
    3. Build up list of line segs, circles, and rects
    '''
    
    # Build up set of path objects
    path_trans_dict = {}
    paths = dom.getElementsByTagName("path")
    for path in paths:
        path_trans_dict[path] = []
    
    # Deal with groups and transformations
    groups = dom.getElementsByTagName("g")
    for group in groups:
        trans_tuple = get_translation(group)
    
        if trans_tuple is not None:
            # Go through each path element in the group element and add the transformation
            ele_paths = group.getElementsByTagName("path")
            for path in ele_paths:
                path_trans_dict[path].append(trans_tuple)
    
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
                
    # Check if anything was loaded         
    if len(layout) < 1:
        raise LayoutError("No layout objects were loaded! (Blank layout)")
                
    # Normalize and check the layout
    return layout

def get_translation(ele):
    trans_tuple = None
    try:
        trans = ele.attributes["transform"]
        trans_lc = trans.value.lower()
        
        if trans_lc.count('rotate') > 0:
            raise Exception('SVG Rotation not supported!')
        elif trans_lc.count('scale') > 0:
            raise Exception('SVG Scaling not supported!')
        elif trans_lc.count('matrix') > 0:
            raise Exception('SVG Matrix not supported!')
        elif trans_lc.count('translate') > 1:
            raise Exception('Multiple SVG Translations not supported!')
        
        if trans_lc.count('translate') > 0:
            lp = trans_lc.find('(')
            rp = trans_lc.find(')')
            nums = trans_lc[lp+1:rp].split(',')
            trans_tuple = (float(nums[0]), float(nums[1]))
    except KeyError:
        # group has no transform
        pass
    
    return trans_tuple

def normalize_layout(layout, tol):
    xlist = []
    ylist = []
    
    # Build Coord Lists
    for obj in layout:
        if isinstance(obj, LayoutLine):
            xlist.append(obj.pt1[0])
            ylist.append(obj.pt1[1])
            xlist.append(obj.pt2[0])
            ylist.append(obj.pt2[1])
        elif isinstance(obj, LayoutPoint):
            xlist.append(obj.pt[0])
            ylist.append(obj.pt[1])
        
    xlist.sort()
    ylist.sort()
    
    # Organize Lists in dicts
    xlen, xdict = norm_dict(xlist, tol)
    ylen, ydict = norm_dict(ylist, tol)
    
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
            
    xlen = xlen+1
    ylen = ylen+1
    
    return xlen, ylen

def find_layout_bounds(layout):
    xlist = []
    ylist = []
    
    for obj in layout:
        if isinstance(obj, LayoutLine):
            xlist.append(obj.pt1[0])
            ylist.append(obj.pt1[1])
            xlist.append(obj.pt2[0])
            ylist.append(obj.pt2[1])
        elif isinstance(obj, LayoutPoint):
            xlist.append(obj.pt[0])
            ylist.append(obj.pt[1])
            
    xlist.sort()
    ylist.sort()
    return ylist[-1], ylist[0], xlist[0], xlist[-1]

def get_id(ele):
    try:
        path_id = ele.attributes["id"].value
        return path_id
    except:
        raise Exception('Path object has no id!')
    
def translate_circle(trans_list, cxy):
    tx = cxy[0]
    ty = cxy[1]
    
    for trans in trans_list:
        tx += trans[0]
        ty += trans[1]
    
    return invert_y((tx,ty))

def handle_circle(path, trans_list):
    try:
        path_type = path.attributes["sodipodi:type"].value
        if path_type == 'arc':
            try:
                cx = float(path.attributes["sodipodi:cx"].value)
                cy = float(path.attributes["sodipodi:cy"].value)
                cxy = translate_circle(trans_list, (cx, cy))
                
                path_id = get_id(path)
                pt_obj = LayoutPoint(path_id, cxy)
                return [pt_obj]
            except KeyError:
                raise Exception('Failed to retrieve arc\'s center!')
    except KeyError:
        # this isn't a circle
        return []

def translate_pt(pt, trans_list):
    for trans in trans_list:
        pt = (pt[0] + trans[0], pt[1] + trans[1])
        
    return pt

def invert_y(xy):
    return (xy[0], -xy[1])

def org_line(pt1, pt2):
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
        
    return npt1,npt2,vertical

def handle_linepath(path, trans_list):
    objs = []
    
    path_id = get_id(path)
    
    try:
        d = path.attributes["d"].value
        
        pts = []
        for g in d.split(' '):
            if len(g) > 1:
                pt_str = g.split(',')
                pts.append((float(pt_str[0]), float(pt_str[1])))
        
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
            raise Exception('No support for closed line paths!')
        
        last_pt = translate_pt(pts[0], trans_list)
        for pt in pts[1:]:
            if rel:
                tpt = (last_pt[0] + pt[0], last_pt[1] + pt[1])
            else:
                tpt = translate_pt(pt, trans_list)
                
            pt1, pt2, vert = org_line(invert_y(last_pt), invert_y(tpt))
            line_obj = LayoutLine(path_id, pt1, pt2, vert)
            objs.append(line_obj)
            last_pt = tpt
            
        return objs
    except KeyError:
        raise Exception('Path object has no drawing information!')

def norm_dict(clist, tol):
    cdict = {}
    
    last_c = clist[0]
    cdict[last_c] = 0
    inc = 0
    for c in clist[1:]:
        if c == last_c or (c > last_c-tol and c < last_c+tol):
            if c != last_c:
                cdict[c] = inc
        else:
            inc += 1
            cdict[c] = inc
            
        last_c = c
        
    return (inc, cdict)

def check_for_overlap(layout):
    for obj1 in layout:
        for obj2 in layout:
            if not(obj1 is obj2):
                if isinstance(obj1, LayoutLine)and \
                   isinstance(obj2, LayoutLine):
                    # exception for overlap check: if a line is a bondwire.
                    if ('pow_bw' not in obj1.path_id) and ('sig_bw' not in obj1.path_id) and \
                       ('pow_bw' not in obj2.path_id) and ('sig_bw' not in obj2.path_id):
                        check_line_overlap(obj1, obj2)
                if isinstance(obj1, LayoutPoint)and \
                   isinstance(obj2, LayoutPoint):
                    check_pt_overlapt(obj1, obj2)
                    
def check_line_overlap(obj1, obj2):
    if obj1.vertical and obj2.vertical and obj1.pt1[0] == obj2.pt1[0]:
        if (obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1]) or \
        (obj2.pt2[1] > obj1.pt1[1] and obj2.pt2[1] < obj1.pt2[1]):
            raise LayoutError('Overlapping vertical lines found!')
    elif (not obj1.vertical) and (not obj2.vertical) and obj1.pt1[1] == obj2.pt1[1]:
        if (obj2.pt1[0] > obj1.pt1[0] and obj2.pt1[0] < obj1.pt2[0]) or \
        (obj2.pt2[0] > obj1.pt1[0] and obj2.pt2[0] < obj1.pt2[0]):
            raise LayoutError('Overlapping horizontal lines found!')
                
        
def check_pt_overlapt(obj1, obj2):
    if obj1.pt[0] == obj2.pt[0] and obj1.pt[1] == obj2.pt[1]:
        raise LayoutError('Overlapping points found!')

if __name__ == '__main__':
    import matplotlib
    from powercad.sym_layout.plot import plot_svg_objs
    #from powercad.sym_layout.svg import load_svg, normalize_layout
    layout = load_svg('../../../sym_layouts/simple.svg')
    normalize_layout(layout, 0.001)
    matplotlib.rc('font', family="Times New Roman", size=24)
    plot_svg_objs(layout)
    