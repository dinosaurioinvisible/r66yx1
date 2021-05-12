
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

'''internal versus external input for membrane'''
def membrane_fx(domain):
    mdomain=np.zeros((7,7))
    for j in range(1,6):
        mdomain[1][j] += np.sum(domain[0,j-1:j+2])-np.sum(domain[2,max(2,j-1):min(j+2,5)])
        mdomain[5][j] += np.sum(domain[6,j-1:j+2])-np.sum(domain[4,max(2,j-1):min(j+2,5)])
    for i in range(1,6):
        mdomain[i][1] += np.sum(domain[i-1:i+2,0])-np.sum(domain[max(2,i-1):min(i+2,5),2])
        mdomain[i][5] += np.sum(domain[i-1:i+2,6])-np.sum(domain[max(2,i-1):min(i+2,5),4])
    membrane = np.where(mdomain[1:6,1:6]>0,1,0)
    return membrane

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
    # if rot and transp: transposes first!
    if transp:
        a = a.reshape(dim,dim).transpose(1,0)
        if ab:
            b = b.reshape(dim,dim).transpose(1,0)
    if rot:
        a = np.rot90(a.reshape(dim,dim),rot)
        if ab:
            b = np.rot90(a.reshape(dim,dim),rot)
    xa = int(''.join(a.flatten().astype(int).astype(str)),2)
    if ab:
        xb = int(''.join(b.flatten().astype(int).astype(str)),2)
        return xa,xb
    return xa
