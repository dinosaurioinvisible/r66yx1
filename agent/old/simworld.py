
import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString
import simagent


class Wall:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        # shapely object
        self.area = LineString([(self.xmin,self.ymin),(self.xmax,self.ymax)])

class Tree:
    def __init__(self, x, y, r=5, energy=10000, feeding_rate=3):
        self.x = x
        self.y = y
        self.r = r
        self.initial_energy = energy
        self.energy = energy
        self.feeding_rate = feeding_rate
        # shapely object
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

    def update(self):
        self.energy += 1

class World:
    def __init__(self, xmax=250, ymax=250\
    , n_walls=5\
    , n_trees=5):
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.walls = []
        self.trees = []
        self.agents = []
        self.allocate()

    # create delimited space with inner wall(s) and trees
    def allocate(self):
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

    # introduce agents
    def allocate_agents(self, n_agents=3, genotype=None):
        while len(self.agents) < n_agents:
            add = True
            ax = np.random.randint(10,self.xmax-10)
            ay = np.random.randint(10,self.ymax-10)
            ao = np.radians(np.random.randint(0,360))
            # simple check to avoid superposition with trees
            for t in self.trees:
                if np.linalg.norm(np.array([ax,ay])-np.array([t.x,t.y])) < t.r+20:
                    add = False
            # create agents (clonal)
            if add:
                # if genotype is None, will be called from agent
                ag = simagent.Agent(ax,ay,ao,genotype)
                self.agents.append(ag)

    def update(self):
        # feeding
        for tree in self.trees:
            n_feeding_ags = 0
            for agent in self.agents:
                if tree.area.intersects(agent.feeding_area):
                    n_feeding_ags += 1
            # so they get benefited from feeding together
            e = (tree.feeding_rate**n_feeding_ags)*n_feeding_ags
            # check trees' energy
            if e <= tree.energy:
                tree.energy -= e
            else:
                e = tree.energy
                tree.energy = 0
            for agent in self.agents:
                if n_feeding_ags > 0:
                    agent.energy += e/n_feeding_ags
        # robots motor responses
        for agent in self.agents:
            agents = [ag for ag in self.agents if ag!=agent]
            # update agents' x, y, o
            world_objects = self.walls+self.trees+agents
            agent.update(world_objects)

    def reset(self):
        # reset trees and agents
        for tree in self.trees:
            tree.energy = tree.initial_energy
        self.agents = []








##
