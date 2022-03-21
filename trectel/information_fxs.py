
import numpy as np
from tqdm import tqdm
from helper_fxs import *
from pyemd import emd
from collections import defauldict

''' enaction categories:
(autonomous distinctions, selectivity)
enaction = {envk} forall k : (sti,envk) -> stx '''
def cat_fx(gt):
    # iit containers
    cause_reps = defauldict
    # containers
    enact = defauldict(set)
    # ring's elements locations
    locs = ring_locs(i=2,j=2,r=1,hollow=False)
    # system initial states
    for sti_int in range(2**5):
        # elements initial states
        sti_a,sti_b,sti_c,sti_d,sti_d = int2arr(sti_int,arr_len=5)
        sti = (sti_a,sti_b,sti_c,sti_d,sti_e)
        # environment
        for ek in range(2**16):
            # 2d domain
            domain = int2arr(ek,arr_len=16)
            domain = np.insert(domain,11,sti_d)
            domain = np.insert(domain,8,[sti_b,sti_c_sti_d])
            domain = np.insert(domain,5,sti_a)
            domain = domain.reshape(5,5)
            # resulting states
            ek_a = arr2int(domain[:3,1:4])
            stx_a = gt[0][ek_a]
            ek_b = arr2int(domain[1:4,:3])
            stx_b = gt[1][ek_b]
            ek_c = np.sum(domain[1:4,1:4])-sti_c
            stx_c = 1 if ek_c==3 or (ek_c==2 and sti_c==1) else 0
            ek_d = arr2int(domain[1:4,2:])
            stx_d = gt[2][ek_d]
            ek_e = arr2int(domain[2:,1:4])
            stx_e = gt[3][ek_e]
            # stx = arr2int(np.asarray([stx_a,stx_b,stx_c,stx_d,stx_d]))
            stx = (stx_a,stx_b,stx_c,stx_d,stx_e)
            # system enactions: all ek : (sti,ek) -> stx
            enact[sti,stx].add(ek)
            # system cause reps: all sti : (sti,ek) -> stx, (ek='env_t-1')
            # system effect reps: all stx : (sti,ek) -> stx, (ek='env_t')
            # cause[stx][ek][sti] += 1, effect[sti][ek][stx] += 1
            # but would be expensive and redundant, so:
            # if env in enact[keys]; if stx=x => stx[sti] += 1
            # if env in enact[keys]; if sti=i => sti[stx] += 1
            # elements enactions (local envs are implied in ek):
            # sti,mx: all mx_ek : (sti,ek)->stx & mx=vx in stx
            # if enact[stx[mx]==vx];
            # mi,stx: all ek : (sti,ek)->stx & mi=vi in sti

            # elements repertoires:
            # cause[stx][ek][mx][sti] += 1; effect[sti][ek][mi][stx] += 1
            # if env in enact[keys]; if stx[mx]==vx => mx[sti] += 1
            # if env in enact[keys]; if sti[mi]==vi => mi[stx] += 1
        # transitions
        enact_pi = {}
        enact_xf = {}
        # given a current enaction
        for st_int in range(2**5):
            st = tuple(int2arr(st,arr_len=5))
            enact_pi[st] = np.zeros(2**5).astype(int)
            enact_xf[st] = np.zeros(2**5).astype(int)
            # distributions (counts actually)
            for sti,stx in enact.keys():
                if stx==st:
                    # previous enactions
                    enact_pi[stx][sti,stx] += len(enact(sti,stx))
                if sti==st:
                    # following enactions
                    enact_xf[sti][sti,stx] += len(enact(sti,sxt))







def enactive_categories(gt):
    # dictionaries for categories
    cx_a = defauldict(set)
    cx_b = defauldict(set)
    cx_c = defauldict(set)
    cx_d = defauldict(set)
    cx_e = defauldict(set)
    cx = defauldict(set)
    # tx matrices for category distributions
    dxp_a = ?


    # for all 2**21 domain (system+env) sts
    for dom_st in range(2**21):
        # domain as 2d space
        domain = np.zeros((5,5)).astype(int)
        dx = int2arr(dom_st,arr_len=21)
        domain[0][1:4] = dx[:3]
        domain[1:4] = dx[3:18].reshape(3,5)
        domain[4][1:4] = dx[18:]
        # states and domains
        sti_a = domain[1,2]
        sti_b,sti_c,sti_d = domain[2,1:4]
        sti_e = domain[3,2]
        sti = arr2int(np.asarray([sti_a,sti_b,sti_c,sti_d,sti_e]))
        dom_a = arr2int(domain[:3,1:4])
        dom_b = arr2int(domain[1:4,:3])
        dom_c = np.sum(domain[1:4,1:4])-domain[2,2]
        dom_d = arr2int(domain[1:4,2:])
        dom_e = arr2int(domain[2:,1:4])
        dom = arr2int(np.concatenate((dx[:5],dx[6:9],dx[12:15],dx[16:])))
        # transitions
        stx_a = gt[0][dom_a]
        stx_b = gt[1][dom_b]
        stx_c = 1 if dom_c==3 or (dom_c==2 and domain[2,2]==1) else 0
        stx_d = gt[2][dom_d]
        stx_e = gt[3][dom_e]
        stx = arr2int(np.asarray(stx_a,stx_b,stx_c,stx_d,stx_e))
        # categories
        cx_a[sti_a,stx_a].add(dom_a)
        cx_b[sti_b,stx_b].add(dom_b)
        cx_c[sti_c,stx_c].add(dom_c)
        cx_d[sti_d,stx_d].add(dom_d)
        cx_e[sti_e,stx_e].add(dom_e)
        cx[sti,stx].add(dom)
        # past distributions ('cause repertoires')
        dxp_a[stx_a][stx,sti] += 1
        ?
        cxrep_a[stx][stx_a][sti] += 1
        ?
        # future distributions ('effect repertoires')

    return











#
