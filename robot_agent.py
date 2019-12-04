
import numpy as np
import geometry
import world
import evol_net

class Robot:
    def __init__(self, energy=100\
    , pos="random", orientation=0\
    , radius=world.xmax/100, speed=world.xmax/100\
    , n_irs=2, ray_angle=60, ray_length=20, n_rays=5, ray_spread=50\
    , fs_angle=180, fs_range=25, fs_noise=0):
    # , n_hidden=5, ut=0.5, lt=0.1, learning=0.4):
        # energy
        self.energy = energy
        # x, y
        if pos=="center":
            self.x = world.xmax/2
            self.y = world.ymax/2
        elif pos=="random":
            self.x = np.random.randint(world.xmax)
            self.y = np.random.randint(world.ymax)
        else:
            self.x = float(input("x: "))
            self.y = float(input("y: "))
        # movement
        self.position = np.array([self.x, self.y])
        self.orientation = orientation
        self.radius = radius
        self.speed = speed
        self.wheel_sep = radius
        # ir sensors
        self.n_irs = n_irs
        self.ir_reading = [None]*self.n_irs
        self.ray_length = ray_length
        self.n_rays = n_rays
        self.ray_spread = np.radians(ray_spread)
        self.ir_noise = 50
        self.irs = []
        self.ir_sensors = []
        self.allocate_irs()
        # food sensor
        self.fs_reading = None
        self.fs_angle = fs_angle
        self.fs_range = fs_range
        self.fs_noise = fs_noise
        self.trees_locs = [tree for tree in world.trees]
        self.tree_r = world.tree_radius
        # rnn
        # self.net = evol_net.RNN()
        self.net = []
        # act (save parameters to return)
        self.parameters = [self.radius, self.ray_length, self.fs_angle, self.fs_range]
        self.data = []
        self.notes = None
        # self.act()


    def act(self):
        # actions for each timestep
        self.read_ir()
        self.read_fs()
        self.move()
        self.update_sensors()
        # join ir_sensors and ir_readings data
        ir_data = [a+[b] for a,b in zip(self.ir_sensors, self.ir_reading)]
        # data: [position, orientation, ir_data, fs_reading, notes, energy]
        self.energy -= 1
        self.data.append([self.position, int(np.degrees(self.orientation)), ir_data, self.fs_reading, self.notes, self.energy])
        self.notes = None

    def update_sensors(self):
        # update information from ir sensors
        self.ir_sensors = []
        for sensor in self.irs:
            sx = self.x+sensor[0][0]
            sy = self.y+sensor[0][1]
            so = geometry.force_angle(self.orientation+sensor[1])
            ll_ray = geometry.force_angle(so+sensor[2][0])
            rr_ray = geometry.force_angle(so+sensor[2][-1])
            # [[rel_x, rel_y], rel_angle, left_most_ray, right_most_ray]
            self.ir_sensors.append([[sx,sy], np.degrees(so), np.degrees(ll_ray), np.degrees(rr_ray)])

    def move(self):
        # new x,y and orientation
        ls, rs = self.robot_speed()
        vel = (ls + rs)/2
        dx = vel*np.cos(self.orientation)
        dy = vel*np.sin(self.orientation)
        do = np.radians((ls - rs)/self.wheel_sep)
        # update, but keep x and y within limits
        self.x += dx
        if self.x > world.xmax:
            self.x = world.xmax - self.radius*2
        if self.x < 0:
            self.x = self.radius*2
        self.y += dy
        if self.y > world.ymax:
            self.y = world.ymax - self.radius*2
        if self.y < 0:
            self.y = self.radius*2
        # reset location if find trees
        for tree_loc in self.trees_locs:
            if np.linalg.norm(tree_loc-self.position) < (self.radius+self.tree_r):
                self.notes = "tree"
                self.x = np.random.randint(world.xmax)
                self.y = np.random.randint(world.ymax)
                self.energy += 5
                # do = np.pi
        # bounce with other robots
        # create input for self.robots_locs
        # for each robot do the same that trees
        # update
        self.position = np.array([self.x, self.y])
        self.orientation += do
        self.orientation = geometry.force_angle(self.orientation)

        # what to do after collisions?
        if self.wall_collision() == True:
            #print("collided...")
            self.notes = "collision"
            self.energy -= 10
            # face opposite direction
            self.orientation = geometry.force_angle(self.orientation+np.pi)
        # update sensors parameters
        # irs[i]: [ir_rel_pos, ir_rel_angles[n], ir_rel_rays]
        for i in range(len(self.irs)):
            rel_x = self.radius*np.cos(self.orientation+self.irs[i][1])
            rel_y = self.radius*np.sin(self.orientation+self.irs[i][1])
            self.irs[i][0] = [rel_x, rel_y]

    def robot_speed(self):
        # speed = net output % urgency % noise
        # input for each timestep
        nin = [ir for ir in self.ir_reading] + [self.fs_reading]
        nin = [0 if i==None else i for i in nin]
        lw, rw = self.net.next(nin)
        # multiply for max speed and add noise
        lw = lw *self.speed #+ np.random.randn()*0.4
        rw = rw *self.speed #+ np.random.randn()*0.4
        # add urgency
        # lw *= self.urgency
        # rw *= self.urgency
        return lw, rw

    def wall_collision(self):
        # collision with world walls
        for wall in world.walls:
            # wall: line segment [a,b]
            a = np.array(wall[0])
            b = np.array(wall[1])
            if geometry.shortest_dist(a, b, self.position) <= self.radius:
                #print("\nposition: {}".format(self.position))
                #print("wall, A: {} to B: {}".format(a,b))
                return True

    def allocate_irs(self):
        # sensor only on the top half of the body uniformily distributed
        if self.n_irs == 2:
            ir_rel_angles = [np.radians(315), np.radians(45)]
        else:
            angle_sep = 180/(self.n_irs+1)
            ir_rel_angles = [geometry.force_angle(np.radians(-90+angle_sep*i)) for i in range(1,self.n_irs+1)]
        for n in range(self.n_irs):
            # relative position for each sensor
            ir_rel_x = self.radius*np.cos(ir_rel_angles[n])
            ir_rel_y = self.radius*np.sin(ir_rel_angles[n])
            ir_rel_pos = np.array([ir_rel_x, ir_rel_y])
            # define ray relative angles for beams
            rays_sep = self.ray_spread/(self.n_rays-1)
            # negative for counterclockwise
            ir_rel_rays = [(-self.ray_spread/2)+rays_sep*n for n in range(self.n_rays)]
            # everything relative to location/orientation
            self.irs.append([ir_rel_pos, ir_rel_angles[n], ir_rel_rays])

    def ray_end(self, ir_x, ir_y, angle, rel_angle):
        # end of ray given standard lenght and particular angle
        # angle1: angle of sensor
        # angle2: angle of ray relative to sensor mid
            # anticlockwise is negative
        ray_angle = geometry.force_angle(angle + rel_angle)
        ray_x = ir_x + self.ray_length*np.cos(ray_angle)
        ray_y = ir_y + self.ray_length*np.sin(ray_angle)
        ray_end = np.array([ray_x, ray_y])
        return ray_end

    def ray_hit(self, ir_pos, angle, rel_angle):
        # simple hit test, does the ray hit any walls?
        # position is position of sensor
        # angle is robot orientation
        # rel_angle is relative angle of ray
        ray_end = self.ray_end(ir_pos[0], ir_pos[1], angle, rel_angle)
        for wall in world.walls:
            wall_start = wall[0]
            wall_end = wall[1]
            # does segment [ir_pos, ray_end] intersect with a wall?
            if geometry.intersect(ir_pos, ray_end, wall_start, wall_end):
                return True
        return False

    def ray_hit_nearest(self, ray_start, ray_end):
        # check if ray hit any walls
        # ray is line segment [p1,p2]
        # w1 is index of world for wall hit by ray with shortest dist d
        hit = False
        min_dist = world.xmax
        wall_index = None
        n_wall = 0
        for wall in world.walls:
            # [p1,p2] is the ray, [p3,p4] is the wall
            wall_start = wall[0]
            wall_end = wall[1]
            if geometry.intersect(ray_start, ray_end, wall_start, wall_end):
                # find intersection point
                intersection = geometry.intersection_point(ray_start, ray_end, wall_start, wall_end)
                # distace to intersection from sensor
                dist = np.linalg.norm(ray_start-intersection)
                if dist < min_dist:
                    hit = True
                    wall_index = n_wall
                    min_dist = dist
            n_wall += 1
        return hit, wall_index, min_dist

    def full_ir_val(self, ir_pos, ir_angle, w):
        # reading for a full beam from sensor at [x,y]
        # center ray end (no spread), w: wall index
        ray_end_mid = self.ray_end(ir_pos[0], ir_pos[1], ir_angle, 0)
        # find intersection point from mid ray to wall along ray
        ix = geometry.intersection_point(ir_pos, ray_end_mid, world.walls[w][0], world.walls[w][1])
        # distance from sensor to the intersection point
        dist = np.linalg.norm(ir_pos-ix)
        # convert to val
        val = self.ir_val(dist)
        return val

    def ir_val(self, dist):
        # IR reading for a given distance from empirical fitting data
        # gaussian 3371*e^(-(d/8.5)^2) fits well
        k = -1*(dist/8.5)*(dist/8.5)
        ir_coeff = 1
        val = ir_coeff * 3371 * np.exp(k)
        # from 0 to 3500, far to near
        return val

    def read_fs(self):
        # search trees within sensing area in polar coordinates [dist, angle]
        # arctan2(y,x)
        fs_reading = [[np.linalg.norm(ti-self.position), np.arctan2(ti[1],ti[0]), ti] for ti in self.trees_locs if np.linalg.norm(ti-self.position)<=self.fs_range]
        if len(fs_reading) == 0:
            self.fs_reading = None
        else:
            fs = sorted(fs_reading, key=lambda i:i[0])
            fs_dist = fs[0][0]
            self.fs_reading = self.fs_range/(1+fs_dist)

        # for angle instead of full circle
        # else:
        #     # sort by distance
        #     fs = sorted(fs_reading, key=lambda i:i[0])
        #     # compute the sensing arc
        #     arc_start = geometry.force_angle(self.orientation-np.radians(self.fs_angle/2))
        #     arc_end = geometry.force_angle(self.orientation+np.radians(self.fs_angle/2))
        #     for i in fs:
        #         fs_dist = i[0]
        #         fs_angle = i[1]
        #         # rel angle
        #         fs_angle = self.orientation-fs_angle
        #         fs_pos = i[2]
        #         # because arctan2 only give results between 0 and pi/2
        #         if fs_pos[0]<self.x:
        #             fs_angle = geometry.force_angle(fs_angle+np.pi/2)
        #         if fs_pos[1]<self.y:
        #             fs_angle = geometry.force_angle(fs_angle+np.pi/2)
        #         # check if within range
        #         if fs_angle>arc_start or fs_angle<arc_end:
        #             # convert to value and save (for now)
        #             # self.fs_reading = self.fs_range/(1+fs_dist)
        #             print("\nESTE ES")
        #             print(fs_pos)
        #             self.fs_reading = fs_angle
        #             break
        #         else:
        #             self.fs_reading = None

    def read_ir(self):
        # basically 3 options for left & right most rays of beam:
        # a) don't sense anything: None
        # b) sense the same wall: full_ir_val()
        # c) sense different things: for all rays: hits/n_rays * irval(av_dist)
        self.ir_reading = []
        for ir_sensor in self.irs:
            rel_pos = ir_sensor[0]
            rel_angle = ir_sensor[1]
            rel_rays = ir_sensor[2]
            # angle of mid ray from sensor, clockwise from due north
            ir_angle = geometry.force_angle(self.orientation + rel_angle)
            # position of sensors
            # sens_x = self.x + self.radius*np.cos(sensor_angle)
            # sens_y = self.y + self.radius*np.sin(sensor_angle)
            ir_x = self.x + rel_pos[0]
            ir_y = self.y + rel_pos[1]
            ir_pos = np.array([ir_x, ir_y])
            # bounding rays relative to a central ir beam
            sp_left = rel_rays[0]
            sp_right = rel_rays[-1]
            # position of ray start
            # px = sens_x
            # py = sens_y
            if self.ray_hit(ir_pos, ir_angle, sp_left) == False and self.ray_hit(ir_pos, ir_angle, sp_right) == False:
                # beam misses everything
                self.ir_reading.append(None)
            else:
                # check right and left rays
                left_ray_end = self.ray_end(ir_x, ir_y, ir_angle, sp_left)
                right_ray_end = self.ray_end(ir_x, ir_y, ir_angle, sp_right)
                l_hit, l_wall, l_dist = self.ray_hit_nearest(ir_pos, left_ray_end)
                r_hit, r_wall, r_dist = self.ray_hit_nearest(ir_pos, right_ray_end)
                # if both hit same wall as nearest object
                if l_hit == True and r_hit == True and l_wall == r_wall:
                    val = self.full_ir_val(ir_pos, ir_angle, l_wall)
                # if not, complicated...
                # find wich rays do hit (proportion that do * fullval)
                else:
                    # try to compute average distance
                    n_hits = 0
                    av_dist = 0
                    # loop through the all the beam's rays
                    for ray_angle in rel_rays:
                        i_ray_end = self.ray_end(ir_x, ir_y, ir_angle, ray_angle)
                        ray_hit = self.ray_hit_nearest(ir_pos, i_ray_end)
                        if ray_hit:
                            n_hits += 1
                            av_dist += ray_hit[2]
                    # average value of min distance
                    av_dist /= n_hits
                    # proportional to n rays that hit (proportion of the beam)
                    val = (n_hits/self.n_rays)*self.ir_val(av_dist)
                    # ir noise: random gaussian loc=0, sigma=1 * ir_noise
                    ir_noise = np.random.normal()*self.ir_noise
                    val += ir_noise
                # it can only be positive
                val == 0 if val < 0 else val
                self.ir_reading.append(int(val))
                self.notes = "detection"
















































































        #
