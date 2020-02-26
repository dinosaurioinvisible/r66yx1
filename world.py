
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
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.n_robots = n_robots
        self.energy = energy
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
        nr = 0
        while nr < self.n_robots:
            add = True
            ax = np.random.randint(10,self.xmax-10)
            ay = np.random.randint(10,self.ymax-10)
            # simple check to avoid superposition with trees
            for t in self.trees:
                if np.linalg.norm(np.array([ax,ay])-np.array([t.x,t.y])) < 10:
                    add = False
            if add:
                ag = agent.Agent(ax,ay)
                self.agents.append(ag)
                nr += 1
        # keep data
        self.objects = self.walls+self.opt_walls+self.trees+self.agents

    def update(self):
        # energy of trees
        for tree in self.trees:
            tree.update()
        # robots states
        for agent in self.agents:
            objects = [o for o in self.objects if o!=agent]
            agent.act(objects)
        self.objects = self.walls+self.opt_walls+self.trees+self.agents











##
