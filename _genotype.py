
import numpy as np
import random

class Genotype:
    def __init__(self, r=2.5\
        , e_in=1, energy=100, de_dt=0.1\
        , max_speed=5, wheels_sep=4\
        , feeding_rate=2, feeding_range=10, feeding_theta=90\
        , s_points=100\
        , vs_n=4, vs_dos=[-15,-60,15,60], vs_range=50, vs_theta=30\
        , olf_n=1, olf_range=22, olf_theta=270\
        , com_range=33, com_len=2, signals="axb"\
        , n_hidden=5\
        , ut=0.5, lt=0.1, vt=0.9\
        , W=[], V=[]\
        , n_motor = 4\
        , plasticity=0):
        # agent
        self.r = r
        self.energy = energy
        self.de_dt = de_dt
        self.max_speed = max_speed
        self.wheels_sep = wheels_sep
        self.feeding_rate = feeding_rate
        self.feeding_range = feeding_range
        self.feeding_theta = feeding_theta
        # sensors
        self.s_points = s_points
        self.e_in = e_in
        # sensors: vision
        self.vs_n = vs_n
        self.vs_dos = vs_dos
        self.vs_range = vs_range
        self.vs_theta = vs_theta
        # sensors: olfactory
        self.olf_n = olf_n
        self.olf_range = olf_range
        self.olf_theta = olf_theta
        # communication channel
        self.com_range = com_range
        self.com_len = com_len
        self.signals = signals
        # nnet
        self.n_input = vs_n+olf_n+e_in+com_len
        self.n_hidden = n_hidden
        self.n_output = n_motor+com_len
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
                self.W[i][j] = random.uniform(-0.75,0.75)
                self.V[i][j] = 0
                # self.V[i][j] = np.random.randint(2)
        # random init for hidden -> motor
        for i in range(self.n_input, self.n_input+self.n_hidden):
            for j in range(self.n_input+self.n_hidden, self.n_net):
                self.W[i][j] = random.uniform(-0.75,0.75)
                self.V[i][j] = 0
                # self.V[i][j] = np.random.randint(2)







    #
