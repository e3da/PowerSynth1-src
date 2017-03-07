'''
@author: Quang Le
This is only a trial version before pluggin version for PowerSynth
The main reason we develop this model is for our 2016 COMPEL conference in Norway
'''
'''In this model, we will show how PowerSynth can predict accurately the operating conditions of the devices with Vdd and VG input
Source: http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=6631982 '''
'''Inputs for this model'''
'''Simulation result from parasitic netlist with MOSFET model -> estimate ID and VDD at different temp --> extrapolating to create a simple function of temp, Idd and Vdd'''
'''Switching frequency to estimate Eon and Eoff'''
'''
Approximations are made:
1st: no parasitic effect from the circuit is considered. 
2nd: The users have to choose a fixed VGS based on the data sheet, so that there is no changes in RDSon vs VGS 
3rd: Material characteristics are fixed with temperature changes. In reality they are calculated based on Temp
4th: For Eon and Eoff, there is a minimal connection with Temp, ---> need more research
'''
'''
Example form will be connected to the new button inside of Graphene window, see graph_app.py
'''
'''
Words from author: I am trying my best to document every single line of code, please do the same when you add a new model to PowerSynth
Recommendation from Tom: we might be able to interface this with C,C++,Java code which make it more efficient 
'''
'''@Python Packages'''
import control as ct
import time
import numpy as np
import os
import csv
import repr
import scipy
import math
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import operator
from matplotlib import colors
from scipy.optimize import curve_fit
'''@PowerSynth Packages'''
from powercad.sym_layout.plot import plot_layout
from powercad.spice_export.thermal_netlist_graph import Module_Full_Thermal_Netlist_Graph

'''Additional Function'''

def list2float(data):
        fdata=[]
        for i in range(len(data)):
            fdata.append(float(data[i]))
        return fdata

'''Main Class'''    
class STMDL():
    def __init__(self,symbolic_layout):
        '''Electrical variables: added as the inputs of constructor'''
        '''Values below might be changed or interfaced with P.S now they are just hard-coded'''
        '''Below show the parameter for user input. For testing its just a fixed value now, we will decide how to interface later'''
        '''Information from CPMF 1200-S0080B datasheet'''
        self.vds_crss = 10  # Look at the value in C-V characteristic, this is the voltage at which the CRSS curve changing from a line to a parabolic form
        self.f_sw = 20e3
        self.Tref = 25
        self.Tamb = 300
        self.ID = 60  # A
        self.VDD = 800  # V
        self.Qrr = 192e-9
        self.RG = 1
        self.Vg = 16
        self.Ciss = 1e-9
        self.Vpl = 6


def csv_load(filedes, filename, tuple):
    lists = [[] for i in range(len(tuple))]
    temp = open(os.path.join(filedes, filename), 'rb')
    tempdata = csv.DictReader(temp)
    for row in tempdata:
        for i in range(len(row)):
            lists[i].append(row[tuple[i]])
    return lists

def csv_load_file(filedir, tuple):
    lists = [[] for i in range(len(tuple))]
    temp = open(filedir, 'rb')
    tempdata = csv.DictReader(temp)
    for row in tempdata:
        for i in range(len(row)):
            lists[i].append(row[tuple[i]])
    return lists
def Eon(vdd, id, tri, tfv, Qrr):
    return vdd * id * (tri + tfv) / 2 + Qrr * vdd


def Eoff(vdd, id, trv, tfi):
    return vdd * id * (trv + tfi) / 2


def Psw_eval(Eon, Eoff, fsw):
    return (Eon + Eoff) * fsw


def rdson_eval_transistor(Tj, alpha, Ro):  # per unit curve
    Tref=27
    return (alpha * (Tj - Tref) + 1) * Ro


def rdson_fit_transistor(xdata, ydata):
    '''
    Return a list of parameters for rdson_eval_transistor
    '''
    popt, pcov = curve_fit(rdson_eval_transistor, xdata, ydata)
    [alpha, Ro] = popt
    return [alpha, Ro]


def fCRSS(Vds, a1, b1, c1, a2, b2, c2):
    return np.piecewise(Vds, [Vds < 12],
                        [lambda Vds: a1 * Vds ** 2 + b1 * Vds + c1, lambda Vds: a2 * Vds ** 2 + b2 * Vds + c2])


def fCRSS_fit(volt, cap):
    CRSS_volts = volt
    CRSS_raw = cap
    popt, pcov = curve_fit(fCRSS, CRSS_volts, CRSS_raw)
    [a1, b1, c1, a2, b2, c2] = popt  # using fCoss
    print 'Crss Fitting Error: '
    return [a1, b1, c1, a2, b2, c2]


def Vth(T, a, b):
    return a * T + b


def Vth_fit(temp, volt):
    popt, pcov = curve_fit(Vth, temp, volt)
    return popt


