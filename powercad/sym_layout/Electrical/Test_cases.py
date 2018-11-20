import cProfile
import matplotlib
import pstats
from powercad.Spice_handler.spice_export.PEEC_num_solver import *
from scipy import *
from powercad.sym_layout.Electrical.E_mesh import *

def test_hier2():
    freqs = [0, 100, 200, 1000]
    for freq in freqs:

        r1 = Rect(14, 10, 0, 10)
        R1 = E_plate(rect=r1, n=(0, 0, 1), z=0, dz=0.2)
        r2 = Rect(10, 0, 0, 5)
        R2 = E_plate(rect=r2, z=0, dz=0.2)
        r3 = Rect(14, 0, 9, 14)
        R3 = E_plate(rect=r3, z=0, dz=0.2)
        r4 = Rect(-1, -6, -6, 20)
        R4 = E_plate(rect=r4, z=0, dz=0.2)
        r5 = Rect(9, 0, 7, 8)
        R5 = E_plate(rect=r5, z=0, dz=0.2)
        r6 = Rect(10, -1, -6, -1)
        R6 = E_plate(rect=r6, z=0, dz=0.2)
        r7 = Rect(10, -1, 15, 20)
        R7 = E_plate(rect=r7, z=0, dz=0.2)

        sh1 = Rect(7, 5, 11.5, 13.5)
        S1 = Sheet(rect=sh1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
        sh2 = Rect(6.5, 5.5, 12.5, 13.5)
        S2 = Sheet(rect=sh2, net='M1_S', type='point', n=(0, 0, 1), z=0.4)
        sh3 = Rect(6.25, 5.75, 11.75, 12.25)
        S3 = Sheet(rect=sh3, net='M1_G', type='point', n=(0, 0, 1), z=0.4)
        sh1 = Rect(7, 5, 1, 3)
        S4 = Sheet(rect=sh1, net='M2_D', type='point', n=(0, 0, 1), z=0.2)
        sh2 = Rect(6.5, 5.5, 1, 2)
        S5 = Sheet(rect=sh2, net='M2_S', type='point', n=(0, 0, 1), z=0.4)
        sh3 = Rect(6.25, 5.75, 2.25, 2.75)
        S6 = Sheet(rect=sh3, net='M2_G', type='point', n=(0, 0, 1), z=0.4)
        sh7 = Rect(14, 12, 4, 10)
        S7 = Sheet(rect=sh7, net='DC_plus', type='point', n=(0, 0, 1), z=0.2)
        sh8 = Rect(-4, -6, 4, 11)
        S8 = Sheet(rect=sh8, net='DC_minus', type='point', n=(0, 0, 1), z=0.2)

        sh9 = Rect(2, 1, 7.25, 7.75)
        S9 = Sheet(rect=sh9, net='Gate', type='point', n=(0, 0, 1), z=0.2)

        sh10 = Rect(6, 5, 7.25, 7.35)
        S10 = Sheet(rect=sh10, net='bwG_m2', type='point', n=(0, 0, 1), z=0.2)

        sh11 = Rect(6, 5, 7.65, 7.75)
        S11 = Sheet(rect=sh11, net='bwG_m1', type='point', n=(0, 0, 1), z=0.2)

        sh12 = Rect(6, 5, 15.25, 15.35)
        S12 = Sheet(rect=sh12, net='bwS_m1', type='point', n=(0, 0, 1), z=0.2)

        sh13 = Rect(6, 5, -1.35, -1.25)
        S13 = Sheet(rect=sh13, net='bwS_m2', type='point', n=(0, 0, 1), z=0.2)

        Mos1 = Component(sheet=[S1, S2, S3], conn=[['M1_D', 'M1_S']], val=[1e-3])
        Mos2 = Component(sheet=[S4, S5, S6], conn=[['M2_D', 'M2_S']], val=[1e-3])
        Bw_S1 = Component(sheet=[S2, S12], conn=[['bwS_m1', 'M1_S']], val=[1e-3])
        Bw_S2 = Component(sheet=[S5, S13], conn=[['bwS_m2', 'M2_S']], val=[1e-3])
        Bw_G1 = Component(sheet=[S3, S11], conn=[['bwG_m1', 'M1_G']], val=[1e-3])
        Bw_G2 = Component(sheet=[S6, S10], conn=[['bwG_m2', 'M2_G']], val=[1e-3])

        new_module = E_module(plate=[R1, R2, R3, R4, R5, R6, R7],
                              sheet=[S7, S8, S9], components=[Mos1, Mos2, Bw_S1, Bw_S2, Bw_G1, Bw_G2])

        new_module.form_group()
        new_module.split_layer_group()
        fig = plt.figure(1)
        ax = a3d.Axes3D(fig)
        ax.set_xlim3d(-5, 25)
        ax.set_ylim3d(-5, 25)
        ax.set_zlim3d(0, 5)
        plot_rect3D(rect2ds=new_module.plate + new_module.sheet, ax=ax)
        plt.show()
        hier = Hier_E(module=new_module)
        hier.form_hierachy()
        fig = plt.figure(2)
        ax = a3d.Axes3D(fig)
        pr = cProfile.Profile()
        pr.enable()
        emesh = ElectricalMesh(hier_E=hier, freq=freq)
        emesh.mesh_grid_hier(Nx=3, Ny=3)
        ax.set_xlim3d(0, 15)
        ax.set_ylim3d(0, 15)
        ax.set_zlim3d(0, 15)
        emesh.plot_3d(fig=fig, ax=ax)
        emesh.update_mutual()

        # EVALUATION
        circuit = Circuit()
        pt1 = (7, -4)
        pt2 = (6.5, 12)
        src1 = emesh.find_node(pt2)
        sink1 = emesh.find_node(pt1)
        print src1, sink1
        circuit.comp_mode = 'val'
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        circuit.assign_freq(freq)
        circuit._assign_vsource(src1, vname='Vs1', volt=1)
        circuit._add_ports(sink1)
        circuit.build_current_info()
        circuit.solve_iv()

        print circuit._compute_imp(src1, sink1, sink1)
        pr.disable()
        pr.create_stats()
        file = open('mystats.txt', 'w')
        stats = pstats.Stats(pr, stream=file)
        stats.sort_stats('time')
        stats.print_stats()

        result = circuit.results
        all_V = []
        all_I = []

        pos = {}
        for n in emesh.graph.nodes():
            node = emesh.graph.node[n]['node']
            pos[n] = node.pos
            net = circuit.node_dict[node.node_id]
            V_name = 'v' + str(net)
            node.V = np.abs(result[V_name])
            all_V.append(node.V)
        v_min = min(all_V)
        v_max = max(all_V)
        normV = Normalize(v_min, v_max)
        fig = plt.figure(3)
        ax = a3d.Axes3D(fig)
        plot_v_map_3D(norm=normV, fig=fig, ax=ax, cmap=emesh.c_map, G=emesh.graph)

        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            I_name = 'I_L' + edge_name
            edge.I = np.abs(result[I_name])
            try:
                width = edge.data['w'] * 1e-3
                thick = 0.2e-3
                A = width * thick
            except:
                A = 1e-6
            edge.J = edge.I / A

            if edge.type != 'hier':
                all_I.append(edge.J)
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(I_min, I_max)
        # fig = plt.figure(4)
        # ax = a3d.Axes3D(fig)
        # plot_I_map_3D(norm=normI, fig=fig, ax=ax, cmap=emesh.c_map, G=emesh.graph)


        # fig = plt.figure(5)
        # ax = fig.add_subplot(111)
        # plt.xlim([-10, 25])
        # plt.ylim([-10, 25])
        # plot_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, ori='v', mode='J')

        # fig = plt.figure(6)
        # ax = fig.add_subplot(111)
        plt.xlim([-10, 25])
        plt.ylim([-10, 25])
        # plot_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, ori='h', mode='J')

        # fig = plt.figure(7)
        # ax = fig.add_subplot(111)
        plt.xlim([-10, 25])
        plt.ylim([-10, 25])
        # plot_combined_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode='J', W=[-10, 20], H=[
        #    -10, 20],rows=25, cols=25)
        # PLOTTING CURRENT/CURRENT DENSITY VECTORS
        all_I = []
        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            try:
                width = edge.data['w'] * 1e-3
                thick = 0.2e-3
                A = width * thick
            except:
                A = 1e-6
            I_name = 'I_L' + edge_name
            edge.I = np.real(result[I_name])
            edge.J = edge.I / A
            all_I.append(edge.J)
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(I_min, I_max)
        fig = plt.figure(8)
        ax = fig.add_subplot(111)
        plt.xlim([-10, 20])
        plt.ylim([-5, 15])
        plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode='J',
                                         W=[-10, 20], H=[-10, 20], numvecs=20, mesh='grid')

        plt.title('frequency ' + str(freq * 1000) + ' Hz')
        plt.show()


