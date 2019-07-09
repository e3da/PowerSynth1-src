from powercad.project_builder.proj_dialogs import New_layout_engine_dialog
import pandas as pd
from powercad.corner_stitch.API_PS import *
from powercad.corner_stitch.CornerStitch import *
from powercad.design.library_structures import *
from powercad.cons_aware_en.database import *
from tqdm import tqdm
from powercad.design import parts
from powercad.design.group import Island, MeshNode
import matplotlib.pyplot as plt
from powercad.corner_stitch.constraintGraph_Dev import constraintGraph
import itertools




class New_layout_engine():
    def __init__(self):
        self.W = None
        self.H = None
        self.window = None
        self.Htree = None
        self.Vtree = None
        self.cons_df = None
        self.Min_X = None
        self.Min_Y = None
        self.cons_info = None
        self.ledge_width=1000.0
        self.ledge_height=1000.0


        self.Types=None  # added for new flow (list of all cs_type)
        self.all_components=None #added for new flow (holds all layout component objects)
        self.init_size=[]

        # for initialize only
        self.init_data = []
        self.cornerstitch = CornerStitch()
        self.min_dimensions = {}
        # current solutions
        self.cur_fig_data = None

        # only activate when the sym_layout API is used
        self.sym_layout = None
        self.layout_sols = {}
    def open_new_layout_engine(self, window):
        self.window = window
        patches = self.init_data[0]
        graph = self.init_data[2]
        num_cols=self.init_data[-1]
        self.new_layout_engine = New_layout_engine_dialog(self.window, patches, W=self.W, H=self , engine=self,graph=graph)
        self.new_layout_engine.show()
        self.new_layout_engine.exec_()

    def cons_from_ps(self):
        '''
        finding constraint values from technology library of PowerSynth
        :return: constraint dataframe according to new layout engine
        '''
        minWidth = self.cons_info[0]
        minHeight = self.cons_info[1]
        minExtension = self.cons_info[2]
        SP = self.cons_info[3]
        En = self.cons_info[4]
        r1 = ['Min Dimensions', 'EMPTY', 'Trace', 'MOS', 'Lead', 'Diode']
        r2 = ['Min Width', str(minWidth[0]), str(minWidth[1]), str(minWidth[2]), str(minWidth[3]), str(minWidth[4])]
        r3 = ['Min Height', str(minHeight[0]), str(minHeight[1]), str(minHeight[2]), str(minHeight[3]),
              str(minHeight[4])]
        r4 = ['Min Extension', str(minExtension[0]), str(minExtension[1]), str(minExtension[2]), str(minExtension[3]),
              str(minExtension[4])]
        r5 = ['Min Spacing', 'EMPTY', 'Trace', 'MOS', 'Lead', 'Diode']
        r6 = ['EMPTY', str(SP[0]), 0, 0, 0, 0]
        r7 = ['Trace', 0, str(SP[1]), 0, 0, 0]
        r8 = ['MOS', 0, 0, str(SP[2]), 0, 0]
        r9 = ['Lead', 0, 0, str(SP[5]), str(SP[3]), 0]
        r10 = ['Diode', 0, 0, 0, str(SP[6]), str(SP[4])]
        r11 = ['Min Enclosure', 'EMPTY', 'Trace', 'MOS', 'Lead', 'Diode']
        r12 = ['EMPTY', 0, str(En[0]), 0, 0, 0]
        r13 = ['Trace', 0, 0, str(En[1]), str(En[2]), str(En[3])]
        r14 = ['MOS', 0, 0, 0, 0, 0]
        r15 = ['Lead', 0, 0, 0, 0, 0]
        r16 = ['Diode', 0, 0, 0, 0, 0]
        my_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16]
        #print "MY",my_list
        df = pd.DataFrame(my_list)

        df.to_csv('out.csv', sep=',', header=None, index=None) # writing to a file out.csv for further reading

        return

    def init_layout(self, sym_layout=None,input_format=None,islands=None):
        
        #initialize new layout engine with old symlayout data structure
        #Returns:
        
        print "initializing ....."
        self.sym_layout = sym_layout


        if sym_layout != None:
            self.cons_info = self.collect_sym_cons_info(sym_layout)
            self.cons_df = self.cons_from_ps()
            input_rects, self.W, self.H = input_conversion(
                sym_layout)  # converts symbolic layout lines and points into rectangles
            input = self.cornerstitch.read_input('list',
                                                 Rect_list=input_rects)  # Makes the rectangles compaitble to new layout engine input format

            self.Htree, self.Vtree = self.cornerstitch.input_processing(input, self.W + 20,
                                                                        self.H + 20)  # creates horizontal and vertical corner stitch layouts
            num_columns = len(self.Htree.hNodeList[0].stitchList)

            patches, combined_graph = self.cornerstitch.draw_layout(rects=input_rects, Htree=self.Htree,
                                                                    Vtree=self.Vtree)  # collects initial layout patches and combined HCS,VCS points as a graph for mode-3 representation
            sym_to_cs = Sym_to_CS(input_rects, self.Htree,
                                  self.Vtree)  # maps corner stitch tiles to symbolic layout objects

            self.init_data = [patches, sym_to_cs, combined_graph, num_columns]
        else:
            input_rects=input_format[0]
            size=input_format[1]
            self.W=size[0]
            self.H=size[1]
            self.create_cornerstitch(input_rects,size,islands)



        # ------------------------------------------


    



    def create_cornerstitch(self,input_rects=None, size=None,islands=None):
        #cornerstitch = CornerStitch()
        #print input_rects

        input = self.cornerstitch.read_input('list',Rect_list=input_rects)  # Makes the rectangles compaitble to new layout engine input format
        self.Htree, self.Vtree = self.cornerstitch.input_processing(input, size[0],size[1])  # creates horizontal and vertical corner stitch layouts
        patches, combined_graph = self.cornerstitch.draw_layout(rects=input_rects, Htree=self.Htree,Vtree=self.Vtree)  # collects initial layout patches and combined HCS,VCS points as a graph for mode-3 representation

        plot = False
        if plot:
            fig2, ax2 = plt.subplots()
            Names = patches.keys()
            Names.sort()
            for k, p in patches.items():

                if k[0] == 'T':
                    x = p.get_x()
                    y = p.get_y()
                    ax2.text(x + 0.1, y + 0.1, k)
                    ax2.add_patch(p)

            for k, p in patches.items():

                if k[0] != 'T':
                    x = p.get_x()
                    y = p.get_y()
                    ax2.text(x + 0.1, y + 0.1, k, weight='bold')
                    ax2.add_patch(p)
            ax2.set_xlim(0, size[0])
            ax2.set_ylim(0, size[1])
            ax2.set_aspect('equal')
            plt.savefig('D:\Demo\New_Flow_w_Hierarchy\Figs'+'/_initial_layout.png')


        cs_islands,sym_to_cs= self.form_cs_island(islands, self.Htree, self.Vtree)
        cs_islands=self.populate_mesh_nodes(cs_islands,self.Htree,self.Vtree) # adding mesh nodes to the islands

        #for island in cs_islands:
            #print island.print_island()

        #sym_to_cs=self.cs_mapped_input(cs_islands) # maps cs tiles to input
        #sym_to_cs = Sym_to_CS(input_rects, self.Htree, self.Vtree)  # maps corner stitch tiles to symbolic layout objects
        print sym_to_cs
        self.init_data = [patches, sym_to_cs,cs_islands, combined_graph]
        #return init_data, Htree, Vtree

    def collect_sym_cons_info(self, sym_layout):
        '''
        Go through sym objs and search for dimensions, sym DRC
        :return:
        '''
        # NOTE: There can be multiple types of mosfets and diodes themselves for now assume all mosfet are the same
        # Take the maximum width and height of the mosfet group, Init with all 0s for cases they are not used
        diode_widths = [0]
        diode_heights = [0]
        mosfet_widths = [0]
        mosfet_heights = [0]
        lead_widths = [0]
        lead_heights = [0]
        # Go through all devices and find max dimensions

        for dev in sym_layout.devices:
            width, height, thickness = dev.tech.device_tech.dimensions
            if dev.is_diode():
                diode_widths.append(width)
                diode_heights.append(height)
            if dev.is_transistor():
                mosfet_widths.append(width)
                mosfet_heights.append(height)

        for lead in sym_layout.leads:
            if lead.tech.shape == Lead.BUSBAR:
                width = lead.tech.dimensions[0]
                height = lead.tech.dimensions[1]
            elif lead.tech.shape == Lead.ROUND:
                width = lead.tech.dimensions[0]  # Radius
                height = lead.tech.dimensions[0]
            lead_widths.append(width)
            lead_heights.append(height)

        # Info is here
        Type2_W = max(mosfet_widths + mosfet_heights)
        Type2_H = Type2_W  # Because a device can rotate
        Type3_W = max(lead_widths + lead_heights)
        Type3_H = Type3_W  # Because a lead can rotate
        Type4_W = max(diode_widths + diode_heights)
        Type4_H = Type4_W  # Because a diode can rotate
        # Design_rule
        design_rule = sym_layout.module.design_rules
        # SEE powercad/design/project_structures.py
        Type1_W = design_rule.min_trace_width
        Gap_1_1 = design_rule.min_trace_trace_width
        Gap_1_2 = design_rule.min_die_trace_dist
        Gap_1_3 = Gap_1_2
        Gap_1_4 = Gap_1_2
        Gap_2_2 = design_rule.min_die_die_dist
        Gap_2_3 = Gap_2_2
        Gap_3_3 = Gap_2_2
        Gap_3_4 = Gap_2_2
        Gap_4_4 = Gap_2_2
        Gap_0_0 = 2  # [EMPTY type]
        # Ledge Width (Type EMPTY to 1 ?)
        ledge_width = sym_layout.module.substrate.ledge_width
        minWidth = [ledge_width, Type1_W, Type2_W, Type3_W, Type4_W]  # Trace,MOS,Lead,Diode
        minHeight = [ledge_width, Type1_W, Type2_H, Type3_H, Type4_H]
        minExtension = [ledge_width, Type1_W, Type2_W, Type3_W, Type4_W]
        Gaps = [Gap_0_0, Gap_1_1, Gap_2_2, Gap_3_3, Gap_4_4, Gap_2_3, Gap_3_4]
        Enclosures = [ledge_width, Gap_1_2, Gap_1_3, Gap_1_4]
        #print Type1_W, Type2_W, Type3_W, Type4_W, Gap_1_2, Gap_2_2, ledge_width
        #print"W", minWidth
        #print"H", minHeight
        #print"E", minExtension
        #print"G", Gaps
        #print"Enc",Enclosures

        return minWidth, minHeight, minExtension, Gaps, Enclosures

    def mode_zero(self): # evaluates mode 0(minimum sized layouts)

        CG1 = CS_to_CG(0)
        CG1.getConstraints(self.cons_df)
        count = 0
        for row in self.cons_df.itertuples(index=False, name='Pandas'):

            count += 1
            if row[0] == 'Min Enclosure':
                found = count
        count = 0
        for row in self.cons_df.itertuples(index=False, name='Pandas'):
            count += 1
            if count == found + 1:
                self.ledge_width = float(row[2])
                self.ledge_height = float(row[2])


        #self.cons_df.to_csv('out_2.csv', sep=',', header=None, index=None)
        Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None,XLoc=None, YLoc=None, seed=None, individual=None,Types=self.Types)  #


        return Evaluated_X, Evaluated_Y


    def get_min_dimensions(self):
        for comp in self.all_components:
            if isinstance(comp, parts.Part):

                name=comp.name
                type=comp.cs_type
                footprint=comp.footprint
                self.min_dimensions[type]=footprint



    # generate layout solutions using constraint graph edge weights randomization for different modes(level)
    def generate_solutions(self, level, num_layouts=1, W=None, H=None, fixed_x_location=None, fixed_y_location=None,seed=None,individual=None,db=None,count=None,bar=False):
        """

        :param level: mode of operation: mode-0(minimum sized layout), mode-1(variable sized layouts), mode-2(fixed sized layouts), mode-3(fixed sized with fixed component locations)
        :param num_layouts: Number of solutions user want to generate (applicable for mode 1-3)
        :param W: floorplan width (for mode 2-3)
        :param H: floorplan height (for mode 2-3)
        :param fixed_x_location: user defined fixed x locations (for mode 3)
        :param fixed_y_location: user given fixed y locations (for mode 3)
        :param bar: show progress bar if True
        :return: Layout solutions and mapped  new layout engine solutions back to symbolic layout (old engine) objects
        """
        #global min_dimensions
        if bar:
            p_bar = tqdm(total=num_layouts,ncols=50)
        else:
            p_bar=None
        CG1 = CS_to_CG(level)
        self.constraint_info=CG1.getConstraints(self.cons_df)
        self.get_min_dimensions()
        '''
        self.min_dimensions['Type_2'] = [float(self.cons_df.iat[1, 3]), float(self.cons_df.iat[2, 3])]
        self.min_dimensions['Type_3'] = [float(self.cons_df.iat[1, 4]), float(self.cons_df.iat[2, 4])]
        self.min_dimensions['Type_4'] = [float(self.cons_df.iat[1, 5]), float(self.cons_df.iat[2, 5])]
        self.new_layout_engine.min_dimensions=self.min_dimensions
        '''

        '''
        if self.new_layout_engine.opt_algo!="NSGAII":
            cwd = os.getcwd()
            self.new_layout_engine.directory = cwd + "/Mode_" + str(level)
            if not os.path.exists(self.new_layout_engine.directory):
                os.makedirs(self.new_layout_engine.directory)  # creating directory
                #shutil.rmtree(self.directory)
            filelist = glob.glob(os.path.join(self.new_layout_engine.directory, "*.csv"))
            for f in filelist:
                os.remove(f)
        #print"Dir", self.directory
        '''
        #self.cons_df.to_csv('out_2.csv', sep=',', header=None, index=None)
        sym_to_cs = self.init_data[1]
        print "sym",sym_to_cs
        cs_islands=self.init_data[2]
        scaler = 1000  # to get back original dimensions all coordinated will be scaled down by 1000
        #mode-0
        if level == 0:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None, XLoc=None, YLoc=None,seed=None,individual=None,Types=self.Types) # for minimum sized layout only one solution is generated

            CS_SYM_information, Layout_Rects = CG1.update_min(Evaluated_X, Evaluated_Y , sym_to_cs, scaler)
            #raw_input()

            print CS_SYM_information


            '''
            #print "Before update"
            #for island in cs_islands:
                #island.print_island(plot=False)
            '''



            #cs_islands_up=self.update_points(cs_islands)


            #CS_SYM_information, Layout_Rects = CG1.UPDATE_min(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree ,sym_to_cs,scaler)  # CS_SYM_information is a dictionary where key=path_id(component name) and value=list of updated rectangles, Layout Rects is a dictionary for minimum HCS and VCS evaluated rectangles (used for plotting only)
            self.cur_fig_data = plot_layout(Layout_Rects, level)
            CS_SYM_Updated = {}
            for i in self.cur_fig_data:
                for k, v in i.items():
                    k=(k[0]*scaler,k[1]*scaler)
                    CS_SYM_Updated[k] = CS_SYM_information
            CS_SYM_Updated = [CS_SYM_Updated] # mapped solution layout information to symbolic layout objects
            cs_islands_up = self.update_islands(CS_SYM_information, Evaluated_X, Evaluated_Y, cs_islands)
            updated_cs_islands = [cs_islands_up]

            #print "After update"
            #for island in cs_islands_up:
                #island.print_island(plot=True,size=k)
                #island.plot_mesh_nodes(size=k)



            if db!=None:
                if count==None:
                    self.save_layouts(Layout_Rects,count=None, db=db)


        #mode-1
        elif level == 1:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=None, H=None,XLoc=None, YLoc=None, seed=seed, individual=individual,Types=self.Types)
            #CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)
            CS_SYM_Updated=[]
            Layout_Rects=[]
            updated_cs_islands=[]
            for i in range(len(Evaluated_X)):
                CS_SYM_Updated1, Layout_Rects1 = CG1.update_min(Evaluated_X[i], Evaluated_Y[i],sym_to_cs,scaler)
                self.cur_fig_data = plot_layout(Layout_Rects1, level=0)
                CS_SYM_info= {}
                for item in self.cur_fig_data:
                    for k, v in item.items():
                        k = (k[0] * scaler, k[1] * scaler)
                        CS_SYM_info[k] = CS_SYM_Updated1
                CS_SYM_Updated.append(CS_SYM_info)
                cs_islands_up = self.update_islands(CS_SYM_Updated1, Evaluated_X[i], Evaluated_Y[i], cs_islands)
                updated_cs_islands.append(cs_islands_up)
                Layout_Rects.append(Layout_Rects1)
                #for island in cs_islands_up:
                    #island.print_island(plot=True,size=k)


            #print "1",CS_SYM_Updated
            #print Layout_Rects
            #CS_SYM_Updated = CS_SYM_Updated['H']
            #self.cur_fig_data = plot_layout(Layout_Rects, level,self.min_dimensions)
            if count==None:
                #for i in range(len(Layout_Rects)):
                for i in range(len(Layout_Rects)):
                    self.save_layouts(Layout_Rects[i],count=i, db=db)
            else:
                #for i in range(len(Layout_Rects)):
                self.save_layouts(Layout_Rects,count=count, db=db)

        #mode-2
        elif level == 2:
            Evaluated_X0, Evaluated_Y0 = self.mode_zero() # mode-0 evaluation is required to check the validity of given floorplan size
            print Evaluated_X0, Evaluated_Y0

            ZDL_H={}
            ZDL_V={}
            for k,v in Evaluated_X0[1].items():

                ZDL_H[k]=v
            for k,v in Evaluated_Y0[1].items():
                ZDL_V[k]=v
            MIN_X={}
            MIN_Y={}
            for k,v in ZDL_H.items():
                MIN_X[ZDL_H.keys().index(k)]=v
            for k,v in ZDL_V.items():
                MIN_Y[ZDL_V.keys().index(k)]=v



            max_x=max(MIN_X.values()) #finding minimum width of the floorplan
            max_y = max(MIN_Y.values()) # finding minimum height of the floorplan
            XLoc=MIN_X.keys()
            YLoc=MIN_Y.keys()

            Min_X_Loc = {}
            Min_Y_Loc = {}

            XLoc.sort()
            YLoc.sort()
            Min_X_Loc[len(XLoc) - 1] = max_x
            Min_Y_Loc[len(YLoc) - 1] = max_y

            for k, v in Min_X_Loc.items(): # checking if the given width is greater or equal minimum width

                if W >= v:
                    #Min_X_Loc[0] = 0
                    #Min_X_Loc[k] = W
                    Min_X_Loc[0] = 0
                    Min_X_Loc[1] = self.ledge_width*scaler
                    Min_X_Loc[k - 1] = W-self.ledge_width*scaler
                    Min_X_Loc[k] = W
                else:
                    print"Enter Width greater than or equal Minimum Width"
                    return
            for k, v in Min_Y_Loc.items():# checking if the given height is greater or equal minimum width
                if H >= v:
                    #Min_Y_Loc[0] = 0
                    #Min_Y_Loc[k] = H

                    Min_Y_Loc[0] = 0
                    Min_Y_Loc[1] = self.ledge_height*scaler
                    Min_Y_Loc[k - 1] = H-self.ledge_height*scaler
                    Min_Y_Loc[k] = H
                else:
                    print"Enter Height greater than or equal Minimum Height"
                    return
            # sorting the given locations based on the graph vertices in ascending order
            Min_X_Loc = collections.OrderedDict(sorted(Min_X_Loc.items()))
            Min_Y_Loc = collections.OrderedDict(sorted(Min_Y_Loc.items()))
            print Min_X_Loc,Min_Y_Loc

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=W, H=H,
                                                      XLoc=Min_X_Loc, YLoc=Min_Y_Loc, seed=seed, individual=individual,Types=self.Types) # evaluates and finds updated locations for each coordinate
            '''
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)
            CS_SYM_Updated = CS_SYM_Updated['H'] # takes only horizontal corner stitch data
            #self.cur_fig_data = plot_layout(Layout_Rects, level,self.min_dimensions) #collects the layout patches
            if count==None:
                #for i in range(len(Layout_Rects)):
                self.save_layouts(Layout_Rects, db=db)
            else:
                #for i in range(len(Layout_Rects)):
                self.save_layouts(Layout_Rects,count=count, db=db)
            '''
            CS_SYM_Updated = []
            Layout_Rects = []
            updated_cs_islands = []
            for i in range(len(Evaluated_X)):
                CS_SYM_Updated1, Layout_Rects1 = CG1.update_min(Evaluated_X[i], Evaluated_Y[i], sym_to_cs,scaler)
                self.cur_fig_data = plot_layout(Layout_Rects1, level=0)
                CS_SYM_info = {}
                for item in self.cur_fig_data:
                    for k, v in item.items():
                        k = (k[0] * scaler, k[1] * scaler)
                        CS_SYM_info[k] = CS_SYM_Updated1
                CS_SYM_Updated.append(CS_SYM_info)
                cs_islands_up = self.update_islands(CS_SYM_Updated1, Evaluated_X[i], Evaluated_Y[i], cs_islands)
                updated_cs_islands.append(cs_islands_up)

                '''
                print "After update"
                for island in cs_islands_up:
                    island.PrintIsland(plot=True,size=k)                
                
                '''
                Layout_Rects.append(Layout_Rects1)
            # print "1",CS_SYM_Updated
            # print Layout_Rects
            # CS_SYM_Updated = CS_SYM_Updated['H']
            # self.cur_fig_data = plot_layout(Layout_Rects, level,self.min_dimensions)
            if count == None:
                # for i in range(len(Layout_Rects)):
                for i in range(len(Layout_Rects)):
                    self.save_layouts(Layout_Rects[i], count=i, db=db)
                    # self.save_layouts(Layout_Rects[i], db=db)
            else:
                # for i in range(len(Layout_Rects)):
                self.save_layouts(Layout_Rects, count=count, db=db)




            #mode-3
        elif level == 3:
            Evaluated_X0, Evaluated_Y0=self.mode_zero()
            ZDL_H = {}
            ZDL_V = {}
            for k, v in Evaluated_X0.items():
                ZDL_H = v
            for k, v in Evaluated_Y0.items():
                ZDL_V = v
            MIN_X = {}
            MIN_Y = {}
            for k, v in ZDL_H.items():
                MIN_X[ZDL_H.keys().index(k)] = v
            for k, v in ZDL_V.items():
                MIN_Y[ZDL_V.keys().index(k)] = v


            self.Min_X = Evaluated_X0
            self.Min_Y = Evaluated_Y0

            Min_X_Loc = {}
            Min_Y_Loc = {}
            for k, v in Evaluated_X0.items():
                XLoc = v.keys()
                max_x = v[max(XLoc)]
            for k, v in Evaluated_Y0.items():
                YLoc = v.keys()
                max_y = v[max(YLoc)]
            XLoc.sort()
            YLoc.sort()
            Min_X_Loc[len(XLoc) - 1] = max_x
            Min_Y_Loc[len(YLoc) - 1] = max_y

            for k, v in Min_X_Loc.items():
                if W >= v:
                    Min_X_Loc[0] = 0
                    Min_X_Loc[k] = W
                    fixed_x_location[k] = W
                    '''
                    Min_X_Loc[0] = -2000
                    Min_X_Loc[1] = 0
                    Min_X_Loc[k - 1] = W
                    Min_X_Loc[k] = W + 2000
                    fixed_x_location[k]=W + 2000
                    '''

                else:
                    print"Enter Width greater than or equal Minimum Width"
                    return None,None
            for k, v in Min_Y_Loc.items():
                if H >= v:
                    Min_Y_Loc[0] = 0
                    Min_Y_Loc[k] = H
                    fixed_y_location[k]=H
                    '''
                    Min_Y_Loc[0] = -2000
                    Min_Y_Loc[1] = 0
                    Min_Y_Loc[k - 1] = H
                    Min_Y_Loc[k] = H + 2000
                    fixed_y_location[k] = H+2000
                    '''
                else:
                    print"Enter Height greater than or equal Minimum Height"
                    return None,None

            #data from GUI
            Nodes_H=fixed_x_location.keys()
            Nodes_V=fixed_y_location.keys()
            Nodes_H.sort()
            Nodes_V.sort()
            distance_H={}
            distance_V={}
            min_distance_H={}
            min_distance_V={}
            for i in range(len(Nodes_H)-1):
                distance_H[Nodes_H[i]]=fixed_x_location[Nodes_H[i+1]]-fixed_x_location[Nodes_H[i]]
                min_distance_H[Nodes_H[i]]=MIN_X[Nodes_H[i+1]]-MIN_X[Nodes_H[i]]
            for i in range(len(Nodes_V)-1):
                distance_V[Nodes_V[i]]=fixed_y_location[Nodes_V[i+1]]-fixed_y_location[Nodes_V[i]]
                min_distance_V[Nodes_V[i]]=MIN_Y[Nodes_V[i+1]]-MIN_Y[Nodes_V[i]]

            ### Creates fixed location table in (vertex:location) format
            for k, v in fixed_x_location.items():
                Min_X_Loc[k] = v
            for k, v in fixed_y_location.items():
                Min_Y_Loc[k] = v

            Min_X_Loc = collections.OrderedDict(sorted(Min_X_Loc.items()))
            Min_Y_Loc = collections.OrderedDict(sorted(Min_Y_Loc.items()))


            for k,v in Min_X_Loc.items():
                if k in distance_H:
                    if distance_H[k]<min_distance_H[k] or Min_X_Loc[k]<MIN_X[k] :
                        print"Invalid Location for X coordinate"
                        return None,None
            for k,v in Min_Y_Loc.items():
                if k in distance_V:
                    if distance_V[k]<min_distance_V[k]or Min_Y_Loc[k]<MIN_Y[k]  :
                        print"Invalid Location for Y coordinate"
                        return None,None

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts,
                                                      W=W, H=H, XLoc=Min_X_Loc, YLoc=Min_Y_Loc, seed=seed,
                                                      individual=individual,Types=self.Types)

            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)


            CS_SYM_Updated = CS_SYM_Updated['H'] # takes only horizontal corner stitch data
            #self.cur_fig_data = plot_layout(Layout_Rects, level,self.min_dimensions,Min_X_Loc,Min_Y_Loc)
            if count==None:
                #for i in range(len(Layout_Rects)):
                self.save_layouts(Layout_Rects, db=db)






        if bar:
            p_bar.close()
         # needs to be returned ---------------> updated_cs_islands
        return  CS_SYM_Updated, updated_cs_islands


    def update_islands(self,cs_sym_info,minx,miny,cs_islands1):
        '''
        :param cs_sym_info:
        :param cs_islands:
        :return:
        '''
        print cs_sym_info
        cs_islands=copy.deepcopy(cs_islands1)
        for i in range(len(cs_islands)):
            island=cs_islands[i]
            for element in island.elements:
                if element[-3] in cs_sym_info:
                    element[1]=cs_sym_info[element[-3]][1]
                    element[2]=cs_sym_info[element[-3]][2]
                    element[3]=cs_sym_info[element[-3]][3]
                    element[4] = cs_sym_info[element[-3]][4]
            for element in island.child:
                if element[-3] in cs_sym_info:
                    element[1]=cs_sym_info[element[-3]][1]
                    element[2]=cs_sym_info[element[-3]][2]
                    element[3]=cs_sym_info[element[-3]][3]
                    element[4] = cs_sym_info[element[-3]][4]
        #keys = ['N', 'S', 'E', 'W']
        for island in cs_islands:
            if len(island.child) == 0:

                #for element in island.elements:

                node_id = 1
                for node in island.mesh_nodes:
                    if node.pos[0] in minx[node_id] and node.pos[1] in miny[node_id]:
                        node.pos[0] = minx[node_id][node.pos[0]]
                        node.pos[1] = miny[node_id][node.pos[1]]
                '''
                for point in island.points:
                    if point[0] in minx[node_id] and point[1] in miny[node_id]:

                        point[0]=minx[node_id][point[0]]
                        point[1]=miny[node_id][point[1]]

                for k in keys:
                    for point in island.boundary_points[k]:

                        if point[0] in minx[node_id] and point[1] in miny[node_id]:
                            point[0]=minx[node_id][point[0]]
                            point[1]=miny[node_id][point[1]]
                '''

            else:
                for element in island.elements:
                    node_id = element[-1]
                    break
                for node in island.mesh_nodes:
                    if node.pos[0] in minx[node_id] and node.pos[1] in miny[node_id]:
                        node.pos[0] = minx[node_id][node.pos[0]]
                        node.pos[1] = miny[node_id][node.pos[1]]
                '''
                for point in island.points:
                    if point[0] in minx[node_id] and point[1] in miny[node_id]:

                        point[0]=minx[node_id][point[0]]
                        point[1]=miny[node_id][point[1]]

                for k in keys:
                    for point in island.boundary_points[k]:
                        if point[0] in minx[node_id] and point[1] in miny[node_id]:

                            point[0] = minx[node_id][point[0]]
                            point[1] = miny[node_id][point[1]]
                '''

        return cs_islands






    def populate_mesh_nodes(self,cs_islands=None,Htree=None,Vtree=None):
        '''

        :param cs_islands: list of cs islands
        :param Htree: Horizontal cs tree
        :param Vtree: Vertical cs tree
        :return: list of cs_islands populated with points list and boundary dictionary of each island
        '''

        all_points=[]
        all_boundaries=[]
        for island in cs_islands:
            points = []
            point_objects=[]
            N=[]
            S=[]
            E=[]
            W=[]

            if len(island.child)==0:
                for rect in island.elements:
                    nodeid=int(rect[-1])
                    for tile in Htree.hNodeList[nodeid-1].stitchList:
                        coordinate1=[tile.cell.x,tile.cell.y]
                        coordinate6=[tile.cell.x+tile.getWidth(),tile.cell.y+tile.getHeight()]
                        coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
                        coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]

                        if coordinate1 not in points:
                            points.append(coordinate1)
                        if coordinate6 not in points:
                            points.append(coordinate6)
                        if coordinate7 not in points:
                            points.append(coordinate7)
                        if coordinate8 not in points:
                            points.append(coordinate8)

                        if tile.EAST.cell.type=='EMPTY':
                            E.append(coordinate8)
                            E.append(coordinate6)
                        if tile.WEST.cell.type=="EMPTY":
                            W.append(coordinate1)
                            W.append(coordinate7)
                        if tile.NORTH.cell.type=='EMPTY':
                            N.append(coordinate7)
                            N.append(coordinate6)
                        if tile.SOUTH.cell.type=="EMPTY":
                            S.append(coordinate1)
                            S.append(coordinate8)


                    '''
                    for tile in Vtree.vNodeList[nodeid - 1].stitchList:
                        if tile.NORTH not in Vtree.vNodeList[nodeid - 1].boundaries:
                            coordinate3 = (tile.NORTH.cell.x, tile.NORTH.cell.y)
                            points.append(coordinate3)
                        if tile.SOUTH not in Vtree.vNodeList[nodeid - 1].boundaries:
                            coordinate5 = (tile.SOUTH.cell.x, tile.SOUTH.cell.y)
                            #points.append(coordinate5)
                    
                    
                    '''
                    for tile in Vtree.vNodeList[nodeid-1].stitchList:
                        coordinate1=[tile.cell.x,tile.cell.y]
                        coordinate6=[tile.cell.x+tile.getWidth(),tile.cell.y+tile.getHeight()]
                        coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
                        coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]
                        if tile.EAST.cell.type=='EMPTY':
                            E.append(coordinate8)
                            E.append(coordinate6)
                        if tile.WEST.cell.type=="EMPTY":
                            W.append(coordinate1)
                            W.append(coordinate7)
                        if tile.NORTH.cell.type=='EMPTY':
                            N.append(coordinate7)
                            N.append(coordinate6)
                        if tile.SOUTH.cell.type=="EMPTY":
                            S.append(coordinate1)
                            S.append(coordinate8)

                        if coordinate1 not in points:
                            points.append(coordinate1)
                        if coordinate6 not in points:
                            points.append(coordinate6)
                        if coordinate7 not in points:
                            points.append(coordinate7)
                        if coordinate8 not in points:
                            points.append(coordinate8)


            else:
                for rect in island.elements:
                    #print rect
                    nodeid=int(rect[-1])
                    #print "N",nodeid
                    break
                #print island.element_names
                for tile in Htree.hNodeList[nodeid - 1].stitchList:
                    coordinate1 = [tile.cell.x, tile.cell.y]
                    coordinate6 = [tile.cell.x + tile.getWidth(), tile.cell.y + tile.getHeight()]
                    coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
                    coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]

                    if coordinate1 not in points:
                        points.append(coordinate1)
                    if coordinate6 not in points:
                        points.append(coordinate6)
                    if coordinate7 not in points:
                        points.append(coordinate7)
                    if coordinate8 not in points:
                        points.append(coordinate8)

                    if tile.EAST.cell.type == 'EMPTY':
                        E.append(coordinate8)
                        E.append(coordinate6)
                    if tile.WEST.cell.type == "EMPTY":
                        W.append(coordinate1)
                        W.append(coordinate7)
                    if tile.NORTH.cell.type == 'EMPTY':
                        N.append(coordinate7)
                        N.append(coordinate6)
                    if tile.SOUTH.cell.type == "EMPTY":
                        S.append(coordinate1)
                        S.append(coordinate8)


                    # points.append(coordinate4)

                for tile in Vtree.vNodeList[nodeid - 1].stitchList:
                    coordinate1 = [tile.cell.x, tile.cell.y]
                    coordinate6 = [tile.cell.x + tile.getWidth(), tile.cell.y + tile.getHeight()]
                    coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
                    coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]
                    if tile.EAST.cell.type == 'EMPTY':
                        E.append(coordinate8)
                        E.append(coordinate6)
                    if tile.WEST.cell.type == "EMPTY":
                        W.append(coordinate1)
                        W.append(coordinate7)
                    if tile.NORTH.cell.type == 'EMPTY':
                        N.append(coordinate7)
                        N.append(coordinate6)
                    if tile.SOUTH.cell.type == "EMPTY":
                        S.append(coordinate1)
                        S.append(coordinate8)
                    if coordinate1 not in points:
                        points.append(coordinate1)
                    if coordinate6 not in points:
                        points.append(coordinate6)
                    if coordinate7 not in points:
                        points.append(coordinate7)
                    if coordinate8 not in points:
                        points.append(coordinate8)

                hnode = Htree.hNodeList[nodeid - 1]
                vnode = Vtree.vNodeList[nodeid - 1]
                cg = constraintGraph()
                zdl_h, zdl_v = cg.dimListFromLayer(hnode, vnode)
                # print zdl_h
                # print zdl_v
                intersections = list(itertools.product(zdl_h, zdl_v))
                intersection_points = [list(elem) for elem in intersections]
                #print len(intersection_points)
                for element in island.elements:
                    # print "EL", element[1],element[2],element[3],element[4],element[0],type(element[0])
                    for point in intersection_points:
                        x1 = point[0]
                        y1 = point[1]
                        for rect in Htree.hNodeList[0].stitchList:
                            # print rect.cell.x,rect.cell.y,rect.getWidth(),rect.getHeight(),rect.cell.type
                            # print rect.cell.type,type(rect.cell.type)

                            if rect.cell.x == element[1] and rect.cell.y == element[2] and rect.getWidth() == element[3] and rect.getHeight() == element[4] and rect.cell.type == str(element[0]):
                                # print"R", rect.cell.x, rect.cell.y, rect.getWidth(), rect.getHeight(), rect.cell.type
                                if x1 >= rect.cell.x and x1 <= rect.cell.x + rect.getWidth() and y1 >= rect.cell.y and y1 <= rect.cell.y + rect.getHeight() and point not in points:

                                    points.append(point)
                                    if point[0] == rect.cell.x:
                                        W.append(point)
                                    if point[0] == rect.cell.x + rect.getWidth():
                                        E.append(point)
                        for rect in Vtree.vNodeList[0].stitchList:

                            if rect.cell.x == element[1] and rect.cell.y == element[2] and rect.getWidth() == element[
                                3] and rect.getHeight() == element[4] and rect.cell.type == element[0]:
                                if x1 >= rect.cell.x and x1 <= rect.cell.x + rect.getWidth() and y1 >= rect.cell.y and y1 <= rect.cell.y + rect.getHeight() and point not in points:
                                    points.append(point)
                                    if point[1] == rect.cell.y:
                                        S.append(point)
                                    if point[1] == rect.cell.y + rect.getHeight():
                                        N.append(point)


            N = [list(item) for item in set(tuple(x) for x in N)]
            S = [list(item) for item in set(tuple(x) for x in S)]
            E = [list(item) for item in set(tuple(x) for x in E)]
            W = [list(item) for item in set(tuple(x) for x in W)]
            points=[list(item) for item in set(tuple(x) for x in points)]
            #island.points = points
            #island.boundary_points['N'] = N
            #island.boundary_points['S'] = S
            #island.boundary_points['E'] = E
            #island.boundary_points['W'] = W
            all_boundaries += N
            all_boundaries += S
            all_boundaries += E
            all_boundaries += W
            all_points += points

            for i in range(len(points)):
                node=MeshNode()
                node.pos=points[i]
                node.node_id=i
                if points[i] in N:
                    node.b_type=['N']
                elif points[i] in S:
                    node.b_type=['S']
                elif points[i] in E:
                    node.b_type=['E']
                elif points[i] in W:
                    node.b_type=['W']
                point_objects.append(node)

            island.mesh_nodes=point_objects




        #print "ALL",len(all_points)
        #print "Boundaries",len(all_boundaries)
        #group = Island()
        #group.plot_points(all_points, all_boundaries, size=(70, 80))


        """
        raw_input()

        for tile in Htree.hNodeList[nodeid - 1].stitchList:
            coordinate1 = [tile.cell.x, tile.cell.y]
            coordinate6 = [tile.cell.x + tile.getWidth(), tile.cell.y + tile.getHeight()]
            coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
            coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]
            '''
            if tile.EAST not in Htree.hNodeList[nodeid - 1].boundaries:
                coordinate2 = (tile.EAST.cell.x, tile.EAST.cell.y)
                points.append(coordinate2)
            if tile.WEST not in Htree.hNodeList[nodeid - 1].boundaries:
                coordinate4 = (tile.WEST.cell.x, tile.WEST.cell.y)
                #points.append(coordinate4)
            '''
            if tile.EAST.cell.type == 'EMPTY':
                E.append(coordinate8)
                E.append(coordinate6)
            if tile.WEST.cell.type == "EMPTY":
                W.append(coordinate1)
                W.append(coordinate7)
            if tile.NORTH.cell.type == 'EMPTY':
                N.append(coordinate7)
                N.append(coordinate6)
            if tile.SOUTH.cell.type == "EMPTY":
                S.append(coordinate1)
                S.append(coordinate8)

            if coordinate1 not in points:
                points.append(coordinate1)
            if coordinate6 not in points:
                points.append(coordinate6)
            if coordinate7 not in points:
                points.append(coordinate7)
            if coordinate8 not in points:
                points.append(coordinate8)
            # points.append(coordinate4)
        '''
        for tile in Vtree.vNodeList[nodeid - 1].stitchList:
            if tile.NORTH not in Vtree.vNodeList[nodeid - 1].boundaries:
                coordinate3 = (tile.NORTH.cell.x, tile.NORTH.cell.y)
                points.append(coordinate3)
            if tile.SOUTH not in Vtree.vNodeList[nodeid - 1].boundaries:
                coordinate5 = (tile.SOUTH.cell.x, tile.SOUTH.cell.y)
                #points.append(coordinate5)                
        
        '''
        for tile in Vtree.vNodeList[nodeid - 1].stitchList:
            coordinate1 = [tile.cell.x, tile.cell.y]
            coordinate6 = [tile.cell.x + tile.getWidth(), tile.cell.y + tile.getHeight()]
            coordinate7 = [tile.cell.x, tile.cell.y + tile.getHeight()]
            coordinate8 = [tile.cell.x + tile.getWidth(), tile.cell.y]
            if tile.EAST.cell.type == 'EMPTY':
                E.append(coordinate8)
                E.append(coordinate6)
            if tile.WEST.cell.type == "EMPTY":
                W.append(coordinate1)
                W.append(coordinate7)
            if tile.NORTH.cell.type == 'EMPTY':
                N.append(coordinate7)
                N.append(coordinate6)
            if tile.SOUTH.cell.type == "EMPTY":
                S.append(coordinate1)
                S.append(coordinate8)
            if coordinate1 not in points:
                points.append(coordinate1)
            if coordinate6 not in points:
                points.append(coordinate6)
            if coordinate7 not in points:
                points.append(coordinate7)
            if coordinate8 not in points:
                points.append(coordinate8)
        """







        return cs_islands





    def form_cs_island(self,islands=None, Htree=None, Vtree=None):
        '''

        :param islands: list of islands from input script
        :param Htree: Horizontal corner stitch tree
        :param Vtree: Vertical corner stitch tree
        :return: list of corner stitch tile mapped rectangles
        '''
        copy_islands = copy.deepcopy(islands)  # list of islands converting input rects to corner stitch tiles
        HorizontalNodeList = []
        VerticalNodeList = []
        for node in Htree.hNodeList:
            if node.child == []:
                continue
            else:
                HorizontalNodeList.append(node)  # only appending all horizontal tree nodes which have children. Nodes having no children are not included

        for node in Vtree.vNodeList:
            if node.child == []:
                continue
            else:
                VerticalNodeList.append(node)  # only appending all vertical tree nodes which have children. Nodes having no children are not included

        cs_islands = []
        cs_mapped_input={}
        for island in copy_islands:
            cs_island = Island()
            cs_island.name = island.name
            elements = island.elements
            child = island.child
            cs_elements = []
            cs_child = []
            for rect in elements:
                for node in HorizontalNodeList:
                    for i in node.stitchList:
                        if rect[1] == i.cell.x and rect[2] == i.cell.y and rect[3] == i.getWidth() and rect[4] == i.getHeight() and rect[0] == i.cell.type:
                            r = [rect[0], rect[1], rect[2], rect[3], rect[4], rect[5], rect[8],i.nodeId]  # type,x,y,width,height,name, hierarchy_level, nodeId
                            cs_elements.append(r)
                            cs_mapped_input[rect[5]]=[i,node,rect[8]]
                            cs_island.element_names.append(rect[5])
                for node in VerticalNodeList:
                    for i in node.stitchList:
                        if rect[1] == i.cell.x and rect[2] == i.cell.y and rect[3] == i.getWidth() and rect[4] == i.getHeight() and rect[0] == i.cell.type:
                            r = [rect[0], rect[1], rect[2], rect[3], rect[4], rect[5], rect[8], i.nodeId]
                            if r not in cs_elements:
                                cs_elements.append(r)
                                cs_mapped_input[rect[5]] =[i,node,rect[8]]
                                cs_island.element_names.append(rect[5])

            cs_island.elements = cs_elements
            if len(child) > 0:
                for rect in child:
                    for node in HorizontalNodeList:
                        for i in node.stitchList:
                            if rect[1] == i.cell.x and rect[2] == i.cell.y and rect[3] == i.getWidth() and rect[4] == i.getHeight() and rect[0] == i.cell.type:
                                r = [rect[0], rect[1], rect[2], rect[3], rect[4], rect[5], rect[8], node.id] # type,x,y,width,height,name, hierarchy_level, parent nodeId
                                cs_child.append(r)
                                cs_mapped_input[rect[5]] =[i,node,rect[8]]
                                cs_island.child_names.append(rect[5])
                    for node in VerticalNodeList:
                        for i in node.stitchList:
                            if rect[1] == i.cell.x and rect[2] == i.cell.y and rect[3] == i.getWidth() and rect[4] == i.getHeight() and rect[0] == i.cell.type:
                                r = [rect[0], rect[1], rect[2], rect[3], rect[4], rect[5], rect[8], node.id]
                                if r not in cs_child:
                                    cs_child.append(r)
                                    cs_mapped_input[rect[5]] =[i,node,rect[8]]
                                    cs_island.child_names.append(rect[5])

            cs_island.child = cs_child
            cs_islands.append(cs_island)
        '''
        for i in cs_islands:
            print i.print_island()
        
        '''



        return cs_islands,cs_mapped_input

    def save_layout(self,Layout_Rects, count, db):
        # print Layout_Rects

        data = []

        for k, v in Layout_Rects.items():
            for R_in in v:
                data.append(R_in)

            data.append([k[0], k[1]])

        l_data = [count, data]
        directory = os.path.dirname(db)
        temp_file = directory + '/out.txt'

        with open(temp_file, 'wb') as f:
            f.writelines(["%s\n" % item for item in data])
            # f.write(''.join(chr(i) for i in range(data)))
        conn = create_connection(db)
        with conn:
            insert_record(conn, l_data, temp_file)
        conn.close()


    def save_layouts(self,Layout_Rects,count=None, db=None):
        max_x = 0
        max_y = 0
        min_x = 1e30
        min_y = 1e30
        Total_H = {}
        for i in Layout_Rects:
            if i[0] + i[2] > max_x:
                max_x = i[0] + i[2]
            if i[1] + i[3] > max_y:
                max_y = i[1] + i[3]
            if i[0] < min_x:
                min_x = i[0]
            if i[1] < min_y:
                min_y = i[1]
            key = (max_x, max_y)
        Total_H.setdefault(key, [])
        Total_H[(max_x, max_y)].append(Layout_Rects)
        colors = ['white', 'green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']
        type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8', 'Type_9']
        if count == None:
            j = 0
        else:
            j = count
        for k, v in Total_H.items():
            # print v, len(v)
            for c in range(len(v)):
                # print "C",c,len(v)
                data = []
                Rectangles = v[c]

                for i in Rectangles:
                    for t in type:
                        if i[4] == t:
                            type_ind = type.index(t)
                            colour = colors[type_ind]
                            if type[type_ind] in self.min_dimensions:
                                w = self.min_dimensions[t][0]
                                h = self.min_dimensions[t][1]
                            else:
                                w = None
                                h = None
                    if w == None and h == None:
                        R_in = [i[0], i[1], i[2], i[3], colour, i[-1], 'None', 'None']
                    else:

                        center_x = (i[0] + i[0] + i[2]) / float(2)
                        center_y = (i[1] + i[1] + i[3]) / float(2)
                        x = center_x - w / float(2)
                        y = center_y - h / float(2)
                        R_in = [i[0], i[1], i[2], i[3], 'white', 0, '--', 'black']
                        R_in1 = [x, y, w, h, colour, i[-1], 'None', 'None']
                        data.append(R_in1)
                    data.append(R_in)

                data.append([k[0], k[1]])
                l_data = [j, data]
                directory = os.path.dirname(db)
                temp_file = directory + '/out.txt'
                with open(temp_file, 'wb') as f:
                    f.writelines(["%s\n" % item for item in data])
                conn = create_connection(db)
                with conn:
                    insert_record(conn, l_data, temp_file)

                if count == None:
                    j += 1
            conn.close()



    """
    def save_layouts(self,Layout_Rects,count=None, db=None):



        for k,v in Layout_Rects.items():

            if k=='H':
                Total_H = {}
                for j in range(len(v)):


                    Rectangles = []
                    for rect in v[j]:  # rect=[x,y,width,height,type]
                        Rectangles.append(rect)
                    max_x = 0
                    max_y = 0
                    min_x = 1e30
                    min_y = 1e30

                    for i in Rectangles:
                        print i
                        if i[0] + i[2] > max_x:
                            max_x = i[0] + i[2]
                        if i[1] + i[3] > max_y:
                            max_y = i[1] + i[3]
                        if i[0] < min_x:
                            min_x = i[0]
                        if i[1] < min_y:
                            min_y = i[1]
                    key=(max_x,max_y)

                    Total_H.setdefault(key,[])
                    Total_H[(max_x,max_y)].append(Rectangles)
        colors = ['white', 'green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']
        type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8', 'Type_9']
        if count==None:
            j=0
        else:
            j=count
        for k, v in Total_H.items():
            #print v, len(v)
            for c in range(len(v)):
                #print "C",c,len(v)
                data = []
                Rectangles = v[c]

                for i in Rectangles:
                    for t in type:
                        if i[4] == t:
                            type_ind = type.index(t)
                            colour = colors[type_ind]
                            if type_ind in self.min_dimensions:
                                w=self.min_dimensions[t][0]
                                h=self.min_dimensions[t][1]
                            else:
                                w=None
                                h=None
                    if w==None and h==None:
                        R_in=[i[0],i[1],i[2],i[3],colour,1,'None','None']
                    else:

                        center_x=(i[0]+i[0]+i[2])/float(2)
                        center_y=(i[1]+i[1]+i[3])/float(2)
                        x=center_x-w/float(2)
                        y=center_y-h/float(2)
                        R_in = [i[0], i[1], i[2], i[3],'green',1,'--','black']
                        R_in1 = [x, y, w, h, colour, 2,'None','None']
                        data.append(R_in1)
                    data.append(R_in)
                


                data.append([k[0], k[1]])
                l_data = [j, data]
                directory = os.path.dirname(db)
                temp_file = directory + '/out.txt'
                with open(temp_file, 'wb') as f:
                    f.writelines(["%s\n" % item for item in data])
                conn = create_connection(db)
                with conn:
                    insert_record(conn, l_data, temp_file)

               
                if count==None:
                    j+=1
            conn.close()
    
    
    """







