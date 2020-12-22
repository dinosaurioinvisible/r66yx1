
import numpy as np
import simgeometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self, s_points=10\
    , vs_do=60, vs_range=60, vs_theta=120\
    , olf_range=25, olf_theta=180\
    , aud_do=90, aud_range=50, aud_theta=180):
        # init
        self.s_points = s_points
        self.vs_do = np.radians(vs_do)
        self.vs_range = vs_range
        self.vs_theta = np.radians(vs_theta)
        self.olf_range = olf_range
        self.olf_theta = np.radians(olf_theta)
        self.aud_do = np.radians(aud_do)
        self.aud_range = aud_range
        self.aud_theta = np.radians(aud_theta)
        # sensor objects
        self.vs1 = None
        self.vs2 = None
        self.olf = None
        self.aud1 = None
        self.aud2 = None
        # sensor values
        self.vs1_val = 0
        self.vs2_val = 0
        self.olf_val = 0
        self.aud1_val = 0
        self.aud2_val = 0
        # objects data
        self.sensors = []
        self.states = []


    def read_env(self, x, y, r, o, objects):
        # define current body states
        self.x = x
        self.y = y
        self.r = r
        self.o = o
        self.world_objects = objects
        # get values
        self.read_vs()
        self.read_olf()
        self.read_aud()
        self.sensors = [self.vs1, self.vs2, self.olf, self.aud1, self.aud2]
        self.states = [self.vs1_val, self.vs2_val, self.olf_val, self.aud1_val, self.aud2_val]


    def read_vs(self):
        # get orientation, create sensor-object and read
        # vs1
        vso1 = simgeometry.force_angle(self.o-self.vs_do)
        sx, sy, self.vs1 = self.s_domain(vso1, self.vs_range, self.vs_theta)
        vs1_reading = self.sensor_reading(sx, sy, self.vs1, self.vs_range)
        k = -1*((vs1_reading/8.5)**2)
        self.vs1_val = (3371 * np.exp(k))/3500
        # vs2
        vso2 = simgeometry.force_angle(self.o+self.vs_do)
        sx, sy, self.vs2 = self.s_domain(vso2, self.vs_range, self.vs_theta)
        vs2_reading = self.sensor_reading(sx, sy, self.vs2, self.vs_range)
        k = -1*((vs2_reading/8.5)**2)
        self.vs2_val = (3371 * np.exp(k))/3500

    def read_olf(self):
        # create sensor-object, read
        sx, sy, self.olf = self.s_domain(self.o, self.olf_range, self.olf_theta)
        olf_reading = self.sensor_reading(sx, sy, self.olf, self.olf_range)
        self.olf_val = (1/np.exp(olf_reading/self.olf_range))**2

    def read_aud(self):
        # aud1
        aud_o1 = simgeometry.force_angle(self.o-self.aud_do)
        sx, sy, self.aud1 = self.s_domain(aud_o1, self.aud_range, self.aud_theta)
        # aud2
        aud_o2 = simgeometry.force_angle(self.o-self.aud_do)
        sx, sy, self.aud2 = self.s_domain(aud_o1, self.aud_range, self.aud_theta)
        # check for signals
        com1 = 0
        com2 = 0
        for ox in self.world_objects:
            if self.aud1.intersects(ox.area):
                try:
                    com1 = ox.com
                except:
                    com1 = 0
            if self.aud2.intersects(ox.area):
                try:
                    com2 = ox.com
                except:
                    com2 = 0
        # TODO
        self.aud1_val = com1
        self.aud2_val = com2

    def sensor_reading(self, sx, sy, sensor, s_range):
        s_reading = 0
        min_dist = s_range+1
        # get closest reading
        for wo in self.world_objects:
            if sensor.intersects(wo.area):
                dist = Point(sx,sy).distance(sensor.intersection(wo.area))
                if dist < min_dist:
                    min_dist = dist
        if min_dist <= s_range:
            s_reading = min_dist
        return s_reading

    def s_domain(self, so, s_range, s_theta):
        # define location
        sx = self.x + self.r*np.cos(so)
        sy = self.y + self.r*np.sin(so)
        # define arc
        arc_start = so-s_theta/2
        arc_end = so+s_theta/2
        # check counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # get arc angle points and force angles
        arc_points = np.linspace(arc_start, arc_end, self.s_points)
        arc_angles = np.array([simgeometry.force_angle(oi) for oi in arc_points])
        arc_x = sx + s_range*np.cos(arc_angles)
        arc_y = sy + s_range*np.sin(arc_angles)
        s_coords = [(sx,sy)]
        [s_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        sensor_domain = Polygon(s_coords)
        return sx, sy, sensor_domain



















#
