from powercad.corner_stitch.optimization_algorithm_support import new_engine_opt
from powercad.corner_stitch.cs_solution import CornerStitchSolution
from powercad.corner_stitch.input_script import *
from powercad.sol_browser.cs_solution_handler import pareto_solutions,export_solutions
from powercad.electrical_mdl.e_handler import E_Rect

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


def opt_choices(algorithm=None):
    if algorithm==None:
        choices = ["NG-RANDOM", "NSGAII", "WS", "SA"]
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
    else:
        return algorithm


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


def eval_single_layout(layout_engine=None, layout_data=None, apis={}, measures=[]):
    opt_problem = new_engine_opt(engine=layout_engine, W=layout_engine.init_size[0], H=layout_engine.init_size[1],
                                 seed=None, level=2, method=None, apis=apis, measures=measures)

    results = opt_problem.eval_layout(layout_data)
    measure_names = []
    for m in measures:
        measure_names.append(m.name)
    Solutions=[]
    name='initial_input_layout'
    solution = CornerStitchSolution(name=name, index=0)
    solution.params = dict(zip(measure_names, results))  # A dictionary formed by result and measurement name
    solution.layout_info = layout_data
    solution.abstract_info = solution.form_abs_obj_rect_dict()
    Solutions.append(solution)
    print "Performance_results",results
    return Solutions


def update_solution_data(layout_dictionary=None, opt_problem=None, measure_names=[], perf_results=[]):
    '''

    :param layout_dictionary: list of CS layout data
    :param opt_problem: optimization object for different modes
    :param measure_names: list of performance names
    :param perf_results: if in data collection mode
    :return:
    '''
    Solutions = []
    print layout_dictionary
    for i in range(len(layout_dictionary)):
        if opt_problem != None:  # Evaluatio mode
            layout_data = {'H':layout_dictionary[i]['H'], 'V': layout_dictionary[i]['V']}
            results = opt_problem.eval_layout(layout_data)
        else:
            results = perf_results[i]
        name = 'Layout_' + str(i)

        solution = CornerStitchSolution(name=name,index=i)
        solution.params = dict(zip(measure_names, results))  # A dictionary formed by result and measurement name
        #print "Added", name,"Perf_values: ", solution.params.values()
        solution.layout_info = layout_dictionary[i]['H']
        solution.abstract_info = solution.form_abs_obj_rect_dict()
        Solutions.append(solution)
    return Solutions

def get_seed(seed=None):
    if seed == None:
        #print "Enter information for Variable-sized layout generation"
        seed = raw_input("Enter randomization seed:")
        try:
            seed = int(seed)
        except:
            print "Please enter an integer"
    return seed

def get_params(num_layouts=None,num_disc =None,temp_init = None, alg=None):
    params = []
    if num_layouts == None:
        if alg == 'NG-RANDOM' or alg == 'LAYOUT_GEN':
            print "Enter desired number of solutions:"
        elif alg=="WS":
            print "Enter number of maximum iterations:"
        elif alg == 'SA':
            print "Enter number of steps: "
        elif alg == 'NSGAII':
            print "Enter desired number of generations:"
        num_layouts = raw_input()
        try:
            num_layouts = int(num_layouts)
        except:
            print "Please enter an integer"
    params.append(num_layouts)

    if alg == 'WS' and num_disc == None:
        print "Enter number of interval for weights to the objectives:"
        num_disc = raw_input()
        try:
            num_disc = int(num_disc)
        except:
            print "Please enter an integer"
    params.append(num_disc)
    if alg == "SA" and temp_init==None:
        print "Enter initial temperature (High):"
        temp_init = raw_input()
        try:
            temp_init = float(temp_init)
        except:
            print "Please enter a valid Temperature"
    params.append(temp_init)
    return params
def get_dims(floor_plan = None):
    if floor_plan==None:
        print "Enter information for Fixed-sized layout generation"
        print "Floorplan Width:"
        width = raw_input()
        width = float(width) * 1000
        print "Floorplan Height:"
        height = raw_input()
        height = float(height) * 1000
        return [width,height]
    else:
        width = floor_plan[0]*1000
        height = floor_plan[1]*1000
        return [width, height]
