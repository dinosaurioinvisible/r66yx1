
import numpy as np

class Genotype:
    def __init__(self,wx_in=None,wx_out=None,thresholds=None,ga=0,gb=0.5):
        self.r = 5
        self.f_range = 2.5
        self.max_speed = 10
        self.wheels_sep = 6
        self.irs_range = 25
        self.irs_dos = [0] #[-90,-60,-30,30,60,90]
        self.irs_angle = 45
        self.n_input = len(self.irs_dos)
        self.n_hidden = 10
        # evolving parameters
        self.wx_in = wx_in
        if not self.wx_in:
            self.wx_in = np.random.uniform(-1,1,size=(self.n_input,self.n_hidden))
        self.wx_out = wx_out
        if not self.wx_out:
            self.wx_out = np.random.uniform(-1,1,size=(self.n_hidden,4))
        self.thresholds = thresholds
        if not self.thresholds:
            self.thresholds = np.random.uniform(0,1,size=(1,self.n_hidden))
        # ga if fires, gb otherwise
        self.ga = ga
        self.gb = gb
