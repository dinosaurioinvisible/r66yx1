
import numpy as np

class Genotype:
    def __init__(self, r=2.5\
        , e_in=0, energy=1000, de_dt=1\
        , max_speed=5, wheels_sep=4\
        , feeding_rate=2, feeding_range=10, feeding_theta=90\
        , s_points=100\
        , vs_n=4, vs_dos=[-15,-60,15,60], vs_range=30, vs_theta=30\
        , olf_n=1, olf_range=30, olf_theta=300\
        , com_range=33, com_len=0, signals="axb"\
        , n_hidden=3\
        , ut=0.5, lt=0, vt=0.9\
        , nn_noise=0.1\
        , W=[], V=[], v_reset=False\
        , n_motor=4\
        , attn=True\
        , plastic=0):
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
        self.n_net = self.n_input+self.n_hidden+self.n_output
        self.ut = ut
        self.lt = lt
        self.vt = vt
        self.nn_noise = nn_noise
        self.W = W
        self.V = V
        # create matrices if they don't exist
        if len(W)==0 and len(V)==0:
            self.random_weights()
        # if there is one more hidden unit
        if self.W.shape[0] != self.n_net:
            self.adjust_shape()
        # activate/deactivate v matrix
        if v_reset:
            self.V = np.zeros((self.n_net, self.n_net))
            self.v_reset = False
        # just to be sure
        self.W = np.where(self.W<0,0,self.W)
        self.W = np.where(self.W>1,1,self.W)
        self.V = np.where(self.V<0,0,self.V)
        self.V = np.where(self.V>1,1,self.V)
        # very optional ideas
        self.attn = attn
        self.plastic = plastic

    def random_weights(self):
        # connectivity matrices
        self.W = np.zeros((self.n_net, self.n_net))
        self.V = np.zeros((self.n_net, self.n_net))
        # random init for input -> hidden
        for i in range(self.n_input, self.n_input+self.n_hidden):
            for j in range(self.n_input):
                #self.W[i][j] = 1
                self.W[i][j] = np.random.uniform(0.1,1)
        # random init for hidden -> hidden
        for i in range(self.n_input, self.n_input+self.n_hidden):
            for j in range(self.n_input, self.n_input+self.n_hidden):
                #self.W[i][j] = 1
                self.W[i][j] = np.random.uniform(0.1,1)
        # random init for hidden -> motor
        for i in range(self.n_input+self.n_hidden,self.n_net):
            for j in range(self.n_input, self.n_input+self.n_hidden):
                #self.W[i][j] = 1
                self.W[i][j] = np.random.uniform(0.1,1)

    def adjust_shape(self):
        # add hidden unit
        if self.W.shape[0] < self.n_net:
            # insert row
            row = np.array([np.random.uniform(0.1,1) for i in range(self.n_net-1)])
            self.W = np.insert(self.W, self.n_input+self.n_hidden, row, axis=0)
            self.V = np.insert(self.V, self.n_input+self.n_hidden, 0, axis=0)
            # insert column
            col = np.array([np.random.uniform(0.1,1) for i in range(self.n_net)])
            self.W = np.insert(self.W, self.n_input+self.n_hidden, col, axis=1)
            self.V = np.insert(self.V, self.n_input+self.n_hidden, 0, axis=1)
        # remove hidden unit
        elif self.W.shape[0] > self.n_net:
            self.W = np.delete(self.W, self.n_input+self.n_hidden, axis=0)
            self.W = np.delete(self.W, self.n_input+self.n_hidden, axis=1)
            self.V = np.delete(self.V, self.n_input+self.n_hidden, axis=0)
            self.V = np.delete(self.V, self.n_input+self.n_hidden, axis=1)









    #
