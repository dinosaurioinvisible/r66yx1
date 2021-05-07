

import numpy as np
from nu_glider import Glider
from nu_fx import xy_around
from nu_genotype import Genotype


class Trial:
    def __init__(self,t=5,xmax=100,ymax=100):
        self.t = t
        self.xmax = xmax
        self.ymax = ymax
        self.world = np.zeros((self.xmax,self.ymax))
        self.run_trial()

    def run_trial(self,genotype=None):
        # intial params
        if not genotype:
            gt = Genotype()
        o0 = 1
        st0 = np.array([1,1,0,0,0,0,0,0,1,0,0,1,0,1,0,0,0,1,1,0,1,0,0,0,0]).reshape(5,5)
        gl = Glider(gt,st0,o0,self.xmax/2,self.ymax/2)
        # sim
        ti = 0
        # self.world[50][53] = 1
        while ti < self.t:
            # allocate glider
            self.world[int(gl.x-2):int(gl.x+3),int(gl.y-2):int(gl.y+3)] = gl.domain[1:6,1:6]
            # interaction domain
            env = self.world[int(gl.x-3):int(gl.x+4),int(gl.y-3):int(gl.y+4)]
            env[int(gl.x-2):int(gl.x+3),int(gl.y-2):int(gl.y+3)] = 0
            self.world[int(gl.x-2):int(gl.x+3),int(gl.y-2):int(gl.y+3)] = 0
            # update glider
            gl.update(env)
            print(gl.domain[1:6,1:6])
            ti += 1

Trial()
