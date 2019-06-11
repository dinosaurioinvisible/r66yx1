
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
x = 0

# Np : SM-state associated with N
Np = 0
# Nv : SM-velocity indicated by node N
Nv = 0
# Nw : weight of node N
Nw = 0

#TODO

# d(x,y) : distance function between 2 SM-states
def distance_fx(self, x, y):
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
    self.nodes.append(new_node)

# new nodes are only added when density is lower than kt = 1
self.kt = 1
# constants for node creation
self.kd = 1000
self.kw = 0.0025

# density : function to know how many nodes and how heavy they are
# (eq. 1)
def density_fx(self):
    density = 0
    for node in self.nodes:
        Np = node[0]
        # a) how many nodes there are near to SM-state x
        # (eq. 3)
        xdistance = 2/1+np.exp(self.kd*(np.absolute(Np-self.x))**2)
        Nw = node[2]
        # b) how heavily weighted those nodes are
        # (eq. 2)
        xweight = 2/(1+np.exp(-self.kw*Nw))
        density += xweight*xdistance
    return density

# compare values and eventually create node
def decide_create_node(self):
    density = self.density_fx()
    if density < self.kt:
        self.create_node()

##################

# Maintenance of nodes dNw/dt

# after creation the weight of the node changes according to:
# dNw/dt = -1+reinforcement
# reinforcement(N, x) = 10*xdistance(Np, x)
# maintenance (eq. 4 & eq. 5)
def maintenance_fx(self):
    xdistance = self.distance(self.nodes[0], self.x)
    self.nodes[-1][2] = -1 + (10*xdistance)

##################

# Nodes influence the motor state

# after 10 time units nodes are activated, added to the pool of nodes
# influence of a node upon the motors can be broken down into 2 factors:

# a) velocity factor : just the motor components of the Nv vector
# velocity (eq. 6)
def velocity(self):
    velocity = 0
    for node in self.nodes:
        Nw = node[2]
        xweight = 2/(1+np.exp(-self.kw*Nw))
        Np = node[0]
        xdistance = 2/1+np.exp(self.kd*(np.absolute(Np-self.x))**2)
        # just the motor components of the Nv Vector
        Nv = node[1]
        #TODO
        Nv_motor = Nv
        velocity += xweight*xdistance*Nv_motor
    return velocity

# b) attraction factor : a force that draws the system towards the node
# so the system tends to move towards regions of familiar SM-space
# (i.e. higher density of nodes)
# to prevent the attraction influence from interfering with the
# velocity influence, the attraction component that is parallel to the
# node's velocity vector is removed

# attraction (eq. 8)
def attraction_fx(self):
    attraction = 0
    for node in self.nodes:
        Nw = node[2]
        xweight = 2/(1+np.exp(-self.kw*Nw))
        Np = node[0]
        xdistance = 2/1+np.exp(self.kd*(np.absolute(Np-self.x))**2)
        # just ortogonal attraction (eq. 7)
        a = (Np - x)
        Nv = node[1]
        ortogonal_attraction = a - a*(Nv/np.absolute(Nv))
        # TODO
        ortofonal_attraction_motor = ortogonal_attraction
        attraction += xweight*xdistance*ortofonal_attraction_motor
    return attraction


# Total influence of the IDSM upon the motor-state are scaled
# by the node's weight
# by [node's] distance to the SM-state
# and summed before being scaled by the density of the nodes
# at current SM-state
# total IDSM influence
# dmotor/dt = (V(x) + A(x))/phi(x) (eq. 9) : (velocity + attraction)/density
def idsm_fx(self):
    idsm_influence = 0
    for node in self.nodes:
        Np = node[0]
        Nv = node[1]
        Nw = node[2]
        xweight = 2/(1+np.exp(-self.kw*Nw))
        xdistance = 2/1+np.exp(self.kd*(np.absolute(Np-self.x))**2)
        # TODO:
        velocity_motor = Nv
        # TODO:
        attraction_motor = (Np-self.x) - (Np-self.x)*(Nv/np.absolute(Nv))
        # TODO:
        idsm_influence += xweight*xdistance*(velocity_motor+attraction_motor)
    density = self.density_fx()
    idsm_influence = idsm_influence*density

##################################

# Experiments and results

# IDSM controlled robot
# training phase : robot first driven to perform a specific behaviour
# free action phase : IDSM has control, recreating patterns of behaviour

# the robot is embedded in a 1D environment with a point of light at the origin
# it has a single motor to move forward pr backwards
# and a single non-directional light sensor
# activation of the sensor : s = 1/1+x**2
# the robot has 1 sensor and 1 motor so its SM-space is 2D

###############################

self.nodes = []
# initial position
self.x = -2.5

# for the first 20 time units the robot is controlled by a training controller
for t in range(20):
    # motor state is set according to a time-dependent equation
    # so the robot goes back and forth but remains on one side of the light
    motor_state = cos(t/2)/2
    # robot's velocity = state of its motor (within -1 and 1) (normalized?)
    velocity = motor_state
    self.x += motor_state
    weight = 0
    # as the robot moves through the training trajectory IDSM add nodes
    # describing the change in SM-state for experienced SM-states
    self.nodes.append([self.x, velocity, weight])

# at t=20 traning phase ends and IDSM takes control
for t in range(20,1000):
    
    self.decide_create_node()
