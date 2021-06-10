
import numpy as np
from copy import deepcopy
from nu_fx import *

class Glider:
    def __init__(self,genotype,st0=1,x0=25,y0=25):
        # gt data
        self.egt = deepcopy(genotype.egt)
        self.rxs = deepcopy(genotype.rxs)
        self.cycles = deepcopy(genotype.cycles)
        self.txs = deepcopy(genotype.txs)
        self.dashes = deepcopy(genotype.dashes)
        # glider trial sts (orientation: 0=north, 1=east, 2=south, 3=west)
        self.st = np.zeros(25).astype(int)
        self.eos = np.zeros(9).astype(int)
        self.i = x0
        self.j = y0
        self.tx_seq = []
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        # threshold for motion
        self.mt = 3
        # trial data
        self.states = []
        self.loc = [[x0,y0]]    # [i,j]
        self.core = []          # core states (int)
        self.memb = []          # membrane states (int)
        self.env = []           # encountered dashes ([int1,(int2),...(int4)])
        self.dodm = []          # dominant orientation and motion [do,dm]
        self.loops = []         # trial recurrences (list of (2,time) arrays)
        self.set_cfg(st0)

    '''update every element for a new global state'''
    def update(self,gl_domain):
        # update core
        core_st = np.zeros(9).astype(int)
        core_dxy = np.zeros(4).astype(int)
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain (int)
            e_in = arr2int(gl_domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            # create response if theres isn't one (dict of responses)
            if not e_in in self.egt.keys():
                self.egt[e_in] = list(np.random.randint(0,2,size=(3)))
            sig,rm,lm = self.egt[e_in]
            # update signal, orientation/motion
            core_st[ei] = sig
            if lm==rm==1:
                core_dxy[self.eos[ei]] += 1
            else:
                self.eos[ei] = (self.eos[ei]+rm-lm)%4
        # update membrane
        membrane = np.zeros((7,7)).astype(int)
        me_domain = deepcopy(gl_domain)
        me_domain[1:6,1:6] = 0
        # reaction if any external cell is active
        for [i,j] in self.me_ij:
            if np.sum(me_domain[i-1:i+2,j-1:j+2]) > 0:
                membrane[i][j] = 1
        self.st = membrane[1:6,1:6]
        self.st[1:4,1:4] = core_st.reshape(3,3)
        self.states.append(self.st)
        # system's motion reaction
        self.gl_motion(core_dxy)
        # data for analysis
        self.gl_data(gl_domain)

    '''bounded group motion'''
    def gl_motion(self,dxy):
        dm = 0
        dx = dxy[1]-dxy[3]
        dy = dxy[0]-dxy[2]
        # select higher sum and move if higher than motion threshold
        if abs(dx)>abs(dy):
            do = 1 if dx>0 else 3
            if abs(dx)>self.mt:
                self.j += int(dx/abs(dx))
                dm = 1
        elif abs(dy)>abs(dx):
            do = 0 if dy>0 else 2
            if abs(dy)>self.mt:
                self.i += int(-dy/abs(dy))
                dm = 1
        # so if dx==dy (no dominant orientation)
        else:
            do = -1
        self.loc.append([self.i,self.j])
        self.dodm.append([do,dm])

    '''core st, membrane st, encountered dashes'''
    def gl_data(self,gl_domain):
        # core
        cx = arr2int(self.st[1:4,1:4].flatten())
        self.core.append(cx)
        # membrane
        mx = ext2int(self.st)
        self.memb.append(mx)
        # encountered dash patterns
        dx0 = self.env[-1]
        gl_env = [gl_domain[0,:],gl_domain[:,-1],np.rot90(gl_domain,2)[0,:],np.rot90(gl_domain,2)[:,-1]]
        dxi = [arr2int(ei) if np.sum(ei)>0 else 0 for ei in gl_env]
        self.env.append(dxi)
        if dxi not in self.dashes:
            self.dashes.append(dxi)
        # transitions
        cx0 = arr2int(gl_domain[2:5,2:5].flatten())
        mx0 = ext2int(gl_domain[1:6,1:6])
        # as if nothing new appears (dxi wouldn't be a cause of dx0 otherwise)
        delta_dx = np.where(np.asarray(dx0)>0,1,0)-np.where(np.asarray(dxi)>0,1,0)
        dx = [dxi[i] if x>=0 else 0 for i,x in enumerate(delta_dx)]
        self.rxs[(tuple(dx0),cx0,mx0)] += [[tuple(dx),cx,mx]]
        # if current sequence comes back to some cyclic state
        if len(self.tx_seq)==0 and (cx,mx) not in self.cycles.keys():
            self.tx_seq = [[cx0,mx0]]
        self.tx_seq.append([cx,mx])
        if len(self.tx_seq)>0 and (cx,mx) in self.cycles.keys():
            tx0 = self.tx_seq[0]
            txn = self.tx_seq[-1]
            self.txs[tuple(tx0),tuple(txn)] = self.tx_seq
            self.tx_seq = []

    '''search for existing & new loops (possible cycles)'''
    def gl_loops(self,r=2):
        for sti,[ci,mi] in enumerate(zip(self.core[:-r],self.memb[:-r])):
            loop = np.zeros((2,len(self.states))).astype(int)
            loop_seq = []
            wi = sti
            wx = sti+r
            # sliding window like
            while wx<len(self.states)-1:
                cx,mx = self.core[wx],self.memb[wx]
                if [ci,mi]==[cx,mx]:
                    loop[0][wi:wx+1] = self.core[wi:wx+1]
                    loop[1][wi:wx+1] = self.memb[wi:wx+1]
                    # it could be the case that different seqs happen (pretty rare though)
                    seq = [(c,m) for [c,m] in zip(self.core[wi:wx+1],self.memb[wi:wx+1])]
                    if seq not in loop_seq:
                        loop_seq.append(seq)
                    # windows skips to states after loop
                    wi = wx+1
                    wx = wi+r
                else:
                    wx+=1
            # if something
            if len(loop_seq)>0:
                self.loops.append(loop)
                for seq in loop_seq:
                    # from zero so it closes the loop (last->first)
                    for si in range(0,len(seq)):
                        cs0,ms0 = seq[si-1]
                        cs,ms = seq[si]
                        if not [cs,ms] in self.cycles[(cs0,ms0)]:
                            self.cycles[(cs0,ms0)] += [[cs,ms]]


    '''allocate glider starting from some known cfg'''
    def set_cfg(self,st0):
        # initial signalings
        if st0==1:
            act=[11,17,8,13,18] # east (south)
        elif st0==2:
            act=[7,11,16,17,18] # south (west)
        elif st0==3:
            act=[6,11,16,7,13] # west (north)
        elif st0==0:
            act=[6,7,8,13,17] # north (east)
        else:
            raise Exception("invalid initial cfg")
        for ei in act:
            self.st[ei] = 1
        self.st = self.st.reshape(5,5)
        # initial orientations
        self.eos += st0%4
        # elements with fixed orientations
        self.eos[1] = 0
        self.eos[3] = 3
        self.eos[5] = 1
        self.eos[7] = 2
        # initial state
        self.states.append(self.st)
        st = arr2int(self.st[1:4,1:4].flatten())
        self.core.append(st)
        self.memb.append(0)
        self.env.append([0,0,0,0])













###
