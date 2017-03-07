'''
Created on Sep 27, 2012

@author: bxs003
'''

from math import sqrt, pi
from copy import copy

from powercad.util import translate_pt
from powercad.sym_layout.symbolic_layout import build_test_layout
from powercad.design.solution_structures import DeviceSolution, LeadSolution, BondwireSolution

class ModuleDesignError(Exception):
    def __init__(self, msg):
        self.args = [msg]
        
class ModuleDesign(object):
    def __init__(self, sym_layout):
        """Holds all of the design geometry information for a specific layout.
        
        Public Access Properties
        devices -- list of DeviceSolution objects
        bondwires -- list of BondWireSolution objects
        leads -- list of LeadSolution objects
        traces -- list of Rect objects
        substrate -- SubstrateInstance object
        substrate_attach --- SubstrateAttachInstance object
        baseplate -- BaseplateInstance object
        
        """
        self.devices = None
        self.bondwires = None
        self.leads = None
        self.traces = None
        self.substrate = None
        self.substrate_attach = None
        self.baseplate = None
        
        self.sym_layout = sym_layout # reference of symbolic layout object
        self._symbolic_layout_to_design() # convert layout to full design object
        
    def _symbolic_layout_to_design(self):
        layout = self.sym_layout
        
        if not layout.layout_ready:
            raise ModuleDesignError("Module layout has not been generated!")
        
        self.substrate = layout.module.substrate
        self.substrate_attach = layout.module.substrate_attach
        self.baseplate = layout.module.baseplate
        
        ledge_width = layout.module.substrate.ledge_width
        
        # Devices
        self.devices = []
        for dev in layout.devices:
            cpos = dev.center_position
            # Translate points over by ledge_width (reference to substrate corner)
            cpos = translate_pt(cpos, ledge_width, ledge_width)
            fp = dev.footprint_rect.deepCopy()
            fp.translate(ledge_width, ledge_width)
            dev_sol = DeviceSolution(cpos, dev.tech, fp)
            self.devices.append(dev_sol)
            
        # Leads
        self.leads = []
        for lead in layout.leads:
            cpos = lead.center_position
            # Translate points over by ledge_width (reference to substrate corner)
            cpos = translate_pt(cpos, ledge_width, ledge_width)
            lead_sol = LeadSolution(cpos, lead.orientation, lead.tech)
            self.leads.append(lead_sol)
            
        # Bondwires
        self.bondwires = []
        for wire in layout.bondwires:
            if (wire.device is not None) and (wire.land_pt is not None):
                dev = wire.device
                for pt_index in xrange(len(wire.start_pts)):
                    pt1 = translate_pt(wire.start_pts[pt_index], ledge_width, ledge_width)
                    pt2 = translate_pt(wire.end_pts[pt_index], ledge_width, ledge_width)
                    eff_diam = wire.tech.eff_diameter()
                    beg_height = dev.tech.device_tech.dimensions[2] + float(dev.tech.attach_thickness)
                    height = wire.tech.a
                    bw = BondwireSolution((pt1, pt2), beg_height, height, wire.tech, eff_diam)
                    self.bondwires.append(bw)
            elif (wire.land_pt is not None) and (wire.land_pt2 is not None):
                for pt1, pt2 in zip(wire.start_pts, wire.end_pts):
                    pt1 = translate_pt(pt1, ledge_width, ledge_width)
                    pt2 = translate_pt(pt2, ledge_width, ledge_width)
                    eff_diam = wire.tech.eff_diameter()
                    beg_height = 0.0
                    height = wire.tech.a
                    bw = BondwireSolution((pt1, pt2), beg_height, height, wire.tech, eff_diam)
                    self.bondwires.append(bw)
        
        # Traces
        self.traces = []
        for line in layout.all_trace_lines:
            if line.intersecting_trace is None:
                rect = copy(line.trace_rect)
                rect.translate(ledge_width, ledge_width)
                self.traces.append(rect)
            else:
                if line.has_rect:
                    rect = copy(line.trace_rect)
                    rect.translate(ledge_width, ledge_width)
                    self.traces.append(rect)
    
if __name__ == '__main__':
    sym_layout = build_test_layout()
    md = ModuleDesign(sym_layout)
    for dev in md.devices:
        print dev.position