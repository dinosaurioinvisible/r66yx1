
import numpy as np

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

# make canonical gol patterns (sx,e=0) from word inputs
def mk_gol_pattern(px,):
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

# increase the domain size
def expand_domain(sx,dims=(0,0)):
    # if not specified, increase a layer
    if np.sum(dims)==0:
        dims = np.array(sx.shape)+2
    nx,mx = dims
    # create new domain and place sx in the center
    dx = np.zeros((nx,mx))
    nc,mc = int(nx/2),int(mx/2)
    dx[nc-2:nc+2,mc-2:mc+2] = sx
    return dx

# adjust domains to the bigger one
def adjust_domains(x1,x2):
    if x1.shape[0] >= x2.shape[0] and x1.shape[1] >= x2.shape[1]:
        x2 = expand_domain(x2,dims=x1.shape)
    elif x2.shape[0] >= x1.shape[0] and x2.shape[1] >= x1.shape[1]:
        x1 = expand_domain(x1,dims=x2.shape)
    return x1,x2

# game of life transition
def gol_step(world_st):
    world = world_st/1
    world_copy = world_st/1
    for ei,vi in enumerate(world_copy):
        for ej,vij in enumerate(vi):
            nb = np.sum(world_copy[max(0,ei-1):ei+2,max(ej-1,0):ej+2]) - vij
            vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and nb==3) else 0
            world[ei,ej] = vx
    return world

# gol transition for multiple arrays
# sx: matrix form to reshape arrays
# sx_domains: gol lattice/domain arrays for each sx -> sy
# make_zero: makes sums<3 = 0 (will die next)
def multi_gol_step(sx,sx_domains,make_zero=True):
    # shape
    n,m = sx.shape    
    # output array
    sxy = np.zeros((sx_domains.shape[0],n*m))
    # simulate transitions
    for di,dx in enumerate(sx_domains):
        dy = gol_step(dx.reshape(n,m)).flatten()
        sxy[di] = dy
    if make_zero:
        sxy_zeros = np.where(np.sum(sxy,axis=1)<3)[0]
        sxy[sxy_zeros] = 0
    return sxy

# to account for transition activity outside dx
# dx: input in matrix form (n,m)
# dy: output in matrix form (n+2,m+2)
def gol_step_expanded(dx):
    # expand domain
    n,m = dx.shape
    domx = np.zeros((n+2,m+2))
    domx[1:-1,1:-1] = dx
    dy = gol_step(domx)
    return dy
def multi_gol_step_expanded(sx,sx_domains,make_zero=True,expand_by=1):
    n,m = sx.shape
    ne = n + expand_by*2
    me = m + expand_by*2
    sxy = np.zeros((sx_domains.shape[0],(ne)*(me)))
    for di,dx in enumerate(sx_domains):
        dy = gol_step_expanded(dx.reshape(ne-2,me-2)).flatten()
        sxy[di] = dy
    if make_zero:
        sxy_zeros = np.where(np.sum(sxy,axis=1)<3)[0]
        sxy[sxy_zeros] = 0
    return sxy

# check for patterns 
# domx: gol domain/lattice in matrix form
# e0: empty environment
def is_block(domx,e0=True):
    if np.sum(domx) >= 4:
        n,m = domx.shape
        for i in range(n):
            for j in range(m):
                if np.sum(domx[i:i+2,j:j+2]) == 4:
                    if e0:
                        if np.sum(domx) == 4:
                            return True
                    else:
                        if np.sum(domx[max(0,i-1):i+3,max(0,j-1):j+3]) == 4:
                            return True
    return False
# same for next timestep
def is_block_next(domx,e0=True):
    n,m = domx.shape
    # block may be outside of current domain
    dom = np.zeros((n+2,m+2))
    dom[1:-1,1:-1] = domx
    domy = gol_step(dom)
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
# sxs: matrix of gol domain sts arrays 
# psx: primary pattern/structure determining ct
def apply_ct(sxs,psx,dims=[0,0]):
    # assume square if no explicit dims
    if np.sum(dims)==0:
        n = m = np.sqrt(sxs.shape[1]).astype(int)
    # adjust sx 
    dx = psx*1
    if sxs[0].shape != psx.flatten().shape:
        dx = np.zeros((n,m))
        ij = int(n/2)
        dx[ij-2:ij+2,ij-2:ij+2] = psx
    # ct
    ct_ids = sum_nonzero(sxs*dx.flatten())
    sxs_ct = sxs[ct_ids]
    return sxs_ct,ct_ids

# check for decaying gol patterns
# sxs: matrix of array-states
# ncells: number of cells in domain
def check_decaying_patterns(sxs,ncells=0,dims=[0,0]):
    # number of sx->sy viable cases, indeces & array sts
    sxys_ids, sxys = [], []
    # if no number of cells, assume same as arrays
    if ncells==0:
        ncells = sxs.shape[1]
    # if no dims, assume squared domain
    if sum(dims)==0:
        n = m = np.sqrt(sxs[0].shape[0]).astype(int)
    # sum of cases with ac number of active cells in domain
    sxs_ac_cases = [sum_is(sxs,ac).shape[0] for ac in range(ncells+1)]
    # check number of active cells after sx->sy transition
    for ac,n_cases in enumerate(sxs_ac_cases):
        if n_cases > 0:
            # for each sx with active cells = ac
            for sx_id in sum_is(sxs,ac):
                sx = sxs[sx_id]
                sy = gol_step(sx.reshape(n,m)).flatten()
                # if sy has at least 3 active cells
                if np.sum(sy) > 2:
                    sxys_ids.append(sx_id)
                    sxys.append(sy)
    # update sxs, sxs ac cases and get sxys ac cases
    sxs = sxs[sxys_ids]
    sxs_ac_cases = [sum_is(sxs,ac).shape[0] for ac in range(ncells+1)]
    sxys_ac_cases = [sum_is(sxys,ac).shape[0] for ac in range(ncells+1)]
    return np.array(sxys_ids), sxs, np.array(sxys), sxs_ac_cases, sxys_ac_cases

