if __name__ == '__main__':
    emptyVPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))
    emptyHPlane = tile(None, None, None, None, None, cell(0, 0, "EMPTY"))

    emptyVStitchList = [emptyVPlane]
    emptyHStitchList = [emptyHPlane]

    emptyVExample = vLayer(emptyVStitchList, 60, 60)
    emptyHExample = hLayer(emptyHStitchList, 60, 60)

    emptyVPlane.NORTH = emptyVExample.northBoundary
    emptyVPlane.EAST = emptyVExample.eastBoundary
    emptyVPlane.SOUTH = emptyVExample.southBoundary
    emptyVPlane.WEST = emptyVExample.westBoundary

    emptyHPlane.NORTH = emptyHExample.northBoundary
    emptyHPlane.EAST = emptyHExample.eastBoundary
    emptyHPlane.SOUTH = emptyHExample.southBoundary
    emptyHPlane.WEST = emptyHExample.westBoundary

    # emptyHExample.insert(5,20,15,5,"SOLID")
    # emptyHExample.insert(8, 15, 12, 10, "SOLID")

    if len(sys.argv) > 1:
        testfile = sys.argv[1]  # taking input from command line

        f = open(testfile, "rb")  # opening file in binary read mode
        index_of_dot = testfile.rindex('.')  # finding the index of (.) in path

        testbase = os.path.basename(testfile[:index_of_dot])  # extracting basename from path
        testdir = os.path.dirname(testfile)  # returns the directory name of file
        print testbase
        if not len(testdir):
            testdir = '.'

        list = []
        # a = ["blue","red","green","yellow","black","orange"]
        i = 0
        for line in f.read().splitlines():  # considering each line in file

            c = line.split(',')  # splitting each line with (,) and inserting each string in c
            if len(c) > 4:
                emptyVExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[
                    4])  # taking parameters of insert function (4 coordinates as integer and type of cell as string)
                emptyHExample.insert(int(c[0]), int(c[1]), int(c[2]), int(c[3]), c[4])

                list.append(patches.Rectangle(
                    (int(c[0]), int(c[3])), (int(c[2]) - int(c[0])), (int(c[1]) - int(c[3])),
                    # facecolor=a[i],
                    fill=False,

                ))
            i += 1
    else:
        exit(1)
    emptyVExample.Final_Merge()
    emptyHExample.Final_Merge()
    emptyHExample.set_id()
    emptyVExample.set_id()

    Hplane2 = emptyHExample
    Vplane2 = emptyVExample
    # for foo in Hplane2.stitchList:
    Hplane2.insert(10, 25, 20, 10, "Type_2")
    for foo in emptyHExample.stitchList:
        print foo.cell.x, foo.cell.type

    # CG = cg.constraintGraph(testdir+'/'+testbase+'gh.png',testdir+'/'+testbase+'gv.png')
    CG = cg.constraintGraph(testdir + '/' + testbase, testdir + '/' + testbase)
    # CG2 = cg.constraintGraph(testdir+'/'+testbase+'gv.png')
    CG.graphFromLayer(emptyHExample, emptyVExample)
    # CG2.graphFromLayer(emptyVExample)

    CG.printVM(testdir + '/' + testbase + 'vmat_h.txt', testdir + '/' + testbase + 'vmat_v.txt')
    # CG2.printVM(testdir+'/'+testbase+'vmat_v.txt')
    # CG1.printZDL()
    # CG2.printZDL()
    # diGraph1 = cg.multiCG(CG)
    # diGraph2 = cg.multiCG(CG)
    # con = constraint.constraint(1, "minWidth", 0, 1)
    # diGraph.addEdge(con.source, con.dest, con)

    # CG1.drawGraph()

    # diGraph1.drawGraph1()
    # diGraph2.drawGraph2()

    CSCG = CSCG.CSCG(emptyHExample, emptyVExample, CG, testdir + '/' + testbase, testdir + '/' + testbase)
    CSCG.findGraphEdges_h()
    CSCG.drawLayer1()
    '''


    CG.cgToGraph_h(testdir + '/' + testbase + 'edgeh.txt')
    CG.cgToGraph_v(testdir + '/' + testbase + 'edgev.txt')
    CSCG = CSCG.CSCG(emptyHExample,emptyVExample, CG,testdir+'/'+testbase,testdir+'/'+testbase)

    CSCG.findGraphEdges_h()
    CSCG.drawLayer1()
    CSCG.findGraphEdges_v()
    CSCG.drawLayer2()

    CSCG.drawRectangle(list)
    CSCG.update_stitchList()
    CSCG.ID_Conversion()
    CSCG.drawLayer11()
    CSCG.drawLayer22()
    '''
    # CSCG.drawLayer_h()
    # CSCG.drawLayer_v()
    # CSCG.drawLayer_hnew()
    # CSCG.drawLayer_hnew()
    # CSCG.drawLayer_vnew()
    # emptyVExample.drawLayer(truePointer=False)
    # emptyHExample.drawLayer(truePointer=False)

