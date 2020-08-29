
import numpy as np

class CTRNN:
    def __init__(self, net_size=10, wx=None, dt=0.1):
        self.net_size = net_size
        self.dt = dt
        self.taus = np.ones((net_size))
        self.biases = np.ones((net_size))
        self.gains = np.ones((net_size))
        self.wx = wx
        if not self.wx:
            self.wx = np.random.uniform(0,1,size(net_size,net_size))
        self.states = np.random.uniform(0,1,size=(net_size))
        self.outputs = np.zeros((net_size))

    def update(self, env_info):
        env_in = np.asarray(env_info)
        net_in = np.dot(self.weights,self.outputs)
        inputs = env_in+net_in
        self.states += self.dt*(1/self.taus) * (inputs-self.states)
        self.outputs = self.transfer_fx(self.states)
