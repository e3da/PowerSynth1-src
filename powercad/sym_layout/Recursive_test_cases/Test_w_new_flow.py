from powercad.corner_stitch.input_script import *

from PySide.QtGui import QFileDialog,QMainWindow

def test_file(input_script=None,bond_wire_info=None):
    if input_script == None:
        input_file = "C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt"  # input script location
    else:
        input_file = input_script

    ScriptMethod=ScriptInputMethod(input_file)
    ScriptMethod.read_input_script()
    ScriptMethod.gather_part_route_info()
    ScriptMethod.gather_layout_info()
    print ScriptMethod.size
    print len(ScriptMethod.cs_info), ScriptMethod.cs_info
    print ScriptMethod.component_to_cs_type
    ScriptMethod.update_constraint_table()


    input_rects=ScriptMethod.convert_rectangle()

    input_info = [input_rects, ScriptMethod.size]
    if bond_wire_info!=None:
        bondwires=ScriptMethod.bond_wire_table(bondwire_info=bond_wire_info)
    # Bond wire table={'BW1': {'BW_object': <powercad.design.Routing_paths.BondingWires instance at 0x16F4D648>, 'Source': 'D1_Drain', 'num_wires': '4', 'Destination': 'B1', 'spacing': '0.1'}, 'BW2': {'BW....}

    print bondwires

    app = QtGui.QApplication(sys.argv)
    window = QMainWindow()
    New_engine = New_layout_engine()
    New_engine.init_layout(input_format=input_info)
    cons_df = show_constraint_table(parent=window,cons_df=ScriptMethod.df)
    New_engine.cons_df = cons_df
    New_engine.Types = ScriptMethod.Types
    New_engine.all_components = ScriptMethod.all_components
    New_engine.open_new_layout_engine(window=window)

    # engine = New_layout_engine()

    # Patches, cs_sym_data = engine.generate_solutions(level=0, num_layouts=1, W=None, H=None, fixed_x_location=None,fixed_y_location=None, seed=None, individual=None)
    # print Patches
    # return all_components,cs_sym_data


def test_case(layout_script,bond_wire_script):

    test_file(input_script=layout_script,bond_wire_info=bond_wire_script)












if __name__ == '__main__':
    test_case(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')