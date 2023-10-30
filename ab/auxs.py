
import numpy as np
from tqdm import tqdm

# int > binary array
def int2array(ni,arr_len,mn=1):
    # reversed for cell order
    x = np.array([int(i) for i in np.binary_repr(ni,arr_len) [::-1]])
    if mn > 1:
        return x.reshape(mn,mn)
    return x

# array to int
def array2int(arr):
    xi = np.sum([x<<e for e,x in enumerate(arr.flatten().astype(int))])
    return xi

# fxs that return ids of the arrays of a matrix that:
# sum = x; higher than x; lower than x; nonzero
def sum_is(matrix,x,axis=1,arrays=False):
    if arrays:
        return matrix[np.where(np.sum(matrix,axis=axis)==x)[0]]
    return np.where(np.sum(matrix,axis=axis)==x)[0]
def sum_in_range(matrix,rl,rh,axis=1,arrays=False):
    ids = np.where(np.logical_and(np.sum(matrix,axis=axis)>=rl,np.sum(matrix,axis=axis)<=rh))[0]
    if arrays:
        return matrix[ids]
    return ids
def sum_higher(matrix,x,axis=1,arrays=False):
    if arrays:
        return matrix[np.where(np.sum(matrix,axis=axis)>x)[0]]
    return np.where(np.sum(matrix,axis=axis)>x)[0]
def sum_lower(matrix,x,axis=1,arrays=False):
    if arrays:
        return matrix[np.where(np.sum(matrix,axis=axis)<x)[0]]
    return np.where(np.sum(matrix,axis=axis)<x)[0]
def sum_nonzero(matrix,axis=1,arrays=False):
    if arrays:
        return matrix[np.sum(matrix,axis=axis).nonzero()[0]]
    return np.sum(matrix,axis=axis).nonzero()[0]

# to check if some sx is surrended by zeros in some domx 
def sum_borders(domx):
    cx = np.sum(domx[1:-1,1:-1])
    return np.sum(domx)-cx
# expand domain size: rows/cols=(bef 0,aft n), else layers
def expand_domain(sx,layers=1,rows=(0,0),cols=(0,0)):
    if np.sum([rows,cols])>0:
        return np.pad(sx,(rows,cols),mode='constant')
    return np.pad(sx,layers,mode='constant')
# expand one layer for multiple domains
def expand_multiple_domains(dxs,sx=()):
    ms,ns = sx.shape if len(sx)>0 else [np.sqrt(dxs.shape[1]).astype(int)]*2
    e_dxs = np.zeros((dxs.shape[0],(ms+2)*(ns+2)))
    sx_ids = expand_domain(np.ones((ms,ns))).flatten().nonzero()[0]
    e_dxs[:,sx_ids] = dxs
    return e_dxs

# adjust domains to bigger, for each dimension
def adjust_domains(x1,x2):
    # n rows/cols to fill     
    rx,cx = np.abs(np.array(x1.shape)-np.array(x2.shape))
    r0,rn = [int(rx/2)]*2 if rx%2==0 else [int(rx/2),int(rx/2)+1]
    c0,cn = [int(cx/2)]*2 if cx%2==0 else [int(cx/2),int(cx/2)+1]
    # if one is bigger than the other
    if x1.shape[0] >= x2.shape[0] and x1.shape[1] >= x2.shape[1]:
        return x1,expand_domain(x2,rows=(r0,rn),cols=(c0,cn))
    if x2.shape[0] >= x1.shape[0] and x2.shape[1] >= x1.shape[1]:
        return expand_domain(x1,rows=(r0,rn),cols=(c0,cn)),x2
    # one is bigger in rows, the other in cols
    if x1.shape[0] > x2.shape[0]:
        x2 = expand_domain(x2,rows=(r0,rn))
    elif x1.shape[0] < x2.shape[0]:
        x1 = expand_domain(x1,rows=(r0,rn))
    if x1.shape[1] > x2.shape[1]:
        x2 = expand_domain(x2,cols=(c0,cn))
    elif x1.shape[1] < x2.shape[1]:
        x1 = expand_domain(x1,cols=(c0,cn))
    return x1,x2

