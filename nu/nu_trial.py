
import numpy as np
from copy import deepcopy
from nu_glider import Glider
from nu_genotype import Genotype
from nu_animation import glx_anim

class Trial:
    def __init__(self,tt=100,wsize=200,auto=False,st0=41,center=True,gtx=None,mode="",dash=0,anim=True):
        self.tt=tt
        self.limit=int(tt/10)
        self.wsize=wsize
        self.world=None
        if auto:
            self.dash_trial(gtx,st0,center,mode,dash,anim)

    '''default trial: st1=SE, single glider, dashed wall world'''
    def run(self,gtx,st0=41,center=True,mode="",dash=0,anim=False):
        # initialize world and glider
        if center:
            x0,y0=int(self.wsize/2),int(self.wsize/2)
        else:
            x0,y0=np.random.randint(10,self.wsize-10,size=(2))
        self.set_world(x0,y0,st0,mode,dash)
        gl = Glider(gtx,st0,x0,y0)
        # run trial
        tlim=0
        for ti in range(self.tt):
            # get world domain
            gl_domain = deepcopy(self.world[gl.i-3:gl.i+4,gl.j-3:gl.j+4])
            # if all core elements are off, it dies
            if np.sum(gl.core)==0:
                return [None,1,0,0]
            # if world object within glider domain (collision), it dies
            if np.sum(gl_domain[1:6,1:6]):
                return [None,0,1,0]
            # if gl doesn't move in time limit, it dies
            elif tlim > self.limit:
                return [None,0,0,1]
            # stop before encounters bounding walls (just in case)
            elif min(gl.i,gl.j)<10 or max(gl.i,gl.j)>self.wsize-10:
                break
            else:
                # allocate and update glider
                gl_domain[1:6,1:6] += gl.st
                gl.update(gl_domain)
                tlim += 1
                if gl.om > 0:
                    tlim=0
        # debug
        # if len(gl.txs) > 0:
        #     print("\n transition? \n")
        #     import pdb; pdb.set_trace()
        # count loops, opt visualization and return
        gl.gl_loops()
        if anim:
            glx_anim(gl,self.world)
        return [gl]

    '''create world and allocate dash patterns'''
    def set_world(self,x0,y0,st0=41,mode="",dash=0,r=5):
        # empty world
        self.world = np.zeros((self.wsize,self.wsize)).astype(int)
        # starting oxy (4=N, 1=E, 2=S, 3=W)
        oxy = int(str(st0)[0])
        # set dashed wall at north
        if mode=="dashes":
            # empty world no dashes
            if dash==0:
                return
            # wall i location (y0 - r)
            wi = y0 -r
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
            self.world = np.where(self.world>1.25,1,np.where(self.world<-1.25,1,0))
            # leave the surroundings empty
            self.world[x0-5:x0+6,y0-5:y0+5] = 0
        # bounding walls
        self.world[:2,:] = 1
        self.world[:,:2] = 1
        self.world[-2:,:] = 1
        self.world[:,-2:] = 1




###
