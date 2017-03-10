'''
Created on Dec 23, 2012

@author: shook
'''

import xml.dom.minidom as xml
import ctypes
from powercad.util import Rect
from matplotlib.pyplot import plot

class LayoutError(Exception):
    def __init__(self, msg):
        ctypes.windll.user32.MessageBoxA(0, msg, "Layout Error", 1)    # Open a Message Box to notify users about the error
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
# Quang: testing input rectangle
class LayoutRect(object):
    def __init__(self,path_id,pt, w, l):
        # Constructor: pt: the left high corner point of a rectangle
        #              w, l: width and length of the rectangle  
        self.path_id=path_id
        self.pt = pt
        self.w = w 
        self.l = l 
        
def load_script(sript_path):
    # qmle added 10-18-2016
    # A specific script language for PS layout:
    #    To specify a line: ID l pos1 pos2
    #    To specify a point ID p pos
    # The script is written in text form or specified by .psc (powersynth script code) 
    layout=[]    # layout is a set of LayoutLines and LayoutPoints
    print sript_path
    with open(sript_path, 'rb') as f: # open the directory of script code
        print f
        objs=[]                      # specified a list of objs (lines and points)
        for line in f:               # read every line of the script 
            if line[0]=='#' or line[0]=='': # check for comments or blank lines
                x=1                         # do nothing if so
            else:                           # in case a line contains layout information
                path_id=line[0:3]           # load path_id
                type=line[5]                # check for layout type (line: l vs point: p)
                if type =='l':              # in case it is a line
                    line_str=line[7:len(line)] # read the layout information
                    dat1,dat2=line_str.split(' ')   # split out 2 points positions
                    dat1=dat1.split('(')[1]         # split out the open bracket
                    dat1=dat1.split(')')[0]         # split out the close bracket
                    x1,y1= dat1.split(',')          # split out string information of position
                    pt1=(float(x1),float(y1))       # convert to float data type
                    dat2=dat2.split('(')[1]         # split out the open bracket
                    dat2=dat2.split(')')[0]         # split out the close bracket
                    x2,y2= dat2.split(',')          # split out string information of position
                    pt2=(float(x2),float(y2))       # convert to float data type
                    if pt1[0]==pt2[0]:              # check if the line is vertical (manhattan style)
                        vert = True                 # set vertical = True
                    elif pt1[1]==pt2[1]:            # check if the line is horizontal (manhattan style)
                        vert = False                # set vertical = True
                    else:                           # Non-Manhattan will be implemented later
                        LayoutError('non-manhattan will be added later')    
                    objs.append(LayoutLine(path_id,pt1,pt2,vert)) # add obj to layout list
                elif type=='p':                     # in case this is a point
                    dat1=line[7:len(line)]          # read the layout information
                    dat1=dat1.split('(')[1]         # split out the open bracket
                    dat1=dat1.split(')')[0]         # split out the close bracket
                    x1,y1= dat1.split(',')          # split out string information of position
                    pt=(float(x1),float(y1))        # convert to float data type
                    objs.append(LayoutPoint(path_id,pt))  # add obj to layout list
    if len(objs) > 0:                               # If there are objs in layout list
            for t in objs:
                layout.append(t)                    # append obj to layout
    print layout
    return layout                                   # return layout
              
                
