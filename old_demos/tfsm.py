'''
Created on Aug 24, 2011

@author: shook
'''

from thermal import DieThermal, solve_for_temps
from util import Rect
import numpy as np
import math

class TFSMInputError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
class TFSMInternalError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
class ContourRect:
    def __init__(self, width, height, avg_val):
        self.width = width
        self.height = height
        self.avg_val = avg_val
        
# Parameter Info
# scaling_ratio: a list of die area/trace area ratios
# scaling_die_temps: a list of die temps corresponding to scaling_ratio
# scaling_trace_temps: a list of trace temps corresponding to scaling_ratio
class ThermalFeatures:
    def __init__(self, iso_top_fluxes, iso_top_avg_temp, trace_top_temps, 
                 scaling_ratio, scaling_die_temps, scaling_trace_temps, 
                 die_power, die_res, sub_res, t_amb, trace_char_dim):
        
        self.iso_top_fluxes = iso_top_fluxes
        self.iso_top_avg_temp = iso_top_avg_temp
        self.trace_top_temps = trace_top_temps
        self.scaling_ratio = scaling_ratio
        self.scaling_die_temps = scaling_die_temps
        self.scaling_trace_temps = scaling_trace_temps
        self.die_power = die_power
        self.die_res = die_res
        self.sub_res = sub_res
        self.t_amb = t_amb
        self.trace_char_dim = trace_char_dim
        
        self.total_eff_power = find_power_from_contours(iso_top_fluxes)
        
        self.scaled_fluxes = iso_top_fluxes
        #self.scale_flux(1.0)
        self.scaled_temps = trace_top_temps
        
    def scale_flux(self, scale_factor):
        scaled_flux_rects = []
        
        prev_an = 0.0
        scaled_prev_an = 0.0
        for flux_rect in self.iso_top_fluxes:
            aspect = flux_rect.width/flux_rect.height
            raw_area = flux_rect.width*flux_rect.height
            
            # find power
            an = raw_area - prev_an
            prev_an = raw_area
            contour_power = an*flux_rect.avg_val
            
            # find new scaled w,h
            new_area = raw_area*scale_factor
            new_w = math.sqrt(aspect*new_area)
            new_h = new_w/aspect
            new_an = new_area - scaled_prev_an
            scaled_prev_an = new_area
            
            
            # find new flux density
            new_flux = contour_power/new_an
            new_rect = ContourRect(new_w, new_h, new_flux)
            scaled_flux_rects.append(new_rect)
        # end for
        
        self.scaled_fluxes = scaled_flux_rects
        
    def scale_temp(self, scale_factor):
        scaled_temp_rects = []
        
        prev_an = 0.0
        scaled_prev_an = 0.0
        for flux_rect in self.iso_top_fluxes:
            aspect = flux_rect.width/flux_rect.height
            raw_area = flux_rect.width*flux_rect.height
            
            # find power
            an = raw_area - prev_an
            prev_an = raw_area
            contour_power = an*flux_rect.avg_val
            
            # find new scaled w,h
            new_area = raw_area*scale_factor
            new_w = math.sqrt(aspect*new_area)
            new_h = new_w/aspect
            new_an = new_area - scaled_prev_an
            scaled_prev_an = new_area
            
            
            # find new flux density
            new_flux = contour_power/new_an
            new_rect = ContourRect(new_w, new_h, new_flux)
            scaled_temp_rects.append(new_rect)
        # end for
        
        self.scaled_temps = scaled_temp_rects
        
        
# Parameter Info
# die_locs: list of die locations eg [[x1, y1],[x2, y2], ...]
class DesignGeometry:
    def __init__(self, die_w, die_h, die_locs, num_dies, trace_rects):
        self.die_w = die_w
        self.die_h = die_h
        self.die_locs = die_locs
        self.num_dies = num_dies
        self.trace_rects = trace_rects
        
