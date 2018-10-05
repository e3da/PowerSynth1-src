'''
Created on March 12, 2017

@author: Jonathan Main

PURPOSE:
 - This module is used to check design rules on a symbolic layout
 
INPUT: 
 - SymbolicLayout object

'''

from powercad.design.library_structures import BondWire
from powercad.design.project_structures import DeviceInstance
from powercad.general.data_struct.util import distance

class DesignRuleCheck():
    
    def __init__(self, symb_layout):
        
        self.symb_layout = symb_layout
        self.err_count = 0
        self.err_report = {}
        
        
    def passes_drc(self, debug = False):
        '''
        Jonathan: Returns False if any DRC errors are found; only returns True if no DRC errors found
        '''
        print "----- Running exhaustive DRC -----"
        print "Using design rules: "
        print "Min trace trace width = " + str(self.symb_layout.design_rules.min_trace_trace_width)
        print "Min trace width = " + str(self.symb_layout.design_rules.min_trace_width)
        print "Min die die dist = " + str(self.symb_layout.design_rules.min_die_die_dist)
        print "Min die trace dist = " + str(self.symb_layout.design_rules.min_die_trace_dist)
        print "Power bondwire to trace dist = " + str(self.symb_layout.design_rules.power_wire_trace_dist)
        print "Signal bondwire to trace dist = " + str(self.symb_layout.design_rules.signal_wire_trace_dist)
        print "Power bondwire to comp dist = " + str(self.symb_layout.design_rules.power_wire_component_dist)
        print "Power bondwire to comp dist = " + str(self.symb_layout.design_rules.signal_wire_component_dist)
        self.err_count = self.count_drc_errors(self)
        if self.err_count > 0.0:
            print str(self.err_count) + " DRC errors found."
            print "ERROR REPORT: " + str(self.err_report)
            return False
        else:
            print "No DRC errors found."
            return True
        

    def count_drc_errors(self, debug = False):
        '''
        Quang: 
        This method will check all the DRC error and report an error counter for each layout
        It is then used in _opt_eval the more errors there are, the more disadvantage will be added to the individual (so that it will be eliminated)
        Errors name and count will be added into self.err_report, this dictionary is used for analysis to improve the software
        I HAVE INCLUDED 2 methods to make this code concise
        plz check: drc_err_dict_update(self,name) and drc_single_check(self,var_name,var_description,debug):
        '''
        self.err_count = 0
        self.err_count += self.drc_single_check(self.symb_layout.h_overflow, 'Horizontal_Overflow', debug)
        self.err_count += self.drc_single_check(self.symb_layout.v_overflow, 'Vertical_Overflow', debug)
        self.err_count += self.drc_single_check(self.symb_layout.h_min_max_overflow[0], 'Min. Horizontal_Overflow', debug)
        self.err_count += self.drc_single_check(self.symb_layout.h_min_max_overflow[1], 'Max. Horizontal_Overflow', debug)
        self.err_count += self.drc_single_check(self.symb_layout.v_min_max_overflow[0], 'Min. Vertical_Overflow', debug)
        self.err_count += self.drc_single_check(self.symb_layout.v_min_max_overflow[1], 'Max. Vertical_Overflow', debug)
        self.err_count += self.drc_single_check(self.check_trace_min_width(), 'Traces less than Min_Width', debug)
        self.err_count += self.drc_single_check(self.check_lead_trace_overlap(), 'Leads are overlapping trace', debug)
        self.err_count += self.drc_single_check(self.check_device_trace_overlap(), 'Devices are not overlapping trace', debug) 
        self.err_count += self.drc_single_check(self.check_component_overlap(), 'Two or more components are overlapping', debug)
        self.err_count += self.drc_single_check(self.check_bondwire_trace_overlap(), 'Bondwires are not contacting trace', debug)
        self.err_count += self.drc_single_check(self.check_bondwire_component_overlap(), 'Bondwires are intersecting other layout components', debug)
        return self.err_count
        
        
    def drc_single_check(self,var_name,var_description,debug):
        ''' 
        Quang:
        This method will check the drc for a drc type with description
        Input: var_name --- The variable represent drc_error 
               var_description --- Description in error dictionary and Debug mode
               Debug--- set equal True to print out error messages
        Return: 0 or 1 so that this value can be added in the err_counter
        '''
        if var_name > 0.0:
            if debug: print var_description, var_name
            self.drc_err_dict_update(var_description)
            return var_name
        else:
            return 0
    
    
    def drc_err_dict_update(self,name):
        '''
        Quang:
        This method is used to add a new error type to error dictionary.
        Used for error analysis
        Input: an error name, it will be counted up for each evaluation and saved in a python dictionary
        Return: None
        '''
        try: 
            self.err_report[str(name)] += 1 # Update error count for existing tuples
        except:
            self.err_report[str(name)] = 0  # When the error first occur, this method will add the new name to error dictionary
        

    def check_trace_min_width(self):
            # Check that all traces are greater than minimum width
            min_width = self.symb_layout.design_rules.min_trace_width
            
            total_error = 0.0
            for rect in self.symb_layout.trace_rects:
                if rect.width < min_width:
                    total_error += min_width - rect.width
                if rect.height < min_width:
                    total_error += min_width - rect.height
                    
            return total_error
    
    def check_lead_trace_overlap(self):
        # Check Lead/Trace Overlap
        total_error = 0.0
        for lead in self.symb_layout.leads:
            # only check against the parent line's immediate connections
            # instead of going through all of the layouts traces
            pline = lead.parent_line
            traces = [pline.trace_rect]
            for line in pline.trace_connections:
                if line.is_supertrace():
                    if line.element.vertical:
                        traces.append(line.trace_rect)
                    else:
                        traces.append(line.intersecting_trace.trace_rect)
                else:
                    traces.append(line.trace_rect) 
                
            lead_rect = lead.footprint_rect.deepCopy()
            #lead_rect.change_size(self.symb_layout.design_rules.min_die_trace_dist)
            lead_area = lead_rect.area()
            area_sum = 0.0
            for rect in traces:
                inter = rect.intersection(lead_rect)
                if inter is not None:
                    area_sum += inter.area()
                if area_sum >= lead_area:
                    break
                
            total_error += lead_area - area_sum
            
        return total_error
            
    def check_device_trace_overlap(self):
        # Check Device/Trace Overlap
        total_error = 0.0
        for device in self.symb_layout.devices:
            # only check against the parent line
            dev_rect = device.footprint_rect.deepCopy()
            dev_rect.change_size(self.symb_layout.design_rules.min_die_trace_dist)
            inter = device.parent_line.trace_rect.intersection(dev_rect)
            if inter is not None:
                total_error += dev_rect.area() - inter.area()
            
        return total_error
    
    def check_component_overlap(self):
        # Check Device->(Device or Trace) Overlap
        checked = {}
        total_error = 0.0
        for pt1 in self.symb_layout.points:
            for pt2 in self.symb_layout.points:
                if pt1 is not pt2:
                    if not((pt1, pt2) in checked):
                        if isinstance(pt1.tech, DeviceInstance) and isinstance(pt2.tech, DeviceInstance):
                            rect1 = pt1.footprint_rect.deepCopy()
                            rect2 = pt2.footprint_rect
                            rect1.change_size(self.symb_layout.design_rules.min_die_die_dist)
                        else:
                            rect1 = pt1.footprint_rect
                            rect2 = pt2.footprint_rect
                            
                        inter = rect1.intersection(rect2)
                        if inter is not None:
                            total_error += inter.area()
                                
                        checked[(pt2, pt1)] = True
        return total_error
    
    def check_bondwire_trace_overlap(self):
        total_error = 0.0
        for bw in self.symb_layout.bondwires:
            if bw.tech.wire_type == BondWire.POWER:
                trace_inset = self.symb_layout.design_rules.power_wire_trace_dist
            elif bw.tech.wire_type == BondWire.SIGNAL:
                trace_inset = self.symb_layout.design_rules.signal_wire_trace_dist
                
            if (bw.land_pt is None) and (bw.land_pt2 is None):
                # bondwires were not even able to be placed
                total_error += len(bw.start_pts+bw.end_pts)
            elif (bw.land_pt is not None) and (bw.land_pt2 is None):
                # bondwire connects device to trace
                rect = bw.trace.trace_rect.deepCopy()
                rect.change_size(-trace_inset) # reduces size of trace by how much room the wire should be given via DRs
                for pt in bw.end_pts:
                    if not rect.encloses(pt[0], pt[1]):
                        total_error += distance(pt, rect.center())
            else: 
                # bondwire connects trace to trace
                start_rect = bw.start_pt_conn.trace_rect.deepCopy()
                end_rect = bw.end_pt_conn.trace_rect.deepCopy()
                # Reduce size of rects by the min. design rule width
                start_rect.change_size(-trace_inset)
                end_rect.change_size(-trace_inset)
                # Check if points are within the design rule area inside rectangle
                for pt in bw.start_pts:
                    if not (start_rect.encloses(pt[0], pt[1])):
                        total_error += distance(pt, start_rect.center())
                
                for pt in bw.end_pts:
                    if not (end_rect.encloses(pt[0], pt[1])):
                        total_error += distance(pt, end_rect.center())
                
        return total_error
    
    def check_bondwire_component_overlap(self):
        '''Checks whether the landing points of bondwires intersect with the wrong components'''
        total_error = 0.0
        for bw in self.symb_layout.bondwires:
            if bw.tech.wire_type == BondWire.POWER:
                trace_inset = self.symb_layout.design_rules.power_wire_component_dist
            elif bw.tech.wire_type == BondWire.SIGNAL:
                trace_inset = self.symb_layout.design_rules.signal_wire_component_dist
                
            if (bw.land_pt is not None) and (bw.land_pt2 is None):
                # bondwire connects device to trace
                for pt in self.symb_layout.points:
                    if pt is not bw.dev_pt:
                        # check for intersection
                        for bwpt in bw.end_pts:
                            rect = pt.footprint_rect.deepCopy()
                            rect.change_size(trace_inset)
                            if rect.encloses(bwpt[0], bwpt[1]):
                                d=distance(bwpt, rect.center())
                                if d!=0:
                                    total_error += 1.0/(distance(bwpt, rect.center()))  # this can create divide for zero problem... In the case that it happen again set a big value as an answer
                                else: 
                                    total_error += float('Inf')
            else:
                # bondwire connects trace to trace
                for pt in self.symb_layout.points:
                    # check for intersection between all components
                    for bwpt in bw.start_pts+bw.end_pts:
                        rect = pt.footprint_rect.deepCopy()
                        rect.change_size(trace_inset)
                        if rect.encloses(bwpt[0], bwpt[1]):
                            d=distance(bwpt, rect.center())
                            if d!=0:
                                total_error += 1.0/(distance(bwpt, rect.center()))  # this can create divide for zero problem... In the case that it happen again set a big value as an answer
                            else: 
                                total_error += float('Inf')
                
        return total_error