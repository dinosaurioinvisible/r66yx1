
import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString


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
            ax = np.random.randint(10,self.xmax-10)
            ay = np.random.randint(10,self.ymax-10)
            tree = Tree(ax,ay)
            self.trees.append(tree)















#
