'''
Created on Apr 16, 2013

@author: bxs003
'''

import os
import subprocess

import numpy as np

from powercad.general.settings.settings import ELMER_BIN_PATH

elmer_sif = """
CHECK KEYWORDS Warn

Header
  Mesh DB "." "{mesh_name}"
End

Simulation
  Min Output Level = 0
  Max Output Level = 31
  Output Caller = True

  Coordinate System = "Cartesian 3D"
  Coordinate Mapping(3) = 1 2 3

  Simulation Type = "Steady State"
  Steady State Max Iterations = 10
  Steady State Min Iterations = 5
  Output Intervals = 1

  Output File = "{data_name}.dat"
  Post File = "{data_name}.ep"
End

Constants
  Gravity(4) = 0 -1 0 9.82
  Stefan Boltzmann = 5.67e-08
End

{body_listing}

Equation 1
  Name = "Equation1"
  Heat Equation = True
  Active Solvers(2) = 1 2
End

Solver 1
  Exec Solver = "Always"
  Equation = "Heat Equation"
  Variable = "Temperature"
  Variable Dofs = 1
  Linear System Solver = "Iterative"
  Linear System Iterative Method = "TFQMR"
  Linear System Max Iterations = 5000
  Linear System Convergence Tolerance = {conv_tol}
  Linear System Abort Not Converged = True
  Linear System Preconditioning = "ILU0"
  Linear System Residual Output = 1
  Steady State Convergence Tolerance = {conv_tol}
  Stabilize = True
  Nonlinear System Convergence Tolerance = 1.0e-05
  Nonlinear System Max Iterations = 1
  Nonlinear System Newton After Iterations = 3
  Nonlinear System Newton After Tolerance = 1.0e-02
  Nonlinear System Relaxation Factor = 1.0
End

Solver 2
  Exec Solver = "Always"
  Equation = "Flux Compute"
  Procedure = "FluxSolver" "FluxSolver"
  Average Within Materials = Logical True
  Calculate Flux = Logical True
  Linear System Solver = "Iterative"
  Linear System Iterative Method = "cg"
  Linear System Preconditioning = ILU0
  Linear System Residual Output = 10
  Linear System Max Iterations = Integer 500
  Linear System Convergence Tolerance = 1.0e-10
End

{material_listing}

Boundary Condition 1
  Name = "DeviceLoad"
  Target Boundaries(1) = 2
  Heat Flux BC = Logical True
  Heat Flux = {heat_flux}
End

Boundary Condition 2
  Name = "Cooling"
  Target Boundaries(1) = 1
  Heat Flux BC = Logical True
  External Temperature = {ambient}
  Heat Transfer Coefficient = {heat_transfer}
End
"""

body_str = """
Body {id}
  Equation = 1
  Material = {id}
End
"""

material_str = """
Material {id}
  Density = {density}
  Heat Conductivity = {heat_cond}
End



"""

def write_module_elmer_sif(directory, sif_fn, data_name, mesh_name, materials, load, ambient, heat_transfer, device_dim, conv_tol):
    """
    Generates an Elmer sif FEM problem description.
    
    Keyword Arguments:
        directory -- file path for sif file
        sif_fn -- .sif filename
        data_name -- the output data filename (creates two files data_name.ep, data_name.dat)
        mesh_name -- the input mesh filename (a folder created by ElmerGrid)
        materials -- a list of tuples (density, heat cond.) in this order:
                     baseplate, sub_attach, metal, isolation, die_attach, device
        load -- wattage given to the device for characterization (Watt)
        ambient -- ambient temperature for characterization (Kelvin)
        heat_transfer -- heat transfer coefficient for approx. convection (at bottom baseplate)
        device_dim -- the characterization device's dimensions (mm)
        conv_tol -- the convergence tolerence of the simulation
        
    Outputs:
        A .sif file representing a module
    """
    
    i = 1
    material_listing = ""
    body_listing = ""
    for material in materials:
        material_listing += material_str.format(id=i, density=material[0], heat_cond=material[1])
        body_listing += body_str.format(id=i)
        i += 1
        
    heat_flux = load/(device_dim[0]*device_dim[1]*1e-6)
    sif_string = elmer_sif.format(data_name=data_name, mesh_name=mesh_name, body_listing=body_listing, 
                                  material_listing=material_listing, ambient=ambient, 
                                  heat_transfer=heat_transfer, heat_flux=heat_flux, conv_tol=str(conv_tol))
    
    sif_path = os.path.join(directory, sif_fn)
    f = open(sif_path, 'w')
    f.write(sif_string)
    f.close()
    
