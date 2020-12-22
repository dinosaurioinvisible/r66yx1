
import numpy as np
import simgeometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import simgenotype
import simsensors
import simnet

class Agent:
    def __init__(self, x=100, y=100, o=0\
    , genotype=None):
        # allocation
        self.x = x; self.y = y; self.o = o
        # features from genotype
        if genotype:
            self.genotype = genotype
        else:
            self.genotype = simgenotype.Genotype()
        self.initial_energy = self.genotype.energy
        self.energy = self.genotype.energy
        self.r = self.genotype.r
        self.max_speed = self.genotype.max_speed
        self.wheels_sep = self.genotype.wheels_sep
        self.feeding_range = self.genotype.feeding_range
        self.feeding_theta = self.genotype.feeding_theta
        # init modules
        self.sensors = simsensors.Sensors(s_points=self.genotype.s_points, vs_do=self.genotype.vs_do, vs_range=self.genotype.vs_range, vs_theta=self.genotype.vs_theta, olf_range=self.genotype.olf_range, olf_theta=self.genotype.olf_theta, aud_do=self.genotype.aud_do, aud_range=self.genotype.aud_range, aud_theta=self.genotype.aud_theta)
        self.net = simnet.RNN(n_input=self.genotype.n_input, n_hidden=self.genotype.n_hidden, n_output=self.genotype.n_output, upper_t=self.genotype.ut, lower_t=self.genotype.lt, veto_t=self.genotype.vt, W=self.genotype.W, V=self.genotype.V)
        # internal
        self.define_body_area()
        self.define_feeding_area()
        self.sm_state = None
        self.com = 0
        # save data
        self.data = {}
        self.data[0] = [self.x, self.y, self.o, self.energy, self.area, self.feeding_area, self.sensors.sensors, self.sensors.states, self.net.states]
        self.t = 1

    def update(self, objects):
        # if alive:
        if self.energy == 0:
            return
        # act
        self.energy -= 1
        # sensory info
        self.sensors.read_env(self.x, self.y, self.o, self.r, objects)
        energy = self.energy/self.initial_energy
        self.sm_state = self.sensors.states+[energy]
        # controller response:
        lw, rw, com = self.net.update(self.sm_state)
        self.com_signal(com)
        self.move(lw, rw, objects)
        # save data [x,y,o, body, feeding area, sensors, net]
        self.data[self.t] = [self.x, self.y, self.o, self.energy, self.area, self.feeding_area, self.sensors.sensors, self.sensors.states, self.net.states]
        self.t += 1

    def move(self, lw, rw, objects):
        # compute dx, dy, do
        lw = lw*self.max_speed*(self.energy/1000)
        rw = rw*self.max_speed*(self.energy/1000)
        vel = (lw+rw)/2
        dx = vel + np.cos(self.o)
        dy = vel + np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update
        self.x += dx
        self.y += dy
        self.o = simgeometry.force_angle(self.o+do)
        self.define_body_area()
        # check for bouncings
        for ox in objects:
            if self.area.intersects(ox.area):
                self.x -= dx*3
                self.y -= dy*3
                self.energy -= 10
                self.define_body_area()
        # check if still alive
        if self.energy <= 0:
            self.energy = 0
            return

    def define_body_area(self):
        # define body
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

    def define_feeding_area(self):
        # define feeding area
        fx = self.x + self.r*np.cos(self.o)
        fy = self.y + self.r*np.sin(self.o)
        arc_start = self.o - np.radians(self.feeding_theta/2)
        arc_end = self.o + np.radians(self.feeding_theta/2)
        # force counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # get arc angle points
        arc_points = np.linspace(arc_start, arc_end, self.genotype.s_points)
        arc_angles = np.array([simgeometry.force_angle(oi) for oi in arc_points])
        # get arc coordinates and create polygon
        arc_x = fx + self.genotype.olf_range*np.cos(arc_angles)
        arc_y = fy + self.genotype.olf_range*np.sin(arc_angles)
        f_coords = [(fx,fy)]
        [f_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        self.feeding_area = Polygon(f_coords)

    def com_signal(self, com):
        self.com = com










        #
