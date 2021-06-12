
import numpy as np
from copy import deepcopy
from nu_fxs import *

#TODO: try di->mi->ci->dx->mx->cx with memb reacting if not core input
#TODO: replace random response for something more sensible (viability based dists?)
# replace defdicts(list) for defdicts(set) (to avoid checking previous instances)

class Glider:
    def __init__(self,genotype,st0=1,x0=25,y0=25):
        # gt data
        self.egt = deepcopy(genotype.egt)
        self.rxs = deepcopy(genotype.rxs)
        self.cycles = deepcopy(genotype.cycles)
        self.txs = deepcopy(genotype.txs)
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
        self.states = []        # 5x5 ndarrays
        self.loc = []           # [xi,yi],...
        self.dxy = []
        self.core = []          # core states (int)
        self.memb = []          # membrane states (int)
        self.env = []           # encountered dashes [d0,d1,d2,d3],...
        self.loops = []         # trial recurrences (list of (2,time) arrays)
        self.dashes = [0]
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
        # update membrane (reaction to any active external cells)
        membrane = np.zeros((7,7)).astype(int)
        me_domain = deepcopy(gl_domain)
        me_domain[1:6,1:6] = 0
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
        dx = dxy[1]-dxy[3]
        dy = dxy[0]-dxy[2]
        ij = 0
        # select higher sum and move if higher than motion threshold
        if abs(dx)>abs(dy):
            if abs(dx)>self.mt:
                self.j += int(dx/abs(dx))
                ij = 1 if int(dx/abs(dx))>0 else 3
        elif abs(dy)>abs(dx):
            if abs(dy)>self.mt:
                self.i += int(-dy/abs(dy))
                ij = 4 if int(-dy/abs(dy))>0 else 2
        self.loc.append([self.i,self.j])
        self.dxy.append(ij)

    '''core st, membrane st, encountered dashes'''
    def gl_data(self,gl_domain):
        # core
        cx0 = self.core[-1]
        cx = arr2int(self.st[1:4,1:4].flatten())
        self.core.append(cx)
        # membrane
        mx0 = self.memb[-1]
        mx = ext2int(self.st)
        self.memb.append(mx)
        # encountered dash patterns
        dx0 = self.env[-1]
        dx = ext2int(gl_domain,index=False)
        self.env.append(dx)
        if dx not in self.dashes:
            self.dashes.append(dx)
        # responses
        if [cx,mx,self.dxy[-1]] not in self.rxs[(cx0,mx0,dx0)]:
            self.rxs[(cx0,mx0,dx0)] += [[cx,mx,self.dxy[-1]]]
        # if glider goes out from a cycle
        if len(self.tx_seq)==0 and (cx,mx,dx) not in self.cycles.keys():
            self.tx_seq = [[cx0,mx0,dx0]]
        self.tx_seq.append([cx,mx,dx])
        # if glider comes back to a cycle
        if len(self.tx_seq)>0 and (cx,mx,dx) in self.cycles.keys():
            d0 = self.tx_seq[0][2]
            self.txs[d0] += [self.tx_seq]
            self.tx_seq = []

    '''search for loops (possible transients/cycles)'''
    def gl_loops(self):
        for i,[ci,mi,di] in enumerate(zip(self.core,self.memb,self.env)):
            skip = []
            cxi = np.where(self.core==ci,1,0)
            mxi = np.where(self.memb==mi,1,0)
            dxi = np.where(self.memb==di,1,0)
            cxmxi = cxi*mxi
            if np.sum(cxmxi)>1:
                if [ci,mi] not in skip:
                    cx = np.where(self.core==ci,self.core,0)
                    mx = np.where(self.memb==mi,self.memb,0)
                    dx = np.where(self.memb==di,self.env,0)
                    loop = np.vstack((cx,mx,dx))
                    self.loops.append(loop)
                    skip.append([ci,mi])

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
        self.loc.append([self.i,self.j])
        self.dxy.append(0)
        self.env.append(0)













###
