
import numpy as np
import matplotlib.pyplot as plt
from information_fxs import SystemInfo
from simulations import ring_gol_trial
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
    fig.supylabel('Information')
    fig.supxlabel('Time')
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
    fig.supylabel('Information')
    fig.supxlabel('Time')
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


#
