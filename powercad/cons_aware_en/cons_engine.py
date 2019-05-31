from powercad.project_builder.proj_dialogs import New_layout_engine_dialog
import pandas as pd
from powercad.corner_stitch.API_PS import *
from powercad.corner_stitch.CornerStitch import *
from powercad.design.library_structures import *
from powercad.cons_aware_en.database import *
from tqdm import tqdm

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
        self.Types=None

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
        self.new_layout_engine = New_layout_engine_dialog(self.window, patches, W=self.W + 20, H=self.H + 20 , engine=self,graph=graph)
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
    '''
    def init_layout_from_symlayout(self, sym_layout=None):
        
        #initialize new layout engine with old symlayout data structure
        #Returns:
        
        print "initializing ....."
        self.sym_layout = sym_layout


        if sym_layout != None:
            self.cons_info = self.collect_sym_cons_info(sym_layout)
            self.cons_df = self.cons_from_ps()


        # ------------------------------------------
        input_rects, self.W, self.H = input_conversion(sym_layout)  # converts symbolic layout lines and points into rectangles
        input = self.cornerstitch.read_input('list', Rect_list=input_rects) # Makes the rectangles compaitble to new layout engine input format

        self.Htree, self.Vtree = self.cornerstitch.input_processing(input, self.W + 20, self.H + 20) # creates horizontal and vertical corner stitch layouts
        num_columns=len(self.Htree.hNodeList[0].stitchList)

        patches, combined_graph = self.cornerstitch.draw_layout(rects=input_rects,Htree=self.Htree,Vtree=self.Vtree) # collects initial layout patches and combined HCS,VCS points as a graph for mode-3 representation
        sym_to_cs = Sym_to_CS(input_rects, self.Htree, self.Vtree) # maps corner stitch tiles to symbolic layout objects

        self.init_data = [patches, sym_to_cs, combined_graph,num_columns]

    
    '''


    def create_cornerstitch(self,input_rects=None, size=None):
        #cornerstitch = CornerStitch()
        input = self.cornerstitch.read_input('list',Rect_list=input_rects)  # Makes the rectangles compaitble to new layout engine input format
        self.Htree, self.Vtree = self.cornerstitch.input_processing(input, size[0],size[1])  # creates horizontal and vertical corner stitch layouts
        patches, combined_graph = self.cornerstitch.draw_layout(rects=input_rects, Htree=self.Htree,Vtree=self.Vtree)  # collects initial layout patches and combined HCS,VCS points as a graph for mode-3 representation
        '''
        plot = True
        if plot:
            plot_layout(fig=patches, size=size)
        '''


        sym_to_cs = Sym_to_CS(input_rects, self.Htree, self.Vtree)  # maps corner stitch tiles to symbolic layout objects
        print sym_to_cs
        self.init_data = [patches, sym_to_cs, combined_graph]
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
        Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None, XLoc=None, YLoc=None,seed=None,individual=None,Types=self.Types)


        return Evaluated_X, Evaluated_Y


    # generate layout solutions using constraint graph edge weights randomization for different modes(level)
    def generate_solutions(self, level, num_layouts=1, W=None, H=None, fixed_x_location=None, fixed_y_location=None,seed=None,individual=None,bar=False):
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
        scaler = 1000  # to get back original dimensions all coordinated will be scaled down by 1000
        #mode-0
        if level == 0:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None, XLoc=None, YLoc=None,seed=None,individual=None,Types=self.Types) # for minimum sized layout only one solution is generated
            CS_SYM_information, Layout_Rects = CG1.UPDATE_min(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree ,sym_to_cs,scaler)  # CS_SYM_information is a dictionary where key=path_id(component name) and value=list of updated rectangles, Layout Rects is a dictionary for minimum HCS and VCS evaluated rectangles (used for plotting only)
            self.cur_fig_data = plot_layout(Layout_Rects, level)
            CS_SYM_Updated = {}
            for i in self.cur_fig_data:
                for k, v in i.items():
                    k=(k[0]*scaler,k[1]*scaler)
                    CS_SYM_Updated[k] = CS_SYM_information
            CS_SYM_Updated = [CS_SYM_Updated] # mapped solution layout information to symbolic layout objects


        #mode-1
        elif level == 1:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=None, H=None,
                                                      XLoc=None, YLoc=None, seed=seed, individual=individual)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)
            CS_SYM_Updated = CS_SYM_Updated['H']
            #self.cur_fig_data = plot_layout(Layout_Rects, level)
            #self.cur_fig_data=None
            self.save_layouts(Layout_Rects, p_bar)
            self.cur_fig_data = None

        #mode-2
        elif level == 2:
            Evaluated_X0, Evaluated_Y0 = self.mode_zero() # mode-0 evaluation is required to check the validity of given floorplan size
            ZDL_H={}
            ZDL_V={}
            for k,v in Evaluated_X0.items():
                ZDL_H=v
            for k,v in Evaluated_Y0.items():
                ZDL_V=v
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

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=W, H=H,
                                                      XLoc=Min_X_Loc, YLoc=Min_Y_Loc, seed=seed, individual=individual) # evaluates and finds updated locations for each coordinate

            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)
            CS_SYM_Updated = CS_SYM_Updated['H'] # takes only horizontal corner stitch data
            #self.cur_fig_data = plot_layout(Layout_Rects, level) #collects the layout patches
            if self.new_layout_engine.opt_algo!="NSGAII":
                self.save_layouts(Layout_Rects, p_bar)
                self.cur_fig_data = None
            else:
                self.cur_fig_data=Layout_Rects




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
                if W > v:
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
                if H > v:
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
                                                      individual=individual)

            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs,scaler)


            CS_SYM_Updated = CS_SYM_Updated['H'] # takes only horizontal corner stitch data
            #self.cur_fig_data = plot_layout(Layout_Rects, level,Min_X_Loc,Min_Y_Loc)
            self.save_layouts(Layout_Rects, p_bar)



            self.cur_fig_data = None

        if bar:
            p_bar.close()

        return self.cur_fig_data, CS_SYM_Updated

    def save_layouts(self,Layout_Rects,p_bar=None):
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
        colors = ['White', 'green', 'red', 'blue', 'yellow', 'pink']
        type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4']
        j=0
        for k, v in Total_H.items():
            #print v, len(v)
            for c in range(len(v)):
                #print "C",c,len(v)
                data = []
                item = 'Layout ' + str(j)
                # data.append(item)
                Rectangles = v[c]

                for i in Rectangles:
                    for t in type:
                        if i[4] == t:
                            type_ind = type.index(t)
                            colour = colors[type_ind]
                            if type_ind>1:
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
                '''
                data.append([k[0], k[1], 'None', 'None', 'None', 'None', 'None', 'None'])

                conn = create_connection(self.new_layout_engine.db)
                with conn:
                    # create a new project
                    table = 'Layout_' + str(j)
                    try:
                        p_bar.update(j)
                    except:
                        print table
                    create_table(conn, name=table)
                    for d in data:
                        insert_record(conn, table, d)
                
                
                
                '''
                table = 'Layout_' + str(j)
                try:
                    #p_bar.update(j)
                    p_bar.update(1)
                except:
                    print table
                data.append([k[0], k[1]])
                l_data = [j, data]
                #data_s=json.dumps(l_data)
                temp_file=self.new_layout_engine.parent.project.directory+'/out.txt'
                with open(temp_file, 'wb') as f:
                    f.writelines(["%s\n" % item for item in data])
                conn = create_connection(self.new_layout_engine.db)
                with conn:
                    insert_record(conn, l_data,temp_file)

                '''
                file_name = self.new_layout_engine.directory+'/' + item + '.csv'

                with open(file_name, 'wb') as my_csv:
                    csv_writer = csv.writer(my_csv, delimiter=',')
                    data.append([k[0], k[1]])
                    # csv_writer.writerow(data) #Name, [x,y,w,h,color,zorder],......,W,H
                    for i in data:
                        csv_writer.writerow(i)

                my_csv.close()
                
                '''

                j+=1
            conn.close()

def plot_layout(Layout_Rects,level,Min_X_Loc=None,Min_Y_Loc=None):
    #global min_dimensions
    # Prepares solution rectangles as patches according to the requirement of mode of operation
    Patches=[]
    if level==0:
        Rectangles=[]
        for k,v in Layout_Rects.items():
            if k=='H':
                for rect in v:                    #rect=[x,y,width,height,type]

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


    """
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


                colors = ['White', 'green', 'red', 'blue', 'yellow', 'pink']
                type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4']
                for i in Rectangles:
                    for t in type:
                        if i[4] == t:
                            type_ind = type.index(t)
                            colour = colors[type_ind]
                            if type_ind>1:
                                w=self.min_dimensions[t][0]
                                h=self.min_dimensions[t][1]
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
    """

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
    ALL_RECTS={}
    DIM=[]

    for j in Htree.hNodeList[0].stitchList:
        p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
        DIM.append(p)
    ALL_RECTS['H']=DIM
    DIM = []
    for j in Vtree.vNodeList[0].stitchList:
        p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
        DIM.append(p)
    ALL_RECTS['V']=DIM

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


