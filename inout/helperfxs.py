
import numpy as np

# convert array > binary > int
def matrix2int(matrix,rot=None):
    if r:
        matrix = np.rot90(matrix,rot)
    x = int(''.join(matrix.flatten().astype(int).astype(str)),2)
    return x

# convert int number into a NxN matrix
def int2matrix(nx,dims=3):
    nx_len = dims**2
    x = np.array([int(i) for i in np.binary_repr(nx,nx_len)]).reshape(dims,dims)
    return x

# convert an external layer into int
def layer2int(matrix,rot=None):
    if r:
        matrix = np.rot90(mat,rot)
    matrix = np.concatenate((matrix[0],matrix[:,-1][1:-1],np.flip(matrix[-1]),np.flip(matrix[:,0][1:-1])))
    x = arr2int(matrix)
    return x

def rhombus2int(rhombus):


# rhomb locations (top to bottom)
def rhombus_locs(i=0,j=0,r=1,hollow=True):
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
