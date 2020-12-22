
from collections import defaultdict
import numpy as np
from glx_glider import Glider


class Evaluation:
    def __init__(self,time=25,wsize=100,supervised=True):
        self.time=time
        self.wsize=wsize
        self.sup=supervised

    '''eval fx: cell by cell, no glider'''
    def gt_eval(self,gt, return_states=False):
        # fts for each cell, states from glider
        tx_cells_fts=[]
        tx_cells_states=[]
        for cfg in range(1,5):
            # if supervised
            if self.sup:
                self.sup_tx=self.supervised_transitions(cfg)
            # new world and glider for trial
            self.world=defaultdict(int)
            self.glider=Glider(gt,config=cfg)
            # run trial
            cell_fts,cell_states=self.trial()
            tx_cells_fts.append(cell_fts)
            tx_cells_states.append(cell_states)
        # weighted fitnesses for each cell
        cells_wfts=[]
        for cell_ft in np.asarray(tx_cells_fts).T:
            wfi = np.sum([(i+1)*fi for i,fi in enumerate(sorted(cell_ft,reverse=True))])
            ci_wft = (2/(len(cell_ft)*(len(cell_ft)+1))) * wfi
            cells_wfts.append(ci_wft)
        # states for analysis or animation
        if return_states:
            return cells_wfts, tx_cells_states
        return cells_wfts

    '''just the continuous update of the glider cell elements'''
    def trial(self):
        ft = np.zeros((25))
        cell_states = [self.glider.state]
        for ti in range(self.time):
            # update world and glider
            self.update_world()
            self.glider.update(self.world)
            cell_states.append(self.glider.state)
            # evaluate (most simple posible (for now at least))
            ft_t = self.ftfx(ti,cell_states[-2])
            ft += ft_t
            # interrupt trial in case
            if np.sum(ft_t)==0:
                return ft,cell_states
        return ft,cell_states

    '''rules for world update, just reset for current empty world'''
    def update_world(self):
        self.world=defaultdict(int)

    '''ft according to the 4 canonical glider configs (only xy)'''
    def ftfx(self,ti,gl_st0):
        # if not supervised
        if not self.sup:
            # +1 for every cell alive
            ft_t = self.glider.state[:,5]
            return ft_t
        # current transition
        ct = ti%4
        sup_xy = gl_st0[:,1:3]+self.sup_tx[ct]
        # discard the dead cells
        glider_xy = self.glider.state[:,1:3]*np.asarray([self.glider.state[:,5]]).T
        # compare expected vs glider
        sup_gl_xy = np.sum(sup_xy-glider_xy,axis=1)
        sup_ft_t = np.where(sup_gl_xy==0,1,0)
        return sup_ft_t

    '''states to train the cells to behave as a glider (only xy)'''
    def supervised_transitions(self,cfg):
        # "correct" glider transitions: 0:g12, 2:g23, 3:g34, 4:g41
        gl_ti=[(0,-1),(0,0),(1,0),(0,0)]
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
        sorted_transitions = [gl_ti[cfg_i] for cfg_i in cfg_sts]
        return sorted_transitions











#
