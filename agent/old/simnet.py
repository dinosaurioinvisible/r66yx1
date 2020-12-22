
import numpy as np


class RNN:
    def __init__(self, n_input=6, n_hidden=3, n_output=6\
        , upper_t=0.5, lower_t=0.1, veto_t=0.9, W=[], V=[]):
        # dimensions
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        self.W = W
        self.V = V
        # threshold values
        self.ut = upper_t
        self.lt = lower_t
        self.vt = veto_t
        # past states for init
        s0 = np.array([np.zeros(self.n_net)])
        self.e_states = [s0]
        self.h_states = [s0]
        # record states
        self.states = None

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
        com_p = eo[0][-5]
        com_n = eo[0][-6]
        com = com_p - com_n
        # print("\nt={}: m1={}, m2={}".format(len(self.e_states)-1,m1,m2))
        # save states data
        self.states = []
        import pdb; pdb.set_trace()
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
