from libc.math cimport sqrt,atan,log,pow,fabs
import numpy as np
from cython.parallel cimport parallel
from libc.stdio cimport printf
from cython.parallel import prange
cimport openmp
# This contains test functions for mutual inductance:
# Test 1: Exact Inductance Equations for Rectangular Conductors With Applications to More Complicated Geometries
# Page 5-6
# http://nvlpubs.nist.gov/nistpubs/jres/69C/jresv69Cn2p127_A1b.pdf

cpdef double[:] mutual_mat_eval(double[:,:] m_mat,int nt):
    '''
    
    Args:
        m_mat: mutual parameters sent from python 
        nt: number of threads requested

    Returns:

    '''
    cdef double [:,:] m_mat1 = np.asarray(m_mat)
    cdef int rows = np.asarray(m_mat).shape[0]
    cdef double [:] result = np.zeros(rows)
    cdef int i,num_t,chunksize
    openmp.omp_set_dynamic(36)
    with nogil, parallel():
        openmp.omp_set_num_threads(nt)
        num_t = openmp.omp_get_max_threads()
        chunksize = rows/num_t
        #printf("%d\n",num_t)
        for i in prange(rows, schedule='static',chunksize=chunksize):
                result[i] = mutual_between_bars(m_mat1[i,:])
    return result

cdef double inter_func1(double x,double y,double z) nogil:
    '''
    Inner calculation of mutual inductance fucntion
    '''
    cdef double x2,x3,x4,y2,y3,y4,z2,z3,z4,s1,s2,xy,xy2,xz,xz2,yz,yz2,sum1,sum2,sum3,sum4,sum5,sum6,sum7
    #printf("x %f\n", x)
    #printf("y %f\n", y)
    #printf("z %f\n", z)

    x2 = x*x;
    x3 = x2*x;
    x4 = x2*x2;
    y2 = y*y;
    y3 = y2*y;
    y4 = y2*y2;
    z2 = z*z;
    z3 = z2*z;
    z4 = z2*z2;
    s1 = sqrt(x2 + y2 + z2);
    s2 = x*y*z/6.0;
    xy = x*y;
    xz = x*z;
    yz = y*z;
    xy2 = xy*xy;
    xz2 = xz*xz;
    yz2 = yz*yz;
    sum4 = 1 / 60.0 * (x4 + y4 + z4 - 3 * (xy2 + yz2 + xz2)) * s1
    if (y != 0 and z != 0) or (x != 0 and y != 0) or (x != 0 and z != 0):
        sum1 = (yz2 / 4.0 - y4 / 24.0 - z4 / 24.0) * x * log(
            (x + s1) / sqrt(y2 + z2))  # if ((z2+y2)!=0) else 0
        sum2 = (xz2 / 4.0 - x4 / 24.0 - z4 / 24.0) * y * log(
            (y + s1) / sqrt(x2 + z2))  # if ((z2 + x2) != 0) else 0
        sum3 = (xy2 / 4.0 - x4 / 24.0 - y4 / 24.0) * z * log(
            (z + s1) / sqrt(x2 + y2))  # if ((x2+y2) != 0) else 0
        sum5 = -s2 * z2 * atan(xy / (z * s1)) if z != 0 else 0
        sum6 = -s2 * y2 * atan(xz / (y * s1)) if y != 0 else 0
        sum7 = -s2 * x2 * atan(yz / (x * s1)) if x != 0 else 0
        return sum1 + sum2 + sum3 + sum4 + sum5 + sum6 + sum7
    else:
        return sum4


cdef double mutual_between_bars (double[:] param) nogil:
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
    cdef double w1,l1,t1,w2,l2,t2,l3,p,E
    w1 = fabs(param[0]*0.1)
    l1 = fabs(param[1]*0.1)
    t1 = fabs(param[2]*0.1)
    w2 = fabs(param[3]*0.1)
    l2 = fabs(param[4]*0.1)
    t2 = fabs(param[5]*0.1)
    l3 = fabs(param[6]*0.1)
    p = fabs(param[7]*0.1)
    E = fabs(param[8]*0.1)
    Const=0.001/(w1*t1*w2*t2)
    Mb = Const * outer_addition(q1=E - w1, q2=E + w2 - w1, q3=E + w2, q4=E, r1=p - t1, r2=p + t2 - t1, r3=p + t2, r4=p,
                                s1=l3 - l1, s2=l3 + l2 - l1, s3=l2 + l3, s4=l3)

    #printf("Mb %f\n",Mb)

    return Mb*1000 # in nH


cdef double outer_addition(double q1, double q2, double q3, double q4, double r1, double r2, double r3, double r4, double s1,
                           double s2, double s3, double s4) nogil:


    cdef double[4] q,r,s
    q[0] = q1
    q[1] = q2
    q[2] = q3
    q[3] = q4
    r[0] = r1
    r[1] = r2
    r[2] = r3
    r[3] = r4
    s[0] = s1
    s[1] = s2
    s[2] = s3
    s[3] = s4
    cdef double interval,sign
    cdef int i,j,k
    cdef double res
    res = 0.0
    for i in xrange(1,5,1):
        for j in xrange(1, 5, 1):
            for k in xrange(1, 5, 1):
                inter_val = inter_func1(q[i - 1], r[j - 1], s[k - 1])
                sign = pow(-1, (i + j + k + 1))
                #printf("inside %i%i%i%f\n", i,j,k,sign*inter_val)
                res = res + sign*inter_val
                #printf("update sum %f\n", res)
    #printf("outer add %f\n", res)

    return res

cdef double check_val(double q, double r, double s, param_dict):
    test = False
    if test:
        if (q, r, s) in param_dict:
            inter_val = param_dict[(q, r, s)]
        else:
            inter_val = inter_func1(q, r, s)
            param_dict[(q, r, s)] = inter_val
    else:
        inter_val = inter_func1(q, r, s)

    return inter_val

