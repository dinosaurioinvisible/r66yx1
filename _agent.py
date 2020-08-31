
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import _genotype
import _sensors
import _axcom
import _rnn
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
        self.de_dt = self.genotype.de_dt
        self.e_in = self.genotype.e_in
        self.r = self.genotype.r
        self.max_speed = self.genotype.max_speed
        self.wheels_sep = self.genotype.wheels_sep
        self.feeding_rate = self.genotype.feeding_rate
        self.feeding_range = self.genotype.feeding_range
        self.feeding_theta = self.genotype.feeding_theta
        self.com_len = self.genotype.com_len
        self.attn = self.genotype.attn
        self.define_body_area()
        self.define_feeding_area()
        # init modules
        self.sensors = _sensors.Sensors(self.genotype)
        self.net = _rnn.RNN(self.genotype)
        if self.com_len > 0:
            self.axcom = _axcom.Com(self.genotype, self.x, self.y)
        self.data = _data.Data()


    def update_in(self, walls, trees, xagents):
        # save starting conditions
        self.data.save_ax(self.x, self.y, self.o, self.area, self.feeding_area, self.e)
        # update sensors and get env info
        self.sensors.define_sensors_area(self.x, self.y, self.o, self.r)
        vs_info, olf_info = self.sensors.read_environment(walls,trees,xagents)
        # communicative input (if active)
        com_info = np.array([0.]*self.com_len)
        if self.com_len > 0:
            self.axcom.define_com_area(self.x, self.y)
            cagents = [xag for xag in xagents if xag.e>0]
            com_info = self.axcom.update_in(cagents)
        # energy input (if active)
        e_info = np.array([0.]*self.e_in)
        if self.e_in > 0:
            ev = 0 if self.e > 1000 else 1-(self.e*self.de_dt/1000)**1.5
            e_info += ev
        # define the sm vector: np array(vs1, ..,vsn, olf, e, c1, ...,cn)
        sm_info = np.concatenate((vs_info,olf_info,e_info,com_info))
        # get response from controller
        self.lw, self.rw, vs_attn, olf_attn, com_vals = self.net.update(np.array(sm_info))
        # attn (if active)
        if self.attn:
            self.sensors.attention_fx(olf_attn, vs_attn)
        # comm output (if active)
        if self.com_len > 0:
            self.axcom.update_out(com_vals)
        # save data
        self.data.save_sensors(self.sensors.vs_sensors, self.sensors.olf_sensor, vs_info, olf_info, e_info, com_info)
        self.data.save_nnet(self.net.e_states[-1], self.net.h_states[-1], vs_attn, olf_attn, com_vals)
        if self.com_len > 0:
            self.data.save_com(self.axcom.com_area, self.axcom.com_out)

    def move_fx(self):
        # compute changes in location (force movement if 0)
        lw = self.lw*self.max_speed + np.random.uniform(-0.1,0.1)
        rw = self.rw*self.max_speed + np.random.uniform(-0.1,0.1)
        vel = (lw+rw)/2
        # update dx, dy, do
        self.dx = vel * np.cos(self.o)
        self.dy = vel * np.sin(self.o)
        do = np.radians((lw-rw)/self.wheels_sep)
        # update x, y, o and body area
        self.x += self.dx
        self.y += self.dy
        self.o = geometry.force_angle(self.o+do)

    def update_location(self, bounds, walls, trees, xagents):
        # call location fxs
        self.define_body_area()
        self.check_overlap(bounds, walls, trees, xagents)
        self.define_feeding_area()

    def feed_fx(self, trees):
        # check if there are trees in feeding area
        trees_lx = [1 if self.feeding_area.intersects(tx.area) else 0 for tx in trees]
        return np.array(trees_lx)

    def update_energy(self, ag_ax_tx):
        # energy - dedt - damage
        de = -(self.de_dt+self.damage)
        # feed according to number of agents near
        for n_ags in ag_ax_tx:
            de += self.feeding_rate*(n_ags**2)
        self.e += de
        # save data outputs
        self.data.save_feeding(ag_ax_tx, de)
        if self.e < 0:
            self.e = 0

    def define_body_area(self):
        # define body
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

    def check_overlap(self, bounds, inner_walls, trees, xagents):
        # acummulative damage per timestep
        self.damage = 0
        # keep within bounds
        while bounds.contains(self.area) == False:
            self.x -= self.dx
            self.y -= self.dy
            self.damage += 3
            self.define_body_area()
        # no damage from trees
        for tx in trees:
            if self.area.intersects(tx.area):
                self.x -= self.dx
                self.y -= self.dy
                self.define_body_area()
                break
        # no damage from other agents
        for xa in xagents:
            if self.area.intersects(xa.area):
                self.x -= self.dx
                self.y -= self.dy
                self.define_body_area()
                break
        # check for overlappings with objects
        # other_world_objects = inner_walls+xagents
        for iw in inner_walls:
            if self.area.intersects(iw.area):
                self.x -= self.dx
                self.y -= self.dy
                self.damage += 3
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