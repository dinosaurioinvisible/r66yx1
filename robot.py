# coding: utf-8

## TODO:
# sensors range is max range, it should be dynamic (~attention)?
#

import numpy as np
#import grid


class Cell:
    def __init__(self, size=2, inside=None):
        self.inside = inside

class Food:
    def __init__(self, )

class SimWorld:
    def __init__(self, xmax=100, ymax=100):
        # world starting from (0,0), just postive coords
        self.xmax = xmax
        self.ymax = ymax
        self.world = np.full((self.xmax, self.ymax), None)

    def init_world(self):
        # cells
        for i in range(0,len(grid),Cell.size):
            for j in range(0,len(grid[i]),Cell.size):
                grid[i,j] = Cell()
        # food sources


        # allocate agents

    def allocate_food(self, n=1, food):
        for i in range(n):
            x = np.random.randint(self.xmin, self.xmax)
            y = np.random.randint(self.ymin, self.ymax)
            if grid[x,y] grid[x,y] = food



class Food:
    def __init__(self, food_type=):
        self.food_type = food_type

    def allocate(self):
        if self.food_type == "tree":

        elif self.food_type == "":
            y
        else:




class Robot:
    # robrad = 6.5          # robot outer radius
    # rob_toprad = 5.75     # radius top body where sensors are
    # wheel_sep = 10        # distance between the wheels along axe
    # sim_time_speed = 0.1
    # num_IRs = 6           # 6 proximity IRs?
    # motor_noise = 0.4
    #
    # num_IR = 6            # number of proximity sensors ?
    # raylen = 25           # length of IR ray
    # ir_noise = 50         # IR sensor noise
    # ir_spread = 0.873     # spread of the ir beam in radians (50 degrees)
    # ir_coef = 1           # reflection coefficient
    def __init__ (self, size=5\
    , fs_number=1, fs_loc=0, fs_range=20\
    , ps=4, ps_loc=4, ps_range=6\
    , wheel_sep=5, vel=1\
    , energy=50):
        self.size = size
        self.fs_number = fs_number
        self.fs_loc = fs_loc
        self.fs_range = fs_range
        self.ps = ps_number
        self.ps_loc = ps_loc
        self.ps_range = ps_range
        self.wheel_sep = wheel_sep
        self.vel = vel
        self.energy = energy
        # features for moving
        self.xloc = np.random.randint(grid.xmin, grid.xmax)
        self.yloc = np.random.randint(grid.ymin, grid.ymin)
        #self.orientation = np.radians(np.random.randint(0,360))
        #self.lw_loc = [self.xloc-(self.wheel_sep/2),self.yloc]
        #self.lw_vel = 0
        #self.rw_loc = [self.xloc+(self.wheel_sep/2),self.yloc]
        #self.rw_vel = 0
        self.dest = False


    # move_robot
    # robot_speed
    # collision
    # wall_collision
    # uniform_noise
    # read_IRs
    # ray_hit
    # IRval
    # fullIRval
    # ray_hit_nearest
    # ray_end
    # ir_reading
    # init_robot

    def sens(self):
        self.food = []
        for fsensor in fs_number:
            # define sensing area
            for i in range(self.xloc-self.fs_range, self.xloc+self.fs_range+1):
                for j in range(self.yloc-self.fs_range, self.yloc+self.fs_range+1):
                    # if food, take note
                    if grid[i,j] > 0:
                        rx = i-self.xloc
                        ry = j-self.yloc
                        r = np.sqrt(x**2+y**2)
                        self.food.append([r, grid[i,j], [i,j]])

    # neural network (input -> percept input -> percept output -> output)
    def decide(self):
        try:
            self.dest = min(self.food)
        except:
            self.dest = False

    def move(self):
        # turn
        if self.dest:
            xdest = self.dest[0][0]
            ydest = self.dest[0][1]
            # dtheta = (self.lw-self.rw)/self.wheel_sep
            # dtheta = np.arctan2(ydest-self.yloc, xdest-self.xloc)
            # self.orientation += dtheta
            # move
            # self.vel = (self.lw_vel+self.rw_vel)/2
            if self.xloc != xdest:
                self.xloc += self.vel*(xdest/np.abs(xdest))
            if self.yloc != ydest:
                self.yloc += self.vel*(ydest/np.abs(ydest))
        else:
            # random/easier move
            # other = np.radians(np.random.randint(0,360))
            # self.orientation = np.random.choice([self.orientation, other])
            # move
            self.xloc = self.vel*np.random.choice([1,0,-1])
            self.yloc = self.vel*np.random.choice([1,0,-1])
        self.energy += -1

    def check_energy(self):
        if self.energy == 0 and self.size == 1:
            sys.stdout.write("the robot is dead")
        elif self.energy == 0:
            self.size += -1
            self.energy = 50
        elif self.energy == 100:
            self.size += 1
            self.energy = 50















#
