
import numpy as np
import geometry as geom
from shapely.geometry import Point
from copy import deepcopy
from rnet import Network
import rsensors


class Agent:
    def __init__(self, network, x,y,o, dt=0.1):
        # position
        self.x = x
        self.y = y
        self.o = o
        # parameters as in Quinn & Shibuya et al
        self.dt = dt
        self.r = 2.9
        self.speed = 8
        self.wsep = 5.2
        self.define_area()
        # init robot's modules
        self.net = Network(network)
        self.sensors = rsensors.Sensors(self.net.irx)
        self.data = AgentData()

    def update(self, env):
        # robot body data
        self.data.save_robot(self.x,self.y,self.o,self.area)
        # sensors
        self.sensors.update(self.x,self.y,self.o,env)
        self.data.save_sensors(self.sensors.irs, self.sensors.irs_info)
        # network
        lm, rm = self.net.update(self.sensors.irs_info)
        self.data.save_net(self.net.states,self.net.firing,self.net.output,lm,rm)
        # velocity
        vl = (lm*self.speed)*self.dt * np.random.uniform(0.9,1.1)
        vr = (rm*self.speed)*self.dt * np.random.uniform(0.9,1.1)
        vel = (vr+vl)/2
        # change
        self.dx = vel*np.cos(self.o)
        self.dy = vel*np.sin(self.o)
        self.do = geom.force_angle((vr-vl)/self.wsep)
        # new position
        self.x += dx
        self.y += dy
        self.define_area()
        self.check_overlap()
        # new orientation
        self.o = geom.force_angle(self.o+self.do)

    def define_area(self):
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)

    def check_overlap(self, env=[]):
        for wo in env:
            if self.area.intersects(wo.area):
                self.x -= self.dx
                self.y -= self.dy
                self.define_area()
                self.do = self.do*np.random.uniform(0,1)
                break


class AgentData:
    def __init__(self):
        # parameters
        self.r = 2.9
        self.speed = 8
        self.wsep = 5.2
        # agent body
        self.x = np.array([])
        self.y = np.array([])
        self.o = np.array([])
        self.area = []
        self.cols = []
        # sensors
        self.irs = []
        self.irs_info = None
        # network data
        self.net_state = []
        self.net_firing = None
        self.net_out = None
        self.motor = []

    def save_robot(self, x,y,o,area):
        self.x = np.append(self.x,x)
        self.y = np.append(self.y,y)
        self.o = np.append(self.o,o)
        self.area.append(deepcopy(area))

    def save_sensors(self,irs,info):
        self.irs.append(irs)
        try:
            self.irs_info = np.vstack((self.irs_info,info))
        except:
            self.irs_info = info

    def save_net(self,state,firing,out,lm,rm):
        self.net_state.append(net_state)
        try:
            self.net_firing = np.vstack((self.net_firing,firing))
            self.net_output = np.vstack((self.net_out,out))
        except:
            self.net_firing = firing
            self.net_out = out
        self.motor.append((lm,rm))


















#
