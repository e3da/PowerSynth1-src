# This is the layout generation and optimization flow using command line only
from powercad.electrical_mdl.cornerstitch_API import *
from powercad.thermal.cornerstitch_API import *
from glob import glob
from powercad.cmd_run.cmd_layout_handler import generate_optimize_layout, script_translator, eval_single_layout
import objgraph
from pympler import muppy,summary
import types
class Cmd_Handler:
    def __init__(self):
        # Input files
        self.layout_script = None  # layout file dir
        self.bondwire_setup = None  # bondwire setup dir
        self.layer_stack_file = None  # layerstack file dir
        self.rs_model_file = None  # rs model file dir
        self.fig_dir = None  # Default dir to save figures
        self.db_dir = None  # Default dir to save layout db
        self.constraint_file=None # Default csv file to save constraint table
        self.new_mode=1 # 1: constraint table setup required, 0: constraint file will be reloaded
        # Data storage
        self.db_file = None  # A file to store layout database

        # CornerStitch Initial Objects
        self.engine = None
        self.comp_dict = {}
        self.wire_table = {}
        self.raw_layout_info = {}
        self.min_size_rect_patches = {}
        # APIs
        self.measures = []
        self.e_api = None
        self.t_api = None
        # Solutions
        self.soluions = None

    def load_macro_file(self, file):
        '''

        :param file:
        :return:
        '''
        run_option = None
        num_layouts = None
        floor_plan = None
        seed = None
        algorithm = None
        t_name =None
        e_name = None
        dev_conn ={}
        with open(file, 'rb') as inputfile:
            thermal_mode = False
            electrical_mode =False
            dev_conn_mode=False
            for line in inputfile.readlines():
                line = line.strip("\r\n")
                info = line.split(" ")
                if line == '':
                    continue
                if line[0] == '#':  # Comments
                    continue
                if info[0] == "Layout_script:":
                    self.layout_script = info[1]
                if info[0] == "Bondwire_setup:":
                    self.bondwire_setup = info[1]
                if info[0] == "Layer_stack:":
                    self.layer_stack_file = info[1]
                if info[0] == "Parasitic_model:":
                    self.rs_model_file = info[1]
                if info[0] == "Fig_dir:":
                    self.fig_dir = info[1]
                if info[0] == "Solution_dir:":
                    self.db_dir = info[1]
                if info[0] == "Constraint_file:":
                    self.constraint_file = info[1]
                if info[0] =="New:":
                    self.new_mode = int(info[1])
                if info[0] == "Option:":  # engine option
                    run_option = int(info[1])
                if info[0] == "Num_of_layouts:":  # engine option
                    num_layouts = int(info[1])
                if info[0] == "Seed:":  # engine option
                    seed = int(info[1])
                if info[0] == "Optimization_Algorithm:":  # engine option
                    algorithm = info[1]
                if info[0] == "Layout_Mode:":  # engine option
                    layout_mode = int(info[1])
                if info[0] == "Floor_plan:":
                    floor_plan = info[1]
                    floor_plan = floor_plan.split(",")
                    floor_plan = [int(i) for i in floor_plan]
                if info[0] == 'Num_generations:':
                    num_gen = int(info[1])
                if info[0]== 'Thermal_Setup:':
                    thermal_mode = True
                if info[0] == 'End_Thermal_Setup.':
                    thermal_mode = False
                if info[0] == 'Electrical_Setup:':
                    electrical_mode = True
                if info[0] == 'End_Electrical_Setup..':
                    electrical_mode = False
                if thermal_mode:
                    if info[0] == 'Measure_Name:' and t_name==None:
                        t_name = info[1]
                    if info[0] == 'Selected_Devices:':
                        devices = info[1].split(",")
                    if info[0] == 'Device_Power:':
                        power = info[1].split(",")
                        power = [float(i) for i in power]
                    if info[0] == 'Heat_Convection:':
                        h_conv = float(info[1])
                    if info[0] == 'Ambient_Temperature:':
                        t_amb = float(info[1])
                if electrical_mode:
                    if info[0] == 'Measure_Name:' and e_name==None:
                        e_name = info[1]
                    if info[0] == 'Measure_Type:':
                        type = int(info[1])
                    if info[0] == 'End_Device_Connection.':
                        dev_conn_mode = False
                    if dev_conn_mode:
                        dev_name = info[0]
                        conn = info[1].split(",")
                        conn = [int(i) for i in conn]
                        dev_conn[dev_name] = conn
                    if info[0] == 'Device_Connection:':
                        dev_conn_mode = True


                    if info[0] == 'Source:':
                        source = info[1]
                    if info[0] == 'Sink:':
                        sink = info[1]
                    if info[0] == 'Frequency:':
                        frequency = float(info[1])
        if self.new_mode==1:
            try:
                with open(self.constraint_file, "w") as my_empty_csv:
                    pass
            except:
                print " wrong file name for constraint file"
                return False
        check_file = os.path.isfile
        check_dir = os.path.isdir
        # Check if these files exist
        cont = check_file(self.layout_script) and check_file(self.bondwire_setup) and check_file(
            self.layer_stack_file) and check_file(self.rs_model_file) and check_dir(self.fig_dir) and check_dir(
            self.db_dir) and check_file(self.constraint_file)
        if cont:
            print "run the optimization"
            self.init_cs_objects()
            self.set_up_db()
            if run_option == 0:
                self.solutions=generate_optimize_layout(layout_engine=self.engine, mode=layout_mode,
                                         optimization=False, db_file=self.db_file,fig_dir=self.fig_dir, num_layouts=num_layouts, seed=seed,
                                         floor_plan=floor_plan)
            elif run_option == 1:
                self.measures=[]
                t_setup_data={'Power': power,'heat_conv':h_conv,'t_amb':t_amb}
                t_measure_data={'name':t_name,'devices':devices}
                e_measure_data = {'name': e_name, 'type': type, 'source': source, 'sink': sink}
                self.setup_thermal(mode='macro', setup_data=t_setup_data,meas_data=t_measure_data)
                self.setup_electrical(mode='macro', dev_conn=dev_conn, frequency=frequency, meas_data=e_measure_data)

                # Convert a list of patch to rectangles
                patch_dict = self.engine.init_data[0]
                width, height = self.engine.init_size
                fig_dict = {(width, height): []}
                for k, v in patch_dict.items():
                    fig_dict[(width, height)].append(v)
                init_rects = {}
                for k, v in self.engine.init_data[1].items():
                    rects = []
                    for i in v:
                        rect = Rectangle(x=i[0] * 1000, y=i[1] * 1000, width=i[2] * 1000, height=i[3] * 1000, type=i[4])
                        rects.append(rect)
                    init_rects[k] = rects
                cs_sym_info = {(width * 1000, height * 1000): init_rects}
                self.solutions=eval_single_layout(layout_engine=self.engine, layout_data=cs_sym_info, apis={'E': self.e_api,
                                                                                             'T': self.t_api},measures=self.measures)
            if run_option == 2:

                self.measures = []
                t_setup_data = {'Power': power, 'heat_conv': h_conv, 't_amb': t_amb}
                t_measure_data = {'name': t_name, 'devices': devices}
                e_measure_data = {'name':e_name,'type':type,'source':source,'sink':sink}
                self.setup_electrical(mode='macro', dev_conn=dev_conn, frequency=frequency, meas_data=e_measure_data)

                self.setup_thermal(mode='macro', setup_data=t_setup_data, meas_data=t_measure_data)
                self.solutions=generate_optimize_layout(layout_engine=self.engine, mode=layout_mode,
                                         optimization=True, db_file=self.db_file,fig_dir=self.fig_dir,
                                         apis={'E': self.e_api, 'T': self.t_api}, num_layouts=num_layouts, seed=seed,
                                         algorithm=algorithm, floor_plan=floor_plan,num_gen=num_gen,measures=self.measures)
        else:
            return cont

    # ------------------ File Resquest -------------------------------------------------
    def database_dir_request(self):
        print "Please enter a directory to save layout database"
        correct = True
        while (correct):
            db_dir = raw_input("Database dir:")
            if os.path.isdir(db_dir):
                self.db_dir = db_dir
                correct = False
            else:
                print "wrong input"

    def fig_dir_request(self):
        print "Please enter a directory to save figures"
        correct = True
        while (correct):
            fig_dir = raw_input("Fig dir:")
            if os.path.isdir(fig_dir):
                self.fig_dir = fig_dir
                correct = False
            else:
                print "wrong input"

    def layout_script_request(self):
        print "Please enter a layout file directory"
        correct = True
        while (correct):
            file = raw_input("Layout Script File:")
            if os.path.isfile(file):
                self.layout_script = file
                correct = False
            else:
                print "wrong input"

    def bondwire_file_request(self):
        print "Please enter a bondwire setup file directory"
        correct = True
        while (correct):
            file = raw_input("Bondwire Setup File:")
            if os.path.isfile(file):
                self.bondwire_setup = file
                correct = False
            else:
                print "wrong input"

    def layer_stack_request(self):
        print "Please enter a layer stack file directory"
        correct = True
        while (correct):
            file = raw_input("Layer Stack File:")
            if os.path.isfile(file):
                self.layer_stack_file = file
                correct = False
            else:
                print "wrong input"

    def res_model_request(self):
        print "Please enter a model file directory"
        correct = True
        while (correct):
            file = raw_input("Model File:")
            if os.path.isfile(file):
                self.rs_model_file = file
                correct = False
            else:
                print "wrong input"

    def cons_dir_request(self):
        print "Please enter a constraint file directory"
        correct = True
        while (correct):
            file = raw_input("Constraint File:")
            if os.path.isfile(file):
                self.constraint_file = file
                correct = False
            else:
                print "wrong input"

    def cons_file_edit_request(self):
        self.new_mode=int(raw_input( "If you want to edit the constraint file, enter 1. Else enter 0: "))

    def option_request(self):
        print "Please enter an option:"
        print "0: layout generation, 1:single layout evaluation, 2:layout optimization, quit:to quit,help:to get help"
        correct = True
        while (correct):
            opt = raw_input("Option:")
            if opt in ['0', '1', '2']:
                return True, int(opt)
            elif opt == 'quit':
                return False, opt
            elif opt == 'help':
                self.help()
            else:
                print "wrong input"

    def help(self):
        print "Layout Generation Mode: generate layout only without evaluation"
        print "Layout Evaluation Mode: single layout evaluation"
        print "Layout Optimization Mode: optimize layout based on initial input"

    def option_layout_gen(self):
        print "Please enter an option:"
        print "0: minimum size, 1:variable size, 2:fixed size, 3:fixed size with fixed locations, quit:to quit"
        print "back: return to the previous stage"

        correct = True
        while (correct):
            opt = raw_input("Option:")
            if opt in ['0', '1', '2', '3']:
                return True, int(opt)
            elif opt == 'quit':
                return False, opt
            elif opt == 'back':
                return True, opt
            else:
                print "wrong input"

    # -------------------INITIAL SETUP--------------------------------------
    def set_up_db(self):
        database = os.path.join(self.db_dir, 'layouts_db')
        filelist = glob(os.path.join(database + '/*'))
        # print filelist
        for f in filelist:
            try:
                os.remove(f)
            except:
                print "can't remove file"

        if not os.path.exists(database):
            os.makedirs(database)
        self.db_file = database + '/' + 'layout.db'
        conn = create_connection(self.db_file)
        with conn:
            create_table(conn)
        conn.close()

    def input_request(self):
        self.layout_script_request()
        self.bondwire_file_request()
        self.layer_stack_request()
        self.res_model_request()
        self.fig_dir_request()
        self.database_dir_request()
        self.cons_dir_request()
        self.cons_file_edit_request()

    def init_cs_objects(self):
        '''
        Initialize some CS objects
        :return:
        '''
        self.engine, self.raw_layout_info, self.wire_table = script_translator(
            input_script=self.layout_script, bond_wire_info=self.bondwire_setup, fig_dir=self.fig_dir, constraint_file=self.constraint_file,mode=self.new_mode)
        for comp in self.engine.all_components:
            self.comp_dict[comp.layout_component_id] = comp

    # --------------- API --------------------------------
    def setup_electrical(self,mode='command',dev_conn={},frequency=None,meas_data={}):

        layer_to_z = {'T': [0, 0.2], 'D': [0.2, 0], 'B': [0.2, 0],
                      'L': [0.2, 0]}
        self.e_api = CornerStitch_Emodel_API(comp_dict=self.comp_dict, layer_to_z=layer_to_z, wire_conn=self.wire_table)
        self.e_api.load_rs_model(self.rs_model_file)
        if mode == 'command':
            self.e_api.form_connection_table(mode='command')
            self.e_api.get_frequency()
            self.measures += self.e_api.measurement_setup()
        elif mode == 'macro':
            self.e_api.form_connection_table(mode='macro',dev_conn=dev_conn)
            self.e_api.get_frequency(frequency)
            self.measures += self.e_api.measurement_setup(meas_data)


    def setup_thermal(self,mode = 'command',meas_data ={},setup_data={}):

        self.t_api = CornerStitch_Tmodel_API(comp_dict=self.comp_dict)
        self.t_api.import_layer_stack(self.layer_stack_file)
        if mode == 'command':
            self.measures += self.t_api.measurement_setup()
            self.t_api.set_up_device_power()

        elif mode == 'macro':
            self.measures += self.t_api.measurement_setup(data=meas_data)
            self.t_api.set_up_device_power(data=setup_data)

    def init_apis(self):
        '''
        initialize electrical and thermal APIs
        '''
        self.measures = []
        self.setup_thermal()
        self.setup_electrical()

    def cmd_handler_flow(self):
        print "This is the command line mode for PowerSynth layout optimization"
        print "Type -m [macro file] to run a macro file"
        print "Type -f to go through a step by step setup"
        print "Type -quit to quit"

        cont = True
        while (cont):
            mode = raw_input("Enter command here")
            if mode == '-f':
                self.input_request()
                self.init_cs_objects()
                self.set_up_db()
                self.cmd_loop()
                cont = False
            elif mode == '-quit':
                cont = False
            elif mode[0:2] == '-m':
                print "Loading macro file"
                m, file = mode.split(" ")
                if os.path.isfile(file):
                    # macro file exists
                    checked = self.load_macro_file(file)
                    if not (checked):
                        continue
                else:
                    print "wrong macro file format or wrong directory, please try again !"


            else:
                print "Wrong Input, please double check and try again !"

    def cmd_loop(self):
        cont = True
        while (cont):
            cont, opt = self.option_request()
            if opt == 0:  # Perform layout generation only without evaluation
                cont, layout_mode = self.option_layout_gen()
                if layout_mode in range(3):
                    self.set_up_db()
                    self.soluions = generate_optimize_layout(layout_engine=self.engine, mode=layout_mode,
                                                             optimization=False, db_file=self.db_file,fig_dir=self.fig_dir,
                                                             apis={'E': self.e_api, 'T': self.t_api})

            if opt == 1:
                self.init_apis()  # Setup measurement
                # Convert a list of patch to rectangles
                patch_dict = self.engine.init_data[0]
                width, height = self.engine.init_size
                fig_dict = {(width, height): []}
                for k, v in patch_dict.items():
                    fig_dict[(width, height)].append(v)
                fig_data = [fig_dict]
                init_rects = {}
                for k, v in self.engine.init_data[1].items():
                    rects = []
                    for i in v:
                        rect = Rectangle(x=i[0] * 1000, y=i[1] * 1000, width=i[2] * 1000, height=i[3] * 1000, type=i[4])
                        rects.append(rect)
                    init_rects[k] = rects
                cs_sym_info = {(width * 1000, height * 1000): init_rects}
                eval_single_layout(layout_engine=self.engine, layout_data=cs_sym_info, apis={'E': self.e_api,
                                                                                             'T': self.t_api},measures=self.measures)

            elif opt == 2:  # Peform layout evaluation based on the list of measures
                self.init_apis()  # Setup measurement
                cont, layout_mode = self.option_layout_gen()
                if layout_mode in range(3):
                    self.set_up_db()
                    self.soluions = generate_optimize_layout(layout_engine=self.engine, mode=layout_mode,
                                                             optimization=True, db_file=self.db_file,fig_dir=self.fig_dir,
                                                             apis={'E': self.e_api, 'T': self.t_api},
                                                             measures=self.measures)



            elif opt == 'quit':
                cont = False


if __name__ == "__main__":
    cmd = Cmd_Handler()
    cmd.cmd_handler_flow()
    objgraph.show_most_common_types()
    all_objects = muppy.get_objects()
    my_types = muppy.filter(all_objects, Type=types.DictType)
    sum1 = summary.summarize(my_types)
    summary.print_(sum1)