
import numpy as np
import matplotlib.pyplot as plt
from information_fxs import SystemInfo
from simulations import ring_gol_trial
from pyemd import emd
from helper_fxs import *


def random_info(tt=100,wsize=25,wth0=0.2):
    rdm_gt = np.random.random((4,512)).round().astype(int)
    rdm_ring,rdm_ft,rdm_simdata = ring_gol_trial(rdm_gt,timesteps=tt,world_size=wsize,world_th0=wth0,save_data=True)
    print('\nrandom gt fitness: {}'.format(rdm_ft))
    rdm_info_object,rdm_info = info_plots(rdm_ring,rdm_ft,rdm_simdata)
    return rdm_info_object,rdm_info

def info_plots(ring,ft,simdata,info_object=None):
    # envs & system sts for every timestep
    env_ijs = ddxlocs(16)
    env = np.zeros(len(simdata)).astype(int)
    sts = np.zeros(len(simdata)).astype(int)
    for t,sd in enumerate(simdata):
        env[t] = arr2int(np.asarray([sd[0][ei,ej] for ei,ej in env_ijs]))
        sts[t] = arr2int(sd[1])
    # array containers
    iit_ci = np.zeros((7,len(simdata)))
    iit_ei = np.zeros((7,len(simdata)))
    iit_cei = np.zeros((7,len(simdata)))
    atm_ci = np.zeros((7,len(simdata)))
    atm_ei = np.zeros((7,len(simdata)))
    atm_cei = np.zeros((7,len(simdata)))
    ix_info = np.zeros((7,len(simdata)))
    # info object
    y = info_object if info_object else SystemInfo(ring.gt)
    # information
    for t,(ek,st) in enumerate(zip(env,sts)):
        # iit
        cis,eis,ceis = y.iit_info(ek,st)
        iit_ci[:,t] = cis+[np.sum(cis[:-1])]
        iit_ei[:,t] = eis+[np.sum(eis[:-1])]
        iit_cei[:,t] = ceis+[np.sum(ceis[:-1])]
        # atm
        acis,aeis,aceis = y.atm_info(st)
        atm_ci[:,t] = acis+[np.sum(acis[:-1])]
        atm_ei[:,t] = aeis+[np.sum(aeis[:-1])]
        atm_cei[:,t] = aceis+[np.sum(aceis[:-1])]
        # ix
        ix = y.ix_info(st)
        ix_info[:,t] = ix+[np.sum(ix[:-1])]
    # plots IIT
    fig,axs = plt.subplots(3,sharex=True,sharey=True)
    fig.suptitle('IIT intrinsic information (ft={})'.format(ft))
    axs[0].plot(iit_ci.T)
    axs[1].plot(iit_ei.T)
    axs[2].plot(iit_cei.T,label=[u for u in 'abcdeXS'])
    axs[0].set_ylabel('cause')
    axs[1].set_ylabel('effect')
    axs[2].set_ylabel('cause-effect')
    # depends on python/plt version
    try:
        fig.supylabel('Information')
        fig.supxlabel('Time')
    except:
        pass
    handles,labels = axs[2].get_legend_handles_labels()
    fig.legend(handles,labels,loc='center right')
    plt.show()
    # plots ATM
    fig,axs = plt.subplots(3,sharex=True,sharey=True)
    fig.suptitle('AT intrinsic information (ft={})'.format(ft))
    axs[0].plot(atm_ci.T)
    axs[1].plot(atm_ei.T)
    axs[2].plot(atm_cei.T,label=[u for u in 'abcdeXS'])
    axs[0].set_ylabel('cause')
    axs[1].set_ylabel('effect')
    axs[2].set_ylabel('cause-effect')
    # depends on python/plt version
    try:
        fig.supylabel('Information')
        fig.supxlabel('Time')
    except:
        pass
    handles,labels = axs[2].get_legend_handles_labels()
    fig.legend(handles,labels,loc='center right')
    plt.show()
    # plots IX
    plt.plot(ix_info.T,label=[u for u in 'abcdeXS'])
    plt.legend()
    plt.title('ix intrinsic information (ft={})'.format(ft))
    plt.xlabel('Time')
    plt.ylabel('Information')
    plt.show()
    return y,[iit_ci,iit_ei,iit_cei,atm_ci,atm_ei,atm_cei,ix_info]



#NP.SUM(TM*C0 * (A0.T+A1.T + B0.T + B1.t),AXIS=1)