def test_Ushape():
    freqs = [0, 10, 21.544, 46.415, 100, 215.443, 464.159, 1000]
    for freq in freqs:
        pr = cProfile.Profile()
        pr.enable()
        R1 = Rect(4, 0, 0, 18)
        R2 = Rect(16, 4, 16, 20)
        R3 = Rect(20, 16, 0, 18)
        # R4 = Rect(7.5,2.5,0,7.5)
        rects = [R1, R2, R3]  # ,R4]
        P1, P2, P3 = [E_plate(rect=r, z=0, dz=0.2) for r in rects]
        new_module = E_module(plate=[P1, P2, P3])
        new_module.form_group()
        new_module.split_layer_group()
        fig = plt.figure(1)
        ax = a3d.Axes3D(fig)
        ax.set_xlim3d(-5, 15)
        ax.set_ylim3d(-5, 15)
        ax.set_zlim3d(0, 2)
        plot_rect3D(rect2ds=new_module.plate, ax=ax)
        #plt.show()
        fig = plt.figure(2)
        ax = a3d.Axes3D(fig)
        ax = plt.subplots()
        hier = Hier_E(module=new_module)
        hier.form_hierachy()
        emesh = ElectricalMesh(hier_E=hier, freq=freq)
        emesh.mesh_grid_hier(Nx=3, Ny=3)
        emesh.plot_lumped_graph()
        #ax.set_xlim3d(-5, 20)
        #ax.set_ylim3d(-5, 20)
        #ax.set_zlim3d(0, 2)
        plt.show()

        circuit = Circuit()
        if freq != 0:
            emesh.update_mutual()
        circuit.comp_mode = 'val'
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        pt1 = (0, 2)
        pt2 = (0, 18)

        src1 = emesh.find_node(pt1)
        sink1 = emesh.find_node(pt2)
        print src1, sink1
        # raw_input()
        # sink3 = emesh.find_node(pt3)
        circuit.assign_freq(freq * 1000)
        circuit._assign_vsource(src1, vname='Vs1', volt=1)
        circuit.Rport = 50

        circuit._add_ports(sink1)
        # circuit._add_ports(sink3)

        circuit.build_current_info()
        circuit.solve_iv()
        # circuit.solve_iv_hspice(filename='ushape.sp', env='hspice')
        print "freq", freq, "model", circuit._compute_imp(src1, sink1, sink1)

        # COMPARE:
        '''
        comp_dict= {}
        for k in circuit.results.keys():
            comp_dict[k] = (circuit.results[k]-circuit.hspice_result[k])/ circuit.hspice_result[k]

        for k in comp_dict.keys():
            print "diff",k,np.abs(comp_dict[k])*100
        '''
        # circuit.results = circuit.hspice_result
        # print "freq", freq, "HSPICE", circuit._compute_imp(src1, sink1, sink1)

        pr.disable()
        pr.create_stats()
        file = open('mystats.txt', 'w')
        stats = pstats.Stats(pr, stream=file)
        stats.sort_stats('time')
        stats.print_stats()
        '''

        result = circuit.results
        all_V = []
        all_I = []
        # PLOTTING VOLTAGE DISTRIBUTION
        pos = {}
        for n in emesh.graph.nodes():
            node = emesh.graph.node[n]['node']
            pos[n] = node.pos
            net = circuit.node_dict[node.node_id]
            V_name = 'v' + str(net)
            node.V = np.abs(result[V_name])
            all_V.append(node.V)
        v_min = min(all_V)
        v_max = max(all_V)
        normV = Normalize(v_min, v_max)
        #fig = plt.figure(3)
        #ax = a3d.Axes3D(fig)
        #ax = fig.add_axes([0, 0, 10, 10])
        #fig,ax = plt.subplots()
        #emesh.find_E(ax = ax)

        plot_v_map_3D(norm=normV, ax=ax, cmap=emesh.c_map, G=emesh.graph)

        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            width =edge.data['w']*1e-3
            thick =0.2e-3
            A = width * thick
            I_name = 'I_L' + edge_name
            edge.I = abs(result[I_name])
            edge.J = edge.I/A
            all_I.append(edge.I)

        # PLOTTING CURRENT / CURRENT DENSITY DISTRIBUTION

        #I_min = min(all_I)
        #I_max = max(all_I)
        #normI = Normalize(I_min, I_max)
        #normI = Normalize(1,102700)
        #fig = plt.figure(4)
        #ax = a3d.Axes3D(fig)
        # (norm=normI, fig=fig, ax=ax, cmap=emesh.c_map, G=emesh.graph)

        #matplotlib.use('Agg')

        #fig = plt.figure(5)

        #fig.canvas.draw()

        #ax = fig.add_subplot(111)
        #plt.xlim([0, 10])
        #plt.ylim([0, 10])
        #plot_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, ori='v',mode = 'J')
        #plt.title('vertical')

        #fig = plt.figure(6)
        #fig.canvas.draw()

        #ax = fig.add_subplot(111)
        #plt.xlim([0, 10])
        #plt.ylim([0, 10])
        #plot_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, ori='h',mode='J')
        #plt.title('horizontal')

        #fig = plt.figure(7)
        #ax = fig.add_subplot(111)
        #plt.xlim([0, 10])
        #plt.ylim([0, 10])
        #plot_combined_I_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode = 'J', W =[0, 10], H =[
        #    0, 10],rows = 25, cols = 25)


        # PLOTTING CURRENT/CURRENT DENSITY VECTORS
        all_I = []
        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            width = edge.data['w'] * 1e-3
            thick = 0.2e-3
            A = width * thick
            I_name = 'I_L' + edge_name
            edge.I = np.real(result[I_name])
            edge.J = edge.I / A #/ 5.96e7
            all_I.append(abs(edge.J))
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(I_min, I_max)
        #normI = Normalize(0,100000)
        #normI = Normalize(0, 2.26e-3)
        fig = plt.figure(8)
        ax = fig.add_subplot(111)
        plt.xlim([-2.5, 17.5])
        plt.ylim([-2.5, 17.5])
        plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode='J', W=[0, 15], H=[
            0, 15], numvecs=31, name='frequency ' + str(freq) + ' kHz', mesh='grid')
        plt.title('frequency ' + str(freq) + ' kHz')
        plt.show()
        '''


