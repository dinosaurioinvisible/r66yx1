import numpy as np
import math
import matplotlib.pyplot as plt
from copy import deepcopy
from tqdm import tqdm

class Agent:

    def __init__(self, m=[], s=[]\
    ,nodes=[]\
    ,delta_t=0.01\
    ,kw=0.0025, kd=1000, kt=1, kr=10.0\
    ,sim_time=100):
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
        # internal
        self.motor_dims = len(m)
        self.sensor_dims = len(s)
        self.x = np.concatenate((self.m, self.s))
        self.density = 0.0
        self.velocity = np.array([0.0]*len(self.x))
        self.attraction =  np.array([0.0]*len(self.x))[:self.motor_dims]
        # records
        self.motor_records = [self.m]
        self.records = []

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
            weight = 2/(1+math.exp(-self.kw*Nw))
        except:
            weight=0
        return weight

    # idsm influence
    def mu_fx(self):







    # density function
    # density_fx = summatory_N(weight_fx * distance_fx)
    def density_fx(self):
        #self.density = 0.0
        density=0
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position, self.x)
                #self.density += (weight*distance)#*self.delta_t
                density += weight*distance
        #self.density*=self.delta_t
        return density*self.delta_t


























#fin
