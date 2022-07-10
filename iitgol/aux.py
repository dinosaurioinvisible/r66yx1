
import numpy as np

# convert int repr into 3x3 matrix
def int2glx(n,arr_len=9):
    # needs to be reversed for assignation to elements [e0,e1,e2...]
    x = np.array([int(i) for i in np.binary_repr(n,arr_len) [::-1]])
    x = x.reshape(3,3)
    return x

# glider valid st txs in empty env
def mkglider():
    # some glider base cfgs (this cycle moves south west)
    gi = np.array([[np.nan,np.nan,0,0,0],[0,0,0,1,0],[0,1,0,1,0],[0,0,1,1,0],[np.nan,0,0,0,0]])
    gx = np.array([[0,0,0,np.nan,np.nan],[0,1,0,0,0],[0,0,1,1,0],[0,1,1,0,0],[0,0,0,0,np.nan]])
    # tensor for storing cfgs
    sts = np.zeros((16,5,5))
    # transition matrix
    tm = np.zeros((16,16))
    # glider cells states for every cfg
    gls = np.zeros((25,2,16))
    # SE, NE, NW, SW
    for r in range(4):
        sts[4*r+0] = np.rot90(gi,r)
        sts[4*r+1] = np.rot90(gx,r)
        sts[4*r+2] = np.rot90(np.transpose(gi),r)
        sts[4*r+3] = np.rot90(np.transpose(gx),r)
        # txs, only for the empty case
        for j in range(4):
            tm[4*r+j,4*r+(j+1)%4] = 1
    # individual elements states
    for i in range(5):
        for j in range(5):
            gls[5*i+j,0] = np.abs(sts[:,i,j]-1)
            gls[5*i+j,1] = sts[:,i,j]
    # indeces of (local) purviews for indiv cells
    pws = np.zeros((25,2,9,16))
    # matrix of indeces
    w = np.zeros((7,7))
    w.fill(np.nan)
    w[1:6,1:6] = np.arange(25).reshape(5,5)
    # indices
    for i in range(1,6):
        for j in range(1,6):
            ijs = w[i-1:i+2,j-1:j+2]
            # 9 cells in pw x 16 glider cfgs (1 if val=1/0 == cell val in cfg)
            pws[5*(i-1)+j-1,0] = np.array([gls[int(ij),0] if not np.isnan(ij) else np.zeros(16) for ij in ijs.flatten()])
            pws[5*(i-1)+j-1,1] = np.array([gls[int(ij),1] if not np.isnan(ij) else np.zeros(16) for ij in ijs.flatten()])
    # nans aren't needed here (only 1 increases probs)
    pws = np.where(np.isnan(pws),0,pws)
    # effect matrices
    ems = np.zeros((25,16,16))
    for i in range(25):
        em = np.nansum(tm*gls[i,0],axis=1).reshape(16,1)*gls[i,0]+np.nansum(tm*gls[i,1],axis=1).reshape(16,1)*gls[i,1]
        ems[i] = np.where(np.isnan(em),0,em)
    return sts,tm,gls,pws,ems


# tensor with 512 flattened 3x3 reps
def flat_mxrep():
    f = np.zeros((512,9))
    for i in range(512):
        f[i] = int2glx(i).flatten()
    return f

# tensor with 3x3 matrix reps
def matrix_reps(e=512,n=3,m=3):
    t = np.zeros((e,n,m))
    for i in range(e):
        gl = int2glx(i)
        t[i] = gl
    return t

# distance matrix for EMD
def mkdm(sts):
    s = sts.reshape(16,25)
    dm = np.array([np.nansum(abs(s-s[i]),axis=1) for i in range(16)])
    return dm








#
