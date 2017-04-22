'''
Created on Apr 22, 2017

@author: jhmain
'''

import os
import csv

from powercad.design.project_structures import BaseplateInstance, SubstrateAttachInstance, SubstrateInstance

class LayerStackImport:
    
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.layer_list = []
        
        self.baseplate = None
        self.substrate_attach = None
        self.substrate = None
        
        self.compatible = True
        self.warnings = []
        self.error_msg = None
        
        
    def import_csv(self):   # Top level function to import layer stack from a CSV File
        self.read_from_csv()
        self.check_layer_stack_compatibility()
        
        
    def read_from_csv(self):    # Get layer stack in list form from the CSV file
        infile = open(os.path.abspath(self.csv_file[0]))
        self.layer_list = []
        layer_reader = csv.reader(infile)
        for row in layer_reader:
            if row[0][0] != '#':    # Ignore header rows (designated by '#' symbol)
                self.layer_list.append(row)
        infile.close()
    
    
    def check_layer_stack_compatibility(self):  # Check if layer stack contained in layer_list is compatible with PowerSynth
        for layer in self.layer_list:
            print '----- layer: ' + str(layer)
            layer_type = layer[0]
            num = int(layer[1])
            name = layer[2]
            pos = int(layer[3])
            
            # Check layer positions 
            # Must be in order B-SA-M-D-M-C (note that component layer is not implemented in PowerSynth yet)
            if pos == 1 and layer_type != 'B:':    # Layer 1: baseplate
                self.compatible = False
                self.error_msg = 'Layer 1 defined as unexpected type ' + layer_type + ' in file. This layer must be type baseplate B: (baseplate).'
                break
            elif pos == 2 and layer_type != 'SA:':     # Layer 2: substrate attach
                self.compatible = False
                self.error_msg = 'Layer 2 defined as unexpected type ' + layer_type + ' in file. This layer must be type SA: (substrate attach).'
                break
            elif pos == 3 and layer_type != 'M:':   # Layers 3: metal
                self.compatible = False
                self.error_msg = 'Layer 3 defined as unexpected type ' + layer_type + ' in file. This layer must be type M: (metal).'
                break
            elif pos == 4 and layer_type != 'D:':  # Layer 4: dielectric
                self.compatible = False
                self.error_msg = 'Layer 4 defined as unexpected type ' + layer_type + ' in file. This layer must be type D: (dielectric).'
                break
            elif pos == 5 and layer_type != 'M:':     # Layer 5: metal
                self.compatible = False
                self.error_msg = 'Layer 5 defined as unexpected type ' + layer_type + ' in file. This layer must be type M: (metal).'
                break
            elif pos == 6 and layer_type != 'C:':  # Layer 6: components
                self.compatible = False
                self.error_msg = 'Layer 6 defined as unexpected type ' + layer_type + ' in file. This layer must be type C: (components).'
                break
            elif pos < 1 or pos > 6:
                self.warnings.append('Layer ' + name + ' position out of range. This layer will be ignored')
                
            else:
                print 'layer passes'
                
        if self.warnings != []:
            for warning in self.warnings:
                print 'WARNING: ' + warning
                
        if self.error_msg != None:
            print 'ERROR: ' + self.error_msg
            

# Module test
if __name__ == '__main__':
    
    layer_list = [['B:', '1', 'B1', '1', '100', '80', '8', '120'], ['SA:', '2', 'SA1', '2', '0.1', '', '', ''], ['M:', '3', 'M1', '3', '90', '70', '', ''], ['D:', '4', 'D1', '4', '90', '70', '', ''], ['M:', '5', 'M2', '5', '90', '70', '', ''], ['C:', '6', 'C1', '6', '', '', '', '']]
    layer_list.append(['M:', '7', 'M3', '7', '100', '100'])
    layer_list.append(['M:', '8', 'M4', '0', '100', '100'])
    
    test = LayerStackImport(None)
    test.layer_stack_list = layer_list
    test.check_layer_stack_compatibility()
    print 'compatible: ' + str(test.compatible)
    
    