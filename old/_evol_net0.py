
import numpy as np
# import genome

class RNN:
    def __init__(self\
        , n_input=3, n_hidden=5, n_output=2\
        , upper_t=0.5, lower_t=0.1, weights=None):
        # dimensions
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output
        # matrices for weights (features as columns)
        if weights == None:
            self.W = np.random.randn(self.n_input, self.n_hidden)
            self.V = np.random.randn(self.n_input, self.n_hidden)
            self.Se = np.random.randn(self.n_hidden, self.n_hidden)
            self.Sh = np.random.randn(self.n_hidden, self.n_hidden)
            self.Me = np.random.randn(self.n_hidden, self.n_output)
            self.Mh = np.random.randn(self.n_hidden, self.n_output)
        else:
            self.W = weights[0]
            self.V = weights[1]
            self.Se = weights[2]
            self.Sh = weights[3]
            self.Me = weights[4]
            self.Mh = weights[5]
        # list of weight matrices for GA
        self.weights = [self.W, self.V, self.Se, self.Sh, self.Me, self.Mh]
        # threshold values
        self.ut = upper_t
        self.lt = lower_t
        # past states for init
        s0 = np.array([np.zeros(self.n_hidden)])
        self.x_states = [s0]
        self.h_states = [s0]

    def sigmoid(self, z):
        return np.array([1/(1+np.exp(-i)) for i in z])

    def transfer_fx(self, x):
        for i in range(len(x[0])):
            if x[0][i] >= self.ut:
                x[0][i] = 1
            elif x[0][i] <= self.lt:
                x[0][i] = 0
            else:
                x[0][i] = (i-self.lt)/(self.ut-self.lt)
        return x

    def veto_input_fx(self, x):
        for i in range(len(x[0])):
            x[0][i] = 0 if x[0][i]>0 else 1
        return x

    def veto_output_fx(self, x):
        for i in range(len(x[0])):
            x[0][i] = 1 if x[0][i]>= self.ut else 0
        return x

    def next(self, x=0, h=0):
        # x: excitatory inputs, h: inhibitory inputs

        ## => Excitatory state
        # for eventual transposition
        x = np.array([x])
        # (excitatory inputs * current weights)
        wx = np.dot(x, self.W)
        # get last excitatory state
        sx0 = np.dot(self.x_states[-1], self.Se)
        # add current and past states
        sx = np.add(wx,sx0)
        self.x_states.append(sx)

        ## => U: inhibitory output
        oh = self.veto_output_fx(sx)

        ## => T: transfer before veto
        noise = np.random.randn(self.n_hidden)
        # add noise from normal distribution
        nx = np.add(sx, noise)
        tx = self.transfer_fx(nx)

        ## > V: inhibitory input -> inhibitory state
        h = np.array([h])
        # in case there is no previus inhibitory input
        h0 = np.array([[0, 0, 0]])
        h = h0+h
        # (inhibitory inputs * veto_weights)
        ih = np.dot(h, self.V)
        # get last inhibitory state
        sh0 = np.dot(self.h_states[-1], self.Sh)
        # add past state
        sh = np.add(ih, sh0)
        self.h_states.append(sh)
        # veto input
        vh = self.veto_input_fx(sh)

        ## => excitatory output
        oe = tx * vh
        # convert to motor and return
        motor_e = np.dot(oe, self.Me)
        motor_h = np.dot(oh, self.Mh)
        m1 = motor_e[0][0] + motor_h[0][0]
        m2 = motor_e[0][1] + motor_h[0][1]
        #print("\ncheck")
        #print(oe)
        #print(oh)
        #print(round(m1,2), round(m2,2))
        return m1, m2














        #
