
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

# TODO
# error grows with less energy

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
        self.sensors = sensors.Sensors(s_points=self.genotype.s_points, ir_angle=self.genotype.ir_angle, ray_length=self.genotype.ray_length, beam_spread=self.genotype.beam_spread, olf_angle=self.genotype.olf_angle, olf_range=self.genotype.olf_range, aud_angle=self.genotype.aud_angle, aud_range=self.genotype.aud_range)
        self.net = evol_net.RNN(n_input=self.genotype.n_in, n_hidden=self.genotype.n_hidden, n_output=self.genotype.n_out, upper_t=self.genotype.ut, lower_t=self.genotype.lt, veto_t=self.genotype.vt, W=self.genotype.W, V=self.genotype.V)
        self.genotype.W = self.net.W
        self.genotype.V = self.net.V
        # SM state = [ir1, ir2, olf, aud1, aud2, e]
        self.state = None
        # data
        self.states = []
        self.positions = []
        self.body_states = []
        self.feeding_states = []

    def act(self, objects):
        # if "alive"
        if self.energy > 0:
            self.energy -= 1
            # sensory information
            self.state = self.sensors.read_env(self.x, self.y, self.o, self.r, objects)
            self.state.append(self.energy)
            # controller response
            lw, rw, com = self.net.action(self.state)
            self.com = com
            self.move(lw, rw, objects)
            # feed
            self.feed(objects)
        else:
            self.energy = 0
        # record data: internal states
        self.states.append(self.state)
        # record data: body and feeding
        self.positions.append([self.x, self.y, self.o])
        self.feeding_states.append(self.feeding)

    def move(self, lw, rw, objects):
        # compute dx, dy, do
        lw = lw*self.max_speed
        rw = rw*self.max_speed
        vel = (lw+rw)/2
        dx = vel * np.cos(self.o)
        dy = vel * np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update
        self.x += dx
        self.y += dy
        self.o = geometry.force_angle(self.o+do)
        self.energy -= 1
        self.bouncing_fx(dx, dy, objects)

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
        # "mouth" location
        fx = self.x + self.r*np.cos(self.o)
        fy = self.y + self.r*np.sin(self.o)
        # feeding area: arc
        arc_start = self.o - np.radians(self.feeding_angle/2)
        arc_end = self.o + np.radians(self.feeding_angle/2)
        # force counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # get arc angle points and force angles
        arc_points = np.linspace(arc_start, arc_end, self.genotype.s_points)
        arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
        # get the arc coordinates and create polygon
        arc_x = fx + self.olf_range*np.cos(arc_angles)
        arc_y = fy + self.olf_range*np.sin(arc_angles)
        feeding_coords = [(fx,fy)]
        [feeding_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        feeding_area = Polygon(feeding_coords)
        # check for trees to feed
        feeding = False
        trees = objects["trees"]
        for tree in trees:
            if feeding_area.intersects(tree):
                feeding = True
                feed_rate = self.feed_rate * (1/np.exp(dist/self.feed_range))


        self.feeding_states.append([feeding_area, feeding])

    def feed(self, objects):
        self.feeding = False
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
