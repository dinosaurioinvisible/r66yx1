


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
