
import numpy as np
from aux import *
from pyemd import emd

class Glider:
    def __init__(self):
        # current st
        self.st = 0
        # glider past,current,future sts for all canonical cfgs
        self.sts = np.zeros((16,3,5,5))
        # transition matrix in empty env
        self.tm = np.zeros((16,16)).astype(int)
        self.mk_sts()
        # powerset of purviews
        self.pws = bin_matrix(5,nans=True)
        # cfgs where cell vals == 0/1
        self.cvw = np.zeros((9,2,16))
        # cells in purview for every 3x3 center cell
        self.ces_pws = np.zeros((9,5,5))
        self.mk_cvs()
        # cause and effect repertoires (cfs,pws,cells,dists)
        self.cxs = np.zeros((16,32,2,2,2,2,2,16))
        self.mk_cxs()
        self.exs = np.zeros((16,32,2,2,2,2,2,16))
        self.mk_exs()

    def mk_sts(self):
        # glider base sts (SE)
        gi = np.array([[0,0,1],[1,0,1],[0,1,1]])
        gx = np.array([[1,0,0],[0,1,1],[1,1,0]])
        # gl sts: r = 0:SE, 1:NE, 2:NW, 3:SW
        for r in range(4):
            self.sts[4*r+0,1,1:-1,1:-1] = np.rot90(gi,r)
            self.sts[4*r+1,1,1:-1,1:-1] = np.rot90(gx,r)
            self.sts[4*r+2,1,1:-1,1:-1] = np.rot90(np.transpose(gi),r)
            self.sts[4*r+3,1,1:-1,1:-1] = np.rot90(np.transpose(gx),r)
            # past=0 and future=2 sts
            self.sts[4*r:4*(r+1),0] = np.roll(self.sts[4*r:4*(r+1),1],1,axis=0)
            self.sts[4*r:4*(r+1),2] = np.roll(self.sts[4*r:4*(r+1),1],-1,axis=0)
            # horizontal motion
            dj = 1 if r == 0 or r == 1 else -1
            self.sts[4*r,2] = np.roll(self.sts[4*r,2],dj,axis=1)
            self.sts[4*r+1,0] = np.roll(self.sts[4*r+1,0],-dj,axis=1)
            # vertical motion
            di = 1 if r == 0 or r == 2 else -1
            self.sts[4*r+2,2] = np.roll(self.sts[4*r+2,2],di,axis=0)
            self.sts[4*r+3,0] = np.roll(self.sts[4*r+3,0],di,axis=0)
            # txs, only for the empty case
            self.tm[4*r:4*(r+1),4*r:4*(r+1)] = np.roll(np.diag((1,1,1,1)),1,axis=1)

    def mst(self):
        return self.sts[self.st,1]

    def mk_cvs(self):
        # cfgs where 3x3 center cells == 1 or 0
        self.cvw[:,1,:] = self.sts[:,1,1:-1,1:-1].reshape(16,9).T
        self.cvw[:,0,:] = np.abs(self.cvw[:,1,:]-1)
        # pw for all 3x3 cells. sliding window
        for i in range(1,4):
            for j in range(1,4):
                w = np.zeros((5,5)).astype(int)
                w[i-1:i+2,j-1:j+2] = 1
                self.ces_pws[3*(i-1)+j-1] = w

    def mk_cxs(self):
        # first order causes
        for cfg in range(16):
            # active cells forming the glider
            ces = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # for every purview
            for pwi in range(1,32):
                pwx = ces*self.pws[pwi]
                # for each single mechanism
                for e,ce in enumerate(ces):
                    # values for the cxs reps indexes
                    cis = np.zeros(5).astype(int)
                    cis[e] = 1
                    c0,c1,c2,c3,c4 = cis
                    # glider pasts that could have led to cell = 1
                    # valid txs in which cell stx == 1 (mechanism)
                    # gps = np.sum(self.tm*self.cvw[ce,1],axis=1)
                    gps = np.matmul(self.tm,self.cvw[ce,1])
                    # active cells in current purview
                    # info from past st shouldn't be very good (due to the transient cfgs)?
                    pwu = pwx[~np.isnan(pwx)].astype(int)
                    cps = (self.sts[cfg,1]*np.sum([self.ces_pws[pw] for pw in pwu],axis=0))[1:-1,1:-1].flatten().nonzero()[0]
                    # all gl states where cells in purview are active
                    cps_gl = np.array([self.cvw[cpi,1] for cpi in cps])
                    cps_gl = np.pad(cps_gl,(0,5),'constant')[:5,:16]
                    # only valid glider pasts, leading to cell = 1
                    # possible gl past sts where pp cells were active
                    # => number of valid past gl sts where each pp cell past st = 1
                    # cps_pp = np.sum(cps_cfgs*gps,axis=1)
                    cps_pp = np.matmul(cps_gl,gps)
                    # for every gl cfg, the sum of the possibilities of all pp cells
                    self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = np.matmul(cps_gl.T,cps_pp)
                # higher order mechanisms
                mxs = np.where(np.isnan(self.pws),0,1)
                for mi in range(1,32):
                    if np.sum(mxs[mi])>0:
                        # avoid conflicting with already gotten first order mxs
                        cx = np.ones(16)
                        c0,c1,c2,c3,c4 = mxs[mi].astype(int)
                        if c0==1:
                            cx *= self.cxs[cfg,pwi,c0,0,0,0,0]
                        if c1==1:
                            cx *= self.cxs[cfg,pwi,0,c1,0,0,0]
                        if c2==1:
                            cx *= self.cxs[cfg,pwi,0,0,c2,0,0]
                        if c3==1:
                            cx *= self.cxs[cfg,pwi,0,0,0,c3,0]
                        if c4==1:
                            cx *= self.cxs[cfg,pwi,0,0,0,0,c4]
                        self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = cx


        # for all at the same time
        # (self.sts[cfg,1]*self.ces_pws[ces])[:,1:-1,1:-1].reshape(5,9)
        #self.pws*ces





























































#