def test_single_trace_mesh():
    freqs = np.linspace(10, 100, 4).tolist()
    freqs = [1000]
    for freq in freqs:
        i = freqs.index(freq)
        R4 = Rect(2, 0, 0, 10)
        P4 = E_plate(R4, 0, 0.2)
        new_module = E_module(plate=[P4])
        new_module.form_group()
        new_module.split_layer_group()
        fig = plt.figure(1)
        ax = a3d.Axes3D(fig)
        hier = Hier_E(module=new_module)
        hier.form_hierachy()
        emesh = ElectricalMesh(hier_E=hier, freq=freq)
        emesh.mesh_grid_hier(Nx=3, Ny=3)
        emesh.update_mutual()
        emesh.plot_3d(fig=fig, ax=ax)
        ax.set_xlim3d(0, 10)
        ax.set_ylim3d(0, 2)
        ax.set_zlim3d(0, 2)
        circuit = Circuit()
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        pt1 = (0, 1)
        pt2 = (10, 1)
        src1 = emesh.find_node(pt1)
        sink1 = emesh.find_node(pt2)
        print src1, sink1
        circuit.assign_freq(freq * 1000)
        circuit._assign_vsource(src1, vname='Vs1', volt=1)
        circuit._add_ports(sink1)
        circuit.build_current_info()
        circuit.solve_iv()
        circuit.solve_iv_hspice(filename='singletrace.sp',
                                env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))

        result = circuit.results

        matplotlib.use('Agg')
        print freq, 'Hz'

        print circuit._compute_imp(src1, sink1, sink1)

        # PLOTTING CURRENT/CURRENT DENSITY VECTORS
        all_I = []

        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            width = edge.data['w'] * 1e-3
            thick = 0.2e-3
            A = width * thick
            I_name = 'I_L' + edge_name
            edge.I = np.real(result[I_name])
            edge.J = edge.I / A
            all_I.append(abs(edge.J))
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(I_min, I_max)
        normI = Normalize(10000, 100000)
        fig = plt.figure(i)
        ax = fig.add_subplot(111)
        plt.xlim([0, 10])
        plt.ylim([-1, 3])
        plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode='J',
                                         W=[0, 10],
                                         H=[0, 2], numvecs=21)
        plt.title('frequency ' + str(freq * 1000) + ' Hz')
    plt.show()


