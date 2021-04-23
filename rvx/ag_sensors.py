

import numpy as np
from ag_helper_fx import force_angle
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self,gt):
        self.sensors = []
        angle = force_angle(np.radians(gt.sangle))
        for dtheta in gt.sdos:
            do = force_angle(np.radians(dtheta))
            self.sensors.append(irSensor(gt.r,gt.srange,angle,do))

    def update(self,ax,ay,ao,env):
        env_info = []
        for sensor in self.sensors:
            val = sensor.update(ax,ay,ao,env)
            env_info.append(val)
        return np.asarray(env_info)

class irSensor:
    def __init__(self,ar,range,angle,do):
        # agent r, sensor range, sensor angle range, sensor rel orient
        self.ar = ar
        self.do = do
        self.range = range
        self.angle = angle
        self.area = None

    def update(self,ax,ay,ao,env):
        self.define_sensor(ax,ay,ao)
        # read environment
        val = 0
        min_dist = self.range
        for tree in env.trees:
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
        sx = ax + self.ar*np.cos(so)
        sy = ay + self.ar*np.sin(so)
        # sensor area
        arc_start = so - self.angle
        arc_end = so + self.angle
        # check for counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # define polygon points
        pxy = [(sx,sy)]
        arc_angles = np.array([force_angle(arc_o) for arc_o in np.linspace(arc_start, arc_end, 10)])
        pxy.extend([(sx+self.range*np.cos(oi),sy+self.range*np.sin(oi)) for oi in arc_angles])
        self.area = Polygon(pxy)











###