# make canonical gol patterns (sx,e=0) from word inputs
def mk_gol_pattern(px):
    if px == 'block':
        dx = np.zeros((4,4))
        dx[1:-1,1:-1] = 1
    elif px == 'blinker':
        d1 = np.zeros((5,3))
        d1[1:-1,1] = 1
        d2 = np.ascontiguousarray(d1)
        dx = [d1,d2]
    elif px == 'glider':
        dx = []
        d1 = np.zeros((5,5))
        d1[1,2] = 1
        d1[2,3] = 1
        d1[3,1:-1] = 1
        d2 = np.zeros((5,5))
        d2[1,1] = 1
        d2[2:-1,2] = 1
        d2[1:3,3] = 1
        for di in [d1,d2]:
            for ri in range(4):
                dr = np.rot90(di,ri)
                dt = np.ascontiguousarray(dr.T)
                dx.extend([dr,dt])
    return dx

# pass set of arrays into tensor of gol domains for visualization
# dxs: matrix with arrays of gol sts
# sx form for reshaping
def mk_dxs_tensor(dxs,sx):
    if dxs.shape[1] != sx.flatten().shape[0]:
        sx = expand_domain(sx)
    sxi,sxj = sx.shape
    tgol = np.zeros((dxs.shape[0],sxi,sxj))
    for di,dx in enumerate(dxs):
        tgol[di] = dx.reshape(sxi,sxj)
    return tgol

# split using rows/cols=0
def rm_env(dx,nc=2):
    dom = dx*1
    # first/last row/col dont change results
    r0 = sum_is(dom[1:-1],0)+1
    c0 = sum_is(dom[:,1:-1],0,axis=0)+1
    i0,j0 = 0,0
    # basically split by rows/cols=0
    if np.sum(r0)>0:
        for i in list(r0)+[dom.shape[0]]:
            if np.sum(dom[i0:i]) <= nc:
                dom[i0:i] = 0
                i0 = i
            else:
                c0 = sum_is(dom[i0:i],0,axis=0)
                for j in list(c0)+[dom.shape[0]]:
                    if np.sum(dom[i0:i,j0:j]) <= nc:
                        dom[i0:i,j0:j] = 0
                    j0 = j
            i0,j0 = i,0
        return dom
    for j in list(c0)+[dom.shape[1]]:
        if np.sum(dom[:,j0:j]) <= nc:
            dom[:,j0:j] = 0
            j0 = j
        else:
            r0 = sum_is(dom[:,j0:j],0)
            for i in list(r0)+[dom.shape[1]]:
                if np.sum(dom[i0:i,j0:j]) <= nc:
                    dom[i0:i,j0:j] = 0
                    i0 = i
        j0,i0 = j,0
    return dom

# expand domain for rolling correctly
# basically they should mantain the dist among act cells
def check_translation(x1,x2r,x2t):
    n,m = x1.shape
    b1 = np.zeros((n+2,m+2))
    b1[1:-1,1:-1] = x1
    bx1 = b1.flatten().nonzero()[0]
    bx1 = np.abs(bx1-bx1[0])
    b2r = np.zeros((n+2,m+2))
    b2r[1:-1,1:-1] = x2r
    bx2r = b2r.flatten().nonzero()[0]
    if np.array_equal(bx1,np.abs(bx2r-bx2r[0])):
        return True
    if np.array_equal(bx1,np.abs(np.flip(bx2r-bx2r[0]))):
        return True
    b2t = np.zeros((n+2,m+2))
    b2t[1:-1,1:-1] = x2t
    bx2t = b2t.flatten().nonzero()[0]
    if np.array_equal(bx1,np.abs(bx2t-bx2t[0])):
        return True
    if np.array_equal(bx1,np.abs(np.flip(bx2t-bx2t[0]))):
        return True
    return False

# game of life transition
# expanded adds an external layer
def gol_step(world_st,expanded=False):
    world = world_st*1 if not expanded else expand_domain(world_st)
    world_copy = world*1
    for ei,vi in enumerate(world_copy):
        for ej,vij in enumerate(vi):
            nb = np.sum(world_copy[max(0,ei-1):ei+2,max(ej-1,0):ej+2]) - vij
            vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and nb==3) else 0
            world[ei,ej] = vx
    return world
