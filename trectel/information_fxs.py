
import numpy as np
from tqdm import tqdm
from helper_fxs import *
from pyemd import emd
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
        # transition matrix (sti,ek,stx)
        self.tm = np.zeros((self.sysr,self.envr,self.sysr))
        # transition matrix for selectivity counts
        self.atm = np.zeros((self.sysr,self.sysr))
        # selectivity sets (all ek : sti,ek -> stx)
        self.sel = defaultdict(set)
        # repertoires (0=a,1=b,2=c,3=d,4=e,5=system)
        # IIt reps: (system st, ek, mech st)
        self.crep = {}
        self.erep = {}
        self.at_crep = {}
        self.at_erep = {}
        for u in range(self.sxs):
            self.crep[u] = np.zeros((2,self.sysr))
            self.erep[u] = np.zeros((2,self.sysr))
            self.at_crep[u] = np.zeros((2,self.sysr))
            self.at_erep[u] = np.zeros((2,self.sysr))
        # 2d domain objects
        self.sys_locs = ddxlocs(r=5)
        self.sys_doms = ddxtensor(r=5)
        self.env_doms = ddxtensor(r=16)
        # system sts in which mu=1
        self.mu1 = [self.sys_doms[ui,uj,:].nonzero() for ui,uj in self.sys_locs]
        # get tx matrix and selectivity sets
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
                # transition matrix & selectivity sets
                self.tm[sti,ek,stx] = 1
                self.sel[sti,stx].add(ek)
        # at (env selective) tx matrix
        for (sti,stx),envs in self.sel.items():
            self.atm[sti,stx] = len(envs)

    # iit cause & effect reps
    def iit_reps(self,st,ek):
        # causes = iit_tm[:,ek,stx], effects = iit_tm[sti,ek,:]
        for u in range(self.sxs):
            # system sts in which mu=1
            mu1 = self.mu1[u]
            # causes
            self.crep[u][1] = np.sum(self.tm[:,ek][mu1],axis=0)
            self.crep[u][0] = np.sum(self.tm[:,ek],axis=0) - self.crep[u][1]
            # effects
            self.erep[u][1] = np.sum(self.tm[:,ek].T[mu1],axis=0)
            self.erep[u][0] = np.sum(self.tm[:,ek].T,axis=0) - self.erep[u][1]
        # system purviews
        self.crep[5] = self.tm[:,ek,st]
        self.erep[5] = self.tm[st,ek,:]
        # return for analysis
        return self.crep,self.erep

    def auto_reps(self,st):
        # cause transition matrix for mu
        for u in range(self.sxs):
            mu1 = self.mu1[u]
            self.at_crep[u][1] = np.sum(self.atm[mu1],axis=0)
            self.at_crep[u][0] = np.sum(self.atm,axis=0)-self.at_crep[u][1]
            self.at_erep[u][1] = np.sum(self.atm.T[mu1],axis=0)
            self.at_erep[u][0] = np.sum(self.atm.T[mu1],axis=0)-self.at_erep[u][1]
        self.at_crep[5] = self.atm[:,st]
        self.at_erep[5] = self.atm[st]
        return self.at_crep,self.at_erep

    # all combinations mediated by sti,ek,stx
    def selectivity_detail(self,sti,ek,stx):
        sti_sel = np.transpose(self.tm[sti,:,:].nonzero())
        env_sel = np.transpose(self.tm[:,ek,:].nonzero())
        stx_sel = np.transpose(self.tm[:,:,stx].nonzero())
        return sti_sel,env_sel,stx_sel
















#
