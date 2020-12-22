import numpy as np

class RNN:
    def __init__(self\
        , n_input=3, n_hidden=5, n_output=2\
        , bias=0.5\
        , upper_t=0.8, lower_t=0.2\
        , learning_rate=0.5):
        # dimensions
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output
        # matrices for weights (features as columns)
        self.W = np.random.randn(self.n_input, self.n_hidden)
        self.V = np.random.randn(self.n_input, self.n_hidden)
        self.U = np.random.randn(self.n_hidden, self.n_hidden)
        self.M = np.random.randn(self.n_hidden, self.n_output)
        # threshold values
        self.ut = upper_t
        self.lt = lower_t
        # past states for init
        s0 = np.array([np.zeros(self.n_hidden)]).T
        self.exc_states = [s0]
        self.inh_states = [s0]
        # to accumulate weights (input, hidden, output)
        self.delta_W = np.zeros((self.n_hidden, self.n_input))
        self.delta_V = np.zeros((self.n_hidden, self.n_input))
        self.delta_M = np.zeros((self.n_output, self.n_hidden))
