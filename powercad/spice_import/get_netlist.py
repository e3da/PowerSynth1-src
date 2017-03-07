'''
Created on Jul 11, 2013

@author: apsimms (edited by jhmain)
'''
# - Renamed get_netlist for naming consistency with other files (previously getnetlist)


class Netdata(): # Defines components that were used in this class
    
    def __init__(self):
        self.str = ''
        self.data = []
        self.comp = []
        self.word = ''
        self.complist = ['X_','M_','D_','R_','L_','C_','V_']
        self.components = ['Thyristors','Mosfets','Diodes','Resistors','Inductors','Capacitors','Voltage Source']
        self.index = 0
    
    def netlistconverter(self,netlist_file): # Opens netlist file and reads line by line to determine the components of the circuit (eg. one of the lines may read: 'V_V1         N04360 0 15Vdc\n'
        netfile = open(str(netlist_file))
        infile = netfile.readline()
        self.str = ''.join(infile)
        while infile:
            self.data = self.findcomponent()
            infile = netfile.readline()
            self.str = ''.join(infile)
        netfile.close()
        
    def findcomponent(self): # Finds all components from a netlist and records all necessary information on a list (data) (eg. one of the components may be 'V_' and it's data would be ['V_V1', 'N04360', '0', '15Vdc'])
        for num in range(len(self.complist)):
            if self.str.find(self.complist[num]) is not -1:
                self.comp = []
                self.getcomp()
                self.data.append(self.comp)
        return self.data
    
    def getcomp(self): # Gets the information for one component i.e. converts that netlist line into many words (eg. ['V_V1', 'N04360', '0', '15Vdc'])
        for num2 in range(len(self.str)-1):
            if self.str[num2] is not ' ': # if the character is a blank,
                self.word += self.str[num2] # append the character to the temp word
            elif self.str[num2-1] is not ' ': # if the character before the character you are currently at is not blank, (i.e. if the end of the current temp word is detected),
                self.comp.append(self.word) # save the temp word, and
                self.word = '' # re-initialize the temp word to blank for the next round.
            else:
                pass
        if self.str[len(self.str)-2] is not ' ': # To save the last word: if the third to last character in the line (i.e. the character before '\n' at the end of the line) is not blank,
            self.comp.append(self.word) # then save the temp word (the last word).
            self.word = '' # reinitialize the temp word to blank

    def getdata(self):
        return self.data
        
    def getcomplist(self):
        return self.complist
        
    def getcomponents(self):
        return self.components
    
    def display(self):  # Displays the data after the operation
        for i in range(len(self.data)):
            print self.data[i]
            print '\n'