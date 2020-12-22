
import numpy as np
import geometry as geom
from shapely.geometry import Point
from copy import deepcopy
import qsensors
import qnet


class Agent:
    def __init__(self, network, x,y,o):
        self.x = x
        self.y = y
        self.o = o
        # values as in Shibuya et al
        self.r = 2.9
        self.speed = 8
        self.wsep = 5.2
        # init robot's modules
        self.dt = 0.1
        self.cols = False
        self.net = qnet.Network(network)
        self.sensors = qsensors.Sensors(self.net.irx,self.r,self.x,self.y,self.o)
        self.data = AgentData()
        self.define_body()
        self.save_data()

    def update(self, xagents):
        # get the environmental info and pass through controller
        env_info = self.sensors.get_info(xagents)
        # env_arr = np.asarray(env_info)*self.dt
        # this shouldn't be multiplied by dt
        # env_arr = np.asarray(env_info)
        self.lm, self.rm = self.net.update(env_info)
        # move and check collisions
        self.move_fx()
        self.cols = False
        for xag in xagents:
            if self.body.intersects(xag.body):
                self.cols += True
                self.collision_fx()
        # redefine sensors for next step
        self.sensors.define_sensors(self.x,self.y,self.o)
        self.save_data()

    def move_fx(self):
        # noise as in Shibuya et al.
        vl = (self.lm*self.speed)*self.dt * np.random.uniform(0.9,1.1)
        vr = (self.rm*self.speed)*self.dt * np.random.uniform(0.9,1.1)
        vel = (vr+vl)/2
        # change
        self.dx = vel*np.cos(self.o)
        self.dy = vel*np.sin(self.o)
        self.do = geom.force_angle((vr-vl)/self.wsep)
        # new location
        self.x += self.dx
        self.y += self.dy
        self.o = geom.force_angle(self.o+self.do)
        self.define_body()

    def collision_fx(self):
        # if they were to collide, they don't move (Quinn's thesis)
        self.x -= self.dx
        self.y -= self.dy
        # but the angle changes in a fraction of the original spin
        self.o = geom.force_angle(self.o-self.do+(self.do*np.random.uniform(0,1)))
        self.define_body()

    def define_body(self):
        pos = Point(self.x,self.y)
        self.body = pos.buffer(self.r)

    def save_data(self):
        self.data.save_data(self.x,self.y,self.o,self.body,self.cols,self.sensors.irs,self.sensors.info,self.net.net_in,self.net.state,self.net.ots,self.net.net_out,self.net.motor_out)


class AgentData:
    def __init__(self):
        # agent data for visualization
        self.x = []
        self.y = []
        self.o = []
        self.body = []
        self.collisions = []
        # sensors
        self.irs = []
        self.irs_info = []
        # network data
        self.net_state = []
        self.net_in = []
        self.net_ots = []
        self.net_out = []
        self.motor_out = []

    def save_data(self, x,y,o,body,collision, irs,irs_info,net_in,net_state,net_ots,net_out,motor_out):
        self.x.append(x)
        self.y.append(y)
        self.o.append(o)
        self.body.append(body)
        self.collisions.append(collision)
        self.irs.append(irs)
        self.irs_info.append(irs_info)
        # net
        self.net_in.append(deepcopy(net_in))
        self.net_state.append(deepcopy(net_state))
        self.net_ots.append(deepcopy(net_ots))
        self.net_out.append(deepcopy(net_out))
        self.motor_out.append(deepcopy(motor_out))














#