def test_3d_module():
    R1 = Rect(5, 0, 0, 10)
    P1 = E_plate(R1, 0, 0.2)
    R2 = Rect(2.5, 0, 0, 10)
    P2 = E_plate(R2, 0.4, 0.2)
    R3 = Rect(5, 3, 0, 10)
    P3 = E_plate(R3, 0.4, 0.2)
    sh1 = Rect(3.5, 3, 2, 3)
    S1 = Sheet(rect=sh1, net='M1_G', type='point', n=(0, 0, -1), z=0.4)
    sh2 = Rect(3.5, 3, 6, 7)
    S2 = Sheet(rect=sh2, net='M2_G', type='point', n=(0, 0, -1), z=0.4)

    sh3 = Rect(2.5, 1.5, 1.5, 3.5)
    S3 = Sheet(rect=sh3, net='M1_S', type='point', n=(0, 0, -1), z=0.4)
    sh4 = Rect(2.5, 1.5, 5.5, 7.5)
    S4 = Sheet(rect=sh4, net='M2_S', type='point', n=(0, 0, -1), z=0.4)

    sh5 = Rect(4, 1, 1, 4)
    S5 = Sheet(rect=sh5, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    sh6 = Rect(4, 1, 5, 8)
    S6 = Sheet(rect=sh6, net='M2_D', type='point', n=(0, 0, 1), z=0.2)

    new_module = E_module(plate=[P1, P2, P3], sheet=[S1, S2, S3, S4, S5, S6])
    new_module.form_group()
    new_module.split_layer_group()
    # Plot 3D
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(-5, 25)
    ax.set_ylim3d(-5, 25)
    ax.set_zlim3d(-2, 2)
    plot_rect3D(rect2ds=new_module.plate, ax=ax)
    plt.show()
    # plot 3D mesh
    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    emesh = ElectricalMesh(hier_E=hier, freq=10)
    emesh.mesh_grid_hier(Nx=3, Ny=3)
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(0, 10)
    ax.set_ylim3d(0, 5)
    ax.set_zlim3d(0, 1)
    emesh.plot_3d(fig=fig, ax=ax)
    plt.savefig("mesh.png", dpi=300)
    plt.show()


def balance_study():
    # Metal top
    R1 = Rect(2, 0, 0, 43.5)
    R2 = Rect(2, 0, 44.5, 46.5)
    R3 = Rect(2, 0, 47.5, 58)
    R4 = Rect(2, 0, 47.5, 58)
    R5 = Rect(5, 3, 0, 58)
    R6 = Rect(15.5, 6, 0, 58)
    R7 = Rect(18.5, 15.5, 0, 11.5)
    R8 = Rect(18.5, 16.5, 12.5, 27.5)
    R9 = Rect(18.5, 15.5, 27.5, 58)
    R10 = Rect(32, 19.5, 0, 28.5)
    R11 = Rect(21.5, 19.5, 29.5, 45.5)
    R12 = Rect(32, 21.5, 29.5, 30.5)
    R13 = Rect(32, 22.5, 30.5, 58)
    R14 = Rect(22.5, 19.5, 46.5, 58)
    R15 = Rect(35, 33, 0, 58)
    R16 = Rect(38, 36, 0, 9.5)
    R17 = Rect(38, 36, 10.5, 12.5)
    R18 = Rect(38, 36, 13.5, 58)
    # Devices and Sheets:
    Dev1 = Rect(26,24,3,4)
    Dev2 = Rect(26, 24, 15, 16)
    Dev3 = Rect(11, 10, 40, 42)
    Dev4 = Rect(11, 10, 52, 54)
    M1_D = Sheet(rect=Dev1, net='M1_D', type='point', n=(0, 0, 1), z=0.2)
    M2_D = Sheet(rect=Dev2, net='M2_D', type='point', n=(0, 0, 1), z=0.2)
    M3_D = Sheet(rect=Dev3, net='M3_D', type='point', n=(0, 0, 1), z=0.2)
    M4_D = Sheet(rect=Dev4, net='M4_D', type='point', n=(0, 0, 1), z=0.2)

    rects = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14, R15, R16, R17, R18]
    sheets= [M1_D,M2_D,M3_D,M4_D]
    #rects = [R6,R7,R8,R9]
    plates = []
    for r in rects:
        z = 0
        dz = 0.2
        plates.append(E_plate(r, z, dz))

    new_module = E_module(plate=plates,sheet=sheets)
    new_module.form_group()
    new_module.split_layer_group()
    # Plot 3D
    fig = plt.figure(1)
    #ax = a3d.Axes3D(fig)
    #ax.set_xlim3d(-2, 62)
    #ax.set_ylim3d(-2, 42)
    #ax.set_zlim3d(-1, 10)
    #plot_rect3D(rect2ds=new_module.plate, ax=ax)
    # plot 3D mesh
    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    emesh = ElectricalMesh(hier_E=hier, freq=10)
    emesh.mesh_grid_hier(Nx=3, Ny=3)
    emesh.update_mutual()
    fig = plt.figure(2)
    emesh.plot_lumped_graph()
    #ax = a3d.Axes3D(fig)
    #ax.set_xlim3d(0, 62)
    #ax.set_ylim3d(0, 42)
    #ax.set_zlim3d(-1, 10)
    #emesh.plot_3d(fig=fig, ax=ax)
    # plt.savefig("mesh.png", dpi=300)
    plt.show()


