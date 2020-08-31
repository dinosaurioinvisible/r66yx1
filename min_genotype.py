
import numpy as np

#TODO: hacer angulos automaticos para vs_n y olf_n

class Genotype:
    def __init__(self, str_gen=None
        , r=2.5, max_speed=5, wheels_sep=4, motor_n=2
        , energy=1000, de_dt=1, e_n=0
        , f_rate=10, f_range=10, f_theta=90
        , vs_n=8, vs_range=25#, vs_loc=[-30,30], vs_range=25, vs_theta=90
        , olf_n=2, olf_loc=[-60,60], olf_range=35, olf_theta=180
        , com_n=0, com_range=25, com_theta=360, com_signals="lxh", com_lt=0.25, com_ut=0.75
        , n_hidden=3, network=None):
        # init from previous or not
        if str_gen:
            self.str_to_obj(str_gen)
        else:
            # agent
            self.r = r
            self.max_speed = max_speed
            self.wheels_sep = wheels_sep
            self.motor_n = motor_n
            self.energy = energy
            self.de_dt = de_dt
            self.e_n = e_n
            # feeding
            self.f_rate = f_rate
            self.f_range = f_range
            self.f_theta = f_theta
            # sensors
            # sensors: vision
            self.vs_n = vs_n
            self.vs_loc = np.array([30+(180*i)/(self.vs_n/2) for i in range(int(self.vs_n/2))])
            self.vs_loc = np.concatenate((self.vs_loc*-1, self.vs_loc))
            self.vs_range = vs_range
            self.vs_theta = 360/self.vs_n
            # sensors: olfact
            self.olf_n = olf_n
            self.olf_loc = olf_loc
            self.olf_range = olf_range
            self.olf_theta = olf_theta
            # communication
            self.com_n = com_n
            self.com_range = com_range
            self.com_theta = com_theta
            self.com_signals = com_signals
            self.com_lt = com_lt
            self.com_ut = com_ut
            # net
            self.n_input = self.vs_n+self.olf_n+self.e_n+self.com_n
            self.n_hidden = n_hidden
            self.n_output = self.motor_n+self.com_n
            self.network = network
            if self.network == None:
                self.network = []
                self.make_network()
            self.wnet = np.around(np.array([nx.wx for nx in self.network]),2)
            # save as str
            self.str_gen = ""
            self.obj_to_str()

    # create network (1st generation)
    def make_network(self):
        # neuron object
        from min_net import Neuron
        # define index and weights for each neuron
        n_net = self.n_input+self.n_hidden+self.n_output
        for i in range(n_net):
            # neuron object
            nx = Neuron()
            # -> input (no recurrent connections to input at first)
            w2i = np.zeros((self.n_input))
            # input -> hidden (common feedforward)
            # hidden -> hidden (recurrent hidden units)
            # output -> hidden (sensorimotor theory)
            w2h = np.array([np.random.uniform(-0.5,1) for n in range(self.n_hidden)])
            # -> output (only from hidden to output)
            if self.n_input <= i < self.n_input+self.n_hidden:
                w2o = np.array([np.random.uniform(-0.5,1) for n in range(self.n_output)])
            else:
                w2o = np.zeros((self.n_output))
            nx.wx = np.concatenate((w2i, w2h, w2o))
            # add to network
            self.network.append(nx)

    # string version
    def obj_to_str(self):
        self.str_gen += "b{}{}{}{}x".format(self.r,self.max_speed,self.wheels_sep,self.motor_n)
        self.str_gen += "v{}{:03}{:03}{:02}{:03}x".format(self.vs_n,self.vs_loc[0],self.vs_loc[1],self.vs_range,self.vs_theta)
        self.str_gen += "o{}{:03}{:03}{:02}{:03}x".format(self.olf_n,self.olf_loc[0],self.olf_loc[1],self.olf_range,self.olf_theta)
        self.str_gen += "c{}{:02}{:03}{}{:04}{:04}x".format(self.com_n,self.com_range,self.com_theta,self.com_signals,self.com_lt,self.com_ut)
        self.str_gen += "n{}".format(self.n_hidden)
        for i in range(len(self.network)):
            nx = self.network[i]
            self.str_gen += "u{:02}{:04}{:04}".format(i,nx.lt,nx.ut)
            for w in nx.wx:
                self.str_gen += "w{:05}".format(w)

    # unpack str
    def str_to_obj(self, str_gen):
        # save
        self.str_gen = str_gen
        # body params
        b = str_gen.index("b")
        self.r = float(str_gen[b+1])
        self.max_speed = int(str_gen[b+2])
        self.wheels_sep = int(str_gen[b+3])
        self.motor_n = int(str_gen[b+4])
        # vision
        v = str_gen.index("v")
        self.vs_n = int(str_gen[v+1])
        self.vs_loc = [-int(str_gen[v+2:v+5]),int(str_gen[v+5:v+8])]
        self.vs_range = int(str_gen[v+8:v+10])
        self.vs_theta = int(str_gen[v+10:v+13])
        # sensors: olfact
        o = str_gen.index("o")
        self.olf_n = int(str_gen[o+1])
        self.olf_loc = int(str_gen[o+2:o+5],int(str_gen[0+5:o+8]))
        self.olf_range = int(str_gen[o+8:o+10])
        self.olf_theta = int(str_gen[o+10:o+13])
        # communication
        c = str_gen.index("c")
        self.com_n = int(str_gen[c+1])
        self.com_range = int(str_gen[c+2:c+4])
        self.com_theta = int(str_gen[c+4:c+7])
        self.com_signals = str_gen[c+7:c+10]
        self.com_lt = float(str_gen[c+10:c+14])
        self.com_ut = float(str_gen[c+14:c+18])
        # network
        n = str_gen.index("n")
        self.n_hidden = int(str_gen[n+1])
        self.n_input = self.vs_n+self.olf_n+self.com_n
        self.n_output = self.motor_n+self.com_n
        n_net = self.n_input+self.n_hidden+self.n_output
        for i in range(self.n_net):
            ui = "u"+str(i)
            u = str_gen.index(ui)
            nx_id = int(str_gen[u+2:u+6])
            nx_lt = float(str_gen[u+6:u+10])
            nx_ut = float(str_gen[u+10:u+14])
            wi = u+14
            wx = []
            for _ in range(n_net):
                wxi = float(str_gen[wi:wi+5])
                wx.append(wxi)
                wi += 5
            self.net_params.append([nx_lt, nx_ut, wx])








##
