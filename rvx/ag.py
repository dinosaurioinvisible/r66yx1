
import numpy as np
from shapely.geometry import Point
from ag_helper_fx import force_angle
import ag_sensors
import ag_controller

class Agent:
    def __init__(self,genotype,x=100,y=100,o=0,e=100,dt=1,worldx=1000,worldy=1000):
        # simulation parameters & initial conditions
        self.worldx=worldx
        self.worldy=worldy
        self.dt=dt
        self.x=x; self.y=y; self.o=o
        self.e=e
        # agent parameters
        self.area = None
        self.r = genotype.r
        self.f_range = genotype.f_range
        self.max_speed = genotype.max_speed
        self.wheels_sep = genotype.wheels_sep
        self.define_body()
        # load sensors
        self.sensors = ag_sensors.Sensors(genotype)
        # load controller
        self.controller = ag_controller.Controller(genotype)
        # data for visualization
        self.data = AgentData(genotype,x,y,o,e,self.controller.net_state)

    def update(self,env):
        # sensor input from environment [[agents],[trees]]
        self.sensors.update(self.x,self.y,self.o,env)
        # get motor response from controller
        lm,rm = self.controller.update(self.sensors.env_info)
        # agent motion and feeding
        self.action_fx(lm,rm,env)
        self.data.save(self.x,self.y,self.o,self.e,self.sensors,self.controller)

    def action_fx(self,lm,rm,env):
        # conver to speed
        ls = lm*self.max_speed #* np.random.uniform(0.9,1.1)
        rs = rm*self.max_speed #* np.random.uniform(0.9,1.1)
        vel = (ls+rs)/2
        # new position (sin/cos are relative to o+do)
        do = (ls-rs)*self.dt/self.wheels_sep
        self.o = force_angle(self.o+do)
        dx = vel*np.sin(self.o)*self.dt
        dy = vel*np.cos(self.o)*self.dt
        self.x += dx
        self.y += dy
        print("ls,rs = [{},{}] vel={}, do={}, o={}, x={}, y={}".format(ls,rs,vel,round(np.degrees(force_angle(do))),round(np.degrees(force_angle(self.o))),round(self.x),round(self.y)))
        self.define_body()
        # feeding and avoid overlapping (bounce back)
        for tree in env[1]:
            if self.area.intersects(tree.area):
                self.x -= dx
                self.y -= dy
                self.o = force_angle(self.o*np.random.uniform(0.9,1.1))
                self.define_body()
            if self.f_area.intersects(tree.area):
                if tree.e >= 5:
                    self.e += 3
                    tree.e -= 3
        # update body area
        self.define_body()

    def define_body(self):
        # keep within bounds ("circular" world)
        if self.x > self.worldx:
            self.x = self.x-self.worldx
        elif self.x < 0:
            self.x = self.worldx+self.x
        if self.y > self.worldy:
            self.y = self.y-self.worldy
        elif self.y < 0:
            self.y = self.worldy+self.y
        # body
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)
        # feeding area
        fx = self.x + (self.r+self.f_range/2)*np.cos(self.o)
        fy = self.y + (self.r+self.f_range/2)*np.sin(self.o)
        floc = Point(fx,fy)
        self.f_area = floc.buffer(self.f_range)


class AgentData:
    def __init__(self,gt,x0,y0,o0,e0,net0):
        # genotype data
        self.r=gt.r
        self.f_range=gt.f_range
        self.irs_range=gt.irs_range
        self.irs_dos=gt.irs_dos
        self.irs_angle=gt.irs_angle
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
        self.irs = [[]]
        self.env_info = np.array([0]*gt.n_input)
        # controller
        self.net_state = net0
        self.net_out = np.array([0]*gt.n_hidden)
        self.motor_out = np.array([0,0])

    def save(self,x,y,o,e,sensors,controller):
        self.x = np.append(self.x,x)
        self.y = np.append(self.y,y)
        self.o = np.append(self.o,o)
        self.e = np.append(self.e,e)
        self.irs.append([ir.area for ir in sensors.ir_sensors])
        self.env_info = np.vstack((self.env_info,sensors.env_info))
        #self.net_state = np.vstack((self.net_state,controller.net_state))
        #self.net_out = np.vstack((self.net_out,controller.net_out))
        self.motor_out = np.vstack((self.motor_out,controller.motor_out))










###
