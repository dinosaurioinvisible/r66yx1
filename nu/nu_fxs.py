
import numpy as np

''' i,j coords around some x,y'''
def xy_around(x,y,r=1,inv=False,ext=False):
    axy = []
    if inv:
        for j in range(-r,r+1,1):
            for i in range(-r,r+1):
                axy.append([y+j,x+i])
    else:
        for j in range(r,(-r-1),-1):
            for i in range(-r,(r+1)):
                axy.append([y+j,x+i])
    if ext:
        size = 2**r+1
        for dr in range(size-r,0,-1):
            del(axy[int(size*dr+1):int(size*(dr+1)-1)])
    return np.asarray(axy)

'''convert array into int'''
def arr2int(a,b=[],rot=None,transp=False):
    # check for second array
    ab = True if len(a)==len(b) else False
    # check if it's a matrix (just in case)
    if len(a.shape) > 1:
        a = a.flatten()
        if ab:
            b = b.flatten()
    dim = int(np.sqrt(a.shape))
    # if rot and transp: transposes first !
    if transp:
        a = a.reshape(dim,dim).transpose(1,0)
        if ab:
            b = b.reshape(dim,dim).transpose(1,0)
    if rot:
        a = np.rot90(a.reshape(dim,dim),rot)
        if ab:
            b = np.rot90(b.reshape(dim,dim),rot)
    xa = int(''.join(a.flatten().astype(int).astype(str)),2)
    if ab:
        xb = int(''.join(b.flatten().astype(int).astype(str)),2)
        return xa,xb
    return xa

'''convert active borders of matrix to int (clockwise)'''
def ext2int(ma,oxy):
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.flip(ma[-1,:]),np.flip(ma[:,0])]
    ma_oxy = ma_arrs[oxy]
    # check if nothing
    if np.sum(ma_arrs)==0:
        return 0
    # which walls have active elements
    wx = []
    ma_wx = [ma_arrs[0][:-1],ma_arrs[1][:-1],ma_arrs[2][:-1],ma_arrs[3][:-1]]
    for wi in range(len(ma_arrs)):
        # 1 wall cases (all active cells in same wall)
        if np.sum(ma_wx)==np.sum(ma_arrs[wi]):
            mx_int = arr2int(ma_arrs[wi])
            return mx_int
        # 2 or more walls
        if np.sum(ma_arrs[wi])>0:
            wx.append(wi)
    # wall indeces
    if len(wx)==1:





    # 2 walls cases
    ml = ma_arrs[(oxy-1)%4][:-1]
    mr = ma_arrs[(oxy+1)%4][1:]
    if np.sum(ml)>0 and np.sum(mr)==0:
        mx = np.concatenate((np.array(ml),ma_oxy))
        mx_int = arr2int(mx)
        return mx_int
    elif np.sum(ml)==0 and np.sum(mr)>0:
        mx = np.concatenate((ma_oxy,np.array(mr)))
        mx_int = arr2int(mx)
        return mx_int
    # 3 or 4 walls?
    else:
        print("more than 2 walls?")
        #import pdb; pdb.set_trace()
        return -1





###
