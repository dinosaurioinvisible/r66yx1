
import numpy as np
from nu_fx import arr2int
from copy import deepcopy

'''initialized only with the 4 known cycles info'''
class Genotype:
    def __init__(self,new_gt=False,glx=None,flex=0):
        # init new
        if new_gt:
            # known element responses (in->out)
            self.rps = set_responses()
            # known core transitions between states
            self.txs,self.grs = set_cycles()
        # for the evol alg
        elif glx:
            self.rps = deepcopy(glx.rps)
            self.txs = deepcopy(glx.txs)
            self.grs = deepcopy(glx.grs)
        else:
            raise Exception("no genotype")
        # prob of different output (error?)
        self.flex = flex

def set_responses():
    # map: gl_in -> gl_response
    variations = False
    variations2 = False
    membrane_gt = False
    gt = [None]*512
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
    # membrane cell that can be on
    mvij = [[[0,0],[4,0]],[[0,4],[4,4]],[[0,0],[0,4]],[[4,0],[4,4]]]
    aevijc = [[[1,1],[3,1]],[[1,3],[3,3]],[[1,1],[1,3]],[[3,1],[3,3]]]
    aeviji = [[0,6],[2,8],[0,2],[6,8]]
    # cases where 2 membrane cells can be on
    mvij2 = [[0,1],[0,3],[1,0],[3,0]]
    aevij2 = [[1,1],[1,3],[1,1],[3,1]]
    aevij2i = [0,2,0,2]
    aevij2c = [[1,2],[1,2],[2,1],[2,1]]
    aevij2ci = [1,1,3,3]
    aevij2co = [0,0,3,3]
    # for very state of A
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
        # membrane
        if membrane_gt:
            for mi in range(0,8):
                gt[mi] = [0,0,0]
        # known viable membrane variations
        if variations:
            for [vi,vj] in mvij[ai]:
                xa[vi][vj] = 1
            for ei,[i,j] in zip(aeviji[ai],aevijc[ai]):
                ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
                eb = int(''.join(str(int(i)) for i in ev),2)
                rm,lm = aer13579[ai]
                gt[eb] = [at[ai+1][ei],rm,lm]
        if variations2:
            for [vi,vj] in mvij2[ai]:
                xa[vi][vj] = 1
            for ei,[i,j] in zip(aevij2i,aevij2):
                ev = np.rot90(xa[i-1:i+2,j-1:j+2],eo).flatten()
                eb = int(''.join(str(int(i)) for i in ev),2)
                rm,lm = aer13579[ai]
                gt[eb] = [at[ai+1][ei],rm,lm]
            for ei,eoc,[i,j] in zip(aevij2ci,aevij2co,aevij2c):
                ev = np.rot90(xa[i-1:i+2,j-1:j+2],eoc).flatten()
                eb = int(''.join(str(int(i)) for i in ev),2)
                em = 0 if at[ai][ei] == 1 else 1
                gt[eb] = [at[ai+1][ei],em,em]
    return gt

def set_cycles():
    # bsts = []
    btrs = []
    bgrs = []
    a = np.array([0,0,1,1,0,1,0,1,1])
    b = np.array([1,0,0,0,1,1,1,1,0])
    # for each cycle
    for do in range(4):
        c1,c2 = arr2int(a,b,rot=do)
        c3,c4 = arr2int(a,b,rot=do,transp=True)
        # bsts.extend([c1,c2,c3,c4])
        btrs.extend([[c1,c2],[c2,c3],[c3,c4],[c4,c1]])
        o1r,o1l = [int(o) for o in np.binary_repr(((1-do)%4),2)]
        o3r,o3l = [int(o) for o in np.binary_repr(((1+do+1)%4),2)]
        r1,r2 = arr2int(np.asarray([1,o1r,o1l,0,0,0,0]),np.asarray([0,o1r,o1l,0,0,0,0]))
        r3,r4 = arr2int(np.asarray([1,o3r,o3l,0,0,0,0]),np.asarray([0,o3r,o3l,0,0,0,0]))
        bgrs.extend([r1,r2,r3,r4])
    return btrs,bgrs

def set_combined_os():
    cos = []
    for o1 in range(0,10):
        for o2 in range(0,10):
            for o3 in range(0,10):
                for o4 in range(0,10):
                    so = o1+o2+o3+o4
                    xo = ''.join(str(o) for o in [o1,o2,o3,o4])
                    if so==9:
                        cos.append(xo)
    cos = (np.asarray(cos).astype(int)/9).astype(int)
    return cos

#Genotype()
