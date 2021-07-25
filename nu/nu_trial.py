
import numpy as np
from copy import deepcopy
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

    '''try behavior for every dash {1:127} (if some dash is specified, it will only run that)'''
    def behavior(self,gt,st0=41,dash=0,anim=False,save=False):
        # initialize glider
        x0,y0 = int(self.wsize/2),int(self.wsize/2)
        if type(gt)==BasicGlider:
            gl=gt
        else:
            gl = BasicGlider(gt,st0)
        results = np.zeros(128).astype(int)
        # for some specific case
        if dash>0:
            gl.set_cfg(st0,x0,y0)
            self.set_world(st0,x0,y0,mode="single_dash",dash=dash)
            tlim=0
            for ti in range(self.tt):
                gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
                # collision or timed out
                if np.sum(gl_domain[1:6,1:6])>0 or tlim>self.limit:
                    break
                # arrived to bounds
                if not 5<gl.i<self.wsize-5 or not 5<gl.j<self.wsize-5:
                    break
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim = 0 if gl.ox > 0 else tlim+1
            if anim:
                glx_anim(gl,self.world,dash=dash,save=save)
        else:
            # to compare all trajectories (and avoid more data in gl)
            trajectories = []
            if anim:
                gt_anim = deepcopy(gt)
            # try behavior for every dash
            for dx in range(1,128):
                # set dashed wall, x0,y0 and orientation
                gl.set_cfg(st0,x0,y0)
                self.set_world(st0,x0,y0,mode="single_dash",dash=dx)
                # run trial
                rx=1
                tlim=0
                trajectory = []
                for ti in range(self.tt):
                    gl_domain = self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4].astype(int)
                    trajectory.append([gl.i,gl.j])
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
                trajectories.append(trajectory)
            if anim:
                glx_anim(gt_anim,self.world,trajectories,save=save)
        results[0] = np.sum(np.where(results>0,1,0))
        return [gt,results]

    '''randomly filled world'''
    def random_fill(self,gt,st0=41,anim=False):
        # initialize world and glider
        x0,y0=int(self.wsize/2),int(self.wsize/2)
        self.set_world(st0,x0,y0,mode="random_fill")
        if type(gt)==BasicGlider:
            gl=gt
            gl.set_cfg(st0,x0,y0)
        else:
            gl=BasicGlider(gt,st0)
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
            glx_anim(gl,self.world)
        return gl

    '''create world and allocate dash patterns'''
    def set_world(self,st0=41,x0=50,y0=50,mode="",dash=0,r=5,gl_motion=None):
        # empty world
        self.world = np.zeros((self.wsize,self.wsize)).astype(int)
        # starting oxy (4=N, 1=E, 2=S, 3=W)
        oxy = int(str(st0)[0])
        # set dashed wall at north
        if mode=="single_dash":
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
        # same but repeated pattern to form a wall
        elif mode=="dash_wall":
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
        elif mode=="random_fill":
            self.world = np.random.normal(0,1,size=(self.wsize,self.wsize))
            self.world = np.where(self.world>2.5,1,np.where(self.world<-2.5,1,0))
            # leave the surroundings empty
            self.world[x0-5:x0+6,y0-5:y0+5] = 0
        # bounding walls
        self.world[:2,:] = 1
        self.world[:,:2] = 1
        self.world[-2:,:] = 1
        self.world[:,-2:] = 1




###
