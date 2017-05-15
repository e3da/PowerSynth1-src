'''
Created on Nov 6, 2012

@author: shook

sxm - This function is only used in svg.py's main().
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch, Circle
from matplotlib.path import Path

from powercad.sym_layout.svg import LayoutLine, LayoutPoint, find_layout_bounds
from powercad.general.util import Rect
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
    
def plot_layout(sym_layout,ax = plt.subplot('111', adjustable='box', aspect=1.0), new_window=True, plot_row_col=False):
    print "plot_layout() started."
    hlist = sym_layout.h_rowcol_list
    vlist = sym_layout.v_rowcol_list
    traces = sym_layout.all_trace_lines
    sub_dim = sym_layout.sub_dim
    '''
    print "H_LIST", hlist
    print "V_LIST", vlist
    print "Traces", traces
    print "sub_dim",sub_dim
    '''
    # Plot substrate boundary first
    sub_w, sub_l = sym_layout.module.substrate.dimensions
    ledge = sym_layout.module.substrate.ledge_width
    sub_rect = Rect(sub_l, 0.0, 0.0, sub_w)
    sub_rect.translate(-ledge, -ledge)
    r = Rectangle((sub_rect.left, sub_rect.bottom), sub_rect.width(), sub_rect.height(), facecolor='#E6E6E6', edgecolor='#616161')
    ax.add_patch(r)
    
    # Setup viewing bounds
    ax.set_xlim(sub_rect.left-1.0, sub_rect.right+1.0)
    ax.set_ylim(sub_rect.bottom-1.0, sub_rect.top+1.0)
    ax.set_axis_off()
    
    for sym in traces:
        plot = True
        if sym.is_supertrace():
            plot = sym.has_rect
            
        if plot:
            color = '#B6C2CF'
            rect = sym.trace_rect
            r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor=color, edgecolor='None')
            ax.add_patch(r)
            
    for lead in sym_layout.leads:
        rect = lead.footprint_rect
        r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor='#4DFF64', edgecolor=color)
        ax.add_patch(r)
        patch = Circle(lead.center_position, radius=0.1)
        ax.add_patch(patch)
    x_pos=[]
    y_pos=[]    
    if len(sym_layout.devices)!=0:
        for dev in sym_layout.devices:     # collect position data
            dev_center=dev.center_position
            x_pos.append(dev_center[0])
            y_pos.append(dev_center[1])
        x_num=x_pos.count(x_pos[0])
        y_num=y_pos.count(y_pos[0])

        '''
        for row in np.arange(1,x_num,1):
            print row
            print enumerate(x_pos)
        '''
        for dev in sym_layout.devices:
            #die_label='die%s'%(sym_layout.devices[die_count].dv_index)
            rect = dev.footprint_rect
            r = Rectangle((rect.left, rect.bottom), rect.width(), rect.height(), alpha=0.5, facecolor='#2A3569', edgecolor=color)
            ax.add_patch(r)
            patch = Circle(dev.center_position, radius=0.1)
            ax.add_patch(patch)
            #ax.text(rect.left, rect.bottom,die_label)
            #die_count+=1
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