def test_mutual():
    R1 = Rect(5, -5, -3.5, -0.5)
    R2 = Rect(5, -5, 0.5, 3.5)
    rects = [R1, R2]
    plates = []
    for r in rects:
        z = 0
        dz = 0.2
        plates.append(E_plate(r, z, dz))
    new_module = E_module(plate=plates)
    new_module.form_group()
    new_module.split_layer_group()
    freq = [10.0, 21.544, 46.415, 100, 215.44, 464.15, 1000]
    for f in freq:
        hier = Hier_E(module=new_module)
        hier.form_hierachy()
        emesh = ElectricalMesh(hier_E=hier, freq=f)
        emesh.mesh_grid_hier(Nx=3, Ny=3)
        fig = plt.figure(2)
        ax = a3d.Axes3D(fig)
        ax.set_xlim3d(-4, 4)
        ax.set_ylim3d(-6, 6)
        ax.set_zlim3d(-1, 5)
        emesh.plot_3d(fig=fig, ax=ax)
        # plt.savefig("mesh.png", dpi=300)
        emesh.update_mutual()
        circuit = Circuit()
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        pt1 = (-2, -5)
        pt2 = (-2, 5)
        pt3 = (2, -5)
        pt4 = (2, 5)
        src1 = emesh.find_node(pt1)
        sink1 = emesh.find_node(pt2)
        src2 = emesh.find_node(pt3)
        sink2 = emesh.find_node(pt4)
        circuit.assign_freq(f * 1000)
        # print src1,sink1
        # print src2,sink2
        # circuit.solve_iv_hspice(filename='testM.sp',
        # env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
        # circuit.results=circuit.hspice_result
        print 'freq', f
        circuit._compute_mutual([src1, src2], [sink1, sink2], vname='Vs1')

