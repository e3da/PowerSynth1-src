'''
Author:      Brett Shook; bxs003@uark.edu

Desc:        Data object class describing a particular particle solution layout

Created:     Apr 7, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''

try:
    import util
    
    import demo_drc
    import tfsm
except:
    print 'unit testing'
    
class DesignInitError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class PowerDesign:
    def __init__(self, thermal_features, design_geometry):
        self.design_geometry = design_geometry
        self.solver = tfsm.TFSMSolver(thermal_features, design_geometry)
        
    # Initialize die positions by random intervals
    def initDiesRand(self, initial_die_placements):
        geom = self.solver.design_geometry
        
        if len(initial_die_placements) < geom.num_dies:
            raise DesignInitError('Not enough die information to place initial die locations.')
        
        die_locs = []
        for i in range(geom.num_dies):
            places = initial_die_placements[i]
            x = util.rand(places[0])
            y = util.rand(places[1])
            die_locs.append([x, y])
            
        if not(self.passesDRC()):
            raise DesignInitError('A design configuration did not pass initial DRC. Please check initial die placement.')
        
        self.solver.updateDieLocs(die_locs)
    
    def update(self, particle):
        geom = self.solver.design_geometry
        
        die_locs = []
        for i in range(geom.num_dies):
            x = particle.position[2*i]
            y = particle.position[2*i + 1]
            die_locs.append([x, y])
            
        self.solver.updateDieLocs(die_locs)
    
    def getModuleTemps(self):
        return self.solver.solve()
    
    def getModuleRsp1s(self):
        return self.solver.getRsp1s()
    
    def getParticlePosition(self):
        particle_position = []
        for die_loc in self.solver.design_geometry.die_locs:
            particle_position.append(die_loc[0])
            particle_position.append(die_loc[1])
            
        return particle_position
    
    def passesDRC(self):
        return demo_drc.passesDRC()
    
def batchRun():
    #ds = [0, 0.5, 1, 3, 5, 7, 9, 10, 11, 11.5]
    ds = [0.0, 0.5, 1, 3, 5, 7, 9, 11, 13, 14, 15, 15.5];
    
    die1 = ''
    die2 = ''
    
    for d in ds:
        rsps = balance_expr(d)
        die1 += str(rsps[0]) + ' '
        die2 += str(rsps[1]) + ' '
        
    print die1
    print die2
    
def balance_expr(d):
    from util import Rect
    import design_config as dc
    import graphing
    
    #main = Rect(31.2, 0.0, 0.0, 24.0)
    main = Rect(39.2, 0.0, 0.0, 30.15)
    traces = [main]
    
    x = main.right()/2.0
    y = main.top()/2.0
    die_locs = [[x, y], [x, main.top()-(d+1.2)]]
    
    des_geom = tfsm.DesignGeometry(dc.die_w, dc.die_h, die_locs, len(die_locs), traces)
    design = PowerDesign(dc.thermal_features, des_geom)
    
    #graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, traces, dc.sub_w, dc.sub_h)
    
    temps = design.getModuleTemps()
    rsp1s = design.getModuleRsp1s()
    
    return rsp1s
    
def trace_coupling_expr():
    from util import Rect
    import design_config as dc
    import graphing
    
    dist = 4.0
    left = Rect(20.0, 0.0, 0.0, 8.0)
    mid = Rect(8.0, 0.0, left.right(), left.right()+dist)
    right = Rect(20.0, 0.0, mid.right(), mid.right()+8.0)
    traces = [left, mid, right]
    
    die_locs = [[4.0, 12.2], [right.left()+4.0, 12.2]]
    
    des_geom = tfsm.DesignGeometry(dc.die_w, dc.die_h, die_locs, len(die_locs), traces)
    design = PowerDesign(dc.thermal_features, des_geom)
    
    graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, traces, dc.sub_w, dc.sub_h)
    
    temps = design.getModuleTemps()
    
    print temps
    
from util import Rect
import design_config as dc
import graphing
    
def testing():
    #from util import Rect
    #import design_config as dc  
    #import graphing
    
    #die_locs = [[8.6, 3.5]]
    #die_locs = [[6.14854306979, 5.99215553178]]
    #die_locs = [[11.1, 1.2]]
    #die_locs = [[4, 3.5], [8.6, 15.5], [8.6, 27.5]]
    #die_locs = [[4.43345,16.09835], [4.43345,3.54809361008], [4.64930700395,26.8315832627], ]
    #die_locs = [[3.75407140239,7.52159999612], [3.75407144902,23.4783999961], [7.60287854575,15.4999999961], ]
    #die_locs = [[4.43345, 14.9517386318], [5.86847021646 , 1.25000003238], [4.92702840065, 29.7500000324]]
    #die_locs = [[4.56442355067, 1.58174359264], [4.43345, 15.1774741664], [4.03646700236, 29.1094069754]]
    #die_locs = [[4.43345000004, 4.09835], [4.43345, 26.9016783748], [4.43345,15.834257251]]
    
    die_locs = [[4.4, 15.6], [8.4, 25.5], [15.6, 25.5], [19.6, 15.6], [15.6, 5.7], [8.4, 5.7]]
    main = Rect(31.2, 0.0, 0.0, 24.0)
    trace_rects = [main]

    des_geom = tfsm.DesignGeometry(dc.die_w, dc.die_h, die_locs, len(die_locs), trace_rects)
    design = PowerDesign(dc.thermal_features, des_geom)
    
    temps = design.getModuleTemps()
    
    #print temps
    graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, trace_rects, dc.sub_w, dc.sub_h)
    
def timing():
    from timeit import Timer
    t = Timer("testing()", "from __main__ import testing")
    n=1000
    print 1e6*t.timeit(n)/n
    
if __name__=='__main__':
    #timing()
    testing()
    