# get all sx: sx -> sy
# sy: any specific gol pattern domain (sx,ex)
# requires matrix/lattice input
def get_sxs_from_sy(sy,e0=True,ct=True):
    # array for expected sy
    n,m = sy.shape
    # all possible domains fot (sx,ex)
    domx = mk_binary_domains(n*m)
    # analyze domains transitions
    # first array = ey for analysis later
    sxs = sy.flatten()
    for dx in domx:
        # centered blocks + any env
        # dy = gol_step(dx.reshape(n,m)).flatten()
        # if np.sum(dy*ey) == 4:
        if is_block_next(dx.reshape(n,m),e0):
            sxs = np.vstack((sxs,dx))
    if ct:
        sxs,ct_ids = apply_ct(sxs,sy)
        return sxs,ct_ids
    return sxs

# get sys from sx
# in this case we can't assume what sy is valid or not
# so we should look for self-sustaining resulting patterns
# sx: gol pattern in matrix form
# sx_domains: tensor for all domains for sx
# txs: number of sx->sy->sy2->...->sy_n transitions
def get_sxys_from_sx(sx,sx_domains,txs=5,make_zero=True,expanded=False,ct=True):
    # basically recursive calling of multi gol step:
    sxs = sx_domains*1
    print()
    for txi in range(txs):
        if expanded:
            sxy = multi_gol_step_expanded(sx,sx_domains,make_zero=make_zero,expand_by=txi+1)
        else:
            sxy = multi_gol_step(sx,sx_domains,make_zero=make_zero)
        print('non zero sys in tx{}: {}'.format(txi+1,sum_nonzero(sxy).shape[0]))
        sx_domains = sxy*1
    # ids for non zero sys
    sxy_ids = sum_nonzero(sxy)
    # return only sx,sy nonzero (self-sustaining) arrays 
    sxs = sxs[sxy_ids]
    sxy = sxy[sxy_ids]
    # continuity
    if ct:
        sxy,ct_ids = apply_ct(sxy,sx)
        return sxs,sxy,ct_ids
    return sxs,sxy

# sxs: matrix of arrays representing gol domains (sx+ex)
# i used sxs to mean anything, sxys, syzs, etc (too late to change it now)
def mk_symsets(sxs,sxs2=[],dims=[0,0]):
    # if not dims assume squared domain
    if np.sum(dims)==0:
        n = m = np.sqrt(sxs.shape[1]).astype(int)
    # ncells for checking acs
    ncells = sxs.shape[1]
    # to store (id,type) & to avoid going again over same ids
    symsets = np.zeros((sxs.shape[0],2)).astype(int)
    # for all doms with same ac number
    for ac in range(ncells):
        ac_ids = sum_is(sxs,ac)
        # if at least 2 of them (to compare)
        if ac_ids.shape[0] == 1:
            symsets[ac_ids[0]] = [ac,ac_ids[0]]
        elif ac_ids.shape[0] > 1:
            # first available: sx
            for ei,sx_id in enumerate(ac_ids):
                # to avoid repetitions
                if symsets[sx_id][0] == 0:
                    symsets[sx_id] = [ac,sx_id]
                    sx = sxs[sx_id].reshape(n,m)
                    # go through the rest of the doms with same ac
                    for ej in range(ei+1,ac_ids.shape[0]):
                        sx2_id = ac_ids[ej]
                        sx2 = sxs[sx2_id].reshape(n,m)
                        # rotations, transpositions, translations
                        if are_symmetrical(sx,sx2):
                            symsets[sx2_id] = [ac,sx_id]
    # organize symsets 
    org_symsets = {}
    print('\ntotal symsets: {}\n'.format(len(set(symsets[:,1]))))
    for ac in list(set(symsets[:,0])):
        org_symsets[ac] = []
        sxs_ac = symsets[np.where(symsets[:,0]==ac)[0]]
        for sxi in list(set(sxs_ac[:,1])):
            ss_ids = np.where(symsets[:,1]==sxi)[0]
            org_symsets[ac].append(ss_ids)
            print(ac,len(ss_ids),ss_ids)
    return symsets,org_symsets

# check symmetries in 2 gol domains 
# x1,x2: matrix form gol reps
def are_symmetrical(x1,x2,nrolls=0):
    # if sizes don't match, adjust to the larger one
    if x1.shape != x2.shape:
        x1,x2 = adjust_domains(x1,x2)
    # if not specified, assume all
    nrolls = x1.shape[0]*x1.shape[1] if nrolls==0 else nrolls
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
        for rli in range(1,nrolls):
            if np.array_equal(x1,np.roll(x2r,rli)):
                return True
            if np.array_equal(x1,np.roll(x2rt,rli)):
                return True
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

# indexing for saving files
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

def load(ext=''):
    import pickle
    import os
    files = [i for i in os.listdir() if '.{}'.format(ext) in i]
    for ei,fi in files:
        print(ei,fi)
    x = input('\nfile: _ ')
    with open()
