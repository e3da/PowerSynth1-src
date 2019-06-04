from powercad.corner_stitch.input_script import *

from PySide.QtGui import QFileDialog,QMainWindow


def optimization_setup(level=None,choice=None):
    if level!=0:

        if choice=='Non-guided randomization':
            print "Enter number of layouts:"

        elif choice=='NSGAII':
            print "Enter number of generations:"

        num_layouts = raw_input()

        if level==2 or level==3:
            print "Enter floorplan width:"
            W=raw_input()
            print "Enter floorplan height:"
            H=raw_input()
            size=[W,H]
        else:
            size=[None,None]

        return num_layouts,size



def test_file(input_script=None,bond_wire_info=None):
    if input_script == None:
        input_file = "C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt"  # input script location
    else:
        input_file = input_script

    ScriptMethod=ScriptInputMethod(input_file) # initializes the class with filename
    ScriptMethod.read_input_script() # reads input script and make two sections
    ScriptMethod.gather_part_route_info() #gathers part and route info
    ScriptMethod.gather_layout_info() #gathers layout info
    print ScriptMethod.size
    print len(ScriptMethod.cs_info), ScriptMethod.cs_info
    print ScriptMethod.component_to_cs_type
    ScriptMethod.update_constraint_table() # updates constraint table


    input_rects=ScriptMethod.convert_rectangle() # converts layout info to cs rectangle info
    input_info = [input_rects, ScriptMethod.size]

    # bond wire file read in
    if bond_wire_info!=None:
        bondwires=ScriptMethod.bond_wire_table(bondwire_info=bond_wire_info)
    #output format of bondwire storing
    # Bond wire table={'BW1': {'BW_object': <powercad.design.Routing_paths.BondingWires instance at 0x16F4D648>, 'Source': 'D1_Drain', 'num_wires': '4', 'Destination': 'B1', 'spacing': '0.1'}, 'BW2': {'BW....}

    #print bondwires

    app = QtGui.QApplication(sys.argv)
    window = QMainWindow()
    New_engine = New_layout_engine()
    New_engine.init_layout(input_format=input_info)
    cons_df = show_constraint_table(parent=window,cons_df=ScriptMethod.df)
    New_engine.cons_df = cons_df
    New_engine.Types = ScriptMethod.Types
    New_engine.all_components = ScriptMethod.all_components

    #New_engine.open_new_layout_engine(window=window)
    Patches, cs_sym_data =New_engine.generate_solutions(level=0, num_layouts=1, W=None, H=None, fixed_x_location=None,fixed_y_location=None, seed=None, individual=None)
    return New_engine.all_components,cs_sym_data,bondwires
    # Don't Delete these lines
    '''
    print "Enter the mode of operation:"
    level=raw_input()
    print level
    if level==0:

        fig_data,cs_sym_info=New_engine.generate_solutions(level, num_layouts=1, W=None, H=None, fixed_x_location=None, fixed_y_location=None,seed=None, individual=None, bar=False)
        print fig_data
        print cs_sym_info

    else:
        print "Enter randomization seed:"
        seed=raw_input()
        print "Choose optimization algorithm: 1. Non-guided randomization   2. NSGAII"
        opt_algo=raw_input()
        if int(opt_algo)==1:
            optimization_algorithm='Non-guided randomization'
        else:
            optimization_algorithm='NSGAII'

        num_layouts,size=optimization_setup(level=level,choice=optimization_algorithm)
        fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=size[0], H=size[1],fixed_x_location=None, fixed_y_location=None, seed=seed,individual=None, bar=False)
        print fig_data
        print cs_sym_info
    
    '''


def test_case(layout_script,bond_wire_script):

    all_components, layout_info, bondwires =test_file(input_script=layout_script,bond_wire_info=bond_wire_script)

    # you can use these info as previously
    print all_components
    print layout_info
    print bondwires


if __name__ == '__main__':
    test_case(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')