def generate_optimize_layout(layout_engine=None, mode=0, optimization=True, db_file=None,fig_dir=None,sol_dir=None, apis={}, measures=[],seed=None,
                             num_layouts = None,num_gen= None , num_disc=None,max_temp=None,floor_plan=None,algorithm=None):
    '''

    :param layout_engine: Layout engine object for layout generation
    :param mode: 0->3 see in cmd.py
    :param optimization: (or evaluation for mode 0) set to be True for layout evaluation
    :param db_file: database file to store the layout info
    :param apis: {'E':e_api,'T':t_api} some apis for electrical and thermal models
    :param measures: list of measure objects
    # Below are some macro mode params:
    :param seed: int -- provide a seed for layout generation used in all methods(macro mode)
    :param floor_plan: [int, int] -- provide width and height values for fix floor plan layout generation mode
    # ALGORITHM PARAMS
    :param algorithm str -- type of algorithm NG-RANDOM,NSGAII,WS,SA
    :param num_layouts int -- provide a number of layouts used in NG RANDOM and WS(macro mode)
    :param num_gen int -- provide a number of generations used in NSGAII (macro mode)
    :param num_disc -- provide a number for intervals to create weights for objectives WS (macro mode)
    :param max_temp -- provide a max temp param for SA (macro mode)

    :return: list of CornerStitch Solution objects
    '''
    plot = True


    # GET MEASUREMENT NAME:
    measure_names = []
    for m in measures:
        measure_names.append(m.name)

    if mode == 0:
        cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=1, W=None, H=None,
                                                                 fixed_x_location=None, fixed_y_location=None,
                                                                 seed=None,
                                                                 individual=None,db=db_file, bar=False)

        print cs_sym_info
        if optimization == True:
            opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=None, level=mode, method=None,
                                         apis=apis, measures=measures)
            Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                             measure_names=measure_names)

        else:
            Solutions = []

            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name,index=i)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)
        if plot:
            sol_path = fig_dir + '/Mode_0'
            if not os.path.exists(sol_path):
                os.makedirs(sol_path)
            for solution in Solutions:
                size=solution.layout_info['H'].keys()[0]
                size=list(size)
                print "Min-size", size[0]/1000,size[1]/1000
                solution.layout_plot(layout_ind=solution.index, db=db_file, fig_dir=sol_path)



    elif mode == 1:
        seed = get_seed(seed)

        if optimization == True:
            choice = opt_choices(algorithm=algorithm)
            params = get_params(num_layouts=num_layouts,alg = 'NG-RANDOM')
            num_layouts = params[0]
            if choice == "NG-RANDOM":

                cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=None, H=None,
                                                                         fixed_x_location=None, fixed_y_location=None,
                                                                         seed=seed, individual=None,db=db_file,count=None, bar=False)

                opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode, method=None,
                                             apis=apis, measures=measures)
                cs_sym_info = cs_sym_info['H']  # only collect horizontal data for solution

                Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                                 measure_names=measure_names)

            else:
                if choice == "NSGAII":
                    params= get_params(num_layouts=num_gen,alg='NSGAII')
                    num_layouts = params[0]
                    # optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="NSGAII",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.optimize()

                elif choice == "WS":
                    params = get_params(num_layouts=num_layouts,num_disc=num_disc,alg='WS')
                    num_layouts=params[0]
                    num_disc = params[1]

                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="FMINCON",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc = num_disc
                    opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                elif choice == "SA":
                    # optimization_algorithm="SA"
                    params = get_params(num_layouts=num_layouts,temp_init=max_temp, alg='SA')
                    num_layouts = params[0]
                    temp_init = params[1]


                    opt_problem = new_engine_opt(engine=layout_engine, W=None, H=None, seed=seed, level=mode,
                                                 method="SA",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init = temp_init  # initial temperature
                    opt_problem.optimize()  # results=list of list, where each element=[fig,cs_sym_info,perf1_value,perf2_value,...]

                Solutions = update_solution_data(layout_dictionary=opt_problem.layout_data, measure_names=measure_names,
                                                 perf_results=opt_problem.perf_results)


            # ---------------------------------------------- save pareto data and plot figures ------------------------------------
            # checking pareto_plot and saving csv file
            pareto_data = pareto_solutions(Solutions)  # a dictionary with index as key and list of performance value as value {0:[p1,p2],1:[...],...}
            export_solutions(solutions=Solutions, directory=sol_dir,pareto_data=pareto_data)  # exporting solution info to csv file
            if plot:
                sol_path = fig_dir + '/Mode_1_pareto'
                if not os.path.exists(sol_path):
                    os.makedirs(sol_path)
                pareto_data = pareto_solutions(Solutions)
                for solution in Solutions:
                    if solution.index in pareto_data.keys():
                        solution.layout_plot(layout_ind=solution.index, db=db_file, fig_dir=sol_path)




        else:  # Layout generation only
            params = get_params(num_layouts=num_layouts,alg='LAYOUT_GEN')
            num_layouts = params[0]

            cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=None, H=None,
                                                                     fixed_x_location=None, fixed_y_location=None,
                                                                     seed=seed, individual=None,db=db_file, bar=False)


            Solutions = []
            cs_sym_info = cs_sym_info['H']  # only collect horizontal data for solution

            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)

                if plot:
                    sol_path = fig_dir + '/Mode_1_gen_only'
                    if not os.path.exists(sol_path):
                        os.makedirs(sol_path)
                    solution.layout_plot(layout_ind=i, db=db_file, fig_dir=sol_path)



    elif mode == 2:

        width,height =get_dims(floor_plan=floor_plan)
        seed = get_seed(seed)

        if optimization == True:
            choice = opt_choices(algorithm=algorithm)
            if choice == "NG-RANDOM":
                params = get_params(num_layouts=num_layouts,alg='NG-RANDOM')
                num_layouts = params[0]
                cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width,
                                                                         H=height,
                                                                         fixed_x_location=None, fixed_y_location=None,
                                                                         seed=seed, individual=None,db=db_file, bar=False)

                opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                             method=None,
                                             apis=apis, measures=measures)

                #cs_sym_info = cs_sym_info['H']  # only collect horizontal data for solution

                Solutions = update_solution_data(layout_dictionary=cs_sym_info, opt_problem=opt_problem,
                                                 measure_names=measure_names)
            else:
                if choice == "NSGAII":
                    params = get_params(num_layouts=num_gen, alg='NSGAII')
                    num_layouts = params[0]
                    # optimization_algorithm="NSGAII"
                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="NSGAII",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.optimize()  # perform optimization

                elif choice == "WS":
                    # optimization_algorithm="W_S"
                    params = get_params(num_layouts=num_layouts, num_disc=num_disc, alg='WS')
                    num_layouts = params[0]
                    num_disc = params[1]

                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="FMINCON",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.num_disc = num_disc
                    opt_problem.optimize()  # perform optimization

                elif choice == "SA":
                    # optimization_algorithm="SA"
                    params = get_params(num_layouts=num_layouts, temp_init=max_temp, alg='SA')
                    num_layouts = params[0]
                    temp_init = params[1]
                    opt_problem = new_engine_opt(engine=layout_engine, W=width, H=height, seed=seed, level=mode,
                                                 method="SA",db=db_file,
                                                 apis=apis, measures=measures)
                    opt_problem.num_measure = 2  # number of performance metrics
                    opt_problem.num_gen = num_layouts  # number of generations
                    opt_problem.T_init = temp_init  # initial temperature
                    opt_problem.optimize()  # perform optimization
                Solutions = update_solution_data(layout_dictionary=opt_problem.layout_data, measure_names=measure_names, perf_results=opt_problem.perf_results)

            #---------------------------------------------- save pareto data and plot figures ------------------------------------
            # checking pareto_plot and saving csv file
            pareto_data = pareto_solutions(Solutions) # a dictionary with index as key and list of performance value as value {0:[p1,p2],1:[...],...}
            export_solutions(solutions=Solutions, directory=sol_dir, pareto_data=pareto_data) # exporting solution info to csv file
            if plot:
                sol_path = fig_dir + '/Mode_2_pareto'
                if not os.path.exists(sol_path):
                    os.makedirs(sol_path)
                pareto_data = pareto_solutions(Solutions)
                for solution in Solutions:
                    if solution.index in pareto_data.keys():
                        solution.layout_plot(layout_ind=solution.index, db=db_file, fig_dir=sol_path)



        else: #layout generation only
            params = get_params(num_layouts=num_layouts, alg='LAYOUT_GEN')
            num_layouts=params[0]


            cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width, H=height,
                                                                     fixed_x_location=None, fixed_y_location=None,
                                                                     seed=seed, individual=None,db=db_file, bar=False)
            #cs_sym_info = cs_sym_info['H'] # only collect horizontal data for solution
            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                solution.abstract_info = solution.form_abs_obj_rect_dict()
                Solutions.append(solution)
                if plot:
                    sol_path = fig_dir + '/Mode_2_gen_only'
                    if not os.path.exists(sol_path):
                        os.makedirs(sol_path)
                    solution.layout_plot(layout_ind=i, db=db_file, fig_dir=sol_path)

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
        cs_sym_info = layout_engine.generate_solutions(mode, num_layouts=num_layouts, W=width, H=height,
                                                              fixed_x_location=window.fixed_x_locations,
                                                              fixed_y_location=window.fixed_y_locations,
                                                              seed=seed, individual=None,db=db_file, bar=False)
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

    '''
    # POPULATING DATABASE
    for i in range(len(Solutions)):  # MARK FOR DELETION
        solution = Solutions[i]
        save_solution(solution.fig_data, id=i, db=db_file)
    
    '''

    return Solutions

