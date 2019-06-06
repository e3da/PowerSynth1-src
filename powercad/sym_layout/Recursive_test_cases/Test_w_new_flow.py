from powercad.corner_stitch.input_script import *
from powercad.corner_stitch.cs_solution import *
from easygui import *
from PySide.QtGui import QFileDialog,QMainWindow
import glob
from powercad.corner_stitch.optimization_algorithm_support import new_engine_opt
from powercad.corner_stitch.fixed_location_setup import *




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


    try:
        app = QtGui.QApplication(sys.argv)
    except:
        pass
    window = QMainWindow()
    New_engine = New_layout_engine()
    New_engine.init_layout(input_format=input_info)
    cons_df = show_constraint_table(parent=window,cons_df=ScriptMethod.df)
    New_engine.cons_df = cons_df
    New_engine.Types = ScriptMethod.Types
    New_engine.all_components = ScriptMethod.all_components
    New_engine.init_size=ScriptMethod.size


    #New_engine.open_new_layout_engine(window=window)
    Patches, cs_sym_data =New_engine.generate_solutions(level=0, num_layouts=1, W=None, H=None, fixed_x_location=None,fixed_y_location=None, seed=None, individual=None)

    return New_engine,New_engine.all_components,cs_sym_data,bondwires,Patches

def save_layouts(Layout_Rects, count,db):
    print Layout_Rects

    data=[]

    for k,v in Layout_Rects.items():
        for R_in in v:
            data.append(R_in)

        data.append([k[0], k[1]])

    l_data = [count, data]
    directory=os.path.dirname(db)
    temp_file = directory + '/out.txt'

    with open(temp_file, 'wb') as f:
        f.writelines(["%s\n" % item for item in data])
        # f.write(''.join(chr(i) for i in range(data)))
    conn = create_connection(db)
    with conn:
        insert_record(conn, l_data, temp_file)
    conn.close()


def assign_fixed_locations(parent,New_engine):  # Fixed Locations (for mode-3)
    fixed_locations = Fixed_locations_Dialog(parent=parent,engine=New_engine)
    fixed_locations.set_node_id(New_engine.init_data[2][1]) # passing the graph
    fixed_locations.show()
    fixed_locations.exec_()

def settingup_db():
    database = os.path.join(os.getcwd(), 'layouts_db')
    filelist = glob.glob(os.path.join(database + '/*'))
    # print filelist
    for f in filelist:
        try:
            os.remove(f)
        except:
            print "can't remove file"

    if not os.path.exists(database):
        os.makedirs(database)

    db = database + '/' + 'layout.db'
    conn = create_connection(db)
    with conn:
        create_table(conn)
    conn.close()
    return db

