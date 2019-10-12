
# Agent from egbert and barandarian agent, 2014. version 7

# Agent
    # distance_fx
    # weight_fx
    # density_fx
        # distance_fx()
        # weight_fx()
    # velocity_fx
        # distance_fx()
        # weight_fx()
    # attraction_fx
        # distance_fx()
        # weight_fx()
    # add_node
        # density_fx()
    # motor_fx
        # velocity_fx()
        # attraction_fx()
        # density_fx()
        # add_node()
    # maintenance_fx
        # distance_fx()
        # Node.activation()
    # idsm_fx
        # motor_fx()
        # maintenance_fx()
# Node
    # activation

# TODO : sensors

import numpy as np
import math
import matplotlib.pyplot as plt
from copy import deepcopy
from tqdm import tqdm

class Agent:

    def __init__(self, m=[], s=[]\
    ,nodes=[]\
    ,dt=0.1\
    ,kw=0.0025, kd=1000, kt=1, kr=10.0\
    ,sim_time=100):
        self.m = np.array(m)
        self.s = np.array(s)
        self.nodes = nodes
        self.dt = dt
        self.kw = kw
        self.kd = kd
        self.kt = kt
        self.kr = kr
        self.sim_time = sim_time
        # internal
        self.motor_dims = len(m)
        self.sensor_dims = len(s)
        self.x = np.concatenate((self.m, self.s))
        self.velocity = np.array([0]*len(self.x))
        # records
        self.motor_records = []
        self.sensor_records = []

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, Np, x):
        try:
            distance = 2/(1+math.exp(self.kd*(np.linalg.norm(Np-x)**2)))
        except OverflowError:
            distance = 0
        return distance

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        try:
            weight = 2/(1+np.math(-self.kw*Nw))
        except:
            weight=0
        return weight

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density=0
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position, self.x)
                density += weight*distance
        return density*self.dt

    # velocity function
    # velocity_fx = ∑ w(Nw) * d(Np,x) * Nv_µ
    def velocity_fx(self):
        self.velocity[:self.motor_dims] *= 0.0
        for node in self.nodes:
            if node.active:
                Nv_motor = node.velocity[:self.motor_dims]
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position, self.x)
                self.velocity[:self.motor_dims]+=weight*distance*Nv_motor
        self.velocity[:self.motor_dims]*=self.dt

    # attraction function
    # attraction_fx = ∑ w(Nw) * d(Np,x) * Gamma(Np-x,Nv)_µ
    def attraction_fx(self):
        attraction=np.array([0.0]*self.motor_dims)
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position, self.x)
                # motor velocity
                Nv_mu = node.velocity[:self.motor_dims]
                # gamma function
                # Gamma_fx = a - a * (Nv / ||Nv||)
                nNv_mu = Nv_mu/np.linalg.norm(Nv_mu) if np.linalg.norm(Nv_mu) > 0 else Nv_mu
                # a = Np_motor - x_motor
                Npx = node.position[:self.motor_dims] - self.x[:self.motor_dims]
                gamma = Npx - Npx*nNv_mu
                attraction+=weight*distance*gamma
        return attraction*self.dt

    # adding nodes
    # if phi(x) < kt=1
    # def add_node(self):
    #     if self.density*self.dt < self.kt:
    #         self.nodes.append(Node(self.x, self.velocity))

    # motor influence
    # dµ/dt = ( V(x) + A(x) ) / phi(x)
    def motor_fx(self):
        self.velocity_fx()
        attraction=self.attraction_fx()
        density=self.density_fx()
        #if density < self.kt:
        self.nodes.append(Node(self.x, self.velocity))
        mu = (self.velocity[:self.motor_dims]+attraction)/density
        return mu

    # maintenance of nodes (updating of nodes' weights)
    # dNw/dt = -1 + r(N,x)
    def maintenance_fx(self):
        dws = []
        for node in self.nodes:
            if node.active:
                # node's reinforcement function
                # r(N,x) = kr=10 * d(Np,x)
                distance_to_x = self.distance_fx(node.position,self.x)
                reinforcement = self.kr * distance_to_x
                dw = (-1 + reinforcement)
                dws.append(dw)
            else:
                dws.append(0.0)
        return np.array(dws)

    # Euler method
    # 1) dx/dt = F(x,t)
    # 2) dx/dt = ∆x/∆t (for small ∆)
    # 3) x_n+1 = x_n + ∆x
    # 2 => ∆x = (dx/dt) * ∆t
    # 1,2 > 3 => x_n+1 = x_n + F(x,t) ∆t

    # IDSM
    def idsm_fx(self):
        x_mu0 = self.x[:self.motor_dims]
        t = 0
        pbar = tqdm(total=self.sim_time)
        while t < self.sim_time:
            # dif. eq. functions
            # dmu/dt : F(x,t) = ( V(x) + A(x) ) / phi(x)
            f_xmu = self.motor_fx()
            # dNw/dt : F(x,t) = -1 + r(N,x)
            f_Nw = self.maintenance_fx()
            # update system
            # dif. eqs. steps : x_n+1 = x_n + F(x,t)*∆t
            # position
            x_mu = x_mu0 + f_xmu
            self.x[:self.motor_dims] = x_mu
            x_mu0 = x_mu
            # record changes
            self.motor_records.append(deepcopy(self.x))
            # weights
            weights0 = np.array([node.weight if node.active else 0.0 for node in self.nodes])
            updated_weights = weights0 + f_Nw*self.dt
            for n in range(len(self.nodes)):
                self.nodes[n].weight = updated_weights[n]
            # nodes
            [node.activation_fx() for node in self.nodes]
            #self.add_node()
            # dif. time
            t += self.dt
            pbar.update(self.dt)
        pbar.close()

