# coding: utf-8

import numpy as np

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

    # geometry
    def force_angle(self, angle):
        if angle > 2*np.pi:
            return angle-2*np.pi
        elif angle < 0:
            return angle+2*np.pi
        else:
            return angle

    # geometry
    def shortest_dist(self, a, b, point):
        # between line segment [a,b] and a point p
        dist = np.linalg(a-b)
        if dist == 0:           # special case A=B
            return np.linalg(point-a)

        # line extending the segment, parameterized as a+t (b-a)
        # find proyection of point p onto the line
        # it falls where t = [(p-a).(b-a)]/dist^2
        t = np.dot((point-a),(b-a))/(dist**2)

        if t < 0:
            np.linalg(point-a)  # off the A end
        if t > 1:
            np.linalg(point-b)  # off the B end
        # proyection onto the line segment
        proy_x = a[0] + t*(b[0]-a[0])
        proy_y = a[1] + t*(b[1]-a[1])
        proyection = np.array([proy_x,proy_y])
        return np.linalg(point-proyection)

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
