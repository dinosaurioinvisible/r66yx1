

import numpy as np
from nu_glider import Glider
from nu_genotype import Genotype
from copy import deepcopy
from nu_animation import glx_anim

class Trial:
    def __init__(self,tt=100,xmax=50,ymax=50,auto=False):
        self.tt = tt
        self.xmax = xmax
        self.ymax = ymax
        self.world = None
        self.data = []
        if auto:
            self.run(anim=True)

    def run(self,genotype=None,anim=False):
        if not genotype:
            gt = Genotype()
        # for ech gt
        x0 = self.xmax/2
        y0 = self.ymax/2
        gl = Glider(gt,x0=x0,y0=y0)
        # try with differents wall patterns
        for dash in range(1,128):
            ti = 0
            self.set_world(dash)
            while ti < self.tt:
                # get world domain and allocate glider
                gl_domain = deepcopy(self.world[int(gl.i-3):int(gl.i+4),int(gl.j-3):int(gl.j+4)])
                # if world object within glider domain it dies
                if np.sum(gl_domain[1:6,1:6]):
                    ti = self.tt
                else:
                    gl_domain[1:6,1:6] += gl.st.reshape(5,5)
                    gl.update(gl_domain)
                ti+=1
            if anim==True:
                glx_anim(gl,self.world)
            self.data.append(deepcopy(gl))
            gl.set_cfg(reset=True)

    def set_world(self,dash):
        # north, east, south, west
        self.world = np.zeros((self.xmax,self.ymax))
        # expected encounter point
        ep = 28
        reps = 6
        # (any of the 2**7 patterns for encounter [0:127])
        dashed_wall = np.zeros(self.ymax)
        dw = [int(xi) for xi in np.binary_repr(dash,7)]*reps
        dashed_wall[int(ep-len(dw)/2):int(ep+len(dw)/2+reps%2)] = dw
        # dashed walls
        self.world[:,30] = dashed_wall
        # bounds
        self.world[1,1:-1]=1
        self.world[1:-1,1]=1
        self.world[-2,1:-1]=1
        self.world[1:-2,-2]=1


#Trial(auto=True)

###
