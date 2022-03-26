
import numpy as np
from tqdm import tqdm
from helper_fxs import *
from pyemd import emd
from copy import deepcopy
from collections import defaultdict

''' repertoires:
This fx makes:
(1) A selectivity repertoire (dict):
sel(i,x) = all envs ek : (sti=i,ek) -> stx=x
sel[sti,stx] = {ek0,ek1,...,ekn}
(2) An autonomous transition matrix:
atm = all (sti,sel(sti,stx)) -> stx
autonomous cause rep = atm cols
atm[:,x] = all (sti,sel(sti,x)) -> stx=x
autonomous effect rep = atm rows
atm[i] = all (sti=i,sel(i,stx)) -> stx
(3) atm for single elements/mechanisms (me)
implicit in atm, but made for speed:
cause rep: sum of all atm[:,stx] where stx(me)=mx
effect rep: sum of all atm[sti] where sti(me)=mi
IIT cause & effect reps can be obtained by:
cause: atm[:,x] where ek in sel[sti,stx=x]
effect: atmx[i] where ek in sel[sti=i,stx]
same goes for elemental mechanisms
'''
class SystemInfo:
    def __init__(self,gt,system_cells=5,env_cells=16):
        self.gt = gt.astype(int)
        self.sxs,self.exs = system_cells,env_cells
        self.sysr = 2**system_cells
        self.envr = 2**env_cells
        # 2d domain objects
        self.sys_locs = ddxlocs(r=self.sxs)
        self.sys_doms = ddxtensor(r=self.sxs)
        self.env_doms = ddxtensor(r=self.exs)
        # emd distance matrix
        self.emd_matrix = dist_matrix(dim=self.sysr,cost=1)
        # system sts in which mechanisms=1
        # self.m1 = [self.sys_doms[ui,uj,:].nonzero()[0] for ui,uj in self.sys_locs]
        # iit tx matrix for the system (sti,ek,stx) and elem. mechanisms
        self.tm = np.zeros((self.sysr,self.envr,self.sysr))
        self.tms = []
        # iit unconstrained distributions (past=uniform)
        self.ucp = np.ones(self.sysr)/self.sysr
        self.ucf_ek = np.ones(self.sysr)
        self.ucf_gt = np.ones(self.sysr)
        # (autonomous) transition matrix (selectivity counts)
        self.atm = np.zeros((self.sysr,self.sysr))
        # at cause/effect reps (only mechanisms)
        self.atm_cs = np.zeros((self.sxs,2,self.sysr))
        self.atm_es = np.zeros((self.sxs,2,self.sysr))
        # at unconstrained future (past also uniform)
        self.atm_ucf = np.zeros(self.sysr)
        # get transition matrices
        self.system_txs()

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
                stxs = [self.gt[u][arr2int(du)] for u,du in enumerate(np.delete(ds,2,0))]
                nbc = np.sum(ds[2]) - stis[2]
                cx = 1 if nbc==3 or (nbc==2 and stis[2]==1) else 0
                stxs.insert(2,cx)
                stx = arr2int(np.asarray(stxs))
                # transition matrix
                self.tm[sti,ek,stx] = 1

    def auto_tm(self):
        # atm: tx matrix with counts for env. selective categorization
        for si in range(self.sysr):
            for sj in range(self.sysr):
                self.atm[si,sj] = self.tm[si,:,sj].nonzero()[0].shape[0]

    def iit_tms(self):
        # iit mechanisms are analyzed over same fixed envs
        self.tms = [deepcopy(self.tm) for _ in range(self.sxs)]
        for u,(ui,uj) in enumerate(self.sys_locs):
            # vu1,vu0: system sts where mu_st=1 & 0 respectively
            vu1 = self.sys_doms[ui,uj,:]
            vu0 = np.absolute(vu1-1)
            # convert every (sti,ek)->stx into (sti,ek) -> stx(mx=vx)
            # it iterates through stis (instead of envs) just for speed
            for si in range(self.sysr):
                # if mx=1 => all stxs(mx=1)=1 & stxs(mx=0)=0; if mx=0 viceversa
                # sti,ek -> stx is unique, but for -> stx(mx) has many options (all mx=1/0)
                self.tms[u][si,:,:] = np.sum(self.tm[si,:,:]*vu1,axis=1).reshape(self.envr,1)*np.full((self.envr,self.sysr),vu1)+np.sum(self.tm[si,:,:]*vu0,axis=1).reshape(self.envr,1)*np.full((self.envr,self.sysr),vu0)

    def iit_reps(self,st,ek):
        # TODO purview: system only for now
        # iit cause and effect repertoires (+1 for system dists)
        creps = np.zeros((self.sxs+1,self.sysr))
        ereps = np.zeros((self.sxs+1,self.sysr))
        # for every elementary mechanism
        for u,(ui,uj) in enumerate(self.sys_locs):
            # system states in which the mu==vu
            vus = np.where(self.sys_doms[ui,uj,:]==st[u],1,0)
            # given ek, sums of all sti->stx : stx(mx=vx); sti,ek -> mx
            cmu = np.sum(self.tms[u][:,ek,:]*vus,axis=1)
            # given ek, sums of all sti(mi=vi)->stx; mi,ek -> stx
            emu = np.sum(self.tms[u][:,ek,:]*vus.reshape(self.sysr,1),axis=0)
            # counts to dists
            creps[u] = cmu/np.sum(cmu)
            ereps[u] = emu/np.sum(emu)
        # for the whole system
        stu = arr2int(st)
        creps[self.sxs] = self.tm[:,ek,stu]/max(1,np.sum(self.tm[:,ek,stu]))
        ereps[self.sxs] = self.tm[stu,ek,:]/max(1,np.sum(self.tm[stu,ek,:]))
        return creps,ereps

    def iit_ucf_fixed_ek(self,ek=0):
        # future dist. of sts with unconstrained inputs
        # (in iit 2014 is obtained for ek=0)
        for tmu in self.tms:
            # mechanisms acting independently (no causal globality)
            self.ucf_ek *= np.sum(tmu[:,ek,:],axis=0)/self.sysr

    def iit_ucf_gt(self):
        # uc future dist. of sts from gt (independent mechs.)
        for u,(ui,uj) in enumerate(self.sys_locs):
            # mu = 1/0
            vu1 = self.sys_doms[ui,uj,:]
            vu0 = np.absolute(vu1-1)
            # mapping gt(mu=1/0) -> stx (uc. by system causal structure)
            ucgt = np.ones((self.sysr,self.sysr))
            gtu1 = self.gt[u].nonzero()[0]
            gtu0 = len(gt[u])-gtu1
            # probabilities
            self.ucf_gt *= np.sum(ucgt*vu1*gtu1+ucgt*vu0*gtu0,axis=0)/(len(self.gt[u])*self.sysr)

    def auto_reps(self):
        # autonomous like repertoires (calculated once and stored)
        # elements/mechanisms (mu (0:4), mu sts (0/1), system sts(0:32))
        for u,(ui,uj) in enumerate(self.sys_locs):
            # system sts where st[u]=vu (1/0)
            vu1 = self.sys_doms[ui,uj,:]
            vu0 = np.absolute(vu1-1)
            # causes: all (sti,E)-> mx, for every stis
            self.atm_cs[u,0] = np.sum(self.atm*vu0,axis=1)/np.sum(self.atm*vu0)
            self.atm_cs[u,1] = np.sum(self.atm*vu1,axis=1)/np.sum(self.atm*vu1)
            # effects: all (mi,E)-> stx, for all stxs
            # atm*vus.reshape is just for clarity; atm.T*vus is the same
            self.atm_es[u,0] = np.sum(self.atm*vu0.reshape(self.sysr,1),axis=0)/np.sum(self.atm.T*vu0)
            self.atm_es[u,1] = np.sum(self.atm*vu1.reshape(self.sysr,1),axis=0)/np.sum(self.atm.T*vu1)

    def at_uc_future(self):
        # un inputs for future enaction
        self.at_ucf = np.sum(self.atm,axis=0)/np.sum(self.atm)

    def atm_creps(self,st):
        # input: system st = [1/0,...,1/0]
        return [self.atm_cs[u,st[u]] for u in range(self.sxs)]

    def atm_ereps(self,st):
        return [self.atm_es[u,st[u]] for u in range(self.sxs)]

    def at_system_crep(self,st):
        # very straight forward for atm
        return self.atm[:,st]/np.sum(self.atm[:,st])

    def at_system_erep(self,st):
        return self.atm[st]/np.sum(self.atm[st])

    def iit_info(self,st,ek):
        creps,ereps = self.iit_reps(st,ek)
        cis = [emd(crmu,self.ucp,self.emd_matrix) for crmu in creps]
        eis_ek = [emd(ermu,self.ucf_ek,self.emd_matrix) for ermu in ereps]
        eis_gt = [emd(ermu,self.ucf_gt,self.emd_matrix) for ermu in ereps]
        ceis_ek = [min(ci,ei) for ci,ei in zip(cis,eis_ek)]
        ceis_gt = [min(ci,ei) for ci,ei in zip(cis,eis_gt)]
        return [creps,ereps,cis,eis_ek,eis_gt,ceis_ek,ceis_gt]

    def at_info(self,st):
        atm_crs = self.atm_creps(st)+[self.at_system_crep(st)]
        atm_ers = self.atm_ereps(st)+[self.at_system_erep(st)]
        cis = [emd(cu,self.ucp,self.emd_matrix) for cu in atm_crs]
        eis = [emd(eu,self.at_ucf,self.emd_matrix) for eu in atm_ers]
        ceis = [min(ci,ei) for ci,ei in zip(cis,eis)]
        return [atm_crs,atm_ers,cis,eis,ceis]

    def selectivity_ix(self,sti,stx):
        return self.tm[sti,:,stx].nonzero()[0]

    def environment_ix(self,ek):
        return np.transpose(self.tm[:,ek,:].nonzero())
















#
