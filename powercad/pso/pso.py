'''
Created on Sep 5, 2012

@author: bxs003
'''

import powercad.util as util
import math

class Particle:
    def __init__(self, design):
        
        # design object maps particle space to design space
        self.design = design
        
        # Particle variables
        self.position = design.position
        self.velocity = design.velocity
        self.best_fitness = self.design.eval_fitness()
        self.best_position = design.position[:]
        
    def fitness(self):
        return self.design.eval_fitness()
            
    def __str__(self):
        s = ''
        for p in self.position:
            s += str(p) + ' '
        return s
    
class ParticleSwarm:
    def __init__(self, design_imp, design_config, pso_config):
        self.design_imp = design_imp
        self.design_config = design_config
        self.pso_config = pso_config
        
        self.particles = None
        self.g_best_position = None
        self.g_best_fitness = 0
        
        self.particle_hist = None
    
    # Clear and setup the swarm
    def setup(self):
        del self.particle_hist
        self.particle_hist = list()
        
        del self.particles
        self.particles = list()
        
        hist_temp = []    
        for i in xrange(self.pso_config.num_particles):
            des = self.design_imp(self.design_config)
            p = Particle(des)
            self.particles.append(p)
            hist_temp.append((p.position[:], p.velocity[:], p.best_fitness))
            
        self.particle_hist.append(hist_temp)
        self.initGroupBest()
        
    # Initialize Group Best Solution
    def initGroupBest(self):
        self.g_best_fitness = self.particles[0].best_fitness
        self.g_best_position = self.particles[0].position[:]
        
        for p in self.particles:
            if self.checkFitness(p.best_fitness, self.g_best_fitness):
                self.g_best_fitness = p.best_fitness
                self.g_best_position = p.position[:]
            
    def checkFitness(self, fit1, fit2):
        if fit1 < fit2: return True
        else: return False
    
    def run(self):
        util.seed_rand(500)
        
        # Shorthand
        pso_config = self.pso_config
        design_config = self.design_config
        
        for i in range(pso_config.max_iterations):
            #print str(self.g_best_position)
            
            # IWA
            wV = pso_config.wV0 - pso_config.wV_delta*(float(i)/float(pso_config.max_iterations))
            
            # Update particles
            hist_temp = []
            for p in self.particles:
                rP = util.rand([0, pso_config.wP])
                rG = util.rand([0, pso_config.wG])
                
                vi = p.velocity
                xi = p.position
                pi = p.best_position
                 
                # Update Velocity and Position
                for d in xrange(design_config.num_dimensions):
                    # Find new velocity
                    vi[d] = wV*vi[d] + rP*(pi[d] - xi[d]) + rG*(self.g_best_position[d] - xi[d])
                    
                    # Limit the velocity
                    if math.fabs(vi[d]) > design_config.v_lim[d]:
                        if vi[d] < 0.0:
                            vi[d] = -design_config.v_lim[d]
                        else:
                            vi[d] = design_config.v_lim[d]
                    
                    # Update position
                    xi[d] = xi[d] + vi[d]
                    
                    # Limit the position from over stepping the search space
                    if xi[d] > design_config.pos_lim[d][1]:
                        xi[d] = design_config.pos_lim[d][1]
                    elif xi[d] < design_config.pos_lim[d][0]:
                        xi[d] = design_config.pos_lim[d][0]
                    
                new_fitness = p.fitness()
                
                hist_temp.append((xi[:], vi[:], new_fitness))
                
                # Compare new fitness against old
                if(self.checkFitness(new_fitness, p.best_fitness)):
                    # Update Best Fitness and Position
                    p.best_fitness = new_fitness
                    p.best_position = p.position[:]
                    
                    # Check if better than group best
                    if(self.checkFitness(new_fitness, self.g_best_fitness)):
                        # Update group best
                        self.g_best_fitness = new_fitness
                        self.g_best_position = p.position[:]
                        
            self.particle_hist.append(hist_temp)
                        

if __name__ == '__main__':
    from design_2d import Design2DConfig, Design2D
    import pso_config
    
    config = Design2DConfig()
    opt = ParticleSwarm(Design2D, config, pso_config)
    opt.setup()
    opt.run()
    
    print opt.particle_hist
    