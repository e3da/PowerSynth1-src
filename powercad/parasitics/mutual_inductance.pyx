from libc.math cimport sqrt,atan,log,pow
import time
from numba import jit

import numpy as np
cimport numpy as np

cimport cython
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# This contains test functions for mutual inductance:
# Test 1: Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
# Page 5-6
# http://nvlpubs.nist.gov/nistpubs/jres/69C/jresv69Cn2p127_A1b.pdf

cdef float inter_func1(float x,float y,float z):
    '''
    Inner calculation of mutual inductance fucntion
    '''
    cdef float x2,x3,x4,y2,y3,y4,z2,z3,z4,sum1,sum2,sum3,sum4,sum5,sum6,sum7
    x2=pow(x,2)
    x3= pow(x, 3)
    x4= pow(x, 4)
    y2= pow(y, 2)
    y3= pow(y, 3)
    y4= pow(y, 4)
    z2= pow(z, 2)
    z3= pow(z, 3)
    z4= pow(z, 4)

    sum4 = 1 / 60.0 * (x4 + y4 + z4 - 3 * x2 * y2 - 3 * y2 * z2 - 3 * x2 * z2) * sqrt(x2 + y2 + z2)
    if (y!=0 and z!=0) or (x!=0 and y!=0) or (x!=0 and z!=0):
        sum1=(y2*z2/4.0-y4/24.0-z4/24.0)*x*log((x+sqrt(x2+y2+z2))/sqrt(y2+z2)) #if ((z2+y2)!=0) else 0
        sum2=(x2*z2/4.0-x4/24.0-z4/24.0)*y*log((y+sqrt(x2+y2+z2))/sqrt(x2+z2)) #if ((z2 + x2) != 0) else 0
        sum3=(x2*y2/4.0-x4/24.0-y4/24.0)*z*log((z+sqrt(x2+y2+z2))/sqrt(x2+y2)) #if ((x2+y2) != 0) else 0
        sum5=-x*y*z3/6.0*atan(x*y/(z*sqrt(x2+y2+z2))) if z!=0 else 0
        sum6=-x*y3*z/6.0*atan(x*z/(y*sqrt(x2+y2+z2))) if y!=0 else 0
        sum7=-x3*y*z/6.0*atan(y*z/(x*sqrt(x2+y2+z2))) if x!=0 else 0

        return sum1+sum2+sum3+sum4+sum5+sum6+sum7
    else:
        return sum4

cdef float inter_func(x, y, z,  sign):
    '''
    Inner calculation of mutual inductance fucntion
    '''

    x2 = x * x
    x3 = x2 * x
    x4 = x3 * x
    y2 = y * y
    y3 = y2 * y
    y4 = y3 * y
    z2 = z * z
    z3 = z2 * z
    z4 = z3 * z
    cond1 = (y2 != 0 and z2 != 0) or (x2 != 0 and y2 != 0) or (x2 != 0 and z2 != 0)
    cond2 = cond1 and x != 0
    cond3 = cond1 and y != 0
    cond4 = cond1 and z != 0
    sum1 = np.where(cond1, (y2 * z2 / 4.0 - y4 / 24.0 - z4 / 24.0) * x * np.log(
        (x + np.sqrt(x2 + y2 + z2)) / np.sqrt(y2 + z2)) + (x2 * z2 / 4.0 - x4 / 24.0 - z4 / 24.0) * y * np.log(
        (y + np.sqrt(x2 + y2 + z2)) / np.sqrt(x2 + z2)) + (x2 * y2 / 4.0 - x4 / 24.0 - y4 / 24.0) * z * np.log(
        (z + np.sqrt(x2 + y2 + z2)) / np.sqrt(x2 + y2)), 0)
    sum2 = np.where(cond2, -x * y * z3 / 6.0 * np.arctan(x * y / (z * np.sqrt(x2 + y2 + z2))), 0)
    sum3 = np.where(cond3, -x * y3 * z / 6.0 * np.arctan(x * z / (y * np.sqrt(x2 + y2 + z2))), 0)
    sum4 = np.where(cond4, -x3 * y * z / 6.0 * np.arctan(y * z / (x * np.sqrt(x2 + y2 + z2))), 0)
    sum5 = 1 / 60.0 * (x4 + y4 + z4 - 3 * x2 * y2 - 3 * y2 * z2 - 3 * x2 * z2) * np.sqrt(x2 + y2 + z2)
    return np.sum(sign * (sum1 + sum2 + sum3 + sum4 + sum5))

cpdef float mutual_between_bars (float w1, float l1, float t1, float w2, float l2, float t2, float l3, float p, float E):
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
    :param E: distance between 2 bars'
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

    Const=0.001/(w1*t1*w2*t2)
    np.warnings.filterwarnings('ignore')
    Mb=Const*outer_addition1(q1=E-w1,q2=E+w2-w1,q3=E+w2,q4=E,r1=p-t1,r2=p+t2-t1,r3=p+t2,r4=p,s1=l3-l1,s2=l3+l2-l1,s3=l2+l3,s4=l3)

    return Mb*1000 # in nH

cdef float outer_addition(float q1, float q2, float q3, float q4, float r1, float r2, float r3, float r4, float s1,
                          float s2, float s3, float s4):
    '''
    Compute the out - most
    :param fxyz: function to be integrated
    :return:
    '''
    DTYPE = np.float32
    cdef np.ndarray q = np.array([q1, q2, q3, q4], dtype=DTYPE)
    cdef np.ndarray r = np.array([r1, r2, r3, r4], dtype=DTYPE)
    cdef np.ndarray s = np.array([s1, s2, s3, s4], dtype=DTYPE)
    x, y, z = np.meshgrid(q, r, s, indexing='ij')
    i,j,k = np.meshgrid(range(1, 5, 1), range(1, 5, 1), range(1, 5, 1))
    sign= np.power(-1,i.flatten()+j.flatten()+k.flatten()+ np.ones((1, 64)))
    res = inter_func(x.flatten(),y.flatten(),z.flatten(),sign)

    return res


cdef float outer_addition1(float q1, float q2, float q3, float q4, float r1, float r2, float r3, float r4, float s1,
                           float s2, float s3, float s4):

    DTYPE = np.float32
    cdef float[:] q = np.array([q1, q2, q3, q4], dtype=DTYPE)
    cdef float[:] r = np.array([r1, r2, r3, r4], dtype=DTYPE)
    cdef float[:] s = np.array([s1, s2, s3, s4], dtype=DTYPE)
    cdef int i,j,k
    cdef float res=0

    for i in range(1,5,1):
        for j in range(1, 5, 1):
            for k in range(1, 5, 1):
                res+=-1**(i+j+k+1)*inter_func1(q[i-1],r[j-1],s[k-1])
    return res


