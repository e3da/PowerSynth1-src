import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches

class Rectangle():
    def __init__(self,type=None,x=None,y=None,width=None,height=None,name=None,Super=None,Schar=None,Echar=None,Netid=None):
        '''

        Args:
            type: type of each component: Trace=Type_1, MOS= Type_2, Lead=Type_3, Diode=Type_4
            x: bottom left corner x coordinate of a rectangle
            y: bottom left corner y coordinate of a rectangle
            width: width of a rectangle
            height: height of a rectangle
            Netid: id of net, in which component is connected to
            name: component path_id (from sym_layout object)
            Schar: Starting character of each input line for input processing:'/'
            Echar: Ending character of each input line for input processing: '/'
        '''


        self.type = type
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.Schar = Schar
        self.Echar=Echar
        self.Netid=Netid
        self.name=name
        self.Super=Super


def draw_rect_list(rectlist, ax, color='blue', pattern='//',x_max=None, y_max=None):
    patch = []
    for r in rectlist:
        p = patches.Rectangle((r[0], r[1]), r[2], r[3], fill=True,
                              edgecolor='black', facecolor=color, hatch=pattern,linewidth=3)
        patch.append(p)
        ax.add_patch(p)
    # ax1.autoscale_view(tight=True)
    plt.xlim(0, x_max)
    plt.ylim(0, y_max)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
    

def plot_layout(Layout_Rects,path,name,level):

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
        #fig1, ax1 = plt.subplots()
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
            R=patches.Rectangle(
                    (i[0], i[1]),  # (x,y)
                    i[2],  # width
                    i[3],  # height
                    facecolor=colour,

                )
            ALL_Patches[key].append(R)

            #ax1.add_patch(R)



        #plt.xlim(0, max_x)
        #plt.ylim(0, max_y)

        #fig1.savefig(path+'/'+name+'-layout.png', bbox_inches='tight')
        #plt.close()
        return ALL_Patches


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
                    Total_H[(max_x,max_y)]=Rectangles
        j = 0
        for k,v in Total_H.items():
            #print "TH",k,v

            Rectangles = v
            max_x=k[0]
            max_y=k[1]
            fig1 = matplotlib.pyplot.figure()
            ax1 = fig1.add_subplot(111, aspect='equal')

            colors = ['White', 'green', 'red', 'blue', 'yellow', 'pink']
            type = ['EMPTY', 'Type_1', 'Type_2', 'Type_3', 'Type_4']
            for i in Rectangles:
                for t in type:
                    if i[4] == t:
                        type_ind = type.index(t)
                        colour = colors[type_ind]

                ax1.add_patch(
                    patches.Rectangle(
                        (i[0], i[1]),  # (x,y)
                        i[2],  # width
                        i[3],  # height
                        facecolor=colour,

                    )
                )

            plt.xlim(0, max_x)
            plt.ylim(0, max_y)
            fig1.savefig(path + '/' + name +'-'+str(j)+ '.png', bbox_inches='tight')
            j+=1
            plt.close()



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