def load_svg(svg_path):
    f = open(svg_path, 'r')
    dom = xml.parse(f) # sxm - document object model
    
    '''
    1. Build up list of path objects
    2. Apply transforms to path objects
    3. Build up list of line segs, circles, and rects
    '''
    
    # Build up set of path objects
    path_trans_dict = {}
    paths = dom.getElementsByTagName("path")
    # for every path, create a dictionary with paths as keys, and values empty (to be populated later).
    for path in paths:
        path_trans_dict[path] = []
    
    # Deal with groups and transformations
    groups = dom.getElementsByTagName("g")
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
                
    # Check if anything was loaded         
    if len(layout) < 1:
        raise LayoutError("No layout objects were loaded! (Blank layout)")
                
    # Normalize and return the layout #sxm- you are not actually normalizing it here.
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
    # This method will take the scaleable vector graphic files and normalize its coordinate  
    xlist = [] # Initialize a blank list
    ylist = [] # Initialize a blank list
    
    # Build Coord Lists
    for obj in layout:                  # Read through all objects in SVG   
        if isinstance(obj, LayoutLine): # if this is a SVG Line
            xlist.append(obj.pt1[0])    # add Line's End Point X value to the list
            ylist.append(obj.pt1[1])    # add Line's End Point Y value to the list
            xlist.append(obj.pt2[0])    # add Line's End Point X value to the list
            ylist.append(obj.pt2[1])    # add Line's End Point Y value to the list
        elif isinstance(obj, LayoutPoint):
            xlist.append(obj.pt[0])     # add Point's X value to the list
            ylist.append(obj.pt[1])     # add Point's Y value to the list
    # Now when we have a list of coordinate values we want to sort them so they will be in right order    
    xlist.sort()                        # sort the X values (from low to high) https://wiki.python.org/moin/HowTo/Sorting
    ylist.sort()                        # sort the Y values (from low to high) https://wiki.python.org/moin/HowTo/Sorting
    
    # Organize Lists in dicts
    xlen, xdict = norm_dict(xlist, tol) # report the dictionary of normalized coordinate as well as its length
    ylen, ydict = norm_dict(ylist, tol) # report the dictionary of normalized coordinate as well as its length
    
    # sxm - convert every line/point from original coordinates to normalized coordinates    
    for obj in layout:
        
        if isinstance(obj, LayoutLine): # Read through all objects in SVG again
            print obj.pt1
            x0 = xdict[obj.pt1[0]]      #
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
                print 'pt_obj ', pt_obj
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

def handle_linepath(path, trans_list): #sxm- returns the end points of a line and its path id as a LayoutLine object.
    objs = []
    
    path_id = get_id(path)
    
    try:
        d = path.attributes["d"].value
        
        pts = []
        for g in d.split(' '):
            if len(g) > 1:
                pt_str = g.split(',') # sxm - point string in the form x,y
                pts.append((float(pt_str[0]), float(pt_str[1]))) # sxm - separate x and y coordinates and save them both in pts[] list.
        
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
        for pt in pts[1:]:
            if rel:
                tpt = (last_pt[0] + pt[0], last_pt[1] + pt[1])
            else:
                tpt = translate_pt(pt, trans_list)
                
            pt1, pt2, vert = org_line(invert_y(last_pt), invert_y(tpt))
            line_obj = LayoutLine(path_id, pt1, pt2, vert) #sxm - to do - find out if/how pt1,pt2,vert special case is used. 
            objs.append(line_obj)
            last_pt = tpt
            
        return objs
    except KeyError:
        raise Exception('Path object has no drawing information!')

def norm_dict(clist, tol):
    # To coders: in order to understand this, go to powercad> sym_layout > symbolic_layout and run the main fucntion.. This will load rd100.svg saved in CVS
    # Now open rd100.svg.. look at the picture and at the same time printing out the variables in the for loop e.g: c, last_c, Now try to count the number of coordinates 
    # on the picture and compare to the print results... you should understand how this work. -- Quang  
    cdict = {}            # coordinate dictionary
    last_c = clist[0]     # take last coordinate
    cdict[last_c] = 0     # initialize it to 0 again
    inc = 0               # initialize the counter
    for c in clist[1:]:
        if (c > last_c-tol and c < last_c+tol):  # Here c==last_c is not necessary
            if c != last_c:
                cdict[c] = inc                   # if not the first coordinate then update the counter. increase of last coordinate counter==0
        else:
            inc += 1                             # update the counter
            cdict[c] = inc                       # use this as the normalized value
            
        last_c = c                               # move to the next coordinate and continue the normalization
    
    print 'cdict', cdict    
    return (inc, cdict)                          # return the counter value as well as the normalized values

def check_for_overlap(layout):
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
    #plot_svg_objs(layout)
    