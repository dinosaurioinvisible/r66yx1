
from collections import defaultdict
import numpy as np
from glx_glider import Glider
import glx_animation

class Evaluation:
    def __init__(self,time=25,wsize=100,supervised=True):
        self.time=time
        self.wsize=wsize
        self.sup=supervised

    '''evaluate the glider behavior starting from each
    of the 4 canonical configurations'''
    def gt_eval(self,gt,return_states=False):
        # run trials
        glx_fts=[]
        glx_states=[]
        for cfg in range(1,5):
            # for supervised trials
            if self.sup:
                self.sup_tx = self.supervised_transitions(cfg)
            # new world and glider
            self.world=defaultdict(int)
            self.glider=Glider(gt,cfg)
            ft,glx_cfg_states=self.trial()
            glx_fts.append(ft)
            glx_states.append(glx_cfg_states)
        # weighted fitness
        sorted_fts = sorted(glx_fts,reverse=True)
        glx_wft = 2/(len(glx_fts)*(len(glx_fts)+1)) * sum([(i+1)*fi for i,fi in enumerate(sorted_fts)])
        # to debug
        # glx_animation.glx_anim(glx_states,glx_fts,gt)
        if return_states:
            return glx_wft,glx_fts,glx_states
        return glx_wft,glx_fts

    '''different version for trial'''
    # each unit has 512 possible inputs
    # each unit has 12 possible outputs (1/0, 1/0, 0/1/2/3)
    # so the mapping goes 512 to 16 (64 for each one in average)
    # if there are 25 units:
    # 25*16 = 300 combinations for outputs
    # is this 300 enough to all the necessary actions for survival?
    # the inmediate surrounding of the membrane would be 24 cells
    # the possible stimuli then, 2^24
    # but, we know that the glider can encounter objects only with 1 wall
    # so this becomes 2^7 = 128 external combinations
    # we could even find only one for all of them
    # it is necessary a elementary form of memory?
    #

    '''just the continuous update of the glider cell elements'''
    def trial(self):
        # max ft: n_cellsxtime: t=5 (so 4 transitions),cells=9: 36
        ft = 0
        glx_states = [self.glider.state]
        for ti in range(self.time):
            # update world and glider
            self.update_world()
            self.glider.update(self.world)
            glx_states.append(self.glider.state)
            # evaluate (most simple posible (for now at least))
            ft_t = self.ftfx(ti,glx_states[-2])
            ft += ft_t
            # interrupt trial in case
            if ft_t==0:
                return ft,glx_states
        return ft,glx_states

    '''rules for world update, just reset for current empty world'''
    def update_world(self):
        self.world=defaultdict(int)

    '''ft according to the 4 canonical glider configs (only xy)'''
    def ftfx(self,ti,gl_st0):
        # if not supervised
        if not self.sup:
            # +1 for every cell alive
            ft_t = np.sum(self.glider.state[:,5])
            return ft_t
        # current transition
        ct = ti%4
        # expected xy
        sup_xy = gl_st0[:,1:3]+self.sup_tx[ct]
        # discard dead cells (make them 0)
        glider_xy = self.glider.state[:,1:3]*np.asarray([self.glider.state[:,5]]).T
        # compare expected vs glider
        sup_gl_xy = np.sum(sup_xy-glider_xy,axis=1)
        ft_t = np.sum(np.where(sup_gl_xy==0,1,0))
        return ft_t

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
