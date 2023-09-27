
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

# check for decaying gol patterns
# sxs: matrix of array-states
# ncells: number of cells in domain
def check_decaying_patterns(sxs,ncells,dims=[0,0]):
    # number of sx->sy viable cases, indeces & array sts
    sxys_ids, sxys = [], []
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
    # symmetries/equivalences
    sxs_ct,sxs_symsets,symsets = get_symsets(sy,sxs,ct)
    return sxs_ct,sxs_symsets,symsets

# systematize the set of sxs -> sy
# considering symmetries, shared cells & locations
def get_symsets(sy,sxs,ct=True):
    # counts from sxs before symmetries
    n,m = sy.shape
    print('\ntotal sxs: {}'.format(sxs.shape[0]))
    for acs in range(n*m+1):
        print(acs,sum_is(sxs,acs).shape[0])
    # look for (dis)-continuity
    # discard sx -> sy transitions if sx & sy don't share at least 1 active cell
    # indices for shared cells > 0
    if ct:
        sxs_ct_ids = np.where(np.sum(sxs*sxs[0],axis=1)>0)[0]
        sxs = sxs[sxs_ct_ids]
    # sums of active cells to look for symmetries
    sxs_sums = np.sum(sxs,axis=1)
    # sy row = -1 to easily avoid counting it, retaining indexes
    sxs_sums[0] = -1
    # lists of indexes of arrays with the same number of active cells
    sxs_ac_id_sets = [[] for _ in range(n*m+1)]
    for sum_i in range(n*m+1):
        sxs_ac_id_sets[sum_i] = np.where(sxs_sums==sum_i)[0]
    # look for rotations and transps within sets
    sxs_syms = [[] for _ in range(n*m+1)]
    sxs_dups = [[] for _ in range(n*m+1)]
    for aci,ac_id_set in enumerate(sxs_ac_id_sets):
        # to avoid re-checking and duplications
        checked_ids = []
        # compare sx arrays
        # ei: index in list, xi_id: index on sxs, xi: array on sxs
        for ei,xi_id in enumerate(ac_id_set):
            # get first array from indexes
            xi = sxs[xi_id]
            # skip previously checked/known eq cases
            if xi_id not in checked_ids:
                eq_ids = [xi_id]
                dup_eq_ids = []
                # look for rotationally eqs arrays
                # ej: 2nd index in list, xj_id: 2nd index on sxs
                for ej in range(ei+1,len(ac_id_set)):
                    xj_id = ac_id_set[ej]
                    if xj_id not in checked_ids:
                        # xj: 2nd array from sxs, reshaped for rot/transp
                        #xj = sxs[xj_id].reshape(n,m)
                        xj = sxs[xj_id].reshape(n,m)
                        # if rotated xj == xi, they are equivalent
                        for rot_i in range(0,4):
                            # 0 rotation for location and transp
                            xj_rot = np.rot90(xj,rot_i).flatten()
                            if np.array_equal(xi,xj_rot):
                                eq_ids.append(xj_id)
                                break
                            # there's only one transp for every rot
                            xj_transp = np.ascontiguousarray(xj_rot.reshape(4,4).T).flatten()
                            if np.array_equal(xi,xj_transp):
                                eq_ids.append(xj_id)
                                break
                            # check translation (location)
                            loc = False
                            for li in range(1,n*m):
                                if np.array_equal(xi,np.roll(xj_rot,li)) or np.array_equal(xi,np.roll(xj_transp,li)):
                                    dup_eq_ids.append(xj_id)
                                    loc=True
                                    break
                            if loc:
                                break
                checked_ids.extend(eq_ids)
                checked_ids.extend(dup_eq_ids)
                # save as array for indexing on sxs
                sxs_syms[aci].append(np.array(eq_ids))
                sxs_dups[aci].append(dup_eq_ids)
    # organize and print
    # check total instances
    n_sxs_symsets = 0
    n_sxs_dups = 0
    n_sxs_acs = [0]*(n*m+1)
    print('sxs')
    for ac in range(n*m+1):
        if len(sxs_syms[ac]) > 0:
            n_sxs_symsets_ac = sum([len(ac_symset) for ac_symset in sxs_syms[ac]])
            n_sxs_dups_ac = sum([len(ac_dups) for ac_dups in sxs_dups[ac]])
            n_sxs_ac = n_sxs_symsets_ac + n_sxs_dups_ac
            n_sxs_acs[ac] = n_sxs_ac
            print('{}, sxs_ss:{}, sxs_dup:{}, sxs:{}'.format(ac,n_sxs_symsets_ac,n_sxs_dups_ac,n_sxs_ac))
            n_sxs_symsets += n_sxs_symsets_ac
            n_sxs_dups += n_sxs_dups_ac
    n_sxs = n_sxs_symsets + n_sxs_dups
    print('total',n_sxs_symsets,n_sxs_dups,n_sxs)
    # symsets info
    symsets = []
    n_symsets = 0
    print('symsets')
    for ac,ac_symsets in enumerate(sxs_syms):
        # join into one symset ids
        print('ac: {}, sxs: {}, symsets: {}'.format(ac,n_sxs_acs[ac],len(ac_symsets)))
        n_symsets += len(ac_symsets)
        for ss,symset in enumerate(ac_symsets):
            symsets.extend(symset)
            symsets.extend(sxs_dups[ac][ss])
    print('total symsets: ',n_symsets)
    for ei,sxi in enumerate(sxs_syms):
        ss_sxs = [len(i) for i in sxi]
        cases = [0,0,0,0]
        for ne,ni in enumerate([1,2,4,8]):
            cases[ne] = np.where(np.asarray(ss_sxs)==ni)[0].shape[0]
        if sum(cases)>0:
            print('{} - c1:{}, c2:{}, c4:{}, c8:{}'.format(ei,cases[0],cases[1],cases[2],cases[3]))
    return sxs,sxs_syms,symsets

# get sys from sx
# in this case we can't assume what sy is valid or not
# so we should look for self-sustaining resulting patterns
# sx: gol pattern in matrix form
# sx_domains: tensor for all domains for sx
# txs: number of sx->sy->sy2->...->sy_n transitions
def get_sxys_from_sx(sx,sx_domains,txs=5,make_zero=True,expanded=False):
    # basically recursive calling of multi gol step:
    sxs = sx_domains*1
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
    return sxs,sxy

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
def save_as(file,fname):
    import pickle
    import os
    while os.path.isfile(fname):
        i = 1
        name,ext = fname.split('.')
        try:
            fi = int(name[-1])+1
            fname = '{}{}.{}'.format(name[:-1],fi,ext)
        except:
            fi = i
            fname = '{}{}.{}'.format(name,i,ext)
    with open(fname,'wb') as f:
        pickle.dump(file,f)
    print('saved as: '.format(fname))

