
import numpy as np

class Net():
    def __init__(self, genotype):
        # parameters
        self.n_input = genotype.n_input
        self.n_hidden = genotype.n_hidden
        self.n_output = genotype.n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        # network states
        self.net_state = np.zeros(self.n_net)
        self.net_out = np.zeros(self.n_output)
        # init network if there isn't one
        self.network = genotype.network
        # output units
        self.motor_n = genotype.motor_n
        self.com_n = genotype.com_n

    # input -> rest of the network
    def update(self, env_info):
        # adjust env_info and update sensors
        env_in = np.concatenate((env_info, np.zeros((self.n_hidden+self.n_output))))
        # assuming parallel like sensory feeding
        sns_out = np.zeros((self.n_net))
        for i in range(0,self.n_input):
            nx = self.network[i]
            # rec activation (if any) + env input
            nx_in = self.net_state[i]+env_in[i]
            nx_out = nx.transfer_fx(nx_in)
            wnx_out = nx_out*nx.wx
            # assuming independent continuity of signals
            self.net_state[i] = 0
            sns_out += wnx_out
        # update: sensors -> network
        self.net_state += sns_out
        # update the remaing units
        hms_out = np.zeros((self.n_net))
        for i in range(self.n_input,self.n_net):
            nx = self.network[i]
            # (latent act + net act), no env act
            nx_in = self.net_state[i]
            nx_out = nx.transfer_fx(nx_in)
            wnx_out = nx_out*nx.wx
            # update network values
            # like in ctrnn (state = -state+inputs)
            # in this case = 0 because there is no dt yet
            self.net_state[i] = 0
            hms_out += wnx_out
            # motor output
            if i >= self.n_input+self.n_hidden:
                no = self.n_net-i-1
                self.net_out[no] = nx_out
        self.net_state += hms_out
        # output
        if self.motor_n == 2:
            ml = self.net_out[0]
            mr = self.net_out[1]
            com = self.net_out[2:2+self.com_n]
        else:
            ml = self.net_out[0]-self.net_out[1]
            mr = self.net_out[2]-self.net_out[3]
            com = self.net_out[4:4+self.com_n]
        return ml, mr, com

class Neuron():
    def __init__(self, lt=-1, ut=1, wx=[]):
        self.lt = lt
        self.ut = ut
        self.wx = wx

    def transfer_fx(self, nx_in):
        # self act + input + noise
        noise = np.random.uniform(-0.1,0.1)
        x = nx_in + noise
        # transfer_fx
        # -1, 1 or ratio: x/(not -1/1 domain)
        nx_out = np.where(x<self.lt,-1, np.where(x>self.ut,1, (x-self.lt)/(self.ut-self.lt)))
        return nx_out







#
