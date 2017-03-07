'''
Created on Sep 6, 2012

@author: bxs003
'''
from math import fabs, sin, pow
import powercad.util as util

class Design2DConfig:
    def __init__(self):
        self.num_dimensions = 2
        
        self.pos_init = [(0.0, 5.0), (0.0, 5.0)]
        self.vel_init = (-1.0, 1.0)
        
        self.pos_lim = [(0.0, 20.0), (0.0, 20.0)]
        self.v_lim = [20.0, 20.0]
        
        util.seed_rand(1337)

class Design2D:
    def __init__(self, config):
        self.config = config
        self.position = list()
        self.velocity = list()
        
        # init particle positions and velocities
        for i in xrange(config.num_dimensions):
            self.position.append(util.rand(config.pos_init[i]))
            self.velocity.append(util.rand(config.vel_init))
    
    def eval_fitness(self):
        X = self.position[0]
        Y = self.position[1]
        # Make a transfer function
        # Find error between the transfer function and the your dataset
        # return error
        return ((fabs(sin(X))+0.5)*pow((X-10),2) + (fabs(sin(Y))+1.0)*pow(Y-10,2))/35.0