def cmd_mode(layout_script=None,bond_wire_script=None):
    '''


    :return:
    '''
    '''
    
    '''
    if layout_script==None and bond_wire_script==None:
        print "Enter layout input script location:"
        layout_input = raw_input()
        print "Enter Bonding wire script location"
        bondwire_info = raw_input()
    else:
        layout_input = layout_script
        bondwire_info = bond_wire_script
    all_components, layout_info,bondwires,New_engine =test_case(layout_script=layout_input,bond_wire_script=bondwire_info)

    print layout_info



    #optimization_setup() # implement later



    while(1):
        msg = "Enter your choice:"
        title = "PowerSynth Usage Options"
        choices = ["Layout generation", "Single layout evaluation", "Layout Optimization","Quit"]
        choice = choicebox(msg, title, choices)

        if choice=="Layout generation":
            Solutions=generate_optimize_layout(New_engine,optimization=False)
            print "Sol",Solutions
        elif choice=="Single layout evaluation":
            msg = "Enter your choice:"
            title = "Single layout evaluation"
            choices = ["Initial input layout evaluation", "Upload new layout"]
            choice = choicebox(msg, title, choices)
            if choice=="Initial input layout evaluation":
                patch_dict=New_engine.init_data[0]

                fig_dict={(New_engine.init_size[0],New_engine.init_size[1]):[]}
                for k,v in patch_dict:
                    fig_dict[(New_engine.init_size[0],New_engine.init_size[1])].append(v)
                fig_data = [fig_dict]
                init_rects={}
                for k,v in New_engine.init_data[1].items():
                    rects=[]
                    for i in v:
                        rect=Rectangle(x=i[0],y=i[1],width=i[2],height=i[3],type=i[4])
                        rects.append(rect)
                    init_rects[k]=rects

                cs_sym_info = [{(New_engine.init_size[0]*1000,New_engine.init_size[1]*1000):init_rects}]
                print cs_sym_info
                opt_problem = new_engine_opt(engine=New_engine, W=New_engine.init_size[0], H=New_engine.init_size[1], seed=None, level=2, method=None)

                perf_values=opt_problem.eval_layout()
                #print perf_values


            else:
                print "Enter layout input script location:"
                layout_input = raw_input()
                print "Enter Bonding wire script location"
                bondwire_info = raw_input()
                all_components, layout_info, bondwires, New_engine = test_case(layout_script=layout_input,bond_wire_script=bondwire_info)
                patch_dict = New_engine.init_data[0]

                fig_dict = {(New_engine.init_size[0], New_engine.init_size[1]): []}
                for k, v in patch_dict:
                    fig_dict[(New_engine.init_size[0], New_engine.init_size[1])].append(v)
                fig_data = [fig_dict]
                init_rects = {}
                for k, v in New_engine.init_data[1].items():
                    rects = []
                    for i in v:
                        rect = Rectangle(x=i[0], y=i[1], width=i[2], height=i[3], type=i[4])
                        rects.append(rect)
                    init_rects[k] = rects

                cs_sym_info = [{(New_engine.init_size[0] * 1000, New_engine.init_size[1] * 1000): init_rects}]

                opt_problem = new_engine_opt(engine=New_engine, W=New_engine.init_size[0], H=New_engine.init_size[1], seed=None,
                                             level=2, method=None)
                perf_values = opt_problem.eval_layout()
                #print perf_values

            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None  # perf_values should go here
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)

            db=settingup_db()
            print fig_data
            for i in range(len(fig_data)):
                save_layouts(fig_data[i], count=i, db=db)

            print "Sol",Solutions
        elif choice=="Layout Optimization":
            Solutions=generate_optimize_layout(New_engine, optimization=True)  # list of cs_solution objects
            print "Sol",Solutions
        elif choice=="Quit":
            break
            exit()

