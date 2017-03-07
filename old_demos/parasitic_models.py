import math

#--------------------------------------------------------------------------
#-----------  resistance model of traces on ground plane-- ----------------
#--------------------------------------------------------------------------
def R_trace (f, w, l, t, h): 
    p = 1/58e6                  # resistivity of trace material; 
    u0 = 1.257e-6               # permeability of vaccum; 
               
    t1 = t*1e-3                 # transfer to unit in m;
    w1 = w*1e-3                 # transfer to unit in m;
    h1 = h*1e-3                 # transfer to unit in m;
    l1 = l*1e-3                 # transfer to unit in m;
    
    # resistance part of trace (trace resistance + ground plane resistance): 
    LR = 0.94 + 0.132*w1/h1 - 0.0062*(w1/h1)*(w1/h1)     

    # resistance calculation:     
    r = LR*(1/math.pi + 1/math.pow(math.pi, 2)*math.log(4*math.pi*w1/t1))*math.sqrt(math.pi*u0*f*p)/(math.sqrt(2)*w1)*l1*1e3 # unit in mOhms
    return r

#print R_trace (300000, 10, 40, 0.41, 0.64)



#--------------------------------------------------------------------------
#-----------  inductance  model of traces on ground plane-- ---------------
#--------------------------------------------------------------------------
def L_trace(w, l, t, h):
    w1 = w*1e-3                     # transfer to unit in m;
    h1 = h*1e-3                     # transfer to unit in m;
    t1 = t*1e-3                     # transfer to unit in m;
    l1 = l*1e-3                     # transfer to unit in m;
    
    c = 3*1e8                        # speed of light;
    u_r = 1                          # relative permeability of the isolation material;
    u_0 = 4*math.pi*1e-7             # permeability of vaccum;
    e_r = 8.8                        # relative permittivity of the isolation material;
    e_0 = 8.85*1e-12                 # permittivity of vaccum;
    
    # effective dielectric permittivity and effective width:    
    w_e = w1 + 0.398*t1*(1 + math.log(2*h1/t1))
    e_eff = (e_r + 1)/2 + (e_r - 1)/2*math.pow(1 + 12*h1/w_e, -1/2) - 0.217*(e_r -1)*t1/(math.sqrt(w_e*h1))


    # micro-strip impedance:
    C_a = e_0*(w_e/h1 + 1.393 + 0.667*math.log(w_e/h1 + 1.444))
    z0 = math.sqrt(e_0*u_0/e_eff)*1/C_a
    
    # inductance calculation of microstrip: 
    Ind_0 = l1*z0*math.sqrt(u_r*e_eff)/c*1e9   # unit in nH;
    
    # inductance calculation of isolated rectangular bar trace:
    Ind_1 = u_0*l1/(2*math.pi)*(math.log(2*l/(w + t)) + 1/2 + 2/9*(w +t)/l)*1e9  # unit in nH;  
    
    # averaged model for inductance calculation:
    Ind = (Ind_0 + Ind_1)/2
    return Ind     

#print L_trace (10, 40, 0.41, 0.64)


 
#-----------------------------------------------------
#-----------  capacitance  model of traces ----------- 
#------------------------------------------------------
def C_trace (w, l, t, h): 
    w1 = w*1e-3         # transfer to unit in m;
    h1 = h*1e-3         # transfer to unit in m;
    l1 = l*1e-3         # transfer to unit in m;
    t1 = t*1e-3         # transfer to unit in m; 
    
    k = 8.8             # relative dielectric constant (permittivity) of the isolation material; 
    e_0 = 8.85*1e-12    # permittivity of vaccum;           
    
    # effective distance between trace and ground plane:
    h1_eff = (2*h1 + t1)/2   

    # effective area of fringe capacitance:     
    A = (2*w1 + 2*l1)*t1  
    
    # effective dielectric constant:    
    k2 = (k +1)/2 + (k -1)/2*math.pow(1 + 12*h1/w1, -0.5) - 0.217*(k -1)*t1/math.sqrt(w1*h1) 
    
    # sum of parallel plate and fringe capacitance    
    c =  k*e_0*(w1*l1)/h1*1e12 + k2*e_0*A/h1_eff*1e12   # unit in pF;
    return c   
 
#print C_trace(10, 40, 0.41, 0.64)    


#-------------------------------------------------------------
#----------- self-partial wire-bond inductance----------------
#-------------------------------------------------------------
def L_wire(l, r):
    l1 = l*1e-3
    r1 = r*1e-3
    u_0 = 4*math.pi*1e-7
    
    Ind = u_0*l1/(2*math.pi)*(math.log(2*l1/r1) - 1)*1e9

    return Ind
    

