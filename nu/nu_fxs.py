
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
def arr2int(a,b=[],rot=None,transp=False,inv=False):
    # int to matrix
    if inv:
        ax = np.asarray([int(i) for i in np.binary_repr(a,9)]).reshape(3,3)
        return ax
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

'''convert active membrane/wall pattern to int (clockwise)'''
def ext2int(ma):
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.flip(ma[-1,:]),np.flip(ma[:,0])]
    # if nothing
    if np.sum(ma_arrs)==0:
        return 0
    # linear array
    ma_ux = np.concatenate((ma_arrs[0][:-1],ma_arrs[1][:-1],ma_arrs[2][:-1],ma_arrs[3][:-1]))
    cn = len(ma_arrs[0])-1
    ei = ma_ux.argmax()
    wi = int(ei/cn)
    # one active vertex element (vals: 1 or 16/64 (first/last))
    if np.sum(ma_ux)==1 and ei%cn==0:
        # for simplicity just 1 (assuming some symmetry)
        return 1
    # 1 wall cases (1 central or more than 1 element)
    for wx in ma_arrs:
        if np.sum(wx)==np.sum(ma_ux):
            wx_int = arr2int(wx)
            return wx_int
    # 2 walls cases
    wl = ma_arrs[(wi+1)%4][:-1]
    wr = ma_arrs[(wi-1)%4][1:]
    if np.sum(wl)>0 and np.sum(wr)==0:
        wx = np.concatenate((wl,ma_arrs[wi]))
    elif np.sum(wl)==0 and np.sum(wr)>0:
        wx = np.concatenate((ma_arrs[wi],wr))
    # 3 or 4 walls?
    else:
        print("more than 2 walls?")
        import pdb; pdb.set_trace()
    wx_int = arr2int(wx)
    return wx_int





###
