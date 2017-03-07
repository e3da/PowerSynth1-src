'''
Created on Mar 24, 2013

@author: bxs003
'''

import sys
import pickle

import matplotlib.pyplot as plt
import networkx as nx
from PySide import QtGui
from PySide.QtGui import QFileDialog

from powercad.sym_layout.plot import plot_layout

def load_symbolic_layout(filename):
    f = open(filename, 'r')
    sym_layout = pickle.load(f)
    f.close()
    return sym_layout

def dump_tech_lib_obj(filename):
    pass

def experiment1():
    sym_layout = load_symbolic_layout("../../../export_data/Optimizer Runs/run4.p")
    sym_layout.gen_solution_layout(58)
    
    ax = plot_layout(sym_layout, new_window=False)
    
    #traces = sym_layout.trace_rects
    #for i in xrange(len(traces)):
    #    center = traces[i].center()
    #    ax.text(center[0], center[1], str(i),
    #            horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='red', alpha=0.8))
    #    print i,': w:',traces[i].width(),' l:',traces[i].height()
        
    #dies = sym_layout.devices
    #for i in xrange(len(dies)):
    #    die = dies[i]
    #    center = die.center_position
    #    w,l,t = die.tech.device_tech.dimensions
    #    ax.text(center[0], center[1], str(i),
    #            horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='red', alpha=0.8))
    #    print i, (center[0]-w*0.5, center[1]-l*0.5)
    
    lg = sym_layout.lumped_graph
    if lg is not None:
        test_pts = []
        pos_data = {}
        for node in lg.nodes(data = True):
            test_pts.append(node[1]['point'])
            pos_data[node[0]] = node[1]['point']
                    
        nx.draw(lg, pos=pos_data, hold=True, node_size=200)
        plot_layout(sym_layout)
    
    plt.show()
    
def load_layout_from_project(project_file, solution_number):
    file = open(project_file,'rb')
    project = pickle.load(file)
    file.close()
    if solution_number < len(project.solutions) and solution_number >= 0:
        sol = project.solutions[solution_number]
        project.symb_layout.gen_solution_layout(sol.index)
        return project.symb_layout
    else:
        print "Solution not found."

if __name__ == "__main__":
    proj = r"C:\Users\shook\Documents\DropBox_madshook\Dropbox\PMLST\PMLST Projects\parasitic extraction layouts\pex_full2\project.p"
    symlayout = load_layout_from_project(proj, 0)
    
    #proj2 = r"C:\Users\shook\Documents\DropBox_madshook\Dropbox\PMLST\PMLST Projects\parasitic extraction layouts\pex_test\project.p"
    #symlayout = load_layout_from_project(proj2, 0)