# gol transition for multiple arrays
# sx_domains: gol lattice/domain arrays for each sx -> sy
# sx: matrix form to reshape arrays 
# mk_zero: makes sums<3 = 0 (will die next)
def multi_gol_step(sx_domains,sx,mk_zero=True,expanded=False):
    # shape & output array
    sxys = np.zeros(sx_domains.shape) if not expanded else np.zeros((sx_domains.shape[0],expand_domain(sx).flatten().shape[0]))
    # simulate transitions
    for di,dx in enumerate(sx_domains):
        if np.sum(dx)>2:
            sxys[di] = gol_step(dx.reshape(sx.shape),expanded=expanded).flatten()
    if mk_zero:
        sxys[sum_lower(sxys,3)] = 0
    return sxys

# check for patterns 
# domx: gol domain/lattice in matrix form
# e0: empty environment
def is_block(domx,e0=False):
    # no more than block + m0 + full env
    # min m0 = 2 sides = 5 cells
    n,m = domx.shape
    if 4 <= np.sum(domx) <= n*m-5:
        for i in range(n):
            for j in range(m):
                if np.sum(domx[i:i+2,j:j+2]) == 4:
                    if np.sum(domx) == 4:
                        return True
                    if not e0:
                        if np.sum(domx[max(0,i-1):i+3,max(0,j-1):j+3]) == 4:
                            return True
    return False
# same for next timestep
def is_block_next(domx,e0=True,expanded=True):
    # block may be outside of current domain
    domy = gol_step(domx,expanded=expanded)
    return is_block(domy,e0)
# blinker
def is_blinker(domx):
    if np.sum(domx) == 3:
        vsum = np.sum(domx,axis=0)
        hsum = np.sum(domx,axis=1)
        if 3 in vsum or 3 in hsum:
            return True
    return False

# a tensor for all binary combinations
def mk_binary_domains(n_cells):
    doms = np.zeros((2**n_cells,n_cells)).astype(int)
    for i in range(n_cells):
        f = 2**i
        xi = np.concatenate((np.zeros(f),np.ones(f)))
        n = int(2**n_cells/(2**(i+1)))
        doms[:,-1-i] = np.tile(xi,n)
    return doms

# more general fx, for gol patterns
# domain environmental (sx + env) tensor
# given a block, blinker or any other structure from the gol (sx)
# make all the env arrays for sx
# e_cells are all the cells in the environment
def mk_sx_domains(sx):
    # number of env cells
    # pblock1: 3 active cells in the same region of the block
    if sx == 'block' or sx == 'pblock1':
        e_cells = 12
    # all possibilities of binary domain
    doms = mk_binary_domains(e_cells)
    # insert sx: for every array, change sx cells into 1
    if sx=='block':
        doms = np.insert(doms,(5,5,7,7),1,axis=1)
    elif sx=='pblock1':
        # corner cell not part of env domain (0 for simplicity)
        doms = np.insert(doms,3,0,axis=1)
        doms = np.insert(doms,(5,8,8),1,axis=1)
    return doms

# helper fx for continuity
# dxs: matrix of gol domain sts arrays 
# psx: primary pattern/structure determining ct
def apply_ct(dxs,psx,ct_ids=False,non_ct_ids=False):
    if dxs.shape != psx.shape:
        psx = psx.flatten()
    ids = sum_nonzero(dxs*psx)
    if ct_ids:
        return dxs[ids],ids
    if non_ct_ids:
        zero_ids = sum_is(dxs*psx,0)
        return dxs[ids],zero_ids
    return dxs[ids]

