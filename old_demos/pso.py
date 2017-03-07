'''
External Dependencies:
Python 2.7
MatPlotLib 1.0.1
Numpy 1.5.1

Author:      Brett Shook; bxs003@uark.edu
Desc:        Implements the primary portion of the Particle Swarm Optimization Algorithm
Created:     Apr 6, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''

import math

import tfsm
import design_config as dc
import pso_config
import util
import graphing

try:
    import power_design
except:
    print 'unit testing'

# Internal Particle Class for PSO
class Particle:
    def __init__(self):
        # PSO variables
        self.best_position = list()
        self.best_fitness = 0
        self.position = list()
        self.velocity = list()
        
        # Create a design description for this particle
        # (maps particle position to design space)
        geometry = tfsm.DesignGeometry(dc.die_w, dc.die_h, dc.die_locs, dc.num_dies, dc.trace_rects)
        self.design = power_design.PowerDesign(dc.thermal_features, geometry)
        self.design.initDiesRand(dc.initial_die_placements)
        
        init_position = self.design.getParticlePosition()
        for i in range(pso_config.dimensions):
            self.best_position.append(init_position[i])
            self.position.append(init_position[i])
            self.velocity.append(util.rand(pso_config.init_vel_range))
            
        self.best_fitness = self.fitness()
        
    def fitness(self):
        # update design information
        self.design.update(self)
        
        temps = self.design.getModuleTemps()
        temps.sort()
                
        return temps[-1]
            
    def __str__(self):
        s = ''
        for p in self.position:
            s += str(p) + ' '
        return s
    

# Main Module Functionality
particles = []
g_best_position = []
g_best_fitness = 0

if pso_config.write_data:
    data_file = open(pso_config.data_file_loc, 'w')

def setup():
    global particles
    util.seed_rand()
    
    del particles[:] # Clear particle list
    
    if pso_config.num_particles <= 0:
        print 'Warning: pso_config says zero or less particles.'
        
    for i in range(pso_config.num_particles):
        p = Particle()
        particles.append(p)
        
    initGroupBest()
    
# Initialize Group Best Solution
# Warning: Should only be used during setup!
def initGroupBest():
    global particles
    global g_best_fitness
    global g_best_position
    
    g_best_fitness = particles[0].best_fitness
    g_best_position = particles[0].position[:]
    
    for p in particles:
        if checkFitness(p.best_fitness, g_best_fitness):
            g_best_fitness = p.best_fitness
            g_best_position = p.position[:]
            
def checkFitness(fit1, fit2):
    if fit1 < fit2: return True
    else: return False
    
def runOpt():
    global g_best_fitness
    global g_best_position
    global particles
    
    printBestSolution()
    die_locs = makeDieList(g_best_position)
    graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, dc.trace_rects, dc.sub_w, dc.sub_h)

    for i in range(pso_config.max_iterations):
        util.seed_rand()
        print str(g_best_fitness)
        
        # IWA
        wV = pso_config.wV0 - pso_config.wV_delta*(float(i)/float(pso_config.max_iterations))
        
        # Update particles
        for p in particles:
            rP = util.rand([0, pso_config.wP])
            rG = util.rand([0, pso_config.wG])
            
            vi = p.velocity
            xi = p.position
            pi = p.best_position
             
            # Update Velocity and Position
            for d in range(pso_config.dimensions):
                vi[d] = wV*vi[d] + rP*(pi[d] - xi[d]) + rG*(g_best_position[d] - xi[d])
                # Limit the velocity from over stepping the search space
                if math.fabs(vi[d]) >= pso_config.v_max:
                    vi[d] = pso_config.v_max
                    
                xi[d] = xi[d] + vi[d]
                # Limit the position from over stepping the search space
                if math.fabs(xi[d]) >= pso_config.x_max:
                    xi[d] = pso_config.x_max
                
            new_fitness = p.fitness()
            
            # Compare new fitness against old
            if(checkFitness(new_fitness, p.best_fitness)):
                # Update Best Position
                p.best_fitness = new_fitness
                p.best_position = p.position[:]
                
                # Check if better than group best
                if(checkFitness(new_fitness, g_best_fitness)):
                    # Update group best
                    g_best_fitness = new_fitness
                    g_best_position = p.position[:]
                
    printBestSolution()
    die_locs = makeDieList(g_best_position)
    graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, dc.trace_rects, dc.sub_w, dc.sub_h)
    
def makeDieList(position_list):
    die_locs = []
    for i in range(0, len(position_list), 2):
        die_loc = []
        die_loc.append(position_list[i])
        die_loc.append(position_list[i+1])
        die_locs.append(die_loc)
            
    return die_locs
    
def printBestSolution():
    global g_best_position
    
    out = ''
    count = 0
    for p in g_best_position:
        if count % 2 == 0:
            out += '[' + str(p) + ','
        else:
            out += str(p) + '], '
            
        count += 1
        
    print '[' + out + ']'

def writeIterationData():
    data_file.write('This is test')

if __name__ == '__main__':
    setup()
    runOpt()
    