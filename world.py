
import numpy as np
import agent
import tree


class Wall:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

class World:
    def __init__(self, xmax=250, ymax=250\
    , n_walls=5\
    , n_trees=5\
    , n_robots=3\
    , energy=1000):
        # init
        self.energy = energy
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.n_robots = n_robots
        # info
        self.objects = []
        self.allocate()

    def allocate(self):
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
                self.opt_walls.append(w)
        # trees
        for n in range(self.n_trees):
            ax = np.random.randint(0,self.xmax)
            ay = np.random.randint(0,self.ymax)
            t = tree.Tree(ax,ay)
            self.trees.append(t)
        # robots
        for n in range(self.n_robots):
            ax = np.random.randint(0,self.xmax)
            ay = np.random.randint(0,self.ymax)
            a = agent.Agent(ax,ay)
            self.agents.append(a)
        self.objects = self.walls+self.trees+self.agents

    def update(self):
        # energy of trees
        for tree in self.trees:
            tree.update()
        # robots states
        for agent in self.agents:
            objects = [o for o in self.objects if o!=agent]
            agent.act(objects)
        self.objects = self.walls+self.trees+self.agents











##
