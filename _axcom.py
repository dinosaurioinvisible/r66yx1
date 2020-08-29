
import numpy as np
from shapely.geometry import Point

class Com:
    def __init__(self, genotype, x, y):
        self.com_range = genotype.com_range
        self.com_len = genotype.com_len
        self.slow, self.snon, self.shigh = [i for i in genotype.signals]
        # thresholds for low/high signals
        self.com_lt = genotype.com_lt
        self.com_ut = genotype.com_ut
        self.com_out = np.array([np.random.choice(signals) for i in range(self.com_len)])
        self.define_com_area(x,y)

    def define_com_area(self, x, y):
        self.x = x
        self.y = y
        loc = Point(self.x,self.y)
        self.com_area = loc.buffer(self.com_range)

    def update_in(self, xagents):
        # convert letters to -1/0/1 input to the network
        # by default, non com_info
        cget = np.array([self.snon]* self.com_len)
        # get closest agent com_out
        min_dist = 100
        for xa in xagents:
            # if both com areas intersect
            if self.com_area.intersects(xa.xcom.com_area):
                # this is to choose the closer agent signal in case there is more than one
                dist = Point(self.x,self.y).distance(Point(xa.x,xa.y))
                if dist < min_dist:
                    cget = xa.com_out
        com_info = np.where(cget==self.slow,-1, np.where(self.shigh,1,0))
        return com_info

    def update_out(self, com):
        # convert numeric values to letters/signals
        self.com_out = np.where(com<self.com_lt,self.slow, np.where(com>self.com_ut,self.shigh,self.snon))












#
