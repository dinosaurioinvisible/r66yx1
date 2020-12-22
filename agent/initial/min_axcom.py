
import numpy as np
from shapely.geometry import Point

class Com:
    def __init__(self, genotype, x,y):
        self.com_n = genotype.com_n
        self.com_range = genotype.com_range
        self.com_theta = genotype.com_theta
        self.com_lt = genotype.com_lt
        self.com_ut = genotype.com_ut
        self.slow, self.non, self.shigh = [i for i in genotype.signals]
        self.com_out = np.array([np.random.choice(signals) for i in range(self.com_n)])
        self.define_com_area(x,y)

    def define_com_area(self, x,y):
        # assuming 360 for now
        self.x = x
        self.y = y
        loc = Point(self.x,self.y)
        self.com_area = loc.buffer(self.com_range)

    def update_in(self, xagents):
        # default (non)
        cget = np.array([self.non]*self.com_n)
        min_dist = self.com_range
        for xa in xagents:
            if self.com_area.intersects(xa.xcom.com_area):
                dist = Point(self.x,self.y).distance(Point(xa.x,xa.y))
                if dist < min_dist:
                    cget = xa.com_out
        com_info = np.where(cget==self.slow,-1, np.where(self.shigh,1,0))
        return com_info

    def update_out(self, com):
        # numeric vals to signals
        self.com_out = np.where(com<self.com_lt,self.slow, np.where(com>self.com_ut,self.shigh, self.snon))






#
