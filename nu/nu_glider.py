
import numpy as np
from copy import deepcopy
from nu_fxs import *

#TODO: replace random response for something more sensible (viability based dists?)

class Glider:
    def __init__(self,genotype,st0=1,x0=25,y0=25):
        # gt data
        self.egt = deepcopy(genotype.egt)
        self.cycles = deepcopy(genotype.cycles)
        self.rxs = deepcopy(genotype.rxs)
        self.txs = deepcopy(genotype.txs)
        self.dxs = deepcopy(genotype.dxs)
        # glider trial sts (orientation: 0=north, 1=east, 2=south, 3=west)
        self.st = np.zeros(25).astype(int)
        self.core = None
        self.membrane = None
        self.eos = np.zeros(9).astype(int)
        self.ems = np.zeros(4).astype(int)
        self.i,self.j = x0,y0
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        # threshold for motion
        self.mt = 3
        # trial data
        self.states = []            # 5x5 ndarrays
        self.core_sts = []          # core states (int)
        self.memb_sts = [0]         # membrane states (int)
        self.loc = [[x0,y0]]        # [[xi,yi],...]
        self.motion = [0]           # [m0,m1,...] (0=None,1=E,2=S,3=W,4=N)
        self.dashes = [0]           # env dashes [d0,d1,...]
        self.tx_seq = []            # sequence from broken cycle to a new one
        self.loops = set()             # trial recurrences (list of (2,time) arrays)
        self.set_cfg(st0)

    '''update every element for a new global state'''
    def update(self,gl_domain):
        # update membrane
        self.gl_membrane(gl_domain,mode="all")
        # update core
        self.gl_core(gl_domain)
        # general st
        self.st = self.membrane.astype(int)      # to avoid np inheritance
        self.st[1:4,1:4] = self.core.reshape(3,3)
        self.states.append(self.st)
        # system's motion reaction
        self.gl_motion()
        # data for analysis
        self.gl_data(gl_domain)

    '''update membrane'''
    def gl_membrane(self,domain,mode=""):
        # nothing from core + anything from outside
        if mode=="basic":
            # TODO
            pass
        # outside input > inside input
        elif mode=="delta":
            # TODO
            pass
        # anything from outside
        elif mode=="all":
            self.membrane = np.zeros((7,7)).astype(int)
            domain[1:6,1:6] = 0
            for [i,j] in self.me_ij:
                if np.sum(domain[i-1:i+2,j-1:j+2])>0:
                    self.membrane[i][j] = 1
            self.membrane = self.membrane[1:6,1:6]
        else:
            raise Exception("no mode for mmebrane")

    '''update core'''
    def gl_core(self,domain):
        self.core = np.zeros(9).astype(int)
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain
            e_in = arr2int(domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            # create response if theres isn't one (dict of responses)
            if not e_in in self.egt.keys():
                self.egt[e_in] = list(np.random.randint(0,2,size=(3)))
            sx,rm,lm = self.egt[e_in]
            # activation
            self.core[ei] = sx
            # motor response
            if lm==rm==1:
                self.ems[self.eos[ei]] += 1
            else:
                self.eos[ei] = (self.eos[ei]+rm-lm)%4

    '''bounded group motion'''
    def gl_motion(self):
        dx = self.ems[1]-self.ems[3]
        dy = self.ems[0]-self.ems[2]
        dm = 0
        # select higher sum and move if higher than motion threshold
        if abs(dx)>abs(dy):
            if abs(dx)>self.mt:
                self.j += int(dx/abs(dx))
                dm = 1 if int(dx/abs(dx))>0 else 3
        elif abs(dy)>abs(dx):
            if abs(dy)>self.mt:
                self.i += int(-dy/abs(dy))
                dm = 4 if int(-dy/abs(dy))>0 else 2
        self.loc.append([self.i,self.j])
        self.motion.append(dm)

    '''core st, membrane st, encountered dashes'''
    def gl_data(self,gl_domain):
        # core
        cx0 = self.core_sts[-1]
        cx = arr2int(self.core)
        self.core_sts.append(cx)
        # membrane
        mx0 = self.memb_sts[-1]
        mx = ext2int(self.membrane)
        self.memb_sts.append(mx)
        # encountered dash patterns
        dx0 = self.dashes[-1]
        dx = ext2int(gl_domain,index=False)
        self.dashes.append(dx)
        self.dxs.add(dx)
        # responses
        self.rxs[(cx0,mx0,dx0)].add((cx,mx,self.motion[-1]))
        # transients: if glider breaks out from a cycle
        if len(self.tx_seq)==0 and (cx,mx,dx) not in self.cycles.keys():
            self.tx_seq = [(cx0,mx0,dx0)]
        self.tx_seq.append((cx,mx,dx))
        # transients: if glider comes back to a cycle
        if len(self.tx_seq)>0 and (cx,mx,dx) in self.cycles.keys():
            d0 = self.tx_seq[0][2]
            self.txs[d0].add(tuple(self.tx_seq))
            self.tx_seq = []

    '''search for loops (possible transients/cycles)'''
    def gl_loops(self):
        for i,[ci,mi,di] in enumerate(zip(self.core_sts,self.memb_sts,self.dashes)):
            cxi = np.where(self.core_sts==ci,1,0)
            mxi = np.where(self.memb_sts==mi,1,0)
            # dxi = np.where(self.dashes==di,1,0)
            cxmxi = cxi*mxi
            if np.sum(cxmxi)>1:
                cx = np.where(self.core_sts==ci,self.core_sts,0)
                mx = np.where(self.memb_sts==mi,self.memb_sts,0)
                dx = np.where(self.dashes==di,self.dashes,0)
                loop = np.vstack((cx,mx,dx))
                self.loops.add(loop)

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
        cx = arr2int(self.st[1:4,1:4].flatten())
        self.core_sts.append(cx)













###
