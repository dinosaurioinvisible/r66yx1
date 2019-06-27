
#v5

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import copy
import pdb

# scale values
# u = self.scale(x)
# v = self.scale(Np)

# sensor?????????????
# self.s = np.array(s)
# self.smax = smax
# self.shist = []
# inside Np as another dimension : Np=[Px,Ps] : Nv=[Vx,Vs]??

# agent
class Agent:
    def __init__(self, x=[], xmax=[]
    ,kw=0.0025, kd=1000, kt=1, kr=10\
    ,sim_time=100\
    ,nodes=[]):
        self.sim_time = sim_time
        # motors and sensors
        self.x = np.array(x)
        self.xmax = np.array(xmax)
        # constants
        self.kw = kw
        self.kd = kd
        self.kt = kt
        self.kr = kr
        # records
        self.nodes = nodes
        self.xhist = []

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        weight = 2/(1+np.exp(-self.kw*Nw))
        return weight

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, Np, x):
        print(np.linalg.norm(Np-x))
        distance = 2/(1+np.exp(self.kd*(np.linalg.norm(Np-x)**2)))
        return distance

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density = 0
        for node in self.nodes:
            Nw = node[2]
            Np = node[0]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(Np, self.x)
            density += (weight*distance)
        return density

    # attraction function
    # attraction_fx = (Np - x) - (Np-x)*(Nv/np.absolute(Nv))
    def attraction_fx(self, Np, x, Nv):
        # in case Nv=0, no avoid dividing by zero
        Nv = 1 if Nv == 0 else Nv
        # euclidian distance for Nv is just its absolute value
        euNv = np.sqrt(Nv**2)
        # Gamma function
        attraction = (Np-x)-((Np-x)*(Nv/euNv))
        return attraction

    # maintenance of nodes (updating of nodes' weights)
    # dNw/dt = -1 + r(N,x)
    def maintenance_fx(self):
        for n in range(len(self.nodes)):
            Np = np.array(self.nodes[n][0])
            # node's reinforcement function
            # r(N,x) = kr=10 * d(Np,x)
            distance = self.distance_fx(Np, self.x)
            reinforcement = self.kr*distance
            updated_weight = -1 + reinforcement
            self.nodes[n][2] = updated_weight

    # IDSM motor influence function
    # d_mu/dt = 1/density_fx * summatory( weight_fx * distance_fx * (velocity + attraction_fx) )
    def motor_fx(self):
        motor_sum = 0
        for node in self.nodes:
            Np = node[0]
            Nv = node[1]
            Nw = node[2]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(Np, self.x)
            attraction = self.attraction_fx(Np, self.x, Nv)
            motor_sum += (weight*distance*(Nv+attraction))
        density = self.density_fx()
        motor_influence = motor_sum/density
        return motor_influence

    # IDSM
    def idsm_fx(self):
        self.maintenance_fx()
        self.motor_fx()

#####################################################
                  # Example experiments
#####################################################

    def training_fx(self, t=20):
        self.x = np.array([-2.5])
        self.xhist.append(copy.deepcopy(self.x))
        self.nodes.append([copy.deepcopy(self.x), 0, 0])
        for t in range(1, t+1):
            # movement
            velocity = np.array([np.cos(t/2)/2])
            self.x += velocity
            # sensor
            # sensor = 1/(1+self.x**2)
            # self.sensor_hist.append(sensor)
            # creation of nodes
            self.nodes.append([copy.deepcopy(self.x), velocity, 0])
            # record for whole history
            self.xhist.append(copy.deepcopy(self.x))
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
            # sensor = 1/(1+self.x**2)
            # self.sensor_hist.append(sensor)
            #
        plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot_all")
        # plt.close()
        plt.plot([t for t in range(len(self.xhist))], [i[0] for i in self.xhist])
        plt.scatter([t for t in range(len(self.xhist))], [i[0] for i in self.xhist])
        plt.xlabel("Time")
        plt.ylabel("Position")
        plt.savefig("_TrainingPlot_x")
        plt.close()
        # plt.plot([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
        # plt.scatter([t for t in range(len(self.sensor_hist))], [i for i in self.sensor_hist])
        # plt.xlabel("Time")
        # plt.ylabel("Position")
        # plt.savefig("_TrainingPlot_s")
        # plt.close()

























####
