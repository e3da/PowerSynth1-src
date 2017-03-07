'''
Created on Nov 7, 2011

@author: bxs003
'''

import os

spice_template = '''.temp {0}
.include "d.inc"
.hdl "powerMOSVA.va"
.print TRAN I(V1) I(V2) V(N003, N007)


L2 N002 N003 100n IC=0.001 

*Gate impedances
L1 N004 N0099 {1}n 
R9 N0099 N006 5
L12 N004 N00992 {1}n 
R92 N00992 N0062 5


 *  D    G    S
X1 N003 N006 N007 powerMOSVA
X2 N003 N0062 N007 powerMOSVA
* Load
R1 N001 N002 10
D1 N007 N003 diode1
D2 N007 N003 diode1
V1 N001 0 400
V2 N004 N008  0 PULSE(-5 20 0 10n 10n 10u 20u) 
L3 N007 N008 {2}n
L4 N008 0 5n

.tran 5e-9 70e-6 UIC

.end'''

netlist_name = 'pcad_netlist.sp'

def run_hspice(temp, gate_inductance, dir, out_name):

    dir_norm = os.path.normpath(dir)
    os.chdir(dir_norm)

    file_name = netlist_name
    path_name = write_net_list(temp, gate_inductance, file_name, dir)
    
    pipe = os.popen('hspice %s' % (file_name))
    text = pipe.readlines()
    pipe.flush()
    pipe.close()
    return text

def write_net_list(temp, gate_inductance, file_name, dir=''):
    
    temp_f = float(temp)
    gl = float(gate_inductance)
        
    spice_out = spice_template.format(temp_f, gl, gl)
    
    full_path = os.path.join(dir, file_name)
    spice_file = open(full_path, 'w')
    spice_file.write(spice_out)
    spice_file.close()
    
    return os.path.normpath(full_path)

if __name__ == '__main__':
    
    from pylab import figure, show, xlabel, ylabel, title, text
    from hspice_plot import *
    
    #run_hspice(110, 12, 'C:/Users/bxs003/Desktop/topology_testing/', 'yo_dawg.out')
    
    lines = run_hspice(110, 12, 'C:/Users/pxt002/Desktop/', 'yo_dawg.out')
    lines[0] = 'Run One'
    
    fig = figure()
    hspice_plot([lines], fig)
    show()
