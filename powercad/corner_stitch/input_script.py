# intermediate input conversion file. Author @ Imam Al Razi (5-29-2019)


from PySide.QtGui import QFileDialog,QMainWindow

import re
from powercad.cons_aware_en.cons_engine import *
import pandas as pd
import constraint
from CornerStitch import *
from PySide import QtCore, QtGui
import sys
#from powercad.project_builder.proj_dialogs import ConsDialog
from powercad.design.parts import *
from powercad.design.Routing_paths import *
from powercad.cons_aware_en.cons_engine import New_layout_engine
import getpass
from powercad.design.group import Island

'''
class ConstraintWindow(QtGui.QMainWindow):
    # A fake window to call the constraint dialog object
    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)
        self.cons_df = None

'''




class ScriptInputMethod():
    def __init__(self,input_script=None):
        if input_script!=None:
            self.input_script=input_script


    def bond_wire_table(self,bondwire_info=None):
        input_file = bondwire_info
        with open(input_file, 'rb') as fp:
            lines = fp.readlines()
            Definition=[]
            table_info=[]
            for i in range(1, len(lines)):
                line = lines[i]
                if len(line) != 2:
                    L = line.strip('\r\n')
                    d_out = re.sub("\t", ". ", L)
                    d_out = re.sub("\s", ",", d_out)
                    line = d_out.rstrip(',')
                    line = line.split(',')
                    Definition.append(line)
                else:
                    part2 = i
                    break

            for i in range(part2 + 2, len(lines)):
                line = lines[i]
                L = line.strip('\r\n')
                d_out = re.sub("\t", ". ", L)
                d_out = re.sub("\s", ",", d_out)
                line = d_out.rstrip(',')
                line = line.split(',')
                table_info.append(line)


        bond_wire_objects=[]

        for i in range(len(Definition)):
            name=Definition[i][0]
            wire=BondingWires(name=name)
            wire.info_file=Definition[i][1]
            wire.load_wire()
            bond_wire_objects.append(wire)

        wires={}
        for i in range(len(table_info)):
            name=table_info[i][0]
            for j in bond_wire_objects:

                if j.name==table_info[i][1]:
                    wires[name]={'BW_object':j,'Source':table_info[i][2],'Destination':table_info[i][3],'num_wires':table_info[i][4],'spacing':table_info[i][5]}


        #for i in bond_wire_objects:
            #print i.printWire()

        #print wires

        #raw_input()
        return wires





    def read_input_script(self):

        input_file=self.input_script
        with open(input_file,'rb') as fp:
            lines = fp.readlines()
        self.Definition=[]  # saves lines corresponding to definition in the input script
        self.layout_info=[] # saves lines corresponding to layout_info in the input script
        for i in range(1,len(lines)):
            line=lines[i]
            if len(line)!=2:
                L = line.strip('\r\n')
                d_out = re.sub("\t", ". ", L)
                d_out = re.sub("\s", ",", d_out)
                line = d_out.rstrip(',')
                line = line.split(',')
                self.Definition.append(line)
            else:
                part2=i
                break

        Input=[]
        for i in range(part2+2,len(lines)):
            line=lines[i]
            L = line.strip('\r\n')
            d_out = re.sub("\t", ". ", L)
            d_out = re.sub("\s", ",", d_out)
            line = d_out.rstrip(',')
            line = line.split(',')
            #self.layout_info.append(line)
            Input.append(line)

        self.layout_info.append(Input[0])
        Modified_input = []
        bondwires = []
        for i in range(1,len(Input)):
            inp = Input[i]
            if inp[0][0] == 'C':
                bondwires.append(inp)
            else:
                if i < len(Input) - 1:
                    inp2 = Input[i + 1]

                    for c in inp2:
                        if c == '+' or c == '-':
                            inp.append(c)
                else:
                    inp.append('+')
                self.layout_info.append(inp)

        for i in self.layout_info:
            print len(i),i




        return self.Definition,self.layout_info


    def gather_part_route_info(self):


        layout_info=self.layout_info
        self.all_parts_info = {}  # saves a list of parts corresponding to name of each part as its key
        self.info_files = {}  # saves each part technology info file name
        for i in self.Definition:
            key = i[0]
            self.all_parts_info.setdefault(key, [])
            self.info_files[key] = i[1]

        # updates type list according to definition input

        for i in self.Definition:

            if i[0] not in constraint.constraint.all_component_types:
                c=constraint.constraint()
                constraint.constraint.add_component_type(c,i[0])
        self.all_components_list =  constraint.constraint.all_component_types  # set of all components considered so far


        self.all_route_info = {}
        for j in range(1, len(layout_info)):
            for k in range(len(layout_info[j])):
                if layout_info[j][k][0] == 'T':
                    key = 'trace'
                    self.all_route_info.setdefault(key, [])
                elif layout_info[j][k][0] == 'B':
                    key = 'bonding wire pad'
                    self.all_route_info.setdefault(key, [])
                elif layout_info[j][k][0] == 'V':
                    key = 'via'
                    self.all_route_info.setdefault(key, [])


        for j in range (1,len(layout_info)):

            #updates routing path components

            for k in range(len(layout_info[j])):
                if layout_info[j][k][0]=='T' and layout_info[j][k+1]=='power':
                    element = RoutingPath(name='trace', type=0, layout_component_id=layout_info[j][k])
                    self.all_route_info['trace'].append(element)
                elif layout_info[j][k][0]=='T' and layout_info[j][k+1]=='signal':
                    element = RoutingPath(name='trace', type=1, layout_component_id=layout_info[j][k])
                    self.all_route_info['trace'].append(element)
                elif layout_info[j][k][0]=='B' and layout_info[j][k+1]=='signal':
                    element = RoutingPath(name='bonding wire pad', type=1, layout_component_id=layout_info[j][k])
                    self.all_route_info['bonding wire pad'].append(element)
                elif layout_info[j][k][0]=='B' and layout_info[j][k+1]=='power':
                    element = RoutingPath(name='bonding wire pad', type=0, layout_component_id=layout_info[j][k])
                    self.all_route_info['bonding wire pad'].append(element)

                #parts info gathering
                elif layout_info[j][k][0] == 'D' and layout_info[j][k+1] in self.all_components_list:
                    rotate=False
                    angle=None
                    for m in range(len(layout_info[j])):
                        if layout_info[j][m][0]=='R':
                            rotate=True

                            angle=layout_info[j][m].strip('R')
                            break
                    if rotate==False:
                        element = Part(name=layout_info[j][k+1], info_file=self.info_files[layout_info[j][k+1]],layout_component_id=layout_info[j][k])
                        element.load_part()
                        self.all_parts_info[layout_info[j][k+1]].append(element)

                    else:
                        element = Part(info_file=self.info_files[layout_info[j][k + 1]],layout_component_id=layout_info[j][k])
                        element.load_part()
                        # print element.footprint
                        if angle == '90':
                            name = layout_info[j][k + 1] + '_' + '90'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 1
                            element.rotate_90()
                        elif angle == '180':
                            name = layout_info[j][k + 1] + '_' + '180'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 2
                            element.rotate_180()
                        elif angle == '270':
                            name = layout_info[j][k + 1] + '_' + '270'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 3
                            element.rotate_270()
                        # print element.footprint
                        self.all_parts_info[layout_info[j][k + 1]].append(element)

                elif layout_info[j][k][0] == 'L' and (layout_info[j][k+1] == 'power_lead' or layout_info[j][k+1]=='signal_lead') and layout_info[j][k+1] in self.all_components_list:
                    rotate = False
                    angle = None
                    for m in range(len(layout_info[j])):
                        if layout_info[j][m][0] == 'R':
                            rotate = True
                            angle = layout_info[j][m].strip('R')
                            break

                    if rotate==False:
                        element = Part(name=layout_info[j][k + 1], info_file=self.info_files[layout_info[j][k + 1]],layout_component_id=layout_info[j][k])
                        element.load_part()
                        self.all_parts_info[layout_info[j][k + 1]].append(element)

                    else:
                        element = Part(info_file=self.info_files[layout_info[j][k + 1]],layout_component_id=layout_info[j][k])
                        element.load_part()
                        # print element.footprint
                        if angle == '90':
                            name = layout_info[j][k + 1] + '_' + '90'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 1
                            element.rotate_90()
                        elif angle == '180':
                            name = layout_info[j][k + 1] + '_' + '180'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 2
                            element.rotate_180()
                        elif angle == '270':
                            name = layout_info[j][k + 1] + '_' + '270'
                            #name = layout_info[j][k + 1]
                            element.name = name
                            element.rotate_angle = 3
                            element.rotate_270()
                        # print element.footprint
                        self.all_parts_info[layout_info[j][k + 1]].append(element)




            '''
            #Nonhierarchical input       
            if layout_info[j][1][0]=='T' and layout_info[j][2]=='power':
                element=RoutingPath(name='trace',type=0,layout_component_id=layout_info[j][1])
                self.all_route_info['trace'].append(element)
            elif layout_info[j][1][0]=='T' and layout_info[j][2]=='signal':
                element = RoutingPath(name='trace', type=1, layout_component_id=layout_info[j][1])
                self.all_route_info['trace'].append(element)
            elif layout_info[j][1][0]=='B' and layout_info[j][2]=='signal':
                element = RoutingPath(name='bonding wire pad', type=1, layout_component_id=layout_info[j][1])
                self.all_route_info['bonding wire pad'].append(element)
            elif layout_info[j][1][0]=='B' and layout_info[j][2]=='power':
                element = RoutingPath(name='bonding wire pad', type=0, layout_component_id=layout_info[j][1])
                self.all_route_info['bonding wire pad'].append(element)

            elif layout_info[j][1][0] == 'D' and layout_info[j][2] in self.all_components_list and len(layout_info[j])<6:
                element = Part(name= layout_info[j][2],info_file=self.info_files[layout_info[j][2]], layout_component_id=layout_info[j][1])
                element.load_part()
                self.all_parts_info[layout_info[j][2]].append(element)
            elif layout_info[j][1][0] == 'L' and layout_info[j][2] == 'power_lead' and layout_info[j][2] in self.all_components_list and len(layout_info[j])<6:
                element = Part(name=layout_info[j][2], info_file=self.info_files[layout_info[j][2]], layout_component_id=layout_info[j][1])
                element.load_part()
                self.all_parts_info[layout_info[j][2]].append(element)
            elif layout_info[j][1][0] == 'L' and layout_info[j][2] == 'signal_lead' and layout_info[j][2] in self.all_components_list and len(layout_info[j])<6:
                element = Part(name=layout_info[j][2], info_file=self.info_files[layout_info[j][2]], layout_component_id=layout_info[j][1])
                element.load_part()
                self.all_parts_info[layout_info[j][2]].append(element)
            elif layout_info[j][1][0] == 'D' and layout_info[j][2] in self.all_components_list and len(layout_info[j])==6 and layout_info[j][5][0]=='R':
                element = Part(info_file=self.info_files[layout_info[j][2]],layout_component_id=layout_info[j][1])
                element.load_part()
                #print element.footprint
                if layout_info[j][5].strip('R')=='90':
                    name=layout_info[j][2]+'_'+'90'
                    element.name=name
                    element.rotate_angle=1
                    element.rotate_90()
                elif layout_info[j][5].strip('R')=='180':
                    name = layout_info[j][2] + '_' + '180'
                    element.name = name
                    element.rotate_angle = 2
                    element.rotate_180()
                elif layout_info[j][5].strip('R')=='270':
                    name = layout_info[j][2] + '_' + '270'
                    element.name = name
                    element.rotate_angle = 3
                    element.rotate_270()
                #print element.footprint
                self.all_parts_info[layout_info[j][2]].append(element)
            elif layout_info[j][1][0] == 'L' and layout_info[j][2] == 'power_lead' and layout_info[j][2] in self.all_components_list and len(layout_info[j])==6 and layout_info[j][5][0]=='R':
                element = Part( info_file=self.info_files[layout_info[j][2]], layout_component_id=layout_info[j][1])
                element.load_part()

                if layout_info[j][5].strip('R')=='90':
                    name = layout_info[j][2] + '_' + '90'
                    element.name = name
                    element.rotate_angle=1
                    element.rotate_90()
                elif layout_info[j][5].strip('R')=='180':
                    name = layout_info[j][2] + '_' + '180'
                    element.name = name
                    element.rotate_angle = 2
                    element.rotate_180()
                elif layout_info[j][5].strip('R')=='270':
                    name = layout_info[j][2] + '_' + '270'
                    element.name = name
                    element.rotate_angle = 3
                    element.rotate_270()
                self.all_parts_info[layout_info[j][2]].append(element)
            elif layout_info[j][1][0] == 'L' and layout_info[j][2] == 'signal_lead' and layout_info[j][2] in self.all_components_list and len(layout_info[j])==6 and layout_info[j][5][0]=='R':
                element = Part( info_file=self.info_files[layout_info[j][2]], layout_component_id=layout_info[j][1])
                element.load_part()
                if layout_info[j][5].strip('R')=='90':
                    name = layout_info[j][2] + '_' + '90'
                    element.name = name
                    element.rotate_angle=1
                    element.rotate_90()
                elif layout_info[j][5].strip('R')=='180':
                    name = layout_info[j][2] + '_' + '180'
                    element.name = name
                    element.rotate_angle = 2
                    element.rotate_180()
                elif layout_info[j][5].strip('R')=='270':
                    name = layout_info[j][2] + '_' + '270'
                    element.name = name
                    element.rotate_angle = 3
                    element.rotate_270()
                self.all_parts_info[layout_info[j][2]].append(element)

            else:
                name=layout_info[j][1][0]+'_'+layout_info[j][2]
                c=constraint.constraint()
                constraint.constraint.add_component_type(c,name)
                element=  RoutingPath(name=name, type=1, layout_component_id=layout_info[j][1])
                key=name
                self.all_route_info.setdefault(key,[])
                self.all_route_info[key].append(element)

            '''



            #print layout_info[j][1][0],layout_info[j][2]

        #print "T",constraint.constraint.component_to_component_type
        #raw_input()
        '''
        for key,comp in self.all_parts_info.items():
            for element in comp:
                if element.rotate_angle in [1,2,3]:
                    c = constraint.constraint()
                    name=element.name
                    constraint.constraint.add_component_type(c, name)
        
        
        '''



        self.all_components_type_mapped_dict = constraint.constraint.component_to_component_type



        #print self.all_parts_info
        #print self.info_files
        #print self.all_route_info
        print "map",self.all_components_type_mapped_dict
        return self.all_parts_info,self.info_files,self.all_route_info,self.all_components_type_mapped_dict

    #def gather_layout_info(layout_info=None, all_parts_info=None, all_route_info=None,all_components_mapped_type_dict=None):
    def gather_layout_info(self):

        layout_info=self.layout_info
        self.size = [float(i) for i in layout_info[0]]  # extracts layout size (1st line of the layout_info)
        self.cs_info = []  # list of rectanges to be used as cornerstitch input information



        self.component_to_cs_type = {}
        # all_components=['EMPTY','power_trace','signal_trace','signal_lead', 'power_lead', 'MOS', 'IGBT', 'Diode','bonding wire pad','via']

        #self.all_components_type_mapped_dict=self.all_components_mapped_type_dict # dict to map component type and cs type
        self.all_components_list= self.all_components_type_mapped_dict.keys()


        #print "comp_list",self.all_components_list #all_components_list=['MOS', 'signal_lead', 'power_lead', 'EMPTY', 'signal_trace', 'power_trace', 'MOS_90']
        #print self.all_components_type_mapped_dict



        all_component_type_names = ["EMPTY"]
        self.all_components = []
        for j in range(1, len(layout_info)):
            for k, v in self.all_parts_info.items():
                for element in v:
                    for m in range(len(layout_info[j])):
                        if element.layout_component_id == layout_info[j][m]:

                            if element not in self.all_components:
                                self.all_components.append(element)
                            if element.name not in all_component_type_names :
                                if element.rotate_angle==0:
                                    all_component_type_names.append(element.name)

        for j in range(1, len(layout_info)):
            for k, v in self.all_route_info.items():
                for element in v:
                    for m in range(len(layout_info[j])):
                        if element.layout_component_id == layout_info[j][m]:
                            if element not in self.all_components:
                                self.all_components.append(element)
                            if element.type == 0 and element.name == 'trace':
                                type_name = 'power_trace'
                            elif element.type == 1 and element.name == 'trace':
                                type_name = 'signal_trace'
                            elif element.name=='bonding wire pad':
                                type_name= 'bonding wire pad'
                            if type_name not in all_component_type_names:
                                all_component_type_names.append(type_name)


        #print all_component_type_names #['EMPTY', 'power_trace', 'signal_trace', 'MOS_90', 'MOS', 'power_lead', 'signal_lead']



        for i in range(len(all_component_type_names)):
            #print all_component_type_names[i]
                self.component_to_cs_type[all_component_type_names[i]] = self.all_components_type_mapped_dict[all_component_type_names[i]]

        print"CS", self.component_to_cs_type #{'MOS': 'Type_5', 'signal_lead': 'Type_4', 'power_lead': 'Type_3', 'EMPTY': 'EMPTY', 'signal_trace': 'Type_2', 'power_trace': 'Type_1', 'MOS_90': 'Type_6'}


        for k, v in self.all_parts_info.items():
            for comp in v:
                if comp.rotate_angle==0:
                    comp.cs_type = self.component_to_cs_type[comp.name]


                #print comp.cs_type


        hier_input_info={}
        for j in range(1, len(layout_info)):
            hier_level = 0
            for m in range(len(layout_info[j])):
                if layout_info[j][m] == '.':
                    hier_level += 1
                    continue
                else:
                    start=m
                    break

            hier_input_info.setdefault(hier_level,[])
            hier_input_info[hier_level].append(layout_info[j][start:])

        print len(hier_input_info[0]),len(hier_input_info[1])
        rects_info=[]
        for k1,layout_data in hier_input_info.items():

            for j in range(len(layout_data)):
                for k, v in self.all_parts_info.items():
                    for element in v:
                        if element.layout_component_id in layout_data[j]:
                            index=layout_data[j].index(element.layout_component_id)
                            type_index=index+1
                            type_name=layout_data[j][type_index]
                            type = self.component_to_cs_type[type_name]
                            x = float(layout_data[j][3])
                            y = float(layout_data[j][4])
                            width = round(element.footprint[0])
                            height = round(element.footprint[1])
                            name = layout_data[j][1]
                            Schar = layout_data[j][0]
                            Echar = layout_data[j][-1]
                            rotate_angle=element.rotate_angle
                            rect_info = [type, x, y, width, height, name, Schar, Echar,k1,rotate_angle] #k1=hierarchy level,# added rotate_angle to reduce type in constraint table
                            rects_info.append(rect_info)

                for k, v in self.all_route_info.items():
                    for element in v:
                        if element.layout_component_id in layout_data[j]:
                            if element.type == 0 and element.name == 'trace':
                                type_name = 'power_trace'
                            elif element.type == 1 and element.name == 'trace':
                                type_name = 'signal_trace'
                            else:
                                type_name=element.name
                            type = self.component_to_cs_type[type_name]
                            x = float(layout_data[j][3])
                            y = float(layout_data[j][4])
                            width = float(layout_data[j][5])
                            height = float(layout_data[j][6])
                            name = layout_data[j][1]
                            Schar = layout_data[j][0]
                            Echar = layout_data[j][-1]
                            rect_info = [type, x, y, width, height, name, Schar, Echar,k1,0] #k1=hierarchy level # 0 is for rotate angle (default=0 as r)
                            rects_info.append(rect_info)
                        else:
                            continue


        self.cs_info=[0 for i in range(len(rects_info))]
        for i in range(len(rects_info)):
            print rects_info[i]
        layout_info=layout_info[1:]
        print "L", len(self.cs_info), len(rects_info),len(layout_info)
        for i in range(len(layout_info)):
            for j in range(len(rects_info)):
                if rects_info[j][5] in layout_info[i]:
                    self.cs_info[i]=rects_info[j]



        print "cs_info",self.cs_info
        #raw_input()



        return self.size,self.cs_info,self.component_to_cs_type,self.all_components

    def update_constraint_table(self):


        #init_constraint=constraint.constraint()
        #init_constraint.update_constraints(all_components=all_components, component_to_cs_type=component_to_cs_type)

        #Types=init_constraint.Type

        Types_init=self.component_to_cs_type.values()
        #print Types_init
        Types = [0 for i in range(len(Types_init))]
        for i in Types_init:
            if i=='EMPTY':
                Types[0]=i
            else:
                t=i.strip('Type_')
                ind=int(t)
                Types[ind]=i


        #print Types

        all_rows = []
        r1 = ['Min Dimensions']
        r1_c=[]
        for i in range(len(Types)):
            for k,v in self.component_to_cs_type.items():
                if v==Types[i]:
                    r1_c.append(k)
        r1+=r1_c
        all_rows.append(r1)
        #print r1

        r2 = ['Min Width']
        r2_c=[0 for i in range(len(Types))]
        for i in range(len(Types)):
            if Types[i]=='EMPTY':
                r2_c[i]=1.0
            else:
                for k,v in self.component_to_cs_type.items():

                    if v==Types[i]:
                        for comp in self.all_components:
                            if k==comp.name and isinstance(comp,Part):
                                #print "H",k,v,comp.footprint
                                if r2_c[i]==0:
                                    r2_c[i]=comp.footprint[0]
                                    break
        for i in range(len(r2_c)):
            if r2_c[i]==0:
                r2_c[i]=2.0




        r2+=r2_c
        all_rows.append(r2)

        #print r2


        r3 = ['Min Height']
        r3_c = [0 for i in range(len(Types))]
        for i in range(len(Types)):
            if Types[i]=='EMPTY':
                r3_c[i]=1.0
            else:
                for k, v in self.component_to_cs_type.items():
                    if v == Types[i]:
                        for comp in self.all_components:
                            if k == comp.name and isinstance(comp,Part):
                                if r3_c[i] == 0:
                                    r3_c[i] = comp.footprint[1]
                                    break
        for i in range(len(r3_c)):
            if r3_c[i]==0:
                r3_c[i]=2.0

        r3 += r3_c
        all_rows.append(r3)
        #print r3

        r4 = ['Min Extension']
        r4_c = [0 for i in range(len(Types))]
        for i in range(len(Types)):
            if Types[i]=='EMPTY':
                r4_c[i]=1.0
            else:
                for k, v in self.component_to_cs_type.items():
                    if v == Types[i]:
                        for comp in self.all_components:
                            if k == comp.name and isinstance(comp,Part):
                                if r4_c[i] == 0:
                                    val = max(comp.footprint)
                                    r4_c[i] = val
                                    break
        for i in range(len(r4_c)):
            if r4_c[i]==0:
                r4_c[i]=2.0


        r4 += r4_c
        all_rows.append(r4)
        #print r4

        r5 = ['Min Spacing']
        r5_c = []
        for i in range(len(Types)):
            for k, v in self.component_to_cs_type.items():
                if v == Types[i]:
                    r5_c.append(k)
        r5 += r5_c
        all_rows.append(r5)
        #print r5

        space_rows=[]
        #print Types
        for i in range(len(Types)):
            for k,v in self.component_to_cs_type.items():

                if v==Types[i]:

                    row=[k]
                    for j in range(len(Types)):
                        row.append(2.0)
                    space_rows.append(row)
                    all_rows.append(row)
        #print space_rows

        r6 = ['Min Enclosure']
        r6_c = []
        for i in range(len(Types)):
            for k, v in self.component_to_cs_type.items():
                if v == Types[i]:
                    r6_c.append(k)
        r6 += r6_c
        all_rows.append(r6)
        #print r6
        enclosure_rows=[]
        for i in range(len(Types)):
            for k,v in self.component_to_cs_type.items():
                if v==Types[i]:
                    row=[k]

                    for j in range(len(Types)):
                        row.append(1.0)
                    enclosure_rows.append(row)
                    all_rows.append(row)
        #print enclosure_rows
        df = pd.DataFrame(all_rows)


        self.Types=Types
        self.df=df
        return self.df,self.Types

    def convert_rectangle(self):

        input_rects = []
        for rect in self.cs_info:
            type = rect[0]
            x = rect[1]
            y = rect[2]
            width = rect[3]
            height = rect[4]
            name = rect[5]
            Schar = rect[6]
            Echar = rect[7]
            hier_level=rect[8]
            input_rects.append(Rectangle(type, x, y, width, height, name, Schar=Schar, Echar=Echar,hier_level=hier_level,rotate_angle=rect[9]))

        return input_rects

    def form_island(self):
        '''

        :return: connected groups according to the input
        '''
        islands=[]
        for i in range(len(self.cs_info)):
            rect=self.cs_info[i]
            if rect[5][0]=='T' and rect[6]=='+' and rect[7]=='+':
                island=Island()
                rectangle = Rectangle(x=rect[1], y=rect[2], width=rect[3], height=rect[4],name=rect[5])
                island.rectangles.append(rectangle)
                island.elements.append(rect)
                name='island_'
                island.name=name+rect[5].strip('T')
                island.element_names.append(rect[5])
                islands.append(island)
            elif rect[5][0]=='T' and rect[6]=='+' and rect[7]=='-':
                island = Island()
                rectangle = Rectangle(x=rect[1], y=rect[2], width=rect[3], height=rect[4], name=rect[5])
                island.rectangles.append(rectangle)
                island.elements.append(rect)
                name = 'island_'
                island.name = name + rect[5].strip('T')
                island.element_names.append(rect[5])
                islands.append(island)
            elif rect[5][0]=='T' and rect[6]=='-' and (rect[7]=='-' or rect[7]=='+'):
                island=islands[-1]
                rectangle = Rectangle(x=rect[1], y=rect[2], width=rect[3], height=rect[4], name=rect[5])
                island.rectangles.append(rectangle)
                island.elements.append(rect)
                island.name = island.name +('_')+ rect[5].strip('T')
                island.element_names.append(rect[5])

        # sorting connected traces on an island
        for island in islands:
            if len(island.elements)>1:
                netid = 0
                all_rects=island.rectangles
                for i in range(len(all_rects)):
                    all_rects[i].Netid=netid
                    netid+=1
                rectangles = [all_rects[0]]
                #all_rects.remove(all_rects[0])


                for rect1 in rectangles:
                    for rect2 in all_rects:
                        if (rect1.right==rect2.left or rect1.bottom==rect2.top or rect1.left==rect2.right or rect1.bottom==rect2.top) and rect2.Netid!=rect1.Netid:
                            if rect2.Netid>rect1.Netid:
                                rectangles.append(rect2)
                                rect2.Netid=rect1.Netid
                            #all_rects.remove(rect2)
                        else:
                            continue
                if len(rectangles) != len(island.elements):
                    print "Check input script !! : Group of traces are not defined in proper way."

                elements = island.elements
                ordered_rectangle_names = [rect.name for rect in rectangles]
                ordered_elements = []
                for name in ordered_rectangle_names:
                    for element in elements:
                        if name == element[5]:
                            if element[5]==ordered_rectangle_names[0]:
                                element[-4]='+'
                                element[-3]='-'
                            elif element[5]!=ordered_rectangle_names[-1]:
                                element[-4]='-'
                                element[-3]='-'
                            elif element[5]==ordered_rectangle_names[-1]:
                                element[-4] = '-'
                                element[-3] = '+'
                            ordered_elements.append(element)
                island.elements = ordered_elements
                island.element_names = ordered_rectangle_names



        return islands

    def populate_child(self,islands=None):
        '''

        :param islands: list of islands
        :return: populate each islands child list
        '''
        all_layout_component_ids=[]
        for island in islands:
            all_layout_component_ids+=island.element_names

        for island in islands:
            layout_component_ids=island.element_names


            end=10000
            for i in range(len(self.cs_info)):
                rect = self.cs_info[i]
                if rect[5] in layout_component_ids:
                    start=i
                elif rect[5] in all_layout_component_ids and i>start:
                    end=i
                    break

            for i in range(len(self.cs_info)):
                rect = self.cs_info[i]
                if rect[5] in layout_component_ids and rect[5] in all_layout_component_ids:
                    continue
                elif rect[5] not in all_layout_component_ids and i>start and i<end:
                    island.child.append(rect)
                    island.child_names.append(rect[5])


        return islands




    def update_cs_info(self,islands=None):

        for island in islands:
            if len(island.element_names)>2:
                for i in range(len(self.cs_info)):
                    if self.cs_info[i][5] == island.element_names[0]:
                        start=i
                        end=len(island.element_names)
                        break
                print start, end

                self.cs_info[start:start+end]=island.elements







        #raw_input()