def form_direct_mutual_pairs(cs_info):
    trace_raw_data = []  # for trace type (power and signal)
    for data in cs_info:  # define groups for traces and devices
        left = data[1]
        bot = data[2]
        right = data[1] + data[3]
        top = data[2] + data[4]
        name = data[5]
        type = data[0]
        if type == 'Type_1' or type == 'Type_2':
            trace_raw_data.append([name, E_Rect(top=top, bottom=bot, left=left, right=right)])




def get_hierachy_info(cs_info):
    #Use raw data from CS info to form a hierarchy which can be used later for meshing. This is less computationally expensive

    group_check =[] # list of names of object, pop this everytime a new intersection is found
    trace_raw_data= [] # for trace type (power and signal)
    conn_raw_data=[] # for other types
    name_to_group=OrderedDict()

    g_id =0
    for data in cs_info: # define groups for traces and devices
        left = data[1]
        bot = data[2]
        right = data[1]+data[3]
        top = data[2] + data[4]
        name = data[5]
        group_check.append(name)
        type = data[0]
        if type == 'Type_1' or type == 'Type_2':
            trace_raw_data.append([name,Rect(top=top,bottom=bot,left=left,right=right)])
            name_to_group[name]=g_id
            g_id +=1 # a unique group id for each rect
        else:
            conn_raw_data.append([name, Rect(top=top, bottom=bot, left=left, right=right)])
    print name_to_group
    # This has to be O(N^2) if they are all in different groups
    for d1 in trace_raw_data:
        name1 = d1[0]
        rect1 = d1[1]
        for d2 in trace_raw_data:
            name2 = d2[0]
            rect2 = d2[1]
            if name_to_group[name1] != name_to_group[name2]: # If they are not in same group
                if rect1.intersects(rect2): # if they intersect to each other
                    name_to_group[name2]= name_to_group[name1] # update the group id of this trace
    init_name = list(set(name_to_group.values()))
    isl_name = ['isl_'+str(i) for i in range(len(init_name))]
    new_isl_name_map = OrderedDict((k,i) for i,k in zip(init_name,isl_name))
    trace_isl = OrderedDict((n,[]) for n in isl_name)
    # Form trace isl
    for k in trace_isl:
        isl = trace_isl[k]
        init_name = new_isl_name_map[k]
        for t in trace_raw_data:
            if init_name == name_to_group[t[0]]:
                isl.append(t)
    # Append conn data to isl:

    for k in trace_isl:
        dev =[]
        for t in trace_isl[k]:
            for c in conn_raw_data:
                if t[1].encloses(c[1].left,c[1].bottom):
                    dev.append(c)
        trace_isl[k]+=dev
    print  trace_isl

    return trace_isl

