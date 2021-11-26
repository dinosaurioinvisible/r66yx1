
import numpy as np
from helperfxs import *


class Ring:
    def __init__(self,gt,i=10,j=10,r=2,st0=0):
        self.gt = gt
        self.i,self.j = i,j
        self.r = r
        self.st_int = st0
        self.st_arr = int2arr(st0,arr_len=(4*r),dim=1)
        self.st_shape = int2ring(st0,r)
        self.zells = []
        init_zells()

    def init_zells(self):
        # relative allocation, initial sts and gts
        zell_locs = ring_locs(i=self.r,j=self.r,r=self.r)
        for e,zell_gt in enumerate(self.gt):
            zi,zj = zell_locs[e]
            zell_st = self.st_arr[e]
            zell = Zell(type=e,gt=zell_gt,i=zi,j=zj,st0=zell_st)
            self.zells.append(zell)

    def update(self,ring_domain):
        # reset
        self.st_arr = []
        # update each zell
        for zell in self.zells:
            zell_env = ring2int(ring_domain,zell.i,zell.j,r=1)
            zell.update(zell_env)
            self.st_arr.append(zell.state)
        # update ring
        self.st_int = arr2int(self.st_arr)
        self.st_shape = int2ring(self.st_int,self.r)


class Zell:
    def __init__(self,type,gt,i,j,st0):
        # 0-7 depending on location
        self.type = type
        # relative location within ring domain
        self.i,self.j = i,j
        # 2^4 binary array
        self.gt = int2arr(n=gt,arr_len=4,dim=1)
        # 1/0
        self.state = st0

    def update(self,env):
        # if on -> off, else search gt
        if self.state = 1:
            self.state = 0
        else:
            self.state = self.gt[env]


#
