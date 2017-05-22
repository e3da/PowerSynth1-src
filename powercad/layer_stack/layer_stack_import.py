'''
Created on Apr 22, 2017

@author: jhmain

PURPOSE:
 - This module is used to import a layer stack from a CSV file
 
INPUT: 
 - Layer stack CSV file
 
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
        
        self.baseplate_abbrev = 'B:'
        self.substrate_attach_abbrev = 'SA:'
        self.metal_abbrev = 'M:'
        self.dielectric_abbrev = 'D:'
        self.interconnect_abbrev = 'I:'
        self.component_abbrev = 'C:'
        
        self.layer_type_abbrev_dict = {}
        self.layer_type_abbrev_dict[self.baseplate_abbrev] = 'baseplate'
        self.layer_type_abbrev_dict[self.substrate_attach_abbrev] = 'substrate_attach'
        self.layer_type_abbrev_dict[self.metal_abbrev] = 'metal'
        self.layer_type_abbrev_dict[self.dielectric_abbrev] = 'dielectric'
        self.layer_type_abbrev_dict[self.interconnect_abbrev] = 'interconnect'
        self.layer_type_abbrev_dict[self.component_abbrev] = 'component'
        
        self.compatible_layer_order = ['[ignore]', 'baseplate', 'substrate_attach', 'metal', 'dielectric', 'interconnect', 'component']
        self.pos_min = 1
        self.pos_max = len(self.compatible_layer_order) - 1
        
        
    def import_csv(self):   # Top level function
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
    
    
    def check_layer_stack_compatibility(self):  # Check if layer stack in list form is compatible with PowerSynth   
        substrate_width = None
        substrate_length = None
        ledge_width = None
          
        for layer in self.layer_list:
            print '--- Checking layer: ' + str(layer)
            
            try:
                layer_type = layer[0]
                num = int(layer[1])
                name = layer[2]
                pos = int(layer[3])
            except:
                self.compatible = False
                self.error_msg = 'Unexpected layer format. A layer row must begin with the following entries: layer type, num, name, pos'
                break
            
            # Check for valid layer type and position
            if layer_type not in self.layer_type_abbrev_dict.keys():
                self.compatible = False
                self.error_msg = 'Unrecognized layer type ' + layer_type
                break
            elif pos < self.pos_min or pos > self.pos_max:
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in out-of-range position ' + str(pos) + '. Layer positions must be in the range ' + str(self.pos_min) + ' to ' + str(self.pos_max) + '.'
                break
            
            # Check for valid layer order
            if self.layer_type_abbrev_dict[layer_type] != self.compatible_layer_order[pos]:
                expected_layer_type = self.compatible_layer_order[pos]
                expected_layer_type_abbrev = self.layer_type_abbreviations_dict[expected_layer_type]
                self.compatible = False
                self.error_msg = 'Layer ' + name + ' in position ' + str(pos) + ' defined as unexpected type ' + layer_type + ' in file. The layer in this position must be type ' + expected_layer_type_abbrev + '(' + expected_layer_type + ')'
                break
               
            # Find baseplate
            if layer_type == self.baseplate_abbrev:
                try:
                    width = float(layer[4])
                    length = float(layer[5])
                    thick = float(layer[6])
                    eff_conv_coeff = int(layer[7])
                except:
                    self.compatible = False
                    self.error_msg = 'Could not find all values in baseplate layer ' + name + '. Baseplate must contain the following fields: layer type, num, name, pos, width, length, thickness, effective convection coefficient.'
                    break
                self.baseplate = BaseplateInstance((width, length, thick), eff_conv_coeff, None)
                print 'Found baseplate ' + str(width) + ', ' + str(length) + ', ' + str(thick) + ', ' + str(eff_conv_coeff)
                
            # Find substrate attach
            if layer_type == self.substrate_attach_abbrev:
                try:
                    thick = float(layer[4])
                except:
                    self.compatible = False
                    self.error_msg = 'Could not find all values in substrate attach layer ' + name + '. Substrate attach must contain the following fields: layer type, num, name, pos, thickness.'
                    break
                self.substrate_attach = SubstrateAttachInstance(thick, None)
                print 'Found substrate attach ' + str(thick)
                    
            # Find substrate 
            if layer_type == self.metal_abbrev or layer_type == self.dielectric_abbrev:
                try:
                    width = float(layer[4])
                    length = float(layer[5])
                except:
                    self.compatible = False
                    self.error_msg = 'Could not find all values in metal/dielectric layer ' + name + '. Metal/dielectric must contain the following fields: layer type, num, name, pos, width, length.'
                    break
                
                if substrate_width == None:
                    substrate_width = width
                elif width != substrate_width:
                    self.compatible = False
                    self.error_msg = 'Unexpected value for width found in metal/dielectric layer ' + name + '. Substrate layers (metal/dielectric) must have same width.'
                    break
                    
                if substrate_length == None:
                    substrate_length = length
                elif length != substrate_length:
                    self.compatible = False
                    self.error_msg = 'Unexpected value for length found in metal/dielectric layer ' + name + '. Substrate layers (metal/dielectric) must have same length.'
                    break
                print 'Found metal/dielectric ' + str(width) + ', ' + str(length)
                
            elif layer_type == self.interconnect_abbrev:
                try:
                    ledge_width = float(layer[4])
                except:
                    self.compatible = False
                    self.error_msg = 'Could not find all values in interconnect layer ' + name + '. Interconnect layers must contain the following fields: layer type, num, name, pos, ledge width.'
                    break
                print 'Found interconnect ' + str(ledge_width)
                
                
        try:
            self.substrate = SubstrateInstance((substrate_width, substrate_length), ledge_width, None)        
        except:
            self.compatible = False
            self.error_msg = 'Could not find substrate layers.'
        print 'Found substrate ' + str(width) + ', ' + str(length) + ', ' + str(ledge_width)  
                    
        # TODO - check for excess substrate layers
                
        if self.warnings != []:
            for warning in self.warnings:
                print 'WARNING: ' + warning
                
        if self.error_msg != None:
            print 'ERROR: ' + self.error_msg
            

# Module test
if __name__ == '__main__':
    
    layer_list_test = [['B:', '1', 'B1', '1', '100', '80', '8', '120'], ['SA:', '2', 'SA1', '2', '0.1', '', '', ''], ['M:', '3', 'M1', '3', '90', '70', '', ''], ['D:', '4', 'D1', '4', '90', '70', '', ''], ['I:', '5', 'M2', '5', '2', '', ''], ['C:', '6', 'C1', '6', '', '', '', '']]
    #layer_list_test.append(['M:', '7', 'M3', '7', '100', '100'])
    #layer_list_test.append(['M:', '8', 'M4', '0', '100', '100'])
    
    test = LayerStackImport(None)
    #print 'compatible layer order' + str(test.compatible_layer_order)
    test.layer_list = layer_list_test
    test.check_layer_stack_compatibility()
    print 'compatible: ' + str(test.compatible)
    
    