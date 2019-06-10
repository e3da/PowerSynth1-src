from powercad.corner_stitch.optimization_algorithm_support import new_engine_opt
import os
from powercad.cons_aware_en.database import create_connection, insert_record
from powercad.corner_stitch.cs_solution import CornerStitchSolution
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from powercad.corner_stitch.input_script import *




# --------------Plot function---------------------
def plot_layout(fig_data=None, rects=None, size=None, fig_dir=None):
    if rects != None:
        colors = ['green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']
        type = ['Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8', 'Type_9']
        # zorders = [1,2,3,4,5]
        Patches = {}

        for r in rects:
            i = type.index(r[0])
            # print i,r.name
            P = patches.Rectangle(
                (r[1], r[2]),  # (x,y)
                r[3],  # width
                r[4],  # height
                facecolor=colors[i],
                alpha=0.5,
                # zorder=zorders[i],
                edgecolor='black',
                linewidth=1,
            )
            Patches[r[5]] = P
        fig_data = Patches

    fig, ax = plt.subplots()

    Names = fig_data.keys()
    Names.sort()
    for k, p in fig_data.items():

        if k[0] == 'T':
            x = p.get_x()
            y = p.get_y()
            ax.text(x + 0.1, y + 0.1, k)
            ax.add_patch(p)
        elif k[0] != 'T':
            x = p.get_x()
            y = p.get_y()
            ax.text(x + 0.1, y + 0.1, k, weight='bold')
            ax.add_patch(p)

    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])
    ax.set_aspect('equal')

    plt.savefig(fig_dir + '/_init_layout' + '.png')


def opt_choices():
    choices = ["Non-guided randomization", "Genetic Algorithm (NSGAII)", "Weighted sum", "Simulated annealing"]
    print "Enter a mode below to choose an optimization algorithm"
    print "List of choices:"
    for mode_id in range(len(choices)):
        print "+mode id:", mode_id, "--> algorithm:", choices[mode_id]
    cont = True
    while cont:
        try:
            id = int(raw_input("Enter selected id here:"))
        except:
            cont = True
        if id in range(4):
            return choices[id]


def save_solution(rects, id, db):
    # print Layout_Rects

    data = []

    for k, v in rects.items():
        for R_in in v:
            data.append(R_in)

        data.append([k[0], k[1]])

    l_data = [id, data]
    directory = os.path.dirname(db)
    temp_file = directory + '/out.txt'

    with open(temp_file, 'wb') as f:
        f.writelines(["%s\n" % item for item in data])
        # f.write(''.join(chr(i) for i in range(data)))
    conn = create_connection(db)
    with conn:
        insert_record(conn, l_data, temp_file)
    conn.close()


def eval_single_layout(layout_engine=None,layout_data=None, apis={}, measures=[]):
    opt_problem = new_engine_opt(engine=layout_engine, W=layout_engine.init_size[0], H=layout_engine.init_size[1],
                                 seed=None, level=2, method=None,apis=apis,measures=measures)

    results = opt_problem.eval_layout(layout_data)
    print results

def update_solution_data(layout_dictionary=None, opt_problem=None, measure_names=[], fig_data=None, perf_results=[]):
    '''

    :param layout_dictionary: list of CS layout data
    :param opt_problem: optimization object for different modes
    :param measure_names: list of performance names
    :param fig_data: list of list for matplotlib rectangle patches of each layout
    :param perf_results: if in data collection mode
    :return:
    '''
    Solutions = []
    for i in range(len(layout_dictionary)):
        if opt_problem != None:  # Evaluatio mode
            results = opt_problem.eval_layout(layout_dictionary[i])
        else:
            results = perf_results[i]
        name = 'Layout_' + str(i)
        solution = CornerStitchSolution(name=name)
        solution.params = dict(zip(measure_names, results))  # A dictionary formed by result and measurement name
        solution.layout_info = layout_dictionary[i]
        solution.abstract_info = solution.form_abs_obj_rect_dict()
        solution.fig_data = fig_data[i]
        Solutions.append(solution)
    return Solutions


