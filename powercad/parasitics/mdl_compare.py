import math
import pickle 
from pykrige.ok import OrdinaryKriging as ok
import math as m
from math import fabs
import os
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import lines
LOWEST_ASPECT_RES = 1.0         # I changed it back to 1.0 Quang as stated in Brett's thesis
LOWEST_ASPECT_IND = 1.0
# Constants:
c = 3.0e8                       # speed of light
u_0 = 4.0*math.pi*1e-7          # permeability of vaccum;
e_0 = 8.85e-12                  # permittivity of vaccum;

#-------------------------------------------Zihao's model--------------------------------------------------------------#
def trace_resistance(f, w, l, t, h, p=1.724e-8):
    # f: Hz (AC frequency)
    # w: mm (trace width, perpendicular to current flow)
    # l: mm (trace length, parallel to current flow)
    # t: mm (trace thickness)
    # h: mm (height of trace above ground plane)
    # p: Ohm*meter (trace resistivity)
    
    w = fabs(w)
    l = fabs(l)
    #if w > l*LOWEST_ASPECT_RES:
    #    w = l*LOWEST_ASPECT_RES
    
    u0 = 1.257e-6               # permeability of vaccum;
               
    t1 = t*1e-3                 # transfer to unit in m;
    w1 = w*1e-3                 # transfer to unit in m;
    h1 = h*1e-3                 # transfer to unit in m;
    l1 = l*1e-3                 # transfer to unit in m;
    
    # resistance part of trace (trace resistance + ground plane resistance): 
    LR = 0.94 + 0.132*(w1/h1) - 0.0062*(w1/h1)*(w1/h1)
    R0 = math.sqrt(2.0*math.pi*f*u0*p)
    comp1 = (l1*R0)/(2.0*math.pi*math.pi*w1)
    comp2 = math.pi + math.log((4.0*math.pi*w1)/t1)
    
    # resistance calculation:
    r = LR*comp1*comp2*1e3 # unit in mOhms
    
    # Zihao's old code (this may be wrong, not sure) -Brett
    # r = LR*(1/math.pi + 1/math.pow(math.pi, 2)*math.log(4*math.pi*w1/t1))*math.sqrt(math.pi*u0*f*p)/(math.sqrt(2)*w1)*l1*1e3 # unit in mOhms
    
    if r <= 0.0:
        r = 1e-6
    
    # returns resistance in milli-ohms
    return r


def trace_inductance(w, l, t, h):  # see main for unit test --Quang
    # Corrected by Brett Shook 2/26/2013
    # w: mm (trace width, perpendicular to current flow)
    # l: mm (trace length, parallel to current flow)
    # t: mm (trace thickness)
    # h: mm (height of trace above ground plane)

    # if this condition is broken,
    # the isolated bar inductance
    # problem will give bad results
    # In this case, lengthen the piece,
    # and return a larger worst case value.
    w = fabs(w)
    l = fabs(l)

    if w > l * LOWEST_ASPECT_IND:
        w = l * LOWEST_ASPECT_IND

    w1 = w * 1e-3  # transfer to unit in m;
    h1 = h * 1e-3  # transfer to unit in m;
    t1 = t * 1e-3  # transfer to unit in m;
    l1 = l * 1e-3  # transfer to unit in m;

    u_r = 1.0  # relative permeability of the isolation material
    e_r = 8.8  # relative permittivity of the isolation material;    <----------------   Why ??????? no inputs

    # effective dielectric permittivity and effective width:
    w_e = w1 + 0.398 * t1 * (1.0 + math.log(2.0 * h1 / t1))
    e_eff = ((e_r + 1.0) / 2.0) + ((e_r - 1.0) / 2.0) * math.pow(1.0 + 12.0 * h1 / w_e, -0.5) - 0.217 * (
    e_r - 1.0) * t1 / (math.sqrt(w_e * h1))

    # micro-strip impedance:
    C_a = e_0 * (w_e / h1 + 1.393 + 0.667 * math.log(w_e / h1 + 1.444))
    z0 = math.sqrt(e_0 * u_0 / e_eff) * (1 / C_a)

    # inductance calculation of microstrip:
    Ind_0 = l1 * z0 * math.sqrt(u_r * e_eff) / c  # Equation 3.9 page 42 Zihao's thesis
    Ind_0 *= 1e9  # unit in nH

    # inductance calculation of isolated rectangular bar trace
    try:
        Ind_1 = u_0 * l1 / (2.0 * math.pi) * (
        math.log(2.0 * l1 / (w1 + t1)) + 0.5 + (2.0 / 9.0) * (w1 + t1) / l1)  # Equation 3.4 page 41 in Zihao's thesis
    except:
        Ind_1 = 10000
    Ind_1 *= 1e9  # unit in nH

    # averaged model for inductance calculation:
    Ind = 0.5 * (Ind_0 + Ind_1)

    if Ind <= 0.0:
        if Ind_0 > 0.0:
            Ind = Ind_0
        elif Ind_1 > 0.0:
            Ind = Ind_1
        else:
            Ind = 1e-6
    # returns inductance in nano-Henries
    return Ind


