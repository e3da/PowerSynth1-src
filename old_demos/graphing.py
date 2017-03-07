
'''
Author:      Brett Shook; bxs003@uark.edu

Desc:        Graphing Utilities

Created:     May 6, 2011
Last Change: May 25, 2011

Copyright: 2011 University of Arkansas Board of Trustees 
'''
import numpy as np
import matplotlib.pyplot as plot
from matplotlib.patches import Rectangle
from matplotlib.path import Path
from pylab import figure, show, xlabel, ylabel, title, text
from spice_net import *
from hspice_plot import *

def plotSolution(die_locs, die_width, die_height, eff_w, eff_h, trace_rects, width, height, temps=[]):
    w2 = die_width/2.0
    h2 = die_height/2.0
    ew2 = eff_w/2.0
    eh2 = eff_h/2.0
    
    ax = plot.subplot(111, adjustable='box', aspect=1.0)
    
    for rect in trace_rects:
        r = Rectangle((rect.l, rect.b), rect.r - rect.l, rect.t - rect.b, facecolor='#FFB24D', edgecolor='none')
        ax.add_patch(r)
    
    die_xs = []
    die_ys = []
    for die_loc in die_locs:
        x = die_loc[0]
        y = die_loc[1]
        die_xs.append(x)
        die_ys.append(y)
        rect = Rectangle((x - w2, y - h2), die_width, die_height, facecolor='#55ee55')
        ax.add_patch(rect)
        
        rect2 = Rectangle((x - ew2, y - eh2), eff_w, eff_h, facecolor='none', edgecolor='#4A50FF')
        ax.add_patch(rect2)
    
    ax.plot(die_xs, die_ys, 'o')
    ax.axis([0, width, 0, height])
    
    plot.show()
    
def subplotSolution(ax, die_locs, die_width, die_height, eff_w, eff_h, trace_rects, left, right, bottom, top, temps=[]):
    w2 = die_width/2.0
    h2 = die_height/2.0
    ew2 = eff_w/2.0
    eh2 = eff_h/2.0
    
    for rect in trace_rects:
        r = Rectangle((rect.l, rect.b), rect.r - rect.l, rect.t - rect.b, facecolor='#FFB24D', edgecolor='none')
        ax.add_patch(r)
    
    die_xs = []
    die_ys = []
    for die_loc in die_locs:
        x = die_loc[0]
        y = die_loc[1]
        die_xs.append(x)
        die_ys.append(y)
        rect = Rectangle((x - w2, y - h2), die_width, die_height, facecolor='#55ee55')
        ax.add_patch(rect)
        
        #rect2 = Rectangle((x - ew2, y - eh2), eff_w, eff_h, facecolor='none', edgecolor='#4A50FF')
        #ax.add_patch(rect2)
    
    title('Design Rendering')
    xlabel('X (mm)')
    ylabel('Y (mm)')
    ax.plot(die_xs, die_ys, 'o')
    ax.axis([left, right, bottom, top])
    
def graphParetoFront(points, left, right, bottom, top):
    xs = []
    ys = []
    
    for p in points:
        xs.append(p[0])
        ys.append(p[1])
        
    ax = plot.subplot(111, adjustable='box', aspect=1.0)
        
    ax.plot(xs, ys, 'o')
    ax.axis([left, right, bottom, top])
    
    plot.show()
    
class SolutionBrowser:
    def __init__(self, fig, pareto_ax, design_ax, info_txt, points, plot_sol_func, hof):
        self.fig = fig

        self.last_lines=None
        self.hs_fig=figure()

        #show()
        self.pareto_ax = pareto_ax
        self.design_ax = design_ax
        self.points = points
        
        self.xs = points.get_xdata()
        self.ys = points.get_ydata()
        
        self.dataind = 0
        self.selected = self.pareto_ax.plot([self.xs[0]], [self.ys[0]], 'o', ms=12, alpha=0.4, color='yellow', visible=False)[0]
        self.info_txt = info_txt
        
        self.plot_sol_func = plot_sol_func
        self.hof = hof
        
    def onPick(self, event):
        
        # Make sure that we are dealing with points
        if event.artist != self.points: return True
                
        # Check that there are some indices
        N = len(event.ind)
        if not N: return True
        
        # the click locations
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata
        
        # Get the closest indice
        distances = np.hypot(x-self.xs[event.ind], y-self.ys[event.ind])
        indmin = distances.argmin()
        self.dataind = event.ind[indmin]
       
        self.update()
        
    def update(self):
        self.plot_sol_func(self.dataind, self.hof, self.design_ax)
        self.selected.set_data(self.xs[self.dataind], self.ys[self.dataind])
        self.selected.set_visible(True)
        
        values = self.hof[self.dataind].fitness.values
        self.info_txt.set_text('Temp: ' + str(round(values[0], 3)) + 'C \nInduct: ' + str(round(values[1], 3)) + 'nH')
        self.info_txt.set_visible(True)
        self.fig.canvas.draw()

        lines = run_hspice(round(values[0], 3),round(values[1], 3), 'C:/Users/bxs003/Desktop/topology_testing/', 'yo_dawg.out')
        lines[0] = 'Temp: ' + str(round(values[0], 3)) + 'C \nInduct: ' + str(round(values[1], 3)) + 'nH'
    
        if self.last_lines is None:
            hspice_plot([lines],self.hs_fig)
        else:
            hspice_plot([self.last_lines,lines],self.hs_fig)
        
        self.last_lines=lines[:]
        self.hs_fig.canvas.draw()
    
def interactiveParetoFront(hof, points, left, right, bottom, top, plot_sol_func):
    xs = []
    ys = []
    for p in points:
        xs.append(p[0])
        ys.append(p[1])
    
    fig = figure()
    pareto_ax = fig.add_subplot(211)
    points = pareto_ax.plot(xs, ys, 'o', picker=5)[0]  # 5 points tolerance
    info_txt = text(95, 7, 'No Point Selected', visible=False)
    
    title('Pareto Front')
    xlabel('Temp. (C)')
    ylabel('Induct. (nH)')
    
    design_ax = fig.add_subplot(212, aspect=1.0)
    
    browser = SolutionBrowser(fig, pareto_ax, design_ax, info_txt, points, plot_sol_func, hof)
    fig.canvas.mpl_connect('pick_event', browser.onPick)
    show()
    
    
def test_sol_plot():
    import design_config as dc
    
    die_locs = [[3.3130750856, 2.04189924117], [3.30506027567,5.41063400538], [3.23221887894, 10.4578584011]]
    plotSolution(die_locs, 4.8, 2.4, 8.1, 7.44, dc.trace_rects, 13.5, 31.0)

if __name__ == '__main__':
    test_sol_plot()
    
