from powercad.corner_stitch.input_script import *
import cProfile
import pstats
from timeit import default_timer as timer
from powercad.electrical_mdl.e_mesh import *
from powercad.electrical_mdl.spice_eval.rl_mat_eval import *
from powercad.design.parts import *
from powercad.electrical_mdl.cornerstitch_API import *
from powercad.parasitics.mdl_compare import load_mdl
from powercad.electrical_mdl.e_netlist import ENetlist
from powercad.general.data_struct.util import draw_rect_list


# This is the initial attempt to link between layout engine and electrical model



def test_half_bridge1():
    print "test half bridge 1"
    file = os.path.abspath("C:\Users\qmle\Desktop\New_Layout_Engine\New_design_flow\Halfbridge1.txt")
    component_list, layout_info = test_file(input_script=file)
    layer_to_z = {'T': [0, 0.2], 'D': [0.2, 0], 'B': [0.2, 0],
                  'L': [0.2, 0]}  # key is info for layout type, value --[z,dz]

    # Prepare new data input format to make it easy to search
    comp_dict={}
    for comp in component_list:
        print comp.layout_component_id
        comp_dict[comp.layout_component_id]=comp

    layout_data = layout_info[0].values()[0]
    print layout_data
    flow_api = CS_API(comp_dict=comp_dict, layout_data=layout_data, layer_to_z=layer_to_z)
    flow_api.form_connection_table()
    flow_api.read_parts_to_sheets()


if __name__ == '__main__':
    test_half_bridge1()