
# for transfer entropy
from collections import Counter
import numpy as np

def te(I,J,window=50):
    # X and Y are numpy arrays with all the values x(t) and y(t)
    t = len(X)
    # create a matrix for states ii, i, j for each time t
    zxy = np.zeros((t,3))
    zxy[:,0] = X.flatten()[1:][0:t-1]
    zxy[:,1] = X.flatten()[0:][0:t-1]
    zxy[:,2] = Y.flatten()[0:][0:t-1]
    # init counters for frequencies
    cii = Counter()
    ci = Counter()
    cj = Counter()
    for sts in zxy[:window]:
        cii[sts[0]] += 1
        ci[sts[1]] += 1
        cj[sts[2]] += 1
    # for each window
    for wt in range(window,t):
        # update counters
        if
        # create distributions (K = i(t+1))
        K =
        I =
        J =
