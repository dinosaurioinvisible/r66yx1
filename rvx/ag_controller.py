

import numpy as np

class Controller:
    def __init__(self, genotype):
        # weights & thresholds
        self.wx_in = genotype.wx_in
        self.wx_out = genotype.wx_out
        self.thresholds = genotype.thresholds
        # decaying factors (ga if fires, gb otherwise)
        self.ga = genotype.ga
        self.gb = genotype.gb
        # network
        self.ag_info = None
        self.net_in = None
        self.net_state = np.random.uniform(0,1,size=(1,genotype.n_hidden)).T
        self.net_out = np.array([0]*genotype.n_hidden)
        self.motor_out = np.array([0,0])

    def update(self,ag_info):
        # env input
        self.ag_info = np.array([ag_info]).T
        self.net_in = np.dot(self.wx_in,self.ag_info)
        # net input = recurrent input + ag input
        self.net_state = self.net_state + self.net_in
        # transfer fx (if act > threshold)
        self.net_out = np.where(self.net_state.T>self.thresholds,1,0).T
        # decay (according to output)
        self.net_state = np.where(self.net_state.T*self.net_out.T>0,self.net_state.T*self.ga,self.net_state.T*self.gb).T
        # motor layer and output
        motor = np.dot(self.wx_out,self.net_out)
        #import pdb; pdb.set_trace()
        mx = np.where(motor>0,1,0)
        self.motor_out = np.concatenate((mx[0]-mx[1],mx[2]-mx[3]))
        #print(self.net_in.T)
        #print(self.net_out.T)
        #print(motor)
        #print(self.motor_out.T)
        return self.motor_out

    def classifier(self):
        # test elemental classification
        forward = {}
        turn_right = {}
        turn_left = {}
        back = {}
        tree = {}
        #
