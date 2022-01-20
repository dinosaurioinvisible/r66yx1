
import numpy as np

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

# convert an external layer into int
def layer2int(matrix,rot=None):
    if r:
        matrix = np.rot90(mat,rot)
    matrix = np.concatenate((matrix[0],matrix[:,-1][1:-1],np.flip(matrix[-1]),np.flip(matrix[:,0][1:-1])))
    x = arr2int(matrix)
    return x

# convert into matrix with ring inside
def int2ring(n,r):
    dim = 2*r+1
    ring_space = np.zeros((dim,dim)).astype(int)
    ring_len = 4*r
    sts = int2arr(n,ring_len)
    locs = ring_locs(i=r,j=r,r=r)
    for st,[i,j] in zip(sts,locs):
        ring_space[i][j] = st
    return ring_space

# convert ring into int
def ring2int(ring_domain,i,j,r,hollow=True):
    arr = []
    locs = ring_locs(i=i,j=j,r=r)
    for [vi,vj] in locs:
        vx = ring_domain[vi][vj]
        arr.append(vx)
    x = arr2int(np.asarray(arr))
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

# locations around some center
def ij_around(i=0,j=0,r=1,hollow=True):
    locs = []
    for xi in range(-r,r+1):
        ij = [-r,r] if hollow == True and -r<xi<r else [jx for jx in range(-r,r+1)]
        for xj in ij:
                locs.append([i+xi,j+xj])
    return locs











#
