
import numpy as np

# convert array > binary > int
def arr2int(arr,rot=None):
    if rot:
        arr = np.rot90(arr,rot)
    # needs to be reversed for elements order [e0,e1,e2,...]
    x_str = ''.join(arr.flatten().astype(int).astype(str)) [::-1]
    x = int(x_str,2)
    return x

# convert int number into an array or a NxN matrix
def int2arr(n,arr_len,dims=1):
    # needs to be reversed for assignation to elements [e0,e1,e2...]
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    if dims > 1:
        x = x.reshape(dims,dims)
    return x

# env int > arr > fills center > matrix > border vectors > ints
def envint2arrs(n,env_cells=8,fill=2,return_matrix=False):
    arr = int2arr(n,arr_len=env_cells)
    arr = np.insert(arr,int(len(arr)/2),fill)
    dim = int(np.sqrt(arr.size))
    mat = arr.reshape(dim,dim)
    # anticlockwise
    borders = [mat[0],mat[:,0],mat[-1],mat[:,-1]]
    eints = [arr2int(bi) for bi in borders]
    if return_matrix:
        return eints+mat
    return eints

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
