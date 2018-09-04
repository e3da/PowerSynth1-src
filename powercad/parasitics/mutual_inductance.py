
from math import pow,log,sqrt,atan,factorial
import time
from numba import jit
import numpy as np
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# This contains test functions for mutual inductance:
# Test 1: Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
# Page 5-6
# http://nvlpubs.nist.gov/nistpubs/jres/69C/jresv69Cn2p127_A1b.pdf
@jit
def inter_func(x,y,z):
    '''
    Inner calculation of mutual inductance fucntion
    '''
    x2=pow(x,2)
    x3=pow(x,3)
    x4=pow(x,4)
    y2=pow(y,2)
    y3=pow(y,3)
    y4=pow(y,4)
    z2=pow(z,2)
    z3=pow(z,3)
    z4=pow(z,4)
    sum4 = 1 / 60.0 * (x4 + y4 + z4 - 3 * x2 * y2 - 3 * y2 * z2 - 3 * x2 * z2) * sqrt(x2 + y2 + z2)
    if (y!=0 and z!=0) or (y!=0 and y!=0) or (x!=0 and z!=0):
        sum1=(y2*z2/4.0-y4/24.0-z4/24.0)*x*log((x+sqrt(x2+y2+z2))/sqrt(y2+z2)) #if ((z2+y2)!=0) else 0
        sum2=(x2*z2/4.0-x4/24.0-z4/24.0)*y*log((y+sqrt(x2+y2+z2))/sqrt(x2+z2)) #if ((z2 + x2) != 0) else 0
        sum3=(x2*y2/4.0-x4/24.0-y4/24.0)*z*log((z+sqrt(x2+y2+z2))/sqrt(x2+y2)) #if ((x2+y2) != 0) else 0
        sum5=-x*y*z3/6.0*atan(x*y/(z*sqrt(x2+y2+z2))) if z!=0 else 0
        sum6=-x*y3*z/6.0*atan(x*z/(y*sqrt(x2+y2+z2))) if y!=0 else 0
        sum7=-x3*y*z/6.0*atan(y*z/(x*sqrt(x2+y2+z2))) if x!=0 else 0
        return sum1+sum2+sum3+sum4+sum5+sum6+sum7
    else:
        return sum4

@jit
def mutual_between_bars(w1,l1,t1,w2,l2,t2,l3,p,d):
    '''
    This function is used to compute the mutual inductance value between 2 rectangular bars in space.
    all dimension are in mm

    :param w1: first bar 's width
    :param l1: first bar 's length
    :param t1: first bar 's thick
    :param w2: second bar 's width
    :param l2: second bar 's length
    :param t2: second bar 's thick
    :param l3: distance between two bars' (longtitude)
    :param p: height of second bar (+z)
    :param d: distance between 2 bars'
    :return: Mutual inductance of 2 bars in nH
    '''
    w1=w1*0.1
    l1=l1*0.1
    t1=t1*0.1

    w2=w2*0.1
    l2=l2*0.1
    t2=t2*0.1

    l3= l3 *0.1
    p=p*0.1
    d=d*0.1

    E=d+w1
    Const=0.001/(w1*t1*w2*t2)
    Mb=Const*outer_addition(q1=E-w1,q2=E+w2-w1,q3=E+w2,q4=E,r1=p-t1,r2=p+t2-t1,r3=p+t2,r4=p,s1=l3-l1,s2=l3+l2-l1,s3=l2+l3,s4=l3)
    return Mb*1000 # in nH
@jit
def outer_addition(q1,q2,q3,q4,r1,r2,r3,r4,s1,s2,s3,s4,fxyz=inter_func):
    '''
    Compute the out - most
    :param fxyz: function to be integrated
    :return:
    '''
    res=0
    q=[q1,q2,q3,q4]
    r=[r1,r2,r3,r4]
    s=[s1,s2,s3,s4]
    for i in range(1,5,1):
        for j in range(1, 5, 1):
            for k in range(1, 5, 1):
                res+=pow(-1,(i+j+k+1))*fxyz(q[i-1],r[j-1],s[k-1])


    return res

def bar_ind(w,l,t,fxyz=inter_func):
    # convert to cm
    w1 = w * 0.1
    l1 = l * 0.1
    t1 = t * 0.1

    Const=0.008/(w1**2*t1**2)

    res = 0
    q = [w1,0]
    r = [t1,0]
    s = [l1,0]
    for i in range(1, 3, 1):
        for j in range(1, 3, 1):
            for k in range(1, 3, 1):
                res += pow(-1, (i + j + k + 1)) * fxyz(q[i - 1], r[j - 1], s[k - 1])
    print res * Const * 1000
    return abs(res*Const*1000) # in nH

def Test_Mutual():
    start=time.time()
    print mutual_between_bars(w1=10,l1=30,t1=0.64,w2=10,l2=30,t2=0.64,l3=0,p=0,d=2)
    print (time.time()-start)#*factorial(5)
    W1=np.linspace(1,20,20)
    W2=W1
    M=[]
    csvfile = open('C:/Users/qmle/Desktop/Testing/Mutual Inductance Fast Henry/Test code/MutualQ3D.csv','rb')
    fieldnames=['W1','W2','M']
    #writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
    reader=csv.DictReader(csvfile)
    M3D=np.zeros((20,20))
    for row in reader:
        M3D[int(row['w1'])-1,int(row['w2'])-1]=float(row['ACL'])
    #writer.writeheader()
    M=np.zeros((20,20))
    for i in range(20):
       for j in range(20):
           M[i,j]=(mutual_between_bars(w1=W1[i],l1=30,t1=0.64,w2=W2[j],l2=30,t2=0.64,l3=0,p=0,d=2))

    REL_ERR=abs(M-M3D)/M3D*100
    X,Y=np.meshgrid(W1,W2)
    fig1 = plt.figure(1)
    ax = fig1.gca(projection='3d')
    #surf1 = ax.plot_surface(X, Y, M)
    ax.scatter(X,Y,REL_ERR,c='b')
    #ax.scatter(X,Y,M3D,c='r')
    plt.xlabel('W1')
    plt.ylabel('W2')
    plt.show()

    csvfile = open('C:/Users/qmle/Desktop/Testing/Mutual Inductance Fast Henry/Test code/MutualQ3D_distance.csv','rb')
    fieldnames=['d1','M']
    M=[]
    M_Q3D=[]
    reader=csv.DictReader(csvfile)
    for row in reader:
        M_Q3D.append(float(row['M']))
    for i in np.arange(2,21,1):
        print i
        M.append(mutual_between_bars(w1=10,l1=30,t1=0.64,w2=10,l2=30,t2=0.64,l3=0,p=0,d=i))

    plt.plot(np.arange(2,21,1),M,'k:',label='Model',c='b',lw=3)
    plt.plot(np.arange(2,21,1),M_Q3D,'k--',label='Q3D',c='r',lw=3)
    plt.xlabel('distance')
    plt.ylabel('M (nH)')
    plt.show()
if __name__=='__main__':
    print mutual_between_bars(w1=10, l1=20, t1=0.2, w2=12, l2=14, t2=0.2, l3=16, p=0, d=4)