def curve_fitting_all(filedes, rds_fn, crss_fn, vth_fn):
    '''
    Curve fitting all the required graph and return a list of parameters
    '''
    
    fd = filedes
    tuple = ['Tj', 'Rds']
    rds_data = csv_load(filedes, rds_fn, tuple)
    [alpha, Ro] = rdson_fit_transistor(list2float(rds_data[0]), list2float(rds_data[1]))
    tuple = ['Vds', 'Cap']
    crss_data = csv_load(filedes, crss_fn, tuple)
    print crss_data[0]
    print crss_data[1]
    [a1, b1, c1, a2, b2, c2] = fCRSS_fit(list2float(crss_data[0]), list2float(crss_data[1]))
    tuple = ['Tj', 'Vth']
    Vth_dat = csv_load(filedes, vth_fn, tuple)
    [a, b] = Vth_fit(list2float(Vth_dat[0]), list2float(Vth_dat[1]))
    parameters = [alpha, Ro, a1, b1, c1, a2, b2, c2, a, b]
    return parameters


def ptot_all(T_list, parameters):
    p_all = []
    for T in T_list:
        p_all.append(ptot_compute_single(T, parameters))
    return p_all


def ptot_compute_single(T, parameters):
    '''
    This model using the estimated value of I and V for every single dies, and the
    temperature from previous stages to estimate the new power disipation. This required extra inputs from data sheet,
    and some initial curve fitting algorithm (Least Square method)
    inputs: Estimated Current through each die
            Estimated Bus voltage of the Half Bridge
            Temperature from last stage for a die
    output: Power Dissipation for a die
    '''
    T = T - 273
    num_island = max(self.r_parent)
    num_dies = max(self.r_id)
    ''' Control parameters'''
    ''' Rds params'''
    alpha = parameters[0]
    Ro = parameters[1]
    ''' CGD or CRSS parameters'''
    a1 = parameters[2]
    b1 = parameters[3]
    c1 = parameters[4]
    a2 = parameters[5]
    b2 = parameters[6]
    c2 = parameters[7]
    a = parameters[8]
    b = parameters[9]
    ''' User's inputs'''
    Id = self.ID / (num_dies / num_island)
    Vdd = self.VDD
    Qrr = self.Qrr
    Rg = self.RG
    Vgson = self.Vg
    Ciss = self.Ciss
    Vpl = self.Vpl
    ''' First Vds is approximate using the new rdson'''
    rds = self.rdson_eval_transistor(T, alpha, Ro)
    # print 'rds: ' +str(rds)
    Vds = Id * rds
    ''' Compute Power Conduction'''
    Pcond = Vds * Id  # ignore parasitic effect for now
    # print 'Power conduction:' +str(Pcond) + 'at T: ' + str(T)
    ''' Compute Eon'''
    '''Find Vth'''
    Vth = self.Vth(T, a, b)
    # print 'Vth: ' + str(Vth)
    '''Find Qgd'''
    Qgd = self.fCRSS(Vds, a1, b1, c1, a2, b2, c2) * (Vdd - Vds)
    # print 'Qgd is: ' +str(Qgd)
    '''Find IGoff and IGon'''
    Igoff = Vpl / Rg
    Igon = (Vgson - Vpl) / Rg
    '''Find rising time for current, falling time for voltage '''
    tri = Rg * Ciss * np.log((Vgson - Vth) / (Vgson - Vpl))
    tfv = Qgd / Igon
    # print 'current rising time: '+ str(tri) +' voltage falling time: '+ str(tfv)
    Eon = self.Eon(Vdd, Id, tri, tfv, Qrr)
    # print 'Eon: ' +str(Eon)
    ''' Compute Eoff'''
    '''Find falling time for current, rising time for voltage '''
    trv = Qgd / Igoff
    tfi = Rg * Ciss * np.log(Vpl / Vth)
    # print 'current falling time: '+ str(tfi) +' voltage rising time: '+ str(trv)
    Eoff = self.Eoff(Vdd, Id, trv, tfi)
    # print 'Eoff: ' +str(Eoff)
    # Compute the total power using parameters list
    # this is just the map how to do it. Remember it is a list of signal so need to call this in another function
    # Only half of the cycle is taken care of now. (50% D)
    Psw = self.Psw_eval(Eon, Eoff, self.f_sw)
    Pave = (Pcond * (1 / (2 * self.f_sw) - tri - tfv - trv - tfi)) / (1 / (self.f_sw * 2)) + (Eon + Eoff) * self.f_sw
    if T == 27:
        print 'Temp: ' + str(T) + ' Conduction loss: ' + str(Pcond) + ' Switching loss: ' + str(Psw)
    if T > 126 and T < 127:
        print 'Temp: ' + str(T) + ' Conduction loss: ' + str(Pcond) + ' Switching loss: ' + str(Psw)
    if T > 225 and T < 226:
        print 'Temp: ' + str(T) + ' Conduction loss: ' + str(Pcond) + ' Switching loss: ' + str(Psw)
        # print 'total loss: ' + str(Ptot)
    print Pave
    return Pave


