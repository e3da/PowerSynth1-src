
from powercad.sym_layout.plot import plot_layout
from powercad.project_builder.proj_dialogs import New_layout_engine_dialog
from powercad.corner_stitch.API_PS import *
from powercad.corner_stitch.CornerStitch import *
from powercad.general.data_struct.util import *


def plot_layout(Layout_Rects,level,path=None,name=None):
    Patches=[]
    if level==0:
        Rectangles=[]
        for k,v in Layout_Rects.items():
            if k=='H':
                for rect in v:                    #rect=[x,y,width,height,type]
                    Rectangles.append(rect)
        max_x = 0
        max_y = 0
        min_x = 1000
        min_y = 1000

        for i in Rectangles:

            if i[0] + i[2] > max_x:
                max_x = i[0] + i[2]
            if i[1] + i[3] > max_y:
                max_y = i[1] + i[3]
            if i[0] < min_x:
                min_x = i[0]
            if i[1] < min_y:
                min_y = i[1]
        colors=['White','green','red','blue','yellow','pink']
        type=['EMPTY','Type_1','Type_2','Type_3','Type_4']
        ALL_Patches={}
        key=(max_x,max_y)
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
                    facecolor=colour
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
                    min_x = 1000
                    min_y = 1000

                    for i in Rectangles:
                        #print i
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
        j = 0


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
                    R= matplotlib.patches.Rectangle(
                            (i[0], i[1]),  # (x,y)
                            i[2],  # width
                            i[3],  # height
                            facecolor=colour
                        )
                    ALL_Patches[key].append(R)
                j+=1
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
    ALL_RECTS={}
    DIM=[]

    for j in Htree.hNodeList[0].stitchList:

        #for j in i.stitchList:
        p = [j.cell.x, j.cell.y, j.getWidth(), j.getHeight(), j.cell.type]
        DIM.append(p)
    ALL_RECTS['H']=DIM
    DIM = []
    for j in Vtree.vNodeList[0].stitchList:

        #for j in i.stitchList:
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