def plot_layout(Layout_Rects,level,min_dimensions=None,Min_X_Loc=None,Min_Y_Loc=None):
    #global min_dimensions
    # Prepares solution rectangles as patches according to the requirement of mode of operation
    Patches=[]
    if level==0:
        Rectangles=[]
        '''
        for k,v in Layout_Rects.items():
            if k=='H':
                for rect in v:                    #rect=[x,y,width,height,type]
                    Rectangles.append(rect)
        
        
        '''
        Rectangles=Layout_Rects

        max_x = 0
        max_y = 0
        min_x = 1e30
        min_y = 1e30

        for i in Rectangles:

            if i[0] + i[2] > max_x:
                max_x = i[0] + i[2]
            if i[1] + i[3] > max_y:
                max_y = i[1] + i[3]
            if i[0] < min_x:
                min_x = i[0]
            if i[1] < min_y:
                min_y = i[1]
        colors = ['white','green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']
        type = ['EMPTY','Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8', 'Type_9']
        ALL_Patches={}
        key=(max_x,max_y)
        #print key
        ALL_Patches.setdefault(key,[])
        for i in Rectangles:
            for t in type:
                if i[4]==t:

                    type_ind=type.index(t)
                    colour=colors[type_ind]
            R=matplotlib.patches.Rectangle(
                    (i[0], i[1]),  # (x,y)
                    i[2],  # width
                    i[3],  # height
                    facecolor=colour,


                )
            ALL_Patches[key].append(R)
        Patches.append(ALL_Patches)



    else:


        for k,v in Layout_Rects.items():

            if k=='H':
                Total_H = {}

                for j in range(len(v)):


                    Rectangles = []
                    for rect in v[j]:  # rect=[x,y,width,height,type]

                        Rectangles.append(rect)
                    max_x = 0
                    max_y = 0
                    min_x = 1e30
                    min_y = 1e30

                    for i in Rectangles:

                        if i[0] + i[2] > max_x:
                            max_x = i[0] + i[2]
                        if i[1] + i[3] > max_y:
                            max_y = i[1] + i[3]
                        if i[0] < min_x:
                            min_x = i[0]
                        if i[1] < min_y:
                            min_y = i[1]
                    key=(max_x,max_y)

                    Total_H.setdefault(key,[])
                    Total_H[(max_x,max_y)].append(Rectangles)
        plot = 0
        for k,v in Total_H.items():

            for i in range(len(v)):

                Rectangles = v[i]
                max_x=k[0]
                max_y=k[1]
                ALL_Patches = {}
                key = (max_x, max_y)
                ALL_Patches.setdefault(key, [])

                colors = ['white', 'green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']

                type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8','Type_9']
                for i in Rectangles:
                    for t in type:
                        if i[4] == t:

                            type_ind = type.index(t)
                            colour = colors[type_ind]

                            if type[type_ind] in min_dimensions:

                                w=min_dimensions[t][0]
                                h=min_dimensions[t][1]
                            else:
                                w=None
                                h=None
                    if w==None and h==None:

                        R= matplotlib.patches.Rectangle(
                                (i[0], i[1]),  # (x,y)
                                i[2],  # width
                                i[3],  # height
                                facecolor=colour

                            )
                    else:
                        #print Min_X_Loc
                        #print Min_Y_Loc
                        '''
                        if (i[0]+i[2])*1000 in Min_X_Loc.values():
                            x=i[0]+i[2]-w
                            y=i[1]
                        elif (i[1]+i[3])*1000 in Min_Y_Loc.values():
                            x=i[0]
                            y=i[1]+i[3]-h
                        elif (i[0]+i[2])*1000 in Min_X_Loc.values() and (i[1]+i[3])*1000 in Min_Y_Loc.values():
                            x = [0]+i[2] - w
                            y = i[1]+i[3]-h
                        elif (i[0])*1000 in Min_X_Loc.values() or (i[1])*1000 in Min_Y_Loc.values():
                            x=i[0]
                            y=i[1]
                        else:
                        '''
                        center_x=(i[0]+i[0]+i[2])/float(2)
                        center_y=(i[1]+i[1]+i[3])/float(2)
                        x=center_x-w/float(2)
                        y=center_y-h/float(2)

                        R = matplotlib.patches.Rectangle(
                            (i[0], i[1]),  # (x,y)
                            i[2],  # width
                            i[3],  # height
                            facecolor='green',
                            linestyle='--',
                            edgecolor='black',
                            zorder=1


                        )#linestyle='--'

                        R1=matplotlib.patches.Rectangle(
                            (x, y),  # (x,y)
                            w,  # width
                            h,  # height
                            facecolor=colour,
                            zorder=2


                        )
                        ALL_Patches[key].append(R1)

                    ALL_Patches[key].append(R)
                plot+=1
                Patches.append(ALL_Patches)


    return Patches



