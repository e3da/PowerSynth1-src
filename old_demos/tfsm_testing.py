ranc'''
Created on Sep 12, 2011

@author: bxs003
'''

import numpy as np
from tfsm import ContourRect, find_power_from_contours
from util import Rect

# die temp rect (theta)
# 4.8 2.4 49.9235

# trace top temp contours (thetas) (Avg Theta Temp = 8.1572)
# Temps: 53.8243   45.9849   38.4381   31.5119   25.1107   19.5288   13.8440    7.6656 (C)
# Widths: 3.3090    4.3216    5.1837    6.1665    7.2115    9.0645   14.1983   83.8300 (mm)
# Heights: 2.0588    2.7741    3.4895    4.5188    5.7801    8.0111   13.5568   54.6000 (mm)

# iso top temp contourheta Temp = 8.1414)
# Temps: 50.6922   43.4816   36.3508   29.9227   23.8731   18.6706   13.3880    7.6468 (C)
# Widths: 3.1684    4.3124    5.2748    6.3046    7.4724    9.4172   14.8463   83.8300 (mm)
# Heights: 1.9519    2.8056    3.6839    4.6913    6.0326    8.3259   14.2123   54.6000 (mm)

# iso top flux contours
# Flux: 1.0472    0.8459    0.6849    0.5329    0.3952    0.2616    0.1568    0.0218  (W/mm^2)
# Widths: 2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034 (mm)
# Heights: 2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231 (mm)

def build_contour_rects(values, widths, heights):
    rects = []
    for i in range(len(values)):
        rect = ContourRect(widths[i], heights[i], values[i])
        rects.append(rect)
        
    return rects

def power_test():
    # Flux captured from top of isolation
    flux = [1.0472, 0.8459, 0.6849, 0.5329, 0.3952, 0.2616, 0.1568, 0.0218] # (W/mm^2)
    widths = [2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034] # (mm)
    heights = [2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231] # (mm)
    
    flux_rects = build_contour_rects(flux, widths, heights)
    
    eff_power = find_power_from_contours(flux_rects)
    print 'Effective Area Power = ' + str(eff_power)
    
