# coding: utf-8

## TODO:
# dynamic plot
# sensors range is max range, it should be dynamic (~attention)?

import numpy as np


class Cell:
    def __init__(self, location, inside=np.array([])):
        self.location = location
        self.inside = inside

class Food:
    def __init__(self, x=0, y=0, energy=10, grow_rate=1, limit=100):
        self.name = "food"
        ##
        self.x = x
        self.y = y
        self.energy = energy
        self.grow_rate = grow_rate
        self.limit = limit

    def regrow(self):
        self.energy += self.energy*self.grow_rate
        self.energy = self.limit if self.energy > self.limit else self.energy

class Robot:
    def __init__(self, x=0, y=0, orientation=0\
    , radius=2, energy=50\
    , vel=1, wheel_sep=2\
    , fsens=2, fsens_loc=1, fsens_range=10\
    , vsens=4, vsens_loc=2, vsens_range=10):
        self.name = "robot"
        ##
        self.x = 0
        self.y = 0
        self.orientation = orientation
        ##
        self.radius = radius
        self.vel = vel
        self.wheel_sep = wheel_sep
        self.energy = energy
        self.fsens = fsens
        self.fsens_loc = fsens_loc
        self.fsens_range = fses_range
        self.vsens = vsens
        self.vsens_loc = vsens_loc
        self.vsens_range = vsens_range

    def move(self):
        vel = (l_speed+r_speed)/2
        dx = vel*np.sin(self.orientation)
        dy = vel*np.cos(self.orientation)
        do = 
        self.x += dx
        self.y += dy
        self.orientation += do


class SimWorld:
    def __init__(self, xmax=2, ymax=2, foods=1, robots=2):
        # world starting from (0,0), just positive coords
        self.xmax = xmax
        self.ymax = ymax
        self.foods = foods
        self.robots = robots
        ##
        self.init_world()
        self.show()

    def init_world(self):
        # cells
        self.world = np.full((self.xmax, self.ymax), None)
        for i in range(len(self.world)):
            for j in range(len(self.world[i])):
                self.world[i,j] = Cell(location=[i,j])
        for n in range(self.foods):
            self.allocate_food()
        for n in range(self.robots):
            self.allocate_robots()

    def allocate_food(self):
        x = np.random.randint(0, self.xmax)
        y = np.random.randint(0, self.ymax)
        self.world[x,y].inside = np.append(self.world[x,y].inside, Food(x=x,y=y))
        print("\nfood source at [{},{}]".format(x,y))

    def allocate_robot(self):
        x = np.random.randint(0, self.xmax)
        y = np.random.randint(0, self.ymax)
        o = np.radians(np.random.randint(0,360))
        self.world[x,y].inside = np.append(self.world[x,y].inside, Robot(x=x,y=y, orientation=o))
        print("\nrobot at [{},{}]".format(x,y))

    def update(self):
        pass

    # only for now, until the dynamic plot
    def show(self):
        map = np.full((self.xmax, self.ymax), None)
        for i in range(len(self.world)):
            for j in range(len(self.world[i])):
                if len(self.world[i,j].inside) > 0:
                    map[i,j] = [x.name for x in self.world[i,j].inside]
        print(map)



















#
