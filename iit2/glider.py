
import numpy as np
from aux import *
from pyemd import emd
from itertools import combinations,chain

'''
There are 6 options for measuring phi, that i can think of:
1. system made of 1s (only 1s can be infomative)
2. considering past/fut 0s as informative as well
3. broadened pws, considering a 3x3 pw for each cell
4. system as organization, so of 7 (2->0,3=1,2->1) elements
5. system as the lattice, including 0s and 1s
6. retrotxs, so that info comes from change, not from sts
'''

'''
there are 3 options for constructing the purviews:
1. (A)(B)CDE: considering past cfg (but where would this info come from?)
2. ()()CDE()(): considering only elements in past & present (but FG are there!)
3. ()()CDEFG: considering present cfg and look into the past
so then, taking opt3, we could:
2a. consider only 1s as informative (but this would lead to opt2)
2b. consider 0s as informative as well, of destruction and creation
=> info from past/fut cfgs where A=0 or 1, given that current mxA = pwA = 1
so for every cfg there is info about what it was not there (from FG),
but still there is a loss of complete information (AB)
'''

class Glider:
    def __init__(self,pw_mode=1):
        # current st
        self.st = 0
        # glider past,current,future sts for all canonical cfgs
        self.sts = np.zeros((16,3,5,5))
        # transition matrix in empty env
        self.tm = np.zeros((16,16)).astype(int)
        # active mechanisms vals for every cfg, given current gl cfg (cfg,mxs,vals)
        self.mxs = np.zeros((16,31,16))
        # cell 1/0 vals in past & fut (from current cfg pov)
        self.ppws = []
        self.fpws = []
        self.mk_glider()
        # cause and effect repertoires (cfgs,mxs,pws,dists)
        self.cxs = np.zeros((16,31,31,16))
        self.exs = np.zeros((16,31,31,16))
        self.mk_reps()


    def mk_glider(self):
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
        # make mechanisms
        # domain of active cells (5) for each ('current/present') glider cfg
        cfgs = self.sts[:,1,1:-1,1:-1].reshape(16,9)
        # for composition of higher order subsys (AB,ABC,ABCD,etc) (31, omitting all zeroes)
        xis = list(chain.from_iterable([list(combinations(np.arange(5),i)) for i in range(2,6)]))
        # first order mechanisms (active cells)
        ### (this could be also made by taking indices only, and building all 512 subsys once)
        for cfg in range(16):
            # active cells (5), acting as causal mechanisms for given cfg
            ### (in an empty space, all cells=0 become part of the env(?))
            cfg_mxs = cfgs[cfg].nonzero()[0]
            # gl cfgs where these cells are active (i.e. mechanisms) from the 16 cgs
            self.mxs[cfg][:5] = cfgs.T[cfg_mxs]
            # higher order mechanisms
            for me,mx in enumerate(xis):
                # combination of the 5 1st order mechanisms
                self.mxs[cfg][me+5] = np.product(self.mxs[cfg][np.asarray(mx)],axis=0)
        # past/fut purviews (considering system motion to avoid ill refs like c0==c1)
        pp1 = self.sts[:,0,1:-1,1:-1].reshape(16,9).T
        pps = [np.abs(pp1-1),pp1]
        fp1 = self.sts[:,2,1:-1,1:-1].reshape(16,9).T
        fps = [np.abs(fp1-1),fp1]
        # until i find a better way to do this
        for cfg in range(16):
            ppws,fpws = [],[]
            cfg_pws = cfgs[cfg].nonzero()[0]
            # first order
            for pi in cfg_pws:
                ppws.append([pps[0][pi],pps[1][pi]])
                fpws.append([fps[0][pi],fps[1][pi]])
            # second order
            for a,b in list(combinations(cfg_pws,2)):
                ppws.append([pps[0][a]*pps[0][b],pps[0][a]*pps[1][b],pps[1][a]*pps[0][b],pps[1][a]*pps[1][b]])
                fpws.append([fps[0][a]*fps[0][b],fps[0][a]*fps[1][b],fps[1][a]*fps[0][b],fps[1][a]*fps[1][b]])
            # third order
            for a,b,c in list(combinations(cfg_pws,3)):
                p3p,p3f = [],[]
                for u in range(8):
                    i,j,k = int2arr(u,3)
                    p3p.extend([pps[i][a]*pps[j][b]*pps[k][c]])
                    p3f.extend([fps[i][a]*fps[j][b]*fps[k][c]])
                ppws.append(p3p)
                fpws.append(p3f)
            # 4th order
            for a,b,c,d in list(combinations(cfg_pws,4)):
                p4p,p4f = [],[]
                for u in range(16):
                    i,j,k,l = int2arr(u,4)
                    p4p.extend([pps[i][a]*pps[j][b]*pps[k][c]*pps[l][d]])
                    p4f.extend([fps[i][a]*fps[j][b]*fps[k][c]*fps[l][d]])
                ppws.append(p4p)
                fpws.append(p4f)
            # system pw
            # easier using tm
            self.ppws.append(ppws)
            self.fpws.append(fpws)

    def glst(self):
        # simple return glider state as 2d rep
        return self.sts[self.st,1]

    def mk_reps(self):
        # first order causes
        for cfg in range(16):
            # indices for purviews
            pwi = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # all purviews for every elementary mechanism
            for me in range(5):
                # everything works using matmul, but sum,axis for causal clarity
                mx = self.mxs[cfg,me]
                # valid past sts leading to current mx=1
                glp_mx = np.sum(self.tm*mx,axis=1)
                #

                import pdb; pdb.set_trace()




        # # first order causes
        # for cfg in range(16):
        #     # active cells forming the glider
        #     ces = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
        #     # for every purview
        #     for pwi in range(1,32):
        #         pwx = ces*self.pws[pwi]
        #         # for each single mechanism
        #         for e,ce in enumerate(ces):
        #             # values for the cxs reps indexes
        #             cis = np.zeros(5).astype(int)
        #             cis[e] = 1
        #             c0,c1,c2,c3,c4 = cis
        #             # glider pasts that could have led to cell = 1
        #             # valid txs in which cell stx == 1 (mechanism)
        #             # gps = np.sum(self.tm*self.cvw[ce,1],axis=1)
        #             gps = np.matmul(self.tm,self.cvw[ce,1])
        #             # active cells in current purview
        #             # info from past st shouldn't be very good (due to the transient cfgs)?
        #             pwu = pwx[~np.isnan(pwx)].astype(int)
        #             cps = (self.sts[cfg,1]*np.sum([self.ces_pws[pw] for pw in pwu],axis=0))[1:-1,1:-1].flatten().nonzero()[0]
        #             # all gl states where cells in purview are active
        #             cps_gl = np.array([self.cvw[cpi,1] for cpi in cps])
        #             cps_gl = np.pad(cps_gl,(0,5),'constant')[:5,:16]
        #             # only valid glider pasts, leading to cell = 1
        #             # possible gl past sts where pp cells were active
        #             # => number of valid past gl sts where each pp cell past st = 1
        #             # cps_pp = np.sum(cps_cfgs*gps,axis=1)
        #             cps_pp = np.matmul(cps_gl,gps)
        #             # for every gl cfg, the sum of the possibilities of all pp cells
        #             self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = np.matmul(cps_gl.T,cps_pp)
        #         # higher order mechanisms
        #         mxs = np.where(np.isnan(self.pws),0,1)
        #         for mi in range(1,32):
        #             if np.sum(mxs[mi])>0:
        #                 # avoid conflicting with already gotten first order mxs
        #                 cx = np.ones(16)
        #                 c0,c1,c2,c3,c4 = mxs[mi].astype(int)
        #                 if c0==1:
        #                     cx *= self.cxs[cfg,pwi,c0,0,0,0,0]
        #                 if c1==1:
        #                     cx *= self.cxs[cfg,pwi,0,c1,0,0,0]
        #                 if c2==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,c2,0,0]
        #                 if c3==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,0,c3,0]
        #                 if c4==1:
        #                     cx *= self.cxs[cfg,pwi,0,0,0,0,c4]
        #                 self.cxs[cfg,pwi,c0,c1,c2,c3,c4] = cx
        #












































# pws (domain) for all 3x3 cells. sliding window
# ces_pws = np.zeros((9,5,5))
# for i in range(1,4):
#     for j in range(1,4):
#         w = np.zeros((5,5)).astype(int)
#         w[i-1:i+2,j-1:j+2] = 1
#         ces_pws[3*(i-1)+j-1] = w
# # reduce to 3x3 (empty env, so no active cells outside)
# ces_pws = ces_pws[:,1:-1,1:-1]
# active cells for every glider cfg
# cfgs = self.sts[:,1,1:-1,1:-1]
# active cells in each active cell purview for every glider cfg
# for cfg in range(16):
    # pw : glider cfg * cells purview * only active cells in that cfg
    # cfg_pws = cfgs.reshape(16,9)[cfg] * ces_pws.reshape(9,9) * np.array(self.sts[cfg,1,1:-1,1:-1].flatten()).reshape(9,1)
    # self.pws[cfg][:5] = cfg_pws[~np.all(cfg_pws==0,axis=1)]













#
