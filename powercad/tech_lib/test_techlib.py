'''
Created on Nov 1, 2012

@author: anizam
'''
import os
import sys
import pickle

from powercad.design.library_structures import *

def open_device_model(filename):
    dir = "../../../device_models/"
    f = open(dir + filename, 'r')
    ret = f.read()
    f.close()
    return ret

def get_device():
    #name, dimensions, properties, device_type, wire_landings, power_side
    device_props = MaterialProperties('Test', 4.62, 890, 8940, None, None, None)
    bl_g = BondwireLanding((5.0, 3.41), BondwireLanding.SIGNAL)
    bl_s1 = BondwireLanding((1, 2.41), BondwireLanding.POWER)
    bl_s3 = BondwireLanding((1, 4.41), BondwireLanding.POWER)
    #device_model = open_device_model('powerMOSVA.va')
    device_model=None
    dev = Device('TEST', (6.82, 6.35, 0.8), device_props, Device.TRANSISTOR,
                 [bl_g, bl_s1, bl_s3], device_model, 1)
    return dev

def get_mosfet():
    device_props = MaterialProperties('SiC', 120.0, 750.0, 3200.0, None, None, None)
    bl_g = BondwireLanding((2.1, 1.55), BondwireLanding.SIGNAL)
    bl_s1 = BondwireLanding((0.77, 2.66), BondwireLanding.POWER)
    bl_s2 = BondwireLanding((0.77, 1.92), BondwireLanding.POWER)
    bl_s3 = BondwireLanding((0.77, 1.18), BondwireLanding.POWER)
    bl_s4 = BondwireLanding((0.77, 0.44), BondwireLanding.POWER)

    dev = Device('CPMF-1200-S160B SiC-MOS', (3.1, 3.1, 0.365), device_props, Device.TRANSISTOR,
                 [bl_g, bl_s1, bl_s2, bl_s3, bl_s4], None, 1)
    return dev

def get_diode():
    device_props = MaterialProperties('SiC', 120.0, 750.0, 3200.0, None, None, None)
    bl_s1 = BondwireLanding((0.84, 2.14), BondwireLanding.POWER)
    bl_s2 = BondwireLanding((0.84, 1.74), BondwireLanding.POWER)
    bl_s3 = BondwireLanding((0.84, 1.34), BondwireLanding.POWER)
    bl_s4 = BondwireLanding((0.84, 0.94), BondwireLanding.POWER)

    dev = Device('CPW4-1200S020B SiC-Diode', (3.08, 3.08, 0.377), device_props, Device.DIODE,
                 [bl_s1, bl_s2, bl_s3, bl_s4], None, 1)
    
    return dev

def get_dieattach():
    # properties
    '''name -- (string) name identification
    thermal_cond -- W/(m*K) -- "Thermal Conductivity"
    spec_heat_cap -- J/(kg*K) -- "Specific Heat Capacity"
    density -- kg/m^3 -- "Material Density"
    electrical_res -- (ohm*m) -- "Electrical Resistivity"
    rel_permit -- (unitless) -- "Relative Permittivity"
    rel_permeab -- (unitless) -- "Relative Permeability"'''
    die_attach_props = MaterialProperties('Pb-Sn Solder Alloy', 35.8, 130.0, 11020.0, None, None, None)
    die_attach = DieAttach(die_attach_props)
    return die_attach

def get_dieattach2():
    die_attach_props = MaterialProperties('SAC405', 62.0, 236.0, 7440.0, None, None, None)
    die_attach = DieAttach(die_attach_props)
    return die_attach

def get_substrate():
    # name, isolation_properties, metal_properties, metal_thickness, isolation_thickness
    isolation_props = MaterialProperties('MarkeTech AlN 160', 160.0, 740.0, 3250.0, None, 8.7, 2.8)
    metal_props = MaterialProperties('Aluminum', 200.0, 904.0, 2710.0, 3.0e-8, None, None)
    substrate = Substrate('Al-AlN-Al 16-25-16 mils', isolation_props, metal_props, 0.41, 0.64)
    return substrate

def get_substrate2():
    # name, isolation_properties, metal_properties, metal_thickness, isolation_thickness
    isolation_props = MaterialProperties('Al_N', 160.0, 740.0, 3250.0, None, 8.7, 2.8)
    metal_props = MaterialProperties('copper', 400.0, 386.0, 8020.0, 1.7e-8, None, None)
    substrate = Substrate('Cu-AlN-Cu 8-25-8 mils', isolation_props, metal_props, 0.2, 0.64)
    return substrate

def get_sub_attach():
    # properties
    subattach_props = MaterialProperties('Pb-Sn Solder Alloy', 35.8, 130.0, 11020.0, None, None, None)
    sub_attach = SubstrateAttach(subattach_props)
    return sub_attach

def get_sub_attach2():
    # properties
    subattach_props = MaterialProperties('SAC405', 62.0, 236.0, 7440.0, None, None, None)
    sub_attach = SubstrateAttach(subattach_props)
    return sub_attach

