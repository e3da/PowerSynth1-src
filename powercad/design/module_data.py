'''
Created on Mar 4, 2013

@author: bxs003
'''

from powercad.tech_lib.test_techlib import get_baseplate, get_sub_attach, get_substrate
from powercad.design.project_structures import BaseplateInstance, SubstrateAttachInstance
from powercad.design.project_structures import SubstrateInstance, ProcessDesignRules
from powercad.thermal.fast_thermal import SublayerThermalFeatures

class ModuleData(object):
    def __init__(self):
        self.baseplate = None # BaseplateInstance obj
        self.substrate_attach = None # SubstrateAttachInstance obj
        self.substrate = None # SubstrateInstance obj
        self.design_rules = None # ProcessDesignRules obj
        self.frequency = None # Project parasitic extraction frequency (Hertz)
        self.ambient_temp = None # Project ambient temperature (Kelvin)
        
        # This information is created by the auto thermal characterization step (not the GUI)
        self.sublayers_thermal = None # Project thermal characterization data (fast_thermal.SublayerThermalFeatures)
        
    def check_data(self):
        if self.baseplate is None:
            raise Exception('Baseplate information not supplied!')
        if self.substrate_attach is None:
            raise Exception('Substrate attach information not supplied!')
        if self.substrate is None:
            raise Exception('Substrate information not supplied!')
        if self.design_rules is None:
            raise Exception('Process Design Rules not supplied!')
        if not isinstance(self.frequency, float):
            raise Exception('Analysis frequency should be supplied in floating point format!')
        if not isinstance(self.ambient_temp, float):
            raise Exception('Ambient Temperature should be supplied in floating point format!')
        
def gen_test_module_data():
    data = ModuleData()
    # dimensions, eff_conv_coeff, baseplate_tech
    data.baseplate = BaseplateInstance((91.44, 74.93, 3.81), 100, get_baseplate())
    
    # thickness, attach_tech
    data.substrate_attach = SubstrateAttachInstance(0.1, get_sub_attach())
    
    # dimensions, ledge_width, substrate_tech
    data.substrate = SubstrateInstance((83.82, 54.61), 1.27, get_substrate())
    
    data.design_rules = ProcessDesignRules(1.27, 1.27, 0.5, 0.5, 0.8, 0.3, 0.2, 0.2)
    data.frequency = 100e3 # 100 kHz
    data.ambient_temp = 300.0 # 300 Kelvin
    
    return data
    