#-----------------------------------------------------------------
#----------- mutual-partial inductance of wire-bond ---------------
#-----------------------------------------------------------------
def M_wire(l, r, d):
    l1 = l*1e-3

    d1 = d*1e-3   # distance between wire-bonds;
    u_0 = 4*math.pi*1e-7
    
    m = u_0*l1/(2*math.pi)*(math.log(l1/d1 + math.sqrt(1 + l1*l1/(d1*d1))) - math.sqrt(1 + d1*d1/(l1*l1)) + d1/l1 )*1e9

    return m


#-------------------------------------------------------------
#----------- single wire-bond resistance----------------------
#-------------------------------------------------------------
def R_wire (f, l, r):
    l1 = l*1e-3
    r1 = r*1e-3
    
    u0 = 1.257e-6                       # permeability in the henries per meter;
    b = 58e6                            # conductivity; 
    d = 1/math.sqrt(math.pi*u0*b*f)     # skin depth is in m;
    
    d1 = d*(1 - math.exp(-r1/d))
    z = 0.62006*r1/d
    y = 0.189774/math.pow(1 + 0.272481*math.pow(math.pow(z, 1.82938) - math.pow(z, -0.99457), 2), 1.0941)
    
    A_eff = math.pi*(2*r1*d1 - d1*d1)*(1 + y)
    
    r_w = l1/(A_eff*b)*1e3  # in mOhms
    
    return r_w

#print 1/(2/(L_wire(11.25, 0.125) + M_wire(11.25, 0.125, 0.6) + M_wire(11.25, 0.125, 1.2)) + 1/(L_wire(11.25, 0.125) + M_wire(11.25, 0.125, 0.6) + M_wire(11.25, 0.125, 0.6)))

## path1: 
#L_p1 = L_trace(5, 6, 0.41, 0.64)+ L_trace(10, 17.59, 0.41, 0.64)+ L_trace(9, 27.9, 0.41, 0.64)+ L_trace(10, 15.67, 0.41, 0.64)+ L_trace(7, 29.09, 0.41, 0.64)+ L_trace(3.5, 6, 0.41, 0.64)
#
#for f in xrange (100000, 1100000, 100000 ):
#    R_p1 = R_trace (f, 5, 6, 0.41, 0.64) +R_trace (f, 10, 17.59, 0.41, 0.64)+R_trace (f, 9, 27.9, 0.41, 0.64)+R_trace (f, 10, 15.67, 0.41, 0.64)+R_trace (f, 7, 29.09, 0.41, 0.64)+R_trace (f, 3.5, 6, 0.41, 0.64)
#    R_p1_wire = R_wire(f, 11.25, 0.125)/3
#    print R_p1+R_p1_wire
    
# # path2: 
#print  L_trace(5, 6, 0.41, 0.64)+ L_trace(10, 17.59, 0.41, 0.64)+ L_trace(9, 20.9, 0.41, 0.64)+ L_trace(10, 22.67, 0.41, 0.64)+ L_trace(7, 29.09, 0.41, 0.64)+ L_trace(3.5, 6, 0.41, 0.64)
#
#for f in xrange (100000, 1100000, 100000 ):
#    R_p2 = R_trace (f, 5, 6, 0.41, 0.64) +R_trace (f, 10, 17.59, 0.41, 0.64)+R_trace (f, 9, 20.9, 0.41, 0.64)+R_trace (f, 10, 22.67, 0.41, 0.64)+R_trace (f, 7, 29.09, 0.41, 0.64)+R_trace (f, 3.5, 6, 0.41, 0.64)
#    R_p2_wire = R_wire(f, 11.25, 0.125)/6
#    print R_p2+R_p2_wire   

# # path3: 
#print  L_trace(5, 6, 0.41, 0.64)+ L_trace(10, 17.59, 0.41, 0.64)+ L_trace(9, 13.9, 0.41, 0.64)+ L_trace(10, 29.67, 0.41, 0.64)+ L_trace(7, 29.09, 0.41, 0.64)+ L_trace(3.5, 6, 0.41, 0.64)
#
#for f in xrange (100000, 1100000, 100000 ):
#    R_p3 = R_trace (f, 5, 6, 0.41, 0.64) +R_trace (f, 10, 17.59, 0.41, 0.64)+R_trace (f, 9, 13.9, 0.41, 0.64)+R_trace (f, 10, 29.67, 0.41, 0.64)+R_trace (f, 7, 29.09, 0.41, 0.64)+R_trace (f, 3.5, 6, 0.41, 0.64)
#    R_p3_wire = R_wire(f, 11.25, 0.125)/12
#    print R_p3+R_p3_wire   

#for f in xrange (100000, 1100000, 100000 ):
#    print R_trace(f, 10, 20, 0.41, 0.64) + R_trace(f, 10, 20, 0.41, 0.64)


print C_trace (4, 25, 0.41, 0.64) 