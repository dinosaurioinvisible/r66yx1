
# SM-space : all possible sensory and motor states of an agent
# 1 sensor + 1 motor : 2D SM-space
# 3 sensor + 5 motor : 8D SM-space

# SM-state : each point in the SM-space

# SM-medium : defines the next motor state for each SM-state
# deformable : mapping changes in time in a state-dependent manner
    # plastic : deformations are conserved
    # elastic : deformations tend to recover their original shape
# iterant : deformations made by trajectories reinforce their pathways

#####################

# the IDSM operates by developing and mantaining a history
# of SM-dynamics. This history takes the form of many "nodes"
# where each node describes the SM-velocity at a SM-state
# at some point in the past

# Node : SM-velocity at a SM-state in time=x

# As the agent behaves, and its SM-state changes, nodes are added
# such that a record is constructed of how sensors and motors have
# changed for variuous SM-states during the system's history

# t=1 : N1=SM-state 1, t=2 : N2=SM-state 2, ... , t=n : Nn=SM-state n

# These are used in a continuous dynamical framework to determine
# future motor-actions such that when a familiar sm-state is encountered
# the IDSM produces behaviour that is similar to the behavior that was
# performed when the agent was previously in a similar situation

####################

# More formaly:
# node = (position, velocity, weight)
# position : SM-state associated with the node
# velocity : velocity of SM-change
# weight : weight of the node
N = [Np, Nv, Nw]

####################

# TABLE 1

#TODO

# x : current SM-state
x =

# Np : SM-state associated with N
Np =
# Nv : SM-velocity indicated by node N
Nv =
# Nw : weight of node N
Nw =

#TODO

# d(x,y) : distance function between 2 SM-states
def distance(self, x, y):
    distance = 0
    x = 0
    y = 0
    distance = x - y
    return distance

# w(Nx) : influence of the weight of node N
# phi(y) : function for the local density of nodes of SM-state y

##################

# creation of nodes

# More formaly, when a new node is created,
# Np : current SM-state
# Nv : current rate of change in each SM-dimension
# Nw = 0 (neutral, not ineffectual)
# Np and Nv are calculated in normalized SM-space
# where all sensor and motor values go between 0 and 1
def create_node(self):
    new_Np = self.x[0]
    new_Nv = self.x[1]
    new_Nw = 0
    new_node = [new_Np, new_Nv, new_Nw]
    return new_node

# new nodes are only added when density is lower than kt = 1
self.kt = 1
# constants for node creation
self.kd = 1000
self.kw = 0.0025

# density : function to know how many nodes and how heavy they are
def density(self):
    density = 0
    for node in self.nodes:
        Np = node[0]
        # a) how many nodes there are near to SM-state x
        xdistance = 2/1+np.exp(self.kd*(np.absolute(Np-self.x))**2)
        Nw = node[2]
        # b) how heavily weighted those nodes are
        xweight = 2/(1+np.exp(-self.kw*Nw))
        density += xweight*xdistance

# compare values and eventually create node
def decide_create_node:
    if self.density < self.kt:
        self.create_node()

##################

# maintenance of nodes dNw/dt

# after creation the weight of the node changes according to:
# dNw/dt = -1+reinforcement
# reinforcement(N, x) = 10*xdistance(Np, x)
def maintenance(self):
    xdistance = self.distance(self.nodes[0], self.x)
    self.nodes[-1][2] = -1 + (10*xdistance)

##################

# Nodes influence the motor state

# after 10 time units nodes are activated, added to the pool of nodes
# velocity
velocity = sum([xweight*xdistance*Nv_mu for n in range(len(nodes))])

# attractive force
aforce = a - (a * Nv/np.absolute(Nv))

# attraction
attraction = sum([xweight*xdistance*aforce_mu])
