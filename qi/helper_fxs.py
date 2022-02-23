
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

# organization
def organization_fx(gt):
    st_txs = {}

    txs = {}
    for sti in range(16):
        # intitial state
        sti_a, sti_b, sti_c, sti_d = int2arr(sti,arr_len=4)
        # syntactic operators/distinctins
        for envi in range(256):
            # env states
            env = int2arr(envi)
            env = np.insert(env,4,2).reshape(3,3)
            envi_a = arr2int(env[0])
            envi_b = arr2int(env[:,0])
            envi_c = arr2int(env[1])
            envi_d = arr2int(env[:,1])

            # sti, ei -> stx
            txs[sti][envi] = stx
            # syntactic distinctions
            sobs[sti][stx].add(envi)


















#
