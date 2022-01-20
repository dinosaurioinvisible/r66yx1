
import numpy as np
from helperfxs import *


class Ring:
    def __init__(self,gt,i,j,st0):
        self.gt = gt
        self.i,self.j = i,j
        self.st = st0
        self.ring_cells = ring_locs(i,j,r=2)
        self.ring_env = ring_locs(i,j,r=3)
        self.st_hist = [st0]

    def update(self,world):
        env = []
        for re in self.ring_env:
            env.append(world[re.i,re.j])
        env_in = arr2int(np.asarray(env))
        self.st = self.gt[env_in]
        self.st_hist.append(self.st)

class xRing:
    def __init__(self,gt,i,j,st0):
        # centroid loc and state (0:255)
        self.i,self.j = i,j
        self.st = st0
        # initialize elements
        self.elements = []
        st_arr = int2arr(st0,len(gt))
        locs = ring_locs()
        for ei in range(len(gt)):
            ex = Element(index=ei,gt=gt[ei],i=locs[ei][0],j=locs[ei][1],st=st_arr[ei])
            self.elements.append(ex)
        # data
        self.st_hist = [st0]

    def update(self,world):
        # update elements
        for ex in self.elements:
            env = world[ex.i-1:ex.i+2:ex.j-1:ex.j+2]
            ex.update(env)
            st_arr.append(ex.st)
        # update ring state and save
        self.st = arr2int(np.asarray([ex.st for ex in self.elements]))
        self.st_hist.append(self.st_int)

class Element:
    def __init__(self,index,gt,i,j,st):
        self.index = index
        self.gt = gt
        self.i,self.j = i,j
        self.st = st

    def update(self,env):
        env_in = arr2int(env)
        self.st = self.gt[env]













#
