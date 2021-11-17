
import numpy as np

class Ring:
    def __init__(self,i,j,gt,st0=0):
        self.i,self.j = i,j
        self.locs = ring_locs(i=i,j=j,r=2,hollow=True)
        self.gt = gt
        self.state = st0

class Trectel:
    def __init__(self,x1,y1,gt1,gt2,st01,st02):
        self.x1,self.y1 = x1,y1
        self.x2 = x1+3
        self.y2 = y1
        self.st1 = st01
        self.st2 = st02


class Rhombus:
    def __init__(self,i,j,gt,st0):
        self.i,self.j = i,j
        self.gt = gt
        self.pos = rhombus_locs(r=2)
        self.state = st0

    def update(self,domain):
