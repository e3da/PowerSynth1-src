'''
@ qmle: This routine is used to connect the layer stack format to formulate the appropriate response surface model
'''
from powercad.layer_stack.layer_stack_import import *
import os
from powercad.interfaces.Q3D.Ipy_script import Q3D_ipy_script

from powercad.interfaces.Q3D.Electrical import rect_q3d_box
from powercad.response_surface.Response_Surface import RS_model
from powercad.response_surface.Layer_Stack import Layer_Stack
from copy import *
from powercad.general.settings.save_and_load import save_file
from powercad.general.settings.Error_messages import InputError,Notifier

def form_trace_model(layer_stack,Width=[1.2,40],Length=[1.2,40],freq=[10,100,10],wdir=None,savedir=None,mdl_name=None
                     ,env=None,options=['Q3D','mesh',False]):
    '''
    # not generic -- only works with current PowerSynth
    :param layer_stack: Layer Stack format
    :param Width:  [min , max]
    :param Length: [min , max]
    :param freq:   [min , max,step]
    :param wdir:   Working directory for file export
    :param savedir: Save direcory for model
    :param mdl_name: model name
    :param env: enviroment path ipy64 for ansys, or fasthenry
    :param options: [sim_option,DoE_option,Cap_analysis]
    :return: export [R,L,C] model to a file
    '''
    ls = layer_stack
    minW, maxW = Width
    minL, maxL = Length
    fmin,fmax,fstep= freq
    fmin=str(fmin) + 'k'
    fmax=str(fmax) + 'k'
    fstep= str(fstep) + 'k'
    sim=options[0]
    doe_mode=options[1]
    c_mode=options[2]
    '''Layer Stack info for PowerSynth'''
    # BASEPLATE
    bp_W = ls.baseplate.dimensions[0]
    bp_L = ls.baseplate.dimensions[1]
    bp_t = ls.baseplate.dimensions[2]
    bp_mat = ls.baseplate.baseplate_tech.properties.id
    # SUBSTRATE ATTACH
    sub_att_mat=ls.substrate_attach.attach_tech.properties.id
    sub_att_thick=ls.substrate_attach.thickness
    # SUBSTRATE
    sub_W = ls.substrate.dimensions[0]
    sub_L = ls.substrate.dimensions[1]
    iso_thick = ls.substrate.substrate_tech.isolation_thickness
    iso_mat = ls.substrate.substrate_tech.isolation_properties.id
    # METAL
    metal_thick = ls.substrate.substrate_tech.metal_thickness
    metal_mat = ls.substrate.substrate_tech.metal_properties.id
    met_W = ls.substrate.dimensions[0] - ls.substrate.ledge_width
    met_L = ls.substrate.dimensions[1] - ls.substrate.ledge_width
    # Compute Ledge_width, calculate dimensions differences to ensure all layer have same center
    ledge_width = (sub_L - met_L) / 2
    bp_iso_diff = (bp_L - sub_L) / 2
    bp_met_diff = ledge_width + bp_iso_diff
    '''First we set up layer stack with material properties '''
    E1, E2, E3, E4 ,E5= (rect_q3d_box() for i in range(5))  # Generalize to add fasthenry later
    # -----------------------
    # Baseplate dimensions and material

    E1.set_size(bp_W, bp_L, bp_t)
    E1.set_name('Baseplate')
    E1.set_material(bp_mat)

    # -----------------------
    #------------------------
    E2.set_size(met_W,met_L,sub_att_thick)
    E2.set_name('SA')
    E2.set_material(sub_att_mat)
    E2.set_pos(bp_met_diff, bp_met_diff, 0)
    # Metal1
    E3.set_size(met_W, met_L, metal_thick)
    E3.set_name('Metal1')
    E3.set_material(metal_mat)
    E3.set_pos(bp_met_diff,bp_met_diff,0)
    # Substrate
    E4.set_size(sub_W, sub_L, iso_thick)
    E4.set_name('Substrate')  # Substrate// Dielectric
    E4.set_pos(bp_iso_diff,bp_iso_diff,0)
    E4.set_material(iso_mat)
    # Trace
    E5.set_size(met_W, met_L, metal_thick)
    E5.set_name('Metal2')  # Metal 2
    E5.set_material(metal_mat)
    '''Model Info'''
    general_info = model_info.format(minW, maxW, minL, maxL, freq[0], freq[1], freq[2])
    Layer1 = layer_info.format(1, bp_mat, bp_t, bp_W, bp_L)
    Layer2 = layer_info.format(2, sub_att_mat, met_W, met_L, sub_att_thick)
    Layer3 = layer_info.format(3, metal_mat, met_W, met_L, metal_thick)
    Layer4 = layer_info.format(4, iso_mat, sub_W, sub_L, iso_thick)
    Layer5 = layer_info.format(5, metal_mat, met_W, met_L, metal_thick)
    pkg_info=general_info + Layer1+ Layer2 + Layer3 + Layer4 + Layer5
    
    ''' Setup Q3D layer stack, options and materials'''
    T1 = Layer_Stack()
    T1.add_Layers([E1, E2, E3, E4, E5])
    T1.define_trace(5,[bp_W,bp_L])  # Select trace layer
    trace_high = E5.get_z()
    if sim=='Q3D':
        sim_commands = Q3D_ipy_script('16.2', wdir, mdl_name,wdir)  # Initialize Script Object
        sim_commands.add_script(T1.get_all_elayers())  # Add Topology structure to script
        sim_commands.set_params('Width', 9, 'XSize', E5)  # Setup parameters
        sim_commands.set_params('Length', 9, 'YSize', E5)  # Setup parameters
        sim_commands.set_params('XTrace',9,'X',E5)
        sim_commands.set_params('YTrace', 9, 'Y', E5)
        sim_commands.set_params('ZTrace',trace_high, 'Z', E5)
        sim_commands.identify_net('signal', 'Metal2', 'SignalNet1')  # Create net objects
        sim_commands.select_source_sink('Source1', E5.get_face(2), 'Sink1', E5.get_face(4),
                                   'SignalNet1')  # Select Source Sink to faces
        sim_commands.analysis_setup(add_C=c_mode)  # Set up an analysis, in this case set as default
        sim_commands.add_freq_sweep(fmin, fmax, fstep)  # Set up frequency sweep on analysis
        sim_commands.create_report('Freq', 'ACR', 'SignalNet1', 'Source1', 'Sweep1', 1)  # Create report
        sim_commands.update_report('Freq', 'ACL', 'SignalNet1', 'Source1', 'Sweep1', 1)
        sim_commands.update_report('Freq', 'C', 'SignalNet1', '', 'Sweep1', 1)
    elif sim=='FastHenry':
        Notifier(msg='FastHenry Interface is underdevelopment',msg_name='Not supported feature')
        return

    ''' Ready to create model'''
    model_input = RS_model(['W', 'L'], const=['H', 'T'])
    model_input.set_dir(savedir)
    model_input.set_data_bound([[minW, maxW], [minL, maxL]])
    model_input.set_name(mdl_name)
    '''Set up DoE, this is fixed for now, will allow user to modify the DoE in the future'''
    if doe_mode=='mesh':
        model_input.create_uniform_DOE([5, 5], True)
    elif doe_mode=='cc':
        model_input.create_DOE(2, 100)
    model_input.generate_fname()
    '''Write the optimetric script with chosen DOE structure'''
    for [w, l] in model_input.DOE.tolist():
        name = model_input.mdl_name + '_W_' + str(w) + '_L_' + str(l)
        sim_commands.change_properties('Width', w)
        sim_commands.change_properties('Length', l)
        sim_commands.change_properties('XTrace',(bp_W-w)/2)
        sim_commands.change_properties('YTrace', (bp_L - l) / 2)
        sim_commands.change_properties('ZTrace', trace_high)
        sim_commands.analyze_all()  # Run analysis
        sim_commands.export_report('Data Table 1', wdir, name)  # Export report to csv files
    sim_commands.make()
    sim_commands.build(env)
    
    "AC INDUCTANCE"
    model_input.set_unit('n', 'H')
    model_input.set_sweep_unit('k', 'Hz')
    model_input.read_file(file_ext='csv',mode='sweep', units=('Hz', 'H'),wdir=wdir)
    model_input.build_RS_mdl('Krigging')
    LAC_model=model_input
    
    "AC RESISTANCE"
    RAC_input=RS_model()
    RAC_input=deepcopy(model_input)
    RAC_input.set_unit('u','Ohm')
    model_input.set_sweep_unit('k', 'Hz')
    RAC_input.read_file(file_ext='csv', mode='single', units=('Hz', 'Ohm'), wdir=wdir)
    RAC_input.build_RS_mdl('Krigging')
    RAC_model=RAC_input
    
    "CAPACITANCE"
    if c_mode:
        Cap_input=RS_model()
        Cap_input=deepcopy(model_input)
        Cap_input.set_unit('p', 'F')
        model_input.set_sweep_unit('k', 'Hz')
        Cap_input.read_file(file_ext='csv', mode='single', units=('Hz', 'F'), wdir=wdir)
        Cap_input.build_RS_mdl('Krigging')
        Cap_model = Cap_input
    else:
        Cap_model=None

    package={'R':RAC_model,'L':LAC_model,'C':Cap_model,'info':pkg_info}

    try:
        save_file(package,os.path.join(savedir,mdl_name+'.rsmdl'))
        Notifier(msg="Sucessfully Saved Model",msg_name="Success!")
    except:
        InputError(msg="Model was not saved")


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
