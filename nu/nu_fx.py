
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

'''group common vals in array'''
def arr2group(x,vals=4,xmax=False,bin=False):
    gi = []
    for vi in range(0,vals):
        gi.append(np.sum(np.where(x==vi,1,0)))
    if xmax:
        xmi = sorted([[xvi,xi] for xi,xvi in enumerate(gi)])[-1][1]
        if bin:
            xbi = [int(i) for i in np.binary_repr(xmi,2)]
            return xbi
        return xmi
    return gi

'''membrane signaling reaction'''
def membrane_fx(domain,me_ij=[],mx=None):
    mdomain=np.zeros((7,7))
    # reacts if any external cell is active
    if len(me_ij)>0:
        domain[1:6,1:6] = 0
        for [i,j] in me_ij:
            if np.sum(domain[i-1:i+2,j-1:j+2]) > 0:
                mdomain[i][j] = 1
        membrane = mdomain[1:6,1:6]
    # reacts if external input > internal input
    else:
        for j in range(1,6):
            mdomain[1][j] += np.sum(domain[0,j-1:j+2])-np.sum(domain[2,max(2,j-1):min(j+2,5)])
            mdomain[5][j] += np.sum(domain[6,j-1:j+2])-np.sum(domain[4,max(2,j-1):min(j+2,5)])
        for i in range(1,6):
            mdomain[i][1] += np.sum(domain[i-1:i+2,0])-np.sum(domain[max(2,i-1):min(i+2,5),2])
            mdomain[i][5] += np.sum(domain[i-1:i+2,6])-np.sum(domain[max(2,i-1):min(i+2,5),4])
        membrane = np.where(mdomain[1:6,1:6]>0,1,0)
    if not mx:
        return membrane
    # sum of all active external cells
    if mx=="all":
        msx = np.sum(membrane)
    # sum as 4 walls
    if mx==4:
        me = np.where(np.asarray([np.sum(membrane[0,:]),np.sum(membrane[:,4]),np.sum(membrane[4,:]),np.sum(membrane[:,0])])>0,1,0)
        msx = arr2int(me)
    # sum as corners + walls
    if mx==8:
        ml = np.sum(membrane[1:4,0])
        mr = np.sum(membrane[1:4,4])
        mu = np.sum(membrane[0,1:4])
        md = np.sum(membrane[4,1:4])
        mul = membrane[0][0]
        mur = membrane[0][4]
        mdl = membrane[4][0]
        mdr = membrane[4][4]
        me = np.where(np.asarray([mul,mu,mur,ml,mr,mdl,md,mdr])>0,1,0)
        msx = arr2int(me)
    # get encountered dash (only for 1 wall)
    if mx=="dash":
        d0 = domain[0,:]
        d1 = domain[:,6]
        d2 = domain[6,:]
        d3 = domain[:,0]
        dm = [d0,d1,d2,d3]
        di = np.asarray([np.sum(dx) for dx in dm]).argmax()
        msx = arr2int(dm[di])
    if not mx:
        raise Exception("mx argument unknown")
    return membrane,msx

'''convert (2) active borders of matrix to int (clockwise)'''
def ext2int(ma):
    mx = np.zeros(11)
    # ext membrane/walls values (clockwise)
    ma_arrs = [ma[0,:],ma[:,-1],np.rot90(ma,2)[0,:],np.rot90(ma,2)[:,-1]]
    ma_wx = [i for i,a in enumerate(ma_arrs) if np.sum(a)>0]
    # assuming a max of 2 consecutive walls interaction
    if len(ma_wx)==0:
        return 0
    # array start from the first wall clockwise 01,12,23,30
    elif len(ma_wx)==1:
        wxs = [3,0] if ma_wx==[3] else [ma_wx[0],ma_wx[0]+1]
    elif len(ma_wx)==2:
        wxs = [3,0] if ma_wx==[0,3] else ma_wx
    # should be common, as corners count for 2 different walls
    elif len(ma_wx)==3:
        # center + higher left or right (consecutive walls)
        ma_wx = [2,3,0] if ma_wx==[0,2,3] else ma_wx
        wl = np.sum(ma_arrs[ma_wx[0]])
        wr = np.sum(ma_arrs[ma_wx[2]])
        # so in case of wl==wr: wr
        wxs = ma_wx[:2] if wl>wr else ma_wx[1:]
    else:
        ma_sx = [(np.sum(mi),i) for i,mi in enumerate(ma_arrs)]
        wi,wj = sorted(ma_sx)[2:]
        wxs = wj[1],wi[1] if wj[0]>wi[0] and wj[1]==3 else wi[1],wj[1]
    # wall starting index
    mx[:2] = [int(i) for i in np.binary_repr(wxs[0],2)]
    # individual element values for those 2 walls
    mx[2:] = np.concatenate((ma_arrs[ma_wx[0]],ma_arrs[ma_wx[1]][1:]))
    # int representation
    mx_int = arr2int(mx)
    return mx_int

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
            b = np.rot90(b.reshape(dim,dim),rot)
    xa = int(''.join(a.flatten().astype(int).astype(str)),2)
    if ab:
        xb = int(''.join(b.flatten().astype(int).astype(str)),2)
        return xa,xb
    return xa














###
