
import numpy as np
from copy import deepcopy
from nu_fx import *

class Glider:
    def __init__(self,genotype,st0=1,x0=25,y0=25):
        # elements responses, glider transitions and known dashes
        self.egt = genotype.egt
        self.txs = genotype.txs
        self.kdp = genotype.kdp
        self.cycles = genotype.cycles
        self.st = np.zeros(25)
        self.eos = np.zeros(9)
        # pos (orientation: 0=north, 1=east, 2=south, 3=west)
        self.i = x0
        self.j = y0
        # elements rel locs and init orientations
        self.ce_ij = xy_around(3,3,r=1,inv=True)
        self.me_ij = xy_around(3,3,r=2,inv=True,ext=True)
        # threshold for motion
        self.mt = 3
        # historic trial data
        self.hi = [x0]
        self.hj = [y0]
        self.states = []
        self.hs = []        # states (int repr)
        self.he = []        # environment (int repr)
        self.hm = []        # motor (1/0)
        self.ho = []        # orientations (int repr)
        self.hcycles = []   # list of sts
        self.set_cfg(st0)

    '''update every element for a new global state'''
    def update(self,gl_domain):
        core_st = np.zeros(9)
        core_xy = np.zeros(4)
        # update core
        for ei,[i,j] in enumerate(self.ce_ij):
            # re-oriented element domain
            be = arr2int(gl_domain[i-1:i+2,j-1:j+2],rot=self.eos[ei])
            # create response if theres isn't one
            if not be in self.egt.keys():
                self.egt[be] = list(np.random.randint(0,2,size=(3)))
            sig,rm,lm = self.egt[be]
            # update signal, orientation/motion
            core_st[ei] = sig
            self.eos[ei] = (self.eos[ei]+rm-lm)%4
            if rm+lm==2:
                core_xy[self.eos.astype(int)[ei]] += 1
        # update membrane, whole glider and motion
        self.st,msx = membrane_fx(gl_domain,self.me_ij,mx="dash")
        self.st[1:4,1:4] = core_st.reshape(3,3)
        # save data
        self.states.append(self.st)
        gbi = arr2int(core_st)
        self.hs.append(gbi)
        self.he.append(msx)
        if msx not in self.kdp:
            self.kdp.append(msx)
        # system's motion reaction
        self.gl_motion(core_xy)

    '''bounded group motion'''
    def gl_motion(self,core_xy):
        # select higher sum and move if higher than motion threshold
        dx = core_xy[1]-core_xy[3]
        dy = core_xy[0]-core_xy[2]
        do = core_xy.argmax()
        di,dj = 0,0
        if abs(dx)>abs(dy) and abs(dx)>self.mt:
            self.j += int(dx/abs(dx))
            do = 1 if dx>0 else 3
        elif abs(dy)>abs(dx) and abs(dy)>self.mt:
            self.i += int(-dy/abs(dy))
            do = 0 if dy>0 else 2
        self.hi.append(self.i)
        self.hj.append(self.j)
        # motion with respect to orientation
        self.hm.append(abs(di+dj))
        mo = arr2int(np.where(self.eos==do,1,0))
        self.ho.append(mo)

    '''count cycles'''
    def fin(self):
        # trial transitions
        self.txs.append(self.hs)
        # known cycles
        for cx in self.cycles:
            cy = False
            cycle = np.zeros(len(self.hs))
            for i in range(len(self.hs)-len(cx)):
                sti = self.hs[i:i+len(cx)]
                if cx==sti:
                    cy = True
                    cycle[i:i+len(cx)] = cx
            if cy:
                self.hcycles.append(cycle)
        # new cycles
        for wsize in range(3,8):
            # last window (wsize=3): 94,95,96 compared with 97,98,99
            for wi in range(len(self.hs)-wsize*2):
                cy_sts = None
                cycle = np.zeros(len(self.hs))
                window_sts = self.hs[wi:wi+wsize]
                for sti in range(wi+wsize,len(self.hs)-wsize):
                    cy = False
                    gl_sts = self.hs[sti:sti+wsize]
                    if window_sts==gl_sts:
                        cy = True
                        cycle[sti:sti+wsize] = gl_sts
                        cy_sts = window_sts
                if cy:
                    self.hcycles.append(cycle)
                    new = True
                    for known_cycle in self.cycles:
                        if cy_sts==known_cycle:
                            new = False
                    if new:
                        self.cycles.append(cy_sts)

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
        gbi = arr2int(self.st[1:4,1:4].flatten())
        self.hs.append(gbi)













###
