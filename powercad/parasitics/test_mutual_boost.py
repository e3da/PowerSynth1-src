from powercad.parasitics.mutual_inductance_saved import *
from timeit import default_timer as timer
from sklearn.svm import SVR
from sklearn import svm
from sklearn.neural_network import MLPClassifier
import numpy as np
import matplotlib.pyplot as plt
from SALib.analyze import morris
from SALib.sample.morris import sample
from SALib.plotting.morris import horizontal_bar_plot, covariance_plot, sample_histograms


def idea1_ressponse_surface():

    n_samples= 1000
    w1 = np.linspace(1,10, n_samples)
    l1 = np.linspace(1, 10, n_samples)
    w2 = np.linspace(1, 10, n_samples)
    l2 = np.linspace(1, 10, n_samples)
    l3 = np.linspace(1, 10, n_samples)
    E = np.linspace(1,4, n_samples)


    f= mutual_between_bars

    Y = np.zeros((n_samples), dtype=np.float64)
    X=np.random.rand(n_samples,6)*10
    start = timer()
    for i in range(n_samples):
        Y[i] = f(X[i,0], X[i,1],0.2, X[i,2], X[i,3],0.2, X[i,4],0, X[i,5])
    print "eval",n_samples,'samples', timer()-start,'s'
    print np.shape(X),np.shape(Y)

    clf = SVR(kernel='linear',gamma='scale', C=1.0, epsilon=0.2)
    clf.fit(X, Y)
    start = timer()
    Y1=clf.predict(X)
    print "predict", n_samples, 'samples', timer() - start, 's'
    print clf.score(X, Y)

    k = 100

    plt.plot(X[0:k,1],Y[0:k],'-')
    plt.plot(X[0:k, 1], Y1[0:k],'--')
    plt.show()

    plt.plot(X[0:k, 2], Y[0:k], '-')
    plt.plot(X[0:k, 2], Y1[0:k], '--')
    plt.show()

    plt.plot(X[0:k, 3], Y[0:k], '-')
    plt.plot(X[0:k, 3], Y1[0:k], '--')
    plt.show()

def idea2_SVM():
    problem = {
        'num_vars': 6,
        'names': ['w1', 'l1', 'w2','l2','l3','E'],
        'bounds': [[1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40]]
    }
    X = sample(problem, N=10000, num_levels=4, grid_jump=2, optimal_trajectories=None)
    n_samples=np.shape(X)[0]
    Y = np.zeros((n_samples), dtype=np.float64)

    f = mutual_between_bars

    for i in range(n_samples):
        Y[i] = f(X[i, 0], X[i, 1], 0.2, X[i, 2], X[i, 3], 0.2, X[i, 4], 0, X[i, 5])
    Y*=1e-9
    #print Y
    Decisions = np.where(Y>1e-10,1,0)
    X_norm = X/np.max(X)
    #print X_norm
    clf = svm.SVC(gamma='scale')

    clf.fit(X_norm, Decisions)
    print  clf.score(X_norm,Decisions)

    X_2 = sample(problem, N=10000, num_levels=4, grid_jump=2, optimal_trajectories=None)
    n_samples = np.shape(X_2)[0]

    Y_2 = np.zeros((n_samples), dtype=np.float64)
    start = timer()
    for i in range(n_samples):
        Y_2[i] = f(X_2[i, 0], X_2[i, 1], 0.2, X_2[i, 2], X_2[i, 3], 0.2, X_2[i, 4], 0, X_2[i, 5])
    print "eval 700000 samples", timer()-start
    X_2 = X_2 / np.max(X_2)

    Y_2 *= 1e-9

    start = timer()

    new_prediction = clf.predict(X_2)
    print "predict time", timer()-start,'s'

    right_decisions = np.where(Y_2 > 1e-10, 1, 0)
    #print new_prediction
    #print right_decisions
    diff = right_decisions-new_prediction
    diff = np.where(diff==0,1,0)
    print sum(diff)
    print len(right_decisions)

def idea3_MLP():
    problem = {
        'num_vars': 6,
        'names': ['w1', 'l1', 'w2', 'l2', 'l3', 'E'],
        'bounds': [[1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40],
                   [1, 40]]
    }
    X = sample(problem, N=100000, num_levels=4, grid_jump=2, optimal_trajectories=None)
    print X
    raw_input()

    n_samples = np.shape(X)[0]
    Y = np.zeros((n_samples), dtype=np.float64)

    f = mutual_between_bars

    for i in range(n_samples):
        Y[i] = f(X[i, 0], X[i, 1], 0.2, X[i, 2], X[i, 3], 0.2, X[i, 4], 0, X[i, 5])
    Y *= 1e-9
    # print Y
    Decisions = np.where(Y > 2e-10, 1, 0)
    X_norm = X / np.max(X)
    # print X_norm
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                        hidden_layer_sizes=(10,), random_state=1)

    clf.fit(X_norm, Decisions)
    print  clf.score(X_norm, Decisions)

    X_2 = sample(problem, N=10000, num_levels=4, grid_jump=2, optimal_trajectories=None)
    n_samples = np.shape(X_2)[0]

    Y_2 = np.zeros((n_samples), dtype=np.float64)
    start = timer()
    for i in range(n_samples):
        Y_2[i]= f(X_2[i, 0], X_2[i, 1], 0.2, X_2[i, 2], X_2[i, 3], 0.2, X_2[i, 4], 0, X_2[i, 5])
    print "eval", n_samples , "samples", timer() - start
    X_2 = X_2 / np.max(X_2)

    Y_2 *= 1e-9

    start = timer()

    new_prediction = clf.predict(X_2)
    print "predict time", timer() - start, 's'

    right_decisions = np.where(Y_2 > 1.1e-10, 1, 0)
    start = timer()
    for i in new_prediction:
        if i == 1:
            f(X_2[0, 0], X_2[0, 1], 0.2, X_2[0, 2], X_2[0, 3], 0.2, X_2[0, 4], 0, X_2[0, 5])
    print "Boosted", timer() - start

    # print new_prediction
    # print right_decisions
    diff = right_decisions - new_prediction
    diff = np.where(diff == 0, 1, 0)
    for i in range(len(diff)):
        if diff[i]==0:
            if Y_2[i]< 1e-10:
                print Y_2[i]
    print sum(diff)
    print len(right_decisions)

idea3_MLP()