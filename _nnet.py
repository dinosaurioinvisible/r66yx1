
import numpy as np


class RNN:
    def __init__(self, genotype):
        # dimensions
        self.n_input = genotype.n_input
        self.n_hidden = genotype.n_hidden
        self.n_output = genotype.n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        self.W = genotype.W
        self.V = genotype.V
        # threshold values
        self.ut = genotype.ut
        self.lt = genotype.lt
        self.vt = genotype.vt
        # past states for init
        s0 = np.array([np.zeros(self.n_net)])
        self.e_states = [s0]
        self.h_states = [s0]

    def update(self, x):
        # input to input nodes
        ix = np.array([x])
        # reshape to hidden layer size
        ix.resize(1,self.n_net)
        # input through matrices, sum normal and veto inputs
        ei = np.dot(ix, self.W)
        hi = np.dot(ix, self.V)
        # add past states
        pe = np.dot(self.e_states[-1], self.W)
        ph = np.dot(self.h_states[-1], self.V)
        ei += pe
        hi += ph
        # go through nodes
        ho = self.veto_out_fx(ei)
        ei_noise = ei + np.random.randn(1, self.n_net)*0.1
        et = self.transfer_fx(ei_noise)
        eh = self.veto_in_fx(hi)
        eo = et*eh
        # save states
        self.e_states.append(eo)
        self.h_states.append(ho)
        # return motor outputs [-1,1]
        # (only excitatory outputs, inhibitory are internal)
        m1_e = eo[0][-4]
        m1_h = eo[0][-3]
        m2_e = eo[0][-2]
        m2_h = eo[0][-1]
        m1 = m1_e - m1_h
        m2 = m2_e - m2_h
        c1 = eo[0][-5]
        c2 = eo[0][-6]
        com = [c1,c2]
        # print("\nt={}: m1={}, m2={}".format(len(self.e_states)-1,m1,m2))
        return m1, m2, com

    def transfer_fx(self, x):
        # if x >= t_up : 1; if x <= t_low: 0; else: (x-t_low)/(t_up-t_low)
        x = np.where(x<=self.lt, 0, x)
        x = np.where(x>=self.ut, 1, x)
        x = np.where((x>self.lt) & (x<self.ut), (x-self.lt)/(self.ut-self.lt), x)
        return x

    def veto_in_fx(self, x):
        # V fx: if x > 0 : 0 else 1
        x = np.where(x>0, 0, 1)
        return x

    def veto_out_fx(self, x):
        # U fx: if x >= t : 1 else 0
        x = np.where(x>=self.vt, 1, 0)
        return x







        #
