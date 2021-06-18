
import numpy as np
from nu_fxs import *
from copy import deepcopy
from collections import defaultdict

'''initialized only with the 4 known cycles info
(dictionaries work as pointing graphs)'''
class Genotype:
    def __init__(self,glx=None,cx_mode="genotype",mx_mode="all",flex=0):
        # init new
        if not glx:
            # elements' responses: dict[env_in] = [signal,rm,lm]
            self.exgt = set_responses()
            # cycles: dict[ci,mi,di]=[cx,mx]
            self.cycles = set_cycles()
            # rxs: responses to env dashes
            # defdict[ci,mi,dash] = set{(cx,mx,dij)}
            self.rxs = defaultdict(set)
            # txs: transients redirecting to set of known cycles
            # defdict[dash0]=[[c0,m0,d0],...,[ci,mi,di],...,[cx,mx,dx]]
            self.txs = defaultdict(list)
            # encountered dashes (set)
            self.dxs = {0}
        else:
            self.egt = deepcopy(glx.egt)
            self.cycles = deepcopy(glx.cycles)
            self.rxs = deepcopy(glx.rxs)
            self.txs = deepcopy(glx.txs)
            self.dxs = deepcopy(glx.dxs)
        # updating modes for core and membrane
        self.cx_mode = cx_mode
        self.mx_mode = mx_mode
        # for future distributions based on viability
        self.flex = flex

'''initial cycles for the default glider (dict/graph type)'''
def set_cycles():
    btrs = {}
    # base states
    a = np.array([0,0,1,1,0,1,0,1,1])
    b = np.array([1,0,0,0,1,1,1,1,0])
    # for each cycle
    for do in range(4):
        c1,c2 = arr2int(a,b,rot=do)
        c3,c4 = arr2int(a,b,rot=do,transp=True)
        # dict version cyclic_rx[ci,mi,di] = [cx,mx]
        btrs[(c1,0,0)] = (c2,0)
        btrs[(c2,0,0)] = (c3,0)
        btrs[(c3,0,0)] = (c4,0)
        btrs[(c4,0,0)] = (c1,0)
    return btrs

'''elements base genotype (cycles only)'''
def set_responses():
    # try set rather for debugging
    ex_gt = {}
    # rel location for elements
    eij = xy_around(2,2,r=1,inv=True)
    # base states
    a = np.array([0,0,1,1,0,1,0,1,1])
    b = np.array([1,0,0,0,1,1,1,1,0])
    c = a.reshape(3,3).transpose(1,0).flatten()
    d = b.reshape(3,3).transpose(1,0).flatten()
    # orientations (a&b start the same, c&d idem)
    ab_ox = np.array([1,0,1,3,1,1,1,2,1])
    cd_ox = np.array([2,0,2,3,2,1,2,2,2])
    # responses
    a_rx = [(1,1),(1,1),(1,1),(0,0),(1,1),(1,1),(1,1),(1,1),(1,1)]
    b_rx = [(1,0),(1,1),(1,0),(1,1),(1,0),(1,1),(1,0),(1,1),(1,0)]
    c_rx = [(1,1),(0,0),(1,1),(1,1),(1,1),(1,1),(1,1),(1,1),(1,1)]
    d_rx = [(0,1),(1,1),(0,1),(1,1),(0,1),(1,1),(0,1),(1,1),(0,1)]
    # 5x5 domain to re-orient elements
    e_dom = np.zeros((5,5)).astype(int)
    # map
    for ei,[i,j] in enumerate(eij):
        # a -> b
        e_dom[1:4,1:4] = a.reshape(3,3)
        ae_in = arr2int(e_dom[i-1:i+2,j-1:j+2],rot=ab_ox[ei])
        ar,al = a_rx[ei]
        ae_rx = (b[ei],ar,al)
        ex_gt[ae_in] = ae_rx
        # b -> c
        e_dom[1:4,1:4] = b.reshape(3,3)
        be_in = arr2int(e_dom[i-1:i+2,j-1:j+2],rot=ab_ox[ei])
        br,bl = b_rx[ei]
        be_rx = (c[ei],br,bl)
        ex_gt[be_in] = be_rx
        # c -> d
        e_dom[1:4,1:4] = c.reshape(3,3)
        ce_in = arr2int(e_dom[i-1:i+2,j-1:j+2],rot=cd_ox[ei])
        cr,cl = c_rx[ei]
        ce_rx = (d[ei],cr,cl)
        ex_gt[ce_in] = ce_rx
        # d -> a
        e_dom[1:4,1:4] = d.reshape(3,3)
        de_in = arr2int(e_dom[i-1:i+2,j-1:j+2],rot=cd_ox[ei])
        dr,dl = d_rx[ei]
        de_rx = (a[ei],dr,dl)
        ex_gt[de_in] = de_rx
    # assuming symetry between these 4 and the whole 16
    return ex_gt


'''element's base responses (just 4 cycles)'''
def set_responses_old_version():
    # map: gl_in -> gl_response
    gt = {}
    a1 = np.array([0,0,1,1,0,1,0,1,1])
    a2 = np.array([1,0,0,0,1,1,1,1,0])
    a3 = np.array([0,1,0,0,0,1,1,1,1])
    a4 = np.array([1,0,1,0,1,1,0,1,0])
    at = [a1,a2,a3,a4,a1]
    # these have cycles of orientations
    aeo13579 = [1,1,2,2]
    aei13579 = [0,2,4,6,8]
    aer13579 = [[1,1],[1,0],[1,1],[0,1]]
    # these have fixed orientations
    aeo2468 = [0,3,1,2]
    aei2468 = [1,3,5,7]
    # for every state of A
    for ai in range(len(at)-1):
        xa = np.zeros((5,5))
        xa[1:4,1:4] = at[ai].reshape(3,3)
        eo = aeo13579[ai]
        # diagonals (x)
        for ei,[i,j] in zip(aei13579,[[1,1],[1,3],[2,2],[3,1],[3,3]]):
            ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
            eb = int(''.join(str(int(i)) for i in ev),2)
            rm,lm = aer13579[ai]
            gt[eb] = [at[ai+1][ei],rm,lm]
        # cross (+)
        for ei,eoc,[i,j] in zip(aei2468,aeo2468,[[1,2],[2,1],[2,3],[3,2]]):
            ev = np.rot90(xa[i-1:i+2,j-1:j+2],eoc).flatten()
            eb = int(''.join(str(int(i)) for i in ev),2)
            em = 0 if at[ai][ei] == 1 else 1
            gt[eb] = [at[ai+1][ei],em,em]
    return gt



#Genotype()
