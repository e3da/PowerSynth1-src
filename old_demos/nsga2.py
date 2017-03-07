'''
Created on Oct 31, 2011

@author: shook
'''

import random
import array
import math

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from pylab import text
from matplotlib.patches import Rectangle

import graphing
import tfsm
import power_design as pd
import design_config as dc
from util import Rect

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)

def getDieLocs(dist):
    return [[-dist, 10.0], [dist, 10.0]]

def getTraces(dist):
    edge_dist = 1.905
    far_edge = 2*dist - edge_dist
    bottom_trace = Rect(0.0, -6.0, -far_edge, far_edge)
    left_trace = Rect(20.0, 0.0, -far_edge, -edge_dist)
    right_trace = Rect(20.0, 0.0, edge_dist, far_edge)
    
    return [left_trace, right_trace, bottom_trace]

def plot_sol_func(index, hof, sub_ax):
    dist = hof[index][0]
    sub_ax.cla()
    
    traces = getTraces(dist)
    die_locs = getDieLocs(dist)
    
    tw = traces[0].width()
    w = traces[2].width()
    b = traces[2].bottom() - 2.0
    t = traces[0].top() + 2.0
    
    des_geom = tfsm.DesignGeometry(dc.die_w, dc.die_h, die_locs, len(die_locs), traces)
    design = pd.PowerDesign(dc.thermal_features, des_geom)
    
    graphing.subplotSolution(sub_ax, die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, traces, -w, w, b, t)
    
    # Draw gate trace
    gate = Rectangle((-0.635, 1.0), 1.27, 20.0, facecolor='#73ffff', edgecolor='none')
    sub_ax.add_patch(gate)
    
    # Draw wire bonds
    diam = 0.25
    h = die_locs[0][1]
    bond1 = Rectangle((-dist, h-diam), dist-0.1, diam, facecolor='#1a1a1a', edgecolor='none')
    bond2 = Rectangle((0.1, h-diam), dist, diam, facecolor='#1a1a1a', edgecolor='none')
    sub_ax.add_patch(bond1)
    sub_ax.add_patch(bond2)
    
    text(0.0, 20.0, 'Gate')
    text(w+2.0, 12.0, 'WireBond Length: ' + str(round(dist, 3)) + ' mm')
    text(w+2.0, 10.0, 'Trace Leg Width: ' + str(round(tw, 3)) + ' mm')

def findHiTemp(dist):
    
    traces = getTraces(dist)
    die_locs = getDieLocs(dist)
    
    des_geom = tfsm.DesignGeometry(dc.die_w, dc.die_h, die_locs, len(die_locs), traces)
    design = pd.PowerDesign(dc.thermal_features, des_geom)
    
    #graphing.plotSolution(die_locs, dc.die_w, dc.die_h, dc.flux_eff_w, dc.flux_eff_h, traces, dc.sub_w, dc.sub_h)
    
    temps = design.getModuleTemps()
    temps.sort()
    
    return temps[-1]

def findInductance(dist):
    l = dist*0.1
    a = 0.025 # wirebond diameter in cm
    # returns nH
    return 2.0*l*(math.log(l/a) + 0.5 + 0.447*a/l)

def eval(individual):
    dist = individual[0]
    return (findHiTemp(dist), findInductance(dist))

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, 4.5, 10.0)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, 1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def checkBounds(min, max):
    def decCheckBounds(func):
        def wrapCheckBounds(*args, **kargs):
            offsprings = func(*args, **kargs)
            for child in offsprings:
                if child[0] > max:
                    child[0] = max
                elif child[0] < min:
                    child[0] = min
            return offsprings
        return wrapCheckBounds
    return decCheckBounds

toolbox.register("evaluate", eval)
toolbox.register("mate", tools.cxBlend, alpha=1.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=3, indpb=0.3)
toolbox.register("select", tools.selNSGA2)

min_dist = 4.5
max_dist = 10.0
toolbox.decorate("mate", checkBounds(min_dist, max_dist))
toolbox.decorate("mutate", checkBounds(min_dist, max_dist))

def main():
    random.seed(64)
    MU, LAMBDA = 15, 30
    
    pop = toolbox.population(n=MU)
    hof = tools.ParetoFront()
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std) 
    stats.register("Max", max)
    
    algorithms.eaMuPlusLambda(toolbox, pop, mu=MU, lambda_=LAMBDA, cxpb=0.5, mutpb=0.2, ngen=50, stats=stats, halloffame=hof)
    
    print "Best individual for measure 1 is {0}, {1}".format(hof[0][0], hof[0].fitness.values)
    print "Best individual for measure 2 is {0}, {1}".format(hof[-1][0], hof[-1].fitness.values)
    
    points = []
    for sol in hof:
        points.append(sol.fitness.values)
    
    l = hof[0].fitness.values[0]
    r = hof[-1].fitness.values[0]
    b = hof[-1].fitness.values[1]
    t = hof[0].fitness.values[1]
    graphing.interactiveParetoFront(hof, points, l, r, b, t, plot_sol_func)
    
    return pop, stats, hof

if __name__ == "__main__":
    main()
    #print findHiTemp(5.0)
    #print findInductance(7.0)