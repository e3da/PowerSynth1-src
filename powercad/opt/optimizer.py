'''
Created on Jan 29, 2013

@author: shook
'''

import pickle
import random
import array
import math
import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import time
class DesignVar(object):
    def __init__(self, constraints, init_values):
        """
        Design variable data structure
        
        Keyword Arguments:
        constraints -- tuple (length of 2) of min and max constraints (min, max)
        init_values -- tuple (length of 2) of min and max for design var initialization (min, max)
        """
        self.constraints = constraints
        self.init_values = init_values     
class NSGAII_Optimizer(object):
    def __init__(self, design_vars, eval_fn, num_measures, seed, num_gen, 
                 mu = 10, ilambda=10, cxpb=0.7, mutpb=0.2): #sxm original values; cxpb=0.5, mutpb=0.2
        """
        http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=996017&tag=1
        Creates a new NSGAII_Optimizer object
        
        Keyword Arguments:
        design_vars -- list of DesignVar objects (represent design parameters and their constraints)
        eval_fn -- function reference to design update/generation function
        num_measures -- int, number of objective functions (performance measures)
        seed -- int, random number seed
        num_gen -- int, number of generations
        
        mu -- int, represents the population size
        lamba -- int, represents the offspring population size
        cxpb -- float, (0.0 to 1.0), represents crossover probability
        mutpb -- float, (0.0 to 1.0), represents mutation probability
        
        """
        
        self.design_vars = design_vars
        self.eval_fn = eval_fn
        self.num_measures = num_measures
        self.seed = seed
        self.num_gen = num_gen
        
        self.mu = mu
        self.ilambda = ilambda
        self.cxpb = cxpb
        self.mutpb = mutpb
        
        random.seed(self.seed)
        
        min_weights = []
        for i in xrange(self.num_measures):
            min_weights.append(-1.0)
        min_weights = tuple(min_weights)
        
        creator.create("FitnessMin", base.Fitness, weights=min_weights)
        creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)
        
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._init_individual, creator.Individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", self.eval_fn)
        self.toolbox.register("mate", tools.cxBlend, alpha=1.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=3, indpb=0.3)
        self.toolbox.register("select", tools.selNSGA2)
        
        self.toolbox.decorate("mate", self._check_bounds())
        self.toolbox.decorate("mutate", self._check_bounds())
        
        self.population = self.toolbox.population(n=self.mu)
        self.solutions = tools.ParetoFront()
        
        self.stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        self.stats.register("Avg", numpy.mean)
        self.stats.register("Std", numpy.std)
    
    def _init_individual(self, Individual):
        ind = []
        for dv in self.design_vars:
            ind.append(random.uniform(dv.init_values[0], dv.init_values[1]))
        return Individual(ind)
        
    def run(self):
        """Runs the optimizer"""
        algorithms.eaMuPlusLambda(self.population, self.toolbox, 
                                  mu=self.mu, lambda_=self.ilambda, 
                                  cxpb=self.cxpb, mutpb=self.mutpb, ngen=self.num_gen, 
                                  stats=self.stats, halloffame=self.solutions, verbose=False)
        
    def _check_bounds(self):
        def dec_check_bounds(func):
            def wrap_check_bounds(*args, **kargs):
                offsprings = func(*args, **kargs)
                for child in offsprings:
                    for i in xrange(len(self.design_vars)):
                        consts = self.design_vars[i].constraints
                        # Min Check
                        if child[i] < consts[0]:
                            child[i] = consts[0]
                        # Max Check
                        elif child[i] > consts[1]:
                            child[i] = consts[1]
                return offsprings
            return wrap_check_bounds
        return dec_check_bounds
    
if __name__=='__main__':
    from pylab import plot, show
    
    class TestProb(object):
        def __init__(self, config = True):
            self.config = config
            dv1 = DesignVar((0.0, 2.0), (0.0, 2.0))
            self.design_vars = [dv1]
        
        def eval(self, individual):
            if self.config:
                f1 = math.pow(individual[0], 2)
            else:
                f1 = math.pow(individual[0], 3)
            f2 = -individual[0] + 2.0
            return f1, f2
        
    prob = TestProb()
    seed = 48575
    ngen = 2
    
    opt = NSGAII_Optimizer(prob.design_vars, prob.eval, 2, seed, ngen)
    opt.run()
    f1 = []
    f2 = []
    count=0
    for sol in opt.solutions:
        count+=1
        f1.append(sol.fitness.values[0])
        f2.append(sol.fitness.values[1])
    print count    
    plot(f1, f2, 'o')
    show()
        
    
        