class Node:

    def __init__(self, position, velocity, weight=0, t2a=10):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.weight = weight
        self.t2a = t2a
        self.active = False

    # activation
    def activation_fx(self):
        if self.t2a > 0:
            self.t2a -= 1
        else:
            self.active = True

#####################################################
              # Experiments
#####################################################

def training_fx(time=35, dt=0.1):
    # intitialize agent
    agent = Agent(m=[-2.5], s=[1/(1+(-2.5)**2)])
    agent.nodes.append(Node(agent.x,agent.velocity))
    # run trainer controller
    t = 0
    pbar = tqdm(total=20)
    while t < 20:
        # movement
        dm = np.array([np.cos(t/2)])*dt
        agent.m += dm
        agent.s = np.array(1/(1+agent.m**2))
        ds = agent.x[agent.motor_dims:]-agent.s
        agent.velocity = np.concatenate((dm,ds))
        agent.x = np.concatenate((agent.m, agent.s))
        # nodes
        f_Nw = agent.maintenance_fx()
        weights0 = np.array([node.weight if node.active else 0.0 for node in agent.nodes])
        updated_weights = weights0 + f_Nw*dt
        for n in range(len(agent.nodes)):
            agent.nodes[n].weight = updated_weights[n]
        [node.activation_fx() for node in agent.nodes]
        agent.nodes.append(Node(agent.x,agent.velocity))
        # record
        agent.motor_records.append(deepcopy(agent.x[:agent.motor_dims]))
        agent.sensor_records.append(deepcopy(agent.x[agent.motor_dims:]))
        t += dt
        pbar.update(dt)
    pbar.close()
    # plots
    plt.plot([t/100 for t in range(len(agent.nodes))], [node.position[0] for node in agent.nodes])
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.savefig("_TrainingPlot")
    plt.close()
    plt.plot([t/100 for t in range(len(agent.nodes))], [node.position[1] for node in agent.nodes])
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.savefig("_TrainingPlot2")
    plt.close()
    # run IDSM
    agent.sim_time = 15
    agent.idsm_fx()
    # plot
    plt.plot([t for t in range(len(agent.nodes))], [node.position for node in agent.nodes])
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.savefig("_IDSMplot")
    plt.close()
    # plot
    plt.plot([t for t in range(len(agent.motor_records))], [x[0] for x in agent.motor_records])
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.savefig("_xPlot")
    plt.close()
    return agent







# fin
