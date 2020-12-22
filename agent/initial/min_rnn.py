
import numpy as np

class RNN:
    def __init__(self, genotype):
        # dimensions
        self.n_input = genotype.n_input
        self.n_hidden = genotype.n_hidden
        self.n_output = genotype.n_output
        self.n_net = genotype.n_net
        # weights
        self.W = genotype.W
        # threshold and noise values
        self.ut = genotype.ut
        self.lt = genotype.lt
        self.nn_noise = genotype.nn_noise
        # internal states (empty state for t=0)
        self.rec_states = np.zeros((self.n_net,1))
        # optional units for communication and attention
        self.com_n = genotype.com_n

    # layer by layer recurrency implementation
    def update(self, x):
        # for backwards internal activation
        retro_activation = np.zeros((self.n_net,1))

        # input layer (Ix)
        # sensory input + previous recurrent states
        x = np.array([x]).T
        rx = x + self.rec_states[:self.n_input]
        # node fx
        x_in = self.neuron_fx(rx)
        # propagation
        # NOTE: potentially fully connected so n_input -> n_net
        # W: (n_net,n_input) • x_in: (n_input,1) = ix: (n_net,1)
        ix = np.dot(self.W[0:self.n_net,0:self.n_input], x_in)
        # save backwards activations for next timestep
        retro_ix = ix[:self.n_input].copy()
        retro_ix.resize((self.n_net,1))
        retro_activation += retro_ix

        # hidden layer (Us)
        # rs: activ from input + rec activ from hidden
        sx = ix[self.n_input:self.n_input+self.n_hidden]
        rs = sx + self.rec_states[self.n_input:self.n_input+self.n_hidden]
        # node fx
        s_in = self.neuron_fx(rs)
        # propagation
        # W: (n_net,n_hidden) • h_in: (n_hidden,1) = ux: (n_net,1)
        us = np.dot(self.W[0:self.n_net,self.n_input:self.n_input+self.n_hidden], s_in)
        # backward states
        retro_us = us[:self.n_input+self.n_hidden].copy()
        retro_us.resize((self.n_net,1))
        retro_activation += retro_us

        # output layer (Vo)
        # ro: activ from input + hidden + rec activ from output
        ox = ix[self.n_input+self.n_hidden:]
        os = us[self.n_input+self.n_hidden:]
        ro = ox + os + self.rec_states[self.n_input+self.n_hidden:]
        # node fx
        out = self.neuron_fx(ro)
        # propagation (in this case output, and potentially backwards)
        # W: (n_net,n_out) • out: (n_out,1) = retro_o: (n_net,1)
        retro_o = np.dot(self.W[0:self.n_net,self.n_input+self.n_hidden:], out)
        # backward states
        retro_activation += retro_o
        self.rec_states = retro_activation

        # output (y)
        m1 = out[0] - out[1]
        m2 = out[2] - out[3]
        # communication
        com = out[4:4+self.com_n].T
        # return as numbers
        return m1[0], m2[0], com[0]

    def neuron_fx(self, x):
        # random noise
        noise = np.array([np.random.uniform(-self.nn_noise,self.nn_noise,len(x))]).T
        x += noise
        # transfer fx
        y = np.where(x<=self.lt,0, np.where(x>=self.ut,1, (x-self.lt)/(self.ut-self.lt)))
        return y
























#
