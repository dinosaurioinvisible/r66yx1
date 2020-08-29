
import numpy as np

class Net()
    def __init__(self, genotype):
        # from genotype
        self.n_input = genotype.n_input
        self.n_hidden = genotype.n_hidden
        self.n_output = genotype.n_output
        self.n_net = self.n_input+self.n_hidden+self.n_output
        self.W = genotype.W
        self.lts = genotype.lts
        self.uts = genotype.lts
        # parameters
        self.dt = 1
        self.taus = np.ones((self.n_net))
        self.states = np.zeros((self.n_net))
        self.output = np.zeros(self.n_output)
        # init network if there isn't one
        if len(self.W) == 0:
            self.init_network(genotype)
