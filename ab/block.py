
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
    block_sxs = get_sxs_from_sy(block,'block',e0=e0,ct=ct)
    if syms:
        sms_arrs,sms_sxc = mk_symsets(block_sxs,block)
        return block_sxs,sms_arrs,sms_sxc
    return block_sxs

# series of recursive transitions from (block,ex) -> sy
# block + every possible env -> sy1 -> sy2 -> ... -> sy_n
def get_block_sxys(txs=1,expanded=True,mk_zero=True,decay_txs=3,expanded_decay=False,ct=True,syms=True,print_all=False):
    block = mk_gol_pattern('block')
    block_sxs = mk_sx_domains('block')
    block_sxs,block_sxys = get_sxys_from_sx(block_sxs,block,txs=txs,expanded=expanded,mk_zero=mk_zero,ct=ct,decay_txs=decay_txs,expanded_decay=expanded_decay)
    if syms:
        sms_arrs,sms_sxc = mk_symsets(block_sxys)
        return block_sxys,sms_arrs,sms_sxc
    return block_sxys

# the idea is that most of higher ac cases are variants of basic pbs
# for basic proto-blocks: rl=3, rh=4
def mk_proto_blocks(rl=0,rh=0,ct=True,incremental=True):
    rl,rh = (rl,rh) if rh>rl else (3,16)
    block = mk_gol_pattern('block')
    dxs = mk_binary_domains(16)
    dxs_ids = sum_in_range(dxs,rl,rh)
    sxs = get_sxs_from_sy(block,sy_px='block',dxs=dxs[dxs_ids],ct=ct)
    #sxs_copy = sxs*1
    sms_ids,pbs_ids = mk_symsets(sxs,block,incremental=incremental)
    return sxs,sms_ids,pbs_ids
    #return sxs_copy,sms_ids,pbs_ids

# apply something similar for future blocks
def mk_per_gliders(rl=0,rh=0,txs=1,dtxs=3,ct=True,incremental=True):
    rl,rh = (rl,rh) if rh > rl else (3,36)
    block = mk_gol_pattern('block')
    dxs = mk_sx_domains('block')
    dxs = sum_in_range(dxs,rl,rh,arrays=True)
    sxs,sxys = get_sxys_from_sx(dxs,block,txs=txs,decay_txs=dtxs,ct=ct)
    sms_ids,per_ids = mk_symsets(sxys,block,incremental=incremental)
    return sxs,sxys,sms_ids,per_ids
    

# def mk_iter_block_sxys(iters=3,)
#     for _ in range(iter):
#         sxs,sxys,ct_ids = get_sxys_from_sx(block,sxs,txs=etxs,expanded=expanded,ct=ct)
#         sxs,sxys = mk_block_decay(sxs,sxys,txs=txs,print_all=print_all,return_all=False)
#     if syms:
#         symsets_arr,symsets = mk_symsets(sxys)
#     return sxys,symsets

# get Dxs for Bc ((bxs,ex) -> Bc)
# get Dys for Bc (Bc -> (bys,ey))
# make symsets: ss(Dxs), ss(Dys)
# go recursevely matching them 
def mk_recursive_block_domains(load=False,auto_load=False,e0=False,ct=True,syms=True,txs=1,save=False):
    if load:
        print('sxs, sxs_symsets_ids, sxys, sxys_symsets_ids')
        sxs,sxs_symsets,sxys,sxys_symsets = load_data(auto=auto_load,ext='bk')
    else:
        sxs,sxs_symsets = get_block_sxs(e0=e0,ct=ct,syms=syms)
        sxys,sxys_symsets = get_block_sxys(txs=txs,ct=ct,syms=syms)
    if save:
        save_as([sxs,sxs_symsets,sxys,sxys_symsets],'block_ztxs={}'.format(txs),ext='bk')
    xy_ids = check_matching_symsets(sxs,sxs_symsets,sxys,sxys_symsets)
    return sxs,sxys,sxs_symsets,sxys_symsets,xy_ids

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

# exts: expanded transitions (only 1 for now)
# txs: non expenanded txs to discard decaying patterns
def analyze_expanded_block_sxys(block_sxys=[],etxs=1,txs=5,ct=True,print_all=True):
    print()
    block = mk_gol_pattern('block')
    # from scratch
    if len(block_sxys)==0:
        bdoms = mk_sx_domains('block')
        # one or many expanded transitions
        sxs,sxys = get_sxys_from_sx(block,bdoms,txs=etxs,mk_zero=True,expanded=True)
    else:
        # for continuing cases
        nme = np.sqrt(block_sxys.shape[1]).astype(int)
        sx0 = block_sxys[0].reshape(nme,nme)
        sxs,sxys = get_sxys_from_sx(sx0,block_sxys,txs=etxs,mk_zero=True,expanded=True)
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

# call 
import sys
if sys.argv[0] == 'block.py':
    auto_load = True if '--auto_load' in sys.argv else False
    mk_recursive_block_domains(load=auto_load,auto=auto_load)



















#