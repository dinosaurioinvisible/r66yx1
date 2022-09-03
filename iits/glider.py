
import numpy as np
from aux import *
from pyemd import emd

class GliderABCs:
    def __init__(self):
        # glider sts, tx matrix, cells sts, pws indx, exs matrices
        self.gx,self.tm,self.gs,self.fpws,self.ems = mkglider()
        # initial state
        self.st = self.gx[0]
        # causes and effects
        self.cxs = np.zeros((25,512))
        self.exs = np.zeros((25,512))
        self.cei = np.zeros((5,5))
        # distance matrix
        self.dm = mkdm(self.gx)
        # methods
        self.glider_base()

    # cause/effect repertoires (prob. dists)
    def glider_base(self):
        # (512x9) reps of 3x3 power set (to open pws)
        f = flat_mxrep()
        # uc past (always homogeneous)
        ucp = np.ones(16)/16
        # ucf: all outputs without input constraints
        ucs = np.sum(self.ems,axis=1)
        # remove non glider cells
        ng = np.where(np.isnan(self.st.flatten()),0,1)
        ucf = np.sum((ucs.T*ng),axis=1)
        ucf /= np.sum(ucf)
        # first order causes
        for ce in range(25):
            # cell's current value = 0/1
            cv = self.st.flatten()[ce]
            if np.isnan(cv):
                self.cxs[ce].fill(np.nan)
            else:
                # glider past cfgs that could have led to cell's cv (1x16)
                ct = np.nansum(self.tm*self.gs[ce,int(cv)],axis=1)
                # fpws: (9 cells in pw x 16 glider cfgs)
                s0 = np.sum(self.fpws[ce,0]*ct,axis=1)*self.fpws[ce,0].T
                s1 = np.sum(self.fpws[ce,1]*ct,axis=1)*self.fpws[ce,1].T
                sx = s0+s1
                # basically, convert cell count in pws
                ux = np.ascontiguousarray(np.matmul(sx,f.T).T)
                div = np.sum(ux,axis=1)
                ux = ux/np.where(div==0,1,div).reshape(512,1)
                self.cxs[ce] = np.array([emd(ui,ucp,self.dm) if np.sum(ui)>0 else 0 for ui in ux])
        # first order effects
        for ce in range(25):
            # again, current val
            cv = self.st.flatten()[ce]
            if np.isnan(cv):
                self.cxs[ce].fill(np.nan)
            else:
                # ucf only from the neighbor cells (not itself)
                # ui = np.where(self.st==0,1,self.st)*np.arange(25).reshape(5,5)
                # ui = ui[max(0,int(ce/5)-1):int(ce/5)+2,max(0,ce%5-1):ce%5+2]
                # ui = np.where(ui==ce,np.nan,ui)
                # ui = ui[~np.isnan(ui)].astype(int)
                # ?
                # effect matrix (16x16) x cells pws (9x16)
                ex = np.matmul(self.ems[ce],self.fpws[ce,int(cv)].T)
                rx = np.ascontiguousarray(np.matmul(ex,f.T).T)
                div = np.sum(rx,axis=1)
                rx = rx/np.where(div==0,1,div).reshape(512,1)
                self.exs[ce] = np.array([emd(ri,ucf,self.dm) if np.sum(ri)>0 else 0 for ri in rx])
        # cause-effect intrinsic info
        self.cei = np.nanmax(np.minimum(self.cxs,self.exs),axis=1).reshape(5,5)
        self.cei_pws = np.array([np.where(np.minimum(self.cxs,self.exs)[i]==cei.flatten()[i])[0] for i in range(25)])

        import pdb; pdb.set_trace()
        # self.pws[ce,0]














































#