def intersection_pt(line1, line2):    # Find intersection point of 2 orthogonal traces
    x = 0                                    # initialize at 0
    y = 0                                    # initialize at 0
    if line1.vertical:                       # line 1 is vertical
        x = line1.pt1[0]                     # take the x value from line 1
    else:                                    # line 1 is horizontal
        y = line1.pt1[1]                     # take the y value from line 1

    if line2.vertical:                       # line2 is vertical
        x = line2.pt1[0]                     # take the x value from line 2
    else:                                    # line 2 is horizontal
        y = line2.pt1[1]                     # take the y value from line 2

    return x, y








def Sym_to_CS(input_rects,Htree,Vtree):
    '''

    :param input_rects: rectangle version of symbolic layout objects
    :param Htree: Horizontal corner stitch tree
    :param Vtree: Vertical corner stitch tree
    :return:
    '''
    # Converts corner stitch rectangles to powersynth objects . Makes a list of tiles mapping each powersynth lyout object

    HorizontalNodeList = []
    VerticalNodeList = []
    for node in Htree.hNodeList:
        if node.child == []:
            continue
        else:
            HorizontalNodeList.append(node)  # only appending all horizontal tree nodes which have children. Nodes having no children are not included

    for node in Vtree.vNodeList:
        if node.child == []:
            continue
        else:
            VerticalNodeList.append(node)  # only appending all vertical tree nodes which have children. Nodes having no children are not included



    ALL_RECTS = {'H':[],'V':[]}
    for node in HorizontalNodeList:
        for i in node.stitchList:
            for j in input_rects:
                #if j.hier_level==0:

                if j.x==i.cell.x and j.y==i.cell.y and j.type==i.cell.type and j.width==i.getWidth() and j.height==i.getHeight():
                    i.name=j.name
                    if node.parent!=None:
                        for m in ALL_RECTS['H']:
                            for k,v in m.items():
                                if v[0].nodeId==node.id:
                                    i.parent_name=v[0].name

                    #if node.parent!=None:
                    #print i.nodeId,j.name,node.id
                    if node.parent==None:
                        dict = {j.name: [i, node.parent]}
                    else:
                        dict={j.name:[i,node]}
                    if dict not in ALL_RECTS['H']:
                        ALL_RECTS['H'].append(dict)



    for node in VerticalNodeList:
        for i in node.stitchList:
            for j in input_rects:
                #if j.hier_level == 0:
                if j.x == i.cell.x and j.y == i.cell.y and j.type == i.cell.type and j.width == i.getWidth() and j.height == i.getHeight():
                    i.name=j.name
                    if node.parent!=None:
                        for m in ALL_RECTS['V']:
                            for k,v in m.items():
                                if v[0].nodeId==node.id:
                                    i.parent_name=v[0].name
                    if node.parent==None:
                        dict = {j.name: [i, node.parent]}
                    else:
                        dict={j.name:[i,node]}
                    if dict not in ALL_RECTS['V']:
                        ALL_RECTS['V'].append(dict)

    '''
    for i in ALL_RECTS['H']:
        for k,v in i.items():
            print v[0].name,v[0].parent_name
    
    '''
    return ALL_RECTS['H']

    #return ALL_RECTS
    '''
    raw_input()


    SYM_CS={}
    for rect in input_rects:
        x1=rect.x
        y1=rect.y
        x2=rect.x+rect.width
        y2=rect.y+rect.height
        type=rect.type
        name=rect.name
        for k,v in ALL_RECTS.items():
            if k=='H':
                key=name
                SYM_CS.setdefault(key,[])
                for i in v:
                    if i[0]>=x1 and i[1]>=y1 and i[0]+i[2]<=x2 and i[1]+i[3]<=y2 and i[4]==type:
                        SYM_CS[key].append(i)

                    else:
                        continue

    return SYM_CS
    
    
    '''



