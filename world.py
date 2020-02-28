
import numpy as np
import genotype
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
    , genotypes = []):
        # init
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.genotypes = genotypes
        self.n_robots = 3 if len(genotypes)==0 else len(genotypes)
        self.objects = {}
        self.allocate_basics()
        self.allocate_agents()

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
            ax = np.random.randint(0,self.xmax)
            ay = np.random.randint(0,self.ymax)
            t = tree.Tree(ax,ay)
            self.trees.append(t)

        def allocate_agents(self):
        # robots
            nr = 0
            while nr < self.n_robots:
                add = True
                ax = np.random.randint(10,self.xmax-10)
                ay = np.random.randint(10,self.ymax-10)
                ao = np.radians(np.random.randint(0,360))
                # simple check to avoid superposition with trees
                for t in self.trees:
                    if np.linalg.norm(np.array([ax,ay])-np.array([t.x,t.y])) < 10:
                        add = False
                # create or use existent genotypes
                if add:
                    if len(self.genotypes) > 0:
                        gen = self.genotypes[nr]
                    else:
                        gen = genotype.Genotype()
                    ag = agent.Agent(ax,ay,ao,gen)
                    self.agents.append(ag)
                    nr += 1

        # keep data
        self.objects["walls"] = self.walls
        self.objects["trees"] = self.trees
        self.objects["agents"] = self.agents

    def update(self):
        # energy of trees
        for tree in self.trees:
            tree.update()
        # robots states
        for agent in self.agents:
            agents = [ag for ag in self.agents if ag!=agent]
            self.objects["agents"] = agents
            agent.act(self.objects)
        self.objects["trees"] = self.trees
        self.objects["agents"] = self.agents










##