class New_layout_engine():
    def __init__(self):
        self. W =None
        self. H =None
        self.window =None
        self.Htree =None
        self.Vtree =None
        self.cons_df =None
        self.Min_X =None
        self.Min_Y =None
        # self.level=None
        # for initialize only
        self.init_data =[]
        self.cornerstitch =CornerStitch()
        # current solutions
        self.cur_fig_data =None
        # only activate when the sym_layout API is used
        self.sym_layout =None
        self.layout_sols ={}
    def open_new_layout_engine(self ,window):
        self.window =window
        patches = self.init_data[0]
        graph =self.init_data[2]
        self.new_layout_engine = New_layout_engine_dialog(self.window, patches, W=self. W +20 ,H= self. H +20
                                                          ,engine=self,
                                                          graph=graph)
        self.new_layout_engine.exec_()
    def init_layout_from_symlayout(self ,sym_layout):
        '''
        initialize new layout engine with old symlayout data structure
        Returns:
        '''
        print "initializing ....."
        self.sym_layout =sym_layout
        input_rects, self.W, self.H = input_conversion(sym_layout)
        input = self.cornerstitch.read_input('list', Rect_list=input_rects)
        self.Htree, self.Vtree = self.cornerstitch.input_processing(input, self.W + 20, self.H + 20)

        patches ,combined_graph =self.cornerstitch.draw_layout(input_rects)
        sym_to_cs = Sym_to_CS(input_rects, self.Htree, self.Vtree)

        self.init_data =[patches ,sym_to_cs ,combined_graph]

    def mode_zero(self):
        # print"pass"
        CG1 = CS_to_CG(0)
        # CG1.getConstraints(path+'/'+'Constraints-1.csv')
        CG1.getConstraints(self.cons_df)
        Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None ,XLoc=None
                                                  ,YLoc=None)
        return Evaluated_X ,Evaluated_Y

    def generate_solutions(self ,level ,num_layouts=1 ,W=None ,H=None ,fixed_x_location=None ,fixed_y_location=None):
        # self.level=level
        CG1 = CS_to_CG(level)
        # CG1.getConstraints(path+'/'+'Constraints-1.csv')
        CG1.getConstraints(self.cons_df)
        sym_to_cs =self.init_data[1]
        if level == 0:
            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None
                                                      ,XLoc=None ,YLoc=None)
            CS_SYM_information, Layout_Rects = CG1.UPDATE_min(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree
                                                              ,sym_to_cs)  # CS_SYM_information is a dictionary where key=path_id(component name) and value=list of updated rectangles, Layout Rects is a dictionary for minimum HCS and VCS evaluated rectangles (used for plotting only)


            self.cur_fig_data = plot_layout(Layout_Rects, level)

            CS_SYM_Updated ={}
            for i in self.cur_fig_data:
                for k ,v in i.items():
                    CS_SYM_Updated[k ] =CS_SYM_information
            CS_SYM_Updated = [CS_SYM_Updated]
        elif level==1:

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=None, H=None
                                                      ,XLoc=None, YLoc=None)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y ,self.Htree, self.Vtree, sym_to_cs)
            CS_SYM_Updated = CS_SYM_Updated['H']
            self.cur_fig_data = plot_layout(Layout_Rects, level)
        elif level==2:
            CG2 = CS_to_CG(0)
            Evaluated_X0, Evaluated_Y0 = CG2.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None
                                                        ,XLoc=None ,YLoc=None)

            # print"Eval0", Evaluated_X0, Evaluated_Y0
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


            for k ,v in Min_X_Loc.items():
                if W>= v:
                    Min_X_Loc[0] = 0
                    Min_X_Loc[k] = W
            for k, v in Min_Y_Loc.items():
                if H >= v:
                    Min_Y_Loc[0] = 0
                    Min_Y_Loc[k] = H

            Min_X_Loc = collections.OrderedDict(sorted(Min_X_Loc.items()))
            Min_Y_Loc = collections.OrderedDict(sorted(Min_Y_Loc.items()))
            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=W, H=H,
                                                      XLoc=Min_X_Loc, YLoc=Min_Y_Loc)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs)
            CS_SYM_Updated = CS_SYM_Updated['H']
            self.cur_fig_data = plot_layout(Layout_Rects, level)
        elif level == 3:
            CG2 = CS_to_CG(0)
            Evaluated_X0, Evaluated_Y0 = CG2.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=None, W=None, H=None,
                                                        XLoc=None, YLoc=None)

            # print"Eval0", Evaluated_X0, Evaluated_Y0
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

            # Min_X_Loc[0] = 0
            # Min_Y_Loc[0] = 0
            Min_X_Loc[len(XLoc) - 1] = max_x
            Min_Y_Loc[len(YLoc) - 1] = max_y

            for k, v in Min_X_Loc.items():
                if W > v:
                    Min_X_Loc[0] = 0
                    Min_X_Loc[k] = W
            for k, v in Min_Y_Loc.items():
                if H > v:
                    Min_Y_Loc[0] = 0
                    Min_Y_Loc[k] = H
            # print "Node", self.init_data[2][1] #Gives the dictionary where key= Node# and value=initial (x,y) coordinate
            ### Data from GUI
            for k, v in fixed_x_location.items():
                Min_X_Loc[k] = v
            for k, v in fixed_y_location.items():
                Min_Y_Loc[k] = v

            Min_X_Loc = collections.OrderedDict(sorted(Min_X_Loc.items()))
            Min_Y_Loc = collections.OrderedDict(sorted(Min_Y_Loc.items()))

            Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=self.Htree, Vtree=self.Vtree, N=num_layouts, W=W, H=H,
                                                      XLoc=Min_X_Loc, YLoc=Min_Y_Loc)
            CS_SYM_Updated, Layout_Rects = CG1.UPDATE(Evaluated_X, Evaluated_Y, self.Htree, self.Vtree, sym_to_cs)

            CS_SYM_Updated = CS_SYM_Updated['H']
            self.cur_fig_data = plot_layout(Layout_Rects, level)

        return self.cur_fig_data, CS_SYM_Updated