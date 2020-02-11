
import numpy as np
import matplotlib.pyplot as plt

# "...to prevent the attraction influence to interfere with the velocity
# influence, the component of the attraction influence that is parallel
# to the node's velocity is removed"
# I feel this quite arbitrary (adhoc maybe): TODO: try not removing it

# supposedly it should be everything simultaneous (dN/dt, dmu/dt)

class Agent:
    def __init__(self, dt=0.1\
    , sdim=1, mdim=1\
    , kw=0.0025, kd=1000, kt=1, kr=10):
        self.dt = dt
        self.sdim = sdim
        self.mdim = mdim
        self.kw = kw
        self.kd = kd
        self.kt = kt
        self.kr = kr
        # initial sm state
        self.nodes = []
        self.x = np.concatenate((np.array([0]*sdim), np.array([0]*mdim)))
        self.c = 0
        self.amp_factor = 1

    # for each timestep
    def idsm(self, sx):
        self.update_nodes()
        idsm_mu = self.motor_fx()
        mx = self.x[self.sdim:] + idsm_mu * self.amp_factor
        # mx = (1+self.x[self.sdim:])/2 + idsm_mu * self.amp_factor
        self.velocity = np.concatenate((sx,mx)) - self.x
        self.add_node()
        self.x = np.concatenate((sx,mx))
        ##
        self.c += 1
        if self.c <= 10:
            print("idsm")
            print(self.c)
            print(idsm_mu)
            print(mx)
            print(self.x)
            print(self.velocity)
        # import pdb; pdb.set_trace()
        ##
        return mx

    def train(self, sx, mx):
        self.update_nodes()
        # normalize mx to fit the sm-space [0,1], [sx(-5)=0.03, sx(0)=1]
        mx = (1+mx)/2
        self.velocity = np.concatenate((sx,mx)) - self.x
        self.add_node()
        self.x = np.concatenate((sx,mx))
        print(self.x)

    # creation of nodes
    def add_node(self):
        density = self.density_fx()
        if density < self.kt:
            self.nodes.append(Node(self.x, self.velocity))
            # print("node added, pos={}, vel={}".format(self.x, self.velocity))

    # for debugging
    def node_map(self):
        active_nodes = []
        for node in self.nodes:
            if node.active:
                active_nodes.append([node.position, node.velocity, node.weight])
        if len(active_nodes) > 1:
            for n in enumerate(active_nodes):
                print("{}: {} - {} - {}".format(n[0],n[1][0],n[1][1],n[1][2]))
            import pdb; pdb.set_trace()

    # density fx
    def density_fx(self):
        density = 0
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position)
                density += weight*distance
        # if density == 0:
            # import pdb; pdb.set_trace()
            # print("density=0, number of nodes: {}".format(len(self.nodes)))
        return density
    # weight fx
    def weight_fx(self, Nw):
        if Nw < -2000 or Nw > 2000:
            import pdb; pdb.set_trace()
            return 0
        weight = 2/(1+np.exp(-self.kw*Nw))
        if weight < 0 or weight > 2:
            import pdb; pdb.set_trace()
            return 0
        return weight
    #distance fx
    def distance_fx(self, Np):
        node_dist = np.linalg.norm(Np-self.x)
        if node_dist > 0.15:
            # print("node dist: {}".format(node_dist))
            # import pdb; pdb.set_trace()
            return 0
        distance = 2/(1+np.exp(self.kd*node_dist**2))
        return distance

    # maintenance of nodes
    def update_nodes(self):
        for node in self.nodes:
            d = self.distance_fx(node.position)
            r = self.kr*d
            node.weight += (-1+r)*self.dt
            node.activation_fx(self.dt)

    # motor responses
    def motor_fx(self):
        ix = self.influence_fx()
        dx = self.density_fx()
        if dx == 0:
            return 0
        dmu = (ix/dx)#*self.dt
        return dmu
    # velocity + attraction
    def influence_fx(self):
        influence = np.array([0.]*self.mdim)
        nodes = 0
        sweights = 0
        sdistances = 0
        svelocities = 0
        sattractions = 0
        for node in self.nodes:
            if node.active:
                weight = self.weight_fx(node.weight)
                distance = self.distance_fx(node.position)
                # velocity component
                velocity = node.velocity[self.sdim:]
                # attraction component
                att = node.position[self.sdim:] - self.x[self.sdim:]
                normed_vel = np.linalg.norm(velocity)
                if normed_vel == 0:
                    attraction = att
                else:
                    attraction = att - att*normed_vel
                # weighted motor influence
                influence += (weight*distance*(velocity+attraction))
                nodes += 1
                sweights += weight
                sdistances += distance
                svelocities += velocity
                sattractions += attraction
                # import pdb; pdb.set_trace()
        #print(self.x)
        #print("{},{},{},{},{},{}".format(nodes,sweights,sdistances,svelocities,sattractions,influence))
        #import pdb; pdb.set_trace()
        return influence


class Node:
    def __init__(self, position, velocity, weight=0):
        self.position = position
        self.velocity = velocity
        self.weight = weight
        self.t2a = 10
        self.active = False

    def activation_fx(self, dt):
        if self.t2a > 0:
            self.t2a -= dt
        else:
            self.active = True







    # move
    # def move(self, sx):
    #     vx = self.velocity_fx()
    #     ax = self.attraction_fx()
    #     dx = self.density_fx()
    #     self.m = (vx+ax)/dx
    #     import pdb; pdb.set_trace()
    # # velocity fx
    # def velocity_fx(self):
    #     velocity = 0
    #     for node in self.nodes:
    #         weight = self.weight_fx(node.weight)
    #         distance = self.distance_fx(node.position)
    #         Nv_mu = node.velocity[self.sdim:]
    #         velocity += weight*distance*Nv_mu
    #     return velocity
    # # attraction fx
    # def attraction_fx(self):
    #     attraction = 0
    #     for node in self.nodes:
    #         weight = self.weight_fx(node.weight)
    #         distance = self.distance_fx(node.position)
    #         a = node.position[self.sdim:] - self.x[self.sdim:]
    #         gamma = self.gamma_fx(a, node.velocity[self.sdim:])
    #         attraction += weight*distance*gamma
    #     return attraction
    # remove velocity component for attraction
    # def gamma_fx(self, a, Nv_mu):
    #     gamma = a - a*Nv_mu/np.linalg.norm(Nv_mu)
    #     return gamma




























##
