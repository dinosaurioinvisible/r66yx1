
import numpy as np
from pyemd import emd
from helper_fxs import *

class ABC:
    def __init__(self,st=100):
        # int<>bin dicts
        self.i2b = int2bin(3)
        self.b2i = bin2int(3)
        # current state
        self.state = np.asarray([int(i) for i in str(st)])
        # tx matrix
        self.tm = np.zeros((8,8))
        self.cxs = np.zeros((7,3,3,3,8))
        self.exs = np.zeros((7,3,3,3,8))
        # distance matrix
        self.dm = dist_matrix(dim=8,cost=1)
        # make
        self.make_abc()
        self.make_at_abc()
        self.info()

    def make_abc(self):
        # A:OR, B:AND, C:XOR
        for sti in range(8):
            ai,bi,ci = self.i2b[sti]
            ax = bi or ci
            bx = ai and ci
            cx = ai ^ bi
            stx = self.b2i[(ax,bx,cx)]
            self.tm[sti,stx] = 1
        # elem. mechanisms 1/0 indices (with respec to system sts)
        self.a1 = np.array([[0,1,0,1,0,1,0,1]])
        self.b1 = np.array([[0,0,1,1,0,0,1,1]])
        self.c1 = np.array([[0,0,0,0,1,1,1,1]])
        self.a0,self.b0,self.c0 = [np.absolute(u1-1) for u1 in [self.a1,self.b1,self.c1]]
        # higher order mechanisms indices
        self.ab = [np.roll(self.a0*self.b0,i) for i in range(4)]
        self.bc = [np.roll(self.b0*self.c0,i) for i in range(0,8,2)]
        self.ac = [np.roll(self.a0*self.c0,i) for i in [0,1,4,5]]
        # mechanisms/purviews
        self.pws = [[self.a0,self.a1],[self.b0,self.b1],[self.c0,self.c1],self.ab,self.bc,self.ac]
        # mechanisms (current) states
        ax,bx,cx = self.state
        self.mx_sts = [[ax,2,2],[2,bx,2],[2,2,cx],[ax,bx,2],[2,bx,cx],[ax,2,cx],[ax,bx,cx]]
        # first order causes:
        # for causes: AB/BC=00 -> AB/B=0 x AB/C=0
        for pwi,pw in enumerate(self.pws):
            # for every elementary mechanism
            for ai,ax in enumerate([self.a0,self.a1]):
                # system values in which A=1/0
                abc_ax = np.sum(self.tm*ax,axis=1)
                # probabilities of pw (ex.AB=00/01/10/11) given A=1/0
                pw_ax = np.sum([np.sum(abc_ax*pwx)*pwx for pwx in pw],axis=0)
                # causes for A=1/0, B=unknown, C=unknown
                self.cxs[pwi,ai,2,2] = pw_ax
            # same for B=0/1, C=0/1
            for bi,bx in enumerate([self.b0,self.b1]):
                self.cxs[pwi,2,bi,2] = np.sum([np.sum(np.sum(self.tm*bx,axis=1)*pwx)*pwx for pwx in pw],axis=0)
            for ci,cx in enumerate([self.c0,self.c1]):
                self.cxs[pwi,2,2,ci] = np.sum([np.sum(np.sum(self.tm*cx,axis=1)*pwx)*pwx for pwx in pw],axis=0)
        # for ABC (system) purview
        for mx in [0,1]:
            # elementary mechanisms A/B/C = 0/1
            self.cxs[6,mx,2,2] = np.sum(self.tm * [self.a0,self.a1][mx],axis=1)
            self.cxs[6,2,mx,2] = np.sum(self.tm * [self.b0,self.b1][mx],axis=1)
            self.cxs[6,2,2,mx] = np.sum(self.tm * [self.c0,self.c1][mx],axis=1)
        # higher order mechanisms
        for pwi in range(7):
            # second order
            for mx,my in [[0,0],[0,1],[1,0],[1,1]]:
                # for AB, BC, AC
                self.cxs[pwi,mx,my,2] = self.cxs[pwi,mx,2,2] * self.cxs[pwi,2,my,2]
                self.cxs[pwi,2,mx,my] = self.cxs[pwi,2,mx,2] * self.cxs[pwi,2,2,my]
                self.cxs[pwi,mx,2,my] = self.cxs[pwi,mx,2,2] * self.cxs[pwi,2,2,my]
            # 3d order (whole ABC system)
            for mx,my,mz in [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]:
                self.cxs[pwi,mx,my,mz] = self.cxs[pwi,mx,2,2] * self.cxs[pwi,2,my,2] * self.cxs[pwi,2,2,mz]
        # unconstrained (all homogeneous)
        self.cxs[:,2,2,2] = np.ones((7,8))
        #
        # first order effects
        # for effects: ABC/AB=10 -> A/AB=10 x B/AB=10 x C/AB=10
        # matrices for effects, including virtual elements not currently constrained
        self.tma = np.sum(self.tm*self.a0,axis=1).reshape(8,1)*self.a0+np.sum(self.tm*self.a1,axis=1).reshape(8,1)*self.a1
        self.tmb = np.sum(self.tm*self.b0,axis=1).reshape(8,1)*self.b0+np.sum(self.tm*self.b1,axis=1).reshape(8,1)*self.b1
        self.tmc = np.sum(self.tm*self.c0,axis=1).reshape(8,1)*self.c0+np.sum(self.tm*self.c1,axis=1).reshape(8,1)*self.c1
        # unconstrained distributions for A,B and C
        ufa = np.sum(self.tma,axis=0)
        ufb = np.sum(self.tmb,axis=0)
        ufc = np.sum(self.tmc,axis=0)
        # for every mechanism
        for ai,ax in enumerate([self.a0,self.a1,np.ones((1,8))]):
            for bi,bx in enumerate([self.b0,self.b1,np.ones((1,8))]):
                for ci,cx in enumerate([self.c0,self.c1,np.ones((1,8))]):
                    # for the elementary purviews (A/B/C)
                    self.exs[0,ai,bi,ci] = np.sum(self.tma*ax.T*bx.T*cx.T,axis=0) * ufb * ufc
                    self.exs[1,ai,bi,ci] = ufa * np.sum(self.tmb*ax.T*bx.T*cx.T,axis=0) * ufc
                    self.exs[2,ai,bi,ci] = ufa * ufb * np.sum(self.tmc*ax.T*bx.T*cx.T,axis=0)
                    # second order purviews (AB/BC/AC)
                    self.exs[3,ai,bi,ci] = np.sum(self.tma*ax.T*bx.T*cx.T,axis=0) * np.sum(self.tmb*ax.T*bx.T*cx.T,axis=0) * ufc
                    self.exs[4,ai,bi,ci] = ufa * np.sum(self.tmb*ax.T*bx.T*cx.T,axis=0) * np.sum(self.tmc*ax.T*bx.T*cx.T,axis=0)
                    self.exs[5,ai,bi,ci] = np.sum(self.tma*ax.T*bx.T*cx.T,axis=0) * ufb * np.sum(self.tmc*ax.T*bx.T*cx.T,axis=0)
                    # third order purview (system ABC)
                    self.exs[6,ai,bi,ci] = np.sum(self.tma*ax.T*bx.T*cx.T,axis=0) * np.sum(self.tmb*ax.T*bx.T*cx.T,axis=0) * np.sum(self.tmc*ax.T*bx.T*cx.T,axis=0)
        import pdb; pdb.set_trace()
        # uc future
        self.ucf = np.sum(self.tma,axis=0)*np.sum(self.tmb,axis=0)*np.sum(self.tmc,axis=0)
        self.ucf /= np.sum(self.ucf)


    def info(self):
        # ax,bx,cx = self.state
        self.ci,self.ei = np.zeros((7,7)),np.zeros((7,7))
        # uc past & future
        ucp = np.ones(8)/8
        ucfs = self.exs[:,2,2,2]/np.sum(self.exs[:,2,2,2],axis=1).reshape(7,1)
        import pdb; pdb.set_trace()
        # for all mechanisms (A,B,C,AB,BC,AC,ABC) (rows)
        for u,[va,vb,vc] in enumerate(self.mx_sts):
            # for all purviews (columns)
            # cause & effect repertoires
            crs = self.cxs[:,va,vb,vc]/np.sum(self.cxs[:,va,vb,vc],axis=1).reshape(7,1)
            ers = self.exs[:,va,vb,vc]/np.sum(self.exs[:,va,vb,vc],axis=1).reshape(7,1)
            # earth mover's distances (cause reps, uc pasts)
            self.ci[u] = [emd(cr,ucp,self.dm) for cr in crs]
            self.ei[u] = [emd(er,ucf,self.dm) for er,ucf in zip(ers,ucfs)]
        # cause-effect intrinsic info
        self.cei = np.minimum(self.ci,self.ei)
        # MIP info
        self.cmip = np.zeros((7,7))
        self.emip = np.zeros((7,7))
        # quick way
        # for causes, mechanisms are commutative and purviews independent
        # for effects is the opposite
        self.cmip[:3,:3] = self.ci[:3,:3]
        self.emip[:3,:3] = self.ei[:3,:3]
        # second order mechanisms (for causes) and purviews (for effects)
        for u,[ux,uy] in enumerate([[0,1],[1,2],[0,2]]):
            # max mip causes
            self.cmip[:3,u+3] = (self.ci[:3,u+3] - np.maximum(self.ci[:3,ux],self.ci[:3,uy])).clip(0)
            self.cmip[u+3,:3] = (self.ci[u+3,:3] - np.maximum(self.ci[ux,:3],self.ci[uy,:3])).clip(0)
            # max mip effects
            self.emip[:3,u+3] = (self.ei[:3,u+3] - np.maximum(self.ei[:3,ux],self.ei[:3,uy])).clip(0)
            self.emip[u+3,:3] = (self.ei[u+3,:3] - np.maximum(self.ei[ux,:3],self.ei[uy,:3])).clip(0)
        # AB,BC,AC
        # for u,[ux,uy] in enumerate([[0,1],[1,2],[0,2]]):
        #     # second order mechanisms, second order purviews
        #     self.cmip[3:6,u+3] = (self.ci[3:6,u+3]-np.maximum(self.ci[3:6,ux],self.ci[3:6,uy])).clip(0)
        #     self.emip[3:6,u+3] = (self.ei[3:6,u+3]-np.maximum(self.ei[3:6,ux],self.ei[3:6,uy])).clip(0)
        # for u,[ux,uy] in enumerate([[0,1],[1,2],[0,2]]):
        #     self.cmip[u+3,3:] *= np.where(self.ci[u+3,3:]*self.ci[ux,3:]*self.ci[uy,3:]>0,1,0)
        #     self.emip[u+3,3:] *= np.where(self.ei[u+3,3:]*self.ei[ux,3:]*self.ei[uy,3:]>0,1,0)
        # third order: ABC system
        # for simplicity
        self.ci = self.ci.round(2)
        self.ei = self.ei.round(2)
        self.cei = self.cei.round(2)
        self.cmip = self.cmip.round(2)
        self.emip = self.emip.round(2)
        # synergy: simple sum from elements
        self.syn_ci = np.sum(self.ci[:3,6])
        self.syn_ei = np.sum(self.ei[:3,6])
        self.syn_cei = np.sum(self.cei[:3,6])
        # enactive version

    def step(self):
        # state transitions
        ai,bi,ci = self.state
        ax = bi or ci
        bx = ai and ci
        cx = ai ^ bi
        self.state = np.array(ax,bx,cx)
        # update mechanisms sts (A,B,C,AB,BC,AC,ABC)
        self.mu_sts = [[ax,2,2],[2,bx,2],[2,2,cx],[ax,bx,2],[2,bx,cx],[ax,2,cx],[ax,bx,cx]]

    def make_at_abc(self):
        # A:OR, B:AND, C:XOR
        self.at_ek_tm = np.zeros((8,3,8))
        self.at_tm = np.zeros((8,8))
        for dk in [0,1]:
            for sti in range(8):
                ai,bi,ci = self.i2b[sti]
                ax = bi or ci or dk
                bx = ai and ci
                cx = ai ^ bi
                stx = self.b2i[(ax,bx,cx)]
                self.at_ek_tm[sti,dk,stx] += 1
                self.at_tm[sti,stx] += 1
        # dists, stx given sti (effects)
        self.ixa = np.zeros((2,8))
        self.ixb = np.zeros((2,8))
        self.ixc = np.zeros((2,8))
        self.ix = np.zeros((2,2,2,8))
        # matrices for effects, including virtual elements not currently constrained
        self.at_tma = np.sum(self.at_tm*self.a0,axis=1).reshape(8,1)*self.a0+np.sum(self.at_tm*self.a1,axis=1).reshape(8,1)*self.a1
        self.at_tmb = np.sum(self.at_tm*self.b0,axis=1).reshape(8,1)*self.b0+np.sum(self.at_tm*self.b1,axis=1).reshape(8,1)*self.b1
        self.at_tmc = np.sum(self.at_tm*self.c0,axis=1).reshape(8,1)*self.c0+np.sum(self.at_tm*self.c1,axis=1).reshape(8,1)*self.c1
        # distributions, causes, sti given stx
        self.xia = np.zeros((2,8))
        self.xib = np.zeros((2,8))
        self.xic = np.zeros((2,8))
        self.xi = np.zeros((2,2,2,8))
        # for ABC (system) purview only
        # sti -> stx
        for mx in [0,1]:
            ax = [self.a0,self.a1][mx]
            bx = [self.b0,self.b1][mx]
            cx = [self.c0,self.c1][mx]
            self.ixa[mx] = np.sum(self.at_tma*ax.T*bx.T*cx.T,axis=0)
            self.ixb[mx] = np.sum(self.at_tmb*ax.T*bx.T*cx.T,axis=0)
            self.ixc[mx] = np.sum(self.at_tmc*ax.T*bx.T*cx.T,axis=0)
        # sti <- stx
        for mx in [0,1]:
            # elementary mechanisms A/B/C = 0/1
            self.xia[mx] = np.sum(self.at_tm * [self.a0,self.a1][mx],axis=1)
            self.xib[mx] = np.sum(self.at_tm * [self.b0,self.b1][mx],axis=1)
            self.xic[mx] = np.sum(self.at_tm * [self.c0,self.c1][mx],axis=1)
        # system
        for ax in [0,1]:
            for bx in [0,1]:
                for cx in [0,1]:
                    axa = [self.a0,self.a1][ax]
                    bxb = [self.b0,self.b1][bx]
                    cxc = [self.c0,self.c1][cx]
                    self.ix[ax,bx,cx] = np.sum(self.at_tma*axa.T*bxb.T*cxc.T,axis=0)*np.sum(self.at_tmb*axa.T*bxb.T*cxc.T,axis=0)*np.sum(self.at_tmc*axa.T*bxb.T*cxc.T,axis=0)
                    self.xi[ax,bx,cx] = self.xia[ax]*self.xib[bx]*self.xic[cx]
        # information (distance to actual events)
        self.ixa_info = np.zeros((2,8))
        self.ixb_info = np.zeros((2,8))
        self.ixc_info = np.zeros((2,8))
        self.xia_info = np.zeros((2,8))
        self.xib_info = np.zeros((2,8))
        self.xic_info = np.zeros((2,8))
        # elements
        for mi in [0,1]:
            #ai,bi,ci = self.i2b[sti]
            for st in range(8):
                stu = np.zeros(8)
                stu[st] = 1
                # sti -> ? || sti -> stx
                self.ixa_info[mi,st] = emd(self.ixa[mi]/np.sum(self.ixa[mi]),stu,self.dm)
                self.ixb_info[mi,st] = emd(self.ixb[mi]/np.sum(self.ixb[mi]),stu,self.dm)
                self.ixc_info[mi,st] = emd(self.ixc[mi]/np.sum(self.ixc[mi]),stu,self.dm)
                # ? <- stx || sti <- stx
                self.xia_info[mi,st] = emd(self.xia[mi]/np.sum(self.xia[mi]),stu,self.dm)
                self.xib_info[mi,st] = emd(self.xib[mi]/np.sum(self.xib[mi]),stu,self.dm)
                self.xic_info[mi,st] = emd(self.xic[mi]/np.sum(self.xic[mi]),stu,self.dm)
        # system
        self.ix_info = np.zeros((8,8))
        self.xi_info = np.zeros((8,8))
        self.at_info = np.zeros((8,8))
        for stu in range(8):
            au,bu,cu = self.i2b[stu]
            for st in range(8):
                stf = np.zeros(8)
                stf[st] = 1
                ix = self.ix[au,bu,cu]/max(1,np.sum(self.ix[au,bu,cu]))
                self.ix_info[stu,st] = emd(ix,stf,self.dm)
                xi = self.xi[au,bu,cu]/max(1,np.sum(self.xi[au,bu,cu]))
                self.xi_info[stu,st] = emd(xi,stf,self.dm)
        # round
        self.ix_info = self.ix_info.round(2)
        self.xi_info = self.xi_info.round(2)
        # min between both
        # self.at_info[stu,st] = np.minimum(self.ix_info,self.xi_info)
















#
