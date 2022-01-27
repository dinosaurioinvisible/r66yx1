
import numpy as np
from tqdm import tqdm
from helper_fxs import *

'''
cause repertoire:
causal probability distribution
for every mechanism (mx) in state (sti)
distribution (cr) of the possible past states (stp)
'''
def get_repertoires(gt):
    # repertoires are dicts for access and plots
    cause_reps = {}
    effect_reps = {}
    uce_reps = {}
    # more than 3 elements mechanisms
    emx_names = ['a','b','c','d','ab','ac','bd','cd','abc','abd','acd','bcd','abcd']
    mx3_indexes = [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
    emx_indexes = [[0],[1],[2],[3],[0,1],[0,2],[1,3],[2,3],[0,1,2],[0,1,3],[0,2,3],[1,2,3],[0,1,2,3]]
    # define repertoires
    for name in emx_names:
        cause_reps[name] = {}
        effect_reps[name] = {}
        # for 3 elements mechanisms
        if len(name) == 1:
            for stc in [0,1]:
                cause_reps[name][stc] = np.zeros(8).astype(int)
                effect_reps[name][stc] = np.zeros(8).astype(int)
        else:
            for bi in range(2**len(name)):
                bsts = int2arr(bi,arr_len=len(name))
                cause_reps[name][tuple(bsts)] = np.zeros(16).astype(int)
                effect_reps[name][tuple(bsts)] = np.zeros(16).astype(int)
        # for unconstrained reps
        if len(name) == 1:
            uce_reps[name] = np.zeros(8).astype(int)
    uce_reps['abcd'] = np.zeros(16).astype(int)
    # full domain (including agent cells)
    domain_range = 2**21
    for domain in tqdm(range(domain_range)):
        # elements states
        dx = int2arr(domain,arr_len=21)
        stp_a = dx[5]
        stp_b = dx[9]
        stp_c = dx[11]
        stp_d = dx[15]
        # if dx[10] == 1:
        # system state (which is the frame mechanism for all)
        mx_sti = [stp_a,stp_b,stp_c,stp_d]
        a_in = arr2int(np.asarray([dx[0],dx[1],dx[2],dx[4],dx[5],dx[6],dx[9],dx[10],dx[11]]))
        b_in = arr2int(np.asarray([dx[3],dx[4],dx[5],dx[8],dx[9],dx[10],dx[13],dx[14],dx[15]]))
        c_in = arr2int(np.asarray([dx[5],dx[6],dx[7],dx[10],dx[11],dx[12],dx[15],dx[16],dx[17]]))
        d_in = arr2int(np.asarray([dx[9],dx[10],dx[11],dx[14],dx[15],dx[16],dx[18],dx[19],dx[20]]))
        sta = gt[0][a_in]
        stb = gt[1][b_in]
        stc = gt[2][c_in]
        std = gt[3][d_in]
        mx_stx = [sta,stb,stc,std]
        for mx_name,indexes in zip(emx_names,emx_indexes):
            # for mechanisms of 3 elements
            if len(indexes) == 1:
                mx_sti_index = arr2int(np.asarray([mx_sti[ei] for ei in mx3_indexes[indexes[0]]]))
                mx_stx_index = arr2int(np.asarray([mx_stx[ei] for ei in mx3_indexes[indexes[0]]]))
                exs_stx = mx_stx[indexes[0]]
                exs_sti = mx_sti[indexes[0]]
            else:
                mx_sti_index = arr2int(np.asarray(mx_sti))
                mx_stx_index = arr2int(np.asarray(mx_stx))
                exs_stx = tuple([mx_stx[i] for i in indexes])
                exs_sti = tuple([mx_sti[i] for i in indexes])
            # cause repertoires: elements (t) -> mechanism (t-1)
            # counts: element st (t+1) -> mechanism st (t)
            cause_reps[mx_name][exs_stx][mx_sti_index] += 1
            # effect repertoires: elements (t) -> mechanism (t+1)
            # counts: elements (t) -> mechanism (t+1)
            effect_reps[mx_name][exs_sti][mx_stx_index] += 1
            # unconstrained future repertoire
            # counts all future states independently of its inputs (current sts)
            try:
                uce_reps[mx_name][mx_stx_index] += 1
            except:
                uce_reps['abcd'][mx_stx_index] += 1
    # convert counts to distributions
    for name in emx_names:
        for key,count in cause_reps[name].items():
            cause_reps[name][key] = count/np.sum(count)
        for key,count in effect_reps[name].items():
            effect_reps[name][key] = count/np.sum(count)
    for name,count in uce_reps.items():
        uce_reps[name] = count/np.sum(count)
    return cause_reps, effect_reps, uce_reps
















#
