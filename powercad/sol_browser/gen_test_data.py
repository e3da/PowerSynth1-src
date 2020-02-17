'''
Created on Jun 8, 2012

@author: bxs003
'''

import math
from random import uniform, seed, randint

from .solution_lib import SolutionLibrary

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def get_objective_data(num_objectives = 3, num_sol_pts = 800):
    seed(1337)
    obj_data = []
    
    for x in range(num_objectives):
        obj = []
        range = random_range()
        for y in range(num_sol_pts):
            if x < num_objectives-1:
                obj.append(uniform(range[0], range[1]))
            else:
                #obj.append(math.pow(math.sin(obj_data[x-1][y]*0.05),2) + math.pow(math.cos(obj_data[x-2][y]*0.05),2))
                obj.append(1000/(obj_data[x-1][y]*obj_data[x-2][y]))
        obj_data.append(obj)
        
    return obj_data
            
def random_range():
    ranges = [(100, 300), (5, 50), (20, 100)]
    range_sel = randint(0,2)
    return ranges[range_sel]

def plot_sols(data):
    figure = plt.figure()
    axes = figure.add_subplot(111, projection='3d')
    axes.scatter(data[0], data[1], data[2])
    plt.show()
    
def make_solution_library(num_objectives = 3, num_sols = 800):
    data = get_objective_data(num_objectives, num_sols)
    if num_objectives == 2:
        names_units = [('Max. Temp.', 'C'), ('Gate Wirebond Ind.', 'nH')]
    elif num_objectives == 3:
        names_units = [('Max. Temp.', 'C'), ('Gate Wirebond Ind.', 'nH'), ('Commutation Path Res.', 'uOhm')]
    elif num_objectives == 4:
        names_units = [('Max. Temp.', 'C'), ('Gate Wirebond Ind.', 'nH'), ('Commutation Path Res.', 'uOhm'), ('Max Width', 'nm')]
    return SolutionLibrary(names_units, data, None, None, None)

if __name__ == '__main__':
    data = get_objective_data(3, 800)
    print(len(data[0]))
    plot_sols(data)
    
#    sol_lib = make_solution_library()
#    for names in sol_lib.measure_names_units:
#        print names
    