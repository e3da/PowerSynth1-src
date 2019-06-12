


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

class BondingWires():
    def __init__(self, name=None,info_file=None):
        '''

        :param name: name of bondwire  (W1,W2,....)
        '''

        self.name=name
        self.info_file=info_file # file containing information about bond wires (.wire)
        self.profile_type=0 # 0:JEDEC-4 points,1: JEDEC-5 points
        self.mat_resistivity=0.0
        self.radius=0.0

    def load_wire(self):

        with open(self.info_file, 'rb') as inputfile:
            for line in inputfile.readlines():
                line = line.strip("\r\n")
                info = line.split(" ")
                if info[0]=='JEDEC-4 points':
                    self.profile_type=0
                elif info[0]=='JEDEC-5 points':
                    self.profile_type = 1
                elif info[0]=='Resistivity':
                    self.mat_resistivity=float(info[1])
                elif info[0]=='Radius':
                    self.radius=float(info[1])

    def printWire(self):
        print self.name
        print self.info_file
        print self.mat_resistivity
        print self.radius

