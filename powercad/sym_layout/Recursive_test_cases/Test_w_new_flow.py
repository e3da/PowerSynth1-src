from powercad.corner_stitch.input_script import *
from powercad.corner_stitch.cs_solution import *
from easygui import *
from PySide.QtGui import QFileDialog,QMainWindow
import glob
from powercad.corner_stitch.optimization_algorithm_support import new_engine_opt


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
    '''
    for i in layout_info:
        for k,v in i.items():
            for id,rect in v.items():
                for j in rect:
                    print j.x/1000.0,j.y/1000.0,j.width/1000.0,j.height/1000.0
    
    '''


    #optimization_setup() # implement later

    layout_data = {}
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


    if level == 0:

        fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=1, W=None, H=None,fixed_x_location=None, fixed_y_location=None, seed=None,individual=None, bar=False)

        print fig_data
        Solutions=[]
        for i in range(len(cs_sym_info)):
            name='Layout_'+str(i)
            solution=CornerStitchSolution(name=name)
            solution.params=None
            solution.layout_info=cs_sym_info[i]
            Solutions.append(solution)
            layout_data[name] = {'Rects': cs_sym_info[i]}
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


            fig_data, cs_sym_info = New_engine.generate_solutions(level, num_layouts=num_layouts, W=None, H=None,
                                                                  fixed_x_location=None, fixed_y_location=None, seed=seed,
                                                                  individual=None, bar=False)
            
            Solutions = []
            for i in range(len(cs_sym_info)):
                name = 'Layout_' + str(i)
                solution = CornerStitchSolution(name=name)
                solution.params = None
                solution.layout_info = cs_sym_info[i]
                Solutions.append(solution)
                layout_data[name] = {'Rects': cs_sym_info[i]}
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
                solution.layout_info = cs_sym_info[i]
                Solutions.append(solution)
                layout_data[name] = {'Rects': cs_sym_info[i]}
            for i in range(len(fig_data)):
                save_layouts(fig_data[i][0], count=i, db=db)




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
                Solutions.append(solution)
                layout_data[name] = {'Rects': cs_sym_info[i]}
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
                solution.layout_info = cs_sym_info[i]
                Solutions.append(solution)
                layout_data[name] = {'Rects': cs_sym_info[i]}
            for i in range(len(fig_data)):
                save_layouts(fig_data[i][0], count=i, db=db)


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



    raw_input()






def test_case(layout_script,bond_wire_script):

    New_engine,all_components,layout_info,bondwires,patches=test_file(input_script=layout_script,bond_wire_info=bond_wire_script)
    plot_solution(patches) # minimum-sized layout plot

    # you can use these info as previously
    return all_components,layout_info,bondwires,New_engine












if __name__ == '__main__':
    cmd_mode(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')
    #test_case(layout_script="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt",bond_wire_script='C:\Users\ialrazi\Desktop\REU_Data_collection_input\\bond_wires.txt')