def generate_optimize_layout(layout_engine=None, mode=0, optimization=True, db_file=None, apis={}, measures=[]):
    '''

    :param layout_engine: Layout engine object for layout generation
    :param mode: 0->3 see in cmd.py
    :param optimization: (or evaluation for mode 0) set to be True for layout evaluation
    :param db_file: database file to store the layout info
    :param apis: {'E':e_api,'T':t_api} some apis for electrical and thermal models
    :return:
    '''

    # GET MEASUREMENT NAME:
    measure_names = []
    for m in measures:
        measure_names.append(m.name)

    if mode == 0:
        fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=1, W=None, H=None,
                                                                 fixed_x_location=None, fixed_y_location=None,
                                                                 seed=None,
                                                                 individual=None, bar=False)

        if optimization == True:
            opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=None, level=mode, method=None,
                                         apis=apis, measures=measures)
            Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                             measure_names=measure_names,fig_data=fig_data)



    elif mode == 1:
        print "Enter information for Variable-sized layout generation"
        seed = raw_input("Enter randomization seed:")
        try:
            seed = int(seed)
        except:
            print "Please enter an integer"

        if optimization == True:
            choice = opt_choices()

            if choice == "Non-guided randomization":
                optimization_algorithm = "NG_RANDOM"
                print "Enter desired number of solutions:"
                num_layouts = raw_input()
                try:
                    num_layouts = int(num_layouts)
                except:
                    print "Please enter an integer"
                fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=None, H=None,
                                                                         fixed_x_location=None, fixed_y_location=None,
                                                                         seed=seed, individual=None, bar=False)

                opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode, method=None,
                                             apis=apis, measures=measures)
                Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                                 measure_names=measure_names,fig_data=fig_data)

            else:
                if choice == "Genetic Algorithm (NSGAII)":
                    print "Enter desired number of generations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    # optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="NSGAII",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.optimize()

                elif choice == "Weighted sum":
                    # optimization_algorithm="W_S"
                    print "Enter desired number of maximum iterations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter number of interval for weights to the objectives:"
                    num_disc = raw_input()
                    try:
                        num_disc = int(num_disc)
                    except:
                        print "Please enter an integer"

                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="FMINCON",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc = num_disc
                    opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                elif choice == "Simulated annealing":
                    # optimization_algorithm="SA"
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
                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="SA",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init = temp_init  # initial temperature
                    opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                Solutions = update_solution_data(layout_dictionary=opt_problem.layout_data, measure_names=measure_names,
                                                 fig_data=opt_problem.fig_data, perf_results=opt_problem.perf_results)

        else: # Layout generation only
            print "Enter desired number of solutions:"
            num_layouts = raw_input()
            try:
                num_layouts = int(num_layouts)
            except:
                print "Please enter an integer"
            fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=None, H=None,
                                                                     fixed_x_location=None, fixed_y_location=None,
                                                                     seed=seed, individual=None, bar=False)

            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                solution.fig_data=fig_data[i]
                Solutions.append(solution)


    elif mode == 2:

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

        if optimization == True:
            choice = opt_choices()
            if choice == "Non-guided randomization":
                optimization_algorithm = "NG_RANDOM"
                print "Enter desired number of solutions:"
                num_layouts = raw_input()
                try:
                    num_layouts = int(num_layouts)
                except:
                    print "Please enter an integer"
                fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width,
                                                                         H=height,
                                                                         fixed_x_location=None, fixed_y_location=None,
                                                                         seed=seed, individual=None, bar=False)

                opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                             method=None,
                                             apis=apis, measures=measures)

                Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                                 measure_names=measure_names,fig_data=fig_data)
            else:
                if choice == "Genetic Algorithm (NSGAII)":
                    print "Enter desired number of generations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    # optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="NSGAII",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.optimize()  # perform optimization

                elif choice == "Weighted sum":
                    # optimization_algorithm="W_S"
                    print "Enter desired number of maximum iterations:"
                    num_layouts = raw_input()
                    try:
                        num_layouts = int(num_layouts)
                    except:
                        print "Please enter an integer"
                    print "Enter number of interval for weights to the objectives:"
                    num_disc = raw_input()
                    try:
                        num_disc = int(num_disc)
                    except:
                        print "Please enter an integer"

                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="FMINCON",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc = num_disc
                    opt_problem.optimize()  # perform optimization

                elif choice == "Simulated annealing":
                    # optimization_algorithm="SA"
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
                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="SA",
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init = temp_init  # initial temperature
                    opt_problem.optimize()  # perform optimization
                Solutions = update_solution_data(layout_dictionary=opt_problem.layout_data, measure_names=measure_names,
                                                 fig_data=opt_problem.fig_data, perf_results=opt_problem.perf_results)
        else:
            print "Enter desired number of solutions:"
            num_layouts = raw_input()
            try:
                num_layouts = int(num_layouts)
            except:
                print "Please enter an integer"
            fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width, H=height,
                                                                     fixed_x_location=None, fixed_y_location=None,
                                                                     seed=seed, individual=None, bar=False)

            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                solution.fig_data=fig_data[i]
                Solutions.append(solution)

    '''
    elif mode == 3:
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

        refresh_layout(layout_engine)
        window = QMainWindow()
        window.input_node_info = {}
        window.fixed_x_locations = {}
        window.fixed_y_locations = {}
        window.engine = layout_engine
        window.mode3_width = width
        window.mode3_height = height
        window.graph = layout_engine.init_data[2]
        window.x_dynamic_range = {}  # To store saved information from the fixed location table
        window.y_dynamic_range = {}  # To store saved information from the fixed location table
        window.dynamic_range_x = {}  # To store saved information from the fixed location table
        window.dynamic_range_y = {}  # To store saved information from the fixed location table
        window.inserted_order = []
        assign_fixed_locations(parent=window, layout_engine=layout_engine)
        # print window.fixed_x_locations
        # print window.fixed_y_locations

        print "Enter desired number of solutions:"
        num_layouts = raw_input()
        try:
            num_layouts = int(num_layouts)
        except:
            print "Please enter an integer"
        fig_data, cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width, H=height,
                                                              fixed_x_location=window.fixed_x_locations,
                                                              fixed_y_location=window.fixed_y_locations,
                                                              seed=seed, individual=None, bar=False)
        # print fig_data
        if optimization == True:
            opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, mode=mode, method=None)
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
            save_solution(fig_data[i], id=i, db=db_file)
    '''
    # POPULATING DATABASE
    for i in range(len(Solutions)):  # MARK FOR DELETION
        solution = Solutions[i]
        save_solution(solution.fig_data, id=i, db=db_file)
    return Solutions


