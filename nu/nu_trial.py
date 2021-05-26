
import numpy as np
from copy import deepcopy
from nu_glider import Glider
from nu_genotype import Genotype
from nu_animation import glx_anim
from nu_gtplot import netplot

class Trial:
    def __init__(self,tt=100,xmax=50,ymax=50,auto=False,gt=None,mode="dashes",dash=127):
        self.tt = tt
        self.xmax = xmax
        self.ymax = ymax
        self.dash = None
        self.world = None
        if auto:
            gtx = Genotype(gt)
            self.set_world(mode,dash)
            self.dash_trial(gtx,plot=True,anim=True)

    '''basic trial for specific dash patterns and single glider'''
    def dash_trial(self,gt,plot=False,anim=False):
        # initialize glider
        gl = Glider(gt,x0=int(self.xmax/2),y0=int(self.ymax/2))
        # run trial
        for ti in range(self.tt):
            # get world domain
            gl_domain = deepcopy(self.world[int(gl.i-3):int(gl.i+4),int(gl.j-3):int(gl.j+4)])
            # if world object within glider domain (collision) it dies
            if np.sum(gl_domain[1:6,1:6]):
                return
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
        gl.fin(self.dash)
        # visualization and return data
        if plot:
            netplot(gl)
        if anim:
            glx_anim(gl,self.world)
        return gl

    '''create world and allocate dash patterns'''
    def set_world(self,mode="dashes",dash=0,r=5):
        # assuming starting cfg: south-east
        self.world = np.zeros((self.xmax,self.ymax))
        self.dash = dash
        y0 = int(self.ymax/2)
        x0 = int(self.xmax/2)
        # set vertical dashed wall for controlled dash trials
        if mode=="dashes":
            # wall location, expected y at contact (upper-left membrane)
            wy = x0+r
            cy = y0+int(1+(wy-(x0+2))/4)-3
            # wall according to dash pattern (2**7=[0:127]) and world y size
            wall_align = [0]*(cy%7)
            dash_pattern = [int(di) for di in np.binary_repr(dash,7)]*(1+int(self.ymax/7))
            dashed_wall = wall_align+dash_pattern
            self.world[:,wy] = dashed_wall[:self.ymax]
        # 4 dashed walls making hashed world (useful for n>1 gliders?)
        elif mode=="hash":
            dashed_wall = [int(di) for di in np.binary_repr(dash,7)]*(1+int(self.ymax/7))
            self.world[x0-r,:] = dashed_wall[:self.xmax]
            self.world[x0+r,:] = dashed_wall[:self.xmax]
            self.world[:,y0+r] = dashed_wall[:self.ymax]
            self.world[:,y0-r] = dashed_wall[:self.ymax]
        # normal distribution: 1 if val higher/lower than sd, 0 otherwise
        elif mode=="full":
            self.world = np.random.normal(0,1,size(self.xmax,self.ymax))
            self.world = np.where(self.world>1,1,np.where(self.world<-1,1,0))
            # leave the surroundings empty
            self.world[x0-5:x0+6,y0-5:y0+5] = 0
        # bounds
        self.world[:2,:] = 1
        self.world[:,:2] = 1
        self.world[-2:,:] = 1
        self.world[:,-2:] = 1




###