def script_translator(input_script=None, bond_wire_info=None, fig_dir=None, constraint_file=None,mode=None):
    ScriptMethod = ScriptInputMethod(input_script)  # initializes the class with filename
    ScriptMethod.read_input_script()  # reads input script and make two sections
    ScriptMethod.gather_part_route_info()  # gathers part and route info
    ScriptMethod.gather_layout_info()  # gathers layout info

    island_info=get_hierachy_info(ScriptMethod.cs_info)
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
    #cons_df = show_constraint_table(parent=window, cons_df=ScriptMethod.df)
    if mode==0:
        cons_df = pd.read_csv(constraint_file)

    else:
        save_constraint_table(cons_df=ScriptMethod.df,file=constraint_file)
        flag=raw_input("Please edit the constraint table from constraint directory: Enter 1 on completion: ")
        if flag=='1':
            cons_df = pd.read_csv(constraint_file)

    New_engine.cons_df = cons_df
    New_engine.Types = ScriptMethod.Types
    New_engine.all_components = ScriptMethod.all_components
    New_engine.init_size = ScriptMethod.size
    plot_layout(fig_data=New_engine.init_data[0], size=New_engine.init_size, fig_dir=fig_dir)

    # New_engine.open_new_layout_engine(window=window)
    cs_sym_data = New_engine.generate_solutions(level=0, num_layouts=1, W=None, H=None, fixed_x_location=None,
                                                         fixed_y_location=None, seed=None, individual=None)
    # cs_sym_data contains both horizontal and vertical CS data

    return New_engine, cs_sym_data, bondwires, island_info