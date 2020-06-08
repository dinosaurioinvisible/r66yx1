
import numpy as np
from shapely.geometry import Point
# abcdex = -0.99, -0.66, -0.33, 0.33, 0.66, 0.99

class Com:
    def __init__(self, genotype):
        self.com_range = genotype.com_range
        self.com_len = genotype.com_len
        self.signals = [i for i in genotype.signals]
        self.com_vals = [-0.99,-0.66,-0.33,0,0.33,0.66,0.99]
        self.define_com_dict()

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
        self.com_info = [0]* self.com_len
        min_dist = 100
        for xa in xagents:
            if self.com_area.intersects(xa.com_area):
                dist = Point(self.x,self.y).distance(xa.x,xa.y)
                if dist < min_dist:
                    self.com_info = xa.com_out
        return self.com_info

    def output_signal(self, com):
        com_out = []
        for c in com:
            if c < -0.66:
                cx = "a"
            elif c < -0.33:
                cx = "b"
            elif c < 0:
                cx = "c"
            elif c == 0:
                cx = "x"
            elif c > 0.66:
                cx = "f"
            elif c > 0.33:
                cx = "e"
            elif c > 0:
                cx = "d"
            com_out.append(cx)
        return com_out










#
