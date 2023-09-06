
import numpy as np
from pyemd import emd

# single cell in the GoL 

# counting x->y
count = np.array([[200, 56], [172, 84]])

# transition matrix for x
# given x, what are the probs for y
# every value divided by the sum of the rows (values for x)
tm_x = count/np.sum(count,axis=1)

# transition matrix for y
# given y, the probs of x
# knowing y, it is each value divided by the vertical sum (values of y)
# then transposed, so it is in function of y->x instead of x->y
tm_y = (count/np.sum(count,axis=0)).T

# distance matrices
# for every x and y value of a,b,...,n elements: sqrt( (ax-bx)**2 + (ay-by)**2 )
# basically the euclidian distance for every comparison
def make_dm(tm):
    dim = tm.shape[0]
    dm = np.zeros((dim,dim))
    for ei,i in enumerate(tm):
        for ej,j in enumerate(tm):
            dm[ei,ej] = np.sqrt((i[0]-j[0])**2 + (i[1]-j[1])**2)
    return dm
dm_x = make_dm(tm_x)
dm_y = make_dm(tm_y)

# distributions for x=0 -> y=1
py_x0 = tm_x[0]
py_x1 = tm_x[1]
px_y0 = tm_y[0]
px_y1 = tm_y[1]

# unconstrained distributions
ucx = np.sum(count,axis=1)
ucx = ucx/np.sum(ucx)
ucy = np.sum(count,axis=0)
ucy = ucy/np.sum(ucy)

# cause and effect info 
def info(x,y,cxy=count):
    # tms
    tmx = cxy/np.sum(cxy,axis=1)
    tmy = np.ascontiguousarray((cxy/np.sum(cxy,axis=0)).T)
    # distributions
    px_y = tmy[y]
    py_x = tmx[x]
    # ucs
    ucx = np.sum(count,axis=1)
    ucx = ucx/np.sum(ucx)
    ucy = np.sum(count,axis=0)
    ucy = ucy/np.sum(ucy)
    # distance matrices
    dmx = make_dm(tmx)
    dmy = make_dm(tmy)    
    # ci and ei
    ci = emd(px_y,ucx,dmx)
    ei = emd(py_x,ucy,dmy)
    print('ci = EMD(p(sx|sy={})||ucx) : {}'.format(y,ci))
    print('ei = EMD(p(sx|sy={})||ucx) : {}'.format(x,ei))
    return ci,ei
