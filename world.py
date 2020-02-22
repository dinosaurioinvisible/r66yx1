
import numpy as np

class World:
    def __init__(self, xmax=250, ymax=250\
    , n_walls=4\
    , n_trees=5, tree_radius=2.5\
    , energy=1000):
        # init
        # self.energy = energy
        self.xmax = xmax
        self.ymax = ymax
        self.n_walls = n_walls
        self.n_trees = n_trees
        # self.tree_radius = tree_radius
        self.allocate()

    def allocate(self):
        # borders
        self.walls = []
        self.walls.append([[0,0],[self.xmax,0]])
        self.walls.append([[0,0],[0,self.ymax]])
        self.walls.append([[0,self.ymax],[self.xmax,self.ymax]])
        self.walls.append([[self.xmax,0],[self.xmax,self.ymax]])
        # optional walls
        if self.n_walls>4:
            for n in range(self.n_walls-4):
                ax = np.random.randint(0,self.xmax)
                ay = np.random.randint(0,self.ymax)
                bx = np.random.randint(0,self.xmax)
                by = np.random.randint(0,self.ymax)
                self.walls.append(["wall",[ax,ay],[bx,by]])
        # trees
        self.trees = []
        for n in range(self.n_trees):
            ax = np.random.randint(0,self.xmax)
            ay = np.random.randint(0,self.ymax)
            self.trees.append(["tree",[ax,ay],[ax,ay]])
        self.objects = self.walls+self.trees

    def update(self, robots_locs=[]):
        # just robots positions for now
        self.robots = []
        for robot_loc in robots_locs:
            self.robots.append("robot", robot_loc, robot_loc)
        self.objects = self.walls+self.trees+self.robots