def script_translator(input_script=None, bond_wire_info=None, fig_dir=None):
    ScriptMethod = ScriptInputMethod(input_script)  # initializes the class with filename
    ScriptMethod.read_input_script()  # reads input script and make two sections
    ScriptMethod.gather_part_route_info()  # gathers part and route info
    ScriptMethod.gather_layout_info()  # gathers layout info
    # print ScriptMethod.size
    # print len(ScriptMethod.cs_info), ScriptMethod.cs_info

    # print ScriptMethod.component_to_cs_type
    ScriptMethod.update_constraint_table()  # updates constraint table

    input_rects = ScriptMethod.convert_rectangle()  # converts layout info to cs rectangle info
    input_info = [input_rects, ScriptMethod.size]

    # bond wire file read in
    if bond_wire_info != None:
        bondwires = ScriptMethod.bond_wire_table(bondwire_info=bond_wire_info)
    # output format of bondwire storing
    # Bond wire table={'BW1': {'BW_object': <powercad.design.Routing_paths.BondingWires instance at 0x16F4D648>, 'Source': 'D1_Drain', 'num_wires': '4', 'Destination': 'B1', 'spacing': '0.1'}, 'BW2': {'BW....}


    try:
        app = QtGui.QApplication(sys.argv)
    except:
        pass
    window = QMainWindow()
    New_engine = New_layout_engine()
    New_engine.init_layout(input_format=input_info)
    cons_df = show_constraint_table(parent=window, cons_df=ScriptMethod.df)
    New_engine.cons_df = cons_df
    New_engine.Types = ScriptMethod.Types
    New_engine.all_components = ScriptMethod.all_components
    New_engine.init_size = ScriptMethod.size
    plot_layout(fig_data=New_engine.init_data[0], size=New_engine.init_size, fig_dir=fig_dir)

    # New_engine.open_new_layout_engine(window=window)
    Patches, cs_sym_data = New_engine.generate_solutions(level=0, num_layouts=1, W=None, H=None, fixed_x_location=None,
                                                         fixed_y_location=None, seed=None, individual=None)

    return New_engine, cs_sym_data, bondwires, Patches