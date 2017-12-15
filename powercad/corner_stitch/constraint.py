import numpy as np

class constraint():
    constraintIndex = ["Empty", "type1"]
    minWidth = [1, 2]
    minSpacing = np.zeros(shape = (len(constraintIndex), len(constraintIndex)))
    '''
    def __init__(self, constraintval, source, dest):
        self.setupMinSpacing()
        self.constraintval = constraintval
        #self.indexNo = indexNo
        #self.constraintType = constraintType
        self.source = source
        self.dest = dest
    '''
    def __init__(self, indexNo, constraintType, source, dest):
        self.setupMinSpacing()
        self.constraintName = self.constraintIndex[indexNo]
        self.indexNo = indexNo
        self.constraintType = constraintType
        self.source = source
        self.dest = dest

    def setupMinSpacing(self):
        constraint.minSpacing = ([[0, 1],[1, 2]])

    def addConstraint(self, conName, conValue):
        self.constraintIndex.append(conName)
        self.constraintValues.append(conValue)

    def getConstraintVal(self):
        if self.constraintType == 'minWidth':
            return constraint.minWidth[self.indexNo]
        elif self.constraintType == 'minSpacing':
            return constraint.minSpacing[source][dest]

    def getConstraintName(self):
        return self.constraintName

    def getIndexNo(self):
        return self.indexNo

    def printCon(self):
        print "CN = ", self.constraintName, "IndexNo = ", self.indexNo
