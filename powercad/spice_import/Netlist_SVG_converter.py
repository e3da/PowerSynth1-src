'''
Created on Jul 11, 2013

@authors: apsimms and jhmain
'''
# Notes:
# - Designed for netlists created in Cadence Design Entry CIS PSPICE (netlist input must be same format)
# - SVG file is saved in .../workspace/PowerCAD/test
# - Works with voltage sources, MOSFETs, thryristors, and diodes (no resistors, inductors, or capacitors)
#
# Design limitations:
# - Design must have 2 voltage sources
# - Assumes the first voltage source to appear in the netlist is the positive source (and the second is negative)
# - Design must have 2 or fewer gates
# - Gate control voltages must be net alias (not a gate voltage source)
# - Design may have up to 2 parallel paths between each source and output (does not support full bridge circuits)
# - Placing a net alias at the output is recommended
#
# Potential bugs:
# - Different netlist format
# - Violating any design limitations
# - Component name conflicts with a shadow node name
#
# To do:
# - Connect to GUI interface
# - Maybe organize build_graph into separate files and/or functions
# - Expand limitations and fix bugs if possible
#
# Future work notes:
# - Maybe allow user to specify positive/negative voltages, gate voltages, output in the GUI
# - Objects in SVG output file must be ungrouped to be manipulated individually in Inkscape

import os
from powercad.spice_import.get_netlist import netdata
from powercad.spice_import.build_graph import create_layout

class converter():

    def __init__(self,netfile, name):
        self.netfile = netfile
        self.name = name

    def convert(self):
        netfile = self.netfile
        name = str(self.name)
        
        #Retrieve data from netlist file
        net = netdata()
        net.netlistconverter(netfile)
        data = net.getdata()
        
        # Draw symbolic layout SVG from netlist data 
        create_layout(data, str(name))             
        
        # Set new file name
        newname = (unicode(str(name)+'.svg'), u'SVG and Netlist Files (*.svg *.net *.txt)')
        return newname
    
'''
#Test module
file_name = '12mosfet'
test_file = os.path.abspath('../../../test/' + file_name + '.txt')
test_name = os.path.abspath('../../../test/' + file_name)

def test_converter(filename,name):
    test = converter(filename,name)
    return test.convert()

print test_converter(test_file, test_name)
'''