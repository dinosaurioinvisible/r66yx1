
import numpy as np
from helper_fxs import *

'''
A 1-cell size system that moves over the GoL grid.
It has 4 elements-sensors, one for each orientation.
State transitions of elements determine a system transition.
The state of the system determines its motion.
Whenever the system moves, the cell is made = 0.
The system is supposed to search for locations = 1.
The GoL updating is independent in hover mode.
'''
class RoverSystem:
    def __init__(self,gt,i=None,j=None,st0=0,hover=False):
        # initial loc (assuming worlds >= 15x15)
        self.i = i if i else np.random.randint(5,10)
        self.j = j if j else np.random.randint(5,10)
        # system st & activation in GoL cell(i,j)
        self.st = st0
        self.st_gol = None
        self.hover = hover
        # system st > motion (-di,dj)
        self.motion = [ [0,0],[-1,0],[0,1],[-1,-1],
                        [1,0],[0,0],[1,-1],[0,-1],
                        [0,1],[-1,1],[0,0],[-1,0],
                        [0,0],[0,1],[1,0],[0,0] ]
        self.xij = None
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
        di,dj = self.motion[self.st]
        # only rover mode
        if not self.hover:
            self.xij = [self.i,self.j] if (di+dj)==0 else None
        self.i += self.motion[self.st][0]
        self.j += self.motion[self.st][1]

class RoverElement:
    def __init__(self,index,gt,st0):
        self.index = index
        self.gt = gt
        self.st = st0

    def update(self,sys_domain):
        # ce_env = np.rot90(sys_domain,-self.index)[0]
        # ce_in = arr2int(ce_env)
        # self.st = self.gt[ce_in]
        ce_in = np.sum(np.rot90(sys_domain,-self.index)[0])
        self.st = 1 if ce_in > 1 else 0





#
