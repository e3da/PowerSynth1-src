'''
Created on Jul 11, 2013

@author: apsimms (edited by jhmain)
'''
# Renamed get_netlist for naming consistency with other files (previously getnetlist)

class netdata(): #Defines components that were used in this class
    
    def __init__(self):
        self.str = ''
        self.data = []
        self.comp = []
        self.word = ''
        self.complist = ['X_','M_','D_','R_','L_','C_','V_']
        self.components = ['Thyristors','Mosfets','Diodes','Resistors','Inductors','Capacitors','Voltage Source']
        self.index = 0
    
    def netlistconverter(self,netlist_file): #Opens netlist file and reads line by line to determine the components of the circuit
        netfile = open(str(netlist_file))
        infile = netfile.readline()
        self.str = ''.join(infile)
        print '\n'
        while infile:
            self.data = self.findcomponent()
            infile = netfile.readline()
            self.str = ''.join(infile)
        netfile.close()
        
    def findcomponent(self): #Finds all components from a netlist and records all necessary information on a list (data)
        for num in range(len(self.complist)):
            if self.str.find(self.complist[num]) is not -1:
                self.comp = []
                self.getcomp()
                self.data.append(self.comp)
        return self.data
    
    def getcomp(self): #Gets the information for one component
        for num2 in range(len(self.str)-1):
            if self.str[num2] is not ' ':
                self.word += self.str[num2]
            elif self.str[num2-1] is not ' ':
                self.comp.append(self.word)
                self.word = ''
            else:
                pass
        if self.str[len(self.str)-2] is not ' ':
            self.comp.append(self.word)
            self.word = ''

    def getdata(self):
        return self.data
        
    def getcomplist(self):
        return self.complist
        
    def getcomponents(self):
        return self.components
    
    def display(self):  #Displays the data after the operation
        for i in range(len(self.data)):
            print self.data[i]
            print '\n'