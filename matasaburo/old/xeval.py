
from collections import defaultdict
import numpy as np
from glider import Glider


class Evaluation:
    def __init__(self,gt,time=25,wsize=100,supervised=True):
        self.time=time
        self.wsize=wsize
        self.sup=supervised

    '''evaluate the glider behavior starting from each
    of the 4 canonical configurations'''
    def gt_eval(self,gt):
        # run trials
        data=[]
        for cfg in range(1,5):
            # for supervised trials
            if self.sup:
                self.sup_sts = self.supervised_states(cfg)
            # new world and glider
            self.world=defaultdict(int)
            self.glider=Glider(gt,config=cfg)
            ft,prog,gl_states=self.trial()
            data.append([ft,prog,gl_states])
        # average fitness
        # av_ft = sum([dtrial[0] for dtrial in data])/len(data)
        # weighted fitness
        sorted_fts = sorted([dt[0] for dt in data],reverse=True)
        wft = 2/(len(data)*(len(data)+1)) * sum([(i+1)*fi for i,fi in enumerate(sorted_fts)])
        data.insert(0,wft)
        return data

    '''just the continuous update of the glider elements
    history: space/domain conformed by the glider's cells
    fitness: number of living cells at each time step
    ft is intended to be global and simple, avoiding cells ft(?)'''
    def trial(self):
        ft=0
        prog=[]
        gl_states=[self.glider.state]
        # run trial
        for ti in range(self.time):
            # update world and glider
            self.update_world()
            self.glider.update(self.world)
            # save cells history
            gl_states.append(self.glider.state)
            # ids of living cells
            ai = np.where(self.glider.state[:,5]>0)
            prog.append(self.glider.state[ai][:,0])
            # fitness fx according to supervised/unsupervised trial
            if self.sup:
                # ft according to cells' known locations + surviving
                ft_t = self.supervised_ftfx(ti,gl_states[-2][:,1:3])
            else:
                # ft based only on number of surviving cells
                ft_t = np.sum(self.glider.state[:,5])
            # to give more importance to later states: max=418
            # ft += ft_t*(ti+1)/10
            ft += ft_t
            # in case all cells die before time
            if ft_t==0:
               return (ft,prog,gl_states)
        return (ft,prog,gl_states)

    '''rules for world change, just reset in empty world'''
    def update_world(self):
        self.world=defaultdict(int)

    '''fts according to the known glider states (only xy)'''
    def supervised_ftfx(self,ti,gl_xy0):
        ct = ti%4
        # array with the 22 expected dxy
        sup_dxy = np.array([sup_ci[ct] for sup_ci in self.sup_sts])
        # expected xy
        sup_xy = gl_xy0+sup_dxy
        # discard dead cells
        glider_xy = self.glider.state[:,1:3]*np.asarray([self.glider.state[:,5]]).T
        # compare expected vs glider
        sup_gl_xy = np.sum(sup_xy-glider_xy,axis=1)
        ft_t = np.sum(np.where(sup_gl_xy==0,1,0))
        return ft_t

    '''states to train the cells to behave as a glider (only xy)'''
    def supervised_states(self,cfg):
        sup_sts = [None]*22
        # glider cell blocks (cells with the same behavior)
        b0=[i for i in range(1,10)]
        b1=[10,11,12]
        b2=[14,16,18]
        b3=[13,15,17]
        b4=[19,20,21]
        b5=[22]
        blocks = [b0,b1,b2,b3,b4,b5]
        # "correct" glider transitions: 0:g12, 2:g23, 3:g34, 4:g41
        b0_sts=[(0,-1),(0,0),(1,0),(0,0)]
        b1_sts=[(0,-1),(1,0),(-1,0),(1,0)]
        b2_sts=[(0,1),(0,-1),(1,0),(0,-1)]
        b3_sts=[(0,0),(0,-1),(1,0),(0,0)]
        b4_sts=[(0,-1),(0,0),(0,0),(1,0)]
        b5_sts=[(0,0),(0,-1),(0,0),(1,0)]
        block_sts = [b0_sts,b1_sts,b2_sts,b3_sts,b4_sts,b5_sts]
        # according to initial cfg
        if cfg==1:
            cfg_sts = [0,1,2,3]
        elif cfg==2:
            cfg_sts = [1,2,3,0]
        elif cfg==3:
            cfg_sts = [2,3,0,1]
        elif cfg==4:
            cfg_sts = [3,0,1,2]
        # map of correct movements
        for bi,block in enumerate(blocks):
            for ci in block:
                block_st = [block_sts[bi][cfg_i] for cfg_i in cfg_sts]
                # from 1:22 to 0:21 (for array)
                sup_sts[ci-1] = block_st
        # sup_sts: list of lists (index = sorted cell correct cfg xy)
        return sup_sts



















#
