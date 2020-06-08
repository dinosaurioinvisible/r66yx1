
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import _genotype
import _sensors
import _comchannel
import _nnet
import _data

class Agent:
    def __init__(self, x=100, y=100, o=0\
    , genotype=None):
        # allocation
        self.x = x; self.y = y; self.o = o
        # get genotype
        if genotype:
            self.genotype = genotype
        else:
            self.genotype = _genotype.Genotype()
        # agent features
        self.e = self.genotype.energy
        self.r = self.genotype.r
        self.max_speed = self.genotype.max_speed
        self.wheels_sep = self.genotype.wheels_sep
        self.feeding_rate = self.genotype.feeding_rate
        self.feeding_range = self.genotype.feeding_range
        self.feeding_theta = self.genotype.feeding_theta
        self.define_body_area()
        self.define_feeding_area()
        # init modules
        self.sensors = _sensors.Sensors(self.genotype)
        self.comchannel = _comchannel.Com(self.genotype)
        self.com_out = self.comchannel.initial_out()
        self.net = _nnet.RNN(self.genotype)
        self.data = _data.Data()


    def update_in(self, walls, trees, xagents):
        # save starting conditions
        self.data.save_ax(self.x, self.y, self.o, self.area, self.feeding_area, self.e)
        # update sensors info and pass info to the nnet        
        self.sensors.define_sensors_area(self.x, self.y, self.o, self.r)
        self.comchannel.define_com_area(self.x, self.y)
        env_info = self.sensors.read_environment(walls,trees,xagents)
        com_info = self.comchannel.update_in(xagents)
        sm_info = env_info+[self.e]+com_info
        # net_in(sm_info) = [vs1, vs2, o, e, c1, c2, c3]
        self.lw, self.rw, com = self.net.update(sm_info)
        self.com_out = self.comchannel.output_signal(com)
        # save data
        self.data.save_sensors(self.sensors.vs_sensors, self.sensors.olf_sensor, env_info)
        self.data.save_com(self.comchannel.com_area, com_info, self.com_out)
        self.data.save_nnet(sm_info, self.net.e_states, self.net.h_states)

    def move_fx(self):
        # update dx, dy, do
        lw = self.lw*self.max_speed
        rw = self.rw*self.max_speed
        vel = (lw+rw)/2
        self.dx = vel + np.cos(self.o)
        self.dy = vel + np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update x, y, o and body area
        self.x += self.dx
        self.y += self.dy
        self.o = geometry.force_angle(self.o+do)

    def update_location(self, world_objects):
        # update position
        self.define_body_area()
        self.check_overlap(world_objects)
        self.define_feeding_area()

    def feed_fx(self, trees):
        # check if tree is in feeding area for this agent
        trees_lx = []
        for tx in trees:
            feed = 0
            if self.feeding_area.intersects(tx.area):
                feed = 1
            trees_lx.append(feed)
        return trees_lx

    def update_energy(self, tx_ax):
        # feed according to number of agents near
        for n in tx_ax:
            e = self.feeding_rate**n * n
            self.e += e
        self.e -= 1
        if self.e <= 0:
            self.e = 0
        # save data outputs
        self.data.save_feeding(tx_ax)

    def define_body_area(self):
        # define body
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

    def check_overlap(self, world_objects):
        # check for overlappings
        for ox in world_objects:
            if self.area.intersects(ox.area):
                self.x -= self.dx
                self.y -= self.dy
                self.e -= 10
                self.define_body_area()
                break

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
        arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
        # get arc coordinates and create polygon
        arc_x = fx + self.feeding_range*np.cos(arc_angles)
        arc_y = fy + self.feeding_range*np.sin(arc_angles)
        f_coords = [(fx,fy)]
        [f_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        self.feeding_area = Polygon(f_coords)


















    #
