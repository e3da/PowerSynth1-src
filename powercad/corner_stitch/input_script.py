# intermediate input conversion file. Author @ Imam Al Razi (5-29-2019)

import re
import pandas



class Part():
    def __init__(self,name=None,type=None,info_file=None,layout_component_id=None):
        """

        :param name: part name : signal_lead, power_lead, MOS, IGBT, Diode
        :param type: lead:0,device:1
        :param info_file: technology file for each part
        :param layout_component_id: 1,2,3.... id in the layout information

        """

        self.name=name
        self.type=type
        self.info_file=info_file
        self.layout_component_id=layout_component_id
        self.footprint=[4,4]

    def printPart(self):
        print "Name: ", self.name
        print "Information location: ", self.info_file
        print "ID in layout: ", self.layout_component_id







class RoutingPath():
    def __init__(self,name=None,type=None,layout_component_id=None):
        '''

        :param name: routing path name: trace,bonding wire pads,vias etc.
        :param type: power:0, signal:1
        :param layout_component_id: 1,2,3.... id in the layout information
        '''
        self.name = name
        self.type = type
        self.layout_component_id = layout_component_id

    def printRoutingPath(self):

        print "Name: ", self.name
        if self.type==0:
            print "Type:  power trace"
        else:
            print "Type:  signal trace"
        print "ID in layout: ", self.layout_component_id


class UpdateConstraintTable():
    def __init__(self,component_list=[]):
        self.component_list=component_list





