
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import sensors
import evol_net

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
    , genotype=None\
    , energy=2000):
        # init
        self.x = x; self.y = y; self.o = o
        # from genotype
        self.genotype = genotype
        self.energy = self.genotype.energy
        self.r = self.genotype.r
        self.max_speed = self.genotype.max_speed
        self.wheels_sep = self.genotype.r
        self.feed_range = self.genotype.feed_range
        self.feed_rate = self.genotype.feed_rate
        self.com = np.random.rand()
        # modules
        self.sensors = sensors.Sensors(olf_angle=self.genotype.olf_angle, olf_range=self.genotype.olf_range, ir_angle=self.genotype.ir_angle, ray_length=self.genotype.ray_length, n_rays=self.genotype.n_rays, beam_spread=self.genotype.beam_spread, aud_angle=self.genotype.aud_angle, aud_range=self.genotype.aud_range)
        self.net = evol_net.RNN(n_input=self.genotype.n_in, n_hidden=self.genotype.n_hidden, n_output=self.genotype.n_out, upper_t=self.genotype.ut, lower_t=self.genotype.lt, veto_t=self.genotype.vt, W=self.genotype.W, V=self.genotype.V)
        self.genotype.W = self.net.W
        self.genotype.V = self.net.V
        # SM array
        self.state = None
        # for animation
        self.ps = [self.sensors.ray_length, self.sensors.ir_angles, self.sensors.olf_range, self.sensors.olf_angles, self.sensors.aud_range/2, self.sensors.aud_angles]
        self.states = []
        self.positions = []
        self.feeding_states = []

    def act(self, objects):
        self.energy -= 1
        # sm state = [ir1, ir2, olf, aud1, aud2, e]
        self.state = self.sensors.read_env(self.x, self.y, self.o, self.r, objects)
        self.state.append(self.energy)
        self.states.append(self.state)
        self.positions.append([self.x, self.y, self.o])
        # controller
        lw, rw, com = self.net.action(self.state)
        self.com = com
        self.move(lw, rw, objects)
        self.feeding = False
        if self.state[2] > 0:
            self.feed(objects)
        self.feeding_states.append(self.feeding)


    def move(self, lw, rw, objects):
        # update x, y, or
        lw = lw*self.max_speed
        rw = rw*self.max_speed
        velocity = (lw+rw)/2
        dx = velocity * np.cos(self.o)
        dy = velocity * np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update
        # print("from x={}, y={}, o={}".format(self.x,self.y,self.o))
        if self.energy > 0:
            self.x += dx
            self.y += dy
            self.o = geometry.force_angle(self.o+do)
            self.energy -= 1
            self.bouncing_fx(dx, dy, objects)
        # print("to x={}, y={}, o={}".format(self.x,self.y,self.o))

    def bouncing_fx(self, dx, dy, objects):
        # so objects don't traspass each other
        pos = Point(self.x, self.y)
        body = pos.buffer(self.r)
        contact = False
        for w in objects["walls"]:
            wall = LineString([(w.xmin,w.ymin),(w.xmax,w.ymax)])
            if body.intersects(wall):
                contact = True
        round_objects = objects["trees"]+objects["agents"]
        for obj in round_objects:
            obj_center = Point(obj.x, obj.y)
            obj_body = obj_center.buffer(obj.r)
            if body.intersects(obj_body):
                contact = True
        if contact:
            self.x -= dx*3
            self.y -= dy*3
            self.energy -= 10

    def feed(self, objects):
        # feed if tree is near
        trees = objects["trees"]
        for tx in trees:
            dist = np.linalg.norm(np.array([tx.x,tx.y])-np.array([self.x,self.y])) - self.r - tx.r
            if dist <= self.feed_range:
                self.feeding = True
                feed_rate = self.feed_rate * (1/np.exp(dist/self.feed_range))
                other_agents = objects["agents"]
                e = tx.feeding_fx(feed_rate, other_agents)
                self.energy += e






































        ##
