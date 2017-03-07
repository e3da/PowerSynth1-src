'''
Created on Jul 11, 2013

@authors: apsimms and jhmain
'''
# Notes:
# - Generates a symbolic layout SVG from a SPICE netlist
# - Designed for netlists created in Cadence Design Entry CIS PSPICE (netlist input must be same format)
# - Works with voltage sources, MOSFETs, thryristors, and diodes
# - Integrated into New Project Dialog GUI 
# - User enters positive source, negative source, and output node names in GUI
#
# Design Rules:
# - User must define positive source, negative source, and output node
# - Design must have 2 or fewer gate signal leads
# - Design must have only 1 device on each path from source lead to output
# - Design cannot contain resistors, inductors, or capacitors
#
# Future work:
# - Add GUI error messages or flags for exceptions and warnings
# - Maybe change symb/net file path to file icon and name (GUI)
# - Run full optimization process from netlist input


from powercad.spice_import.get_netlist import Netdata
from powercad.spice_import.build_graph import LayoutBuilder

class converter():

    def __init__(self,netfile, name):
        self.netfile = netfile
        self.name = name

    def convert(self, vp='', vn='', output_node=''):
        netfile = self.netfile
        name = str(self.name)
        
        # Retrieve data from netlist file
        Net = Netdata()
        Net.netlistconverter(netfile)
        data = Net.getdata()
        
        # Draw symbolic layout SVG from netlist data 
        Layout = LayoutBuilder(data, str(name), vp, vn, output_node)
        Layout.generate_symbolic_layout()
        
        # Set new file name
        newname = (unicode(str(name)+'.svg'), u'SVG and Netlist Files (*.svg *.net *.txt)')
        return newname
    

# Test module (test file directory is /workspace/PowerCAD/test)
if __name__ == '__main__':
    import os
    file_name = '12mosfet'
    test_file = os.path.abspath('../../../test/' + file_name + '.txt')
    test_name = os.path.abspath('../../../test/' + file_name)
    
    def test_converter(filename,name):
        test = converter(filename,name)
        return test.convert('V1', 'V2', 'V0')
    
    print test_converter(test_file, test_name)