if __name__ == '__main__':

    input_file="C:\Users\ialrazi\Desktop\REU_Data_collection_input\h-bridge.txt"  # input script location
    with open(input_file,'rb') as fp:
        lines = fp.readlines()
    Definition=[]  # saves lines corresponding to definition in the input script
    layout_info=[] # saves lines corresponding to layout_info in the input script
    for i in range(1,len(lines)):
        line=lines[i]
        if len(line)!=2:
            L = line.strip('\r\n')
            d_out = re.sub("\t", ". ", L)
            d_out = re.sub("\s", ",", d_out)
            line = d_out.rstrip(',')
            line = line.split(',')
            Definition.append(line)
        else:
            part2=i
            break

    for i in range(part2+2,len(lines)):
        line=lines[i]
        L = line.strip('\r\n')
        d_out = re.sub("\t", ". ", L)
        d_out = re.sub("\s", ",", d_out)
        line = d_out.rstrip(',')
        line = line.split(',')
        layout_info.append(line)
    #print part2, Definition
    print layout_info
    all_parts=['signal_lead', 'power_lead', 'MOS', 'IGBT', 'Diode'] # list of all parts considered so far
    all_parts_info={} # saves a list of parts corresponding to name of each part as its key
    info_files={} # saves each part technology info file name
    for i in Definition:
        if i[0] in all_parts:
            key=i[0]
            all_parts_info.setdefault(key,[])
            info_files[key]=i[1]

    all_routes=['trace','bonding wire pad','via']
    all_route_info={}
    for j in range (1,len(layout_info)):
        if layout_info[j][1][0]=='T':
            key='trace'
            all_route_info.setdefault(key,[])
        elif layout_info[j][1][0]=='B':
            key='bonding wire pad'
            all_route_info.setdefault(key, [])
        elif layout_info[j][1][0]=='V':
            key = 'via'
            all_route_info.setdefault(key, [])

    size=[float(i) for i in layout_info[0]] # extracts layout size (1st line of the layout_info)

    for j in range (1,len(layout_info)):
        if layout_info[j][1][0]=='T' and layout_info[j][2]=='power':
            element=RoutingPath(name='trace',type=0,layout_component_id=layout_info[j][1])
            all_route_info['trace'].append(element)
        elif layout_info[j][1][0]=='T' and layout_info[j][2]=='signal':
            element = RoutingPath(name='trace', type=1, layout_component_id=layout_info[j][1])
            all_route_info['trace'].append(element)
        elif layout_info[j][1][0]=='B' and layout_info[j][2]=='signal':
            element = RoutingPath(name='bonding wire pad', type=1, layout_component_id=layout_info[j][1])
            all_route_info['trace'].append(element)
        elif layout_info[j][1][0]=='B' and layout_info[j][2]=='power':
            element = RoutingPath(name='bonding wire pad', type=0, layout_component_id=layout_info[j][1])
            all_route_info['trace'].append(element)
        elif layout_info[j][1][0]=='D'and layout_info[j][2]=='MOS':
            element= Part(name='MOS',type=1,info_file=info_files['MOS'],layout_component_id=layout_info[j][1])
            all_parts_info['MOS'].append(element)
        elif layout_info[j][1][0]=='D'and layout_info[j][2]=='DIODE':
            element= Part(name='DIODE',type=1,info_file=info_files['DIODE'],layout_component_id=layout_info[j][1])
            all_parts_info['DIODE'].append(element)
        elif layout_info[j][1][0]=='D'and layout_info[j][2]=='IGBT':
            element= Part(name='IGBT',type=1,info_file=info_files['IGBT'],layout_component_id=layout_info[j][1])
            all_parts_info['IGBT'].append(element)
        elif layout_info[j][1][0]=='L'and layout_info[j][2]=='power_lead':
            element = Part(name='power_lead', type=0, info_file=info_files['power_lead'], layout_component_id=layout_info[j][1])
            all_parts_info['power_lead'].append(element)
        elif layout_info[j][1][0]=='L'and layout_info[j][2]=='signal_lead':
            element = Part(name='signal_lead', type=0, info_file=info_files['signal_lead'], layout_component_id=layout_info[j][1])
            all_parts_info['signal_lead'].append(element)

        #print layout_info[j][1][0],layout_info[j][2]
    print all_parts_info, info_files
    print all_route_info


    cs_info = [] # list of rectanges to be used as cornerstitch input information
    component_to_cs_type={}
    #all_components=['EMPTY','power_trace','signal_trace','signal_lead', 'power_lead', 'MOS', 'IGBT', 'Diode','bonding wire pad','via']

    all_component_type_names=["EMPTY"]
    all_components=[]
    for j in range(1, len(layout_info)):
        for k,v in all_parts_info.items():
            for element in v:
                if element.layout_component_id==layout_info[j][1]:
                    #print layout_info[j]
                    if element not in all_components:
                        all_components.append(element)
                    if element.name not in all_component_type_names:
                        all_component_type_names.append(element.name)
        for k,v in all_route_info.items():
            for element in v:

                if element.layout_component_id==layout_info[j][1]:
                    if element not in all_components:
                        all_components.append(element)
                    if element.type==0 and element.name=='trace':
                        type_name='power_trace'
                    elif element.type==1 and element.name=='trace':
                        type_name='signal_trace'
                if type_name not in all_component_type_names:
                    all_component_type_names.append(type_name)
    #print all_component_type_names
    types = []
    for i in range(len(all_component_type_names)):
        type = 'Type_' + str(i)
        types.append(type)

    #print types

    for i in range(len(types)):
        component_to_cs_type[all_component_type_names[i]]=types[i]
    print component_to_cs_type
    for j in range(1, len(layout_info)):
        for k,v in all_parts_info.items():
            for element in v:
                if element.layout_component_id==layout_info[j][1]:
                    #print layout_info[j]
                    type=component_to_cs_type[element.name]
                    x=float(layout_info[j][3])
                    y=float(layout_info[j][4])
                    width = float(layout_info[j][5])
                    height = float(layout_info[j][6])
                    name=layout_info[j][1]
                    Schar='/'
                    Echar='/'
                    rect_info=[type,x,y,width,height,name,Schar,Echar]
                    cs_info.append(rect_info)
        for k,v in all_route_info.items():
            for element in v:
                if element.layout_component_id==layout_info[j][1]:
                    if element.type==0 and element.name=='trace':
                        type_name='power_trace'
                    elif element.type==1 and element.name=='trace':
                        type_name='signal_trace'
                    type = component_to_cs_type[type_name]
                    x = float(layout_info[j][3])
                    y = float(layout_info[j][4])
                    width = float(layout_info[j][5])
                    height = float(layout_info[j][6])
                    name = layout_info[j][1]
                    Schar = '/'
                    Echar = '/'
                    rect_info = [type, x, y, width, height, name, Schar, Echar]
                    cs_info.append(rect_info)
                else:
                    continue

    print cs_info








    '''
    for line in lines:  # considering each line in file
        print line,line.index, len(line)
        
        L = line.strip('\r\n')
        if len(L) > 5:
            d_out = re.sub("\t", ". ", L)
            d_out = re.sub("\s", ",", d_out)
            line = d_out.rstrip(',')
            line = line.split(',')
            if line!=['#', 'Layout', 'Information']:
                Definition.append(line)
        '''

    #print Definition
