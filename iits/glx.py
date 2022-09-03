import numpy as np
from aux import *
from pyemd import emd

'''
#1
when considering what/where is the glider at every t,
instead of taking a 3x3 or 5x5 displaced domain
we can, using a 7x7 domain, follow production, so
creation and destruction (activation & deactivation)
given the autonomous organization of the glider
#2
regarding what is the unconstrained behavior
we could, in this case consider 3 different levels,
a) the organized, autonomous glider
b) the organized, but untraceble, game of life (world)
c) and the unorganized case posed by the iit (free-like)
#3
about the repertoires calculation,
given the empty environment,
we know that only the glider's core will change
so we can compute the dists on that 3x3 domain
'''


class Glider:
    def __init__(self):
        # glider st for every canonical cfg in empty env
        self.sts = np.zeros((16,5,5))
        # transition matrix in empty env
        self.tm = np.zeros((16,16)).astype(int)
        self.mk_sts()
        # cfgs where cell vals == 0/1
        self.cvw = np.zeros((25,2,16))
        # cells in purview for every cell (flattened)
        self.pws = np.zeros((25,25)).astype(int)
        self.mk_cvs()
        # cause and effect repertoires
        self.cxs = np.zeros((25,))
        self.mk_cxs()

    def mk_sts(self):
        # some glider base cfgs (this cycle moves south west)
        gi = np.array([[np.nan,np.nan,0,0,0],[0,0,0,1,0],[0,1,0,1,0],[0,0,1,1,0],[np.nan,0,0,0,0]])
        gx = np.array([[0,0,0,np.nan,np.nan],[0,1,0,0,0],[0,0,1,1,0],[0,1,1,0,0],[0,0,0,0,np.nan]])
        # 0*:SE, 1*:NE, 2*:NW, 3*:SW
        for r in range(4):
            self.sts[4*r+0] = np.rot90(gi,r)
            self.sts[4*r+1] = np.rot90(gx,r)
            self.sts[4*r+2] = np.rot90(np.transpose(gi),r)
            self.sts[4*r+3] = np.rot90(np.transpose(gx),r)
            # txs, only for the empty case
            for j in range(4):
                self.tm[4*r+j,4*r+(j+1)%4] = 1

    def mk_cvs(self):
        # cfgs where cells == 0
        self.cvw[:,0,:] = np.abs(self.sts.reshape(16,25).T-1)
        # cfgs where cells == 1
        self.cvw[:,1,:] = self.sts.reshape(16,25).T
        # sliding window
        for i in range(5):
            for j in range(5):
                w = np.zeros((5,5)).astype(int)
                w[max(0,i-1):i+2,max(0,j-1):j+2] = 1
                self.pws[5*i+j] = w.flatten()

    #def mk_cxs(self):
        # first order causes
        #for ce in range()

    def mk_ucp(self):
        # iit homogeneous uc past
        self.ucp_iit = np.ones(512)/512
        # gol unconstrained past (gol rules)
        # all 512 possibilities (3x3)
        mr = matrix_reps(m=3,n=3)
        # sts in which center cell == 1
        m1 = mr[:,1,1]
        # sum of active cells
        ms = np.sum(mr.reshape(512,9),axis=1)
        # sts maintaining center cell alive
        self.ucp_gol = np.where(ms==2,1,0)*m1+np.where(ms==3)




























#
