
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self, genotype):
        # init
        self.s_points = genotype.s_points
        # olfact
        self.olf_range = genotype.olf_range/2
        self.olf_theta = np.radians(genotype.olf_theta)/2
        # vision (by default values)
        self.vs_n = genotype.vs_n
        self.vs_dos = np.radians(genotype.vs_dos)
        self.vs_range = [genotype.vs_range/2]*self.vs_n
        self.vs_theta = [np.radians(genotype.vs_theta)/2]*self.vs_n
        # for attention
        self.na_olf_range = genotype.olf_range/2
        self.na_olf_theta = np.radians(genotype.olf_theta)/2
        self.na_vs_range = genotype.vs_range/2
        self.na_vs_theta = np.radians(genotype.vs_theta)/2

    def define_sensors_area(self, x, y, o, r):
        self.vs_sensors = []
        for n in range(self.vs_n):
            # list of angles of sensors defined in genotype
            vso = geometry.force_angle(o+self.vs_dos[n])
            # sensor location
            self.vsx = x + r*np.cos(vso)
            self.vsy = y + r*np.sin(vso)
            # define arc (sensor angle +- sensor angle range)
            arc_start = vso-self.vs_theta[n]/2
            arc_end = vso+self.vs_theta[n]/2
            # check for counter-clockwise
            if arc_start > arc_end:
                arc_end += np.radians(360)
            # define sensor area
            arc_points = np.linspace(arc_start, arc_end, self.s_points)
            arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
            arc_xs = self.vsx + self.vs_range[n]*np.cos(arc_angles)
            arc_ys = self.vsy + self.vs_range[n]*np.sin(arc_angles)
            area_coords = [(self.vsx,self.vsy)]
            [area_coords.append((xi,yi)) for xi,yi in zip(arc_xs, arc_ys)]
            # define sensor polygon
            sensor_domain = Polygon(area_coords)
            self.vs_sensors.append(sensor_domain)
        # olfactory sensor location
        # basically the same, but by separate is clearer
        # (sensor in the membrane with same orientation)
        self.osx = x + r*np.cos(o)
        self.osy = y + r*np.sin(o)
        # define arc and polygon
        arc_start = o-self.olf_theta/2
        arc_end = o+self.olf_theta/2
        if arc_start > arc_end:
            arc_end += np.radians(360)
        arc_points = np.linspace(arc_start, arc_end, self.s_points)
        arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
        arc_xs = self.osx + self.olf_range*np.cos(arc_angles)
        arc_ys = self.osy + self.olf_range*np.sin(arc_angles)
        area_coords = [(self.osx,self.osy)]
        [area_coords.append((xi,yi)) for xi,yi in zip(arc_xs, arc_ys)]
        self.olf_sensor = Polygon(area_coords)


    def read_environment(self, walls, trees, xagents):
        world_objects = walls+trees+xagents
        self.info = []
        # read ir sensors
        for n in range(len(self.vs_sensors)):
            val = 0
            min_dist = 100
            for wo in world_objects:
                if self.vs_sensors[n].intersects(wo.area):
                    dist = Point(self.vsx,self.vsy).distance(self.vs_sensors[n].intersection(wo.area))
                    if dist < min_dist:
                        min_dist = dist
            if min_dist < self.vs_range[n]:
                # k = -1*((min_dist/8.5)**2)
                #val = (3371 * np.exp(k))/35000
                val = (1/np.exp(min_dist/(self.olf_range/2)))**2
            self.info.append(val)
        # "olfactory" sensor
        val = 0
        min_dist = 100
        for tree in trees:
            if self.olf_sensor.intersects(tree.area):
                dist = Point(self.osx,self.osy).distance(self.olf_sensor.intersection(tree.area))
                if dist < min_dist:
                    min_dist = dist
            if min_dist < self.olf_range:
                val = (1/np.exp(min_dist/(self.olf_range/2)))**2
        self.info.append(val)
        return self.info

    def attention_fx(self, olf_attn, vs_attn):
        # modify range and area for inputs
        # [-1,1] -> [range=min, theta=max] , [range=max, theta=min]
        if olf_attn:
            self.olf_range = self.na_olf_range + self.na_olf_range*olf_attn[0]
            self.olf_theta = self.na_olf_theta - self.na_olf_theta*olf_attn[0]
        if len(vs_attn) > 0:
            self.vs_range =  self.na_vs_range + self.na_vs_range*vs_attn
            self.vs_theta = self.na_vs_theta - self.na_vs_theta*vs_attn
















#