def generate_optimize_layout(New_engine,optimization=True):


    msg = "Enter the mode of operation:"
    title = "Layout Generation Modes"
    choices = ["Minimum-sized layout", "Variable-sized layout", "Fixed-sized layout", "Fixed-sized with fixed location"]
    choice = choicebox(msg, title, choices)


    if choice=="Minimum-sized layout":
        level=0
    elif choice=="Variable-sized layout":
        level=1
    elif choice=="Fixed-sized layout":
        level=2
    elif choice=="Fixed-sized with fixed location":
        level=3

    db=settingup_db()

    if level == 0:

        fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=1, W=None, H=None,fixed_x_location=None, fixed_y_location=None, seed=None,individual=None, bar=False)


        if optimization==True:
            opt_problem = new_engine_opt(engine=New_engine, W=None, H=None, seed=None, level=level, method=None)
            results = []
            for i in range(len(cs_sym_info)):
                perf_values = opt_problem.eval_layout()
                results.append([fig_data[i], cs_sym_info[i]])
                for j in range(len(perf_values)):
                    results[i].append(perf_values[j])
        Solutions=[]
        for i in range(len(cs_sym_info)):
            name='Layout_'+str(i)
            solution=CornerStitchSolution(name=name)
            solution.params=None
            solution.layout_info=cs_sym_info[i]
            solution.abstract_info=solution.form_abs_obj_rect_dict()
            Solutions.append(solution)


        for i in range(len(fig_data)):
            save_layouts(fig_data[i],count=i,db=db)



    elif level==1:
        print "Enter information for Variable-sized layout generation"
        print "Enter randomization seed:"
        seed=raw_input()
        try:
            seed=int(seed)
        except:
            print "Please enter an integer"

        if optimization==True:
            msg = "Choose an optimization algorithm:"
            title = "Optimization Algorithm Options"
            choices = ["Non-guided randomization", "Genetic Algorithm (NSGAII)", "Weighted sum", "Simulated annealing"]
            choice = choicebox(msg, title, choices)

            if choice=="Non-guided randomization":
                optimization_algorithm="NG_RANDOM"
                print "Enter desired number of solutions:"
                num_layouts = raw_input()
                try:
                    num_layouts = int(num_layouts)
                except:
                    print "Please enter an integer"
                fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=None, H=None,fixed_x_location=None, fixed_y_location=None,seed=seed,individual=None, bar=False)


                opt_problem = new_engine_opt(engine=New_engine, W=None, H=None, seed=seed, level=level, method=None)
                results=[]
                for i in range(len(cs_sym_info)):
                    perf_values=opt_problem.eval_layout()
                    results.append([fig_data[i],cs_sym_info[i]])
                    for j in range(len(perf_values)):
                        results[i].append(perf_values[j])


                #fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=None, H=None,fixed_x_location=None, fixed_y_location=None, seed=seed,individual=None, bar=False)

                Solutions = []
                for i in range(len(cs_sym_info)):
                    name = 'Layout_' + str(i)
                    solution = CornerStitchSolution(name=name)
                    solution.params = None
                    solution.layout_info = cs_sym_info[i]
                    solution.abstract_info = solution.form_abs_obj_rect_dict()
                    Solutions.append(solution)

                for i in range(len(fig_data)):
                    save_layouts(fig_data[i], count=i, db=db)

            else:
                if choice=="Genetic Algorithm (NSGAII)":
                    print "Enter desired number of generations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    #optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=New_engine, W=None, H=None,seed=seed,level=level,method="NSGAII")
                    opt_problem.num_measure=2 #number of performance metrics
                    opt_problem.num_gen=num_layouts # number of generations
                    results=opt_problem.optimize() # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]


                elif choice== "Weighted sum":
                    #optimization_algorithm="W_S"
                    print "Enter desired number of maximum iterations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter number of interval for weights to the objectives:"
                    num_disc=raw_input()
                    try:
                        num_disc = int(num_disc)
                    except:
                        print "Please enter an integer"

                    opt_problem = new_engine_opt(engine=New_engine, W=None, H=None, seed=seed, level=level, method="FMINCON")
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc=num_disc
                    results = opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                elif choice=="Simulated annealing":
                    #optimization_algorithm="SA"
                    print "Enter desired number of steps:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter initial temperature (High):"
                    temp_init = raw_input()
                    try:
                        temp_init = float(temp_init)
                    except:
                        print "Please enter a valid Temperature"
                    opt_problem = new_engine_opt(engine=New_engine, W=None, H=None, seed=seed, level=level, method="SA")
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init=temp_init # initial temperature
                    results = opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]


                cs_sym_info = []
                fig_data = []
                for i in range(len(results)):
                    cs_sym_info.append(results[i][1])
                    fig_data.append(results[i][0])


                Solutions = []
                for i in range(len(cs_sym_info)):
                    name = 'Layout_' + str(i)
                    solution = CornerStitchSolution(name=name)
                    solution.params = None
                    solution.layout_info = cs_sym_info[i][0]
                    solution.abstract_info = solution.form_abs_obj_rect_dict()
                    Solutions.append(solution)

                for i in range(len(fig_data)):
                    save_layouts(fig_data[i][0], count=i, db=db)
        else:
            print "Enter desired number of solutions:"
            num_layouts = raw_input()
            try:
                num_layouts = int(num_layouts)
            except:
                print "Please enter an integer"
            fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=None, H=None,
                                                                  fixed_x_location=None, fixed_y_location=None,
                                                                  seed=seed, individual=None, bar=False)


            # fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=None, H=None,fixed_x_location=None, fixed_y_location=None, seed=seed,individual=None, bar=False)

            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)

            for i in range(len(fig_data)):
                save_layouts(fig_data[i], count=i, db=db)

    elif level==2:

        print "Enter information for Fixed-sized layout generation"
        print "Floorplan Width:"
        width = raw_input()
        width = float(width)*1000
        print "Floorplan Height:"
        height = raw_input()
        height = float(height)*1000
        print "Enter randomization seed:"
        seed = raw_input()
        try:
            seed = int(seed)
        except:
            print "Please enter an integer"

        if optimization==True:
            msg = "Choose an optimization algorithm:"
            title = "Optimization Algorithm Options"
            choices = ["Non-guided randomization", "Genetic Algorithm (NSGAII)", "Weighted sum","Simulated annealing"]
            choice = choicebox(msg, title, choices)
            if choice=="Non-guided randomization":
                optimization_algorithm="NG_RANDOM"
                print "Enter desired number of solutions:"
                num_layouts = raw_input()
                try:
                    num_layouts = int(num_layouts)
                except:
                    print "Please enter an integer"
                fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=width, H=height,fixed_x_location=None, fixed_y_location=None,
                                                                      seed=seed,individual=None, bar=False)

                opt_problem = new_engine_opt(engine=New_engine, W=width, H=height, seed=seed, level=level, method=None)
                results=[]
                for i in range(len(cs_sym_info)):
                    perf_values=opt_problem.eval_layout()
                    results.append([fig_data[i],cs_sym_info[i]])
                    for j in range(len(perf_values)):
                        results[i].append(perf_values[j])


                Solutions = []
                for i in range(len(cs_sym_info)):
                    name = 'Layout_' + str(i)
                    solution = CornerStitchSolution(name=name)
                    solution.params = None
                    solution.layout_info = cs_sym_info[i]
                    solution.abstract_info = solution.form_abs_obj_rect_dict()
                    Solutions.append(solution)

                for i in range(len(fig_data)):
                    save_layouts(fig_data[i], count=i, db=db)

            else:
                if choice=="Genetic Algorithm (NSGAII)":
                    print "Enter desired number of generations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    #optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=New_engine, W=width, H=height,seed=seed,level=level,method="NSGAII")
                    opt_problem.num_measure=2 #number of performance metrics
                    opt_problem.num_gen=num_layouts # number of generations
                    results=opt_problem.optimize() # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]




                elif choice== "Weighted sum":
                    #optimization_algorithm="W_S"
                    print "Enter desired number of maximum iterations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter number of interval for weights to the objectives:"
                    num_disc=raw_input()
                    try:
                        num_disc = int(num_disc)
                    except:
                        print "Please enter an integer"

                    opt_problem = new_engine_opt(engine=New_engine, W=width, H=height, seed=seed, level=level, method="FMINCON")
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc=num_disc
                    results = opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]



                elif choice=="Simulated annealing":
                    #optimization_algorithm="SA"
                    print "Enter desired number of steps:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter initial temperature (High):"
                    temp_init = raw_input()
                    try:
                        temp_init = float(temp_init)
                    except:
                        print "Please enter a valid Temperature"
                    opt_problem = new_engine_opt(engine=New_engine, W=width, H=height, seed=seed, level=level, method="SA")
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init=temp_init # initial temperature
                    results = opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                cs_sym_info = []
                fig_data = []
                for i in range(len(results)):
                    cs_sym_info.append(results[i][1])
                    fig_data.append(results[i][0])

                Solutions = []
                for i in range(len(cs_sym_info)):
                    name = 'Layout_' + str(i)
                    solution = CornerStitchSolution(name=name)
                    solution.params = None
                    solution.layout_info = cs_sym_info[i][0]
                    solution.abstract_info = solution.form_abs_obj_rect_dict()
                    Solutions.append(solution)

                for i in range(len(fig_data)):
                    save_layouts(fig_data[i][0], count=i, db=db)
        else:
            print "Enter desired number of solutions:"
            num_layouts = raw_input()
            try:
                num_layouts = int(num_layouts)
            except:
                print "Please enter an integer"
            fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=width, H=height,
                                                                  fixed_x_location=None, fixed_y_location=None,
                                                                  seed=seed, individual=None, bar=False)


            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)

            for i in range(len(fig_data)):
                save_layouts(fig_data[i], count=i, db=db)


    elif level==3:
        print "Enter information for Fixed-sized layout generation"
        print "Floorplan Width:"
        width = raw_input()
        width = float(width) * 1000
        print "Floorplan Height:"
        height = raw_input()
        height = float(height) * 1000
        print "Enter randomization seed:"
        seed = raw_input()
        try:
            seed = int(seed)
        except:
            print "Please enter an integer"

        print "Choose Nodes to be fixed from figure"

        refresh_layout_mode3(New_engine)
        window = QMainWindow()
        window.input_node_info = {}
        window.fixed_x_locations = {}
        window.fixed_y_locations = {}
        window.engine=New_engine
        window.mode3_width=width
        window.mode3_height=height
        window.graph=New_engine.init_data[2]
        window.x_dynamic_range = {}  # To store saved information from the fixed location table
        window.y_dynamic_range = {}  # To store saved information from the fixed location table
        window.dynamic_range_x = {}  # To store saved information from the fixed location table
        window.dynamic_range_y = {}  # To store saved information from the fixed location table
        window.inserted_order = []
        assign_fixed_locations(parent=window,New_engine=New_engine)
        #print window.fixed_x_locations
        #print window.fixed_y_locations

        print "Enter desired number of solutions:"
        num_layouts = raw_input()
        try:
            num_layouts = int(num_layouts)
        except:
            print "Please enter an integer"
        fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=width, H=height,
                                                              fixed_x_location=window.fixed_x_locations, fixed_y_location=window.fixed_y_locations,
                                                              seed=seed, individual=None, bar=False)
        #print fig_data
        if optimization==True:
            opt_problem = new_engine_opt(engine=New_engine, W=width, H=height, seed=seed, level=level, method=None)
            results = []
            for i in range(len(cs_sym_info)):
                perf_values = opt_problem.eval_layout()
                results.append([fig_data[i], cs_sym_info[i]])
                for j in range(len(perf_values)):
                    results[i].append(perf_values[j])

        Solutions = []
        for i in range(len(cs_sym_info)):
            name = 'Layout_' + str(i)
            solution = CornerStitchSolution(name=name)
            solution.params = None
            solution.layout_info = cs_sym_info[i]
            solution.abstract_info = solution.form_abs_obj_rect_dict()
            Solutions.append(solution)

        for i in range(len(fig_data)):
            save_layouts(fig_data[i], count=i, db=db)


    return Solutions




