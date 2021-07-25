
import numpy as np
from nu_glider import Glider
from nu_glider_v2 import BasicGlider
from nu_genotype import Genotype
from nu_animation import glx_anim

class Trial:
    def __init__(self,tt=100,wsize=100,auto=False,gtx=None,st0=41,anim=False):
        self.tt=tt
        self.limit=int(tt/10)
        self.wsize=wsize
        self.world=None
        if auto:
            self.full(gtx,st0,anim=True)

    '''try behavior for every dash possible'''
    def behavior(self,gt,st0=41,single_dash=0,anim=False,save=False):
        # initialize glider
        x0,y0 = int(self.wsize/2),int(self.wsize/2)
        if type(gt)==BasicGlider:
            gl=gt
        else:
            gl = BasicGlider(gt,st0)
        results = np.zeros(128).astype(int)
        # for some specific case
        if single_dash>0:
            gl.set_cfg(st0,x0,y0)
            self.set_world(st0,x0,y0,mode="dash",dash=single_dash)
            tlim=0
            for ti in range(self.tt):
                gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
                if np.sum(gl_domain[1:6,1:6])>0 or tlim>self.limit:
                    break
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim = 0 if gl.ox > 0 else tlim+1
        else:
            # try behavior for every dash
            for dx in range(1,128):
                # set dashed wall, x0,y0 and orientation
                gl.set_cfg(st0,x0,y0)
                self.set_world(st0,x0,y0,mode="dash",dash=dx)
                # run trial
                rx=1
                tlim=0
                for ti in range(self.tt):
                    gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
                    # collision
                    if np.sum(gl_domain[1:6,1:6])>0 or tlim>self.limit:
                        rx=0
                        break
                    # arrived to bounds
                    if not 5<gl.i<self.wsize-5 or not 5<gl.j<self.wsize-5:
                        rx=2
                        break
                    # update
                    else:
                        gl_domain[1:6,1:6] += gl.st
                        gl.update(gl_domain)
                        tlim = 0 if gl.ox > 0 else tlim+1
                results[dx] = rx
        results[0] = np.sum(np.where(results>0,1,0))
        if anim:
            glx_anim(gl,self.world,basic=True,save=save)
        return [gl,results]

    '''randomly fully filled world'''
    def full(self,gt,st0=41,anim=False):
        # initialize world and glider
        x0,y0=int(self.wsize/2),int(self.wsize/2)
        self.set_world(st0,x0,y0,mode="full")
        if type(gt)==BasicGlider:
            gl=gt
            gl.set_cfg(st0,x0,y0)
            basic=True
        else:
            gl=Glider(gt,st0,x0,y0)
            basic=False
        # run trial
        tlim=0
        for ti in range(self.tt):
            # get world domain
            gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
            # if world object within glider domain (collision), it dies
            if np.sum(gl_domain[1:6,1:6]):
                break
            # if gl doesn't move in time limit, it dies
            elif tlim > self.limit:
                break
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim = 0 if gl.ox > 0 else tlim+1
        if anim:
            glx_anim(gl,self.world,basic=basic)
        return gl

    '''default trial: st41=NE, single glider, dashed wall world'''
    def dashes(self,gtx,st0=41,dash=0,anim=False):
        # initialize world and glider
        x0,y0=int(self.wsize/2),int(self.wsize/2)
        self.set_world(st0,x0,y0,mode="dash",dash=dash)
        gl = Glider(gtx,st0,x0,y0)
        # run trial
        tlim=0
        for ti in range(self.tt):
            # get world domain
            gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
            # if all core elements are off, it dies
            if np.sum(gl.core)==0:
                if anim:
                    glx_anim(gl,self.world)
                return 0
            # if world object within glider domain (collision), it dies
            elif np.sum(gl_domain[1:6,1:6]):
                if anim:
                    glx_anim(gl,self.world)
                return 1
            # if gl doesn't move in time limit, it dies
            elif tlim > self.limit:
                if anim:
                    glx_anim(gl,self.world)
                return 2
            # stop before encounters bounding walls (just in case)
            elif min(gl.i,gl.j)<10 or max(gl.i,gl.j)>self.wsize-10:
                break
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim += 1
                if gl.ox > 0:
                    tlim=0
        # end and return
        gl.gl_loops()
        if anim:
            glx_anim(gl,self.world)
        return gl

    '''create world and allocate dash patterns'''
    def set_world(self,st0=41,x0=50,y0=50,mode="",dash=0,r=5,gl_motion=None):
        # empty world
        if mode != "complex_dash":
            self.world = np.zeros((self.wsize,self.wsize)).astype(int)
        # starting oxy (4=N, 1=E, 2=S, 3=W)
        oxy = int(str(st0)[0])
        # set dashed wall at north
        if mode=="dash":
            if dash==0:
                return
            wi = y0-r
            dj = int(str(st0)[1])
            if dj==1 or dj==2:
                wj = x0-3+int(r/4)
            else:
                wj = x0+3-int(r/4)
            dx = [int(di) for di in np.binary_repr(dash,7)]
            self.world[wi,wj:wj+7] = dx
            rot = 4-oxy
            self.world = np.rot90(self.world,rot)
        # allocate second wall according to gl motion
        elif mode=="complex_dash":
            # dash binary pattern
            dx = [int(di) for di in np.binary_repr(dash,13)]
            dx1,dx2 = dx[:7],dx[7:]
            # go trough space in wall
            if gl_motion==4:
                return
            # horizontal motion
            if gl_motion==1:
                wj = x0+3+1
            elif gl_motion==3:
                wj = x0-3-1
            # reverse motion
            # TODO
        # same but repeated pattern
        elif mode=="dashes":
            # empty world no dashes
            if dash==0:
                return
            # wall i location (y0 - r)
            wi = y0-r
            # dash j starting point (x0+gl_size + j-steps (1 per cycle))
            wj = x0-3 + int(r/4)
            # create dashed wall (align+repeated pattern)
            dx = [int(di) for di in np.binary_repr(dash,7)]
            align = (wj%7)+1
            dx_wall = [0]*align + dx*int(self.wsize/5)
            self.world[wi] = dx_wall[:self.wsize]
            # rotate according to initial orientation (rot90 rotates left)
            rx = 4-oxy
            self.world = np.rot90(self.world,rx)
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
            self.world = np.where(self.world>2.2,1,np.where(self.world<-2.2,1,0))
            # leave the surroundings empty
            self.world[x0-5:x0+6,y0-5:y0+5] = 0
        # bounding walls
        self.world[:2,:] = 1
        self.world[:,:2] = 1
        self.world[-2:,:] = 1
        self.world[:,-2:] = 1




###
