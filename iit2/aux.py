
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

# distance matrix for n states
# need to fix this
def xmk_dm(n_sts,cost=1,as_float=True):
    ns = np.arange(n_sts)
    mi,mj = np.meshgrid(ns,ns)
    dm = np.abs(mi-mj)*cost
    # if not float, returns dm as int
    if as_float:
        return dm.astype(float)
    return dm

# distance matrix
def mk_dm(dim=8,cost=1,as_float=True):
    dm = np.zeros((dim,dim))
    for i in range(dim):
        bin_i = int2arr(i,3)
        for j in range(dim):
            bin_j = int2arr(j,3)
            dij = np.sum([abs(bi-bj) for bi,bj in zip(bin_i,bin_j)])
            dm[i][j] = cost * dij
    # if not float, returns dm as int
    if as_float:
        return dm.astype(float)
    return dm

# gol timestep (bounded domains)
def gol_timestep(domain):
    # only int 0/1
    dcopy = domain.astype(int)
    # iterate through cells
    for ei,di in enumerate(domain):
        for ej,dij in enumerate(di):
            # apply gol rule (max for borders)
            nbsum = np.sum(domain[max(0,ei-1):ei+2,max(0,ej-1):ej+2]) - dij
            dcopy[ei,ej] = 1 if nbsum==3 or (nbsum==2 & dij==1) else 0
    return dcopy

# tx matrix for a GoL individual cell
def txs_gol_cell():
    # 512 txs, 2 sts (sti,stx) & 9 cells domain
    tx_tensor = np.zeros((512,2,9))
    tx_matrix = np.zeros((512,512))
    # for each sti 0:512 -> stx
    for i in range(512):
        # sti
        sti = int2arr(i,arr_len=9)
        tx_tensor[i,0] = sti
        # stx
        stx = gol_timestep(sti.reshape(3,3))
        tx_tensor[i,1] = stx.flatten()
        # sti -> stx
        x = arr2int(stx)
        tx_matrix[i,x] += 1
    return tx_tensor,tx_matrix


































#
