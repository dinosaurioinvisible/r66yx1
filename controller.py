
import numpy as np
import neural_net
import sensors
import motor
# import body         # TODO
# import environment  # world

# loop of interactions
# de/dt = E(e,p)    # environment: environment & body
#
# da/dt = A(a,s)    # neural dynamics: sensors & neural dynamics
# ds/dt = S(e,a)    # sensors: environment & neural dynamics
# dm/dt = M(a)      # motors: neural dynamics
#
# dp/dt = B(p,m,e)  # body: body & motors & environment

class Controller:
    def __init__(self, energy=100):
        self.energy = energy
        # self.body = robot.Robot()
        self.sensors = sensors.Sensors()
        self.nnet = nnet.Net()
        self.motors = motors.Motors()

    # TODO
    # this fx should reflect the effect of the actions
    # of the agent into the environment and viceversa
    # but this should be outside the controller
    # skip for now
    # environment
    # def e_ex(self, e, p):
    #     e = E(e,p)
    #     return e
    # body
    # def b_fx(self, p, m, e):
    #   p = B(p,m,e)
    #   return p

    def act(self):
        # sensors
        s = self.s_fx(e,a)
        # nnet
        a = self.a_fx(a,s)
        # motors
        m = self.m_fx(a)
        # return only motor activation
        # (body-env dynamics are not part of the controller)
        return m