def refresh_layout_mode3(New_engine):

    #self.canvas_init = FigureCanvas(fig2)
    fig2, ax2 = plt.subplots()


    init_fig = New_engine.init_data[0]
    init_graph = New_engine.init_data[2]
    Names = init_fig.keys()
    Names.sort()
    for k, p in init_fig.items():

        if k[0] == 'T':
            x = p.get_x()
            y = p.get_y()
            #ax2.text(x + 1, y + 1, k)
            ax2.add_patch(p)
    for k, p in init_fig.items():

        if k[0] != 'T':
            x = p.get_x()
            y = p.get_y()
            #ax2.text(x + 1, y + 1, k, weight='bold')
            ax2.add_patch(p)

    data = {"x": [], "y": [], "label": []}
    for label, coord in init_graph[1].items():
        data["x"].append(coord[0])
        data["y"].append(coord[1])
        data["label"].append(label)

    ax2.plot(data['x'], data['y'], 'o', picker=5)
    for k, v in init_graph[1].items():
        ax2.annotate(k, (v[0], v[1]),size=8)
    size = New_engine.init_size
    ax2.set_xlim(0, size[0])
    ax2.set_ylim(0, size[1])

    #self.canvas_init.callbacks.connect('pick_event', self.on_click)
    plt.savefig("C:\Users\ialrazi\Desktop\REU_Data_collection_input\Figs"+'/mode3.png')


def test_case(layout_script,bond_wire_script):

    New_engine,all_components,layout_info,bondwires,patches=test_file(input_script=layout_script,bond_wire_info=bond_wire_script)
    plot_solution(patches) # minimum-sized layout plot

    # you can use these info as previously
    return all_components,layout_info,bondwires,New_engine












if __name__ == '__main__':
    cmd_mode(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')
    #test_case(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')

