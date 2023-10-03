
import numpy as np
from pyemd import emd 
from auxs import *

# get all proto-block domains (sx: sx -> sy=block)
# pb_domains: all sxs that could have led to a block
# out: (m,16) matrix of flattened sx arrays 
# reduced by rotation & transposition
# reduced by continuity (sx & sy share 1+ cells)
# pb_domains,pb_symsets = get_sxs_from_sy(block)
# pb_symsets: list of indexes for all instances classified as symsets
# cause info
def get_block_sxs(e0=False,ct=True,syms=True):
    block = mk_gol_pattern('block')
    block_sxs,ct_ids = get_sxs_from_sy(block,e0=e0,ct=ct)
    if syms:
        symsets_arr,symsets = mk_symsets(block_sxs)
    return block_sxs,symsets
    # pb_sxs,pb_sxs_symsets,pb_symsets = get_sxs_from_sy(block,e0,ct,mk_symsets=mk_symsets)
    # return pb_sxs,pb_sxs_symsets,pb_symsets

# look for decaying transitions (after sx->sy and before sy->sz)
# sxys: matrix of arrays of sy states with ac>2 (so = or -> zero)
# sxs: sx sts (for updating and making indices)
# the idea is too look for other states that -> zero
def mk_block_decay(sxs,sxys,txs=1,print_all=True,return_all=False):
    # number of cells in domain (for ac range)
    ncells = sxys.shape[1]
    # copy of sxys for processing & acs for storing
    z_sts = sxys*1
    sts_acs = np.zeros((ncells+1,1+2*txs))
    sts_acs[:,0] = np.array([sum_is(sxys,i).shape[0] for i in range(ncells+1)])
    # txs go: y -> z1 => z1 -> z2 => z2 -> z3, etc
    print()
    for txi in range(txs):
        # valid indices, z sts, z number of cases for every ac
        zn_ids,z0,z_sts,z0_acs,z_acs = check_decaying_patterns(z_sts,ncells)
        # update sxs & sxys indices (to match z)
        sxys = sxys[zn_ids]
        sxs = sxs[zn_ids]
        # update sxs & sxys counts
        txid = (txi+1)*2
        sts_acs[:,txid-1] = z_acs
        sts_acs[:,txid] = np.array([sum_is(sxys,i).shape[0] for i in range(ncells+1)])
        sxs_acs = [sum_is(sxs,i).shape[0] for i in range(ncells+1)]
        if print_all:
            # print update sxys and tx data
            print('\ntx{}: sxys -> z{}: {}\n'.format(txi+2,txi+1,zn_ids.shape[0]))
        for ac in range(ncells):
            if np.sum(sts_acs[ac]):
                # print sxys ac, acs, z_n & retro updated y_n counts 
                pp = 'ac:{:2}, x:{:3}, y:{:3}'+''.join([', z'+str(i+1)+':{:3} >{:3}' for i in range(txi+1)])
                print(pp.format(*[ac]+[sxs_acs[ac]]+list(sts_acs[ac,:txid+1].astype(int))))
    print()
    # make arrays
    txs_ac_sts = [[] for _ in range(ncells+1)]
    for ac in range(ncells):
        if np.sum(sts_acs[ac]) > 1:
            # arrays for each state stored by ac cases
            for sts in [sxs,sxys,z_sts]:
                txs_ac_sts[ac].append(sum_is(sts,ac,arrays=True))
    # return only y ac sums
    if return_all:
        y_acs = np.delete(sts_acs,np.arange(1,sts_acs.shape[1],2),axis=1)
        return sxs,sxys,z_sts,txs_ac_sts,y_acs
    return sxs,sxys

# series of recursive transitions from (block,ex) -> sy
# block + every possible env -> sy1 -> sy2 -> ... -> sy_n
def get_block_sxys(iter=1,etxs=1,txs=1,expanded=True,ct=True,syms=True,print_all=True):
    block = mk_gol_pattern('block')
    sxs = mk_sx_domains('block')
    for _ in range(iter):
        sxs,sxys,ct_ids = get_sxys_from_sx(block,sxs,txs=etxs,expanded=expanded,ct=ct)
        sxs,sxys = mk_block_decay(sxs,sxys,txs=txs,print_all=print_all,return_all=False)
    if syms:
        symsets_arr,symsets = mk_symsets(sxys)
    return sxys,symsets

