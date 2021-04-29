

import numpy as np
from ag_helper_fx import force_angle
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Sensors:
    def __init__(self,gt):
        self.ir_sensors = []
        angle = force_angle(np.radians(gt.irs_angle))
        for dtheta in gt.irs_dos:
            do = force_angle(np.radians(dtheta))
            self.ir_sensors.append(irSensor(gt.r,gt.irs_range,do,angle,gt.irs_colors))

    def update(self,ax,ay,ao,env):
        env_info = []
        for sensor in self.ir_sensors:
            val = sensor.update(ax,ay,ao,env)
            env_info.append(val)
        ls = env_info[:int(len(env_info)/2)]
        rs = env_info[int(len(env_info)/2):]
        return ls,rs

class irSensor:
    def __init__(self,ag_r,range,do,angle,colors):
        # agent r, sensor range, sensor angle range, sensor rel orient
        self.x = None
        self.y = None
        self.ag_r = ag_r
        self.range = range
        self.angle = angle
        self.do = do
        self.colors = colors
        self.area = None

    def update(self,ax,ay,ao,env):
        self.define_sensor(ax,ay,ao)
        # read environment (only trees for now)
        val = 0
        cval = 0
        self.ray = None
        min_dist = self.range
        for tree in env[1]:
            if self.area.intersects(tree.area):
                dist = Point(self.x,self.y).distance(self.area.intersection(tree.area))
                if dist < min_dist:
                    min_dist = dist
                    val = 1/np.exp(min_dist/self.range)
                    # 100: red, 010: green, 001: blue
                    # 110: yellow, 011: cyan, 101: magenta
                    # 000: black, 111: white, 0.5 0.5 0.5: grey
                    if self.colors:
                        cval = tree.color * val
                    else:
                        cval = val
        return cval

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
        self.area = Polygon(pxy)











###
