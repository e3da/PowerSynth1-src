'''
@ Quang Le: This routine is used to connect the layer stack format to formulate the appropriate response surface model
'''
from powercad.layer_stack.layer_stack_import import *
import os
from powercad.interfaces.Q3D.Ipy_script import Q3D_ipy_script

from powercad.interfaces.Q3D.Electrical import rect_q3d_box
from powercad.response_surface.Response_Surface import RS_model
from powercad.response_surface.Layer_Stack import Layer_Stack

def form_trace_model(layer_stack_dir,options=None):
    LS=LayerStackImport(layer_stack_dir)
    LS.import_csv()
    print LS.layer_list
    '''First we set up layer stack with material properties '''
    E1, E2, E3, E4 = (rect_q3d_box() for i in range(4))
    # -----------------------
    # Baseplate
    bp_W=LS.baseplate.dimensions[0]
    bp_L=LS.baseplate.dimensions[1]
    bp_t=LS.baseplate.dimensions[3]
    E1.set_size(bp_W, bp_L, bp_t)
    E1.set_name('Baseplate')
    # Substrate
    sub_W=LS.substrate.
    # -----------------------
    # Metal1
    E2.set_size(48, 48, 0.2)
    E2.set_name('Metal1')
    # -----------------------
    E3.set_size(50, 50, 0.5)
    E3.set_name('Substrate')  # Substrate// Dielectric
    E3.set_material('Al_N')
    # -----------------------
    E4.set_size(48, 48, 0.2)
    E4.set_name('Metal2')  # Metal 2



if __name__=="__main__":
    dir="C://Users//Quang//Google Drive//MSCAD PowerSynth Archives//Internal//MDK//Layer Stack//layer_test_v4_1.csv"
    dir=os.path.abspath(dir)
    form_model(dir)
