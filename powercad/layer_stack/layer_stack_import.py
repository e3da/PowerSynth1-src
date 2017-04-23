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
        
        self.pos_min = 1
        self.pos_max = 6
        
        
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
            
            try:
                layer_type = layer[0]
                num = int(layer[1])
                name = layer[2]
                pos = int(layer[3])
            except:
                self.compatible = False
                self.error_msg = 'Unexpected layer format. A layer row must begin with the following entries: layer type, num, name, pos'
                break
            
            # Check layer positions 
            # Must be in order B-SA-M-D-M-C (note that component layer is not implemented in PowerSynth yet)
            if pos == 1 and layer_type != 'B:':    # Layer 1: baseplate
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type baseplate B: (baseplate).'
                break
            elif pos == 2 and layer_type != 'SA:':     # Layer 2: substrate attach
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type SA: (substrate attach).'
                break
            elif pos == 3 and layer_type != 'M:':   # Layers 3: metal
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type M: (metal).'
                break
            elif pos == 4 and layer_type != 'D:':  # Layer 4: dielectric
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type D: (dielectric).'
                break
            elif pos == 5 and layer_type != 'M:':     # Layer 5: metal
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type M: (metal).'
                break
            elif pos == 6 and layer_type != 'C:':  # Layer 6: components
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type C: (components).'
                break
            elif pos < self.pos_min or pos > self.pos_max:
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in out-of-range position ' + str(pos) + '. Layer positions must be in the range ' + str(self.pos_min) + ' to ' + str(self.pos_max) + '.'
                
            # Find baseplate
            if layer_type == 'B:':
                try:
                    width = float(layer[4])
                    length = float(layer[5])
                    thick = float(layer[6])
                    eff_conv_coeff = int(layer[7])
                except:
                    self.compatible = False
                    self.error_msg = 'Expected values not found in baseplate layer ' + name + '. Baseplate must contain the following fields: layer type, num, name, pos, width, length, thickness, eff_conv_coeff.'
                    break
                self.baseplate = BaseplateInstance((width, length, thick), eff_conv_coeff, None)
                print 'Found baseplate ' + str(width) + ', ' + str(length) + ', ' + str(thick) + ', ' + str(eff_conv_coeff)
                
            # Find substrate attach
            if layer_type == 'SA:':
                try:
                    thick = float(layer[4])
                except:
                    self.compatible = False
                    self.error_msg = 'Expected values not found in substrate attach layer ' + name + '. Substrate attach must contain the following fields: layer type, num, name, pos, thickness.'
                    break
                self.substrate_attach = SubstrateAttachInstance(thick, None)
                print 'Found substrate attach ' + str(thick)
                    
            # Find substrate 
            if layer_type == 'M:' or layer_type == 'D:':
                try:
                    width = float(layer[4])
                    length = float(layer[5])
                except:
                    self.compatible = False
                    self.error_msg = 'Expected values not found in metal/dielectric layer ' + name + '. Metal/dielectric must contain the following fields: layer type, num, name, pos, width, length.'
                    break
                
                if self.substrate == None:
                    self.substrate = SubstrateInstance((width, length), 2, None)
                    self.warnings.append('Substrate property ledge_width has initialized to a default value of 2. This value can be changed from the module stack section in the main window.')
                    print 'Found substrate ' + str(width) + ', ' + str(length) + ', ' + str(2)  
                else:
                    if width != self.substrate.dimensions[0]:
                        self.compatible = False
                        self.error_msg = 'Unexpected value for width found in metal/dielectric layer ' + name + '. Substrate layers (metal/dielectric) must have same length.'
                        break
                    elif length != self.substrate.dimensions[1]:
                        self.compatible = False
                        self.error_msg = 'Unexpected value for width found in metal/dielectric layer ' + name + '. Substrate layers (metal/dielectric) must have same length.'
                        break 
                    else:
                        print 'Found metal/dielectric layer matching existing substrate layer'  
                        # TODO - check for excess substrate layers
                
        if self.warnings != []:
            for warning in self.warnings:
                print 'WARNING: ' + warning
                
        if self.error_msg != None:
            print 'ERROR: ' + self.error_msg
            

# Module test
if __name__ == '__main__':
    
    layer_list_test = [['B:', '1', 'B1', '1', '100', '80', '8', '120'], ['SA:', '2', 'SA1', '2', '0.1', '', '', ''], ['M:', '3', 'M1', '3', '90', '70', '', ''], ['D:', '4', 'D1', '4', '90', '70', '', ''], ['M:', '5', 'M2', '5', '90', '70', '', ''], ['C:', '6', 'C1', '6', '', '', '', '']]
    #layer_list_test.append(['M:', '7', 'M3', '7', '100', '100'])
    #layer_list_test.append(['M:', '8', 'M4', '0', '100', '100'])
    
    test = LayerStackImport(None)
    test.layer_list = layer_list_test
    test.check_layer_stack_compatibility()
    print 'compatible: ' + str(test.compatible)
    
    