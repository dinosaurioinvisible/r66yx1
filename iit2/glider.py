
import numpy as np
from aux import *
from pyemd import emd

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
    def __init__(self):
        # current st
        self.st = 0
        # glider past,current,future sts for all canonical cfgs
        self.sts = np.zeros((16,3,5,5))
        # transition matrix in empty env
        self.tm = np.zeros((16,16)).astype(int)
        # active mechanisms vals for every cfg, given current gl cfg (cfg,mxs,vals)
        self.mxs = np.zeros((16,31,16))
        # cell 1/0 vals in past & fut (from current cfg pov)
        self.ppws = np.zeros((16,5,16))
        self.fpws = np.zeros((16,5,16))
        self.mk_glider()
        # cause and effect repertoires (cfgs,mxs,pws,dists)
        self.cxs = np.zeros((16,31,31,16))
        self.mk_cxs()
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
            # txs, only for the empty case
            self.tm[4*r:4*(r+1),4*r:4*(r+1)] = np.roll(np.diag((1,1,1,1)),1,axis=1)
        # override past/future sts where there is translation
        for cfg in [0,6,8,14]:
            # horizontal
            dj = 1 if cfg in [0,6] else -1
            self.sts[cfg,2] = np.roll(self.sts[cfg,2],dj,axis=1)
            self.sts[cfg+1,0] = np.roll(self.sts[cfg+1,0],-dj,axis=1)
        # current (t) -> future <=> past <- current (t+1)
        for cfg in [2,4,10,12]:
            # vertical
            di = 1 if cfg in [2,12] else -1
            self.sts[cfg,2] = np.roll(self.sts[cfg,2],di,axis=0)
            self.sts[cfg+1,0] = np.roll(self.sts[cfg+1,0],-di,axis=0)
        # make mechanisms
        # for composition of higher order subsys (AB,ABC,ABCD,etc) (31, omitting all zeroes)
        mx_subsys = powerset(5,min_set_size=2)
        # first order mechanisms (active cells)
        ### (this could be also made by taking indices only, and building all 512 subsys once)
        for cfg in range(16):
            # active cells (5), acting as causal elementary mechanisms for given cfg
            ### (in an empty space, all cells=0 become part of the env(?))
            cfg_mxs = self.sts[cfg,1,1:-1,1:-1].flatten().nonzero()[0]
            # gl cfgs where these cells are active (i.e. mechanisms) from the 16 cfgs
            self.mxs[cfg,:5] = self.sts[:,1,1:-1,1:-1].reshape(16,9).T[cfg_mxs]
            # higher order mechanisms
            for me,mx in enumerate(mx_subsys):
                # all combinations of the (5) 1st order mechanisms
                self.mxs[cfg,me+5] = np.product(self.mxs[cfg][np.asarray(mx)],axis=0)
        # make purviews
        # cfgs as future and past from other cgfs (considering production/motion)
        ### (this is to avoid ill references/comparisons like c0==c1)
        self.as_fsts = np.zeros((16,5,5))
        for cfg in range(16):
            # following the transition matrix
            fst = self.tm[:,cfg].nonzero()[0]
            # get current cfg's fut from the cfg which future is current cfg
            self.as_fsts[cfg] = self.sts[fst,2]
        # pasts are the pasts of every next cfg in self.sts
        self.as_psts = np.roll(self.sts[:,0],-1,axis=0)
        # past/fut elementary purviews
        for cfg in range(16):
            # current active cells (elementary purviews)
            cfg_pws = self.sts[0,1,1:-1,1:-1].flatten().nonzero()[0]
            # for every active cell in current cfg, all cfgs vals 0/1
            self.fpws[cfg] = self.as_fsts[:,1:-1,1:-1].reshape(16,9).T[cfg_pws]
            self.ppws[cfg] = self.as_psts[:,1:-1,1:-1].reshape(16,9).T[cfg_pws]

    def mk_cxs(self):
        # for higher order combinations of purviews
        pws2 = powerset(5,min_set_size=2,max_set_size=2)
        pws3 = powerset(5,min_set_size=3,max_set_size=3)
        pws4 = powerset(5,min_set_size=4,max_set_size=4)
        # for causes, for each mx we need all pws
        for cfg in range(16):
            # all can be done with matmul, but i prefer sum,axis for clarity
            for me,mx in enumerate(self.mxs[cfg]):
                # past gl cfgs that could have led to mx=1
                psmx = np.sum(self.tm*mx,axis=1)
                # cxs from elementary purviews for mx
                self.cxs[cfg,me,:5] = np.sum(self.ppws[cfg]*psmx,axis=1).reshape(5,1)*self.ppws[cfg] + np.sum(np.abs(self.ppws[cfg]-1)*psmx,axis=1).reshape(5,1)*np.abs(self.ppws[cfg]-1)
                # second order pws (10)
                for pwe,pwi in enumerate(pws2):
                    # for every subsystem of 2 elements
                    ab = self.ppws[cfg][np.asarray(pwi)]
                    # a1b1, b1a0, a0b0, b0a1
                    pwx = np.vstack((ab,np.abs(ab-1))) * np.roll(np.vstack((ab,np.abs(ab-1))),-1,axis=0)
                    self.cxs[cfg,me,5+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(4,1)*pwx,axis=0)
                # third order pws (10)
                for pwe,pwi in enumerate(pws3):
                    # for each subsystem of 3 elements
                    a,b,c = self.ppws[cfg][np.asarray(pwi)]
                    # a0x4,a1x4 * b0x2,b1x2;x2 * c0c1;x4
                    pwx = np.repeat([np.abs(a-1),a],[4,4],axis=0) * np.tile([np.abs(b-1),b],(2,2)).reshape(8,16) * np.tile([np.abs(c-1),c],(4,1))
                    self.cxs[cfg,me,15+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(8,1)*pwx,axis=0)
                # fourth order (5)
                for pwe,pwi in enumerate(pws4):
                    # for each subsystem of 4 elements
                    a,b,c,d = self.ppws[cfg][np.asarray(pwi)]
                    # same, but a0x8,a1x8, etc
                    pwx = np.repeat([np.abs(a-1),a],[8,8],axis=0) * np.tile([np.abs(b-1),b],(2,4)).reshape(16,16) * np.tile([np.abs(c-1),c],(4,2)).reshape(16,16) * np.tile([np.abs(d-1),d],(8,1))
                    self.cxs[cfg,me,25+pwe] = np.sum(np.sum(pwx*psmx,axis=1).reshape(16,1)*pwx,axis=0)
                # all elements together (whole system) (1)
                a,b,c,d,e = self.ppws[cfg]
                pwx = np.repeat([np.abs(a-1),a],[16,16],axis=0) * np.tile([np.abs(b-1),b],(2,8)).reshape(32,16) * np.tile([np.abs(c-1),c],(4,4)).reshape(32,16) * np.tile([np.abs(d-1),d],(8,2)).reshape(32,16) * np.tile([np.abs(e-1),e],(16,1))
                self.cxs[cfg,me,30] = np.sum(np.sum(pwx*psmx,axis=1).reshape(32,1)*pwx,axis=0)
                # turn counts into distributions
                self.cxs[cfg,me] /= np.sum(self.cxs[cfg,me],axis=1).reshape(31,1)

        import pdb; pdb.set_trace()

        # self.lx_ppws,self.lx_fpws = [],[]
        # pp1 = self.sts[:,0,1:-1,1:-1].reshape(16,9).T
        # pps = [np.abs(pp1-1),pp1]
        # fp1 = self.sts[:,2,1:-1,1:-1].reshape(16,9).T
        # fps = [np.abs(fp1-1),fp1]
        # # until i find a better way to do this
        # for cfg in range(16):
        #     ppws,fpws = [],[]
        #     cfg_pws = self.sts[cfg,1,1:-1,1:-1].nonzero()[0]
        #     # first order
        #     for pi in cfg_pws:
        #         ppws.append([pps[0][pi],pps[1][pi]])
        #         fpws.append([fps[0][pi],fps[1][pi]])
        #     # second order
        #     for a,b in list(combinations(cfg_pws,2)):
        #         ppws.append([pps[0][a]*pps[0][b],pps[0][a]*pps[1][b],pps[1][a]*pps[0][b],pps[1][a]*pps[1][b]])
        #         fpws.append([fps[0][a]*fps[0][b],fps[0][a]*fps[1][b],fps[1][a]*fps[0][b],fps[1][a]*fps[1][b]])
        #     # third order
        #     for a,b,c in list(combinations(cfg_pws,3)):
        #         p3p,p3f = [],[]
        #         for u in range(8):
        #             i,j,k = int2arr(u,3)
        #             p3p.extend([pps[i][a]*pps[j][b]*pps[k][c]])
        #             p3f.extend([fps[i][a]*fps[j][b]*fps[k][c]])
        #         ppws.append(p3p)
        #         fpws.append(p3f)
        #     # 4th order
        #     for a,b,c,d in list(combinations(cfg_pws,4)):
        #         p4p,p4f = [],[]
        #         for u in range(16):
        #             i,j,k,l = int2arr(u,4)
        #             p4p.extend([pps[i][a]*pps[j][b]*pps[k][c]*pps[l][d]])
        #             p4f.extend([fps[i][a]*fps[j][b]*fps[k][c]*fps[l][d]])
        #         ppws.append(p4p)
        #         fpws.append(p4f)
        #     # system pw
        #     #
        #     # easier using tm
        #     self.lx_ppws.append(ppws)
        #     self.lx_fpws.append(fpws)
        # import pdb; pdb.set_trace()

    def glst(self):
        # simple return glider st as 2d rep & active cells indices
        return self.sts[self.st,1],self.sts[self.st,1,1:-1,1:-1].flatten().nonzero()[0]

    def mk_reps(self):
        # # causes
        # for cfg in range(16):
        #     # everything works using matmul, but sum,axis for causal clarity
        #     for me,mx in enumerate(self.mxs[cfg]):
        #         # valid past gl cfgs leading to current mx=1
        #         glp_mx = np.sum(self.tm*mx,axis=1)
        #         # for each purview
        #         for pwi,pwx in enumerate(self.lx_ppws[cfg][:-1]):
        #             # past pws vals leading to current cfg, where: mx = c pws = 1
        #             self.cxs[cfg,me,pwi] = np.sum(np.sum(glp_mx*pwx,axis=1).reshape(len(pwx),1)*pwx,axis=0)
        #         # system purview
        #         self.cxs[cfg,me,30] = np.sum(self.cxs[cfg,me,:5],axis=0)
        #         # as distributions
        #         mx_sums = np.sum(self.cxs[cfg,me],axis=1)
        #         mx_sums = np.where(mx_sums==0,1,0).reshape(31,1)
        #         self.cxs[cfg,me] = self.cxs[cfg,me]/mx_sums
        # import pdb; pdb.set_trace()
        # effects
        return
        for cfg in range(16):
            # is similar, but not the same, so better apart for clarity
            for me,mx in enumerate(self.mxs[cfg]):
                # elementary purviews
                a0,a1 = self.fpws[cfg][0]
                b0,b1 = self.fpws[cfg][1]
                c0,c1 = self.fpws[cfg][2]
                d0,d1 = self.fpws[cfg][3]
                e0,e1 = self.fpws[cfg][4]
                # likelihood of fut values for pw=0 and pw=1
                fa = np.sum(self.tm*a0)*a0 + np.sum(self.tm*a1)*a1
                fb = np.sum(self.tm*b0)*b0 + np.sum(self.tm*b1)*b1
                fc = np.sum(self.tm*c0)*c0 + np.sum(self.tm*c1)*c1
                fd = np.sum(self.tm*d0)*d0 + np.sum(self.tm*d1)*d1
                fe = np.sum(self.tm*e0)*e0 + np.sum(self.tm*e1)*e1
                # valid fut values for pws, given that mx = 1 = current pw
                m1 = np.sum(self.tm * mx.T,axis=0)
                mxa = np.sum(m1*a0)*a0 + np.sum(m1*a1)*a1
                mxb = np.sum(m1*b0)*b0 + np.sum(m1*b1)*b1
                mxc = np.sum(m1*c0)*c0 + np.sum(m1*c1)*c1
                mxd = np.sum(m1*d0)*d0 + np.sum(m1*d1)*d1
                mxe = np.sum(m1*e0)*e0 + np.sum(m1*e1)*e1
                # elementary pws fut values, given mechanism mx = 1
                self.exs[cfg,me,0] = mxa * fb*fc*fd*fe
                self.exs[cfg,me,1] = fa* mxb *fc*fd*fe
                self.exs[cfg,me,2] = fa*fb* mxc *fd*fe
                self.exs[cfg,me,3] = fa*fb*fc* mxd *fe
                self.exs[cfg,me,4] = fa*fb*fc*fd * mxe

                # import pdb; pdb.set_trace()
                # higher order purview
                for pwi,pwx in enumerate(self.fpws[cfg][5:-1]):
                    # fut pws vals given current cfg, where mx = c pws = 1
                    pass

                    # import pdb; pdb.set_trace()


        # fut values for a=0 and a=1 (pws without mechanisms yet)
        # fa = np.sum(self.tm*self.a0)*self.a0 + np.sum(self.tm*self.a1)*self.a1
        # fb = np.sum(self.tm*self.b0)*self.b0 + np.sum(self.tm*self.b1)*self.b1
        # fc = np.sum(self.tm*self.c0)*self.c0 + np.sum(self.tm*self.c1)*self.c1
        # mechanisms
        # m1 = np.sum(self.tm * self.a1.T,axis=0)
        # mx1 = np.sum(m1*self.a0)*self.a0 + np.sum(m1*self.a1)*self.a1
        # cxa1 = mx1 * fb * fc

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