def trace_capacitance(w, l, t, h, k=8.8):
    # w: mm (trace width, perpendicular to current flow)
    # l: mm (trace length, parallel to current flow)
    # t: mm (trace thickness)
    # h: mm (height of trace above ground plane)
    # k: (no unit) (relative dielectric constant (permittivity) of the isolation material)

    w1 = w * 1e-3  # transfer to unit in m;
    h1 = h * 1e-3  # transfer to unit in m;
    l1 = l * 1e-3  # transfer to unit in m;
    t1 = t * 1e-3  # transfer to unit in m;

    # effective distance between trace and ground plane:
    h1_eff = (2.0 * h1 + t1) / 2.0

    # effective area of fringe capacitance:
    A = 2.0 * t1 * (w1 + l1)

    # effective dielectric constant:
    try:
        keff = (k + 1.0) / 2.0 + ((k - 1.0) / 2.0) * math.pow(1.0 + (12.0 * h1) / w1, -0.5) - 0.217 * (
        k - 1.0) * t1 / math.sqrt(w1 * h1)  # equation 3.18 page 50 from Zihao's thesis
    except:
        return 10000
    # sum of parallel plate and fringe capacitance
    c = k * e_0 * (w1 * l1) / h1 + keff * e_0 * A / h1_eff  # equation 3.19 page 50 from Zihao's thesis
    c *= 1e12  # unit in pF
    if c <= 0.0:
        c = 1e-6

    return c
def load_mdl(dir,mdl_name):
    mdl=pickle.load(open(os.path.join(dir,mdl_name),"rb"))
    print "model loaded"
    return mdl

def trace_res_krige(f,w,l,mdl):
    #unit is uOhm
    model = mdl.model[0]
    op_freq=mdl.op_point
    r=model.execute('points',[w],[l])
    r=np.ma.asarray(r[0])
    return r*m.sqrt(f/op_freq)

def trace_ind_krige(f,w,l,mdl):
    # unit is nH
    n_params=len(mdl.input)
    params=[]
    for i in range(n_params):
        params.append(np.ma.asarray((mdl.model[i].execute('points',w,l)))[0])
    l=mdl.sweep_function(f,params[0],params[1])
    return l

def trace_cap_krige(w,l,mdl):
    # unit is pF
    model=mdl.model[0]
    c=model.execute('points',[w],[l])   
    c=np.ma.asarray(c[0])

    return c