def test_layer_stack_mutual():
    es = E_stack(file="C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\ELayerStack//3_layers.csv")
    es.load_layer_stack()
    R1 = Rect(5, -5, -3.5, -0.5)
    R2 = Rect(5, -5, 0.5, 3.5)
    layer1 = [R1, R2]
    plates = []
    for r in layer1:
        z = 1.68
        dz = 0.2
        plates.append(E_plate(r, z, dz))
    R3 = Rect(20, -20, -20, 20)
    #layer2 = [R3]
    #for r in layer2:
        #z = 0.84
        #dz = 0.2
        #plates.append(E_plate(r, z, dz))
    R4 = Rect(5, -5, 0.5, 3.5)
    R5 = Rect(5, -5, -3.5, -0.5)
    layer3 = [R4,R5]
    for r in layer3:
        z = 0
        dz = 0.2
        plates.append(E_plate(r, z, dz))

    #print plates
    new_module = E_module(plate=plates,layer_stack=es)
    new_module.form_group()
    new_module.split_layer_group()
    # Plot 3D
    #fig = plt.figure(1)
    #ax = a3d.Axes3D(fig)
    #ax.set_xlim3d(-35, 35)
    #ax.set_ylim3d(-35, 35)
    #ax.set_zlim3d(-1, 10)
    #plot_rect3D(rect2ds=new_module.plate, ax=ax)

    #plt.show()
    freq = [10.0, 21.544, 46.415, 100, 215.44, 464.15, 1000]
    f=1000
    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    emesh = ElectricalMesh(hier_E=hier, freq=f)
    emesh.mesh_grid_hier(Nx=5, Ny=3)
    fig = plt.figure(1)
    ax = a3d.Axes3D(fig)
    ax.set_xlim3d(-35, 35)
    ax.set_ylim3d(-35, 35)
    ax.set_zlim3d(-1, 1)
    emesh.plot_3d(fig=fig, ax=ax)
    plt.show()

    # plt.savefig("mesh.png", dpi=300)
    emesh.update_mutual()
    circuit = Circuit()
    circuit._graph_read(emesh.graph)
    circuit.m_graph_read(emesh.m_graph)
    pt1 = (-2, -5,1.68)
    pt2 = (-2, 5, 1.68)
    pt3 = (2, -5, 1.68)
    pt4 = (2, 5, 1.68)
    pt5 = (-2, -5, 0)
    pt6 = (-2, 5, 0)
    pt7 = (2, -5, 0)
    pt8 = (2, 5, 0)
    #pt5 = (0, 0, 0)

    src1 = emesh.find_node(pt1)
    sink1 = emesh.find_node(pt2)
    src2 = emesh.find_node(pt3)
    sink2 = emesh.find_node(pt4)
    src3 = emesh.find_node(pt5)
    sink3 = emesh.find_node(pt6)
    src4 = emesh.find_node(pt7)
    sink4 = emesh.find_node(pt8)
    #sink3 = emesh.find_node(pt5)