class TFSMSolver:
    def __init__(self, thermal_features, design_geometry):
        self.thermal_features = thermal_features
        self.design_geometry = design_geometry
        
        self.rsp1_list = []
        
        if not self.checkTraceRects():
            raise TFSMInputError('Traces are intersecting!')
        
    def updateDieLocs(self, die_locs):
        self.design_geometry.die_locs = die_locs
    
    def updateTraceRects(self, trace_rects):
        self.design_geometry.trace_rects = trace_rects
        
        if not self.checkTraceRects():
            raise TFSMInputError('Traces are intersecting!')
        
    # returns True if trace rects are correct
    def checkTraceRects(self):
        # No trace rects should intersect each other
        return True
    
    def getRsp1s(self):
            return self.rsp1_list
            
    # Returns list of die temps    
    def solve(self):
        
        self.rsp1_list = []
        tf = self.thermal_features
        
        # Die dimensions
        die_a = self.design_geometry.die_w*self.design_geometry.die_h
        die_w2 = self.design_geometry.die_w/2
        die_h2 = self.design_geometry.die_h/2
            
        die_locs = self.design_geometry.die_locs
        num_dies = len(die_locs)
        
        if num_dies <= 0:
            raise TFSMInputError('No dies are present in the design!')
        
        #------------------------------------------------------------------
        #-----------  Trace Scaling Temperature Characterization ----------
        #------------------------------------------------------------------
        
        trace_rects = self.design_geometry.trace_rects
        
        ratio = tf.scaling_ratio
        die_scale_temp = tf.scaling_die_temps
        trace_scale_temp = tf.scaling_trace_temps
        
        # Find total trace area
        trace_area = 0.0
        for rect in trace_rects:
            trace_area += rect.area()
        
        # Use trace scaling temps to find the die avg temp and trace avg temp
        dt_ratio = die_a/trace_area 
        trace_temp = np.interp(dt_ratio, ratio, trace_scale_temp)
        base_die_temp = np.interp(dt_ratio, ratio, die_scale_temp)
        total_trace_temp = num_dies*trace_temp
        #print 'total trace: ' + str(total_trace_temp+22)
        
        # Make some aliases for power
        p0 = tf.die_power
        ptotal = tf.total_eff_power
        
        # Calculate Rsp2
        rsp2 = (trace_temp - tf.iso_top_avg_temp)/p0
    
        #------------------------------------------------------------------
        #---------------------  Main Algorithm ----------------------------
        #------------------------------------------------------------------
        
        # Solving for these
        die_thermals = []
        
        trace_temp_rects = tf.trace_top_temps
        
        for i in range(len(die_locs)):
            # Build current die rect
            die = die_locs[i]
            x = die[0]
            y = die[1]
            die_region = Rect(die_h2, -die_h2, -die_w2, die_w2)
            die_region.translate(x, y)
            
            #------------------------------------------------------------------
            #---------------------    Edge Effect    --------------------------
            #------------------------------------------------------------------
            
            # Find effective power
            power_sum = 0.0
            
            for trace_rect in trace_rects:
                prev_an = 0.0
                
                for flux_rect in tf.scaled_fluxes:
                    w2 = flux_rect.width/2
                    h2 = flux_rect.height/2
                    comp_rect = Rect(h2, -h2, -w2, w2)
                    comp_rect.translate(x, y)
                    
                    inters = comp_rect.intersection(trace_rect)
                    if inters is not None:
                        inters_area = inters.area()
                        an = inters_area - prev_an
                        prev_an = inters_area
                        power_sum += an*flux_rect.avg_val
                    #end if
                #end for
            #end for
                   
            pe = (power_sum/ptotal)*p0
            #print pe
            
            if pe <= 0.0:
                pe = 0.00001
                
            Re = (base_die_temp - trace_temp)*(p0 - pe)/(p0*pe)
            
            #------------------------------------------------------------------
            #---------------------  Thermal Coupling --------------------------
            #------------------------------------------------------------------
            
            theta = 0.0
            wsum = 0.0
            for coupled_die in die_locs:
                if not(coupled_die is die):
                    die_x = coupled_die[0]
                    die_y = coupled_die[1]
                    
                    prev_an = 0.0
                    for temp_rect in trace_temp_rects:
                        
                        # Build current temp rect
                        w2 = temp_rect.width/2
                        h2 = temp_rect.height/2
                        comp_rect = Rect(h2, -h2, -w2, w2)
                        comp_rect.translate(die_x, die_y)
                        
                        inters = comp_rect.intersection(die_region)
                        if inters is not None:
                            inter_area = inters.area()
                            an = inter_area - prev_an
                            prev_an = inter_area
                            wsum += temp_rect.avg_val*an
                        #end if
                    #end for
                #end if not coupled
            #end for
            theta = wsum/die_a
            die_bottom_temp = theta+base_die_temp
            rsp1 = (die_bottom_temp - total_trace_temp)/p0 + Re
            self.rsp1_list.append(rsp1)
            dt = DieThermal(tf.die_res, rsp1, p0)
            die_thermals.append(dt)
        #end for
        
        # Solve lumped system for temperatures
        temps = solve_for_temps(die_thermals, tf.sub_res + rsp2, tf.t_amb)
        return temps
        
        
