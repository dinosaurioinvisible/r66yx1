
import numpy as np
from copy import deepcopy
from nu_fx import xy_around, arr2int, membrane_fx

class Glider:
    def __init__(self,genotype,st0=1,x0=None,y0=None):
        # basal responses and cycles
        self.st0=st0
        self.gt = genotype.basal_responses
        self.basal_sts = genotype.basal_sts
        self.basal_txs = genotype.basal_txs
        self.st = np.zeros(25)
        self.eos = np.zeros(9)
        # pos (orientation: 0=north, 1=east, 2=south, 3=west)
        self.i = x0
        self.j = y0
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        # threshold for motion
        self.mt = 2
        # historic data
        self.ft = 0
        self.hi = [x0]
        self.hj = [y0]
        self.hb = []
        self.states = []
        self.set_cfg()

    def update(self,gl_domain):
        core_st = np.zeros(9)
        motion = [0]*4
        # update core
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain
            bi = arr2int(gl_domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            # create response if theres isn't one
            if not self.gt[bi]:
                self.gt[bi] = list(np.random.randint(0,2,size=(3)))
            sig,rm,lm = self.gt[bi]
            # update
            core_st[ei] = sig
            self.eos[ei] = (self.eos[ei]+rm-lm)%4
            if rm+lm == 2:
                motion[int(self.eos[ei])] += 1
        # update membrane
        self.st = membrane_fx(gl_domain)
        self.st[1:4,1:4] = core_st.reshape(3,3)
        self.st = self.st.flatten()
        # update glider and save data
        self.states.append(self.st)
        gbi = arr2int(self.st.reshape(5,5)[1:4,1:4])
        self.hb.append(gbi)
        self.motion_fx(motion)
        self.ft_fx()

    def ft_fx(self):
        if len(self.hb) > 1:
            if self.hb[-2] not in self.basal_sts:
                if self.hb[-1] in self.basal_sts:
                    self.ft += 1

    def motion_fx(self,motion):
        # east/west
        mx = motion[1] - motion[3]
        # north/south
        my = motion[0] - motion[2]
        # chose the higher and compare to threshold
        if max(abs(mx),abs(my)) > self.mt:
            if abs(mx) > abs(my):
                self.j += mx/abs(mx)
            else:
                self.i -= my/abs(my)
        self.hi.append(deepcopy(self.i))
        self.hj.append(deepcopy(self.j))

    def set_cfg(self,reset=False):
        # reset
        if reset:
            self.st = np.zeros(25)
            self.eos = np.zeros(9)
            self.i = self.hi[0]
            self.j = self.hj[0]
            self.ft = 0
            self.hi = [self.i]
            self.hj = [self.j]
            self.hb = []
            self.states = []
        # initial signalings
        if self.st0==1:
            act=[11,17,8,13,18] # east (south)
        elif self.st0==2:
            act=[7,11,16,17,18] # south (west)
        elif self.st0==3:
            act=[6,11,16,7,13] # west (north)
        elif self.st0==4 or self.st0==0:
            act=[6,7,8,13,17] # north (east)
        else:
            raise("invalid cfg0")
        for ei in act:
            self.st[ei] = 1
        # initial orientations
        self.eos += self.st0%4
        # elements with fixed o
        self.eos[1] = 0
        self.eos[3] = 3
        self.eos[5] = 1
        self.eos[7] = 2
        # initial state
        self.states.append(self.st)
        gbi = arr2int(self.st.reshape(5,5)[1:4,1:4])
        self.hb.append(gbi)


###
