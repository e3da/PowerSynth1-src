'''
Updated from December,2017
@ author: Imam Al Razi(ialrazi)
'''
import numpy as np

class constraint():
    Type=["EMPTY","Type_1", "Type_2","Type_3","Type_4"]  # in this version 4 types of components are considered (Trace, MOS, Leads, Diodes)
    type=["0","1","2","3","4"]
    constraintIndex =['minWidth','minSpacing','minEnclosure','minExtension','minHeight'] # 5 types of constraints

    minSpacing = np.zeros(shape = (len(constraintIndex)-1, len(constraintIndex)-1)) # minimum spacing is a 2-D matrix
    minEnclosure = np.zeros(shape=(len(constraintIndex) - 1, len(constraintIndex) - 1)) # minimum Enclosure is a 2-D matrix
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
        constraint.minWidth=width
    def setupMinHeight(self,height):
        constraint.minHeight=height
    def setupMinSpacing(self,spacing):
        constraint.minSpacing =spacing
    def setupMinEnclosure(self,enclosure):
        constraint.minEnclosure=enclosure
    def setupMinExtension(self,extension):
        constraint.minExtension=extension
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
            return constraint.minHeight[indexNO]
        elif self.constraintType == 'minSpacing':
            return constraint.minSpacing[source][dest]
        elif self.constraintType == 'minEnclosure':
            return constraint.minEnclosure[source][dest]
        elif self.constraintType == 'minExtension':
            indexNO=self.Type.index(type)
            return constraint.minExtension[indexNO]


    def getIndexNo(self):
        return self.indexNo



