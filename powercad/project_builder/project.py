'''
Created on Oct 10, 2012

@author: pxt002
'''

from powercad.design.module_data import ModuleData
from powercad.general.settings.settings import DEFAULT_TECH_LIB_DIR

class Project:
    def __init__(self, name, directory, tech_lib_dir = DEFAULT_TECH_LIB_DIR, netlist=None,symb_layout=None):
        """
        Keyword arguments:
            name -- project name
            directory -- directory in which to save all project files
            symb_layout -- SymbolicLayout object for the project
            module_data -- module data object for the project (holds material info. etc.)
            num_gen -- number of generations for optimization run
            deviceTable -- list of components in system
        """
        self.layout_engine = "SL"
        self.netlist=netlist
        self.name = name
        self.directory = directory
        self.tech_lib_dir = tech_lib_dir
        self.tbl_bondwire_connect=None
        self.layer_stack_file =None
        self.symb_layout = symb_layout # this is for old layout engine
        self.module_data = ModuleData()
        self.sym_info={} # This is for new layout engine

        self.solutions = [] # list of saved solutions obtained from Solution Browser
#        self.curr_sol = None # solution object to get passed back to main window

        # Number of optimization generations to run
        self.num_gen = 100

    def add_solution(self, solution):
        if self.solutions is None:
            self.solutions = [solution]
        else:
            self.solutions.append(solution)
    def add_symb(self,sym_info,name):
        self.sym_info[name]=sym_info

if __name__ == '__main__':
    print('unit testing the project')