def input_conversion(sym_layout):

    x_coordinates =[]                        # stores the x coordinates of all objects for conversion
    y_coordinates =[]                        # stores the y coordinates of all objects for conversion
    for obj in sym_layout.all_lines:

        x_coordinates.append(obj.pt1[0])
        y_coordinates.append(obj.pt1[1])

        x_coordinates.append(obj.pt2[0])
        y_coordinates.append(obj.pt2[1])
    for obj in sym_layout.all_points:
        x_coordinates.append(obj.pt[0])
        y_coordinates.append(obj.pt[1])
    # print set(x_coordinates),set(y_coordinates)
    x_coordinates =list(set(x_coordinates))
    y_coordinates =list(set(y_coordinates))
    Extend =[]
    mx_y =max(y_coordinates)

    converted_x_coordinates =[( i +1 ) *10 for i in x_coordinates] # stores the converted x coordinates of all objects for conversion
    converted_y_coordinates = [( i +1) * 10 for i in y_coordinates] # stores the converted y coordinates of all objects for conversion
    x_max = max(converted_x_coordinates) # stores maximum x value to determine total width of the layout
    y_max = max(converted_y_coordinates) # stores max y value to determine total height of the layout
    # print x_max,y_max, converted_x_coordinates, converted_y_coordinates
    Rectangles =[] # stores rectangle objects with (Type,x,y,width,height)
    Super_Traces =[] # stores super traces
    Super_Traces_dict ={} # stores super traces {(vertical trace y2,y2,x2,x2):horizontal trace}
    Connected ={}

    Points =[]
    for obj in sym_layout.all_lines:
        Points.append(obj.pt1)
        Points.append(obj.pt2)

    Points =list(set(Points))

    for obj1 in sym_layout.all_lines:
        for obj2 in sym_layout.all_lines:
            if obj1!=obj2:
                if obj1.pt1[0] >= obj2.pt1[0] and obj1.pt1[0] <= obj2.pt2[0] and \
                        obj2.pt1[1] >= obj1.pt1[1] and obj2.pt1[1] <= obj1.pt2[1]:
                    pt =intersection_pt(obj1, obj2)
                    if not (frozenset([obj1, obj2]) in Connected.values()):
                        Connected[pt ] =([obj1 ,obj2])



    for obj1 in sym_layout.all_lines:
        for obj2 in sym_layout.all_lines:
            if obj1!=obj2:

                if obj1.pt1[0] > obj2.pt1[0] and obj1.pt1[0] < obj2.pt2[0] and obj2.pt1[1] > obj1.pt1[1] and obj2.pt1[1] < obj1.pt2[1] and obj1.vertical!=obj2.vertical:  # in case of T shape (from the pic you drew above this is a super trace
                    # print obj1.pt1,obj1.pt2,obj2.pt1,obj2.pt2
                    Super_Traces.append(obj1)
                    Super_Traces.append(obj2)
                    # Super_Traces_dict[(obj1.pt2[1],obj1.pt1[1],obj1.pt2[0],obj1.pt1[0])]=obj2
                    Super_Traces_dict[obj1] = obj2
            else:
                continue

                # sym_layout.all_lines.remove(obj1)

    # print Connected
    Intersections ={}
    for k, v in Connected.items():

        lines =list(set(v))
        if len(lines ) >1:
            Intersections[k ] =lines

    CONNECTED =[item for sublist in Intersections.values() for item in sublist ]
    ext =0
    for line in sym_layout.all_lines:
        if line.vertical == False and line.pt1[1] == mx_y :
            ext =1
    for obj in sym_layout.all_lines:
        if obj not in Super_Traces:
            y_ind2 = y_coordinates.index(obj.pt2[1])
            if obj.vertical == True and y_ind2 == mx_y and obj not in CONNECTED :
                if ext==1:
                    Extend.append(obj)

    for obj in sym_layout.all_lines:
        if obj not in Super_Traces:

            if obj.vertical == True:
                x_ind = x_coordinates.index(obj.pt1[0])
                y_ind = y_coordinates.index(obj.pt1[1])
                # x_ind2=x_coordinates.index(obj.pt2[0])
                y_ind2 = y_coordinates.index(obj.pt2[1])

                x = converted_x_coordinates[x_ind]
                y = converted_y_coordinates[y_ind]
                if obj in Extend:
                    height = converted_y_coordinates[y_ind2] - y + 8

                else:
                    height = converted_y_coordinates[y_ind2] - y

                width = 8


            else:
                x_ind = x_coordinates.index(obj.pt1[0])
                y_ind = y_coordinates.index(obj.pt1[1])
                x_ind2 = x_coordinates.index(obj.pt2[0])
                # print x_ind2
                # y_ind2 = y_coordinates.index(obj.pt2[1])
                x = converted_x_coordinates[x_ind]
                y = converted_y_coordinates[y_ind]
                width = converted_x_coordinates[x_ind2] - x + 8
                height = 8

            R = Rectangle('Type_1', x, y, width, height, name=obj.path_id)
            Rectangles.append(R)
        else:
            if obj.vertical == True:

                for k, v in Super_Traces_dict.items():

                    if k == obj:
                        if k.pt1[1] < k.pt2[1]:
                            y_ind = y_coordinates.index(obj.pt1[1])
                            y_ind2 = y_coordinates.index(obj.pt2[1])
                        else:
                            y_ind = y_coordinates.index(obj.pt2[1])
                            y_ind2 = y_coordinates.index(obj.pt1[1])
                        if v.pt1[0] < v.pt2[0]:
                            x_ind = x_coordinates.index(v.pt1[0])
                            x_ind2 = x_coordinates.index(v.pt2[0])
                        else:
                            x_ind = x_coordinates.index(obj.pt2[0])
                            x_ind2 = x_coordinates.index(v.pt1[0])
                        x = converted_x_coordinates[x_ind]
                        y = converted_y_coordinates[y_ind]
                        width = converted_x_coordinates[x_ind2] - x + 8
                        y2 = converted_y_coordinates[y_ind2]
                        height = y2 - y

                R = Rectangle('Type_1', x, y, width, height, name=obj.path_id) # super trace is now a single rectangle with name="vertical trace name+horizontal trace name':if 'Ta' and 'Tb' are supertrace where Ta is vertical new name of converted rectangle is 'TaTb'
                Rectangles.append(R)

            else:
                continue
    Rectangles.sort(key=lambda x: x.Netid, reverse=False)
    #print "LEN",len(Rectangles)

    for rect1 in Rectangles:
        for rect2 in Rectangles:
            for element in Intersections.values() :
                #print"EL",element[0].path_id,element[1].path_id
                if element[0].vertical == True:
                    if rect1.name == element[0].path_id and rect2.name == element[1].path_id:

                        if rect1.x >= rect2.x and rect1.x + rect1.width <= rect2.x + rect2.width and rect1.y == rect2.y:
                            rect1.y += rect2.height
                            rect1.height -= rect2.height

                        elif rect2.y >= rect1.y and rect2.y + rect2.height <= rect1.y + rect1.height and rect1.x == rect2.x:
                            rect2.width -= rect1.width
                            rect2.x += rect1.width

                        elif rect2.y >= rect1.y and rect2.y + rect2.height <= rect1.y + rect1.height and rect1.x + rect1.width == rect2.x + rect2.width:

                            rect2.width -= rect1.width

                elif element[1].vertical == True:
                    if rect1.name == element[1].path_id and rect2.name == element[0].path_id:
                        if rect1.x >= rect2.x and rect1.x + rect1.width <= rect2.x + rect2.width and rect1.y == rect2.y:
                            rect1.y += rect2.height
                            rect1.height -= rect2.height
                        elif rect2.y >= rect1.y and rect2.y + rect2.height <= rect1.y + rect1.height and rect1.x == rect2.x:
                            rect2.width -= rect1.width
                            rect2.x += rect1.width
                        elif rect2.y >= rect1.y and rect2.y + rect2.height <= rect1.y + rect1.height and rect1.x + rect1.width == rect2.x + rect2.width:

                            rect2.width -= rect1.width



    Input_rects = []
    for rect in Rectangles:
        rect.Schar = '/'
        rect.Echar = '/'
        Input_rects.append(rect)
    for rect in Rectangles:
        for k,v in Super_Traces_dict.items():
            #print"K", k.path_id,rect.name
            if k.path_id==rect.name:

                rect1=Rectangle('Type_1', rect.x, rect.y, rect.width, rect.height, name=v.path_id)

                rect1.Schar = '/'
                rect1.Echar = '/'
                Input_rects.append(rect1)

    for obj in sym_layout.all_points:
        if obj.path_id[0] == 'M':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind] + 2
            y = converted_y_coordinates[y_ind] + 2
            width = 4
            height = 4
            type = 'Type_2'
            name = obj.path_id
        elif obj.path_id[0] == 'L':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind] + 1
            y = converted_y_coordinates[y_ind] + 2
            width = 6
            height = 4
            type = 'Type_3'
            name = obj.path_id
        elif obj.path_id[0] == 'D':
            x_ind = x_coordinates.index(obj.pt[0])
            y_ind = y_coordinates.index(obj.pt[1])
            x = converted_x_coordinates[x_ind] + 2
            y = converted_y_coordinates[y_ind] + 2
            width = 3
            height = 3
            type = 'Type_4'
            name = obj.path_id

        Input_rects.append(Rectangle(type, x, y, width, height, name, Schar='/', Echar='/'))

    return Input_rects,x_max,y_max


