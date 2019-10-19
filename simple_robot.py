# coding: utf-8

import numpy as np
import geometry

class Robot:
    def __init__(self, x=None, y=None, o=None\
    , radius=2, wsep=2, speed=1, motor_noise=0\
    , xsens=2, xsens_range=10):
        ##
        self.x = np.random.randint(0,100) if x != None else x
        self.y = np.random.randint(0,100) if y != None else y
        self.o = np.radians(np.random.randint(0,360)) if o != None else o
        ##
        self.radius = radius
        self.wsep = wsep
        self.speed = speed
        self.motor_noise
        ##
        self.xsens = xsens
        self.xsens_range = xsens_range
        ##
        self.lw = 0
        self.rw = 0
        self.theta = 0
        ##

    def speed(self, w):
        if w > -15 and w < 15:
            speed = 0.6*w
        else:
            w = 1.2*w
        w += self.motor_noise
        return speed

    def wall_collision(self):
        if self.shortest_dist(p1,p2,robot_position) <= self.radius:
            return True
        return False

    def collision(self):
        if self.shortest_dist(location, obstacle) < self.radius:
            return True
        else:
            return False

    def move(self):
        l_speed = speed(self.lw)
        r_speed = speed(self.rw)
        vel = (l_speed + r_speed)/2

        dx = vel*np.con(self.o)
        dy = vel*np.sin(self.o)
        dtheta = (l_speed - r_speed)/wsep

        self.x += dx
        self.y += dy
        self.o += dtheta
        self.o = self.force_angle(self.o)
