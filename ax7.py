
# Agent from egbert and barandarian agent, 2014. version 7

# TODO: the nodes, ho do I put them inside the dif.eq. ?

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

import numpy as np
import matplotlib as plt
from copy import deepcopy

class Agent:

    def __init__(self, m=[], s=[]\
    ,nodes=[]\
    ,delta_t=0.01\
    ,kw=0.0025, kd=1000, kt=1, kr=10\
    ,sim_time=20):
        self.m = np.array(m)
        self.s = np.array(s)
        self.nodes = nodes
        self.delta_t = delta_t
        # constant for weight_fx
        self.kw = kw
        # constant for distant_fx
        self.kd = kd
        # new node if density < kt
        self.kt = kt
        # reinforcement = kr * d(Np,x)
        self.kr = kr
        self.sim_time = sim_time
        ###
        self.mdim = len(m)
        self.sdim = len(s)
        self.x = np.concatenate((self.m, self.s))
        self.x0 = deepcopy(x)
        self.velocity = np.array([0]*len(self.x))

    # distance function
    # distance_fx = 2/1+np.exp(kd*(Np-x)**2)
    def distance_fx(self, Np, x):
        try:
            distance = 2/(1+np.exp(self.kd*((np.linalg.norm(Np-x))**2)))
            return distance
        except OverflowError:
            return 0

    # weight function
    # weight_fx = 2/1+np.exp(-kw*Nw)
    def weight_fx(self, Nw):
        # % Nw : self.weight = 0.0
        weight = 2/(1+np.exp(-self.kw*Nw))
        return weight

    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        density = 0
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position, self.x)
                density += (weight*distance)
        return density

    # velocity function
    # velocity_fx = ∑ w(Nw) * d(Np,x) * Nv_µ
    def velocity_fx(self):
        self.velocity *= 0
        for node in self.nodes:
            if node.active:
                Nv_motor = node.velocity[0:self.motor_dims]
                weight = weight_fx(node.weight)
                distance = distance_fx(node.position, self.x)
            self.velocity += weight * distance * Nv_motor

    # attraction function
    # attraction_fx = ∑ w(Nw) * d(Np,x) * Gamma(Np-x,Nv)_µ
    def attraction_fx(self):
        attraction = 0
        for node in self.nodes:
            if node.active:
                weight = weight_fx(node.weight)
                distance = distance_fx(node.position, self.x)
                # to avoid division by zero
                Nv = 1 if Nv == 0 else Nv
                # unit vector
                nNv = Nv/np.linalg.norm(Nv)
                # gamma function
                # Gamma_fx = a - a dot (Nv / ||Nv||)
                gamma = (node.position-self.x) - ((node.position-self.x)*nNv)
                attraction += weight * distance * gamma
        return attraction

    # adding nodes
    # if phi(x) < kt=1
    def add_node(self):
        density = self.density_fx()
        if density < self.kt:
            self.nodes.append(Node(self.x, self.velocity))

    # dif. eqs.
    # 1) dx/dt = F(x,t)
    # 2) dx/dt = ∆x/∆t (for small ∆)
    # 3) x_n+1 = x_n + ∆x
    # 2) => ∆x = (dx/dt) * ∆t
    # 1,2 > 3 => x_n+1 = x_n + F(x,t) ∆t

    # motor influence
    # dµ/dt = ( V(x) + A(x) ) / phi(x)
    def motor_fx(self):
        # dif. eq.
        t = 0
        while t < 1:
            # F(x,t) = ( V(x) + A(x) ) / phi(x)
            velocity = self.velocity_fx()
            attraction = self.attraction_fx()
            density = self.density_fx()
            f_xt = (velocity+attraction)/density
            # x_n+1 = x_n + F(x,t) ∆t
            self.x = self.x0 + (f_xt * self.delta_t)
            # new x0 and t
            self.x0 = deepcopy(self.x)
            t += self.delta_t

    # maintenance of nodes (updating of nodes' weights)
    # dNw/dt = -1 + r(N,x)
    def maintenance_fx(self, distance_to_x):
        # dif. eq.
        t = 0
        while t < 1:
            # node's reinforcement function
            # r(N,x) = kr=10 * d(Np,x)
            reinforcement = self.kr * distance_to_x
            # F(x,t) = -1 + r(N,x)
            f_xt = -1 + reinforcement
            #
            self.nodes[n][2] = updated_weight
            # x_n+1 = x_n + F(x,t) ∆t
            self.x = self.x0 + (f_xt * self.delta_t)
            # new x0 and t
            self.x0 = deepcopy(self.x)
            t += self.delta_t

    # IDSM
    def idsm_fx(self):
        # dif. time
        t = 0
        while t < self.sim_time:
            idsm_motor = self.motor_fx()


            [node.activation_fx() for node in self.nodes]


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







# fin
