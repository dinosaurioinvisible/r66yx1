
import numpy as np
from nu_fxs import *
from nu_genotype import set_cycles
from collections import defaultdict
from collections import Counter

class BasicGlider:
    def __init__(self,gt,st0):
        # gt is a 1x512 array
        self.exgt = gt
        # trial sts
        self.st = None
        self.eos = None
        self.ox = None
        self.cycles = set_cycles()
        self.cy = True
        self.cys = defaultdict(int)
        self.cx0 = None
        self.core_rxs = defaultdict(Counter)
        self.memb_rxs = defaultdict(set)
        self.env_rxs = defaultdict(set)
        self.i,self.j = 0,0
        self.motion = np.zeros(5).astype(int)
        self.loc = None
        self.states = None
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        self.mt = 2

    def update(self,gl_domain):
        # membrane
        membrane = np.zeros((7,7)).astype(int)
        memb_domain = gl_domain.astype(int)
        memb_domain[1:6,1:6] = 0
        for [i,j] in self.me_ij:
            if np.sum(memb_domain[i-1:i+2,j-1:j+2])>0:
                membrane[i][j] = 1
        membrane = membrane[1:6,1:6]
        # core and local motion
        motion = [0,0,0,0]
        core = np.zeros(9).astype(int)
        core_domain = np.zeros((7,7)).astype(int)
        core_domain[1:6,1:6] = membrane.astype(int)
        core_domain[2:5,2:5] = gl_domain[2:5,2:5].astype(int)
        for ei,[i,j] in enumerate(self.ce_ij):
            e_in = arr2int(core_domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            rx = self.exgt[e_in]
            if rx>=4:
                core[ei] = 1
            if rx==3 or rx==7:
                motion[self.eos[ei]] += 1
            elif rx==1 or rx==5:
                self.eos[ei] = (self.eos[ei]-1)%4
            elif rx==2 or rx==6:
                self.eos[ei] = (self.eos[ei]+1)%4
        # global state and motion
        self.st = membrane.astype(int)
        self.st[1:4,1:4] = core.reshape(3,3)
        self.states.append(self.st.astype(int))
        dx = motion[1]-motion[3]
        dy = motion[0]-motion[2]
        self.ox = 0
        if abs(dx)>abs(dy) and abs(dx)>=self.mt:
            self.j += int(dx/abs(dx))
            self.ox = 1 if int(dx/abs(dx))>0 else 3
        elif abs(dy)>abs(dx) and abs(dy)>=self.mt:
            self.i += int(-dy/abs(dy))
            self.ox = 4 if int(-dy/abs(dy)) else 2
        self.loc.append([self.i,self.j])
        self.motion[self.ox] += 1
        # responses
        cx = arr2int(core)
        mx = ext2int(membrane)
        ex = ext2int(gl_domain)
        self.memb_rxs[mx].add(ex)
        self.core_rxs[cx][self.cx0,mx] += 1
        self.env_rxs[self.ox].add(ex)
        # check for cyclyc states
        if self.cy==True and (cx,mx,ex) not in self.cycles.keys():
            self.cy = False
        if self.cy==False:
            if (cx,mx,ex) in self.cycles.keys():
                self.cys[self.cx0,cx] += 1
        self.cx0 = cx

    def set_cfg(self,st0,x0,y0):
        # location
        self.i,self.j = x0,y0
        self.loc = [[x0,y0]]
        # cycling?
        self.cy = True
        # initial states (assuming initial empty env)
        if st0==14:
            act=[3,1,2,5,8]     # east -> north
        elif st0==12:
            act=[3,7,2,5,8]     # east -> south
        elif st0==21:
            act=[1,5,6,7,8]     # south -> east
        elif st0==23:
            act=[1,3,6,7,8]     # south -> west
        elif st0==34:
            act=[0,3,6,1,5]     # west -> north
        elif st0==32:
            act=[0,3,6,7,5]     # west -> south
        elif st0==41:
            act=[0,1,2,5,7]     # north -> east
        elif st0==43:
            act=[0,1,2,3,7]     # north -> west
        else:
            raise Exception("invalid initial cfg")
        cxi = np.zeros(9).astype(int)
        for ei in act:
            cxi[ei] = 1
        self.cx0 = arr2int(cxi)
        self.st = np.zeros((5,5)).astype(int)
        self.st[1:4,1:4] = cxi.reshape(3,3)
        self.states = [self.st]
        # initial orientations (changing, then fixed-start ones)
        self.eos = np.zeros(9).astype(int)
        eos0 = int(str(st0)[0])%4
        self.eos += eos0
        self.eos[1] = 0
        self.eos[3] = 3
        self.eos[5] = 1
        self.eos[7] = 2
