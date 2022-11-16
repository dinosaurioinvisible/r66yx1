
import numpy as np
from aux import *
from pyemd import emd

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
        pd_01 = np.array([1,0])
        pd_10 = np.array([0,1])
        txs = [pd_01,pd_10]
        # minimal probability distribution (0.5, 0.5)
        pd_txs = np.array([len(tx_01),len(tx_10)])
        pd_txs /= np.sum(pd_txs)
        # unconstrained dist. wouldn't make sense as past/future here
        # so, tx_uc is the set of available distinctions
        tx_uc = np.array([len(tx_01),len(tx_10)])
        # phi (intrinsic info) : earth mover's distance

        phi_01 = emd(pd_01,uc)

        # b1 -> b2
        # p(sti -> stx | stx=b2) (unknown past st)
        # for cv in self.b2.flatten():











































#
