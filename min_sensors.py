
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self, genotype):
        # init
        self.s_points = 100
        # vision (by default values)
        self.vs_n = genotype.vs_n
        self.vs_loc = np.radians(genotype.vs_loc)
        self.vs_range = genotype.vs_range
        self.vs_theta = np.radians(genotype.vs_theta)
        # olfact
        self.olf_n = genotype.olf_n
        self.olf_loc = np.radians(genotype.olf_loc)
        self.olf_range = genotype.olf_range
        self.olf_theta = np.radians(genotype.olf_theta)


    def define_sensors_area(self, x,y,o,r):
        self.vs_sensors = []
        self.vs_xy = []
        for n in range(self.vs_n):
            # list of angles of sensors defined in genotype
            vso = geometry.force_angle(o+self.vs_loc[n])
            # sensor location
            vsx = x + r*np.cos(vso)
            vsy = y + r*np.sin(vso)
            self.vs_xy.append([vsx,vsy])
            # define arc (sensor angle +- sensor angle range)
            arc_start = vso-self.vs_theta/2
            arc_end = vso+self.vs_theta/2
            # check for counter-clockwise
            if arc_start > arc_end:
                arc_end += np.radians(360)
            # define sensor area
            arc_points = np.linspace(arc_start, arc_end, self.s_points)
            arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
            arc_xs = vsx + self.vs_range*np.cos(arc_angles)
            arc_ys = vsy + self.vs_range*np.sin(arc_angles)
            area_coords = [(vsx,vsy)]
            [area_coords.append((xi,yi)) for xi,yi in zip(arc_xs, arc_ys)]
            # define sensor polygon
            sensor_domain = Polygon(area_coords)
            self.vs_sensors.append(sensor_domain)
        # olfactory sensor location
        self.olf_sensors = []
        self.olf_xy = []
        # basically the same, but by separate is clearer
        for n in range(self.olf_n):
            # list of angles of sensors defined in genotype
            olfo = geometry.force_angle(o+self.olf_loc[n])
            # sensor location
            olfx = x + r*np.cos(olfo)
            olfy = y + r*np.sin(olfo)
            self.olf_xy.append([olfx,olfy])
            # define arc
            arc_start = olfo-self.olf_theta/2
            arc_end = olfo+self.olf_theta/2
            if arc_start > arc_end:
                arc_end += np.radians(360)
            arc_points = np.linspace(arc_start, arc_end, self.s_points)
            arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
            arc_xs = olfx + self.olf_range*np.cos(arc_angles)
            arc_ys = olfy + self.olf_range*np.sin(arc_angles)
            area_coords = [(olfx,olfy)]
            [area_coords.append((xi,yi)) for xi,yi in zip(arc_xs, arc_ys)]
            self.olf_sensors.append(Polygon(area_coords))

    def read_environment(self, walls, trees, xagents):
        world_objects = walls+trees+xagents
        vs_info = []
        # read vision
        for n in range(len(self.vs_sensors)):
            val = 0
            min_dist = self.vs_range
            for wo in world_objects:
                if self.vs_sensors[n].intersects(wo.area):
                    dist = Point(self.vs_xy[n][0],self.vs_xy[n][1]).distance(self.vs_sensors[n].intersection(wo.area))
                    if dist < min_dist:
                        min_dist = dist
                        val = 0.13+(1-np.exp(-(self.vs_range-min_dist)/self.vs_range)**2)
            vs_info.append(val)
        # read olf
        olf_info = []
        for n in range(len(self.olf_sensors)):
            val = 0
            min_dist = self.olf_range
            for tx in trees:
                if self.olf_sensors[n].intersects(tx.area):
                    dist = Point(self.olf_xy[n][0],self.olf_xy[n][1]).distance(self.olf_sensors[n].intersection(tx.area))
                    if dist < min_dist:
                        min_dist = dist
                        val = 0.13+(1-np.exp(-(self.olf_range-min_dist)/self.olf_range)**2)
            olf_info.append(val)
        # return arrays
        return np.array(vs_info), np.array(olf_info)









































#
