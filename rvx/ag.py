
import numpy as np
from shapely.geometry import Point
from ag_helper_fx import force_angle
import ag_sensors
import ag_controller

class Agent:
    def __init__(self,genotype,x=100,y=100,o=0,e=100):
        # simulation parameters & initial conditions
        self.worldx=1000
        self.worldy=1000
        self.dt=1
        self.x=x; self.y=y; self.o=o
        self.e=e
        # agent parameters
        self.area = None
        self.r = genotype.r
        self.frange = genotype.frange
        self.max_speed = genotype.max_speed
        self.wheels_sep = genotype.wheels_sep
        self.define_agent()
        # load sensors
        self.sensors = ag_sensors.Sensors(genotype)
        # load controller
        self.controller = ag_controller.Controller(genotype)
        # data for visualization
        self.data = AgentData(genotype,x,y,o,e,self.controller.net_state)

    def update(self,env):
        # sensor input from environment
        env_info = self.sensors.update(env)
        # get motor response from controller
        lm,rm = self.controller.update(env_info)
        # agent motion and feeding
        self.action_fx(lm,rm,env)
        self.save_data(self.x,self.y,self.o,self.e,env_info,self.controller.net_state,self.controller.net_out,np.asarray([lm,rm]))

    def action_fx(self,lm,rm,env):
        ls = lm*self.max_speed * np.random.uniform(0.9,1.1)
        rs = rm*self.max_speed * np.random.uniform(0.9,1.1)
        vel = (ls+rs)/2
        # new position (sin/cos are relative to o+do)
        do = (ls-rs)*self.dt/self.wheels_sep
        self.o = force_angle(self.o+do)
        dx = vel*np.sin(self.o)*self.dt
        dy = vel*np.cos(self.o)*self.dt
        self.x += dx
        self.y += dy
        self.define_agent()
        # feeding and avoid overlapping (bounce back)
        for tree in env.trees:
            if self.area.intersects(tree.area):
                self.x -= dx
                self.y -= dy
                self.o = force_angle(self.o*np.random.uniform(0.9,1.1))
                self.define_agent()
            if self.farea.intersects(tree.area):
                self.e += 1
                tree.e -= 1
        # update body area
        self.define_body()

    def define_body(self):
        # keep within bounds ("circular" world)
        if self.x > self.worldx:
            self.x = self.x-self.worldx
        elif self.x < 0:
            self.x = self.worldx-self.x
        if self.y > self.worldy:
            self.y = self.y-self.worldy
        elif self.y < 0:
            self.y = self.worldy-self.y
        # body
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)
        # feeding area
        fx = self.x + (self.r+self.frange/2)*np.cos(self.o)
        fy = self.y + (self.r+self.frange/2)*np.sin(self.o)
        floc = Point(fx,fy)
        self.farea = loc.buffer(floc)


class AgentData:
    def __init__(self,gt,x0,y0,o0,e0,net0):
        # genotype data
        self.r=gt.r
        self.frange=gt.frange
        self.srange=gt.srange
        self.sdos=gt.sdos
        self.sangles=gt.sangles
        self.wx_in=gt.wx_in
        self.wx_out=gt.wx_out
        self.thresholds=gt.thresholds
        self.ga=gt.ga
        self.gb=gt.gb
        # arrays for historic data
        self.x = np.array([x0])
        self.y = np.array([y0])
        self.o = np.array([o0])
        self.e = np.array([e0])
        # sensors
        self.env_info = np.array([0]*len(gt.sdos))
        # controller
        self.net_state = net0
        self.net_out = np.array([0]*gt.nhidden)
        self.motor_output = np.array([0,0,0,0])

    def save_data(self,x,y,o,e,env_info,net_state,net_out,motor_output):
        self.x = np.append(self.x,x)
        self.y = np.append(self.y,y)
        self.o = np.append(self.o,o)
        self.e = np.append(self.e,e)
        self.env_info = np.vstack((self.env_info,env_info))
        self.net_state = np.vstack((self.net_state,net_state))
        self.net_out = np.vstack((self.net_out,net_out))
        self.motor_output = np.vstack((self.motor_output,motor_output))










###
