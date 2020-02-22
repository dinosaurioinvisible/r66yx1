
import numpy as np
import world
import sensors
import evol_net
# import motor
# import body

# object - symbol - concept : world x - SM input - perception
# the normative (cognitive?) domain is made of perceptions from experiences
# meaning is the association of some trait to another (link between exps)

#

# Theoretical SM loop of interactions
# de/dt = E(e,p)    # environment: environment & body
#
# ds/dt = S(e,a)    # sensors: environment & neural dynamics
# da/dt = A(a,s)    # neural dynamics: sensors & neural dynamics
# dm/dt = M(a)      # motors: neural dynamics
#
# dp/dt = B(p,m,e)  # body: body & motors & environment

class Agent:
    def __init__(self, energy=100\
    , x=100, y=100, or=0\
    , r=2.5, speed=5):
        # init
        self.energy = energy
        self.x = x
        self.y = y
        self.or = or
        self.r = r
        self.speed = speed
        self.wheels_sep = r
        self.sensors = sensors.Sensors()
        self.nnet = nnet.Net()
        # SM array
        self.sm = []

    def act(self, objects):
        env_input = self.sensors.read_env(self.x, self.y, self.r, self.or, objects)
        self.move(??)


    def move(self):
        # update x, y, or
        lw, rw = self.net.action(??)
        lw = lw*self.speed
        rw = rw*self.speed
        vel = (lw+rw)/2
        dx = vel*np.cos(self.or)
        dy = vel*np.sin(self.or)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update
        self.x += dx
        self.y += dy
        self.o += do
        self.o = geometry.force_angle(self.or)





































        ##
