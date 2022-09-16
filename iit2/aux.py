
import numpy as np
from itertools import combinations

# int > binary array
def int2arr(n,arr_len):
    # reversed for cell order
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    return x

# binary matrix rep
def bin_matrix(r,nans=False):
    x = np.zeros((r,2**r))
    for i in range(r):
        b = np.concatenate((np.zeros(2**i),np.ones(2**i)))
        x[i] = np.tile(b,2**(r-i-1))
    if nans:
        x = np.where(x==0,np.nan,1)
    return x.T

# array to int
def arr2int(arr):
    xi = np.sum([x<<e for e,x in enumerate(arr.flatten().astype(int))])
    return xi

# tensor with NxM matrix reps
def matrix_reps(n=3,m=3):
    x = 2**(n*m)
    t = np.zeros((x,n,m))
    for i in range(x):
        xmn = int2arr(i,n*m).reshape(n,m).astype(int)
        t[i] = xmn
    return t

# list of powerset combinations
def powerset(ne,min_set_size=1,max_set_size=0):
    # ne: number of elements
    max_set_size = ne+1 if max_set_size<min_set_size else max_set_size
    pset = []
    for i in range(min_set_size,max_set_size+1):
        pset.extend(list(combinations(np.arange(ne),i)))
    return pset

# dict for int reps
def int_reps(mreps):
    ireps = {}
    for xi in range(mreps.shape[0]):
        mi = tuple(mreps[xi].flatten().astype(int))
        ireps[mi] = xi
    return ireps

# distance matrix for abc
def mk_abc_dm(dim=8,cost=1):
    dm = np.zeros((dim,dim))
    for i in range(dim):
        bin_i = int2arr(i,3)
        for j in range(dim):
            bin_j = int2arr(j,3)
            dij = np.sum([abs(bi-bj) for bi,bj in zip(bin_i,bin_j)])
            dm[i][j] = cost * dij
    return dm

# distance matrix for glider EMD
def mk_gl_dm(sts):
    s = sts.reshape(16,25)
    dm = np.array([np.nansum(abs(s-s[i]),axis=1) for i in range(16)])
    return dm





































#
