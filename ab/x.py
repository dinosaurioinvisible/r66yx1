
# analysis of the block 

# make block pattern 
# block in a 4x4 empty lattice (Bx,e=0)
# block = mk_gol_pattern('block')

# make tensor of block domains (Bc,ex)
# (all possible env combinations for canonical block)
# out: (2^16,16) matrix of flattened arrays 
# block_domains = mk_sx_domain('block')

# clasiffy transitions
def mk_block_txs(block_domains):
    # classifications
    # 0: dy is or will become zero (dy < 3)
    # 40: block and empty env
    # 44: block + env
    # 30: future block (center=3, env=0)
    # 33: fb + env
    # 3,4,5,6,7,8: any other 3,4,5,6,7,8
    # 90: centre = 0, env >= 3
    # 99: any other type
    txs = np.zeros((4096,2,16)).astype(int) # index, dx=0,dy=1, dx/dy
    txs_types = np.zeros((4096)).astype(int)
    for di,dx in enumerate(block_domains):
        dy = gol_step(dx.reshape(4,4)).astype(int)
        # active cells
        dsum = np.sum(dy)
        bsum = np.sum(dy[1:-1,1:-1])
        esum = dsum - bsum
        # classification
        if dsum < 3:
            dt = 0
        elif bsum == 3 and esum == 0:
            dt = 30
        elif bsum == 3 and esum > 0:
            dt = 33
        elif bsum == 4 and esum == 0:
            dt = 40
        elif bsum == 4 and esum > 0:
            dt = 44
        elif bsum == 0 and esum > 2:
            dt = 90
        elif 2 < dsum < 9:
            dt = dsum
        else:
            dt = 99
        txs[di] = [dx,dy.flatten()]
        txs_types[di] = dt
    return txs,txs_types

# main function for now
# todo: delete summary[1] and clean in general
# todo: only lookinf for things in the center for now
def mk_block_analysis():
    block_domains = mk_sx_domains('block')
    block_txs, txs_types = mk_block_txs(block_domains)
    txs_summary = {}
    recursive_blocks = []
    for ti in (0,30,33,40,44,3,4,5,6,7,8,90,99):
        tx_cases = np.where(txs_types==ti,1,0)
        txs_summary[ti] = [np.sum(tx_cases), list(np.where(tx_cases)[0])]
    # print premiliminary
    for i,j in zip(txs_summary.keys(),txs_summary.values()):
        print("tx_type: {}, n_cases: {}".format(i,j[0]))
    # check which bys survive later and if they do blocks
    for ti in (0,30,33,40,44,3,4,5,6,7,8,90,99):
        bz_cases = []
        bw_cases = []
        for ci in txs_summary[ti][1]:
            # bx -> by -> bz
            bz = gol_step(block_txs[ci][1].reshape(4,4))
            if np.sum(bz) > 2:
                bz_cases.append(ci)
                # look for blocks
                if np.sum(bz[1:-1,1:-1]) == 4:
                    rbx = block_txs[ci][0].reshape(4,4)
                    rby = block_txs[ci][1].reshape(4,4)
                    if np.sum(bz) == 4:
                        recursive_blocks.append([ci,ti,'xyz_40',rbx,rby,bz])
                    else:    
                        recursive_blocks.append([ci,ti,'xyz_44',rbx,rby,bz])
                # or proto blocks
                elif np.sum(bz[1:-1,1:-1]) == 3 and np.sum(bz) == 3:
                    rbx = block_txs[ci][0].reshape(4,4)
                    rby = block_txs[ci][1].reshape(4,4)
                    recursive_blocks.append([ci,ti,'xyz_p3',rbx,rby,bz])
                elif np.sum([bz[1,:2],bz[2,2:]]) == 4 and np.sum(bz) == 4:
                    rbx = block_txs[ci][0].reshape(4,4)
                    rby = block_txs[ci][1].reshape(4,4)
                    recursive_blocks.append([ci,ti,'xyz_p4',rbx,rby,bz])
                # bx -> by -> bz -> bw
                bw = gol_step(bz)
                if np.sum(bw) > 2:
                    bw_cases.append(ci)
                    # look for blocks
                    if np.sum(bw[1:-1,1:-1]) == 4:
                        rbx = block_txs[ci][0].reshape(4,4)
                        rby = block_txs[ci][1].reshape(4,4)
                        if np.sum(bw) == 4:
                            recursive_blocks.append([ci,ti,'xyzw_40',rbx,rby,bz,bw])
                        else:
                            recursive_blocks.append([ci,ti,'xyzw_44',rbx,rby,bz,bw])
                    # or proto blocks
                    elif np.sum(bw[1:-1,1:-1]) == 3 and np.sum(bz) == 3:
                        rbx = block_txs[ci][0].reshape(4,4)
                        rby = block_txs[ci][1].reshape(4,4)
                        recursive_blocks.append([ci,ti,'xyzw_p3',rbx,rby,bz,bw])
                    elif np.sum([bw[1,:2],bw[2,2:]]) == 4 and np.sum(bw) == 4:
                        rbx = block_txs[ci][0].reshape(4,4)
                        rby = block_txs[ci][1].reshape(4,4)
                        recursive_blocks.append([ci,ti,'xyzw_p4',rbx,rby,bz,bw])
        txs_summary[ti].append(bz_cases)
        txs_summary[ti].append(bw_cases)
    # print more results
    print()
    for i,j in zip(txs_summary.keys(),txs_summary.values()):
        print('type: {}, cases: {}, bz: {}, bw: {}'.format(i,j[0],len(j[2]),len(j[3])))
    print()
    rblocks = {}
    for rbi in ('xyz_40','xyz_44','xyz_p3','xyz_p4','xyzw_40','xyzw_44','xyzw_p3','xyzw_p4'):
        rblocks[rbi] = [u for u in recursive_blocks if u[2]==rbi]
    for rk in rblocks.keys():
        print('rb_type: {}, cases: {}'.format(rk,len(rblocks[rk])))
    return block_txs, txs_summary, rblocks

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


