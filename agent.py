
# agent-object

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import copy
import pdb

# agent
class Agent:
    def __init__(self, sim_time=15\
    ,x=[], xmax=[]
    ,kw=0.0025, kd=1000, kt=1, nodes=[]):
        self.sim_time = sim_time
        self.x = np.array(x)
        self.xmax = xmax
        self.kw = kw
        self.kd = kd
        self.kt = kt
        self.nodes = nodes
        self.sensor_hist = []
        ####
        # initial node
        # self.nodes.append([self.x, 0, 0])
        # 
        #
        #
        # records for position (independent of the creation of nodes)
        self.all_x = []
        self.all_nodes = []
        self.why = []

    # escaling fx
    # Np & Nv are calculated in a normalized SM space where
    # the range of sensor and motor values are scaled between 0 and 1
    def scale(self, x, datamax, rangemax=1):
        # ex = (x * range max) / (dataset max)
        e_x = (x*rangemax)/datamax
        return e_x

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        weight = 2/(1+np.exp(-self.kw*Nw))
        return weight

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, x, Np):
        # scale values
        # scale from dataset values (problem : values change : scaling is incorrect)
        # xmax = max([max(np.absolute(node[0])) for node in self.nodes])
        u = self.scale(x, self.xmax)
        v = self.scale(Np, self.xmax)
        # euclidian distance between vectors
        eudist = np.sqrt(sum([(i-j)**2 for i,j in zip(u,v)]))
        distance = 2/(1+np.exp(self.kd*((eudist)**2)))
        return distance

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density = 0
        for node in self.nodes:
            Nw = node[2]
            Np = np.array(node[0])
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            density += weight*distance
        return density

    # attraction function
    # attraction_fx = (Np - x) - (Np-x)*(Nv/np.absolute(Nv))
    def attraction_fx(self, x, Np, Nv):
        # scale
        # vmax = max(np.absolute([node[1] for node in self.nodes]))
        # if-else just not to divide by zero
        # nNv = self.scale(Nv, vmax) if Nv else 1
        #
        #
        # if-else just not to divide by zero
        nNv = np.sqrt(Nv**2)
        nNv=1 if not nNv else nNv
        attraction = (Np-x)-((Np-x)*(Nv/nNv))
        return attraction

    # IDSM motor influence function
    # d_mu/dt = 1/density_fx * summatory( weight_fx * distance_fx * (velocity + attraction_fx) )
    def idsm_fx(self):
        density = self.density_fx()
        motor_influence = 0
        for node in self.nodes:
            Np = np.array(node[0])
            Nv = np.array(node[1])
            Nw = node[2]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            # velocity : Nv
            attraction = self.attraction_fx(self.x, Np, Nv)
            #
            motor_influence += weight*distance*(Nv+attraction)
        idsm_influence = (1/density)*motor_influence
        # new position
        self.x = self.x + idsm_influence
        # creation of nodes
        # if density fx < kt = 1
        if density < self.kt:
            # velocity is given by the idsm
            # position = x + idsm influence
            # initial weight = 0
            self.nodes.append([copy.deepcopy(self.x), idsm_influence, 0])
        #
        #
        #
        self.all_nodes.append([copy.deepcopy(self.x), idsm_influence, 0])
        self.why.append([density, motor_influence, Nv, attraction, idsm_influence])

    # sensory input
    def sensory_fx(self):
        # s = 1 / (1 + x**2)
        s_input = 1/(1+self.x**2)
        self.sensor_hist.append(s_input)

    # node's reinforcement function
    # r(N,x) = 10 * d(Np,x)
    def reinforcement_fx(self, x, Np):
        xdistance = self.distance_fx(x, Np)
        reinforcement = 10*xdistance
        return reinforcement

    # maintenance of nodes (updating of nodes' weights)
    def maintenance_fx(self):
        for n in range(len(self.nodes)):
            Np = np.array(self.nodes[n][0])
            reinforcement = self.reinforcement_fx(self.x, Np)
            # dNw/dt = -1 + r(N,x)
            updated_weight = -1 + reinforcement
            # = -1+r | += -1+r
            self.nodes[n][2] = updated_weight

    #####################################################
                      # Example experiments
    #####################################################

    # Figure 3
    # 2-motor, 0-sensor IDSM
    # sim_time = 20
    # manually added 4 nodes in relative proximity
    # externally assigned 2 motor states
    # m1 = 0.75 * cos( (2π / 10) * t
    # m2 = 0.75 * sin( (2π / 10) * t
    def figure3(self, time=20, iw = [-500, -100, 0, 50, 100]):
        for iwx in iw:
            # nodes = [position, velocity, weight]
            n1 = [[0.55, 0.50], 0, iwx]
            n2 = [[0.50, 0.45], 0, 0]
            n3 = [[0.45, 0.50], 0, 0]
            n4 = [[0.50, 0.55], 0, 0]
            self.nodes.append(n1, n2, n3, n4)
            for t in range(1, time+1):
                self.idsm_fx()
                self.maintenance_fx()
                self.all_x.append(copy.deepcopy(self.x))
            # plot x, y
            plt.plot([node[0][0] for node in self.nodes],[node[0][1] for node in self.nodes])
            figname = "node_weight_fig3_{}".format(iwx)
            plt.savefig(figname)
            plt.close
            # plot weight influence
            # plt.streamplot(x, y, u, v)
            # figname = "influence_fig3_{}".format(iwx)
            # plt.savefig(figname)
            # plt.close