def get_baseplate():
    # properties
    base_props = MaterialProperties('copper', 190.0, 385.0, 9700.0, 1.70e-8, None, 1.0)
    baseplate = Baseplate(base_props)
    return baseplate

def get_power_lead():
    # name, lead_type, shape, dimensions, properties
    ld_props = MaterialProperties('Aluminium', None, None, None, 3.0e-8, None, None)
    lead = Lead('Aluminium Busbar Lead 18x5x0.5x10mm', Lead.POWER, Lead.BUSBAR, (5, 5.0, 0.5, 10.0), ld_props)
    return lead

def get_power_lead2():
    # name, lead_type, shape, dimensions, properties
    ld_props = MaterialProperties('Copper', None, None, None, 1.7e-8, None, None)
    lead = Lead('Copper Busbar Lead 7.85x2x0.5x3mm', Lead.POWER, Lead.BUSBAR, (7.85, 2.0, 0.5, 3.0), ld_props)
    return lead

def get_signal_lead():
    # name, lead_type, shape, dimensions, properties
    ld_props = MaterialProperties('Aluminium', None, None, None, 3.0e-8, None, None)
    lead = Lead('Cylindrical Aluminium Lead 1.2mm Diam.', Lead.SIGNAL, Lead.ROUND, (1.2, 10), ld_props)
    return lead

def get_signal_lead2():
    # name, lead_type, shape, dimensions, properties
    ld_props = MaterialProperties('Copper', None, None, None, 1.7e-8, None, None)
    lead = Lead('Cylindrical Copper Lead 0.75mm Diam.', Lead.SIGNAL, Lead.ROUND, (0.75, 2.5), ld_props)
    return lead

def get_signal_bondwire():
    # name, wire_type, shape, dimensions, a, b, properties
    wire_props = MaterialProperties('Aluminium', None, None, None, 3.0e-8, None, None)
    bondwire = BondWire('Aluminium Signal Bondwire 0.1mm', BondWire.SIGNAL,
                        BondWire.ROUND, 0.1, 0.2, 0.125, wire_props)
    return bondwire

def get_signal_bondwire2():
    # name, wire_type, shape, dimensions, a, b, properties
    wire_props = MaterialProperties('Copper', None, None, None, 1.7e-8, None, None)
    bondwire = BondWire('Copper Signal Bondwire 0.15mm', BondWire.SIGNAL,
                        BondWire.ROUND, 0.15, 0.7, 0.125, wire_props)
    return bondwire

def get_power_bondwire():
    # name, wire_type, shape, dimensions, a, b, properties
    wire_props = MaterialProperties('Aluminium', None, None, None, 3.0e-8, None, None)
    bondwire = BondWire('Aluminium Power Bondwire 0.3x0.2mm', BondWire.POWER, 
                        BondWire.RIBBON, (0.3, 0.2), 0.4, 0.25, wire_props)
    return bondwire

def get_power_bondwire2():
    # name, wire_type, shape, dimensions, a, b, properties
    wire_props = MaterialProperties('Copper', None, None, None, 1.7e-8, None, None)
    bondwire = BondWire('Copper Power Bondwire 0.15mm', BondWire.POWER,
                        BondWire.ROUND, 0.15, 0.7, 0.125, wire_props)
    return bondwire

def make_sub_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def pickle_those_devices():
    dir = "../../../tech_lib/"
    print dir
    test_tech_dict = {"Substrates": [get_substrate, get_substrate2],
                      "Substrate_Attaches": [get_sub_attach, get_sub_attach2],
                      "Baseplates": [get_baseplate],
                      "Die_Attaches": [get_dieattach, get_dieattach2],
                      "Layout_Selection/Device": [get_device, get_mosfet, get_diode],
                      "Layout_Selection/Lead": [get_power_lead, get_power_lead2, get_signal_lead, get_signal_lead2],
                      "Layout_Selection/Bond Wire": [get_signal_bondwire, get_signal_bondwire2, get_power_bondwire, get_power_bondwire2]
                      }
    
    for key in test_tech_dict:
        value = test_tech_dict[key]
        sub_dir = os.path.join(dir, key)
        print sub_dir
        make_sub_dir(sub_dir)
        for func in value:
            obj = func()
            if hasattr(obj, 'name'):
                print obj.name
                pickle.dump(obj, open(os.path.join(sub_dir, obj.name+".p"),"wb"))
            else:
                print obj.properties.name
                pickle.dump(obj, open(os.path.join(sub_dir, obj.properties.name+".p"),"wb"))

if __name__ == '__main__':
    pickle_those_devices()
    print "--- Pickle Complete ---"
#    get_substrate()
#    get_dieattach()
#    get_device()
#    get_sub_attach()
#    get_baseplate()
#    get_power_lead()
#    get_signal_lead()
#    get_signal_bondwire()
#    get_power_bondwire()