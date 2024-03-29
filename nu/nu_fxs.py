
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

'''v5 of the same, just go with the whole thing'''
def ext2int(ma):
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.flip(ma[-1,:]),np.flip(ma[:,0])]
    # if nothing
    if np.sum(ma_arrs)==0:
        return 0
    # membrane to int (0 : 65.536) (2**16), env (0 : 16,777,216) (2**24)
    # 0: north and so on clockwise (flip for continuity of array)
    me = np.concatenate((ma[0,:][:-1],ma[:,-1][:-1],np.flip(ma[-1,:][:-1]),np.flip(ma[:,0][:-1])))
    # flip so that ma[0][0]=1 and so on
    mx = int(''.join(np.flip(me).astype(str)),2)
    return mx

'''core st -> loosely visually based int,int (for plotting)'''
def core2core(cx):
    ax = np.asarray([int(i) for i in np.binary_repr(cx,9)])
    # x: higher -> E, lower -> W
    x = [ax[2],ax[5],ax[8],ax[4],ax[0],ax[3],ax[6]]
    xi = arr2int(np.asarray(x))
    # y: higher -> N, lower -> S
    y = [ax[0],ax[1],ax[2],ax[4],ax[6],ax[7],ax[8]]
    yi = arr2int(np.asarray(y))
    return xi,yi

'''convert from full int to aprox. int'''
def reduce(arr,bin_pos=16):
    mi = [int(i) for i in np.binary_repr(arr,bin_pos)]
    # insert last elements for first corner wall
    for xe in range(int(bin_pos/8)-1):
        mi.insert(0+xe,mi[-1-xe])
    msi = []
    # size of wall part
    psize = int(bin_pos/8)+1
    pstep = int(bin_pos/8)
    for i in range(8):
        si = np.sum(mi[i*pstep:(i*pstep)+psize])
        msi.append(si)
    msi = np.asarray(np.flip(msi))
    msi = np.where(msi>0,1,0)
    mxi = arr2int(msi)
    return mxi



###
