
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
def mk_pb_domains(block=[],e0=False,ct=True,xpn=True,print_data=True):
    block = block if len(block)>0 else mk_gol_pattern('block')
    pb_domains = get_sxs_from_sy(block,'block',e0=e0,ct=ct,xpn=xpn,print_data=print_data)
    return pb_domains 

# series of recursive transitions from (block,ex) -> sy
# block + every possible env -> sy1 -> sy2 -> ... -> sy_n
def mk_fb_domains(block=[],expanded=True,mk_zero=True,decay_txs=3,expanded_decay=False,ct=True,print_data=True):
    block = block if len(block)>0 else mk_gol_pattern('block')
    block_domains = mk_sx_domains('block')
    block_domains,fb_domains = get_sxys_from_sx(block_domains,block,expanded=expanded,mk_zero=mk_zero,ct=ct,decay_txs=decay_txs,expanded_decay=expanded_decay,print_data=print_data)
    return block_domains,fb_domains

# generalizes symmetries among domains
# 1) rotation, translation & transposition
# 2) incremental analysis
def mk_block_symsets(dxs,print_data=True,tensor=False):
    block = mk_gol_pattern('block')
    sms,sms_ids = mk_symsets(dxs,block,incremental=True,print_data=print_data)
    if tensor:
        return mk_dxs_tensor(dxs[sms_ids],block)
    return sms,dxs[sms_ids]

# the idea is that most of higher ac cases are variants of basic pbs
# for basic proto-blocks: rl=3, rh=4
def mk_proto_blocks(rl=3,rh=3,e0=False,expanded=True,ct=True,incremental=True,tensor=False,print_data=False):
    rl,rh = (rl,rh) if rh>rl else (3,16)
    block = mk_gol_pattern('block')
    dxs = mk_binary_domains(16)
    dxs_ids = sum_in_range(dxs,rl,rh)
    sxs = get_sxs_from_sy(block,sy_px='block',dxs=dxs[dxs_ids],e0=e0,expanded=expanded,ct=ct,print_data=print_data)
    sms_cases,pbs_ids = mk_symsets(sxs,block,incremental=incremental,print_data=print_data)
    if tensor:
        return mk_dxs_tensor(sxs[pbs_ids],block)
    return sxs[pbs_ids]

def mk_fwd_blocks(rl=3,rh=3,expanded=True,mk_zero=True,ct=True,decay_txs=2,expanded_decay=False,decay_ct=True,incremental=True,tensor=False,print_data=False):
    rl,rh = (rl,rh) if rh>rl else (3,16)
    block = mk_gol_pattern('block')
    dxs = sum_in_range(mk_sx_domains('block'),rl,rh,arrays=True)
    sxs,sxys = get_sxys_from_sx(dxs,block,mk_zero=mk_zero,ct=ct,expanded=expanded,decay_txs=decay_txs,expanded_decay=expanded_decay,decay_ct=decay_ct,print_data=print_data)
    sms_cases,fbs_ids = mk_symsets(sxys,block,incremental=incremental,print_data=print_data)
    if tensor:
        return mk_dxs_tensor(sxs[fbs_ids],block),mk_dxs_tensor(sxys[fbs_ids],block)
    return sxs[fbs_ids],sxys[fbs_ids]

def recursive_protoblocks(rl=3,rh=5,e0=False,ct=True):
    rl,rh = (rl,rh) if rh>rl else (3,16)
    block = mk_gol_pattern('block')


class Block:
    def __init__(self,e0=True,mk0=True,expanded=False,dec_txs=2,print_data=True):
        self.e0 = e0
        self.mk0 = mk0
        self.exp = expanded
        self.dtxs = dec_txs
        self.pout = print_data
        self.block = mk_gol_pattern('block')
        self.mk_pbs()
        self.mk_basic_pbs()
        self.mk_fbs()

    def mk_pbs(self):
        self.pbs_dxs = get_sxs_from_sy(self.block,sy_px='block',e0=self.e0,expanded=self.exp,ct=True,print_data=self.pout)
        self.pb_cases,pb_ids = mk_symsets(self.pbs_dxs,self.block,incremental=True,print_data=self.pout)
        self.pbs = mk_dxs_tensor(self.pbs_dxs[pb_ids],self.block)
    def mk_basic_pbs(self,rl=3,rh=5):
        dxs_ids = sum_in_range(self.pbs_dxs,rl,rh)
        self.basic_pbs_dxs = get_sxs_from_sy(self.block,sy_px='block',dxs=self.pbs_dxs[dxs_ids],e0=self.e0,expanded=self.exp,ct=True,print_data=self.pout)
        self.basic_pb_cases,basic_pb_ids = mk_symsets(self.basic_pbs_dxs,self.block,incremental=True,print_data=self.pout)
        self.basic_pbs = mk_dxs_tensor(self.basic_pbs_dxs[basic_pb_ids],self.block)
    def mk_fbs(self):
        dxs = mk_sx_domains('block')
        bxs,bys = get_sxys_from_sx(dxs,self.block,mk_zero=self.mk0,ct=True,expanded=self.exp,decay_txs=self.dtxs,expanded_decay=False,decay_ct=True,print_data=self.pout)
        self.fb_cases,fb_ids = mk_symsets(bys,self.block,incremental=True,print_data=self.pout)
        self.bxs = mk_dxs_tensor(bxs[fb_ids],self.block)
        self.fbs = mk_dxs_tensor(bys[fb_ids],self.block)

# TODO: graphs
# TODO: buscar pbs en fbs

# main fx
def block_main(save=False,load=False,print_data=True):
    block = mk_gol_pattern('block')
    # previous and forward domains
    if load:
        pb_domains,block_domains,fb_domains = load_data(filename='block_domains.bk')
        pb_arrs,fb_arrs = load_data(filename='block_domains_syms.bk')
        if print_data:
            print_ac_cases(pb_domains,title='proto-block cases:')
            print_ac_cases(fb_domains,title='fwd-block cases:')
            print_ac_cases(pb_arrs,title='proto-block syms:')
            print_ac_cases(fb_arrs,title='fwd-block syms:')
    else:
        pb_domains = mk_pb_domains(block,print_data=True)
        block_domains,fb_domains = mk_fb_domains(block,print_data=True)
        # symmetries 
        print('\nproto-block:') if print_data==True else print()
        pb_cases,pb_arrs = mk_block_symsets(pb_domains,print_data=print_data)
        #print('\nblock:') if print_data==True else print()
        #fb_cases,bk_arrs = mk_block_symsets(block_domains,print_data=print_data)
        print('\nfwd-block:') if print_data==True else print()
        fb_cases,fb_arrs = mk_block_symsets(fb_domains,print_data=print_data)
        if save:
            save_as([pb_domains,block_domains,fb_domains],name='block_domains',ext='bk')
            save_as([pb_arrs,fb_arrs],name='block_domains_syms',ext='bk')
    pbs = mk_proto_blocks()
    return pb_arrs,fb_arrs,pbs





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
# import sys
# if sys.argv[0] == 'block.py':
#     auto_load = True if '--auto_load' in sys.argv else False
#     mk_recursive_block_domains(load=auto_load,auto=auto_load)



















#