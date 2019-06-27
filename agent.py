
# agent-object

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import copy
import pdb

# agent
class Agent:
    def __init__(self, sim_time=15\
    ,x=[], xmax=1
    ,kw=0.0025, kd=1000, kt=1, nodes=[]):
        self.sim_time = sim_time
        self.x = np.array(x)
        self.xhistory = []
        self.xmax = xmax
        self.kw = kw
        self.kd = kd
        self.kt = kt
        self.nodes = nodes
        self.sensor_hist = []


    # escaling fx
    # Np & Nv are calculated in a normalized SM space where
    # the range of sensor and motor values are scaled between 0 and 1
    # ex = (x * range max) / (dataset max)
    def scale(self, x, rangemax=1):
        ex = (x*rangemax)/self.xmax
        return ex

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        weight = 2/(1+np.exp(-self.kw*Nw))
        return weight

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, x, Np):
        # scale values
        u = self.scale(x)
        v = self.scale(Np)
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
        sum_weight = 0
        sum_distance = 0
        sum_vel_attraction = 0
        for node in self.nodes:
            Np = np.array(node[0])
            Nv = np.array(node[1])
            Nw = node[2]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            # velocity : Nv
            attraction = self.attraction_fx(self.x, Np, Nv)
            # sum
            motor_influence += weight*distance*(Nv+attraction)
            sum_weight += weight
            sum_distance += distance
            sum_vel_attraction += (Nv*attraction)
        idsm_influence = (1/density)*motor_influence
        print(self.x)
        print("idsm={} = 1/density={} * w(Nw)={} * d(Np,x)={} * Vel+Att={}".format(idsm_influence, density, sum_weight, sum_distance, sum_vel_attraction))
        # new position
        self.x = self.x + idsm_influence
        self.xhistory.append(copy.deepcopy(self.x))
        # creation of nodes
        # if density fx < kt = 1
        if density < self.kt:
            # velocity is given by the idsm
            # position = x + idsm influence
            # initial weight = 0
            self.nodes.append([copy.deepcopy(self.x), idsm_influence, 0])

    # sensory input
    def sensory_fx(self):
        # s = 1 / (1 + x**2)
        s_input = 1/(1+self.x**2)
        self.sensor_hist.append(s_input)

    # node's reinforcement function
    # r(N,x) = 10 * d(Np,x)
    def reinforcement_fx(self, x, Np):
        xdistance = self.distance_fx(x, Np)
        return 10*xdistance

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

    def training_fx(self, time=20):
        self.x = np.array([-2.5])
        self.xhistory.append(copy.deepcopy(self.x))
        self.nodes.append([copy.deepcopy(self.x), 0, 0])
        for t in range(1, time+1):
            # movement
            velocity = np.array([np.cos(t/2)/2])
            self.x += velocity
            # sensor
            sensor = 1/(1+self.x**2)
            self.sensor_hist.append(sensor)
            # creation of nodes
            self.nodes.append([copy.deepcopy(self.x), velocity, 0])
            # record for whole history
            self.xhistory.append(copy.deepcopy(self.x))
            # print
            print("x={}".format(self.x))
            print("vel={}".format(velocity))
        # plot
        plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot")
        # plt.close()
        # IDSM operation
        for t in range(15):
            self.idsm_fx()
            # sensor
            sensor = 1/(1+self.x**2)
            self.sensor_hist.append(sensor)
            #
        plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot_all")
        # plt.close()
        plt.plot([t for t in range(len(self.xhistory))], [i[0] for i in self.xhistory])
        plt.scatter([t for t in range(len(self.xhistory))], [i[0] for i in self.xhistory])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot_x")
        plt.close()
        plt.plot([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
        plt.scatter([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot_s")
        plt.close()