def elmer_solve(directory, sif_fn, mesh_fn):
    # Write Elmer start file (points elmer to sif file)
    f = open(os.path.join(directory, "ELMERSOLVER_STARTINFO"), 'w')
    f.write(sif_fn+'\n')
    f.write("1\n")
    f.close()
    #print "ELMERSOLVER_STARTINFO file written"    
    # Run ElmerGrid on msh file
    print 'Run ElmerGrid'
    exec_path = os.path.join(ELMER_BIN_PATH, "ElmerGrid").replace("/","\\")
    
    print "exec_path= ", exec_path
    args = [exec_path, "14", "2", mesh_fn] 
    print "Popen", args, subprocess.PIPE, directory
    
    p = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=directory)
    print "subprocess.Popen() completed"
    stdout, stderr = p.communicate()
    print stdout, stderr
    if stdout.count("The opening of the mesh file thermal_char.msh failed!") > 0:
        raise Exception("The opening of the mesh file failed! (Check permissions on temp data directory)")
    print stdout
    # Run ElmerSolver
    
    print 'Run ElmerSolver'
    print ELMER_BIN_PATH
    exec_path = os.path.join(ELMER_BIN_PATH, "ElmerSolver").replace("/","\\")
    args = [exec_path]
    print args
    p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, cwd=directory)
    stdout, stderr = p.communicate()
    print stdout,stderr
    if stdout.count("Failed convergence tolerances.") > 0:
        print stdout
        raise Exception("Thermal characterization FEM model failed to converge!")
    elif stdout.count("Failed") > 0:
        print stdout
        raise Exception("Thermal characterization failed!")
    
    
def get_nodes_near_z_value(data_path, z_value, tol):
    f = open(data_path, 'r')
    total_nodes = int(f.readline().split()[0])
    f.readline() # skip this line
    
    xs = []
    ys = []
    nodes = []
    # Read in nodes
    num = 0
    for i in xrange(0,total_nodes):
        line_split = f.readline().split()
        x = float(line_split[0])
        y = float(line_split[1])
        z = float(line_split[2])
        if z <= z_value+tol and z >= z_value-tol:
            xs.append(x)
            ys.append(y)
            nodes.append(i)
        
    # Find data
    found = False
    while(not found):
        line_split = f.readline().split()
        if line_split[0] == '#time' and line_split[1] == '1':
            found = True
            
    # Read data
    t_temp = []
    t_z_flux = []
    for i in xrange(0,total_nodes):
        line_split = f.readline().split()
        temp = float(line_split[0])
        t_temp.append(temp)
        flux_z = float(line_split[3])
        t_z_flux.append(flux_z)
    
    f.close()
    
    # Filter data
    temp = []
    z_flux = []
    for node in nodes:
        temp.append(t_temp[node])
        z_flux.append(t_z_flux[node])
    
    return np.array(xs), np.array(ys), np.array(temp), np.array(z_flux)

if __name__ == '__main__':
    mesh_name = 'thermal_char'
    data_name = 'data'
    sif_name = 'thermal_char.sif'
    directory = r"C:\Users\qmle\Desktop\Testing\ElmerSif"
    
    materials = [(5000.0, 100.0), (6000.0, 200.0),
                 (7000.0, 300.0), (8000.0, 400.0),
                 (9000.0, 500.0), (10e3, 600.0), (11e3, 3.69)]
    
    write_module_elmer_sif(directory, sif_name, data_name, mesh_name, materials, 30.0, 300.0, 100.0, (4.8, 2.4), 1e-3)
    elmer_solve(directory, sif_name, mesh_name)
    data_path = os.path.join(directory, mesh_name, data_name+'.ep')
    xs, ys, temp, z_flux = get_nodes_near_z_value(data_path, 5.84e-3, 1e-7)
    
    # Do a little checking
    import numpy
    xs = numpy.array(xs)
    print numpy.max(xs)
    