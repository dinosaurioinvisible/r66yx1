
import numpy as np
from helperfxs import *

class World:
    def __init__(self,size=25,fill_sd=2.5):
        # fill grid
        if fill_sd == 0:
            self.grid = np.zeros((size,size)).astype(int)
        else:
            self.grid = np.random.normal(0,1,size=(size,size))
            self.grid = np.where(self.grid>fill_sd,1,np.where(self.grid<-fill_sd,1,0)).astype(int)

    # gol updating rule, but allocating agents first
    def update(self,agents=[]):
        # agents are updated first and allocated before updating world
        for agent in agents:
            self.grid[agent.i-2:agent.i+3,agent.j-2:agent.j+3] = agent.state.astype(int)
        # transition grid
        xgrid = self.grid.astype(int)
        # update according to GoL rule
        for ei,vi in enumerate(xgrid):
            for ej,vij in enumerate(vi):
                nb = np.sum(xgrid[ei-2:ei+3,ej-2:ej+3]) - vij
                vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and nb==3) else 0
                self.grid[ei,ej] = vx

class Agent:
    def __init__(self,i,j,xells,cfg0=None):
        self.i, self.j = i,j
        self.xells = xells
        self.state = np.random.randint(0,2,(3,3)) if cfg0==None else cfg0


    def update(self,agent_domain):
        agent_domain[1:-1,1:-1] = self.state.astype(int)
        for xi,xell in enumerate(self.xells):
            agent_domain[1+di:4+di,1+dj:4+dj]

        for di in range(3):
            for dj in range(3):
                env = agent_domain[1+di:4+di,1+dj:4+dj]


class Xell:
    def __init__(self,gt=None,i=None,j=None,o=None,sx=None):
        # genotype [1x512]
        self.gt = gt
        self.i,self.j = i,j
        # 0:N, 1:E, 2:S, 3:S
        self.o = o
        self.sx = sx

    def update(self,env):
        # re-oriented input
        rx = array2int(env,r=self.o)
        # 0:3 no signal, 4:7 signal
        self.sx,self.o = (1,rx-4) if rx>3 else (0,rx)

# class Trial:
#     def __init__(self,tt=100,wdim=20,fill_sd=2.5):
#         # trial time
#         self.tt = tt
#         # define world
#         if fill_sd == 0:
#             self.world = np.zeros((wdim,wdim)).astype(int)
#         else:
#             self.world = np.random.normal(0,1,size=(wdim,wdim))
#             self.world = np.where(self.world>fill_sd,1,np.where(<-fill_sd,1,0))
#         # make agents
#         xy0 = int(wdim/2)
#         self.world[xy0-5:xy0+6,xy0-5:xy0+6] = 0
#         self.agents = agents
#
# class Glx:
#     def __init__(self,x,y,gts,cfg0):
#         self.x = x; self.y = y
#         self.cells = []
#         self.make_glx(gts,cfg0)
#
#     def update(self,world):
#         pass
#
#     def make_glx(self,gts):
#         locs = xy_around(self.x,self.y)
#         for i,gt in enumerate(gts):
#             self.cells.append(Xel(gt,xy=locs[i],o=cfg[i][0],sx=cfg[i][1]))
#
