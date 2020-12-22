
import numpy as np
import r66agent
from rnet import NeuralSpace
from tqdm import tqdm
from copy import deepcopy
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Evaluation:
    def __init__(self, genotype, time=100, reps=2):
        # same for all trials
        self.genotype = genotype
        self.network = NeuralSpace.decode(genotype)
        self.time = time
        self.reps = reps
        self.alphas = [0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5]
        self.av_ft = 0
        self.dt = 0.1
        self.trials = []
        self.evaluate()

    def evaluate(self):
        # trials
        for alpha in self.alphas:
            for rep in self.reps:
                trial = Trial(self.time,self.network,alpha,self.dt)
                self.trials.append(trial)
        # sort results
        self.trials = sorted(self.trials, key=lambda x:x.ft, reverse=True)
        self.av_ft = sum([trial.ft for trial in self.trials])/len(self.trials)


class Trial:
    def __init__(self,network,alpha,time,ev_task=0,dt=0.1):
        # evaluation parameters
        self.alpha = alpha
        self.time = time
        self.dt = dt
        self.ft = 0
        # trial parameters (according to task)
        self.agents = []
        self.trees = []
        # ev task 0 is simply to find a tree in an open world
        if ev_task==0:
            # init agent
            x0 = 0; y0 = 0; o0 = alpha
            self.agents.append(r66.Agent(self.network,x0,y0,o0))
            # init tree(s)
            tr = 2.5
            tx = np.random.randint(10,25)
            ty = np.random.randint(10,25)
            self.trees.append(Tree(tx0,ty0,tr))
        # data for visualization
        # self.xy0 = Point(x0,y0)

    def run(self):
        # time
        self.tx = 0
        while self.tx < self.time:
            self.tx += self.dt
            # updates
            for agent in self.agents:
                xagents = [ag for ag in self.agents if ag!=agent]
                env = xagents+self.trees
                agent.update(env)
            # evaluate
            self.ft_eval()
            # terminating conditions
            if self.ev_task==0:
                if sum([tree.e for tree in self.trees]) == 0:
                    self.tx = self.time+1
        # fitness
        # self.ft =

    def ft_eval(self):
        pass


class Tree:
    def __init__(self,x,y,r):
        self.e = 1
        self.x = x
        self.y = y
        self.r = r
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)

    def update(self, de=0.1):
        self.e -= de
        if self.e <= 0:
            self.area == None



































##


















































#
