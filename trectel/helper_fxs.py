
import numpy as np

# convert array > binary > int
def arr2int(arr):
    xi = np.sum([x<<e for e,x in enumerate(arr.flatten().astype(int))])
    return xi

# convert int number into an array or a NxN matrix
def int2arr(n,arr_len,dims=1):
    # needs to be reversed for assignation to elements [e0,e1,e2...]
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    if dims > 1:
        x = x.reshape(dims,dims)
    return x

# list of bin<->int conversions
# (to avoid calling the fxs all the time)
def bin2int(n):
    b2i = {}
    for ni in range(2**n):
        nb = int2arr(ni,arr_len=n)
        b2i[tuple(nb)] = ni
    return b2i

def int2bin(n):
    i2b = {}
    for ni in range(2**n):
        nb = int2arr(ni,arr_len=n)
        i2b[ni] = nb
    return i2b

# cell locations (domain=21, env=16, sys=5)
def ddxlocs(r):
    ij = []
    env_js = [[1,2,3],[0,1,3,4],[0,4],[0,1,3,4],[1,2,3]]
    sys_js = [[],[2],[1,2,3],[2],[]]
    for i in range(5):
        # domain
        if r==21:
            j0,jn = (1,4) if i%4==0 else (0,5)
            for j in range(j0,jn):
                ij.append([i,j])
        # environment only
        elif r==16:
            for j in env_js[i]:
                ij.append([i,j])
        # ring system
        elif r==5:
            for j in sys_js[i]:
                ij.append([i,j])
    return ij

# tensor for 2d domains
def ddxtensor(r):
    # non empty locations
    ij = ddxlocs(r)
    # tensor object
    ddx = np.zeros((5,5,2**r))
    for er,[ei,ej] in enumerate(ij):
        ezr = 2**er
        ez0 = np.zeros(ezr)
        ez1 = np.ones(ezr)
        ez01 = np.concatenate((ez0,ez1))
        dez = 2**(r-er-1)
        ezt = np.full((dez,len(ez01)),ez01).flatten()
        ddx[ei,ej,:] = ezt
    return ddx.astype(int)

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
def dist_matrix(dim=8,cost=1):
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
