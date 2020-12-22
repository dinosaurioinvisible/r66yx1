

import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon


class Network:
    def __init__(self,network):
        self.network = network
        self.irx = self.working_irs()
        self.state = np.zeros((len(network)))
        self.firing = np.zeros((len(network)))
        self.net_out = np.zeros((len(network)+4))
        self.motor_out = None

    def update(self, env_info):
        # net_in : sensors + recurrent; reset net_out
        net_in = np.concatenate((env_info,self.net_out[:-4]))
        self.net_out = np.zeros((len(network)+4))
        # update each neuron
        for i,nx in enumerate(self.network):
            # inner state: activation * decay constant + sensory + recurrent inputs
            nx_in = np.dot(nx.wx_in,np.array([self.net_in]).T)[0]
            nx.act = nx.act*(1-nx.gamma) + nx_in
            # interneural output function (fire if over threshold)
            # set decay constant for t=t+1 according to firing
            nx.ot = 1 if nx.act >= nx.th else 0
            nx.gamma = nx.gb if ot==1 else nx.ga
            nx_out = nx.wx_out * nx.ot
            self.net_out += nx_out
            # for analysis
            self.state[i] = nx.act
            self.firing[i] = nx.ot
        # motor output
        motor = self.net_out[:-4]
        motor_out = np.where(motor>0,1,0)
        lm = motor_out[0] - motor_out[1]
        rm = motor_out[2] - motor_out[3]
        return lm,rm

    def working_irs(self):
        # define working irs
        irs = np.zeros((self.n_input))
        for nx in self.network:
            irs += nx.wx_in[:self.n_input]
        irs = np.where(irs!=0,True,False)
        return irs


class NeuralSpace:
    def __init__(self):
        # parameters for neural space
        self.xrange = 200; self.yrange = 250
        self.srange = 50; self.mrange = 30
        # default number of inputs/outputs
        self.def_input = 8; self.def_output = 4
        # neural space
        self.sregion = []; self.mregion = []
        self.make_space()

    def make_space(self):
        # sensor region
        # 8 units in 2 rows of 4 units, sensor domain: 200x50
        # neuron area: space/8, then shrinked by 25%
        rdx = self.xrange/4
        rx = [[rdx*i+(rdx*0.25/2),rdx*(i+1)-(rdx*0.25/2)] for i in range(4)]
        sdy = self.srange/2
        sy = [[sdy*i+(sdy*0.25/2),sdy*(i+1)-(sdy*0.25/2)] for i in range(2)]
        for xloc in rx:
            for yloc in sy:
                self.sregion.append(RegionNeuron(xloc,yloc))
        # motor region
        # 4 units (1 row), motor domain: 200x30 (also 75%)
        ym = self.yrange-self.mrange
        ymloc = [ym+self.mrange*0.25, self.yrange-self.mrange*0.25]
        for xloc in rx:
            self.mregion.append(RegionNeuron(xloc,ymloc))

    def decode(self,genotype):
        # inter neural region (from genotype)
        interneurons = [Neuron(gene) for gene in genotype]
        neurons = self.sregion+interneurons+self.mregion
        # neuron cannot take input from motor nodes (input/hidden -> hidden)
        # neuron cannot output to sensor nodes (hidden -> hidden/output)
        # topology -> network (only hidden neurons)
        for nx in interneurons:
            # inputs for each neuron (sensor/hidden -> hidden)
            nx.wx_in = [0]*(len(neurons[:-self.def_output]))
            for ci in nx.l_in:
                c_in = False
                for ni in range(len(neurons[:-self.def_output])):
                    if Point(ci[0],ci[1]).within(neurons[ni].area):
                        nx.wx_in[ni] = ci[2]
                        c_in = True
                nx.cx_in.append(c_in)
            # outputs for each neuron (hidden -> hidden/motor)
            nx.wx_out = [0]*(len(neurons[self.def_input:]))
            for co in nx.l_out:
                c_out = False
                for no in range(len(neurons[self.def_input:])):
                    if Point(co[0],co[1]).within(neurons[self.def_input+no].area):
                        nx.wx_out[no] = co[2]
                        c_out = True
                nx.cx_out.append(c_out)
        # number of inputs (working sensors) this network
        # instead of changing this, i'm just making input=0
        return interneurons


class RegionNeuron:
    def __init__(self, xloc, yloc):
        # fixed predefined rectangles for sensor/motor regions
        x0,x1 = xloc
        y0,y1 = yloc
        self.area = Polygon([(x0,y0),(x0,y1),(x1,y1),(x1,y0),(x0,y0)])

class Neuron:
    def __init__(self, gene, rmax=15):
        # from genotype
        self.id = gene[0]
        self.x = gene[1]
        self.y = gene[2]
        self.th = gene[3]
        self.ga = gene[4]
        self.gb = gene[5]
        self.l_in = gene[6]
        self.l_out = gene[7]
        # for topology
        self.loc = Point(self.x,self.y)
        self.area = self.loc.buffer(rmax)
        self.cx_in = []
        self.cx_out = []
        # for updating
        self.act = 0
        self.ot = 0
        self.gamma = self.ga
        self.wx_in = []
        self.wx_out = []







































#
