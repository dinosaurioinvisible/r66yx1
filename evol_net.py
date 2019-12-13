
import numpy as np
# import genome

class RNN:
    def __init__(self, n_input=3, n_hidden=2, n_output=4\
        , upper_t=0.6, lower_t=0.2, veto_t=0.7, weights=None):
        # dimensions
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        # matrices for weights (features as columns)
        # no output or input matrices
        if weights == None:
            # connectivity matrices
            #self.W = np.random.randint(2, size=(self.n_input, self.n_net))
            self.W = np.zeros((self.n_net, self.n_net))
            self.V = np.zeros((self.n_net, self.n_net))
            # random init for input -> hidden
            for i in range(self.n_input, self.n_input+self.n_hidden):
                for j in range(self.n_input):
                    self.W[i][j] = np.random.randn()
                    self.V[i][j] = np.random.randn()
            # random init for hidden -> motor
            for i in range(self.n_input+self.n_hidden, self.n_net):
                for j in range(self.n_input, self.n_input+self.n_hidden):
                    self.W[i][j] = np.random.randn()
                    self.V[i][j] = np.random.randn()
        else:
            self.W = weights[0]
            self.V = weights[1]
        # list of weight matrices for GA
        self.weights = [self.W, self.V]
        # threshold values
        self.ut = upper_t
        self.lt = lower_t
        self.vt = veto_t
        # past states for init
        # s0 = np.array([np.zeros(self.n_net)])
        # self.e_states = [s0]
        # self.h_states = [s0]

    def action(self, x):
        # input to input nodes
        ix = np.array([x])
        # reshape to hidden layer size
        ix.resize(1,self.n_net)
        # input through matrices, sum normal and veto inputs
        ei = np.dot(ix, self.W)
        hi = np.dot(ix, self.V)
        # add past states
        # ei += self.e_states[-1]
        # hi += self.h_states[-1]
        # go through nodes
        ho = self.veto_out_fx(ei)
        ei_noise = ei + np.random.randn(1, self.n_net)
        et = self.transfer_fx(ei_noise)
        eh = self.veto_in_fx(hi)
        eo = et*eh
        # save states
        # self.e_states.append(eo)
        # self.h_states.append(ho)
        # apply act fx to motor act values (excitatory + inhibitory)
        mx = eo + ho
        mo = self.sigmoid(mx)
        # return motor outputs [-1,1]
        m1_e = mo[0][-4]
        m1_h = mo[0][-3]
        m2_e = mo[0][-2]
        m2_h = mo[0][-1]
        m1 = m1_e - m1_h
        m2 = m2_e - m2_h
        import pdb; pdb.set_trace()
        return m1, m2

    def sigmoid(self, z):
        return np.array([1/(1+np.exp(-i)) for i in z])

    def transfer_fx(self, x):
        # if x >= t_up : 1; if x <= t_low: 0; else: (x-t_low)/(t_up-t_low)
        z = np.where(x<=self.lt, 0, x)
        x = np.where(x>=self.ut, 1, (x-self.lt)/(self.ut-self.lt))
        x = x*z
        return x

    def veto_in_fx(self, x):
        # if x > 0 : 0 else 1
        x = np.where(x>0, 1, 0)
        return x

    def veto_out_fx(self, x):
        # if x >= t : 1 else 0
        x = np.where(x>=self.vt, 1, 0)
        return x







        #
