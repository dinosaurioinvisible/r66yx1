
import numpy as np
import pickle

# convert array > binary > int
def arr2int(arr,rot=None):
    if rot:
        arr = np.rot90(arr,rot)
    x = int(''.join(arr.flatten().astype(int).astype(str)),2)
    return x

# convert int number into an array or a NxN matrix
def int2arr(n,arr_len,dims=1):
    x = np.array([int(i) for i in np.binary_repr(n,arr_len)])
    if dims > 1:
        x = x.reshape(dims,dims)
    return x

# ring locations (top to bottom, left to right)
def ring_locs(i=0,j=0,r=1,hollow=True):
    locs = []
    for ir in range(-r,r+1):
        ij = set([abs(ir)-r,r-abs(ir)]) if hollow == True else [jx for jx in range(abs(ir)-r,r-abs(ir)+1)]
        for jr in ij:
            locs.append([i+ir,j+jr])
    locs = sorted(locs)
    return locs

# distance matrix
def dist_matrix(dim=8,cost=0.5):
    dm = np.zeros((dim,dim))
    for i in range(dim):
        bin_i = int2arr(i,3)
        for j in range(dim):
            bin_j = int2arr(j,3)
            dij = np.sum([abs(bi-bj) for bi,bj in zip(bin_i,bin_j)])
            dm[i][j] = cost * dij
    return dm

# convert ring world > ring environment > int
def env2int(world,i=None,j=None):
    # if not centered
    i = int(world.shape[0]/2) if not i else i
    j = int(world.shape[1]/2) if not j else j
    # assuming ring of 4 elements
    env = world[i-2:i+3,j-2:j+3].flatten()
    for dx in [24,20,17,13,12,11,7,4,0]:
        env = np.delete(env,dx)
    xi = arr2int(env)
    return xi

# only for ring envs (16 elements)
def int2ring_env(xi,unknown=0):
    env = int2arr(xi,arr_len=16)
    for di in [0,4,7,11,12,13,17,20,24]:
        env = np.insert(env,di,unknown)
    env = env.reshape(5,5)
    return env






















#
