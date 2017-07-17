
class constraint():
    constraintIndex = ["Min_spacing", "Min_width"]
    constraintValues = [3, 4]

    def __init__(self, indexNo):
        self.constraintName = self.constraintIndex[indexNo]
        self.indexNo = indexNo

    def addConstraint(self, conName, conValue):
        self.constraintIndex.append(conName)
        self.constraintValues.append(conValue)

    def getConstraintName(self):
        return self.constraintName

    def getIndexNo(self):
        return self.indexNo

    def printCon(self):
        print "CN = ", self.constraintName, "IndexNo = ", self.indexNo