if __name__ == '__main__':
    mdl_dir='D:\Testing\Py_Q3D_test\All rs models'
    mdl1=load_mdl(mdl_dir,'RAC_mesh_100_krige.rsmdl')
    DOE=mdl1.DOE
    Q3D_R=mdl1.input[0]
    print mdl1.unit.to_string()
    print Q3D_R # uOhm
    mdl2 = load_mdl(mdl_dir, 'Mdl2.rsmdl')
    Q3D_L=mdl2.input[0]
    mdl2=load_mdl(mdl_dir, 'LAC_mesh_100_krige.rsmdl')
    print mdl2.op_point
    print Q3D_L # nH
    mdl3=load_mdl(mdl_dir,'C_mesh_100_krige.rsmdl')
    Q3D_C=mdl3.input[0]
    print Q3D_C # pF

    w=[]
    l=[]

    for i in range(10):
        for j in range (10):
            w.append(float(i))
            l.append(float(j))
    time1 = time.time()
    a = trace_res_krige(20, w, l, mdl1)
    b = trace_ind_krige(20,w,l,mdl2)
    c = trace_cap_krige(w,l,mdl3)
    time2=time.time()
    print 'Krigging time',time2-time1
    time2=time.time()
    print time2
    for i in range(100):
        n=trace_resistance(20000, 10, 20, 0.2, 0.5)*1000

    print 'Microstrip time', time.time()
    print trace_resistance(20000, 1, 20, 0.2, 0.5)*1000
    # Compare Q3D resistance with microstrip 
    '''
    # plot Q3D vs Microstrip resistance
    fig1 = plt.figure(0)
    ax = fig1.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_resistance(110000, X_2[j], X_2[i], 0.2, 0.5)*1000
    surf1 = ax.plot_surface(X1, Y1, Z1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    ax.scatter(DOE[:,0], DOE[:,1], Q3D_R, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Resistance (uOhm)')
    
    # plot Q3D vs Microstrip inductance
    
    fig2 = plt.figure(1)
    ax = fig2.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_inductance(X_2[j], X_2[i], 0.2, 0.5)
    surf2 = ax.plot_surface(X1, Y1, Z1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    ax.scatter(DOE[:,0], DOE[:,1], Q3D_L, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Inductance (nH)')
    
    # plot Q3D vs Microstrip Capacitance
    
    fig3 = plt.figure(2)
    ax = fig3.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_capacitance(X_2[j], X_2[i], 0.2, 0.5)
    surf2 = ax.plot_surface(X1, Y1, Z1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    ax.scatter(DOE[:,0], DOE[:,1], Q3D_C, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Capacitance (pH)')
    
    scatter1_proxy = lines.Line2D([0], [0], linestyle='none', c='r', marker='o')
    scatter2_proxy = lines.Line2D([0], [0], linestyle='none', c='b', marker='o')
    ax.legend([scatter1_proxy, scatter2_proxy], ['Q3D', 'Microstrip'], numpoints=1)
    fig1.suptitle('Q3D vs Microstrip Resistance', fontsize=20)
    fig2.suptitle('Q3D vs Microstrip Inductance', fontsize=20)
    fig3.suptitle('Q3D vs Microstrip Capacitance', fontsize=20)
    plt.show()
    
    # plot Q3D vs RS resistance
    fig4 = plt.figure(3)
    ax = fig4.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_res_krige(110,X_2[j], X_2[i], mdl_dir, 'RAC_mesh_100_krige.rsmdl')
    surf1 = ax.plot_surface(X1, Y1, Z1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    ax.scatter(DOE[:,0], DOE[:,1], Q3D_R, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Resistance (uOhm)')
    
    fig5 = plt.figure(4)
    ax = fig5.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_ind_krige(110,X_2[j], X_2[i], mdl_dir, 'LAC_mesh_100_krige.rsmdl')
    surf2 = ax.plot_surface(X1, Y1, Z1, cmap=cm.jet,linewidth=0, antialiased=False)
    ax.set_zlim(0, 1.01)
    #ax.scatter(DOE[:,0], DOE[:,1], Q3D_L, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Inductance (nH)')
    
    fig6 = plt.figure(5)
    ax = fig6.gca(projection='3d')
    X_1=np.linspace(1.2,20,10)
    Y_1=np.linspace(1.2,20,10)
    X,Y=np.meshgrid(X_1,Y_1)
    Z=np.zeros((10,10))
    
    Z1=np.zeros((10,10))
    X_2=np.linspace(1.2,20,10)
    Y_2=np.linspace(1.2,20,10)
    X1,Y1=np.meshgrid(X_2,Y_2)
    for i in range(10):
        for j in range(10):
            Z1[i,j]=trace_cap_kridge(X_2[j], X_2[i], mdl_dir, 'C_mesh_100_krige.rsmdl')
    surf3 = ax.plot_surface(X1, Y1, Z1, cmap=cm.coolwarm,linewidth=0, antialiased=False)
    ax.scatter(DOE[:,0], DOE[:,1], Q3D_C, c='r',s=10)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Length (mm)')
    ax.set_zlabel('Capacitance (pF)')
    scatter1_proxy = lines.Line2D([0], [0], linestyle='none', c='r', marker='o')
    scatter2_proxy = lines.Line2D([0], [0], linestyle='none', c='b', marker='o')
    ax.legend([scatter1_proxy, scatter2_proxy], ['Q3D', 'Response Surface'], numpoints=1)
    
    fig4.suptitle('Q3D vs Response Surface', fontsize=20)
    fig5.suptitle('Q3D vs Response Surface', fontsize=20)
    fig6.suptitle('Q3D vs Response Surface', fontsize=20)
    
    plt.show()

   '''
    
