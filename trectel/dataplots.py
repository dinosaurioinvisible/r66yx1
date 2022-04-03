
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



NP.SUM(TM*C0 * (A0.T+A1.T + B0.T + B1.t),AXIS=1)

# IIT's ABC system
# step by step to avoid any possible confusion
class ABC:
    def __init__(self):
        # int<>bin dicts
        self.i2b = int2bin(3)
        self.b2i = bin2int(3)
        # distance matrix
        self.emd_tm = dist_matrix(dim=8,cost=1)
        # tx matrices (system & elementary mechanisms)
        self.tm,self.tma,self.tmb,self.tmc = [np.zeros((8,8))]*4
        # indices where elem mechanisms = 1/0
        self.a0,self.a1,self.b0,self.b1,self.c0,self.c1 = [None]*6
        # (pws, v=1/0, dist), 8 purviews: [],a,b,c,ab,ac,bc,abc
        self.cxa,self.cxb,self.cxc = [np.zeros((8,2,8))]*3
        self.exa,self.exb,self.exc = [np.zeros((8,2,8))]*3


        # cause/effect repertoires, elements
        self.ca,self.cb,self.cc = np.zeros((2,8)),np.zeros((2,8)),np.zeros((2,8))
        self.ea,self.eb,self.ec = np.zeros((2,8)),np.zeros((2,8)),np.zeros((2,8))
        # unconstrained dists
        self.ucp,self.ucf = np.ones(8)/8,np.ones(8)
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
        a1 = np.array([[0,1,0,1,0,1,0,1]])
        a0 = np.absolute(a1-1)
        b1 = np.array([[0,0,1,1,0,0,1,1]])
        b0 = np.absolute(b1-1)
        c1 = np.array([[0,0,0,0,1,1,1,1]])
        c0 = np.absolute(c1-1)
        # elem. mechanisms tx matrices
        self.tma = np.sum(self.tm*self.a0,axis=1).reshape(8,1)*a0+np.sum(self.tm*self.a1,axis=1).reshape(8,1)*a1
        self.tmb = np.sum(self.tm*self.b0,axis=1).reshape(8,1)*b0+np.sum(self.tm*self.b1,axis=1).reshape(8,1)*b1
        self.tmc = np.sum(self.tm*self.c0,axis=1).reshape(8,1)*c0+np.sum(self.tm*self.c1,axis=1).reshape(8,1)*c1
        # higher order mechanisms indices
        self.ab00 = np.array([[1,0,0,0,1,0,0,0]])
        self.ab10,self.ab01,self.ab11 = [np.roll(self.ab00,i) for i in range(1,4)]
        self.ac00 = np.array([[0,1,0,1,0,0,0,0]])
        self.ac10,self.ac01,self.ac11 = [np.roll(self.ac00,i) for i in [1,4,5]]
        self.bc00 = np.array([[1,1,0,0,0,0,0,0]])
        self.bc10,self.bc01,self.bc11 = [np.roll(self.bc00,i) for i in range(2,8,2)]
        # cause/effect counts (for repertoires)
        # purviews : working matrices; mechanisms : index arrays for 1/0 sts
        self.a_a0 = np.sum(self.tma*a0*a0.T)*a0 + np.sum(self.tma*a0*a1.T)*a1
        self.a_a1 = np.sum(self.tma*a1*a0.T)*a0 + np.sum(self.tma*a1*a1.T)*a1
        self.b_a0 = np.sum(self.tma*a0*b0.T)*b0 + np.sum(self.tma*a0*b1.T)*b1
        self.b_a1 = np.sum(self.tma*a1*b0.T)*b0 + np.sum(self.tma*a1*b1.T)*b1
        self.c_a0 = np.sum(self.tma*a0*c0.T)*c0 + np.sum(self.tma*a0*c1.T)*c1
        self.c_a1 = np.sum(self.tma*a1*c0.T)*c0 + np.sum(self.tma*a1*c1.T)*c1
        self.ab_a0 = np.sum(self.tma*self.tmb*a0*ab00.T)*a0 + np.sum(self.tma*a0*a1.T)*a1




        # PURVIEWS ARE MADE BY COMBINING MATRICES
        # MECHANISMS OPERATE OVER PURVIEWS
        # for elementary mechanisms: a/b/c, 0/1, pdist
        cx_a,cx_b,cx_c,cx_ab,cx_ac,cx_bc,cx_abc = cxs = [np.zeros((3,2,8))]*7
        ex_a,ex_b,ex_c,ex_ab,ex_ac,ex_bc,ex_abc = exs = [np.zeros((3,2,8))]*7
        # purviews: 0:A,1:B,2:C,3:AB,4:AC,5:BC,6:ABC
        cx_a_a0 = np.sum(self.tma*a0*a0.T)*a0 + np.sum(self.tma*a0*a1.T)*a1
        cx_a_a1 = np.sum(self.tma*a1*a0.T)*a0 + np.sum(self.tma*a1*a1.T)*a1
        cx_a_b0 = np.sum(self.tma*b0,axis=1)
        cx_a_b1 = np.sum(self.tma*b1,axis=1)
        cx_a_c0 = np.sum(self.tma*c0,axis=1)
        cx_a_c1 = np.sum(self.tma*c1,axis=1)
        cx_b_a0 = np.sum(self.tmb,a0,axis=1)
        cx_b_a1 = np.sum(self.tmb,a1,axis=1)
        cx_b_b0 = np.sum(self.tmb*b0*b0.T)*b0 + np.sum(self.tmb*b0*b1.T)*b1
        cx_b_b1 = np.sum(self.tmb*b1*b0.T)*b0 + np.sum(self.tmb*b1*b1.T)*b1
        cx_b_c0 = np.sum(self.tmb,c0,axis=1)
        cx_b_c1 = np.sum(self.tmb,c1,axis=1)
        cx_c_a0 = np.sum(self.tmc*a0,axis=1)
        cx_c_a1 = np.sum(self.tmc*a1,axis=1)
        cx_c_b0 = np.sum(self.tmc*b0,axis=1)
        cx_c_b1 = np.sum(self.tmc*b1,axis=1)
        cx_c_c0 = np.sum(self.tmc*c0*c0.T)*c0 + np.sum(self.tmb*c0*c1.T)*c1
        cx_c_c1 = np.sum(self.tmc*c1*c0.T)*c0 + np.sum(self.tmb*c1*c1.T)*c1
        cx_ab_a0 = np.sum(self.tma*self.tmb*a0,axis=1)
        cx_ab_a1 = np.sum(self.tma*self.tmb*a1,axis=1)
        cx_ab_b0 = np.sum(self.tma*self.tmb*b0,axis=1)
        cx_ab_b1 = np.sum(self.tma*self.tmb*b1,axis=1)
        cx_ab_c0 = np.sum(self.tma*self.tmb*self.tmc*c0,axis=1)
        cx_ab_c1 = np.sum(self.tma*self.tmb*self.tmc*c1,axis=1)
        cx_ac_a0 = np.sum(self.tma*self.tmc*a0,axis=1)
        cx_ac_a1 = np.sum(self.tma*self.tmc*a1,axis=1)

        cx_ac_b0 = np.sum(self.tma*self.tmc*b0,axis=1)
        cx_ac_b1 = np.sum(self.tma*self.tmc*b1,axis=1)

        cx_ac_c0 = np.sum(self.tma*self.tmc*c0,axis=1)
        cx_ac_c1 = np.sum(self.tma*self.tmc*c1,axis=1)



        for cx in cxs:
            # A = 0
            cx[0,0] =
            #
                cx[u,v0] = np.sum(self.tma*self.tmb*self.tmc*v0,axis=1)
                cx[u,v1] = np.sum(self.tma*self.tmb*self.tmc*v1,axis=1)

        cx_ab_c0 = np.sum(self.tma*self.tmb*self.tmc*c0,axis=1)


        cxs = [self.cxa,self.cxb,self.cxc]
        exs = [self.exa,self.exb,self.exc]
        tms = [self.tma,self.tmb,self.tmc]
        mvs = [[self.a0,self.a1],[self.b0,self.b1],[self.c0,self.c1]]
        # purviews: 0:[],1:A,2:B,3:C,4:AB,5:AC,6:BC,7:ABC
        for cx,tm,[v0,v1] in zip(cxs,exs,tms,mvs):
            # empty set: []

            # elementary purviews A|A=1/0, B|A=1/0, C|A=1/0, etc
            # causes
            # ap_a/b/c=0/1
            cx[1,0] = np.sum(tm*v0*a0.T)*a0 + np.sum(tm*v0*a1.T)*a1
            cx[1,1] = np.sum(tm*v1*a0.T)*a0 + np.sum(tm*v1*a1.T)*a1
            # bp_a/b/c=0/1
            cx[2,0] = np.sum(tm*v0*b0.T)*b0 + np.sum(tm*v0*b1.T)*b1
            cx[2,1] = np.sum(tm*v1*b0.T)*b0 + np.sum(tm*v1*b1.T)*b1
            # cp_a/b/c=0/1
            cx[3,0] = np.sum(tm*v0*c0.T)*c0 + np.sum(tm*v0*c1.T)*c1
            cx[3,1] = np.sum(tm*v1*c0.T)*c0 + np.sum(tm*v1*c1.T)*c1
            # effects
            # af_a/b/c=0/1
            ex[1,0] = np.sum(tm*v0.T*a0)*a0 + np.sum(tm*v0.T*a1)*a1
            ex[1,1] = np.sum(tm*v1.T*a0)*a0 + np.sum(tm*v1.T*a1)*a1
            # bf_a/b/c=0/1
            ex[2,0] = np.sum(tm*v0.T*b0)*b0 + np.sum(tm*v0.T*b1)*b1
            ex[2,1] = np.sum(tm*v1.T*b0)*b0 + np.sum(tm*v1.T*b1)*b1
            # cf_a/b/c=0/1
            ex[3,0] = np.sum(tm*v0.T*c0)*c0 + np.sum(tm*v0.T*c1)*c1
            ex[3,1] = np.sum(tm*v1.T*c0)*c0 + np.sum(tm*v1.T*c1)*c1
            # higher order purviews, elementary mechanisms
            # causes
            # abp_a/b/c=0/1
            ex[4,0] = np.sum((tm*v0)*(a0.T+a1.T+b0.T+b1.T),axis=1)
            ex[4,1] = np.sum((tm*v1)*(a0.T+a1.T+b0.T+b1.T),axis=1)
            # acp_a/b/c=0/1
            cx[5,0] = np.sum(tm*v0*ac00.T)*ac00 + np.sum(tm*v0*ac10.T)*ac10 + np.sum(tm*v0*ac01.T)*ac01 + np.sum(tm*v0*ac11.T)*ac11
            cx[5,1] = np.sum(tm*v1*ac00.T)*ac00 + np.sum(tm*v1*ac10.T)*ac10 + np.sum(tm*v1*ac01.T)*ac01 + np.sum(tm*v1*ac11.T)*ac11
            # bcp_a/b/c=0/1
            cx[6,0] = np.sum(tm*v0*bc00.T)*bc00 + np.sum(tm*v0*bc10.T)*bc10 + np.sum(tm*v0*bc01.T)*bc01 + np.sum(tm*v0*bc11.T)*bc11
            cx[6,1] = np.sum(tm*v1*bc00.T)*bc00 + np.sum(tm*v1*bc10.T)*bc10 + np.sum(tm*v1*bc01.T)*bc01 + np.sum(tm*v1*bc11.T)*bc11
            # effects


            acf_abc = tma*a1.T*tmc*c0.T*b0.T
            # AB,AC,BC purviews
            cx[4,0] = np.sum(tm*v0*self.ab00.T)*self.ab00 + np.sum(tm*v0*self.ab10.T)*self.ab10 + np.sum(tm*v0*self.ab01.T)*self.ab01 + np.sum(tm*v0*self.ab11.T)*self.ab11
            cx[4,1] = np.sum(tm*v1*self.ab00.T)*self.ab00 + np.sum(tm*v1*self.ab10.T)*self.ab10 + np.sum(tm*v1*self.ab01.T)*self.ab01 + np.sum(tm*v1*self.ab11.T)*self.ab11
            cx[5,0] = np.sum(tm*v0*self.ac00.T)*self.ac00 + np.sum(tm*v0*self.ac10.T)*self.ac10 + np.sum(tm*v0*self.ac01.T)*self.ac01 + np.sum(tm*v0*self.ac11.T)*self.ac11
            cx[5,1] = np.sum(tm*v1*self.ac00.T)*self.ac00 + np.sum(tm*v1*self.ac10.T)*self.ac10 + np.sum(tm*v1*self.ac01.T)*self.ac01 + np.sum(tm*v1*self.ac11.T)*self.ac11
            cx[6,0] = np.sum(tm*v0*self.bc00.T)*self.bc00 + np.sum(tm*v0*self.bc10.T)*self.bc10 + np.sum(tm*v0*self.bc01.T)*self.bc01 + np.sum(tm*v0*self.bc11.T)*self.bc11
            cx[6,1] = np.sum(tm*v1*self.bc00.T)*self.bc00 + np.sum(tm*v1*self.bc10.T)*self.bc10 + np.sum(tm*v1*self.bc01.T)*self.bc01 + np.sum(tm*v1*self.bc11.T)*self.bc11
            # ABC
            cx[7,0] = np.sum(tm*v0,axis=1)
            cx[7,1] = np.sum(tm*v1,axis=1)
            # effects
            ex[7,0] = np.sum(tm*v0.T,axis=0)
            ex[7,1] = np.sum(tm*v1.T,axis=0)



        # cause/effect counts for reps
        for u,[cu,eu] in enumerate(zip([self.ca,self.cb,self.cc],[self.ea,self.eb,self.ec])):
            tmu = np.sum(self.tm*v0[u],axis=1).reshape(8,1)*v0[u]+np.sum(self.tm*v1[u],axis=1).reshape(8,1)*v1[u]
            cu[0] = np.sum(tmu*v0[u],axis=1)#/np.sum(tmu*v0[u])
            cu[1] = np.sum(tmu*v1[u],axis=1)#/np.sum(tmu*v1[u])
            eu[0] = np.sum(tmu*v0[u].reshape(8,1),axis=0)#/np.sum(tmu.T*v0[u])
            eu[1] = np.sum(tmu*v1[u].reshape(8,1),axis=0)#/np.sum(tmu.T*v1[u])
            # unconstrained distributions
            self.ucf *= np.sum(tmu,axis=0)/8

    ac_abc = np.sum(self.tm*self.ac01.T)*self.ac01*self.ucfb
    ac_abc /= np.sum(ac_abc)
    # elementary info: purview ABC=100
    # self.cx = self.ca[1]*self.cb[0]*self.cc[0]/np.sum(self.ca[1]*self.cb[0]*self.cc[0])
    # purview: set of elements over which cause/effect reps of mu are calculated
    #c_a1 = np.sum(tma*a1*c0.reshape(8,1))*c0+np.sum(tma*a1*c1.reshape(8,1))*c1
    #b_b0 = np.sum(tmb*b0*c0.reshape(8,1))*c0+np.sum(tmb*b0*c1.reshape(8,1))*c1
    #ab00 = np.array([1,0,0,0,1,0,0,0])
    #ab10,ab01,ab11 = [np.roll(ab00,i) for i in range(1,4)]
    #ab_c0 = np.sum(tmc*c0*ab00.T)*ab00+np.sum(tmc*c0*ab10.T)*ab10+np.sum(tmc*c0*ab01.T)*ab01+np.sum(tmc*c0*ab11.T)*ab11

    def info(self,st=[1,0,0]):
        # st int and arr
        st,st_int = (self.i2b[st],st) if type(st)==int else (st,self.b2i[tuple(st)])
        # cause & effect info
        cis = [round(emd(cu[u],self.ucp,self.emd_tm),2) for u,cu in zip(st,[self.ca,self.cb,self.cc])]
        eis = [round(emd(eu[u],self.ucf,self.emd_tm),2) for u,eu in zip(st,[self.ea,self.eb,self.ec])]
        # system cause & effect
        cx = self.tm[:,st_int]/max(1,np.sum(self.tm[:,st_int]))
        ex = self.tm[st_int]/max(1,np.sum(self.tm[st_int]))
        cis.append(round(emd(cx,self.ucp,self.emd_tm),2))
        eis.append(round(emd(ex,self.ucf,self.emd_tm),2))
        # cause-effect info
        ceis = [min(ci,ei) for ci,ei in zip(cis,eis)]
        return cis,eis,ceis


























#
