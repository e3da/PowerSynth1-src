'''
@ Quang Le: This routine is used to connect the layer stack format to formulate the appropriate response surface model
'''
from powercad.layer_stack.layer_stack_import import *
import os
from powercad.interfaces.Q3D.Ipy_script import Q3D_ipy_script

from powercad.interfaces.Q3D.Electrical import rect_q3d_box
from powercad.response_surface.Response_Surface import RS_model
from powercad.response_surface.Layer_Stack import Layer_Stack

def form_trace_model(layer_stack,Width=[1.2,40],Length=[1.2,40],freq=[10,100,10],wdir=None,savedir=None,mdl_name=None
                     ,ipy64_dir=None,options=None,): # not generic -- only works with current PowerSynth
    ''' Gather information from user inputs '''
    ls = layer_stack
    minW, maxW = Width
    minL, maxL = Length
    fmin,fmax,fstep= freq
    fmin=str(fmin) + 'k'
    fmax=str(fmax) + 'k'
    fstep= str(fstep) +'k'
    '''First we set up layer stack with material properties '''
    E1, E2, E3, E4 = (rect_q3d_box() for i in range(4))
    # -----------------------
    # Baseplate dimensions and material
    bp_W=ls.baseplate.dimensions[0]
    bp_L=ls.baseplate.dimensions[1]
    bp_t=ls.baseplate.dimensions[2]
    bp_mat=ls.baseplate.baseplate_tech.properties.id
    E1.set_size(bp_W, bp_L, bp_t)
    print bp_mat
    E1.set_name('Baseplate')
    E1.set_material(bp_mat)
    # Substrate
    sub_W = ls.substrate.dimensions[0]
    sub_L = ls.substrate.dimensions[1]
    metal_thick = ls.substrate.substrate_tech.metal_thickness
    metal_mat=ls.substrate.substrate_tech.metal_properties.id
    iso_thick = ls.substrate.substrate_tech.isolation_thickness
    iso_mat=ls.substrate.substrate_tech.isolation_properties.id
    met_W = ls.substrate.dimensions[0]-ls.substrate.ledge_width
    met_L = ls.substrate.dimensions[1]-ls.substrate.ledge_width
    ledge_width=(sub_L-met_L)/2
    bp_iso_diff=(bp_L-sub_L)/2
    bp_met_diff=ledge_width+bp_iso_diff
    # -----------------------
    # Metal1
    E2.set_size(met_W, met_L, metal_thick)
    E2.set_name('Metal1')
    E2.set_material(metal_mat)
    E2.set_pos(bp_met_diff,bp_met_diff,0)
    print metal_mat
    # -----------------------
    E3.set_size(sub_W, sub_L, iso_thick)
    E3.set_name('Substrate')  # Substrate// Dielectric
    E3.set_pos(bp_iso_diff,bp_iso_diff,0)
    E3.set_material(iso_mat)
    # -----------------------
    E4.set_size(met_W, met_L, metal_thick)
    E4.set_name('Metal2')  # Metal 2
    E4.set_material(metal_mat)
    # need to make this generic if possible in the future
    general_info = model_info.format(minW, maxW, minL, maxL, freq[0], freq[1], freq[2])
    Layer1 = layer_info.format(1, bp_mat, bp_t, bp_W, bp_L)
    Layer2 = layer_info.format(2, metal_mat, met_W, met_L, metal_thick)
    Layer3 = layer_info.format(3, iso_mat, sub_W, sub_L, iso_thick)
    Layer4 = layer_info.format(4, metal_mat, met_W, met_L, metal_thick)
    print general_info + Layer1 + Layer2 + Layer3 + Layer4
    ''' Setup Q3D layer stack, options and materials'''
    T1 = Layer_Stack()
    T1.add_Layers([E1, E2, E3, E4])
    T1.define_trace(4,[bp_W,bp_L])  # Select trace layer
    trace_high = E4.get_z()
    script1 = Q3D_ipy_script('16.2', wdir, mdl_name,wdir)  # Initialize Script Object
    script1.add_script(T1.get_all_Elayers())  # Add Topology structure to script
    script1.set_params('Width', 9, 'XSize', E4)  # Setup parameters
    script1.set_params('Length', 9, 'YSize', E4)  # Setup parameters
    script1.set_params('XTrace',9,'X',E4)
    script1.set_params('YTrace', 9, 'Y', E4)
    script1.set_params('ZTrace',trace_high, 'Z', E4)
    script1.identify_net('signal', 'Metal2', 'SignalNet1')  # Create net objects
    script1.select_source_sink('Source1', E4.get_face(2), 'Sink1', E4.get_face(4),
                               'SignalNet1')  # Select Source Sink to faces
    script1.analysis_setup()  # Set up an analysis, in this case set as default


    script1.add_freq_sweep(fmin, fmax, fstep)  # Set up frequency sweep on analysis

    mdl1 = RS_model(['W', 'L'], const=['H', 'T'])
    mdl1.set_dir(savedir)
    mdl1.set_data_bound([[minW, maxW], [minL, maxL]])
    mdl1.set_name(mdl_name)
    script1.create_report('Freq', 'ACR', 'SignalNet1', 'Source1', 'Sweep1', 1)  # Create report
    script1.update_report('Freq', 'ACL', 'SignalNet1', 'Source1', 'Sweep1', 1)
    script1.update_report('Freq', 'C', 'SignalNet1', '', 'Sweep1', 1)
    mdl1.create_uniform_DOE([10, 10], True)
    mdl1.create_DOE(2, 100)
    print mdl1.DOE
    mdl1.generate_fname()
    for [w, l] in mdl1.DOE.tolist():
        name = mdl1.mdl_name + '_W_' + str(w) + '_L_' + str(l)
        # print name
        script1.change_properties('Width', w)
        script1.change_properties('Length', l)
        print 'X',(bp_W-w)/2
        script1.change_properties('XTrace',(bp_W-w)/2)
        script1.change_properties('YTrace', (bp_L - l) / 2)
        script1.change_properties('ZTrace', trace_high)
        script1.analyze_all()  # Run analysis
        script1.export_report('Data Table 1', wdir, name)  # Export report to csv files
    script1.make()
    script1.build('C://Users//qmle//Desktop//Testing//Py_Q3D_test//IronPython//ipy64.exe')
    mdl1.set_unit('n', 'H')
    mdl1.set_sweep_unit('k', 'Hz')
    mdl1.read_file('csv', 'sweep', 90, ('Hz', 'H'),wdir)
    mdl1.build_RS_mdl('Krigging')
    mdl1.set_mdl_info(general_info + Layer1 + Layer2 + Layer3 + Layer4)

    mdl1.save_model()


model_info = '''
    Width: from {0} mm to {1} mm
    Length: from {2} mm to {3} mm
    Frequency: from {4} kHz to {5} kHz, step={6} kHz
'''

layer_info= '''
    Layer Id = {0}
        Material  = {1}
        Width = {2} mm
        Length = {3} mm
        Thickness = {4} mm
'''
if __name__=="__main__":
    dir="C://Users//qmle//Google Drive//MSCAD PowerSynth Archives//Internal//MDK//Layer Stack Quang//MDK_Review_Quang.csv"
    dir=os.path.abspath(dir)
    form_trace_model(dir)
