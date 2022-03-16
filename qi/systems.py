
import numpy as np
from helper_fxs import *



'''A ring surrounding a 3x3 space
in this case environment is inside the system'''
class ContainerRing:
    def __init__(self,gt,i=3,j=3,exs=8,st0=[]):
        # gt = nxm matrix, n=elements, m=responses
        self.gt = gt
        self.i,self.j = i,j
        # disconnected (4) or full ring (8)
        edges = True if exs==4 else False
        self.exs_ij = ring_locs(i=i,j=j,r=2,hollow=True,only_edges=edges)
        self.st = np.asarray(st0) if len(st0)==exs else np.random.randint(0,2,size=(exs))

    def update(self,world):
        for ex,[ei,ej] in enumerate(self.exs_ij):
            # sum to int pos in gt => other sts=(0:7)+env=(0/1) => (0:8)
            ex_in = min(np.sum(world[ei-1:ei+2,ej-1:ej+2])-world[ei,ej],3)
            # retreive response from gt
            self.st[ex] = self.gt[ex][ex_in]





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


# if self.edges:
    # binary to int pos in gt => r1_out = gt[r1][int(ek,r2,r3,r4)]
    # ex_net = np.delete(self.st,ex)
    # ek = 1 if np.sum(world[ei-1:ei+2,ej-1:ej+2])-world[ei,ej]>0 else 0
    # ex_in = arr2int(np.append(ek,ex_net))
# else:
# st_copy = list(self.st)



#
