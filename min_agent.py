
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon
import min_genotype
import min_sensors
import min_axcom
import min_net
import min_data


class Agent:
    def __init__(self, genotype,
    x=100, y=100, o=0):
        # get genotype
        self.genotype = genotype
        # location
        self.x = x; self.y = y; self.o = o
        # agent features
        self.r = self.genotype.r
        self.max_speed = self.genotype.max_speed
        self.wheels_sep = self.genotype.wheels_sep
        self.define_body_area()
        # energy
        self.e = self.genotype.energy
        self.de_dt = self.genotype.de_dt
        self.e_n = self.genotype.e_n
        self.damage = 0
        # feeding
        self.f_rate = self.genotype.f_rate
        self.f_range = self.genotype.f_range
        self.f_theta = self.genotype.f_theta
        self.define_feeding_area()
        # communication
        self.com_n = self.genotype.com_n
        # init modules
        self.sensors = min_sensors.Sensors(self.genotype)
        self.net = min_net.Net(self.genotype)
        if self.com_n > 0:
            self.axcom = min_axcom.Com(self.genotype, self.x, self.y)
        self.data = min_data.Data()


    def update_in(self, walls, trees, xagents):
        # save starting conditions
        self.data.save_ax(self.x, self.y, self.o, self.area, self.f_area, self.e)
        # update sensors and get env info
        self.sensors.define_sensors_area(self.x, self.y, self.o, self.r)
        vs_info, olf_info = self.sensors.read_environment(walls,trees,xagents)
        # energy input (if active)
        e_info = np.array([0.]*self.e_n)
        if self.e_n > 0:
            ev = 0 if self.e > 1000 else 1-(self.e*self.de_dt/1000)**1.5
            e_info += ev
        # communicative input (if active)
        com_info = np.array([0.]*self.com_n)
        if self.com_n > 0:
            self.axcom.define_com_area(self.x, self.y)
            cagents = [xag for xag in xagents if xag.e>0]
            com_info = self.axcom.update_in(cagents)
        # define the sm vector: np array(vs1, ..,vsn, olf, e, c1, ...,cn)
        sm_info = np.concatenate((vs_info,olf_info,e_info,com_info))
        # get response from controller
        self.lm, self.rm, com = self.net.update(sm_info)

        # print("\ngenotype: {}".format(self.genotype))
        # print("xy:{},{}".format(round(self.x,2),round(self.y,2)))
        # print("vs_info={}".format(np.around(vs_info,2)))
        # print("olf_info={}".format(np.around(olf_info,2)))
        # print("e_info={}".format(np.around(e_info,2)))
        # print(">input: {}".format(np.around(self.net.net_state[:5],2)))
        # print("hidden: {}".format(np.around(self.net.net_state[5:7],2)))
        # print("motors: {}".format(np.around(self.net.net_state[7:],2)))
        # print("output: {}".format(np.around(self.net.net_out,2)))
        # print("lm={}, rm={}".format(self.lm, self.rm))
        #import pdb; pdb.set_trace()

        # communication
        if self.com_n > 0:
            self.axcom.update_out(com)
            self.data.save_com(self.axcom.com_area, self.axcom.com_out)
        # save data
        self.data.save_sensors(self.sensors.vs_sensors, self.sensors.olf_sensors, vs_info, olf_info, e_info, com_info)
        self.data.save_nnet(self.net.net_state, self.net.net_out)

    def move_fx(self):
        # compute changes in location (force movement if 0)
        lw = self.lm*self.max_speed + np.random.uniform(-0.1,0.1)
        rw = self.rm*self.max_speed + np.random.uniform(-0.1,0.1)
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

    def update_e(self, trees):
        # simple version, independent
        ntx = sum([1 if self.f_area.intersects(tx.area) else 0 for tx in trees])
        de = ntx*self.f_rate - self.damage - self.de_dt
        self.e += de
        self.e = 0 if self.e < 0 else self.e
        self.damage = 0

    # def feed_fx(self, trees):
        # check if there are trees in feeding area
        # trees_lx = [1 if self.f_area.intersects(tx.area) else 0 for tx in trees]
        # return np.array(trees_lx)

    # def update_energy(self, ag_ax_tx):
        # energy - dedt - damage
        # de = -(self.de_dt+self.damage)
        # feed according to number of agents near
        # for n_ags in ag_ax_tx:
        #     de += self.f_rate*(n_ags**2)
        # self.e += de
        # save data outputs
        # self.data.save_feeding(ag_ax_tx, de)
        # if self.e < 0:
        #     self.e = 0

    def define_body_area(self):
        # define body
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

    def check_overlap(self, bounds, inner_walls, trees, xagents):
        # keep within bounds
        while bounds.contains(self.area) == False:
            self.x -= self.dx
            self.y -= self.dy
            do = np.radians(np.random.randint(360))
            self.o = geometry.force_angle(self.o+do)
            self.define_body_area()
            self.damage += 100
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
                do = np.radians(np.random.randint(360))
                self.o = geometry.force_angle(self.o+do)
                self.define_body_area()
                self.damage += 10

    def define_feeding_area(self):
        # define feeding area
        fx = self.x + self.r*np.cos(self.o)
        fy = self.y + self.r*np.sin(self.o)
        arc_start = self.o - np.radians(self.f_theta/2)
        arc_end = self.o + np.radians(self.f_theta/2)
        # force counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # get arc angle points
        arc_points = np.linspace(arc_start, arc_end, 100)
        arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
        # get arc coordinates and create polygon
        arc_x = fx + self.f_range*np.cos(arc_angles)
        arc_y = fy + self.f_range*np.sin(arc_angles)
        f_coords = [(fx,fy)]
        [f_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        self.f_area = Polygon(f_coords)


















    #
