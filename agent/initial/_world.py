
import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon

class Wall:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        # shapely object
        self.area = LineString([(self.xmin,self.ymin),(self.xmax,self.ymax)])

class Tree:
    def __init__(self, x, y, r=5, energy=10000):
        # r=2.5 base
        # r=5 for world_size=1000
        # r=12.5 for one tree only experiments
        self.x = x
        self.y = y
        self.r = r
        self.initial_energy = energy
        self.energy = energy
        # shapely object
        pos = Point(self.x, self.y)
        self.area = pos.buffer(self.r)

class World:
    def __init__(self, xmax=250, ymax=250\
    , n_walls=4\
    , n_trees=10\
    , debug=False):
        # bounds
        self.xmax = xmax
        self.ymax = ymax
        self.bounds = Polygon([(0,0),(0,self.ymax),(self.xmax,self.ymax),(self.xmax,0)])
        # objects
        self.n_walls = n_walls
        self.n_trees = n_trees
        self.walls = []
        self.trees = []
        #self.agents = []
        self.allocate_walls()
        self.allocate_trees()

    def allocate_walls(self):
        # create delimited space
        w1 = Wall(0,0,self.xmax,0)
        w2 = Wall(0,0,0,self.ymax)
        w3 = Wall(0,self.ymax,self.xmax,self.ymax)
        w4 = Wall(self.xmax,0,self.xmax,self.ymax)
        self.walls = [w1,w2,w3,w4]
        # optional walls
        for n in range(self.n_walls-4):
            ax = np.random.randint(0,self.xmax)
            ay = np.random.randint(0,self.ymax)
            bx = np.random.randint(0,self.xmax)
            by = np.random.randint(0,self.ymax)
            w = Wall(ax,ay,bx,by)
            self.walls.append(w)

    def allocate_trees(self):
        # trees
        for n in range(self.n_trees):
            ax = np.random.randint(10,self.xmax-10)
            ay = np.random.randint(10,self.ymax-10)
            tree = Tree(ax,ay)
            self.trees.append(tree)















#
