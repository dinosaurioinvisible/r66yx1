
import numpy as np

# convert array > binary > int
def arr2int(arr):
    # needs to be reversed for elements order [e0,e1,e2,...]
    x_str = ''.join(arr.flatten().astype(int).astype(str)) [::-1]
    return int(x_str,2)

# convert int number into an array or a NxN matrix
def int2arr(n,arr_len,dims=1):
    # needs to be reversed for assignation to elements [e0,e1,e2...]
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    if dims > 1:
        x = x.reshape(dims,dims)
    return x

# ring locations (top to bottom, left to right, symmetrical)
def ring_locs(i=0,j=0,r=1,hollow=True,only_edges=False):
    locs = []
    for ir in range(-r,r+1):
        ij = set([abs(ir)-r,r-abs(ir)]) if hollow == True else [jx for jx in range(abs(ir)-r,r-abs(ir)+1)]
        for jr in ij:
            if only_edges:
                if ir%r==0:
                    locs.append([i+ir,j+jr])
            else:
                locs.append([i+ir,j+jr])
    locs = sorted(locs)
    return locs

# distance matrix
def dist_matrix(dim=8,cost=1):
    dm = np.zeros((dim,dim))
    for i in range(dim):
        bin_i = int2arr(i,3)
        for j in range(dim):
            bin_j = int2arr(j,3)
            dij = np.sum([abs(bi-bj) for bi,bj in zip(bin_i,bin_j)])
            dm[i][j] = cost * dij
    return dm















#