# get all sx: sx -> sy
# sy: any specific gol pattern domain (sx,ex)
# requires matrix/lattice input
# sy_px: sy expected pattern ('block','blinker',etc)
# dxs: specific (smaller) domain
def get_sxs_from_sy(sy,sy_px,dxs=[],e0=True,expanded=True,ct=True,print_data=True):
    # array for expected sy
    n,m = sy.shape
    if len(dxs)==0:
        # all possible domains for (sx,ex)
        dxs = mk_binary_domains(n*m)
    # analyze domains transitions
    sxs = []
    for dx in tqdm(dxs):
        if sy_px == 'block':
            if is_block_next(dx.reshape(n,m),e0=e0,expanded=expanded):
                sxs.append(dx)
    sxs = np.array(sxs)
    print('\nproto domains: {}/{}'.format(sxs.shape[0],dxs.shape[0]))
    if ct:
        sxs = apply_ct(sxs,sy)
        print('\nafter CT: {}'.format(sxs.shape[0]))
    if print_data:
        print_ac_cases(sxs,title='proto domains:')
    return sxs

# get sys from sx
# in this case we can't assume what sy is valid or not
# so we should look for self-sustaining resulting patterns
# sx: initial gol pattern in matrix form
# dxs: tensor for all domains for sx
# decay txs: number of sy->z1->z2->...->zn transitions
# mk_zero: auto make zero domains < 3
def get_sxys_from_sx(dxs,sx,mk_zero=True,expanded=True,ct=True,decay_txs=3,expanded_decay=False,decay_ct=True,print_data=True):
    # gol step for every array
    sxys = multi_gol_step(dxs,sx,mk_zero=mk_zero,expanded=expanded)
    nz_ids = sum_nonzero(sxys)
    sxys = sxys[nz_ids]
    if print_data:
        print('\nnon zero dxs in sy: {}/{}'.format(sxys.shape[0],sum_nonzero(dxs).shape[0]))
    dxs = dxs[nz_ids]
    sx = expand_domain(sx) if expanded else sx
    if ct:
        sxys,ct_ids = apply_ct(sxys,sx,ct_ids=True)
        dxs = dxs[ct_ids]
        if print_data:
            print('\nnon zero after CT: {}'.format(sum_nonzero(sxys).shape[0]))
    # decay txs for every array
    if decay_txs>0:
        # y -> z1 -> z2 ->...-> zn decay txs (often 2 or 3) (includes ct)
        sxys,z_ids = mk_dxs_decay(sxys,sx,decay_txs=decay_txs,expanded=expanded_decay,ct=decay_ct,print_data=print_data)
        dxs = dxs[z_ids]
    return dxs,sxys

# check & discard domains transition into 0
# dxs: matrix of arrays for gol domains
# sx: for reshaping gol arrays for sx -> sy txs
def mk_dxs_decay(dxs,sx,decay_txs=2,expanded=False,ct=True,z_arrays=False,print_data=False):
    dzs,psx = dxs*1,dxs*1
    # y -> z transition into future 
    for txi in range(decay_txs):
        dzs = multi_gol_step(dzs,sx,mk_zero=True,expanded=expanded)
        if ct:
            psx = psx if not expanded else expand_multiple_domains(psx,sx)
            nz,non_ct_ids = apply_ct(dzs,psx,non_ct_ids=True)
            dzs[non_ct_ids] = 0
            psx = dzs*1
        if print_data:
            title = 'non zero dzs in tx{}: {}'.format(txi+1,sum_nonzero(dzs).shape[0])
            print_ac_cases(sum_nonzero(dzs,arrays=True),title=title)
    # apply ids only at the end to avoid mismatches
    yz_ids = sum_nonzero(dzs)
    if z_arrays:
        return dxs[yz_ids],dzs[yz_ids],yz_ids
    return dxs[yz_ids],yz_ids

# gets number of cases of n active cells from domain
def get_ac_cases(dxs,ac=0,rl=0,rh=0,arrays=False,ids=False,nonzero=False):
    if ac>0:
        if arrays:
            return sum_is(dxs,ac,arrays=True)
        if ids:
            return sum_is(dxs,ac)
        return sum_is(dxs,ac).shape[0]
    rl,rh = (rl,rh) if rl<rh else (0,dxs.shape[1])
    nz = 0 if nonzero==True else -1
    ids = [sum_is(dxs,ac) for ac in range(rl,rh+1) if sum_is(dxs,ac).shape[0]>nz]
    if arrays:
        return dxs[ids]
    if ids:
        return ids
    return np.array([i.shape[0] for i in ids])
