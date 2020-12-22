
import numpy as np

class Genotype:
    def __init__(self, energy=5000\
        , r=2.5\
        , max_speed=5, wheels_sep=2.5\
        , feeding_range=10, feeding_theta=90\
        , s_points=100\
        , vs_do=60, vs_range=50, vs_theta=120\
        , olf_range=25, olf_theta=270\
        , aud_do=90, aud_range=50, aud_theta=180\
        , n_in=6, n_hidden=3, n_out=6\
        , ut=0.5, lt=0.1, vt=0.9\
        , W=[], V=[]\
        , plasticity=0):
        # agent
        self.energy = energy
        self.r = r
        self.max_speed = max_speed
        self.wheels_sep = wheels_sep
        self.feeding_range = feeding_range
        self.feeding_theta = feeding_theta
        # sensors
        self.s_points = s_points
        self.vs_do = vs_do
        self.vs_range = vs_range
        self.vs_theta = vs_theta
        self.olf_range = olf_range
        self.olf_theta = olf_theta
        self.aud_do = aud_do
        self.aud_range = aud_range
        self.aud_theta = aud_theta
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
