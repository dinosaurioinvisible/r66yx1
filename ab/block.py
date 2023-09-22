
import numpy as np
from pyemd import emd 
from auxs import *

# analysis of the block 

# make block pattern 
# block in a 4x4 empty lattice (Bx,e=0)
# block = mk_gol_pattern('block')

# make tensor of block domains (Bc,ex)
# (all possible env combinations for canonical block)
# out: (2^16,16) matrix of flattened arrays 
# block_domains = mk_sx_domain('block')

# get all proto-block domains (sx: sx -> sy=block)
# pb_domains: all sxs that could have led to a block
# out: (m,16) matrix of flattened sx arrays 
# reduced by rotation & transposition
# reduced by continuity (sx & sy share 1+ cells)
# pb_domains,pb_symsets = get_sxs_from_sy(block)
# pb_symsets: list of indexes for all instances classified as symsets
# cause info
def get_block_sxs(e0=False,ct=True):
    block = mk_gol_pattern('block')
    pb_sxs,pb_sxs_symsets,pb_symsets = get_sxs_from_sy(block,e0,ct)
    return pb_sxs,pb_sxs_symsets,pb_symsets

# series of recursive transitions from (block,ex) -> sy
# block + every possible env -> sy1 -> sy2 -> ... -> sy10
# for the block, there's no change after the 10th iteration
def get_block_sys(txs=10,make_zero=True,expanded=False):
    block = mk_gol_pattern('block')
    block_domains = mk_sx_domains('block')
    sxs,sxy = get_sys_from_sx(block,block_domains,txs,make_zero=make_zero,expanded=expanded)
    if not expanded:
        analize_block_sxy(sxy)
    return sxs,sxy

def analyze_expanded_block(txs=1,ct=True):
    print()
    block = mk_gol_pattern('block')
    # adjust block to 6x6
    nme = 4+(2*txs)
    be = np.zeros((6,6))
    be[1:-1,1:-1] = block
    be = be.flatten()
    bdoms = mk_sx_domains('block')
    exs,exys = get_sys_from_sx(block,bdoms,txs,make_zero=True,expanded=True)
    # preview
    exys_sums = [sum_is(exys,i).shape[0] for i in range(nme*nme+1)]
    print()
    for ei,es in enumerate(exys_sums):
        if es>0:
            print('ac:{}, sxys:{}'.format(ei,es))
    # continuity
    if ct:
        cty = sum_nonzero(exys*be,arrays=False)
        exs = exs[cty]
        exys = exys[cty]
        print('\nsxs/sxys after ct:{}\n'.format(cty.shape[0]))
    exys_sums = [sum_is(exys,i).shape[0] for i in range(nme*nme+1)]
    for ei,es in enumerate(exys_sums):
        if es>0:
            print('ac:{}, sxys:{}'.format(ei,es))
    # sy -> syy transition to discard unviable sxys
    syys_ids = []
    syys = []
    for ei,es in enumerate(exys_sums):
        if es>0:
            n_syy = 0
            for sy_id in sum_is(exys,ei):
                sy = exys[sy_id]
                syy = gol_step(sy.reshape(nme,nme)).flatten()
                if np.sum(syy)>2:
                    n_syy += 1
                    syys_ids.append(sy_id)
                    syys.append(syy)
            #print('ac:{}, sxys:{}, syys:{}'.format(ei,es,n_syy))
    syys_ids = np.array(syys_ids)
    # tx2 sxs,sxys,syys
    exs = exs[syys_ids]
    exys = exys[syys_ids]
    syys = np.array(syys)
    exys_sums = [sum_is(exys,i).shape[0] for i in range(nme*nme+1)]
    syys_sums = [sum_is(syys,i).shape[0] for i in range(nme*nme+1)]
    print('\nsxs/sxys/syys after syy_tx: {}\n'.format(syys_ids.shape[0]))
    for ei in range(nme*nme+1):
        if exys_sums[ei]+syys_sums[ei]>0:
            print('ac:{}, sxys:{}, syys:{}'.format(ei,exys_sums[ei],syys_sums[ei]))
    # a further tx to discard unviable cfgs: sy -> syy -> syyy
    syyys_ids = []
    syyys = []
    for ei,es in enumerate(syys_sums):
        if es>0:
            n_syyy = 0
            for syy_id in sum_is(syys,ei):
                syy = syys[syy_id]
                syyy = gol_step(syy.reshape(nme,nme)).flatten()
                if np.sum(syyy)>2:
                    n_syyy += 1
                    syyys_ids.append(syy_id)
                    syyys.append(syyy)
            #print('ac:{}, sxys:{}, syys:{}, syyys:{}'.format(ei,exys_sums[ei],es,n_syyy))
    syyys_ids = np.array(syyys_ids)
    # tx3 sxs,sxys,syys,syys
    exs = exs[syyys_ids]
    exys = exys[syyys_ids]
    syys = syys[syyys_ids]
    syyys = np.array(syyys)
    exys_sums = [sum_is(exys,i).shape[0] for i in range(nme*nme+1)]
    syys_sums = [sum_is(syys,i).shape[0] for i in range(nme*nme+1)]
    syyys_sums = [sum_is(syyys,i).shape[0] for i in range(nme*nme+1)]
    print('\nsxs/sxys/syys after syyy_tx: {}\n'.format(syyys_ids.shape[0]))
    for ei in range(nme*nme+1):
        if exys_sums[ei]+syys_sums[ei]+syyys_sums[ei]>0:
            print('ac:{}, sxys:{}, syys:{}, syyys:{}'.format(ei,exys_sums[ei],syys_sums[ei],syyys_sums[ei]))
    # one more to see what happens
    # a further tx to discard unviable cfgs: sy -> syy -> syyy
    y4_ids = []
    y4 = []
    for ei,es in enumerate(syyys_sums):
        if es>0:
            n_y4 = 0
            for syyy_id in sum_is(syyys,ei):
                syyy = syyys[syyy_id]
                sy4 = gol_step(syyy.reshape(nme,nme)).flatten()
                if np.sum(sy4)>2:
                    n_y4 += 1
                    y4_ids.append(syyy_id)
                    y4.append(sy4)
            #print('ac:{}, sxys:{}, syys:{}, syyys:{}'.format(ei,exys_sums[ei],es,n_syyy))
    y4_ids = np.array(y4_ids)
    # tx3 sxs,sxys,syys,syys
    exs = exs[y4_ids]
    exys = exys[y4_ids]
    syys = syys[y4_ids]
    syyys = syyys[y4_ids]
    y4 = np.array(y4)
    exys_sums = [sum_is(exys,i).shape[0] for i in range(nme*nme+1)]
    syys_sums = [sum_is(syys,i).shape[0] for i in range(nme*nme+1)]
    syyys_sums = [sum_is(syyys,i).shape[0] for i in range(nme*nme+1)]
    y4_sums = [sum_is(y4,i).shape[0] for i in range(nme*nme+1)]
    print('\nsxs/sxys/syys after y4_tx: {}\n'.format(y4_ids.shape[0]))
    for ei in range(nme*nme+1):
        if exys_sums[ei]+syys_sums[ei]+syyys_sums[ei]+y4_sums[ei]>0:
            print('ac:{}, sxys:{}, syys:{}, syyys:{}, y4:{}'.format(ei,exys_sums[ei],syys_sums[ei],syyys_sums[ei],y4_sums[ei]))
    # now check sxys more in detail

    return exs,exys,syys,syyys,y4


