
import numpy as np
from copy import deepcopy
from nu_glider import Glider
from nu_genotype import Genotype
from nu_animation import glx_anim

class Trial:
    def __init__(self,tt=100,wsize=200,auto=False,st0=1,center=True,gtx=None,mode="",dash=0,anim=True):
        self.tt=tt
        self.limit=int(tt/10)
        self.wsize=wsize
        self.world=None
        if auto:
            self.dash_trial(gtx,st0,center,mode,dash,anim)

    '''default trial: st1=SE, single glider, dashed wall world'''
    def run(self,gtx,st0=1,center=True,mode="",dash=0,anim=False):
        # initialize world and glider
        if center:
            x0,y0=int(self.wsize/2),int(self.wsize/2)
        else:
            x0,y0=np.random.randint(10,self.wsize-10,size=(2))
        self.set_world(x0,y0,st0,mode,dash)
        gl = Glider(gtx,st0,x0,y0)
        # run trial
        dist=0
        tlim=0
        for ti in range(self.tt):
            # get world domain
            gl_domain = deepcopy(self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4])
            # if world object within glider domain (collision), it dies
            if np.sum(gl_domain[1:6,1:6]):
                glx_anim(gl,self.world)
                return [None,1,0,ti,dist]
            # if gl doesn't move in time limit, it dies
            elif tlim > self.limit:
                glx_anim(gl,self.world)
                return [None,0,1,ti,dist]
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim += 1
                if gl.dxy[-1]>0:
                    tlim=0
                    dist+=1
        glx_anim(gl,self.world)
        # count loops, opt visualization and return
        gl.gl_loops()
        if anim:
            glx_anim(gl,self.world)
        return [gl,dist]

    '''create world and allocate dash patterns'''
    def set_world(self,x0,y0,st0=1,mode="",dash=0,r=5):
        # empty world
        self.world = np.zeros((self.wsize,self.wsize)).astype(int)
        # set vertical dashed wall for controlled dash trials
        if mode=="dashes":
            # wall location, expected y at contact (upper-left membrane)
            wy = x0+r
            cy = y0+int(1+(wy-(x0+2))/4)-3
            # wall according to dash pattern (2**7=[0:127]) and world y size
            wall_align = [0]*(cy%7)
            dash_pattern = [int(di) for di in np.binary_repr(dash,7)]*(1+int(self.wsize/7))
            dashed_wall = wall_align+dash_pattern
            self.world[:,wy] = dashed_wall[:self.wsize]
            # south west and north west cases
            if st0==2 or st0==3:
                self.world = np.rot90(self.world,2)
        # 4 dashed walls making hashed world (useful for n>1 gliders?)
        elif mode=="hash":
            dashed_wall = [int(di) for di in np.binary_repr(dash,7)]*(1+int(self.wsize/7))
            self.world[x0-r,:] = dashed_wall[:self.wsize]
            self.world[x0+r,:] = dashed_wall[:self.wsize]
            self.world[:,y0+r] = dashed_wall[:self.wsize]
            self.world[:,y0-r] = dashed_wall[:self.wsize]
        # normal distribution: 1 if val higher/lower than sd, 0 otherwise
        elif mode=="full":
            self.world = np.random.normal(0,1,size=(self.wsize,self.wsize))
            self.world = np.where(self.world>1.25,1,np.where(self.world<-1.25,1,0))
            # leave the surroundings empty
            self.world[x0-5:x0+6,y0-5:y0+5] = 0
        # bounding walls
        self.world[:2,:] = 1
        self.world[:,:2] = 1
        self.world[-2:,:] = 1
        self.world[:,-2:] = 1




###
