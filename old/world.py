
import numpy as np
import genotype
import agent
# import tree


class Wall:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

class Tree:
    def __init__(self, x=100, y=100, r=5, energy=1000):
        # init
        self.x = x
        self.y = y
        self.r = r
        self.energy = energy

    def update(self):
        self.energy += 1

    def feeding_fx(self, feed_rate, other_agents):
        e = 0
        n_agents = 1
        for agent in other_agents:
            dist = np.linalg.norm(np.array([self.x,self.y])-np.array([agent.x,agent.y])) - agent.r - self.r
            if dist <= agent.feed_range:
                n_agents += 1
        if feed_rate <= self.energy:
            e = feed_rate**n_agents
            self.energy -= e
        return e

class World:
    def __init__(self, xmax=250, ymax=250\
    , n_walls=5\
    , n_trees=5):
        # init
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.objects = {}
        self.allocate_basics()

    def allocate_basics(self):
        self.walls = []
        self.opt_walls = []
        self.trees = []
        self.agents = []
        # borders
        w1 = Wall(0,0,self.xmax,0)
        w2 = Wall(0,0,0,self.ymax)
        w3 = Wall(0,self.ymax,self.xmax,self.ymax)
        w4 = Wall(self.xmax,0,self.xmax,self.ymax)
        self.walls = [w1,w2,w3,w4]
        # optional walls
        if self.n_walls>4:
            for n in range(self.n_walls-4):
                ax = np.random.randint(0,self.xmax)
                ay = np.random.randint(0,self.ymax)
                bx = np.random.randint(0,self.xmax)
                by = np.random.randint(0,self.ymax)
                w = Wall(ax,ay,bx,by)
                self.walls.append(w)
        # trees
        for n in range(self.n_trees):
            ax = np.random.randint(0,self.xmax-10)
            ay = np.random.randint(0,self.ymax-10)
            tree = Tree(ax,ay)
            self.trees.append(tree)
        # store
        self.objects["walls"] = self.walls
        self.objects["trees"] = self.trees

    def allocate_agents(self, n_agents, gen):
        if gen == None:
            gen = genotype.Genotype()
        nr = 0
        while nr < n_agents:
            add = True
            ax = np.random.randint(10,self.xmax-10)
            ay = np.random.randint(10,self.ymax-10)
            ao = np.radians(np.random.randint(0,360))
            # simple check to avoid superposition with trees
            for t in self.trees:
                if np.linalg.norm(np.array([ax,ay])-np.array([t.x,t.y])) < t.r+gen.r:
                    add = False
            # create agents
            if add:
                ag = agent.Agent(ax,ay,ao,gen)
                self.agents.append(ag)
                nr += 1
        # store
        self.objects["agents"] = self.agents

    def update(self):
        # energy of trees
        for tree in self.trees:
            tree.update()
        # print("trees updated")
        # robots states
        for agent in self.agents:
            agents = [ag for ag in self.agents if ag!=agent]
            self.objects["agents"] = agents
            agent.act(self.objects)
        # store new data
        self.objects["trees"] = self.trees
        self.objects["agents"] = self.agents
        # print("agents updated")









##
