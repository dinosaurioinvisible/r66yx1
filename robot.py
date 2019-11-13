
import numpy as np
import geometry
import world

#TODO
# after collisions
# urgency fx, to define speed
# parameter/variable to differentiate lw and rw speed
# parameter/variable to alter irval
# compute for all ray_spread values (5 in the original)
# innner wall could rotate clockwise

class Robot:
    def __init__(self, x=50, y=50, orientation=0\
    , radius=2.5, wheel_sep=2, motor_noise=0\
    , n_irs=2, ray_length=10, n_rays=5, ray_spread=1, ir_noise=0):
        # movement
        self.x = x
        self.y = y
        self.position = np.array([self.x, self.y])
        self.orientation = orientation
        self.radius = radius
        self.wheel_sep = wheel_sep
        self.lw_speed = 5
        self.rw_speed = 5
        self.motor_noise = motor_noise  #np.random.random()
        # sensors
        self.reading = None
        self.n_irs = n_irs
        self.ray_length = ray_length
        self.n_rays = n_rays
        self.ray_spread = ray_spread
        self.ir_noise = ir_noise        # np.random.random()
        self.irs = []
        self.allocate_irs()
        # urgency parameter between 0 and 1
        self.urgency = 0
        # temporary, replacement for empirical fxs
        self.rob_speed = 1
        self.irval = 1
        # act
        self.data = []
        self.notes = None
        self.act()


    def act(self):
        print("\nrobot in {} looking at {}".format(self.position, self.orientation))
        print("ir_readings: {}".format(self.reading))
        self.data.append([self.position, self.orientation, self.reading, self.notes])
        self.notes = None
        self.ir_reading()
        self.move()

    def move(self):
        print("move")
        l_speed, r_speed = self.robot_speed()
        vel = (l_speed+r_speed)/2
        dx = vel*np.sin(self.orientation)
        dy = vel*np.cos(self.orientation)
        do = (l_speed - r_speed)/self.wheel_sep

        # oldx = self.x
        # oldy = self.y
        # oldtheta = self.orientation

        # new x,y and orientation
        # keep x and y within limits
        # force angle between 0 and 2pi
        self.x += dx
        if self.x > world.xmax:
            self.x = world.xmax
        self.y += dy
        if self.y > world.ymax:
            self.y = world.ymax
        self.position = np.array([self.x, self.y])
        self.orientation += do
        self.orientation = geometry.force_angle(self.orientation)

        if self.collision() == True:
            # what to do after collisions?
            # reset after collision
            self.x -= dx
            self.y -= dy
            # self.orientation = oldtheta
            print("collided...")
            self.notes = "collision"
            self.orientation += self.motor_noise
            self.orientation = geometry.force_angle(self.orientation)

    def robot_speed(self):
        # there is no translation from voltage in this case
        # speed = speed % ? % urgency % noise
        # ? = something to get different speeds for lw and rw
        l_speed = self.lw_speed * self.rob_speed + self.lw_speed*self.urgency
        r_speed = self.rw_speed * self.rob_speed + self.rw_speed*self.urgency
        # add random noise from a normal distribution
        l_speed += np.random.randn()
        r_speed += np.random.randn()
        return l_speed, r_speed

    def collision(self):
        # collision with world walls
        for wall in world.walls:
            # wall: line segment [a,b]
            a = np.array(wall[0])
            b = np.array(wall[1])
            if geometry.shortest_dist(a, b, self.position) <= self.radius:
                print("\nposition: {}".format(self.position))
                print("wall, A: {} to B: {}".format(a,b))
                return True

    # define relative angles and positions from mid top
    def allocate_irs(self):
        print("allocate")
        # sensor only on the top half of the body uniformily distributed
        ir_rel_angle = 0
        angle_sep = 180/(self.n_irs+1)
        for n in range(self.n_irs):
            # define relative angle
            if 90 >= ir_rel_angle >= 270:
                ir_rel_angle = 360 - ir_rel_angle
            else:
                ir_rel_angle += angle_sep
            # define relative position
            ir_rel_x = self.radius*np.cos(ir_rel_angle)
            ir_rel_y = self.radius*np.sin(ir_rel_angle)
            ir_rel_pos = np.array([ir_rel_x, ir_rel_y])
            # define ray relative angles
            rays_sep = self.ray_spread/(self.n_rays-1)
            # negative for counterclockwise
            ir_rel_rays = [(-self.ray_spread/2)+rays_sep*n for n in range(self.n_rays)]
            # ir = [angle, position, rays]
            # everything relative to location/orientation
            self.irs.append([np.radians(ir_rel_angle), ir_rel_pos, ir_rel_rays])

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

    def ir_reading(self):
        print("ir_reading")
        for ir_sensor in self.irs:
            rel_angle = ir_sensor[0]
            rel_pos = ir_sensor[1]
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
                self.reading = None
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
                self.reading = int(val)
                return int(val)














































































        #
