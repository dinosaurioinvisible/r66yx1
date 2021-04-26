

import numpy as np
from ag_helper_fx import force_angle
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self,gt):
        self.ir_sensors = []
        self.env_info = np.array([0]*gt.n_input)
        angle = force_angle(np.radians(gt.irs_angle))
        for dtheta in gt.irs_dos:
            do = force_angle(np.radians(dtheta))
            self.ir_sensors.append(irSensor(gt.r,gt.irs_range,angle,do))

    def update(self,ax,ay,ao,env):
        self.env_info = []
        for sensor in self.ir_sensors:
            val = sensor.update(ax,ay,ao,env)
            self.env_info.append(val)
        self.env_info = np.asarray(self.env_info)

class irSensor:
    def __init__(self,ar,range,angle,do):
        # agent r, sensor range, sensor angle range, sensor rel orient
        self.x = None
        self.y = None
        self.ag_r = ar
        self.do = do
        self.range = range
        self.angle = angle
        self.area = None

    def update(self,ax,ay,ao,env):
        self.define_sensor(ax,ay,ao)
        # read environment (only trees for now)
        val = 0
        min_dist = self.range
        for tree in env[1]:
            if self.area.intersects(tree.area):
                dist = Point(self.x,self.y).distance(self.area.intersection(tree.area))
                if dist < min_dist:
                    min_dist = dist
                    val = 1/np.exp(min_dist/self.range)
        return val

    def define_sensor(self,ax,ay,ao):
        # sensor orientation
        so = force_angle(ao+self.do)
        # sensor loc
        self.x = ax+self.ag_r*np.sin(so)
        self.y = ay+self.ag_r*np.cos(so)
        # sensor area
        arc_start = so - self.angle/2
        arc_end = so + self.angle/2
        # check for counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # define polygon points
        pxy = [(self.x,self.y)]
        arc_angles = np.array([force_angle(arc_o) for arc_o in np.linspace(arc_start, arc_end, 10)])
        pxy.extend([(self.x+self.range*np.sin(oi),self.y+self.range*np.cos(oi)) for oi in arc_angles])
        #import pdb; pdb.set_trace()
        self.area = Polygon(pxy)











###
