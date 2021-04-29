
import numpy as np
import ag
import ag_genotype
from shapely.geometry import Point

class Trial:
    def __init__(self,t=300,dt=1,
        worldx=1000,worldy=1000,
        n_trees=10,n_agents=1,
        debug_mode=False):
        # simulation parameters
        self.t=t
        self.dt=dt
        self.worldx = worldx
        self.worldy = worldy
        self.n_agents = n_agents
        self.n_trees = n_trees
        # trees are the same for all trials
        self.trees=[]
        self.allocate_trees()
        self.agents=[]
        # debugging check
        if debug_mode:
            self.debug_trial()

    def run_trial(self,genotype):
        # trials change only initial orientation
        trials_ft = []
        if self.n_agents == 1:
            for o0 in [0,90,180,270]:
                e0 = 50
                self.allocate_single_agent(genotype,o0,e0)
                tx = 0
                agent = self.agents[0]
                while tx < self.t:
                    agent.update([self.agents,self.trees])
                    tx += self.dt
                trials_ft.append(agent.e)
            agent_ft = sum([(i+1)*ft for i,ft in enumerate(sorted(trials_ft,reverse=True))])/4
        # group is future work
        return agent_ft

    def allocate_single_agent(self,genotype,o0,e0):
        # init agent (if only 1 agent: put in the center)
        ax = self.worldx/2
        ay = self.worldy/2
        self.agents = [ag.Agent(genotype,ax,ay,o0,e0,self.dt,self.worldx,self.worldy)]

    def allocate_group(self,genotype):
        na = 0
        self.agents = []
        while na < n_agents:
            allocate = True
            ax = np.random.randint(200,self.worldx-200)
            ay = np.random.randint(200,self.worldy-200)
            ae = 50
            ao = ag_o + np.random_choice([0,90,180,270])
            new_agent = ag.Agent(genotype,ax,ay,ao,ae,self.dt,self.worldx,self.worldy)
            for agent in self.agents:
                if new_agent.area.intersects(agent.area):
                    allocate = False
            if allocate:
                self.agents.append(new_agent)
                na += 1

    def allocate_trees(self):
        # trees randomly, but not close to the agent (avoid ft+ by xy chance)
        nt = 0
        while nt < self.n_trees:
            allocate = True
            # 1: left, 2: right, 3: up, 4: down
            tloc = np.random.choice([1,2,3,4])
            if tloc==1:
                tx = np.random.randint(self.worldx/20,self.worldx/2-self.worldx/10)
                ty = np.random.randint(self.worldy/20,self.worldy-self.worldy/20)
            elif tloc==2:
                tx = np.random.randint(self.worldx/2+self.worldx/10,self.worldx-self.worldx/20)
                ty = np.random.randint(self.worldy/20,self.worldy-self.worldy/20)
            elif tloc==3:
                tx = np.random.randint(self.worldx/20,self.worldx-self.worldx/20)
                ty = np.random.randint(self.worldy/2+self.worldy/10,self.worldy-self.worldy/20)
            elif tloc==4:
                tx = np.random.randint(self.worldx/20,self.worldx-self.worldx/20)
                ty = np.random.randint(self.worldy/20,self.worldy/2-self.worldy/10)
            new_tree = Tree(x=tx,y=ty)
            for tree in self.trees:
                if new_tree.area.intersects(tree.area):
                    allocate = False
            if allocate:
                self.trees.append(new_tree)
                nt += 1

    def debug_trial(self,genotype=None):
        if not genotype:
            genotype = ag_genotype.Genotype()
        # basic agent in the center
        self.worldx = 100
        self.worldy = 100
        self.trees.append(Tree(x=75,y=50,r=10))
        ax = self.worldx/2
        ay = self.worldy/2
        ao = 0
        self.agents.append(ag.Agent(genotype,ax,ay,ao,worldx=self.worldx,worldy=self.worldy))
        agent = self.agents[0]
        # debug commands
        self.debug_t = 0
        self.debug_move(agent,50,0.5,0.5)
        self.debug_move(agent,1,0,0.5)
        self.debug_move(agent,50,0.2,0.2)
        self.debug_move(agent,1,0,1)
        self.debug_move(agent,25,1,1)
        self.debug_move(agent,20,0.8,0.2)
        self.debug_move(agent,10,1,1)
        self.debug_move(agent,10,0,0)
        self.debug_move(agent,25,0.5,0.3)
        self.debug_move(agent,self.t-self.debug_t,0.1,0.1)

    def debug_move(self,agent,time,lm,rm):
        tx = 0
        while tx < time:
            env_info = agent.sensors.update(agent.x,agent.y,agent.o,[self.agents,self.trees])
            agent.data.save(agent.x,agent.y,agent.o,agent.e,agent.sensors,agent.controller)
            agent.action_fx(lm,rm,[self.agents,self.trees])
            tx += 1
        self.debug_t += time


class Tree:
    def __init__(self,x,y,r=10,e=100,color=False):
        self.x = x
        self.y = y
        self.r = r
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)
        self.e = e
        if color:
            self.color = np.random.choice([0,0,1],[0,1,0],[1,0,0])

    def update(self):
        # for size updating according to e
        self.e += 1
        self.r = self.e/10
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)
