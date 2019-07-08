from powercad.corner_stitch.CornerStitch import Rectangle
from powercad.cons_aware_en.database import *
import matplotlib.pyplot as plt
import matplotlib
class CornerStitchSolution:

    def __init__(self, name='', index=None, params=None,fig_data=None):
        """Describes a solution saved from the Solution Browser

        Keyword arguments:
        name -- solution name
        index -- cs solution index
        params -- list of objectives in tuples (name, unit, value)
        """
        self.name = name
        self.index = index
        self.params = params
        self.layout_info={}   # dictionary holding layout_info for a solution with key=size of layout
        self.abstract_info={} # dictionary with solution name as a key and layout_symb_dict as a value


    def form_abs_obj_rect_dict(self, div=1000):
        '''
        From group of CornerStitch Rectangles, form a single rectangle for each trace
        Output type : {"Layout id": {'Sym_info': layout_rect_dict,'Dims': [W,H]} --- Dims is the dimension of the baseplate
        where layout_rect_dict= {'Symbolic ID': [R1,R2 ... Ri]} where Ri is a Rectangle object
        '''
        if isinstance(self.layout_info, dict):
            p_data = self.layout_info['H']
        else:
            #print self.layout_info
            p_data=self.layout_info[0]['H']
        layout_symb_dict={}
        layout_rect_dict = {}


        W, H = p_data.keys()[0]
        W = float(W) / div
        H = float(H) / div
        rect_dict = p_data.values()[0]
        print p_data
        print rect_dict
        for r_id in rect_dict.keys():
            # print 'rect id',r_id
            left = 1e32
            bottom = 1e32
            right = 0
            top = 0
            for rect in rect_dict[r_id]:
                type = rect.type
                min_x = float(rect.left) / div
                max_x = float(rect.right) / div
                min_y = float(rect.bottom) / div
                max_y = float(rect.top) / div
                if min_x <= left:
                    left = float(min_x)
                if min_y <= bottom:
                    bottom = float(min_y)
                if max_x >= right:
                    right = float(max_x)
                if max_y >= top:
                    top = float(max_y)
            layout_rect_dict[r_id] = Rectangle(x=left, y=bottom, width=right - left, height=top - bottom, type=type)
        layout_symb_dict[self.name] = {'rect_info': layout_rect_dict, 'Dims': [W, H]}
        #print layout_symb_dict[layout]
        return layout_symb_dict



    def layout_plot(self, layout_ind=0, db=None, fig_dir=None):
        fig1, ax1 = plt.subplots()

        choice = 'Layout ' + str(layout_ind)

        conn = create_connection(db)
        v1=[]

        with conn:
            # create a new project
            #table = 'Layout_' + str(layout_ind)
            all_data = retrieve_data(conn,layout_ind)
            #all_data=json.loads(all_data)

            #print "A",all_data
            data=str(all_data[0])
            lines=data.split()
            all_lines=[]
            for i in lines:
                if i[-1]!=']':
                    if i[0]=='[':
                        l=[i[1:-1]]

                    else:
                        l.append(i[0:-1])
                else:
                    j=i[0:-1]
                    l.append(j)
                all_lines.append(l)


            colors = ['white', 'green', 'red', 'blue', 'yellow', 'purple','pink','magenta','orange','violet']

            colours=["'white'","'green'","'red'","'blue'","'yellow'","'purple'","'pink'","'magenta'","'orange'","'violet'"]


            for row in all_lines:
                #print"R", row
                if len(row) < 4:
                    k1 = (float(row[0]), float(row[1]))
                else:

                    x = float(row[0])
                    y = float(row[1])
                    w = float(row[2])
                    h = float(row[3])
                    colour = str(row[4])
                    ind=colours.index(colour)
                    colour=colors[ind]
                    order = int(row[5])
                    if row[6] != "'None'":
                        #linestyle = row[6]
                        edgecolor = row[7]
                        ind = colours.index(edgecolor)
                        edgecolor = colors[ind]

                    if row[6] == "'None'":
                        #print "IN"
                        R1 = matplotlib.patches.Rectangle(
                            (x, y),  # (x,y)
                            w,  # width
                            h,  # height
                            facecolor=colour,
                            zorder=order

                        )
                    else:
                        #print x, y, w, h, colour, order, row[6], row[7]
                        #print "here"
                        R1 = matplotlib.patches.Rectangle(
                            (x, y),  # (x,y)
                            w,  # width
                            h,  # height
                            facecolor=colour,
                            linestyle='--',
                            edgecolor=edgecolor,
                            zorder=order

                        )
                    v1.append(R1)

            for p in v1:
                ax1.add_patch(p)
            ax1.set_xlim(0, k1[0])
            ax1.set_ylim(0, k1[1])
            ax1.set_aspect('equal')
            plt.savefig(fig_dir+'/layout_'+str(layout_ind)+'.png')

        conn.close()