# same, only for printing
def print_ac_cases(dxs,rl=0,rh=0,nonzero=True,title=''):
    rl,rh = (rl,rh) if rh<rh else (0,dxs.shape[1])
    nz = 0 if nonzero==True else -1
    ids = [(ac,len(sum_is(dxs,ac))) for ac in range(rl,rh+1) if sum_is(dxs,ac).shape[0]>nz]
    print()
    print(title)
    for ac,ncases in ids:
        print('acs: {}, cases: {}'.format(ac,ncases))
    total = sum([nc for ac,nc in ids])
    print('total: {}'.format(total))

# look for symmetries from less to more activ cells 
# sxs: matrix of gol sts in array form
# sx: sample/canon for reshaping
def mk_symsets(sxs,sx,incremental=False,print_data=False):
    # for expanded cases
    sx = expand_domain(sx) if sxs.shape[1] != sx.flatten().shape[0] else sx
    n,m = sx.shape
    ncells = n*m
    # symsets arr: for each sx array: ac,symset canon/type id, id (easier later)
    symset_cases = np.zeros((sxs.shape[0],3)).astype(int)
    # list of (ac,ids), if 1 make directly, omit all cases for ac=0
    for ac,id1 in [(ac,sum_is(sxs,ac)[0]) for ac in range(ncells) if sum_is(sxs,ac).shape[0]==1]:
        symset_cases[id1] = [ac,id1,id1]
    ac_sxs = [(ac,sum_is(sxs,ac)) for ac in range(ncells) if sum_is(sxs,ac).shape[0]>1]
    # compare sxs sts
    for ac,ac_ids in ac_sxs:
        for ei,idx in enumerate(ac_ids):
            if symset_cases[idx][0] == 0:
                symset_cases[idx] = [ac,idx,idx]
                for idx2 in ac_ids[ei+1:]:
                    if symset_cases[idx2][0] == 0:
                        if are_symmetrical(sxs[idx].reshape(n,m),sxs[idx2].reshape(n,m)):
                            symset_cases[idx2] = [ac,idx,idx2]
    # ids for all arrays in same symset, and indices for only first case (canon-like)
    symset_cases = np.array(sorted(list(symset_cases),key=lambda x:(x[0],x[1]))).reshape(sxs.shape[0],3)
    symset_ids = np.array(sorted(list(set(symset_cases[:,1]))))
    if print_data:
        print_ac_cases(sxs[symset_ids],title='general symsets:')
    if incremental:
        return mk_incremental_symsets(sxs,sx,symset_cases,symset_ids,print_data=print_data)
    return symset_cases,symset_ids

# check for equivalent instances within symsets
# basically, patterns with more acs should be different to make a new symset
# e.g., if sx_ac=4 and sx_ac=6 are the same plus 2, then: (sx,ei) and (sx,ej)
def mk_incremental_symsets(sxs,sx,sms_cases,pbs_ids,print_data=False):
    sx = expand_domain(sx) if sxs.shape[1] != sx.flatten().shape[0] else sx
    n,m = sx.shape
    checked_pbs = []
    for ei,pbi in enumerate(pbs_ids):
        if pbi not in checked_pbs:
            checked_pbs.append(pbi)
            for pbj in pbs_ids[ei+1:]:
                if are_sx_instances(sxs[pbi].reshape(n,m),sxs[pbj].reshape(n,m)):
                    pbij = np.where(sms_cases[:,1]==pbj)[0]
                    checked_pbs.append(pbj)
                    sms_cases[pbij,1] = pbi
    sms_cases = np.array(sorted(list(sms_cases),key=lambda x:(x[0],x[1]))).reshape(sxs.shape[0],3)
    pbs_ids = np.array(sorted(list(set(sms_cases[:,1]))))
    if print_data:
        print_ac_cases(sxs[pbs_ids],title='incremental symsets:')
    return sms_cases,pbs_ids

