

import numpy as np

class Controller:
    def __init__(self, genotype):
        # weights & thresholds
        self.wx_in = genotype.wx_in
        self.wx_out = genotype.wx_out
        self.thresholds = genotype.thresholds
        # decaying factors (ga if fires, gb otherwise)
        self.ga = genotype.ga
        selg.gb = genotype.gb
        # hidden layer
        self.net_state = np.random.uniform(0,1,genotype.nhidden)
        self.net_out = None

    def update(self,env_info):
        # env input
        env_input = np.dot(env_info,self.wx_in)
        # net input = recurrent input + env input
        self.net_state = self.net_state + env_input
        # transfer fx (if act > threshold)
        self.net_out = np.where(self.net_state>self.thresholds,1,0)
        # decay (according to output)
        self.net_state = np.where(self.net_state*self.net_transfer>0,self.net_state*self.ga,self.net_state*self.gb)
        # motor layer and output
        motor_in = np.dot(self.net_out,self.wx_out)
        mx = np.where(motor>0,1,0)
        motor_output = (mx[0]-mx[1], mx[2]-mx[3])
        return motor_output
