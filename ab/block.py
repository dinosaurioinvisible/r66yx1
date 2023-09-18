
import numpy as np
from pyemd import emd 
from auxs import *

# analysis of the block 

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
    block_domains = mk_block_domains()
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
    # sy_dom: all past possible cfgs for current (sy,ey) domain
    sx_dom,sy_dom = mk_tx_domain(sx,sy)


























#