# domain configurations (12 env cells for the block)
# function to make a matrix with all cfgs 
def mk_block_domains(n_cells=12):
    doms = np.zeros((2**n_cells,n_cells)).astype(int)
    # all env cfgs
    for i in range(n_cells):
        f = 2**i
        xi = np.concatenate((np.zeros(f),np.ones(f)))
        n = int(2**n_cells/(2**(i+1)))
        doms[:,-1-i] = np.tile(xi,n)
    # insert blocks 
    doms = np.insert(doms,(5,5,7,7),1,axis=1) 
    return doms


    # # translation and rotations (symmetries)
    # # 1) classify by number of active and shared sx-sy cells
    # symx = {}
    # # number of active cells in sx (skip sx->sy=0 cases)
    # for n_ac in range(3,n*m-3):
    #     # to classify by n_ac
    #     symx[n_ac] = {}
    #     # to classify by common/shared cells (hints symmetry)
    #     # possible range: 0 to n active cells in sy=ey
    #     for cc in range(np.sum(ey).astype(int)+1):
    #         symx[n_ac][cc] = []
    #     # indexes for sxs with active cells = n_ac
    #     # +1 because sxs[1:] (skip sy)
    #     sxs_ac = np.where(np.sum(sxs[1:],axis=1)==n_ac)[0].astype(int)+1
    #     # common active cells between sx and sy
    #     for sxi in sxs_ac:
    #         n_cc = np.sum(sxs[sxi]*ey).astype(int)
    #         symx[n_ac][n_cc].append(sxi)
    # # 2) look for symmetries
    # # rotations
    # sxs_syms = {}
    # for aci in range(3,n*m-3):
    #     sxs_syms[aci] = {}
    #     for cci in range(np.sum(ey).astype(int)+1):
    #         # skip 0 and 1 cases
    #         if len(symx[aci][cci]) < 2:
    #             sxs_syms[aci][cci] = [symx[aci][cci]]
    #         else:
    #             sxs_syms[aci][cci] = []
    #             # already counted in previous cycles
    #             all_syms = []
    #             for ei,si in enumerate(symx[aci][cci][:-1]):
    #                 if si in all_syms:
    #                     break
    #                 else:
    #                     syms = [si]
    #                 for sj in symx[aci][cci][ei+1:]:
    #                     # rotation and transposition
    #                     for ri in range(1,4):
    #                         sjr = np.rot90(sxs[sj].reshape(4,4),ri)
    #                         if np.array_equal(sxs[si],sjr.flatten()) == True:
    #                             syms.append(sj)
    #                             all_syms.append(sj)
    #                             break
    #                         sjt = np.ascontiguousarray(sjr.T).flatten()
    #                         if np.array_equal(sxs[si],sjt) == True:
    #                             syms.append(sj)
    #                             all_syms.append(sj)
    #                             break
    #                     # non rotation case
    #                     if sj not in all_syms:
    #                         sjt0 = np.ascontiguousarray(sxs[sj].reshape(4,4).T).flatten()
    #                         if np.array_equal(sxs[si],sjt0) == True:
    #                             syms.append(sj)
    #                             all_syms.append(sj)

    #                 sxs_syms[aci][cci].append(syms)
    #                 # all_syms.extend(syms)
    # # print data
    # for k_ac in sxs_syms.keys():
    #     xac = []
    #     for k_cc in sxs_syms[k_ac].keys():
    #         xcc = [[k_cc,len(simset),simset] for simset in sxs_syms[k_ac][k_cc]]
    #         xac.extend(xcc)
    #     sumset = np.sum([i[1] for i in xac])
    #     n_symsets = np.sum([1 for i in xac if i[1]>0]).astype(int)
    #     print('\nactive cells: {}, sx->sy cases: {}, symsets: {}'.format(k_ac,sumset,n_symsets))
    #     if sumset > 0:
    #         for xai in xac:
    #             if xai[1] > 0:
    #                 print('common cells: {}, symset len: {}'.format(xai[0],xai[1]))
    #                 print('symsets cases: {}'.format(xai[2]))
    # return sxs,sxs_syms
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
