'''
Updated from December,2017
@ author: Imam Al Razi(ialrazi)
'''
import numpy as np

class constraint():
    '''
    all_components = ['EMPTY', 'power_trace', 'signal_trace', 'signal_lead', 'power_lead', 'MOS', 'IGBT', 'Diode','bonding wire pad', 'via']
    Type = []
    type=[]
    for i in range(len(all_components)):
        t = 'Type_' + str(i)
        Type.append(t)
        t.append(str(i))
    #Type=["EMPTY","Type_1", "Type_2","Type_3","Type_4"]  # in this version 4 types of components are considered (Trace, MOS, Leads, Diodes)

    #type=["0","1","2","3","4"]

    constraintIndex =['minWidth','minSpacing','minEnclosure','minExtension','minHeight'] # 5 types of constraints

    minSpacing = np.zeros(shape = (len(Type)-1, len(Type)-1)) # minimum spacing is a 2-D matrix
    minEnclosure = np.zeros(shape=(len(Type) - 1, len(Type) - 1)) # minimum Enclosure is a 2-D matrix


    '''

    def __init__(self,all_components=None,all_component_names=None):
        self.all_components=all_components
        self.all_component_names=all_component_names

        Type = []
        type = []
        for i in range(len(self.all_component_names)):
            t = 'Type_' + str(i)
            Type.append(t)
            type.append(str(i))
        # Type=["EMPTY","Type_1", "Type_2","Type_3","Type_4"]  # in this version 4 types of components are considered (Trace, MOS, Leads, Diodes)

        # type=["0","1","2","3","4"]

        self.constraintIndex = ['minWidth', 'minSpacing', 'minEnclosure', 'minExtension','minHeight']  # 5 types of constraints

        self.minSpacing = np.zeros(shape=(len(Type) - 1, len(Type) - 1))  # minimum spacing is a 2-D matrix
        self.minEnclosure = np.zeros(shape=(len(Type) - 1, len(Type) - 1))  # minimum Enclosure is a 2-D matrix


    def __init__(self,indexNo=None):
        """

        :param indexNo: index of the constraint type
        """
        self.indexNo = indexNo
        if indexNo !=None:
            self.constraintType = self.constraintIndex[self.indexNo]

    """
    Setting up different type of constraint values
    """
    def setupMinWidth(self,width):
        self.minWidth=width
    def setupMinHeight(self,height):
        self.minHeight=height
    def setupMinSpacing(self,spacing):
        self.minSpacing =spacing
    def setupMinEnclosure(self,enclosure):
        self.minEnclosure=enclosure
    def setupMinExtension(self,extension):
        self.minExtension=extension
    def addConstraint(self, conName, conValue):
        self.constraintIndex.append(conName)
        self.constraintValues.append(conValue)

    # returns constraint value of given edge
    def getConstraintVal(self,source=None,dest=None,type=None):
        if self.constraintType == 'minWidth':
            indexNO=self.Type.index(type)
            return constraint.minWidth[indexNO]
        elif self.constraintType == 'minHeight':
            indexNO=self.Type.index(type)
            return self.minHeight[indexNO]
        elif self.constraintType == 'minSpacing':
            return self.minSpacing[source][dest]
        elif self.constraintType == 'minEnclosure':
            return self.minEnclosure[source][dest]
        elif self.constraintType == 'minExtension':
            indexNO=self.Type.index(type)
            return self.minExtension[indexNO]


    def getIndexNo(self):
        return self.indexNo



