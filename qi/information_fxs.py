
import numpy as np
from collections import defaultdict
from helper_fxs import *

# organization
# selectivity
# syntactic distinctions
# information
# normativity

def organization_fx(gt):
    # transitions (sti (+env) > stx)
    txs = {}
    # transitions matrices
    tx_matrix = np.zeros((16,16)).astype(int)
    tx_matrix_norm = np.zeros((16,16)).astype(int)
    # fortuity (envs -> stx) & selectivity (envs : sti>stx)
    frt = defaultdict(set)
    sel_st = {}
    sel = defaultdict(set)
    # intrinsic info IIT (cause/effect/uce reps, cei info)
    cxrep = {}
    exrep = {}
    uxrep = {}
    # intrinsic info*: fore (stx -> P(stz)), event (sti->P(stx)->stx)
    fore_xi = {}
    event_xi = {}
    # normativity

    # system state
    for sti in range(16):
        # transitions
        txs[sti] = {}
        # state selectivity
        sel_st[sti] = defaultdict(set)
        # information
        exrep[sti] = np.zeros(16).astype(int)
        fore_xi[sti] = np.zeros(16).astype(int)
        # elements/mechanisms states
        ex_stis = int2arr(sti,arr_len=4)

        # env states and responses
        for envi in range(256):
            ex_envs = envint2arrs(envi)
            ex_stxs = [gt[ei][ex_env] for ei,ex_env in enumerate(ex_envs)]
            stx = arr2int(np.asarray(ex_stxs))
            # transitions (organization)
            txs[sti][envi] = stx
            # fortuity & selectivity
            fty[stx].add(envi)
            sel_st[sti][stx].add(envi)
            sel[(sti,stx)].add(envi)
            # information IIT (for every mechanism)
            if stx not in cxrep.keys():
                cxrep[stx] = np.zeros(16).astype(int)
            cxrep[stx][sti] += 1
            exrep[sti][stx] += 1
            for ex_stx in ex_stxs:
                uxrep[]
            uxrep[]
            # information
            fore_xi[sti][stx] += 1

            # tx matrices
            tx_matrix[sti][stx] += 1

        # countings to probs
        fore_xi[sti] = fore_xi/256
    # isol. system transition matrix
    for sti in range(16):
        matrix_sys[sti] = np.zeros(16)
        stx = txs[sti]
        matrix_sys[sti][stx] += 1
    # event information
    event_xi[]


















#