# Finds total power (in Watts) captured by flux contours
def find_power_from_contours(flux_rects):
    power = flux_rects[0].width*flux_rects[0].height*flux_rects[0].avg_val
    for i in range(1, len(flux_rects)):
        curr = flux_rects[i]
        prev = flux_rects[i-1]
        
        power += (curr.width*curr.height - prev.width*prev.height)*curr.avg_val;
        
    return power

# Utility function for turning arrays of contour data into ContourRect objects
def build_contour_rects(values, widths, heights):
    rects = []
    for i in range(len(values)):
        rect = ContourRect(widths[i], heights[i], values[i])
        rects.append(rect)
        
    return rects

if __name__ == '__main__':
    
    #-------------------------------------------------------
    #----------------- Thermal Parameters ------------------
    #-------------------------------------------------------

    ratio = [0.0025, 0.0154, 0.125, 0.25, 0.5, 0.75]
    die_scale_temp = [49.92, 49.54, 51.64, 56.38, 68.41, 81.25]
    trace_scale_temp = [8.16, 12.44, 27.93, 40.31, 59.34, 77.58]
    
    iso_top_avg_temp = 8.1414
    sub_res = 0.203535
    t_amb = 22.0
    die_power = 40.0
    die_res = 0.2165
    
    # Flux through isolation top
    iso_top_flux = [1.0472, 0.8459, 0.6849, 0.5329, 0.3952, 0.2616, 0.1568, 0.0218]
    iso_top_flux_w = [2.7315, 3.6798, 4.6314, 5.6152, 6.6991, 7.7830, 8.8669, 21.4034]
    iso_top_flux_h = [2.3702, 2.9790, 3.5881, 4.1985, 4.8089, 5.8033, 8.1433, 19.4231]
    iso_top_flux_rects = build_contour_rects(iso_top_flux, iso_top_flux_w, iso_top_flux_h)
    
    # Trace top theta temp. dist.
    trace_top_temps = [53.8243, 45.9849, 38.4381, 31.5119, 25.1107, 19.5288, 13.8440, 7.6656]
    trace_top_w = [3.1684, 4.3124, 5.2748, 6.3046, 7.4724, 9.4172, 14.8463, 83.8300]
    trace_top_h = [2.0588, 2.7741, 3.4895, 4.5188, 5.7801, 8.0111, 13.5568, 54.6000]
    trace_temp_rects = build_contour_rects(trace_top_temps, trace_top_w, trace_top_h)
    
    # Build thermal features object
    thermal = ThermalFeatures(iso_top_flux_rects, iso_top_avg_temp, trace_temp_rects,
                              ratio, die_scale_temp, trace_scale_temp, die_power,
                              die_res, sub_res, t_amb)
    
    #-------------------------------------------------------
    #----------------- Geometry Parameters -----------------
    #-------------------------------------------------------

    die_w = 4.8
    die_h = 2.4
    
    num_dies = 2
    die_locs = [[2.4, 3.2], [14.0, 11.0]]
    
    # Traces
    trace_left = Rect(20.0, 0.0, 0.0, 8.0)
    trace_mid = Rect(8.0, 0.0, 0.0, 2.0)
    trace_mid.translate(8.0, 0.0)
    trace_right = Rect(20.0, 0.0, 0.0, 8.0)
    trace_right.translate(10.0, 0.0)
    trace_rects = [trace_left, trace_mid, trace_right]
    
    # Build design geometry object
    geometry = DesignGeometry(die_w, die_h, die_locs, num_dies, trace_rects)
    
    #-------------------------------------------------------
    #-----------------    Test Solver      -----------------
    #-------------------------------------------------------
    
    solver = TFSMSolver(thermal, geometry)
    temps = solver.solve()
    for t in temps:
        print t

