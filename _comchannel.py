
import numpy as np
from shapely.geometry import Point
# abc x def = -0.99, -0.66, -0.33, 0, 0.33, 0.66, 0.99

class Com:
    def __init__(self, genotype, x, y):
        self.com_range = genotype.com_range
        self.com_len = genotype.com_len
        self.signals = [i for i in genotype.signals]
        self.com_vals = [-1,0,1]
        self.define_com_dict()
        self.define_com_area(x,y)

    def define_com_dict(self):
        self.com_dict = {}
        for i in range(len(self.signals)):
            self.com_dict[self.signals[i]] = self.com_vals[i]

    def initial_out(self):
        out = []
        while len(out) < self.com_len:
            out.append(self.signals[np.random.randint(len(self.signals))])
        return out

    def define_com_area(self, x, y):
        self.x = x
        self.y = y
        loc = Point(self.x,self.y)
        self.com_area = loc.buffer(self.com_range)

    def update_in(self, xagents):
        com_get = ["x"]* self.com_len
        min_dist = 100
        for xa in xagents:
            # if the other agente is alive
            if xa.e > 0:
                # if both com areas intersect
                if self.com_area.intersects(xa.comchannel.com_area):
                    # this is to choose the closer agent signal in case there is more than one
                    dist = Point(self.x,self.y).distance(Point(xa.x,xa.y))
                    if dist < min_dist:
                        com_get = xa.com_out
        self.com_info = [self.com_dict[ci] for ci in com_get]
        return self.com_info

    def output_signal(self, com):
        com_out = []
        for c in com:
            if c < -0.33:
                cx = "a"
            elif c > 0.33:
                cx = "b"
            else:
                cx = "x"
            com_out.append(cx)
        return com_out










#