def save_constraint_table(cons_df=None,file=None):
    if file!=None:
        cons_df.to_csv(file, sep=',', header=None, index=None)

'''
def show_constraint_table(parent,cons_df=None):


    dialog = ConsDialog(parent=parent, cons_df=cons_df)
    dialog.show()
    dialog.exec_()
    return parent.cons_df

'''

    #print "parent consdf",main_window.cons_df




def plot_layout(fig=None,size=None):
    if isinstance(fig,list):
        rects=fig
        colors = ['green', 'red', 'blue', 'yellow', 'purple', 'pink', 'magenta', 'orange', 'violet']
        type = ['Type_1', 'Type_2', 'Type_3', 'Type_4', 'Type_5', 'Type_6', 'Type_7', 'Type_8', 'Type_9']
        # zorders = [1,2,3,4,5]
        Patches = {}

        for r in rects:
            i = type.index(r[0])
            # print i,r.name
            P = matplotlib.patches.Rectangle(
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
        fig=Patches

    fig2, ax2 = plt.subplots()


    Names = fig.keys()
    Names.sort()
    for k, p in fig.items():

        if k[0] == 'T':
            x = p.get_x()
            y = p.get_y()
            ax2.text(x + 0.1, y + 0.1, k)
            ax2.add_patch(p)

    for k, p in fig.items():

        if k[0] != 'T':
            x = p.get_x()
            y = p.get_y()
            ax2.text(x + 0.1, y + 0.1, k, weight='bold')
            ax2.add_patch(p)
    ax2.set_xlim(0, size[0])
    ax2.set_ylim(0, size[1])
    ax2.set_aspect('equal')

    user_name = getpass.getuser()
    if user_name == 'qmle':
        fig_dir = "C:\Users\qmle\Desktop\New_Layout_Engine\New_design_flow\\"
    elif user_name=='ialrazi':
        fig_dir = 'C:/Users/ialrazi/Desktop/REU_Data_collection_input/Figs/'
    plt.savefig( fig_dir+ '_init_layout' + '.png')



def mode_zero(cons_df,Htree,Vtree): # evaluates mode 0(minimum sized layouts)

    CG1 = CS_to_CG(0)
    CG1.getConstraints(cons_df)
    #ledge_width=float(cons_df.iat[10,2])
    #ledge_height=float(cons_df.iat[10,2])

    #self.cons_df.to_csv('out_2.csv', sep=',', header=None, index=None)
    Evaluated_X, Evaluated_Y = CG1.evaluation(Htree=Htree, Vtree=Vtree, N=None, W=None, H=None, XLoc=None, YLoc=None,seed=None,individual=None)

    #print "X",Evaluated_X
    #print "Y",Evaluated_Y
    return Evaluated_X, Evaluated_Y

def plot_solution(Patches=None):
    user_name = getpass.getuser()
    if user_name == 'qmle':
        fig_dir = "C:\Users\qmle\Desktop\New_Layout_Engine\New_design_flow\\"
    elif user_name == 'ialrazi':
        fig_dir = 'C:/Users/ialrazi/Desktop/REU_Data_collection_input/Figs/'
    for i in range(len(Patches)):
        fig, ax1 = plt.subplots()
        for k, v in Patches[i].items():
            for p in v:
                #print"c", p.get_x(),p.get_y()
                ax1.add_patch(p)
            ax1.set_xlim(0, k[0])
            ax1.set_ylim(0, k[1])

        ax1.set_aspect('equal')
        plt.savefig(fig_dir+str(i)+'.png')



if __name__ == '__main__':

    component_list,layout_info=test_file()

    print len(component_list),component_list
    print len(layout_info),layout_info








