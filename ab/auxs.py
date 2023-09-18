
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

# a tensor for all binary combinations
def mk_binary_domains(n_cells):
    doms = np.zeros((2**n_cells,n_cells)).astype(int)
    for i in range(n_cells):
        f = 2**i
        xi = np.concatenate((np.zeros(f),np.ones(f)))
        n = int(2**n_cells/(2**(i+1)))
        doms[:,-1-i] = np.tile(xi,n)
    return doms

# domain environmental (sx + env) tensor
# given a block, blinker or any other structure from the gol (sx)
# make all the env arrays for sx
# e_cells are all the cells in the environment
def mk_sx_domain(sx):
    # number of env cells
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

# get all sx: sx -> sy
# sy = 'block', 'blinker', etc
def get_sxs(sy):
    # array for expected sy
    ey = mk_gol_pattern(sy)
    n,m = ey.shape
    ey = ey.flatten()
    # all possible domains fot (sx,ex)
    domx = mk_binary_domains(n*m)
    # analyze domains transitions
    # firt array = ey for analysis later
    sxs = ey*1
    for dx in domx:
        dy = gol_step(dx.reshape(n,m)).flatten()
        # perfect blocks
        if np.sum(dy*ey) == 4:
            sxs = np.vstack((sxs,dx))
    # translation and rotations (symmetries)
    # 1) classify by number of active and shared sx-sy cells
    symx = {}
    # number of active cells in sx (skip sx->sy=0 cases)
    for n_ac in range(3,n*m-3):
        # to classify by n_ac
        symx[n_ac] = {}
        # to classify by common/shared cells (hints symmetry)
        # possible range: 0 to n active cells in sy=ey
        for cc in range(np.sum(ey).astype(int)+1):
            symx[n_ac][cc] = []
        # indexes for sxs with active cells = n_ac
        # +1 because sxs[1:] (skip sy)
        sxs_ac = np.where(np.sum(sxs[1:],axis=1)==n_ac)[0].astype(int)+1
        # common active cells between sx and sy
        for sxi in sxs_ac:
            n_cc = np.sum(sxs[sxi]*ey).astype(int)
            symx[n_ac][n_cc].append(sxi)
    # 2) look for symmetries
    # rotations
    sxs_syms = {}
    for aci in range(3,n*m-3):
        sxs_syms[aci] = {}
        for cci in range(np.sum(ey).astype(int)+1):
            # skip 0 and 1 cases
            if len(symx[aci][cci]) < 2:
                sxs_syms[aci][cci] = [symx[aci][cci]]
            else:
                sxs_syms[aci][cci] = []
                # already counted in previous cycles
                all_syms = []
                for ei,si in enumerate(symx[aci][cci][:-1]):
                    if si in all_syms:
                        break
                    else:
                        syms = [si]
                    for sj in symx[aci][cci][ei+1:]:
                        # rotation and transposition
                        for ri in range(1,4):
                            sjr = np.rot90(sxs[sj].reshape(4,4),ri)
                            if np.array_equal(sxs[si],sjr.flatten()) == True:
                                syms.append(sj)
                                all_syms.append(sj)
                                break
                            sjt = np.ascontiguousarray(sjr.T).flatten()
                            if np.array_equal(sxs[si],sjt) == True:
                                syms.append(sj)
                                all_syms.append(sj)
                                break
                        # non rotation case
                        if sj not in all_syms:
                            sjt0 = np.ascontiguousarray(sxs[sj].reshape(4,4).T).flatten()
                            if np.array_equal(sxs[si],sjt0) == True:
                                syms.append(sj)
                                all_syms.append(sj)

                    sxs_syms[aci][cci].append(syms)
                    # all_syms.extend(syms)
    # print data
    for k_ac in sxs_syms.keys():
        xac = []
        for k_cc in sxs_syms[k_ac].keys():
            xcc = [[k_cc,len(simset),simset] for simset in sxs_syms[k_ac][k_cc]]
            xac.extend(xcc)
        sumset = np.sum([i[1] for i in xac])
        n_symsets = np.sum([1 for i in xac if i[1]>0]).astype(int)
        print('\nactive cells: {}, sx->sy cases: {}, symsets: {}'.format(k_ac,sumset,n_symsets))
        if sumset > 0:
            for xai in xac:
                if xai[1] > 0:
                    print('common cells: {}, symset len: {}'.format(xai[0],xai[1]))
                    print('symsets cases: {}'.format(xai[2]))
    return sxs,sxs_syms


        


    # # data
    # if not data:
    #     return sxs
    # # ncells, ncases, shared_cells
    # sx_cases = []
    # # for rotation and translations
    # cc_index = {}
    # # 0 to all
    # for i in range(n*m+1):
    #     # sxs according to the number of active cells in dx
    #     nsxs = np.sum(np.where(np.sum(sxs[1:],axis=1)==i,1,0))
    #     # count of common/shared active cells between sx and sy
    #     ccells = [0] * np.sum(ey).astype(int)
    #     # indexes+1 because sxs[1:]
    #     indexes = np.where(np.sum(sxs[1:],axis=1)==i)[0].astype(int)+1
    #     # to classify sxs with same active ncells (i) and ccells (ci/cci)
    #     cc_index[i] = {}
    #     for ci in range(np.sum(ey).astype(int)+1):
    #         cc_index[i][ci] = []
    #     # indexes for sxs -> sy that may be the same after rot/transl
    #     for xi in indexes:
    #         # number of common cells
    #         cci = np.sum(sxs[0]*sxs[xi]).astype(int)
    #         # count
    #         ccells[cci] += 1
    #         # classification
    #         cc_index[i][cci].append(xi)
    #     sx_cases.append([i,nsxs,ccells])
    #     print(i,nsxs,ccells)
    # # rotation and tranlation
    # return sxs, sx_cases, cc_index


# cause repertoire
# 
# def mk_crep(sy):



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

