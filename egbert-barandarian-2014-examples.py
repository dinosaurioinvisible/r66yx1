
# examples from paper
import numpy as np
import matplotlib.pyplot as plt

x
nodes = []

# weight function
# kw = 0.0025
# weight_fx = 2/1+np.exp(-kw*Nw)
def weight_fx(Nw, kw=0.0025):
    weight = 2/1+np.exp(-kw*Nw)
    return weight

# distance function
# kd = 1000
# distance_fx = 2/1+np.exp(kd*(Np-x)**2)
def distance_fx(x, Np, kd=1000):
    distance = 2/1+np.exp(kd*(Np-x)**2)
    return distance

# density function
# density_fx = summatory_N(weight_fx * distance_fx)
def density_fx(x, nodes):
    density = 0
    for node in nodes:
        Nw = node[2]
        Np = node[0]
        weight = weight_fx(Nw)
        distance = distance_fx(x, Np)
        density += weight*distance
    return density

# creation of nodes
# if density fx < kt = 1
def add_node_fx(x, nodes, kt=1):
    density = density_fx(x, nodes)
    if density < kt:
        # change from last node to current position
        velocity = x-nodes[-1]
        weight = 0
        nodes.append([x, velocity, weight])

# attraction function
# attraction_fx = (Np - x) - (Np-x)*(Nv/np.absolute(Nv))
def attraction_fx(x, Np, Nv):
    attraction = (Np-x)-(Np-x)*(Nv/np.absolute(Nv))
    return attraction

# IDSM motor influence function
# d_mu/dt = 1/density_fx * summatory( weight_fx * distance_fx * (velocity + attraction_fx) )
def idsm_fx(x, nodes):
    density = density_fx(x, nodes)
    motor_influence = 0
    for node in nodes:
        weight = weight_fx(Nw)
        distance = distance_fx(x, Np)
        # velocity : Nv
        Nv = node[1]
        attraction = attraction_fx(x, Np, Nv)
        motor_influence += weight*distance*(Nv+atraction)
    idsm_influence = (1/density)*motor_influence
    return idsm_influence

# node's reinforcement function
# r(N,x) = 10 * d(Np,x)
def reinforcement_fx(x, Np):
    xdistance = distance_fx(x, Np)
    reinforcement = 10*xdistance
    return reinforcement

# maintenance of nodes (updating of nodes' weights)
# dNw/dt = -1 + r(N,x)
def maintenance_fx(x, nodes):
    for node in nodes:
        Np = node[0]
        reinforcement = reinforcement_fx(x, Np)
        updated_weight = -1+reinforcement
        node[2] = updated_weight
