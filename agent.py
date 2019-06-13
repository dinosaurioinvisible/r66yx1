
# agent-object

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import pdb

# agent
class Agent:
    def __init__(self, x=-2.5, nodes=[], kw=0.0025, kd=1000, kt=1):
        self.x = x
        self.nodes = nodes
        self.kw = kw
        self.kd = kd
        self.kt = 1
        ####
        # t=0, velociy=1 for convinience so attraction isn't nan
        # self.nodes.append([self.x, 0, 0)
        # records for position (independent of the creation of nodes)
        self.history = []

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
        weight = 2/1+np.exp(-self.kw*Nw)
        return weight

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, x, Np):
        # scale values
        xmax = max([node[0] for node in self.nodes])
        ex = self.scale(x, xmax)
        eNp = self.scale(Np, xmax)
        distance = 2/(1+np.exp(self.kd*((ex-eNp)**2)))
        return distance

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density = 0
        for node in self.nodes:
            Nw = np.array(node[2])
            Np = np.array([node[0]])
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            density += weight*distance
        return density

    # attraction function
    # attraction_fx = (Np - x) - (Np-x)*(Nv/np.absolute(Nv))
    def attraction_fx(self, x, Np, Nv):
        # scale
        vmax = max([node[1] for node in self.nodes])
        nNv = self.scale(Nv, vmax)
        attraction = (Np-x)-(Np-x)*(Nv/nNv)
        return attraction

    # IDSM motor influence function
    # d_mu/dt = 1/density_fx * summatory( weight_fx * distance_fx * (velocity + attraction_fx) )
    def idsm_fx(self):
        density = self.density_fx()
        motor_influence = 0
        for node in self.nodes:
            Np = np.array([node[0]])
            Nv = np.array([node[1]])
            Nw = np.array(node[2])
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            # velocity : Nv
            attraction = self.attraction_fx(self.x, Np, Nv)
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
            self.nodes.append([self.x, idsm_influence, 0])
            print("node added")
            print([self.x, idsm_influence, 0])
        else:
            print("nothing")
        print("density = "+str(density))

    # node's reinforcement function
    # r(N,x) = 10 * d(Np,x)
    def reinforcement_fx(self, x, Np):
        xdistance = self.distance_fx(x, Np)
        reinforcement = 10*xdistance
        return reinforcement

    # maintenance of nodes (updating of nodes' weights)
    # dNw/dt = -1 + r(N,x)
    def maintenance_fx(self):
        for n in range(len(self.nodes)):
            Np = np.array(self.nodes[n][0])
            reinforcement = self.reinforcement_fx(self.x, Np)
            updated_weight = -1+reinforcement
            self.nodes[n][2] = updated_weight

    # training
    # for the first 20 time units the robot is controlled by a training controller
    def training_fx(self, t=20):
        for t in range(1, t+1):
            # movement
            velocity = np.cos(t/2)/2
            weight = 0
            self.x += velocity
            # creation of nodes
            self.history.append(self.x)
            self.nodes.append([self.x, velocity, weight])
        plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.xlabel("Time")
        plt.ylabel("Position")
        #plt.savefig("TrainingPlot")

    # idsm control phase
    def operation(self, time=10):
        print("\n")
        [print(node) for node in self.nodes]
        print("\n")
        for t in range(time):
            print("\n")
            print(t)
            self.idsm_fx()
            self.maintenance_fx()
            [print(node) for node in self.nodes[-5:-1]]
            self.history.append(self.x)
        plt.plot([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.scatter([t for t in range(len(self.nodes))], [i[0] for i in self.nodes])
        plt.savefig("WholePlot")
        plt.close()
        # print positions independently of the creation of the nodes
        plt.plot([t for t in range(len(self.history))], [i for i in self.history])
        plt.savefig("AgentHistory")
        plt.close()



    # experiment

    # __main__
    # if __name__ == "__main__":
    #    main()
