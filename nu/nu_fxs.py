
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
def ext2int(ma,index=True):
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.flip(ma[-1,:]),np.flip(ma[:,0])]
    ma_n = len(ma_arrs[0])-1
    # check if nothing
    if np.sum(ma_arrs)==0:
        return 0
    # first and last active cells
    ma_arr = np.concatenate((ma_arrs[0][:-1],ma_arrs[1][:-1],ma_arrs[2][:-1],ma_arrs[3][:-1]))
    mi = ma_arr.argmax()
    mn = len(ma_arr)-np.flip(ma_arr).argmax()
    # if only 1: center around that

    # starting corner index (0=NW, 1=NE, 2=SE, 3=SW)
    ei,en = int(mi/ma_n),int(mn/ma_n)
    ew0 = en if ei==0 and en==3 else ei
    ew1 = (ew0+1)%ma_n
    # combined as int or list
    if index:
        # vector = index & elements from 2 adjacent walls
        mx = np.zeros((ma_n*2)+3)
        mx[:2] = [int(i) for i in np.binary_repr(ew0,2)]
        mx[2:] = np.concatenate((ma_arrs[ew0],ma_arrs[ew1][1:]))
    else:
        # return list of dash patterns from walls
        if np.sum(ma_arrs[ew1][1:])>0:
            mx = np.concatenate((ma_arrs[ew0],ma_arrs[ew1][1:]))
        else:
            mx = ma_arrs[ew0]
    mx_int = arr2int(mx)
    return mx_int







###
