

import numpy as np
from nu_glider import Glider
from nu_genotype import Genotype
from copy import deepcopy
from nu_animation import glx_anim
from nu_gtplot import netplot

class Trial:
    def __init__(self,tt=100,xmax=50,ymax=50,auto=False):
        self.tt = tt
        self.xmax = xmax
        self.ymax = ymax
        self.world = None
        self.data = []
        self.ngt = 0
        if auto:
            self.run(anim=True)

    def run(self,gt=None,anim=False):
        if not gt:
            gt = Genotype()
        # for ech gt
        self.ngt += 1
        self.data=[]
        gl = Glider(gt,x0=int(self.xmax/2),y0=int(self.ymax/2))
        # try with differents wall patterns
        print("")
        for dash in range(1,128):
            self.set_world(dash)
            ti = 0
            endt = 100
            while ti < self.tt:
                # get world domain and allocate glider
                gl_domain = deepcopy(self.world[int(gl.i-3):int(gl.i+4),int(gl.j-3):int(gl.j+4)])
                # if world object within glider domain it dies
                if np.sum(gl_domain[1:6,1:6]):
                    endt=ti
                    ti=self.tt
                else:
                    gl_domain[1:6,1:6] += gl.st
                    gl.update(gl_domain)
                ti+=1
            if anim:
                glx_anim(gl,self.world)
            if gl.recs>5 and endt==100:
                self.data.append([dash,deepcopy(gl.recs),deepcopy(gl)])
            print("gt{}: dash={}/127, recs={}, endt={}, saved={}, gt={}      ".format(self.ngt,dash,gl.recs,endt,len(self.data),gt),end='\r')
            gl.set_cfg(reset=True,gt=gt)
        glgt = sorted(self.data,key=lambda x:x[1],reverse=True)[0][2]
        netplot(glgt)
        return self.data

    def set_world(self,dash):
        # north, east, south, west
        self.world = np.zeros((self.xmax,self.ymax))
        # walls locs and dash pattern (2**7=[0:127])
        vwalls = [30]
        reps = int(self.ymax/7)
        # expected contact y-point (i=domain start,j=contact membrane)
        ci = int(self.ymax/2)+int(1+(vwalls[0]-(self.xmax/2+2))/4)-3
        # allocate walls
        dw = [0]*(ci%7)+[int(xi) for xi in np.binary_repr(dash,7)]*reps+[0]*6
        for vw in vwalls:
            self.world[:,vw] = dw[:self.ymax]
        # bounds
        self.world[1,1:-1]=1
        self.world[1:-1,1]=1
        self.world[-2,1:-1]=1
        self.world[1:-2,-2]=1


#Trial(auto=True)

###