# check symmetries in 2 gol domains 
# x1,x2: matrix form gol reps
def are_symmetrical(x1,x2,nrolls=0):
    # if sizes don't match, adjust to the larger one
    if x1.shape != x2.shape:
        x1,x2 = adjust_domains(x1,x2)
    # if not specified, assume all
    nrolls = x1.flatten().shape[0] if nrolls==0 else nrolls
    # rotations
    for ri in range(4):
        # rotations
        x2r = np.rot90(x2,ri)
        if np.array_equal(x1,x2r):
            return True
        # transpositions
        x2rt = np.ascontiguousarray(x2r.T)
        if np.array_equal(x1,x2rt):
            return True
        # translations
        if check_translation(x1,x2r,x2rt):
            return True
    return False

# check for cases where sx appears in a different env
# for the basic cases: sx,e0 <-> sx,ex
# x1: the basic/known instance, to compare against
def are_sx_instances(dx1,dx2):
    x1,x2 = dx1*1,dx2*1
    x2 = rm_env(x2)
    if np.sum(x2) > np.sum(x1):
        x2 = rm_env(x2)
    if np.sum(x1) == np.sum(x2):
        return are_symmetrical(x1,x2)
    return False

# sxs1,sxs2: arrays for gol sts 
# ss1,ss2: symsets from sxs1,sxs2
def check_matching_symsets(sxs,ssx,sxys,ssy,xdims=[0,0],ydims=[0,0]):
    # if not dims, assume squared domains
    if np.sum(xdims)==0:
        xdims = [np.sqrt(sxs[0].shape[0]).astype(int)]*2
    if np.sum(ydims)==0:
        ydims = [np.sqrt(sxys[0].shape[0]).astype(int)]*2
    nx,mx = xdims
    ny,my = ydims
    # output arrray
    matching_ids = []
    # compare according to active cells
    ncells = max(sxs.shape[1],sxys.shape[1])
    for ac in range(ncells):
        if ac in ssx.keys() and ac in ssy.keys():
            for symset_x in ssx[ac]:
                sx = sxs[symset_x[0]].reshape(nx,mx)
                for symset_y in ssy[ac]:
                    sy = sxys[symset_y[0]].reshape(ny,my)
                    if are_symmetrical(sx,sy):
                        matching_ids.append([symset_x[0],symset_y[0]])
    print('\nmatching_ids:')
    for i,j in matching_ids:
        print(i,j)
    return matching_ids

# distance matrices for intrinsic info
# for every x and y value of a,b,...,n elements: sqrt( (ax-bx)**2 + (ay-by)**2 )
# basically the euclidian distance for every comparison
def make_dms(count):
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
    dim = tm_x.shape[0]
    # fill x
    dmx = np.zeros((dim,dim))
    for ei,i in enumerate(tm_x):
        for ej,j in enumerate(tm_x):
            dmx[ei,ej] = np.sqrt((i[0]-j[0])**2 + (i[1]-j[1])**2)
    # fill y 
    dmy = np.zeros((dim,dim))
    for ei,i in enumerate(tm_y):
        for ej,j in enumerate(tm_y):
            dmy[ei,ej] = np.sqrt((i[0]-j[0])**2 + (i[1]-j[1])**2)
    return dmx,dmy

# saving and loading with pickle
def save_as(file,name,ext=''):
    import pickle
    import os
    fname = '{}.{}'.format(name,ext)
    while os.path.isfile(fname):
        i = 1
        name,ext = fname.split('.')
        try:
            fi = int(name[-1])+1
            fname = '{}{}.{}'.format(fname[:-1],fi,ext)
        except:
            fi = i+1
            fname = '{}{}.{}'.format(fname,i,ext)
    with open(fname,'wb') as f:
        pickle.dump(file,f)
    print('\nsaved as: {}\n'.format(fname))

def load_data(filename='',auto=True,ext=''):
    import pickle
    import os
    if filename:
        try:
            with open(filename,'rb') as fname:
                fdata = pickle.load(fname)
                return fdata
        except:
            print('\n{} not in dir\n'.format(filename))
    fnames = [i for i in os.listdir() if '.{}'.format(ext) in i]
    x = 1
    while False==False:
        print()
        for ei,fi in enumerate(fnames):
            print('{} - {}'.format(ei+1,fi))
            if not auto:
                x = int(input('\nfile: _ '))
            try:
                with open(fnames[x-1],'rb') as fname:
                    fdata = pickle.load(fname)
                    return fdata
            except:
                print('\ninvalid input?\n')
