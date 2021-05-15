
import numpy as np
from copy import deepcopy
from nu_fx import *

class Glider:
    def __init__(self,genotype,st0=1,x0=None,y0=None):
        # basal responses and cycles
        self.st0 = st0
        self.rps = genotype.rps
        self.txs = genotype.txs
        self.grs = genotype.grs
        self.st = np.zeros(25)
        self.eos = np.zeros(9)
        # pos (orientation: 0=north, 1=east, 2=south, 3=west)
        self.i = x0
        self.j = y0
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        # threshold for motion
        self.mt = 3
        # historic data
        self.recs = 0
        self.hi = [x0]
        self.hj = [y0]
        self.states = []
        self.hb = [tx[0] for tx in self.txs]
        self.set_cfg()

    def update(self,gl_domain):
        core_st = np.zeros(9)
        core_xy = [0]*4
        # update core
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain
            be = arr2int(gl_domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            # create response if theres isn't one
            if not self.rps[be]:
                self.rps[be] = list(np.random.randint(0,2,size=(3)))
            sig,rm,lm = self.rps[be]
            # update
            core_st[ei] = sig
            self.eos[ei] = (self.eos[ei]+rm-lm)%4
            #core_xy.append(int((rm-lm)/2))
            if rm+lm == 2:
                core_xy[int(self.eos[ei])] += 1
        # update membrane and glider states
        self.st,gms = membrane_fx(gl_domain)
        self.st[1:4,1:4] = core_st.reshape(3,3)
        self.states.append(self.st)
        gbi = arr2int(core_st)
        self.hb.append(gbi)
        # glider motion and orientation
        dxy = np.asarray([core_xy[1]-core_xy[3],core_xy[0]-core_xy[2]])
        dj,di = np.where(abs(dxy)>=max(max(abs(dxy)),self.mt),dxy/max(max(abs(dxy)),1),0).astype(int)
        dj,di = (0,0) if abs(di)==abs(dj) else (dj,di)
        self.j,self.i = (self.j+dj,self.i-di)
        self.hi.append(deepcopy(self.i))
        self.hj.append(deepcopy(self.j))
        # glider general response (motion, orientation, membrane)
        gxy = [abs(dj+di)]
        go = arr2group(self.eos,xmax=True,bin=True)
        gl_response = arr2int(np.asarray(gxy+go+gms))
        self.grs.append(gl_response)
        # update fitness
        self.recs_fx()

    def recs_fx(self):
        tx = [self.hb[-2],self.hb[-1]]
        if tx not in self.txs:
            if self.hb[-1] in self.hb[:-1]:
                self.recs += 1
        self.txs.append(tx)

    def set_cfg(self,st0=None,reset=False,gt=None):
        # reset
        if reset:
            if st0 and st0!=self.st0:
                self.st0 = st0
            self.eos = np.zeros(9)
            self.st = np.zeros(25)
            self.states = []
            self.i = self.hi[0]
            self.j = self.hj[0]
            self.hi = [self.i]
            self.hj = [self.j]
            self.recs = 0
            self.hb = [tx[0] for tx in self.txs[:16]]
            if not gt:
                raise Exception("can't reset without genotype")
            self.grs = gt.grs
            self.rps = gt.rps
            self.txs = gt.txs
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
            raise Exception("invalid cfg0")
        for ei in act:
            self.st[ei] = 1
        self.st = self.st.reshape(5,5)
        # initial orientations
        self.eos += self.st0%4
        # elements with fixed o
        self.eos[1] = 0
        self.eos[3] = 3
        self.eos[5] = 1
        self.eos[7] = 2
        # initial state
        self.states.append(self.st)
        gbi = arr2int(self.st[1:4,1:4].flatten())
        self.hb.append(gbi)
        go = arr2group(self.eos,xmax=True,bin=True)
        gr = [0]+go+[0]*4
        gl_r0 = arr2int(np.asarray(gr))
        self.grs.append(gl_r0)


###