def compare_block_expanded(txs=1):
    block = mk_gol_pattern('block')
    bdoms = mk_sx_domains('block')
    sxs,sxy = get_sys_from_sx(block,bdoms,txs,make_zero=True,expanded=False)
    exs,exy = get_sys_from_sx(block,bdoms,txs,make_zero=True,expanded=True)
    sxy_sums = [sum_is(sxy,i).shape[0] for i in range(17)]
    exy_sums = [sum_is(exy,i).shape[0] for i in range((4+(2*txs))**2+1)]
    for i,(sv,ev) in enumerate(zip(sxy_sums,exy_sums)):
        print(i,sv,ev)
    for ei,ex in enumerate(exy_sums[17:]):
        if ex>0:
            print(ei+17+1,ex)
    return sxy,exy

def analize_block_sxy(sxy):
    # analize sxy
    # number of sy arrays according to number of active cells (0 to 16)
    sxy_ac = [sum_is(sxy,i).shape[0] for i in range(17)]
    for ac,ac_cases in enumerate(sxy_ac):
        if ac_cases>0:
            print(ac,ac_cases)
    # 3 active cells: look for blinkers
    sy_blinkers = 0
    for sy3 in sxy[sum_is(sxy,3)]:
        if is_blinker(sy3.reshape(4,4)):
            sy_blinkers += 1
    print('{} blinkers from {}'.format(sy_blinkers,sxy_ac[3]))
    # 4 active cells: look for blocks (and rings)
    sy_blocks,sy_rings = 0,0
    for sy4 in sxy[sum_is(sxy,4)]:
        if is_block(sy4.reshape(4,4)):
            sy_blocks += 1
        else:
            sy_rings += 1
    print('{} blocks from {}'.format(sy_blocks,sxy_ac[4]))
    print('{} rings from {}'.format(sy_rings,sxy_ac[4]))
    # 5 active cells: gliders? 


def get_block_cause_info():
    # prob of sx given sy=block, ucx: uniform
    crep = np.array([len(i) for i in pb_symsets])
    crep = crep/(np.sum(crep))
    ucx = np.ones(crep.shape[0])/crep.shape[0]
    # distance matrix for EMD
    dm = 0
    ci = emd(crep,ucx,dm)
    return ci


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



# effect information (from proto-blocks into block)
# given a protoblock x, how probable is its transition into a block
# sx/sy = 'block', 'pblock1', etc
def get_sx_info(sx,sy):
    # sx_dom: (sx,ex)
    sx_dom = mk_sx_domain(sx)
    # sy_dom: all past possible cfgs for current (sy,ey) domain
    # all (sx,ex) from where we need to see those that could have led to sy
    if sy == 'block':
        sy_dom_cells = 16
    sy_dom = mk_binary_domains(sy_dom_cells)
    # cause repertoire: p(x| y=sy)
    crep = mk_crep(sy)
























#