#       #circuit._add_ports(sink3)

    circuit.assign_freq(f * 1000)
    print 'freq', f
    #circuit._compute_mutual([src1, src2], [sink1, sink2], vname='Vs1')
    circuit._compute_matrix([src1, src2,src3,src4], [sink1, sink2,sink3,sink4])
    all_I = []
    result = circuit.results
    for e in emesh.graph.edges(data=True):
        edge = e[2]['data']
        edge_name = edge.name
        width = edge.data['w'] * 1e-3
        thick = edge.thick
        A = width * thick
        I_name = 'I_L' + edge_name
        edge.I = np.real(result[I_name])
        edge.J = edge.I / A
        all_I.append(abs(edge.J))
    I_min = min(all_I)
    I_max = max(all_I)
    normI = Normalize(I_min, I_max)
    #fig = plt.figure(2)
    #ax = fig.add_subplot(111)
    #plt.xlim([-20, 20])
    #plt.ylim([-20, 20])
    #plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=0, mode='J',
    #                                 W=[-20, 20],
    #                                 H=[-20, 20], numvecs=51)
    #plt.show()
    # print src1,sink1
    # print src2,sink2
    # circuit.solve_iv_hspice(filename='testM.sp',
    # env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))
    # circuit.results=circuit.hspice_result

def S_para_IWIPP():

    freqs = [10, 21.544, 46.415, 100, 215.443, 464.159, 1000,2154.43,4641.59,10000, 21544.3, 46415.9, 100000]
    freqs = np.logspace(4,9,num=20).tolist()
    #f_cv = [f*1000 for f in freqs]
    R1 = Rect(8, 0, 0, 5)
    R2 = Rect(8, 5, 5, 20)
    R3 = Rect(11, 9, 0, 20)
    rects = [R1, R2, R3]

    plates = [E_plate(rect=r, z=1.035, dz=0.035) for r in rects]
    # R4= Rect(13, -1, -1, 21)
    # plates.append(E_plate(rect=R4, z=0, dz=0.035))
    new_module = E_module(plate=plates)
    new_module.form_group()
    new_module.split_layer_group()
    hier = Hier_E(module=new_module)
    hier.form_hierachy()
    emesh = ElectricalMesh(hier_E=hier, mdl_name='s_params_test.rsmdl')
    emesh.mesh_grid_hier(Nx=3, Ny=3)
    #emesh.plot_lumped_graph()
    #plt.show()
    pt1 = (2.5, 0, 1.035)
    pt2 = (20, 6.5, 1.035)
    pt3 = (0, 10, 1.035)
    pt4 = (20, 10, 1.035)

    P1 = emesh.find_node(pt1)
    P2 = emesh.find_node(pt2)
    P3 = emesh.find_node(pt3)
    P4 = emesh.find_node(pt4)
    S_dict={'freq':[]}
    for i in range(4):
        for j in range(4):
            S_dict['S{0}{1}'.format(i + 1, j + 1)]  =[]
    for freq in freqs:
        emesh.f=freq/1000
        emesh.update_trace_RL_val()
        emesh.update_C_val()

        circuit = Circuit()
        circuit.assign_freq(freq)

        circuit.comp_mode = 'val'
        circuit._graph_read(emesh.graph)
        emesh.update_mutual()
        circuit.m_graph_read(emesh.m_graph)
        #print P1,P2,P3,P4
        #P5 = emesh.find_node(pt5)
        circuit._graph_add_comp('C100',1,29, 68e-12)
        #circuit._graph_add_comp('R100', 1, 29, 0.4e8)
        circuit._graph_add_comp('C300', 2, 24, 34e-12)
        #circuit._graph_add_comp('R300', 2, 24, 0.2e8)

        circuit._graph_add_comp('C400', 2, 25, 34e-12)
        #circuit._graph_add_comp('R400', 2, 25, 0.2e8)

        circuit._graph_add_comp('C500', 3, 26, 34e-12)
        #circuit._graph_add_comp('R500', 3, 26, 0.2e8)

        circuit.Rport=50
        S_mat=circuit._compute_S_params(ports=[P1,P2,P3,P4],emesh=emesh,plot=False,mode='mag')
        S_dict['freq'].append(freq)
        for i in range(4):
            for j in range(4):
                S_dict['S{0}{1}'.format(i + 1, j + 1)].append(S_mat[i, j])
    legends=[]
    for i in range(4):
        for j in range(4):
            plt.semilogx(freqs, S_dict['S{0}{1}'.format(i + 1, j + 1)])
            legends.append('S{0}{1}'.format(i+1,j+1))
    plt.legend(legends)

    plt.show()

    with open('spara3.csv', 'wb') as data:
        w = csv.writer(data)
        w.writerow(S_dict.keys())
        for i in range(len(freqs)):
            row = []
            for k in S_dict.keys():
                print S_dict[k]
                row.append(S_dict[k][i])
            w.writerow(row)


