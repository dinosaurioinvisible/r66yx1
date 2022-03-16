
import numpy as np
from helper_fxs import *


'''It was supposed to be a ring,
but considering the center element as part of the system
it basically becomes a blinker'''
class RingB:
    def __init__(self,gt,i,j,st0=[0,1,1,1,0]):
        self.gt = gt
        self.i,self.j = i,j
        self.locs = ring_locs(i=i,j=j,r=1,hollow=False)
        self.dom_locs = ring_locs(i=2,j=2,r=1,hollow=True)
        self.st = np.asarray(st0) if len(st0)==5 else np.random.randint(0,2,size=(5))

    def update(self,domain):
        # update outer elements
        for rx,[ri,rj] in enumerate(self.dom_locs):
            rx_dom = arr2int(domain[ri-1:ri+2,rj-1:rj+2])
            self.st[rx] = self.gt[rx][rx_dom]
        # update core
        cx = np.sum(domain[1:4,1:4]) - self.st[2]
        self.st[2] = 1 if cx==3 or (self.st[2]==1 and cx==2) else 0




'''Ring made of elements with their own genotype'''
class Ring:
    def __init__(self,gt,i,j,st0=6):
        # system
        self.i,self.j = i,j
        self.cx_st = 1
        self.st = st0
        self.domain = None
        # elements
        self.elements = []
        ex_locs = ring_locs(i=i,j=j,r=1)
        ex_sts = int2arr(st0,arr_len=len(gt))
        for ex_gt,[exi,exj],ex_st in zip(gt,ex_locs,ex_sts):
            ex = Element(ex_gt,exi,exj,ex_st)
            self.elements.append(ex)

    def update(self,world):
        # insert core st in world
        world[self.i,self.j] = self.cx_st
        # insert elements sts in world
        for ex in self.elements:
            world[ex.i,ex.j] = ex.st
        # update elements
        for ex in self.elements:
            ex_domain = world[ex.i-1:ex.i+2,ex.j-1:ex.j+2]
            ex.update(ex_domain)
        # update world
        for ex in self.elements:
            world[ex.i,ex.j] = ex.st
        # update core
        cx_nb = np.sum(world[self.i-1:self.i+2,self.j-1:self.j+2]) - self.cx_st
        self.cx_st = 1 if cx_nb==3 or (self.cx_st==1 and cx_nb==2) else 0
        world[self.i,self.j] = self.cx_st
        # update state
        self.domain = world[self.i-2:self.i+3,self.j-2:self.j+3]
        self.st = arr2int(np.asarray([ex.st for ex in self.elements]))
        # import pdb; pdb.set_trace()

    def reset(self,st0,i=None,j=None):
        # optional reallocation
        self.i = i if i else self.i
        self.j = j if j else self.j
        # reset initial states (new trial)
        ex_sts = int2arr(st0,arr_len=len(self.elements))
        for ei,sti in enumerate(ex_sts):
            self.elements[ei].st = sti

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