def coupling_test():
    # X -> Broad side of substrate
    # Y -> Narrow side of substrate
    
    sub_w = 83.83
    sub_h = 54.6
    sub_w2 = sub_w/2
    sub_h2 = sub_h/2
    
    # Isolation Top theta temp. dist.
    iso_top_avg_temp = 8.1414
    iso_top_temps = [50.6922, 43.4816, 36.3508, 29.9227, 23.8731, 18.6706, 13.3880, 7.6468]
    iso_top_w = [3.1684, 4.3124, 5.2748, 6.3046, 7.4724, 9.4172, 14.8463, 83.8300]
    iso_top_h = [1.9519, 2.8056, 3.6839, 4.6913, 6.0326, 8.3259, 14.2123, 54.6000]
    iso_temp_rects = build_contour_rects(iso_top_temps, iso_top_w, iso_top_h)
    
    # Trace Top theta temp. dist.
    trace_top_avg_temp = 8.1572
    trace_top_temps = [53.8243, 45.9849, 38.4381, 31.5119, 25.1107, 19.5288, 13.8440, 7.6656]
    trace_top_w = [3.1684, 4.3124, 5.2748, 6.3046, 7.4724, 9.4172, 14.8463, 83.8300]
    trace_top_h = [2.0588, 2.7741, 3.4895, 4.5188, 5.7801, 8.0111, 13.5568, 54.6000]
    trace_temp_rects = build_contour_rects(trace_top_temps, trace_top_w, trace_top_h)
    
    # Trace Rectangle
    trace_w2 = 24.0/2
    trace_h2 = 31.2/2
    #trace_w2 = sub_w2
    #trace_h2 = sub_h2
    trace_rect = Rect(trace_h2, -trace_h2, -trace_w2, trace_w2)
    
    # Die Char.
    die_bottom_temp = 49.9235 # avg theta temp
    die_w = 4.8
    die_h = 2.4
    die_a = die_w*die_h
    
    die_w2 = die_w/2
    die_h2 = die_h/2
    
    die_dist = 3.0
    print 'Die Dist = ' + str(die_dist) + ' mm'
    
    die1_x = 0.0
    die1_y = -die_dist/2
    
    die1_rect = Rect(die_h2 + die1_y, -die_h2 + die1_y, 
                     -die_w2 + die1_x, die_w2 + die1_x)
    
    die2_x = 0.0
    die2_y = die_dist/2
    
    # Comparing against die 2's temp dist
    # Usually would be all other dies
    # Find Avg Die Temp
    prev_an = 0.0
    an_sum = 0.0
    temp_avg = 0.0
    for temp_rect in trace_temp_rects:
        w2 = temp_rect.width/2
        h2 = temp_rect.height/2
        comp_rect = Rect(h2 + die2_y, -h2 + die2_y, -w2 + die2_x, w2 + die2_x)
        
        if comp_rect.intersects(die1_rect):
            inters = comp_rect.intersection(die1_rect).area()
            an = inters - prev_an
            prev_an = inters
            
            an_sum += an
            temp_avg += (die_bottom_temp + temp_rect.avg_val)*an/die_a
            
    temp_avg += (die_a - an_sum)*die_bottom_temp/die_a
    die_temp_avg = temp_avg
    
    print 'Die Bottom Avg:  ' + str(die_temp_avg+22)
    
    # Find Avg Trace Temp
    # 1. Calc Intersection of die temp dist rect (translated with the die) and trace rects (stationary) -> call this the clip rect
    # 2. Find avg temp of clip rect for iso top and trace top
    # 3. Find intersection of clip rect and contribution rect(s)
    # 4. Find new avg temp of the clip rect
    
    # Find Avg Trace Temp
    # Dies are identical, so share the same temp dist dim
    dies_xpos = [die1_x, die2_x]
    dies_ypos = [die1_y, die2_y]
    
    # Loop through all dies on this particular trace rect
    # Start from a zero avg temp
    trace_avg_temp = 0.0
    for i in range(len(dies_xpos)):
        x = dies_xpos[i]
        y = dies_ypos[i]
        
        trace_area = trace_rect.area()
        
        prev_an = 0.0
        an_sum = 0.0
        temp_avg = 0.0
        for temp_rect in trace_temp_rects:
            w2 = temp_rect.width/2
            h2 = temp_rect.height/2
            comp_rect = Rect(h2 + y, -h2 + y, -w2 + x, w2 + x)
            
            if comp_rect.intersects(trace_rect):
                inters = comp_rect.intersection(trace_rect).area()
                an = inters - prev_an
                prev_an = inters
                
                an_sum += an
                temp_avg += (trace_avg_temp + temp_rect.avg_val)*an/trace_area
                    
        temp_avg += (trace_area - an_sum)*trace_avg_temp/trace_area
        trace_avg_temp = temp_avg
    
    print 'Trace Avg Temp:  ' + str(trace_avg_temp+22)
    
    print 'Rsp1:  ' + str((die_temp_avg-trace_avg_temp)/40)
    
    # Find Avg Isolation temp
    # 1. Find intersection between substrate rect and all contrib substrate rects
    # 2. Find the new avg temp of substrate
    
    # Find Effective Power for each die
    # 1. Find the intersection of each local connected trace rect with each effective flux rect
    # 2. Find the total power flowing through this region -> this is effective power
    
    
    # ---- Separate Test (Edge Testing) ----
    
    # 1. Already know die temp (no coupling)
    # 2. Find trace temp
    # 3. Find effective power
    # 4. Calc Rsp1
    
    print '\n-----Edge Testing-----'
    
    # Trace Scaling Temperature Characterization
    ratio = [0.0025, 0.0154, 0.125, 0.25, 0.5, 0.75]
    die_scale_temp = [49.92, 49.54, 51.64, 56.38, 68.41, 81.25]
    trace_scale_temp = [8.16, 12.44, 27.93, 40.31, 59.34, 77.58]
    
    iso_top_flux = [1.0472, 0.8459, 0.6849, 0.5329, 0.3952, 0.2616, 0.1568, 0.0218]
    iso_top_flux_w = [2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034]
    iso_top_flux_h = [2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231]
    iso_top_flux_rects = build_contour_rects(iso_top_flux, iso_top_flux_w, iso_top_flux_h)
    
    p0 = 40
    ptotal = 36.6883840747
    
    edge_dist = 2.0
    print 'Edge Dist = ' + str(edge_dist)
    
    edge_die_x = -trace_w2 + die_w2 + edge_dist
    #edge_die_x = 0.0
    
    edge_die_y = -trace_h2 + die_h2 + edge_dist
    #edge_die_y = 0.0
    
    # Use trace scaling temps to find the die avg temp and trace avg temp
    dt_ratio = die_a/trace_rect.area()
    die_temp = np.interp(dt_ratio, ratio, die_scale_temp)
    trace_temp = np.interp(dt_ratio, ratio, trace_scale_temp)
    
    # Find effective power
    prev_an = 0.0
    power_sum = 0.0
    max_flux_w = iso_top_flux_rects[-1].width
    max_flux_h = iso_top_flux_rects[-1].height
    
    for flux_rect in iso_top_flux_rects:
        
        # Flux rect w and h need to be scaled to w and h of trace when scaled below effective w and h
        scaled = False
        
        #Check width
        if trace_rect.width() > flux_rect.width:
            w2 = flux_rect.width/2
        else:
            print 'Scaled Flux on X!'
            scaled = True
            w2 = flux_rect.width*(trace_rect.width()/(2*max_flux_w))
            
        # Check height    
        if trace_rect.height() > flux_rect.height:
            h2 = flux_rect.height/2
        else:
            print 'Scaled Flux on Y!'
            scaled = True
            h2 = flux_rect.height*(trace_rect.height()/(2*max_flux_h))
        
        if scaled:
            a1 = flux_rect.width*flux_rect.height
            a2 = 4*w2*h2
            area_ratio = a1/a2
        else:
            area_ratio = 1.0
        
        comp_rect = Rect(h2 + edge_die_y, -h2 + edge_die_y, -w2 + edge_die_x, w2 + edge_die_x)
        
        if comp_rect.intersects(trace_rect):
            inters = comp_rect.intersection(trace_rect).area()
            an = inters - prev_an
            prev_an = inters
            power_sum += an*(area_ratio*flux_rect.avg_val)
            
    pe = (power_sum/ptotal)*p0
    print "Eff. Power = " + str(pe)
    rsp0 = (die_temp - trace_temp)/p0
    rsp1 = rsp0*p0/pe
    
    print 'Die Bot Avg = ' + str(die_temp+22)
    print 'Trace Avg = ' + str(trace_temp+22)
            
    print 'Rsp0 = ' + str(rsp0)
    print 'Rsp1 = ' + str(rsp1)
    
