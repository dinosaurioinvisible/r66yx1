
import numpy as np
from helper_fxs import *

class Blinker:
    def __init__(self):
        # transition tensor (for sts) and matrix
        self.cell_tt,self.cell_tm = txs_gol_cell()
        # blinker sts
        self.b1 = np.array([[0,1,0],[0,1,0],[0,1,0]])
        self.b2 = np.array([[0,0,0],[1,1,1],[0,0,0]])

        # info [sti <-> stx]
        self.mk_txs_info()


    def mk_txs_info(self):
        # cell i -> 0/1
        tx_i0 = np.where(tt[:,1,4]==0)[0] # (400)
        tx_i1 = np.where(tt[:,1,4]==1)[0] # (112)
        # cell 0/1 -> x
        tx_0x = np.where(tt[:,0,4]==0)[0] # (256)
        tx_1x = np.where(tt[:,0,4]==1)[0] # (256)
        # 0 -> 0 (200), 1 -> 1 (200); but these aren't actually changes
        tx_00 = np.array(list(set(tx_0x).intersection(set(tx_i0))))
        tx_11 = np.array(list(set(tx_1x).intersection(set(tx_i1))))
        # 0 -> 1 (56), 1 -> 0 (56); these'd yield the same amount of info
        tx_01 = np.array(list(set(tx_0x).intersection(set(tx_i1))))
        tx_10 = np.array(list(set(tx_1x).intersection(set(tx_i0))))
        # so for a single cell, there'd be 2 intrinsic distinctions
        # equally (minimally) informative, but different in nature
        phi_01 = 


        # b1 -> b2
        # p(sti -> stx | stx=b2) (unknown past st)
        # for cv in self.b2.flatten():







    def mk_cell_dist(self):
        #
        self.pix = np.zeros((2,2,4))
        # p(sti -> stx | sti=ci)
        # 0 -> 1, 0 -> 0
        np.where(tt[:,0,4]==0)[0]
        # 1 -> 1, 1 -> 0
        c11 = np.sum(self.tt[self.tt[:,0,4].nonzero()[0],1,4])
        c10 = 256 - c11



        #ci,cx = self.b1[4], self.b2[4]
