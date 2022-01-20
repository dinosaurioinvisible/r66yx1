
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

# ring locations (top to bottom, left to right)
def ring_locs(i=0,j=0,r=1,hollow=True):
    locs = []
    for ir in range(-r,r+1):
        ij = set([abs(ir)-r,r-abs(ir)]) if hollow == True else [jx for jx in range(abs(ir)-r,r-abs(ir)+1)]
        for jr in ij:
            locs.append([i+ir,j+jr])
    locs = sorted(locs)
    return locs
