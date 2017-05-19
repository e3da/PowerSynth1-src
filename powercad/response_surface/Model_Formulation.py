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



if __name__=="__main__":
    dir="C://Users//Quang//Google Drive//MSCAD PowerSynth Archives//Internal//MDK//Layer Stack//layer_test_v4_1.csv"
    dir=os.path.abspath(dir)
    form_model(dir)
