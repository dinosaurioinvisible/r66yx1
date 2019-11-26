
import numpy as np
import geometry
import world

class Robot:
    def __init__(self, energy=100\
    , pos="random", orientation=0\
    , radius=world.xmax/100, wheel_sep=2, motor_noise=0\
    , n_irs=2, ray_length=5, n_rays=5, ray_spread=45, ir_noise=0\
    , fs_range=10, fs_noise=0):
        # energy
        self.energy = energy
        # urgency parameter between 0 and 1
        self.urgency = 0
        # movement
        if pos=="center":
            self.x = world.xmax/2
            self.y = world.ymax/2
        else:
            self.x = np.random.randint(world.xmax)
            self.y = np.random.randint(world.ymax)
        self.position = np.array([self.x, self.y])
        self.orientation = orientation
        self.radius = radius
        self.wheel_sep = wheel_sep
        self.lw_speed = 5
        self.rw_speed = 5
        self.motor_noise = motor_noise  # direct np.random.random() for now
        # ir sensors
        self.ir_reading = None
        self.n_irs = n_irs
        self.ray_length = ray_length
        self.n_rays = n_rays
        self.ray_spread = np.radians(ray_spread)
        self.ir_noise = ir_noise        # direct np.random.random() for now
        self.irs = []
        self.ir_sensors = []
        self.allocate_irs()
        # food sensor
        self.fs_reading = None
        self.fs_range = fs_range
        self.fs_noise = fs_noise
        self.trees_locs = [tree for tree in world.trees]
        # temporary, replacement for empirical fxs
        self.rob_speed = 1
        self.irval = 1
        # act
        self.data = []
        self.notes = None
        self.act()


    def act(self):
        # actions for each timestep
        self.ir_reading()
        self.fs_reading()
        self.move()
        self.update_sensors()
        # data: [position, orientation, sensors, ir_reading, fs_reading, notes]
        self.data.append([self.position, int(np.degrees(self.orientation)), self.ir_sensors, self.ir_reading, self.fs_reading, self.notes])
        self.notes = None

    def update_sensors(self):
        # update information from ir sensors
        # ir sensors
        self.ir_sensors = []
        for sensor in self.irs:
            sx = self.x+sensor[0][0]
            sy = self.y+sensor[0][1]
            so = geometry.force_angle(self.orientation+sensor[1])
            ll_ray = geometry.force_angle(so+sensor[2][0])
            rr_ray = geometry.force_angle(so+sensor[2][-1])
            # [[rel_x, rel_y], rel_angle, ray_length, left_most_ray, right_most_ray]
            self.ir_sensors.append([[sx,sy], so, self.ray_length, ll_ray, rr_ray])
        # food sensor
        # TODO

    def move(self):
        #print("move")
        # new x,y and orientation
        l_speed, r_speed = self.robot_speed()
        vel = (l_speed+r_speed)/2
        dx = vel*np.cos(self.orientation)
        dy = vel*np.sin(self.orientation)
        do = (l_speed - r_speed)/self.wheel_sep
        # keep x and y within limits
        self.x += dx
        if self.x > world.xmax:
            self.x = world.xmax - self.radius
        if self.x < 0:
            self.x = self.radius
        self.y += dy
        if self.y > world.ymax:
            self.y = world.ymax - self.radius
        if self.y < 0:
            self.y = self.radius
        # update
        self.position = np.array([self.x, self.y])
        self.orientation += do
        # force angle between 0 and 2pi
        self.orientation = geometry.force_angle(self.orientation)
        # what to do after collisions?
        if self.collision() == True:
            #print("collided...")
            self.notes = "collision"
            self.energy -= 10
            self.orientation = geometry.force_angle(self.orientation-np.degrees(np.random.randint(90, 270)))
        # update sensors parameters
        # irs[i]: [ir_rel_pos, ir_rel_angles[n], ir_rel_rays]
        for i in range(len(self.irs)):
            rel_x = self.radius*np.cos(self.orientation+self.irs[i][1])
            rel_y = self.radius*np.sin(self.orientation+self.irs[i][1])
            self.irs[i][0] = [rel_x, rel_y]

    def robot_speed(self):
        # there is no translation from voltage in this case
        # speed = speed % ? % urgency % noise
        # ? = something to get different speeds for lw and rw
        l_speed = self.lw_speed * self.rob_speed + self.lw_speed*self.urgency
        r_speed = self.rw_speed * self.rob_speed + self.rw_speed*self.urgency
        # add random noise from a normal distribution
        l_speed += np.random.randn()    #self.motor_noise     #np.random.randn()
        r_speed += np.random.randn()    #self.motor_noise     #np.random.randn()
        # print("{}, {}".format(l_speed, r_speed))
        return l_speed, r_speed

    def collision(self):
        # collision with world walls
        for wall in world.walls:
            # wall: line segment [a,b]
            a = np.array(wall[0])
            b = np.array(wall[1])
            if geometry.shortest_dist(a, b, self.position) <= self.radius:
                #print("\nposition: {}".format(self.position))
                #print("wall, A: {} to B: {}".format(a,b))
                return True

    # define relative angles and positions from mid top
    def allocate_irs(self):
        #print("allocate")
        # sensor only on the top half of the body uniformily distributed
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
        ray_x = self.ray_length*np.cos(ray_angle)
        ray_y = self.ray_length*np.sin(ray_angle)
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
        # with mid ray angle (a)
        # center ray end (no spread)
        # w: wall index
        ray_end_mid = self.ray_end(ir_pos[0], ir_pos[1], ir_angle, 0)
        # intersection point mid ray to wall along ray
        #try:
        ix = geometry.intersection_point(ir_pos, ray_end_mid, world.walls[w][0], world.walls[w][1])
        #except:
            #import pdb; pdb.set_trace()
        # distance from sensor to the intersection point
        dist = np.linalg.norm(ir_pos-ix)
        # IRval
        # IR reading for a given distance
        # from empirical fitting data
        # gaussian 3371*e^(-(d/8.5)^2) fits well
        # k = -1*(d/8.5)*(d/8.5)
        return dist

    def fs_reading(self):
        # search within sensing area
        self.fs_reading = [ti for ti in self.trees_loc if np.linalg.norm(ti-self.position)<=self.fs_range]


    def ir_reading(self):
        #print("ir_reading")
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
                self.ir_reading = None
                return 0
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
                    val = n_hits/self.n_rays*self.irval
                    val += self.ir_noise
                    # it can only be positive
                    val == 0 if val < 0 else val
                self.ir_reading = int(val)
                return int(val)














































































        #
