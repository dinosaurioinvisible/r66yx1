
import numpy as np
from helper_fxs import *

'''
A 1-cell size system that floats over the GoL grid.
(The GoL updating is independent from the system).
It has 4 elements-sensors, one for each orientation.
State transitions of elements determine a system transition.
The state of the system determines its motion.
The system is supposed to float only over active GoL cells.
'''
class HoverSystem:
    def __init__(self,gt,i=None,j=None,st0=0):
        # initial loc (assuming worlds >= 15x15)
        self.i = i if i else np.random.randint(5,10)
        self.j = j if j else np.random.randint(5,10)
        # system st & activation in GoL cell(i,j)
        self.st = st0
        self.st_gol = None
        # system st > motion (-di,dj)
        self.motion = [ [0,0],[-1,0],[0,1],[-1,-1],
                        [1,0],[0,0],[1,-1],[0,-1],
                        [0,1],[-1,1],[0,0],[-1,0],
                        [0,0],[0,1],[1,0],[0,0] ]
        # elements
        exs_sts = int2arr(st0,arr_len=4)
        self.exs = [CellElement(i,gt[i],exs_sts[i]) for i in range(4)]

    def update(self,domain):
        # gol activation in cell(i,j)
        self.st_gol = domain[1][1]
        # elements
        for ex in self.exs:
            ex.update(domain.astype(int))
        # system st & loc (e0,e2:north,south ; e1,e3:west,east)
        exs_sts = np.asarray([ex.st for ex in self.exs])
        self.st = array2int(exs_sts)
        self.i += self.motion[self.st][0]
        self.j += self.motion[self.st][1]


class HoverElement:
    def __init__(self,index,gt,st0):
        self.index = index
        self.gt = gt
        self.st = st0

    def update(self,sys_domain):
        ce_env = np.rot90(sys_domain,-self.index)[0]
        ce_in = arr2int(ce_env)
        self.st = self.gt[ce_in]






#
