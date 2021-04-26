
import numpy as np
import ag
import ag_genotype
from shapely.geometry import Point

class Trial:
    def __init__(self, genotype=None, t=300, dt=1, worldx=1000, worldy=1000, mode="debug", n_trees=20, n_agents=1):
        self.t=t
        self.dt=dt
        self.worldx = worldx
        self.worldy = worldy
        # fill world with trees
        self.trees=[]
        self.agents=[]
        self.allocate(n_trees,n_agents)
        # debugging check and run
        if mode == "debug":
            self.debug_trial()
        else:
            self.run_trial()

    def run_trial(self):
        tx = 0
        while tx < self.t:
            for agent in self.agents:
                agent.update([self.agents,self.trees])
            for tree in self.trees:
                tree.update()

    def allocate(self,n_trees,n_agents):
        nt = 0
        while nt < n_trees:
            allocate = True
            tx = np.random.randint(50,self.worldx-50)
            ty = np.random.randint(50,self.worldy-50)
            new_tree = Tree(x=tx,y=ty)
            for tree in self.trees:
                if new_tree.area.intersects(tree.area):
                    allocate = False
            if allocate:
                self.trees.append(new_tree)
                nt += 1
        # init agent
        self.agents=[]
        if not genotype:
            genotype = ag_genotype.Genotype()
        na = 0
        while na < n_agents:
            allocate = True
            ax = np.random.randint(200,self.worldx-200)
            ay = np.random.randint(200,self.worldy-200)
            ao = np.radians(np.random.choice([0,90,180,270]))
            ae = 100
            new_agent = ag.Agent(genotype,ax,ay,ao,ae,self.dt,self.worldx,self.worldy)
            for agent in self.agents:
                if new_agent.area.intersects(agent.area):
                    allocate = False
            if allocate:
                self.agents.append(new_agent)
                na += 1

    def debug_trial(self):
        self.trees = []
        agent = self.agents[0]
        agent.x = 500
        agent.y = 500
        agent.o = 0
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
            agent.action_fx(lm,rm,[self.agents,self.trees])
            agent.data.save(agent.x,agent.y,agent.o,agent.e,agent.sensors,agent.controller)
            tx += 1
        self.debug_t += time


class Tree:
    def __init__(self, e=10, x=None, y=None, r=10):
        self.e = e
        self.x = x
        self.y = y
        self.r = r
        loc = Point(self.x,self.y)
        self.area = loc.buffer(self.r)

    def update(self):
        self.e += 1
