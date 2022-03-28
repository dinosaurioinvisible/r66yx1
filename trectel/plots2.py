
import numpy as np
import matplotlib.pyplot as plt
from information_fxs import SystemInfo
from helper_fxs import *


def info_plots(ring,simdata):
    # envs & system sts for every timestep
    env_ijs = ddxlocs(16)
    env = np.zeros(len(simdata)).astype(int)
    sts = np.zeros(len(simdata)).astype(int)
    for t,sd in enumerate(simdata):
        env[t] = arr2int(np.asarray([sd[0][ei,ej] for ei,ej in env_ijs]))
        sts[t] = arr2int(sd[1])
    # array containers
    iit_ci = np.zeros((6,len(simdata)))
    iit_ei = np.zeros((6,len(simdata)))
    iit_cei = np.zeros((6,len(simdata)))
    atm_ci = np.zeros((6,len(simdata)))
    atm_ei = np.zeros((6,len(simdata)))
    atm_cei = np.zeros((6,len(simdata)))
    ix_info = np.zeros((6,len(simdata)))
    # info class
    y = SystemInfo(ring.gt)
    # information
    for t,(ek,st) in enumerate(zip(env,sts)):
        # iit
        cis,eis,ceis = y.iit_info(ek,st)
        iit_ci[:,t] = cis
        iit_ei[:,t] = eis
        iit_cei[:,t] = ceis
        # atm
        acis,aeis,aceis = y.atm_info(st)
        atm_ci[:,t] = cis
        atm_ei[:,t] = eis
        atm_cei[:,t] = ceis
        # ix
        ix_info[:,t] = y.ix_info(st)
    return iit_ci,iit_ei,iit_cei,atm_ci,atm_ei,atm_cei,ix_info