# get Dxs for Bc ((bxs,ex) -> Bc)
# get Dys for Bc (Bc -> (bys,ey))
# make symsets: ss(Dxs), ss(Dys)
# go recursevely matching them 
def mk_recursive_block_domains(load=False,e0=False,ct=True,syms=True,txs=1,save=False):
    if load:
        pass
    else:
        sxs,sxs_symsets = get_block_sxs(e0=e0,ct=ct,syms=syms)
        sxys,sxys_symsets = get_block_sxys(txs=txs,ct=ct,syms=syms)
    if save:
        save_as([sxs,sxs_symsets,sxys,sxys_symsets],'block_data',ext='bk')
    xy_ids = check_matching_symsets(sxs,sxs_symsets,sxys,sxys_symsets)
    return sxs,sxys,sxs_symsets,sxys_symsets,xy_ids

# exts: expanded transitions (only 1 for now)
# txs: non expenanded txs to discard decaying patterns
def analyze_expanded_block_sxys(block_sxys=[],etxs=1,txs=5,ct=True,print_all=True):
    print()
    block = mk_gol_pattern('block')
    # from scratch
    if len(block_sxys)==0:
        bdoms = mk_sx_domains('block')
        # one or many expanded transitions
        sxs,sxys = get_sxys_from_sx(block,bdoms,txs=etxs,make_zero=True,expanded=True)
    else:
        # for continuing cases
        nme = np.sqrt(block_sxys.shape[1]).astype(int)
        sx0 = block_sxys[0].reshape(nme,nme)
        sxs,sxys = get_sxys_from_sx(sx0,block_sxys,txs=etxs,make_zero=True,expanded=True)
    nme = np.sqrt(sxys.shape[1]).astype(int)
    sxys_sums = [sum_is(sxys,i).shape[0] for i in range(nme*nme+1)]
    # print initial data
    print()
    for ei,es in enumerate(sxys_sums):
        if es>0:
            print('ac:{}, sxys:{}'.format(ei,es))
    # continuity
    if ct:
        sxys,ct_ids = apply_ct(sxys,block)
        sxs = sxs[ct_ids]
        sxys_sums = [sum_is(sxys,i).shape[0] for i in range(nme*nme+1)]
        print('\nsxs/sxys after ct: {}\n'.format(ct_ids.shape[0]))
        for ei,es in enumerate(sxys_sums):
            if es>0:
                print('ac:{}, sxys:{}'.format(ei,es))
    # transitions to discard decaying patterns (sy -> zx_n)
    sxs,sxys,syzs,ac_sts,y_acs = mk_block_decay(sxs,sxys,txs=txs,print_all=print_all)
    return sxs,sxys,syzs,ac_sts,y_acs

# def get_block_cause_info():
#     # prob of sx given sy=block, ucx: uniform
#     # crep = np.array([len(i) for i in pb_symsets])
#     # crep = crep/(np.sum(crep))
#     # ucx = np.ones(crep.shape[0])/crep.shape[0]
#     # distance matrix for EMD
#     dm = 0
#     ci = emd(crep,ucx,dm)
#     return ci

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



# # effect information (from proto-blocks into block)
# # given a protoblock x, how probable is its transition into a block
# # sx/sy = 'block', 'pblock1', etc
# def get_sx_info(sx,sy):
#     # sx_dom: (sx,ex)
#     sx_dom = mk_sx_domain(sx)
#     # sy_dom: all past possible cfgs for current (sy,ey) domain
#     # all (sx,ex) from where we need to see those that could have led to sy
#     if sy == 'block':
#         sy_dom_cells = 16
#     sy_dom = mk_binary_domains(sy_dom_cells)
#     # cause repertoire: p(x| y=sy)
#     crep = mk_crep(sy)
























#