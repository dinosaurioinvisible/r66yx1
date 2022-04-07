
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
    def __init__(self):
        # int<>bin dicts
        self.i2b = int2bin(3)
        self.b2i = bin2int(3)
        # current state
        self.state = np.array([1,0,0])
        # distance matrix
        self.emd_tm = dist_matrix(dim=8,cost=1)
        # tx matrix
        self.tm = np.zeros((8,8))
        # 7 purviews, A,B,C, 8 probabilities
        self.cxs,self.exs = np.zeros((7,3,3,3,8)),np.zeros((7,3,3,3,8))
        # unconstrained dists
        self.ucp = np.ones(8)/8
        self.ucf = np.ones((7,8))
        # make matrices and repertoires
        self.make_abc()

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
        # elem. mechanisms 1/0 indices
        self.a1 = np.array([[0,1,0,1,0,1,0,1]])
        self.b1 = np.array([[0,0,1,1,0,0,1,1]])
        self.c1 = np.array([[0,0,0,0,1,1,1,1]])
        self.a0,self.b0,self.c0 = [np.absolute(u1-1) for u1 in [self.a1,self.b1,self.c1]]
        # higher order mechanisms indices
        self.ab = [np.roll(self.a0*self.b0,i) for i in range(4)]
        self.ac = [np.roll(self.a0*self.c0,i) for i in [0,1,4,5]]
        self.bc = [np.roll(self.b0*self.c0,i) for i in range(0,8,2)]
        # container array
        self.mu = [[self.a0,self.a1],[self.b0,self.b1],[self.c0,self.c1],self.ab,self.ac,self.bc]
        # probabilities of purviews, given mechanisms
        # purviews: A=0,B=1,C=2,AB=3,AC=4,BC=5,ABC=6
        # A/B/C values = 0/1/2 (2=independent) => exs[pw,2,2,2] = UC pw
        # cxs/exs[purview][A,B,C] = [p0,p1,...,p7]
        for pwe,pw in enumerate(self.mu):
            # values A/B/C = 0,1,2 (2:independent)
            for va,ma in enumerate([self.a0,self.a1,np.ones(8)]):
                for vb,mb in enumerate([self.b0,self.b1,np.ones(8)]):
                    for vc,mc in enumerate([self.c0,self.c1,np.ones(8)]):
                        # for causes: p(AB|AB=10) = p(AB|A=1) x p(AB|B=0)
                        self.cxs[pwe][va][vb][vc] = np.sum([np.sum(self.tm*ma*mb*mc*pwi.T)*pwi for pwi in pw],axis=0)
                        # for effects: p(ABC|A=1) = p(A|A=1) x p(B|A=1) x p(C|A=1)
                        self.exs[pwe][va][vb][vc] = np.sum([np.sum(self.tm*ma.T*mb.T*mc.T*pwi)*pwi for pwi in pw],axis=0)
        # system ABC
        for va,ma in enumerate([self.a0,self.a1,np.ones(8)]):
            for vb,mb in enumerate([self.b0,self.b1,np.ones(8)]):
                for vc,mc in enumerate([self.c0,self.c1,np.ones(8)]):
                    # causes
                    self.cxs[6][va][vb][vc] = np.sum(self.tm*ma*mb*mc,axis=1)
                    # effects
                    if 2 in [va,vb,vc]:
                        # already computed (for some, not all, mechanisms)
                        self.exs[6][va][vb][vc] = self.exs[0,va,vb,vc]*self.exs[1,va,vb,vc]*self.exs[2,va,vb,vc]
                    else:
                        # specific values for A,B,C
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

    def info(self):
        sta,stb,stc = self.state
        self.ci,self.ei = np.zeros((7,7)),np.zeros((7,7))
        # for all mechanisms
        for u,[va,vb,vc] in enumerate([[sta,2,2],[2,stb,2],[2,2,stc],[sta,stb,2],[sta,2,stc],[2,stb,stc],[sta,stb,stc]]):
            # for all purviews
            crs = self.cxs[:,va,vb,vc]/np.sum(self.cxs[:,va,vb,vc],axis=1).reshape(7,1)
            self.ci[u] = [round(emd(cr,self.ucp,self.emd_tm),2) for cr in crs]
            ers = self.exs[:,va,vb,vc]/np.sum(self.exs[:,va,vb,vc],axis=1).reshape(7,1)
            self.ei[u] = [round(emd(er,ucf,self.emd_tm),2) for er,ucf in zip(ers,self.ucf)]
        self.cei = np.minimum(self.ci,self.ei)
        self.max_cei = np.amax(self.cei)

    def mip(self):
        va,vb,vc = self.state
        cx_sys = self.cxs[6,va,vb,vc]
        cx_sys_mip = ?























#
