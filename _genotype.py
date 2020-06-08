
import numpy as np

class Genotype:
    def __init__(self, energy=5000\
        , r=2.5\
        , max_speed=5, wheels_sep=4\
        , feeding_rate=3, feeding_range=10, feeding_theta=90\
        , s_points=100\
        , vs_n=2, vs_dos=[-45,45], vs_range=55, vs_theta=100\
        , olf_range=22, olf_theta=270\
        , com_range=33, com_len=3, signals="abcxdef"\
        , n_in=7, n_hidden=5, n_out=7\
        , ut=0.5, lt=0.1, vt=0.9\
        , W=[], V=[]\
        , plasticity=0):
        # agent
        self.energy = energy
        self.r = r
        self.max_speed = max_speed
        self.wheels_sep = wheels_sep
        self.feeding_rate = feeding_rate
        self.feeding_range = feeding_range
        self.feeding_theta = feeding_theta
        # sensors
        self.s_points = s_points
        self.vs_n = vs_n
        self.vs_dos = vs_dos
        self.vs_range = vs_range
        self.vs_theta = vs_theta
        self.olf_range = olf_range
        self.olf_theta = olf_theta
        # communication channel
        self.com_range = com_range
        self.com_len = com_len
        self.signals = signals
        # nnet
        self.n_input = n_in
        self.n_hidden = n_hidden
        self.n_output = n_out
        self.ut = ut
        self.lt = lt
        self.vt = vt
        self.W = W
        self.V = V
        if len(W)==0 and len(V)==0:
            self.random_weights()
        self.plasticity = plasticity

    def random_weights(self):
        # matrices for weights (features as columns)
        self.n_net = self.n_input+self.n_hidden+self.n_output
        # connectivity matrices
        self.W = np.zeros((self.n_net, self.n_net))
        self.V = np.zeros((self.n_net, self.n_net))
        # random init for input -> hidden
        for i in range(self.n_input):
            for j in range(self.n_input, self.n_input+self.n_hidden):
                self.W[i][j] = np.random.randn()
                self.V[i][j] = 0
                # self.V[i][j] = np.random.randint(2)
        # random init for hidden -> motor
        for i in range(self.n_input, self.n_input+self.n_hidden):
            for j in range(self.n_input+self.n_hidden, self.n_net):
                self.W[i][j] = np.random.randn()
                self.V[i][j] = 0
                # self.V[i][j] = np.random.randint(2)







    #
