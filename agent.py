
# agent-object

import numpy as np
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
        self.history = []

    # actions
    # training
    # self.x = -2.5
    # self.training_fx()

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        weight = 2/1+np.exp(-self.kw*Nw)
        return weight

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, x, Np):
        distance = 2/(1+np.exp(self.kd*(Np-x)**2))
        return distance

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density = 0
        for node in self.nodes:
            Nw = node[2]
            Np = node[0]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            density += weight*distance
        return density

    # creation of nodes
    # if density fx < kt = 1
    def add_node_fx(self):
        density = self.density_fx()
        if density < self.kt:
            # change from last node to current position
            velocity = self.x-self.nodes[-1]
            weight = 0
            nodes.append([self.x, velocity, weight])
            print("node added")
            print([self.x, velocity, weight])
        else:
            print("nothing")
        print("density = "+str(density))

    # attraction function
    # attraction_fx = (Np - x) - (Np-x)*(Nv/np.absolute(Nv))
    def attraction_fx(self, x, Np, Nv):
        # pdb.set_trace()
        attraction = (Np-x)-(Np-x)*(Nv/np.absolute(Nv))
        return attraction

    # IDSM motor influence function
    # d_mu/dt = 1/density_fx * summatory( weight_fx * distance_fx * (velocity + attraction_fx) )
    def idsm_fx(self):
        density = self.density_fx()
        motor_influence = 0
        for node in self.nodes:
            Np = node[0]
            Nv = node[1]
            Nw = node[2]
            weight = self.weight_fx(Nw)
            distance = self.distance_fx(self.x, Np)
            # velocity : Nv
            attraction = self.attraction_fx(self.x, Np, Nv)
            motor_influence += weight*distance*(Nv+attraction)
        idsm_influence = (1/density)*motor_influence
        return idsm_influence

    # node's reinforcement function
    # r(N,x) = 10 * d(Np,x)
    def reinforcement_fx(self, x, Np):
        xdistance = self.distance_fx(x, Np)
        reinforcement = 10*xdistance
        return reinforcement

    # maintenance of nodes (updating of nodes' weights)
    # dNw/dt = -1 + r(N,x)
    def maintenance_fx(self):
        for node in self.nodes:
            Np = node[0]
            reinforcement = self.reinforcement_fx(self.x, Np)
            updated_weight = -1+reinforcement
            node[2] = updated_weight

    # training
    # for the first 20 time units the robot is controlled by a training controller
    def training_fx(self, t=20):
        # t=0
        self.nodes.append([self.x,0,0])
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
    def operation(self, time=100):
        print("\n")
        [print(node) for node in self.nodes]
        print("\n")
        for t in range(time):
            print("\n")
            print(t)
            self.maintenance_fx()
            self.idsm_fx()
            self.add_node_fx()
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
