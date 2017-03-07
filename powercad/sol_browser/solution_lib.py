'''
Created on Jun 26, 2012

@author: bxs003
'''

class SolutionLibrary:
    def __init__(self, sym_layout):
        self.measure_names_units = [] # A list of tuples of measure names and units e.g. [('Inductance', 'nH'), ('Resistance', 'mOhms')]
        self.measure_data = [] # A list of number lists containing the performance data for each objective [[1,2,3,...,], [3,6,2,...,]]
        self.individuals = []
    
        # correctly size measure_data
        for i in xrange(len(sym_layout.perf_measures)):
            self.measure_names_units.append((sym_layout.perf_measures[i].name, sym_layout.perf_measures[i].units))
            self.measure_data.append([])
            for j in xrange(len(sym_layout.solutions)):
                self.measure_data[i].append(float(sym_layout.solutions[j].fitness.values[i]))
                
        for sol in sym_layout.solutions:
            self.individuals.append(list(sol))
                
#        print "measure_names_units", self.measure_names_units
#        print "measure_data", self.measure_data
         
        