def test_layer_stack_ushape():

    freqs = [10, 21.544, 46.415, 100, 215.443, 464.159, 1000]
    for freq in freqs:
        es = E_stack(file="C:\Users\qmle\Desktop\Documents\Conferences\IWIPP\ELayerStack//3_layers.csv")
        es.load_layer_stack()
        pr = cProfile.Profile()
        pr.enable()
        R1 = Rect(4, 0, 0, 20)
        R2 = Rect(16, 4, 16, 20)
        R3 = Rect(20, 16, 0, 20)
        rects = [R1, R2, R3]
        plates = [E_plate(rect=r, z=1.68, dz=0.2) for r in rects]
        R4 = Rect(30, -10, -10, 30)
        layer2 = [R4]
        #for r in layer2:
        #    plates.append(E_plate(r, z=0.84, dz=0.2))
        R5 = Rect(4, 0, 0, 20)
        R6 = Rect(16, 4, 16, 20)
        R7 = Rect(20, 16, 0, 20)
        rects1 = [R5, R6, R7]

        plates  +=[E_plate(rect=r, z=0, dz=0.2) for r in rects1]
        #print len(plates)
        new_module = E_module(plate=plates,layer_stack=es)
        new_module.form_group()
        new_module.split_layer_group()

        hier = Hier_E(module=new_module)
        hier.form_hierachy()
        emesh = ElectricalMesh(hier_E=hier, freq=freq,mdl_name= '3d_ushape.rsmdl')
        emesh.mesh_grid_hier(Nx=4, Ny=4)
        #fig = plt.figure(1)
        #ax = a3d.Axes3D(fig)
        #ax.set_xlim3d(-10, 35)
        #ax.set_ylim3d(-10, 35)
        #ax.set_zlim3d(-1, 2)
        #emesh.plot_3d(fig=fig, ax=ax)

        #plt.show()
        circuit = Circuit()
        if freq != 0:
            emesh.update_mutual()
        circuit.comp_mode = 'val'
        circuit._graph_read(emesh.graph)
        circuit.m_graph_read(emesh.m_graph)
        pt1 = (0, 2, 1.68)
        pt2 = (0, 18, 1.68)
        pt3 = (0, 2, 0)
        pt4 = (0, 18, 0)
        src1 = emesh.find_node(pt1)
        sink1 = emesh.find_node(pt2)
        src2 = emesh.find_node(pt3)
        sink2 = emesh.find_node(pt4)
        circuit.assign_freq(freq * 1000)
        circuit.Rport = 50

        #circuit._assign_vsource(src1, vname='Vs1', volt=1)
        #circuit._add_ports(sink1)
        #circuit._add_ports(sink2)

        #circuit.build_current_info()
        print freq,'kHz'
        #circuit.solve_iv()
        #print circuit._compute_imp(src1, sink1, sink1)
        #circuit._compute_matrix([src1], [sink1])

        circuit._compute_matrix([src1, src2], [sink1, sink2])
        '''
        all_I = []
        result = circuit.results
        for e in emesh.graph.edges(data=True):
            edge = e[2]['data']
            edge_name = edge.name
            width = edge.data['w'] * 1e-3
            thick = edge.thick * 1e-3
            A = width * thick
            I_name = 'I_L' + edge_name
            edge.I = np.real(result[I_name])
            edge.J = edge.I / A
            all_I.append(abs(edge.J))
        I_min = min(all_I)
        I_max = max(all_I)
        normI = Normalize(0, 15000)

        fig = plt.figure(2)
        ax = fig.add_subplot(111)
        plt.xlim([0, 20])
        plt.ylim([0, 20])
        plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=1.68, mode='J',
                                         W=[0, 20],
                                         H=[0, 20], numvecs=31)
        plt.show()
        '''
        #fig = plt.figure(3)
        #ax = fig.add_subplot(111)
        #plt.xlim([0, 20])
        #plt.ylim([0, 20])
        #plot_combined_I_quiver_map_layer(norm=normI, ax=ax, cmap=emesh.c_map, G=emesh.graph, sel_z=1.68, mode='J',
        #                                 W=[0, 20],
        #                                 H=[0, 20], numvecs=31)
        #circuit.solve_iv()
        #circuit.solve_iv_hspice(filename='ushape.sp',
        #                        env=os.path.abspath('C:\synopsys\Hspice_O-2018.09\WIN64\hspice.exe'))

        #circuit.results = circuit.hspice_result
        #print "freq", freq, "model", circuit._compute_imp(src1, sink1, sink1)

if __name__ == '__main__':
    #test_mutual()
    # test_hier2()
    #test_Ushape()
    S_para_IWIPP()
    #test_layer_stack_ushape()
    #test_layer_stack_mutual()
    #balance_study()
    #test_3d_module()
    # test_single_trace_mesh()