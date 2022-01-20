
import numpy as np
from helper_fxs import *

'''Ring made of elements with their own genotype'''
class RingSystem:
    def __init__(self,gt,i,j,st0):
        # system
        self.i, self.j = i,j
        self.core_st = 1
        self.st = st0
        # elements
        self.elements = []
        ex_locs = ring_locs(i=i,j=j,r=len(gt))
        ex_sts = int2arr(st0,arr_len=len(gt))
        for ex_gt,[exi,exj],ex_st in zip(gt,ex_locs,ex_sts):
            ex = Element(ex_gt,exi,exj,ex_st)
            self.elements.append(ex)

    def update(self,world):
        # update elements
        for ex in self.elements:
            domain = np.sum(world[ex.i-1:ex.i+2,ex.j-1:ex.j+2])
            ex.update(domain)
        # update world
        for ex in self.elements:
            world[ex.i,ex.j] = ex.st
        # update core
        core_domain = np.sum(world[self.i-1:self.i+2,self.j-1:self.j+2]) - 1
        self.core_st = 1 if 2 <= core_domain <= 3 else 0
        # update state
        world[self.i,self.j] = self.core_st
        self.st = arr2int(np.asarray([ex.st for ex in self.elements]))

class Element:
    def __init__(self,gt,i,j,st0):
        self.i,self.j = i,j
        self.st = st0
        self.gt = gt

    def update(self,domain):
        domain_in = arr2int(domain)
        self.st = self.gt[domain_in]

def system_gt(elements=4):
    # system gt is made of different gts for every element
    # 0/1 for every 3x3 st+env
    gt = np.random.randint(0,2,size=(elements,512))
    return gt