def Pcond_eval(self, Id_list, Vds_list, Ton, list=True):
    '''
    This method integrate through the list of Id-Vds output to compute power conduction
    Ton: simulation time
    Id_list: list of Id in 1 period
    Vds_list: list of Vd in 1 period
    If list is false, this function is used for approximation value of ID,VDS
    '''
    if list:  # simulation case
        Pcond = []
        for i in np.arange(0, len(Id_list), 1):
            Pcond.append(Id_list[i] * Vds_list[i])
        Power_cond = sum(Pcond) / float(Ton)
    else:  # no simulation case
        Power_cond = Id_list * Vds_list
    return Power_cond


'''---------------------------CODE under maintenance ---------------------------------------------------------------'''
'''These functions below are still connected to PowerSynth, DONT delete///'''
class ET_analysis():
    '''Constructor - Need to redefined, depends on how you want to interface it. Now I keep it as simple as possible'''
    def __init__(self,thermal_netlist_graph):
        '''True False list, whether the list of data is not provided from data sheet. If not estimation will be made'''
        self.Vth_list=True
        '''Thermal variable '''
        self.thermal_module=thermal_netlist_graph
        self.thermal_res=thermal_netlist_graph.thermal_res
        self.thermal_cap=thermal_netlist_graph.thermal_cap
        self.r_val=[]
        self.r_type=[]
        self.r_id=[]
        self.r_parent=[]
        self.c_val=[]
        self.c_type=[]
        self.c_id=[]
        self.c_parent=[]
        self.Rdie=[]
        self.Risl=[]
        self.Cdie=[]
        self.Cisl=[]
        self.Rsub={}
        self.Csub={}
        '''Electrical variables: added as the inputs of constructor'''
        '''Values below might be changed or interfaced with P.S now they are just hard-coded'''
        '''Below show the parameter for user input. For testing its just a fixed value now, we will decide how to interface later'''
        '''Information from CPMF 1200-S0080B datasheet'''
        self.vds_crss=10# Look at the value in C-V characteristic, this is the voltage at which the CRSS curve changing from a line to a parabolic form
        self.f_sw=20e3
        self.Tref=25
        self.Tamb=300
        self.ID=60 #A
        self.VDD=800 # V
        self.Qrr=192e-9
        self.RG=1
        self.Vg=16
        self.Ciss=1e-9
        self.Vpl=6
        '''
        
        '''
        #thermal_mdl=self.ET_formation_1(self.f_sw)
        
        #self.ptot_compute_single(300-273, parameters)
        '''
        Testing simulation
        '''
        
        
        #self.runsim_init(thermal_mdl,16.9)
        #self.Run_sim(thermal_mdl , parameters, 300000)
        
    def Run_sim(self,Thermal_model,parameters,cycles):
        starttime=time.time()
        num_island=max(self.r_parent)
        num_dies=max(self.r_id)
        side=num_island+num_dies+1  
        '''First we create initial conditions for all layers, this is just the ambient temperature'''
        To=np.ones((side,1))
        To=self.Tamb*To
        To=np.asarray(To)
        s_power=time.time()
        Po=self.ptot_all(To[0:num_dies], parameters)
        self.sucessive_approximation(Po, parameters)
        t_power=time.time()-s_power
        print 'power computation time '+str(t_power)
        print 'initial power dissipation'   
        print Po
        die1=[]
        die2=[]
        die3=[]
        die4=[]
        die5=[]
        die6=[]
        die7=[]
        die8=[]
        die9=[]
        die10=[]
        die11=[]
        die12=[]
        isl1=[]
        isl2=[]
        P_list=[]
        T_list=[]
        for i in range(cycles):
            if i==0:
                [Input,Time]=self.form_inputs(Po,6)
                Time, Temp, xout = ct.forced_response(Thermal_model,Time,Input,To) 
                #print 'New Temp'
                Temp_next=Temp[:,5]
                P_next=self.ptot_all(Temp_next[0:num_dies], parameters)
                #print 'Next Power dissipation'
                #print P_next
            else:
                P_list.append(P_next[8])
                die1.append(Temp[0,:].tolist())
                die2.append(Temp[1,:].tolist())
                die3.append(Temp[2,:].tolist())
                die4.append(Temp[3,:].tolist())
                die5.append(Temp[4,:].tolist())
                die6.append(Temp[5,:].tolist())
                die7.append(Temp[6,:].tolist())
                die8.append(Temp[7,:].tolist())
                die9.append(Temp[8,:].tolist())
                die10.append(Temp[9,:].tolist())
                die11.append(Temp[10,:].tolist())
                die12.append(Temp[11,:].tolist())
                isl1.append(Temp[num_dies,:].tolist())
                [Input,Time]=self.form_inputs(P_next,6)
                Time, Temp, xout = ct.forced_response(Thermal_model,Time,Input,Temp_next) 
                #print 'New Temp'
                #print Temp
                Temp_next=Temp[:,5]
                T_list.append(Temp_next[8])
                if math.isnan(Temp_next[8]):
                    break
                P_next=self.ptot_all(Temp_next[0:num_dies], parameters)
                #print 'Next Power dissipation'
                #print P_next
        simtime=time.time()-starttime
        print 'simulation time:'
        print simtime
        die1=list(itertools.chain.from_iterable(die1))
        die2=list(itertools.chain.from_iterable(die2))
        die3=list(itertools.chain.from_iterable(die3))
        die4=list(itertools.chain.from_iterable(die4))
        die5=list(itertools.chain.from_iterable(die5))
        die6=list(itertools.chain.from_iterable(die6))
        die7=list(itertools.chain.from_iterable(die7))
        die8=list(itertools.chain.from_iterable(die8))
        die9=list(itertools.chain.from_iterable(die9))
        die10=list(itertools.chain.from_iterable(die10)) 
        die11=list(itertools.chain.from_iterable(die11))
        die12=list(itertools.chain.from_iterable(die12))
        #print temp_change     
        max_temp=max(Temp_next)
        max_P=max(P_next)  
        Time_list=np.arange(0,len(die9),1)*1/(4*self.f_sw)
        Time_power= np.arange(0,len(P_list),1)*1/(self.f_sw)
        print len(Time_list)
        #print len(Temp_list)
        fig=plt.figure()
        ET= fig.add_subplot(1,1,1)
        c=[]
        for color in colors.cnames.keys():
            c.append(color)
        ET.set_xlabel('Time (s)')
        ET.set_ylabel('Temperature (C)')
        die9=[x-273 for x in die9]
        ET.plot(Time_list,die11,color=c[0], lw=1)
        #ET.plot(Time_list,die2,color=c[1], lw=1) 
        #ET.plot(Time_list,die3,color=c[2], lw=1)
        #ET.plot(Time_list,die4,color=c[3], lw=1)
        #ET.plot(Time_list,die5,color=c[4], lw=1)
        #ET.plot(Time_list,die6,color=c[5], lw=1)
        #ET.plot(Time_list,die7,color=c[6], lw=1)
        #ET.plot(Time_list,die8,color=c[7], lw=1)
        #ET.plot(Time_list,die9,color=c[8], lw=1)
        #ET.plot(Time_list,die10,color=c[9], lw=1)  
        #ET.plot(Time_list,die11,color=c[10], lw=1)
        #ET.plot(Time_list,die12,color=c[11], lw=1)
        plt.show() 
        fig=plt.figure()
        PowervsTemp=fig.add_subplot(1,1,1)
        PowervsTemp.set_xlabel('Temperature (C)')
        PowervsTemp.set_ylabel('Power (W)')
        T_list=[x-273 for x in T_list]
        PowervsTemp.plot(T_list,P_list,color=c[0],lw=3)
        plt.show() 
        plt.show() 
        fig=plt.figure()
        PowervsTime=fig.add_subplot(1,1,1)
        PowervsTime.set_xlabel('Time (s)')
        PowervsTime.set_ylabel('Power (W)')
        PowervsTime.plot(Time_power,P_list,color=c[0],lw=3)
        plt.show() 
        print 'Min Power: '+str(max(Po))
        print 'Max Power: '+str(max_P) 
        print 'Mean Power:'+str(np.mean(P_list))
        print 'Max Temp:' +str(max_temp)
        print 'Time: '+ str(Time)
                
    def form_inputs(self,powerlist,samples):
        num_dies=max(self.r_id)
        row=max(self.r_id)+1
        sp=samples    # Number of Samples
        if sp%2==1:
            sp=sp+1 # Make the number of sample even so that its easier to generate the input
        T=np.arange(0,1/self.f_sw,1/(sp*self.f_sw))
        col=len(T)
        
        U=np.zeros((row,col),dtype=np.float64)
        for k in np.arange(0,col,1):
            for i in np.arange(0,num_dies,1):
                P=powerlist[i]
                if k< sp/2:
                    P=powerlist[i]
                else:
                    P=0       
                U.itemset((i,k),P)
                U.itemset(num_dies,k,self.Tamb)
        #print T
        return [U,T]
                            
    def runsim_init(self,model,p_const):
        '''
        Simple simulation with constant Power dissipation to test speed 
        '''
        start=time.time()
        u=self.input_simple(p_const)
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        side=num_island+num_dies+1          
        xo=np.ones((side,1))
        xo=self.Tamb*xo
        xo=np.asarray(xo)
        [U,T]=self.form_switching_sample(u,300000,aver=False)
        Tout, yout, xout = ct.forced_response(model, T, U,xo)
        stop=time.time()-start
        print 'total time: ' +str(stop)
        ydraw= yout.tolist()
        ydraw=ydraw[:,199999]
        
        
        return ydraw[:,199999]
         
    def form_switching_sample(self,u,cycle,aver=False):
        f_sw=self.f_sw
        T=np.arange(0,cycle/f_sw,1/f_sw)
        T=np.asarray(T) 
        print T.shape
        side=max(self.r_id)+1
        U=np.zeros((side,cycle),dtype=np.float64)
        if aver==False:
            for i in range(cycle):
                if i%2==0:
                    U[:,i]=u.T
                else:
                    z=np.zeros((1,len(u)))
                    z.itemset((0,len(u)-1),self.Tamb)
                    U[:,i]=z 
        else:            
            for i in range(cycle):
                U[:,i]=u.T/2
        return [U,T]      
         
    def ET_formation_1(self,f_sw):
        '''
        This method will first load the thermal data in R and C network_x to compute the state space model for thermal
        estimation
        State Space model:
        T'=A*T + B*P(t) 
        y= C*T + D*P(t)
        A and B will be automatically computed based on the exported value
        # Load data from networkX_ for now utilize the Thermal Netlist model 
        # If we want to put this in NSGA, have to compute it directly to upgrade speed
        C is an Identity matrix 
        D is just a zero matrix with same dimension as B
        The method utilize control system tool box in Python check this link:
        http://python-control.readthedocs.io/en/latest/ '''

        for r_node in self.thermal_res.nodes(data=True):
            R=r_node[1].get('component')
            if R is not None:             # include all the sources and resistances
                if R.type=='res': 
                    self.r_val.append(R.value)
                    self.r_type.append(R.name[0:3])
                    self.r_id.append(int(R.name[3:len(R.name)]))
                    self.r_parent.append(R.parent)
                if R.type=='v_src':
                    self.Tamb=R.value    
        for c_node in self.thermal_cap.nodes(data=True):
            C=c_node[1].get('component')
            if C is not None:
                if C.type=='cap': 
                    self.c_val.append(C.value)
                    self.c_type.append(C.name[0:3])
                    self.c_id.append(int(C.name[3:len(C.name)]))
                    self.c_parent.append(C.parent)
        # Sort data and prepare to create state spaces matrix               
        r_sorted=np.array(self.r_id)
        inds = r_sorted.argsort()
        isl_sorted=np.array(self.r_parent)[inds]
        r_sorted=r_sorted[inds]
        r_type_sorted=np.array(self.r_type)[inds]
        r_val_sorted=np.array(self.r_val)[inds]
        c_sorted=np.array(self.c_id)[inds]
        c_type_sorted=np.array(self.c_type)[inds]
        c_val_sorted=np.array(self.c_val)[inds]
        # Put data in dictionary form
        for x,y,z,w in zip(r_sorted,r_type_sorted,r_val_sorted,isl_sorted):
            if y =='die':
                data={'id':x,'val':z,'isl':w}
                self.Rdie.append(data)      
            elif y=='isl':
                data={'id:':x,'val':z} 
                self.Risl.append(data)
            else:   
                data={'id:':x,'val':z} 
                self.Rsub=data        
        for x,y,z,w in zip(c_sorted,c_type_sorted,c_val_sorted,isl_sorted):
            if y =='die':
                data={'id':x,'val':z,'isl':w}
                self.Cdie.append(data)      
            elif y=='isl':
                data={'id:':x,'val':z} 
                self.Cisl.append(data)
            else:   
                data={'id:':x,'val':z} 
                self.Csub=data            
        a_mat=self.form_a_mat()
        b_mat=self.form_b_mat()
        # forming C matrix
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        side=num_island+num_dies+1
        c_mat=np.identity(side,np.float64)
        c_mat=np.asarray(c_mat)
        d_mat=np.zeros(b_mat.shape,dtype=np.float64) 
        d_mat=np.asarray(d_mat)
        thermal_model=ct.ss(a_mat,b_mat,c_mat,d_mat)
        return thermal_model

    def input_simple(self,p):  #simple way to test the setup with one input
        '''
        Matrix P formation:
         size= (num of dies + 1)x1 
         Here is an example with 2 dies
         'Pdie1'
         'Pdie2'
         'Tamb
        '''
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        side=num_dies+1  
        pdiss=np.zeros((side,1),dtype=np.float64)
        for i in np.arange(0,num_dies,1):
            pdiss.itemset(i,0,p)    
        pdiss.itemset(side-1,0,self.Tamb)  
        return pdiss

    def form_a_mat(self):
        '''
        Matrix A formation:
         size= (num of dies + num of islands + 2)x(num of dies + num of islands + 2)
         the first group corresponds to temperature of all dies
         the second group corresponds to temperature of all islands
         the last group corresponds to temperature of the substrate layer 
         Here is an example with 2 dies, 1 islands 
            ' -1/R1C1   0     1/R1C1      0         ' 'Tdie1'
            '     0  -1/R2C2  1/R2C2      0         ' 'Tdie2'  
        A = '     0     0   -1/RislCisl 1/RislCisl  ' 'Tisl'
            '     0     0        0      -1/RsubCsub ' 'Tsub '
             
        Warning : numpy matrix start indexing from 0 not 1 like matlab    
        '''  
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        side=num_island+num_dies+1
        A=np.zeros((side,side),dtype=np.float64) 
        A.itemset(side-1,side-1,0)
        for i in np.arange(0,num_dies,1):
            R=self.Rdie[i]['val']
            C=self.Cdie[i]['val']
            A.itemset((i,i),-1/(R*C))
            if self.Rdie[i]['isl']==self.Cdie[i]['isl']: # check if they are on same isl else there is sth wrong here
                isl_ind=self.Rdie[i]['isl']+num_dies-1
            A.itemset((i,isl_ind),1/(R*C))
        sub_layer_ind=num_dies+num_island  
        for j in np.arange(0,num_island,1):
            R=self.Risl[j]['val']  
            C=self.Cisl[j]['val']
            isl_ind=j+num_dies
            A.itemset((isl_ind,isl_ind),-1/(R*C))
            A.itemset((isl_ind,sub_layer_ind),1/(R*C))

        Rsub=self.Rsub['val']
        Csub=self.Csub['val']
        A.itemset(sub_layer_ind,sub_layer_ind,-1/(Rsub*Csub))
        return np.asarray(A)

    def form_b_mat(self):
        '''
        Matrix B formation:
         size= (num of dies + num of islands + 2)x(num of dies + num of islands + 2)
         using for Power input at different stages 
         Here is an example with 2 dies, 1 islands   
            ' 1/C1    0     0         ' 'Pdie1 '
            '   0   1/C2    0         'x'Pdie2 '  
        B = '1/Cisl 1/Cisl  0         ' 'Tamb  '
            '1/Csub 1/Csub  1/RsubCsub'    
        ''' 
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        rows=num_island+num_dies+1
        cols=num_dies+1
        B=np.zeros((rows,cols),dtype=np.float64) 
        for i in np.arange(0,num_dies,1):
            C=self.Cdie[i]['val']
            B.itemset(i,i,1/C)
        for i in np.arange(0,num_island,1):
            isl_row=i+num_dies
            C=self.Cisl[i]['val']
            for j in np.arange(0,num_dies/num_island,1):
                isl_col=i*(num_dies/num_island)+j
                B.itemset((isl_row,isl_col),1/C)
        sub_layer_row=num_dies+num_island     
        Csub=self.Csub['val']
        Rsub=self.Rsub['val']
        for i in np.arange(0,cols-1,1):
            B.itemset(sub_layer_row,i,1/Csub)
        B.itemset(sub_layer_row,cols-1,1/(Rsub*Csub))    
        return np.asarray(B)    

    '''------------------------------------Power Dissipation Model From Here On--------------------------------------'''

    def Eon(self, vdd, id, tri, tfv, Qrr):
        return vdd*id*(tri+tfv)/2+Qrr*vdd

    def Eoff(self,vdd,id,trv,tfi):
        return vdd*id*(trv+tfi)/2

    def Psw_eval(self,Eon,Eoff,fsw):
        return (Eon+Eoff)*fsw

    def rdson_eval_transistor(self,Tj,alpha,Ro):  # per unit curve
        Tref=self.Tref
        return (alpha*(Tj-Tref)+1)*Ro

    def rdson_fit_transistor(self,xdata,ydata):
        '''
        Return a list of parameters for rdson_eval_transistor
        '''
        popt, pcov = curve_fit(self.rdson_eval_transistor, xdata,ydata)
        [alpha,Ro]=popt
        return [alpha,Ro]

    def fCRSS(self,Vds,a1,b1,c1,a2,b2,c2):
        return np.piecewise(Vds, [Vds < 12], [lambda Vds:a1*Vds**2+b1*Vds+c1  , lambda Vds:a2*Vds**2+b2*Vds+c2]) 

    def fCRSS_fit(self,volt,cap):
        CRSS_volts=volt
        CRSS_raw=cap
        popt, pcov = curve_fit(self.fCRSS, CRSS_volts, CRSS_raw)
        [a1,b1,c1,a2,b2,c2]=popt # using fCoss  
        print 'Crss Fitting Error: '
        return [a1,b1,c1,a2,b2,c2]

    def Vth(self,T,a,b):
        return a*T+b

    def Vth_fit(self,temp,volt):
        popt, pcov = curve_fit(self.Vth, temp, volt)
        return popt

    def curve_fitting_all(self,filedes,rds_fn,crss_fn,vth_fn):
        '''
        Curve fitting all the required graph and return a list of parameters
        '''
        fd=filedes
        tuple=['Tj','Rds']
        rds_data= self.csv_load(filedes, rds_fn, tuple)
        [alpha,Ro]=self.rdson_fit_transistor(list2float(rds_data[0]),list2float(rds_data[1]))
        tuple=['Vds','Cap']
        crss_data=self.csv_load(filedes, crss_fn, tuple)
        print crss_data[0]
        print crss_data[1]
        [a1,b1,c1,a2,b2,c2]=self.fCRSS_fit(list2float(crss_data[0]), list2float(crss_data[1]))
        tuple=['Tj','Vth']
        Vth_dat=self.csv_load(filedes,vth_fn,tuple)
        if self.Vth_list==True:
            [a,b]=self.Vth_fit(list2float(Vth_dat[0]),list2float(Vth_dat[1]))
        else:
            a=0
            b=0        
        parameters=[alpha,Ro,a1,b1,c1,a2,b2,c2,a,b]     
        return parameters

    def ptot_all(self,T_list,parameters):
        p_all=[]
        for T in T_list:
           p_all.append(self.ptot_compute_single(T, parameters))
        return p_all    
        
    def ptot_compute_single(self,T,parameters):
        '''
        This model using the estimated value of I and V for every single dies, and the
        temperature from previous stages to estimate the new power disipation. This required extra inputs from data sheet,
        and some initial curve fitting algorithm (Least Square method) 
        inputs: Estimated Current through each die
                Estimated Bus voltage of the Half Bridge
                Temperature from last stage for a die
        output: Power Dissipation for a die
        '''
        T=T-273
        num_island=max(self.r_parent)
        num_dies=max(self.r_id) 
        ''' Control parameters'''
        ''' Rds params'''
        alpha=parameters[0]
        Ro=parameters[1]
        ''' CGD or CRSS parameters'''
        a1=parameters[2] 
        b1=parameters[3]
        c1=parameters[4]
        a2=parameters[5]
        b2=parameters[6]
        c2=parameters[7]
        a= parameters[8]
        b= parameters[9]
        ''' User's inputs'''
        Id=self.ID/(num_dies/num_island)
        Vdd=self.VDD
        Qrr=self.Qrr
        Rg=self.RG
        Vgson=self.Vg
        Ciss=self.Ciss
        Vpl=self.Vpl
        ''' First Vds is approximate using the new rdson'''
        rds=self.rdson_eval_transistor(T, alpha, Ro)
        #print 'rds: ' +str(rds)
        Vds=Id*rds
        ''' Compute Power Conduction'''
        Pcond=Vds*Id # ignore parasitic effect for now
        #print 'Power conduction:' +str(Pcond) + 'at T: ' + str(T)
        ''' Compute Eon'''
        '''Find Vth'''
        Vth=self.Vth(T, a, b)
        #print 'Vth: ' + str(Vth)
        '''Find Qgd'''
        Qgd=self.fCRSS(Vds,a1,b1,c1,a2,b2,c2)*(Vdd-Vds)
        #print 'Qgd is: ' +str(Qgd)
        '''Find IGoff and IGon'''
        Igoff=Vpl/Rg
        Igon =(Vgson-Vpl)/Rg 
        '''Find rising time for current, falling time for voltage '''
        tri=Rg*Ciss*np.log((Vgson-Vth)/(Vgson-Vpl))
        tfv=Qgd/Igon
        #print 'current rising time: '+ str(tri) +' voltage falling time: '+ str(tfv)
        Eon=self.Eon(Vdd, Id, tri, tfv, Qrr) 
        #print 'Eon: ' +str(Eon) 
        ''' Compute Eoff'''
        '''Find falling time for current, rising time for voltage '''
        trv=Qgd/Igoff
        tfi=Rg*Ciss*np.log(Vpl/Vth)
        #print 'current falling time: '+ str(tfi) +' voltage rising time: '+ str(trv)
        Eoff=self.Eoff(Vdd, Id, trv, tfi)
        #print 'Eoff: ' +str(Eoff)
        # Compute the total power using parameters list
        # this is just the map how to do it. Remember it is a list of signal so need to call this in another function
        # Only half of the cycle is taken care of now. (50% D)
        Psw=self.Psw_eval(Eon, Eoff, self.f_sw)
        Pave=(Pcond*(1/(2*self.f_sw)-tri-tfv-trv-tfi))/(1/(self.f_sw*2))+(Eon+Eoff)*self.f_sw
        if T == 27:
            print 'Temp: ' +str(T) +' Conduction loss: '+ str(Pcond) +' Switching loss: '+str(Psw)
        if T>126 and T<127:
            print 'Temp: ' +str(T) +' Conduction loss: '+ str(Pcond) +' Switching loss: '+str(Psw)   
        if T>225 and T<226:
            print 'Temp: ' +str(T) +' Conduction loss: '+ str(Pcond) +' Switching loss: '+str(Psw)        
        #print 'total loss: ' + str(Ptot)
        print Pave
        return Pave

    def Pcond_eval(self,Id_list,Vds_list,Ton,list=True):
        '''
        This method integrate through the list of Id-Vds output to compute power conduction 
        Ton: simulation time
        Id_list: list of Id in 1 period 
        Vds_list: list of Vd in 1 period
        If list is false, this function is used for approximation value of ID,VDS
        '''     
        if list:  #simulation case
            Pcond=[]
            for i in np.arange(0,len(Id_list),1):
                Pcond.append(Id_list[i]*Vds_list[i])   
            Power_cond=sum(Pcond)/float(Ton)
        else:  # no simulation case
            Power_cond=Id_list*Vds_list      
        return Power_cond
    
    def csv_load(self,filedes,filename,tuple):
        lists = [[] for i in range(len(tuple))]
        temp=open(os.path.join(filedes,filename),'rb')
        tempdata=csv.DictReader(temp)
        print tempdata
        print len(tuple)
        for row in tempdata:
            for i in range(len(row)):
                lists[i].append(row[tuple[i]])
        return lists

    def s_s_analysis(self,P_list):
        '''
        Analysis already avaiavle in fast_thermal, this is an extra version (more compatible)
        Tdies 1-n'''   
        temps=[]
        num_island=max(self.r_parent)
        num_dies=max(self.r_id)
        Psub=sum(P_list)
        Psub=Psub[0]
        for i in np.arange(0,num_dies,1):
            Rdie=self.Rdie[i]['val']
            if num_island!=1:
                if i < num_dies/num_island+1:
                    Pisl=sum(itertools.islice(P_list, 0, num_dies/num_island, 1))
                    Pisl=Pisl[0]
                else:
                    Pisl=sum(itertools.islice(P_list, num_dies/num_island,len(P_list), 1))
                    Pisl=Pisl[0]
            else:
                Pisl=Psub           
            T=Rdie*P_list[i]+self.Risl[self.Rdie[i]['isl']-1]['val']*Pisl+Psub*self.Rsub['val']+self.Tamb
            temps.append(T)   
        return temps

    def sucessive_approximation(self,Po,parameters):
        '''This is just a proof of concept for now. It will be added inside the optimization loop as an evaluate fucntion'''
        Plow=[x/2 for x in Po]
        print Plow
        Tsso=self.s_s_analysis(Plow) # First use power dissipation at ambient temperature
        converged=False
        count=0
        T_amb=[273]*len(Tsso)
        while(not(converged)):
            if count==0:
                Phigh=self.ptot_all(Tsso, parameters)
                Phigh=[x/2 for x in Phigh]
                Pave=[(x+y)/2 for x,y in zip(Plow,Phigh)]
                Pave=Phigh
                T_new=self.s_s_analysis(Pave)
                count+=1
                dt=[x-y for x,y in zip(T_new,Tsso)]
                if max(dt)<1:
                    converged=True
                print count
                print [T - 273 for T in T_new]
                print Pave 
            else:
                T_old=T_new
                Plow=Phigh
                Phigh=self.ptot_all(T_old, parameters)
                Phigh=[x/2 for x in Phigh]
                Pave=[(x+y)/2 for x,y in zip(Plow,Phigh)]
                Pave=Phigh
                T_new=self.s_s_analysis(Pave)
                count+=1
                dt=[x-y for x,y in zip(T_new,T_old)]   
                if max(dt)<1:
                    converged=True
                print count
                print [T - 273 for T in T_new]
                print Pave
if __name__ == '__main__':
    '''
    filedes='C:\Users\qmle\Desktop\cpmf_1200_s160b\cpmf_1200_s160b'
    filename='Rdson.csv'
    tuple=['Tj','Rds']
    data= csv_load(filedes, filename, tuple)
    print data
    print rdson_fit(list2float(data[0]),list2float(data[1]))
    Id_list=[1,2,3]
    Vds_list=[1,2,3]
    Ton=1
    print Conduction_loss_eval(Id_list, Vds_list, Ton) 
    '''         
        
        

