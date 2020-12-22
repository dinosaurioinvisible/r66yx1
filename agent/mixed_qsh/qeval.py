
import numpy as np
import qagent
import qnet
import geometry as geom
from tqdm import tqdm
from copy import deepcopy
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Evaluation:
    def __init__(self, genotype, time=300, reps=2):
        # for all trials (from Quinn thesis and Shibuya et al)
        self.genotype = genotype
        self.nx_space = qnet.NeuralSpace()
        self.network = self.nx_space.decode(genotype)
        self.time = time
        self.reps = reps
        self.alphas = [0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5]
        self.av_ft = 0
        self.dt = 0.1
        # self.data_dt = 1
        self.trials = []
        self.evaluate()

    def evaluate(self):
        alphas = self.alphas*self.reps
        for alpha in tqdm(alphas):
            trial = Trial(self.time,self.network,alpha,self.dt)
            self.trials.append(trial)
        # sort results
        self.trials = sorted(self.trials, key=lambda x:x.ft, reverse=True)
        self.av_ft = sum([trial.ft for trial in self.trials])/len(self.trials)


class Trial:
    def __init__(self,time,network,alpha,dt=0.1,data_dt=1):
        # basics
        self.network = network
        self.time = time
        self.alpha = alpha
        self.dt = dt
        self.data_dt = data_dt
        # parameters as in Shibuya et al.
        self.agsR = 2.9
        self.di = 1.25
        self.cmax = 10
        self.dmax = 40
        self.dist = 0
        self.max_dist = 0
        self.cols = 0
        self.cp = 1
        self.ft = 0
        # data for visualization
        self.triangles=[]
        self.data_gt=[]
        self.data_st=[]
        self.data_ft=[]
        self.data_cp=[[0,1]]
        # data for transfer entropy
        self.states = []
        # self.i_given_ij = Counter()
        self.te_frame = 50
        # allocate agents (Shibuya et al)
        self.agents = []
        y0 = np.sqrt((2*(self.di+self.agsR))**2 - (self.di+self.agsR)**2)
        o0 = geom.force_angle(np.radians(300)+self.alpha)
        self.agents.append(qagent.Agent(self.network,0,y0,o0))
        x1 = -(self.agsR+self.di)
        o1 = geom.force_angle(np.radians(60)+self.alpha)
        self.agents.append(qagent.Agent(self.network,x1,0,o1))
        x2 = self.agsR+self.di
        o2 = geom.force_angle(np.radians(180)+self.alpha)
        self.agents.append(qagent.Agent(self.network,x2,0,o2))
        # initial allocations data
        self.triangle = Polygon([[ag.x,ag.y] for ag in self.agents])
        self.xy0 = self.triangle.centroid
        self.ags_dist = [agent.body.distance(self.xy0) for agent in self.agents]
        self.save_data()
        self.run()


    def run(self):
        # run trial
        # for ti in range(self.time):
        self.tx = 0
        while self.tx < self.time:
            self.tx += self.dt
            # update info from environment, net and movement
            for agent in self.agents:
                xagents = [ag for ag in self.agents if ag!=agent]
                agent.update(xagents)
            # evaluate group and save
            self.cols += sum([ag.cols for ag in self.agents])
            self.triangle = Polygon([[ag.x,ag.y] for ag in self.agents])
            self.dist = self.triangle.centroid.distance(self.xy0)
            self.ags_dist = [agent.body.distance(self.triangle.centroid) for agent in self.agents]
            self.ft_eval()
            # if cols > cmax: end trial
            if self.cols > self.cmax:
                self.tx = self.time
        # fitness at the end of trial (ft * collision penalty)
        self.ft = self.ft*self.cp

    def ft_eval(self):
        # evaluation of traveled distance
        if self.dist <= self.max_dist:
            gt = 0
        elif self.max_dist >= self.dmax:
            gt = 0
        else:
            # so max_dist < dist < dmax
            gt = self.dist - self.max_dist
            self.max_dist = self.dist
        # evaluation of closeness
        st = 0
        for ag_dist in self.ags_dist:
            st += 4*self.agsR - ag_dist
        stft = 1 + 2*np.tanh(st/(8*self.agsR))
        # distance * closeness
        dft = gt * stft
        self.ft += dft
        # collisions
        cp = max(0,1.0-(self.cols/(1+self.cmax)))
        if cp < self.cp:
            self.cp = cp
            self.data_cp.append([self.tx,self.cp])        
        # save for analysis
        if self.tx%self.data_dt<self.dt:
            self.save_data(gt,st,stft,dft)


    def save_data(self, gt=0,st=0,stft=0,dft=0):
        self.triangles.append(self.triangle)
        self.data_gt.append([round(self.dist,2), round(self.max_dist,2),round(gt,2)])
        d1,d2,d3 = [round(dx,2) for dx in self.ags_dist]
        self.data_st.append([d1,d2,d3, round(st,2),round(stft,2)])
        self.data_ft.append([round(dft,2),deepcopy(self.ft)])















#
