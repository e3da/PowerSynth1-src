import numpy as np

class constraint():
    Type=["EMPTY","Type_1", "Type_2","Type_3","Type_4"]
    type=["0","1","2","3","4"]
    constraintIndex =['minWidth','minSpacing','minEnclosure','minExtension','minHeight']

    minSpacing = np.zeros(shape = (len(constraintIndex)-1, len(constraintIndex)-1))
    minEnclosure = np.zeros(shape=(len(constraintIndex) - 1, len(constraintIndex) - 1))
    def __init__(self,indexNo=None):

        self.indexNo = indexNo
        if indexNo !=None:
            self.constraintType = self.constraintIndex[self.indexNo]








    def setupMinWidth(self,width):
        constraint.minWidth=width
    def setupMinHeight(self,height):
        #print"H", height
        constraint.minHeight=height
    def setupMinSpacing(self,spacing):
        #constraint.minSpacing = ([[0,0,0,0,0],[0,5, 3, 4,5],[0,3, 5, 5,6],[0,4, 5, 5,8],[0,5,6,8,5]])
        constraint.minSpacing =spacing

    def setupMinEnclosure(self,enclosure):
        constraint.minEnclosure=enclosure
        #constraint.minEnclosure=([[0,5,5,5,5],[0,0, 3, 4,5],[0,0, 0, 2,3],[0,0, 0, 0,1],[0,0,0,0,0]])
    def setupMinExtension(self,extension):
        constraint.minExtension=extension

    def addConstraint(self, conName, conValue):
        self.constraintIndex.append(conName)
        self.constraintValues.append(conValue)

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



