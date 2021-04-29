
import numpy as np

class Genotype:
    def __init__(self,wx_in=None,wx_out=None,thresholds=None,ga=None,gb=None):
        self.r = 5
        self.f_range = 5
        self.max_speed = 5
        self.wheels_sep = 6
        self.irs_range = 25
        # same number of sensor for side
        self.irs_dos = [-90,-60,-30,30,60,90]
        self.irs_angle = 30
        self.irs_colors = False
        self.n_input = len(self.irs_dos)+1
        self.n_hidden = 10
        self.n_output = 4
        # evolving parameters
        self.wx_in = wx_in
        if not self.wx_in:
            self.wx_in = np.random.uniform(-1,1,size=(self.n_hidden,self.n_input))
        self.wx_out = wx_out
        if not self.wx_out:
            self.wx_out = np.random.uniform(-1,1,size=(self.n_output,self.n_hidden))
        self.thresholds = thresholds
        if not self.thresholds:
            self.thresholds = np.random.uniform(-0.5,0.5,size=(1,self.n_hidden))
        # ga if fires, gb otherwise
        self.ga = ga
        if not self.ga:
            self.ga = np.random.uniform(0,0.1,self.n_hidden)
        self.gb = gb
        if not self.gb:
            self.gb = np.random.uniform(0.2,0.5,self.n_hidden)

    def mutate(self,mut_rate):
        # wx_in
        vx = np.random.uniform(-0.1,0.1,size=self.wx_in.shape)
        rx = np.random.uniform(0,1,size=self.wx_in.shape)
        rx = np.where(rx<mut_rate,1,0)
        self.wx_in = np.where(self.wx_in*rx!=0,self.wx_in+vx,self.wx_in)
        # wx_out
        vx = np.random.uniform(-0.1,0.1,size=self.wx_out.shape)
        rx = np.random.uniform(0,1,size=self.wx_out.shape)
        rx = np.where(rx<mut_rate,1,0)
        self.wx_out = np.where(self.wx_out*rx!=0,self.wx_out+vx,self.wx_out)
        # thresholds
        vx = np.random.uniform(-0.1,0.1,size=self.thresholds.shape)
        rx = np.random.uniform(0,1,size=self.thresholds.shape)
        rx = np.where(rx<mut_rate,1,0)
        self.thresholds = np.where(self.thresholds*rx!=0,self.thresholds+vx,self.thresholds)
        # ga
        vx = np.random.uniform(-0.025,0.025,size=self.ga.shape)
        rx = np.random.uniform(0,1,size=self.ga.shape)
        rx = np.where(rx<mut_rate,1,0)
        self.ga = np.where(self.ga*rx!=0,self.ga+vx,self.ga)
        self.ga = np.where(self.ga<0,0,self.ga)
        self.ga = np.where(self.ga>0.4,0.4,self.ga)
        # gb
        vx = np.random.uniform(-0.1,0.1,size=self.gb.shape)
        rx = np.random.uniform(0,1,size=self.gb.shape)
        rx = np.where(rx<mut_rate,1,0)
        self.gb = np.where(self.gb*rx!=0,self.gb+vx,self.gb)
        self.gb = np.where(self.gb<0.1,0.1,self.gb)
        self.gb = np.where(self.gb>0.8,0.8,self.gb)

    def combine(self,gt2,mut_rate):
        if np.random.choice([True,False]):
            self.wx_in = gt2.wx_in
        if np.random.choice([True,False]):
            self.wx_out = gt2.wx_out
        if np.random.choice([True,False]):
            self.thresholds = gt2.thresholds
        if np.random.choice([True,False]):
            self.ga = gt2.ga
        if np.random.choice([True,False]):
            self.gb = gt2.gb
        if np.random.choice([True,False]):
            self.mutate(mut_rate)









####