# IIT's ABC system
# step by step to avoid any possible confusion
class ABC:
    def __init__(self,st=100):
        # int<>bin dicts
        self.i2b = int2bin(3)
        self.b2i = bin2int(3)
        # current state
        self.state = np.array([int(i) for i in str(st)])
        # distance matrix
        self.emd_tm = dist_matrix(dim=8,cost=1)
        # tx matrix
        self.tm = np.zeros((8,8))
        # 7 purviews, A,B,C, 8 probabilities
        self.cxs,self.exs = np.zeros((7,3,3,3,8)),np.zeros((7,3,3,3,8))
        # unconstrained distributions
        self.ucp = np.ones(8)/8
        self.ucf = np.ones((7,8))
        # make matrices and repertoires
        self.make_abc()
        self.info()
        self.mip_info()


    def make_abc(self):
        # main tx matrix
        for sti in range(8):
            # A:OR, B:AND, C:XOR
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
        # mechanisms indices container array
        self.mu_ids = [[self.a0,self.a1],[self.b0,self.b1],[self.c0,self.c1],self.ab,self.bc,self.ac]
        # mechanisms sts: A/B/C current vals = 0/1/2; 2=indep. => exs[pw,2,2,2] = UC pw
        sta,stb,stc = self.state
        self.mu_sts = [[sta,2,2],[2,stb,2],[2,2,stc],[sta,stb,2],[2,stb,stc],[sta,2,stc],[sta,stb,stc]]
        # probabilities of purviews, given mechanisms
        # purviews: A=0,B=1,C=2,AB=3,BC=4,AC=5,ABC=6
        # cxs/exs[purview][A,B,C] = [p0,p1,...,p7]
        for pwe,pw in enumerate(self.mu_ids):
            # values A/B/C = 0,1,2 (2:independent)
            for va,ma in enumerate([self.a0,self.a1,np.ones(8)]):
                for vb,mb in enumerate([self.b0,self.b1,np.ones(8)]):
                    for vc,mc in enumerate([self.c0,self.c1,np.ones(8)]):
                        # ex. for causes: p(AB|AB=10) = p(AB|A=1) x p(AB|B=0)
                        self.cxs[pwe][va][vb][vc] = np.sum([np.sum(self.tm*ma*mb*mc*pwi.T)*pwi for pwi in pw],axis=0)
                        # ex. for effects: p(ABC|A=1) = p(A|A=1) x p(B|A=1) x p(C|A=1)
                        self.exs[pwe][va][vb][vc] = np.sum([np.sum(self.tm*ma.T*mb.T*mc.T*pwi)*pwi for pwi in pw],axis=0)
        # second order mechanisms
        for pw in range(3,6):
            # causes
            for va,vb in [[0,0],[1,0],[0,1],[1,1]]:
                self.cxs[pw,va,vb,2] = self.cxs[pw,va,2,2] * self.cxs[pw,2,vb,2]
            for vb,vc in [[0,0],[1,0],[0,1],[1,1]]:
                self.cxs[pw,2,vb,vc] = self.cxs[pw,2,vb,2] * self.cxs[pw,2,2,vc]
            for va,vc in [[0,0],[1,0],[0,1],[1,1]]:
                self.cxs[pw,va,2,vc] = self.cxs[pw,va,2,2] * self.cxs[pw,2,2,vc]
        # system
        for va,ma in enumerate([self.a0,self.a1,np.ones(8)]):
            for vb,mb in enumerate([self.b0,self.b1,np.ones(8)]):
                for vc,mc in enumerate([self.c0,self.c1,np.ones(8)]):
                    # causes
                    self.cxs[6][va][vb][vc] = np.sum(self.tm*ma*mb*mc,axis=1)
                    # effects
                    if 2 in [va,vb,vc]:
                        # already computed (when not all A,B & C are defined)
                        self.exs[6][va][vb][vc] = self.exs[0,va,vb,vc]*self.exs[1,va,vb,vc]*self.exs[2,va,vb,vc]
                    else:
                        # specific values for all A,B & C
                        self.exs[6][va][vb][vc] = np.sum(self.tm*ma.T*mb.T*mc.T,axis=0)
        # not necessary, but for clarity
        self.ucf = self.exs[:,2,2,2]/np.sum(self.exs[:,2,2,2],axis=1).reshape(7,1)

    def step(self):
        # state transitions
        ai,bi,ci = self.state
        ax = bi or ci
        bx = ai and ci
        cx = ai ^ bi
        self.state = np.array(ax,bx,cx)
        # update mechanisms sts (A,B,C,AB,BC,AC,ABC)
        self.mu_sts = [[ax,2,2],[2,bx,2],[2,2,cx],[ax,bx,2],[2,bx,cx],[ax,2,cx],[ax,bx,cx]]

    def info(self):
        sta,stb,stc = self.state
        self.ci,self.ei = np.zeros((7,7)),np.zeros((7,7))
        # for all mechanisms (A,B,C,AB,BC,AC,ABC) (rows)
        for u,[va,vb,vc] in enumerate(self.mu_sts):
            # for all purviews (columns)
            # cause repertoires
            crs = self.cxs[:,va,vb,vc]/np.sum(self.cxs[:,va,vb,vc],axis=1).reshape(7,1)
            # earth mover's distance (cause rep, uc rep)
            self.ci[u] = [emd(cr,self.ucp,self.emd_tm) for cr in crs]
            ers = self.exs[:,va,vb,vc]/np.sum(self.exs[:,va,vb,vc],axis=1).reshape(7,1)
            self.ei[u] = [emd(er,ucf,self.emd_tm) for er,ucf in zip(ers,self.ucf)]
        self.cei = np.minimum(self.ci,self.ei)
        self.max_cei = np.amax(self.cei)


    def mip_info(self):
        self.cmip = np.zeros((7,7))
        self.emip = np.zeros((7,7))
        # elementary mechanisms
        for mu,[ua,ub,uc] in enumerate(self.mu_sts[:3]):
            for pu in range(3):
                # a/a, a/b, etc
                cx = self.cxs[pu,ua,ub,uc]/np.sum(self.cxs[pu,ua,ub,uc])
                # A/B -> A/[] x []/B = uc past, same for all
                cx_mip = self.cxs[pu,2,2,2]/np.sum(self.cxs[pu,2,2,2])
                self.cmip[mu,pu] = emd(cx,cx_mip,self.emd_tm)
        # second order mechanisms
        for mu,[ua,ub,uc] in enumerate(self.mu_sts[:3]):
            for pu,[px,py] in enumerate([[0,1],[1,2],[0,2]]):
                # a/ab, a/bc, a/ac, etc
                cx = self.cxs[pu+3,ua,ub,uc]/np.sum(self.cxs[pu+3,ua,ub,uc])
                # a/ab -> a/a x []/b, a/b x []/a, same for all
                mps = np.asarray([[self.ci[mu,px],self.cxs[px,ua,ub,uc]],[self.ci[mu,py],self.cxs[py,ua,ub,uc]]])
                cx_mips = [mpi[1]/np.sum(mpi[1]) for mpi in mps if mpi[0]==mps[:,0].max()]
                self.cmip[mu,pu+3] = min([emd(cx,cxi,self.emd_tm) for cxi in cx_mips])
                # ab/a, ab/b, ab/c, etc (vertical, over elem 3x3)
                va,vb,vc = self.mu_sts[pu+3]
                vx = self.cxs[mu,va,vb,vc]/np.sum(self.cxs[mu,va,vb,vc])
                # ab/a -> a/a x b/[], a/[] x b/a, same for all
                xa,xb,xc = self.mu_sts[px]
                ya,yb,yc = self.mu_sts[py]
                vps = np.asarray([[self.ci[px,mu],self.cxs[mu,xa,xb,xc]],[self.ci[py,mu],self.cxs[mu,ya,yb,yc]]])
                if vps[:,0].max()>0 and self.ci[pu+3,mu]>0:
                    vx_mips = [vpi[1]/np.sum(vpi[1]) for vpi in vps if vpi[0]==vps[:,0].max()]
                    self.cmip[pu+3,mu] = min([emd(vx,vxi,self.emd_tm) for vxi in vx_mips])
                else:
                    self.cmip[pu+3,mu] = 0
        # second order from second order mechanisms
        for mu,[ua,ub,uc] in enumerate(self.mu_sts[3:6]):
            for pu,[px,py] in enumerate([[0,1],[1,2],[0,2]]):
                # ab/ab, ab/bc, ab/cd, etc
                cx = self.cxs[pu+3,ua,ub,uc]/np.sum(self.cxs[pu+3,ua,ub,uc])
                # bc/ab -> bc/a x []/b, bc/b x []/a, b/ab x c/[], c/ab x b/[], same for all
                mx,my = [[0,1],[1,2],[0,2]][mu]
                xa,xb,xc = self.mu_sts[mx]
                ya,yb,yc = self.mu_sts[my]
                mps = np.asarray([[self.ci[mx,pu+3],self.cxs[pu+3,xa,xb,xc]],[self.ci[my,pu+3],self.cxs[pu+3,ya,yb,yc]],[self.ci[mu+3,px],self.cxs[px,ua,ub,uc]],[self.ci[mu+3,py],self.cxs[py,ua,ub,uc]]])
                cx_mips = [mpi[1]/np.sum(mpi[1]) for mpi in mps if mpi[0]==mps[:,0].max()]
                self.cmip[mu+3,pu+3] = min([emd(cx,cxi,self.emd_tm) for cxi in cx_mips])
        # third order mechanisms
        for mu in range(6):
            # a/abc,b/abc,c/abc
            ua,ub,uc = self.mu_sts[mu]
            pws = [3,4,5]
            cx = self.cxs[6,ua,ub,uc]/self.cxs[6,ua,ub,uc].sum()
            mps = np.asarray([[self.cmip[mu,pwi],self.cxs[pwi,ua,ub,uc]] for pwi in pws])
            cx_mips = [mpi[1]/np.sum(mpi[1]) for mpi in mps if mpi[0]==mps[:,0].max()]
            self.cmip[mu,6] = min([emd(cx,cxi,self.emd_tm) for cxi in cx_mips])
            # vertical, on top of 6x6
            if self.ci[6,mu] > 0:
                sa,sb,sc = self.state
                vx = self.cxs[mu,sa,sb,sc]/self.cxs[mu,sa,sb,sc].sum()
                vx_mips = [self.cxs[mu,(*self.mu_sts[vi])] for vi in np.where(self.cmip[:7,mu]==self.cmip[:7,mu].max())[0]]
                self.cmip[6,mu] = min([emd(vx,vxi/vxi.sum(),self.emd_tm) for vxi in vx_mips])
            else:
                self.cmip[6,mu] = 0
        # abc/abc
        sa,sb,sc = self.state
        cx = self.cxs[6,sa,sb,sc]/np.sum(self.cxs[6,sa,sb,sc])
        px,pu = np.where(self.cmip==np.amax(self.cmip))
        vu = [self.state[i] if i==px else 2 for i in range(3)]
        va,vb,vc = vu
        cx_mip = self.cxs[pu[0],va,vb,vc]/self.cxs[pu[0],va,vb,vc].sum()
        self.cmip[6,6] = emd(cx,cx_mip,self.emd_tm)
        # quick version for effects
        self.emip[:3,:3] = self.ei[:3,:3]
        for u,[px,py] in enumerate([[0,1],[1,2],[0,2]]):
            self.emip[u+3,:3] = (self.ei[u+3,:3]-np.maximum(self.emip[px,:3],self.emip[py,:3])).clip(0)#*np.where(np.maximum(self.emip[px,:3],self.emip[py,:3])>0,1,0)
            self.emip[:3,u+3] = (self.ei[:3,u+3]-np.maximum(self.emip[:3,px],self.emip[:3,py])).clip(0)*np.where(np.maximum(self.emip[:3,px],self.emip[:3,py])>0,1,0)
            self.emip[3:6,u+3] = (self.ei[3:6,u+3]-np.maximum(self.emip[3:6,px],self.emip[3:6,py])).clip(0)*np.where(np.maximum(self.emip[3:6,px],self.emip[3:6,py])>0,1,0)
            self.emip[6,u+3] = (self.ei[6,u+3]-np.amax(self.emip[3:6,u+3]))*np.where(np.amax(self.emip[3:6,u+3])>0,1,0)
        self.emip[6,:3] = (self.ei[6,:3]-np.amax(self.emip[:,:3],axis=0)).clip(0)
        self.emip[:,6] = (self.ei[:,6]-np.amax(self.ei[:,:6],axis=1)).clip(0)
        # round for vis
        self.ci = self.ci.round(2)
        self.ei = self.ei.round(2)
        self.cei = self.cei.round(2)
        self.cmip = self.cmip.round(2)
        self.emip = self.emip.round(2)
        # max phi
























#
