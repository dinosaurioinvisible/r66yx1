
import numpy as np
import geometry
import sensors
import evol_net
import tree
# import motor
# import body

# object - symbol - concept : world x - SM input - perception
# the normative (cognitive?) domain is made of perceptions from experiences
# meaning is the association of some trait to another (link between exps)

# Theoretical SM loop of interactions
# de/dt = E(e,p)    # environment: environment & body
#
# ds/dt = S(e,a)    # sensors: environment & neural dynamics
# da/dt = A(a,s)    # neural dynamics: sensors & neural dynamics
# dm/dt = M(a)      # motors: neural dynamics
#
# dp/dt = B(p,m,e)  # body: body & motors & environment

class Agent:
    def __init__(self, x=100, y=100, o=0\
    , energy=100\
    , r=2.5, max_speed=5\
    , feed_range=5, feed_rate=5):
        # init
        self.energy = energy
        self.x = x; self.y = y; self.o = o
        self.r = r; self.max_speed = max_speed
        self.wheels_sep = r
        self.velocity = 0
        self.feed_range = feed_range
        self.feed_rate = feed_rate
        self.com = np.random.rand()
        # modules
        self.sensors = sensors.Sensors()
        self.net = evol_net.RNN()
        # SM array
        self.state = None
        # for animation
        self.ps = [self.sensors.ray_length, self.sensors.ir_angles, self.sensors.olf_range, self.sensors.olf_angles, self.sensors.aud_range/2, self.sensors.aud_angles]
        self.states = []
        self.positions = []

    def act(self, objects):
        self.energy -= 1
        # sm state = [ir1, ir2, olf, aud1, aud2, e]
        self.state = self.sensors.read_env(self.x, self.y, self.o, self.r, objects)
        self.state.append(self.energy)
        self.states.append(self.state)
        self.positions.append([self.x, self.y, self.o])
        # controller
        lw, rw, com = self.net.action(self.state)
        self.communicate(com)
        self.move(lw, rw)
        self.feed(objects)

    def move(self, lw, rw):
        # update x, y, or
        lw = lw*self.max_speed
        rw = rw*self.max_speed
        self.velocity = (lw+rw)/2
        dx = self.velocity * np.cos(self.o)
        dy = self.velocity * np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update
        if self.energy > 0:
            self.x += dx
            self.y += dy
            self.o += do
            self.o = geometry.force_angle(self.o)
            self.energy -= 1

    def feed(self, objects):
        # feed if tree is near
        trees = [x for x in objects if type(x)==tree.Tree]
        for tx in trees:
            dist = np.linalg.norm(np.array([tx.x,tx.y])-np.array([self.x,self.y]))
            if dist <= self.feed_range:
                feed_rate = self.feed_rate*(1/dist)
                e = tx.feeding_fx(feed_rate)
                self.energy += e

    def communicate(self, com):
        # ultra simple for now
        self.com = com



































        ##
