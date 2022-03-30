
import numpy as np
from tqdm import tqdm
from helper_fxs import *
from pyemd import emd
from copy import deepcopy
from collections import defaultdict

'''
1) IIT intrinsic information
2) autonomous homolog information search
3) ix information sti-><-stx
'''
class SystemInfo:
    def __init__(self,gt,system_cells=5,env_cells=16):
        # basic paramaters
        self.gt = gt.astype(int)
        self.sxs,self.exs = system_cells,env_cells
        self.sysr = 2**system_cells
        self.envr = 2**env_cells
        # 2d domain objects
        self.sys_locs = ddxlocs(r=self.sxs)
        self.sys_doms = ddxtensor(r=self.sxs)
        self.env_doms = ddxtensor(r=self.exs)
        # emd distance matrix & int<>bin conversions
        self.emd_matrix = dist_matrix(dim=self.sysr,cost=1)
        self.sys_i2b = int2bin(self.sxs)
        self.dom_b2i = bin2int(9)
        # iit tx matrix for the system (sti,ek,stx) and elem. mechanisms
        self.tm = np.zeros((self.sysr,self.envr,self.sysr))
        self.creps = []
        self.ereps = []
        # iit unconstrained distributions (past=uniform)
        self.ucp = np.ones(self.sysr)/self.sysr
        self.ucf = np.ones(self.sysr)
        # (autonomous) transition matrix (selectivity counts)
        self.atm = np.zeros((self.sysr,self.sysr))
        # at cause/effect reps (only mechanisms)
        self.atm_cs = np.zeros((self.sxs,2,self.sysr))
        self.atm_es = np.zeros((self.sxs,2,self.sysr))
        # at unconstrained future (past also uniform)
        self.atm_ucf = np.zeros(self.sysr)
        # run
        self.system_txs()
        self.make_iit_reps()
        self.make_atm_reps()


    '''main fx, creates the sti:ek:stx tx matrix'''
    def system_txs(self):
        # system initial states
        for sti in tqdm(range(self.sysr)):
            # elements/elementary-mechanisms initial states
            stis = [self.sys_doms[i,j,sti] for i,j in self.sys_locs]
            # environmental sts
            for ek in range(self.envr):
                # combine system & env domains
                dom = self.sys_doms[:,:,sti] + self.env_doms[:,:,ek]
                # local domains
                ds = [dom[i-1:i+2,j-1:j+2].flatten() for i,j in self.sys_locs]
                # resulting sts (genotype) & core (GoL rule)
                stxs = [self.gt[u][self.dom_b2i[tuple(du)]] for u,du in enumerate(np.delete(ds,2,0))]
                nbc = np.sum(ds[2]) - stis[2]
                cx = 1 if nbc==3 or (nbc==2 and stis[2]==1) else 0
                stxs.insert(2,cx)
                stx = arr2int(np.asarray(stxs))
                # transition matrix
                self.tm[sti,ek,stx] = 1
        # atm: tx matrix with counts for env. selective categorization
        for si in range(self.sysr):
            for sj in range(self.sysr):
                self.atm[si,sj] = self.tm[si,:,sj].nonzero()[0].shape[0]

    ''' IIT tx matrices, cause, effect, uc repertoires & info'''

    def make_iit_reps(self):
        # iit mechanisms are analyzed over the same fixed envs
        self.creps = [np.zeros((2,self.envr,self.sysr)) for _ in range(self.sxs)]
        self.ereps = [np.zeros((2,self.envr,self.sysr)) for _ in range(self.sxs)]
        vu0 = np.ones((1,1,self.sysr))
        vu1 = np.ones((1,1,self.sysr))
        # given ek and stx(mx=vx), get all possible stis
        for u,(ui,uj) in tqdm(enumerate(self.sys_locs)):
            # arrays indicating where mu=1/0
            vu1[0,0] = self.sys_doms[ui,uj,:]
            vu0[0,0] = np.absolute(vu1-1)
            # transition matrix for mu
            tmu = np.sum(self.tm*vu1,axis=2).reshape(self.sysr,self.envr,1)*vu1+np.sum(self.tm*vu0,axis=2).reshape(self.sysr,self.envr,1)*vu0
            # causes: given ek, all sti->stx where stx(mx=vx) (horizontal sums)
            self.creps[u][0,:,:] = np.sum(tmu*vu0,axis=2).T
            self.creps[u][1,:,:] = np.sum(tmu*vu1,axis=2).T
            # effects: given ek, all sti->stx where sti(mi=vi) (vertical sums)
            self.ereps[u][0,:,:] = np.sum(tmu*vu0.T,axis=0)
            self.ereps[u][1,:,:] = np.sum(tmu*vu1.T,axis=0)
            # uc future: dist of future st with uc inputs
            self.ucf *= np.sum(tmu[:,0,:],axis=0)/self.sysr

    def iit_reps(self,ek,st):
        # system st int -> binary array of sts
        stb = self.sys_i2b[st]
        # elementary cause/effect repertoires
        crs = [cru[vu,ek,:]/max(1,np.sum(cru[vu,ek,:])) for vu,cru in zip(stb,self.creps)]
        ers = [eru[vu,ek,:]/max(1,np.sum(eru[vu,ek,:])) for vu,eru in zip(stb,self.ereps)]
        # system repertoires
        crs.append(self.tm[:,ek,st]/max(1,np.sum(self.tm[:,ek,st])))
        ers.append(self.tm[st,ek,:]/max(1,np.sum(self.tm[:,ek,st])))
        return crs,ers

    def iit_info(self,ek,st):
        # repertoires
        crs,ers = self.iit_reps(ek,st)
        # cause/effect info: Dist(cause/effect reps || uc past/future)
        cis = [emd(cu,self.ucp,self.emd_matrix) for cu in crs]
        eis = [emd(eu,self.ucf,self.emd_matrix) for eu in ers]
        # cause-effect info: shared (min) ci,ei
        ceis = [min(ci,ei) for ci,ei in zip(cis,eis)]
        return cis,eis,ceis

    '''autonomous homolog functions'''

    def make_atm_reps(self):
        # autonomous like repertoires
        # elements/mechanisms (mu (0:4), mu sts (0/1), system sts(0:32))
        for u,(ui,uj) in tqdm(enumerate(self.sys_locs)):
            # system sts where st[u]=vu (1/0)
            vu1 = self.sys_doms[ui,uj,:]
            vu0 = np.absolute(vu1-1)
            # causes: all (sti,E)-> mx, for every stis
            self.atm_cs[u,0] = np.sum(self.atm*vu0,axis=1)/np.sum(self.atm*vu0)
            self.atm_cs[u,1] = np.sum(self.atm*vu1,axis=1)/np.sum(self.atm*vu1)
            # effects: all (mi,E)-> stx, for all stxs
            # atm*vus.reshape is just for clarity; atm.T*vus is the same
            self.atm_es[u,0] = np.sum(self.atm*vu0.reshape(self.sysr,1),axis=0)#/np.sum(self.atm.T*vu0)
            self.atm_es[u,1] = np.sum(self.atm*vu1.reshape(self.sysr,1),axis=0)#/np.sum(self.atm.T*vu1)
        # un inputs for future enaction
        self.atm_ucf = np.sum(self.atm,axis=0)/np.sum(self.atm)

    def atm_reps(self,st):
        # int to bin
        stb = self.sys_i2b[st]
        # at. cause/effect reps
        atm_crs = [self.atm_cs[u,stb[u]] for u in range(self.sxs)]
        atm_ers = [self.atm_es[u,stb[u]] for u in range(self.sxs)]
        # system
        atm_crs.append(self.atm[:,st]/np.sum(self.atm[:,st]))
        atm_ers.append(self.atm[st]/np.sum(self.atm[st]))
        return atm_crs,atm_ers

    def atm_info(self,st):
        # repertoires
        atm_crs,atm_ers = self.atm_reps(st)
        # cause, effect & cause-effect info
        atm_cis = [emd(cu,self.ucp,self.emd_matrix) for cu in atm_crs]
        atm_eis = [emd(eu,self.atm_ucf,self.emd_matrix) for eu in atm_ers]
        atm_ceis = [min(ci,ei) for ci,ei in zip(atm_cis,atm_eis)]
        return atm_cis,atm_eis,atm_ceis

    '''atm, intrinsic time'''

    def ix_info(self,st):
        # chiasmatic info: sti,ek -> <- ek,stx
        stb = self.sys_i2b[st]
        ix = [emd(self.atm_cs[u,stb[u]],self.atm_es[u,stb[u]],self.emd_matrix) for u in range(self.sxs)]
        cix = self.atm[:,st]/np.sum(self.atm[:,st])
        eix = self.atm[st]/np.sum(self.atm[st])
        ix.append(emd(cix,eix,self.emd_matrix))
        return ix

    '''other methods'''

    def selectivity_ix(self,sti,stx):
        return self.tm[sti,:,stx].nonzero()[0]

    def environment_ix(self,ek):
        return np.transpose(self.tm[:,ek,:].nonzero())
















#