def separated_coupling():
    
    # Flux through Isolation Top
    iso_top_flux = [1.0472, 0.8459, 0.6849, 0.5329, 0.3952, 0.2616, 0.1568, 0.0218]
    iso_top_flux_w = [2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034]
    iso_top_flux_h = [2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231]
    iso_top_flux_rects = build_contour_rects(iso_top_flux, iso_top_flux_w, iso_top_flux_h)
    
    p0 = 40
    ptotal = 36.6883840747
    
    # Trace Top theta temp. dist.
    trace_top_temps = [53.8243, 45.9849, 38.4381, 31.5119, 25.1107, 19.5288, 13.8440, 7.6656]
    trace_top_w = [3.1684, 4.3124, 5.2748, 6.3046, 7.4724, 9.4172, 14.8463, 83.8300]
    trace_top_h = [2.0588, 2.7741, 3.4895, 4.5188, 5.7801, 8.0111, 13.5568, 54.6000]
    trace_temp_rects = build_contour_rects(trace_top_temps, trace_top_w, trace_top_h)
    
    # Die Geometry
    die_w = 4.8
    die_h = 2.4
    die_a = die_w*die_h
    die_w2 = die_w/2
    die_h2 = die_h/2
    
    die1_x = 2.4
    die1_y = 3.2
    die1_rect = Rect(die_h2, -die_h2, -die_w2, die_w2)
    die1_rect.translate(die1_x, die1_y)
    
    die2_x = 14.0
    die2_y = 11.0
    die2_rect = Rect(die_h2, -die_h2, -die_w2, die_w2)
    die2_rect.translate(die2_x, die2_y)
    
    #die_rects = [die1_rect, die2_rect]
    
    # Isolation with one die (theta)
    iso_top_avg_temp = 8.1414
    
    # Check for trace intersections (Add this later for error checking)
    # trace rects
    trace_left = Rect(20.0, 0.0, 0.0, 8.0)
    trace_mid = Rect(8.0, 0.0, 8.0, 10.0)
    trace_right = Rect(20.0, 0.0, 10.0, 18.0)
    trace_rects = [trace_left, trace_mid, trace_right]
    
    #------------------------------------------------------------------
    #-----------  Trace Scaling Temperature Characterization ----------
    #------------------------------------------------------------------
    ratio = [0.0025, 0.0154, 0.125, 0.25, 0.5, 0.75]
    die_scale_temp = [49.92, 49.54, 51.64, 56.38, 68.41, 81.25]
    trace_scale_temp = [8.16, 12.44, 27.93, 40.31, 59.34, 77.58]
    
    trace_area = trace_left.area() + trace_mid.area() + trace_right.area()
    
    # Use trace scaling temps to find the die avg temp and trace avg temp
    dt_ratio = die_a/trace_area
    base_die_temp = np.interp(dt_ratio, ratio, die_scale_temp)
    trace_temp = np.interp(dt_ratio, ratio, trace_scale_temp)
    
    print 'trace temp: ' + str(2*trace_temp+22)
    trace_temp_avg = 2*trace_temp
    
    #------------------------------------------------------------------
    #---------------------  Thermal Coupling --------------------------
    #------------------------------------------------------------------
    
    prev_an = 0.0
    an_sum = 0.0
    temp_avg = 0.0
    for temp_rect in trace_temp_rects:
        w2 = temp_rect.width/2
        h2 = temp_rect.height/2
        # Build current temp rect
        comp_rect = Rect(h2 + die2_y, -h2 + die2_y, -w2 + die2_x, w2 + die2_x)
        
        inters = comp_rect.intersection(die1_rect)
        if inters is not None:
            inter_area = inters.area()
            an = inter_area - prev_an
            prev_an = inter_area
            
            an_sum += an
            temp_avg += (base_die_temp + temp_rect.avg_val)*an/die_a
            
    temp_avg += (die_a - an_sum)*base_die_temp/die_a
    die_temp_avg = temp_avg
    
    print 'Die Bottom Avg:  ' + str(die_temp_avg+22)
    
    #------------------------------------------------------------------
    #---------------------    Edge Effect    --------------------------
    #------------------------------------------------------------------
    
    # Find effective power
    power_sum = 0.0
    
    for trace_rect in trace_rects:
        prev_an = 0.0
        
        for flux_rect in iso_top_flux_rects:
            w2 = flux_rect.width/2
            h2 = flux_rect.height/2
            comp_rect = Rect(h2, -h2, -w2, w2)
            comp_rect.translate(die2_x, die2_y)
            
            inters = comp_rect.intersection(trace_rect)
            if inters is not None:
                inters_area = inters.area()
                an = inters_area - prev_an
                prev_an = inters_area
                power_sum += an*flux_rect.avg_val
            
    pe = (power_sum/ptotal)*p0
    rsp0 = (die_temp_avg - trace_temp_avg)/p0
    rsp1 = rsp0*p0/pe
    print 'effect power = ' + str(pe)
    print 'rsp1(no edge) = ' + str(rsp0)
    print 'rsp1(edge effect) = ' + str(rsp1)
    
    print 'isolation = ' + str(2*iso_top_avg_temp + 22)
    

if __name__=='__main__':
    separated_coupling()