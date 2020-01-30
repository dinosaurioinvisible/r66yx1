
import numpy as np
import world
import geometry

class Sensors:
    def __init__(self, fs_angle=360, fs_range=25\
    , ir_angle=60, ray_length=20, n_rays=5, beam_spread=60):
    # init
    self.ir_angles = [np.radians(ir_angle), geometry.force_angle(np.radians(-ir_angle))]
    self.ray_length = ray_length
    self.n_rays = n_rays
    self.beam_spread = ray_spread
    self.ray_sep = beam_spread/(n_rays-1)
    self.fs_angle = fs_angle
    self.fs_range = fs_range

    def read_irs(self, x, y, r, or):
        ir_reading = []
        for ir_angle in self.ir_angles:
            ir_or = geometry.force_angle(or+ir_angle)
            ir_x = x + r*np.cos(ir_or)
            ir_y = y + r*np.sin(ir_or)
            ir_rays = [geometry.force_angle(ir_or-self.ray_spread/2+self.ray_sep*n) for n in range(self.n_rays)]
            # check if beam misses everything
            hit_left = self.ray_hit(ir_x, ir_y, ir_rays[0])
            hit_right = self.ray_hit(ir_x, ir_y, ir_rays[-1])
            if hit_left == False and hit_right == False:
                ir_reading.append(None)
            else:
                # check ray by ray and form "an image"
                pass



    def ray_hit(self, ir_x, ir_y, ray_or):
        ray_end = self.ray_end(ir_x, ir_y, ray_or)


    def ray_end(self, ir_x, ir_y, ray_or):
        ray_x = ir_x + self.ray_length*np.cos(ray_or)
        ray_y = ir_y + self.ray_length*np.sin(ray_or)
        return np.array([ray_x, ray_y])

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
        # from 0 to 3500 far to near orginally. here normalized 0 to 1
        val /= 3500
        return val

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
                val = 0 if val < 0 else val
                self.ir_reading.append(int(val))
                self.notes = "detection"

    def read_fs(self):
        # search trees within sensing area in polar coordinates [dist, angle]
        # arctan2(y,x)
        fs_reading = [[np.linalg.norm(tree_loc-self.position), np.arctan2(tree_loc[1],tree_loc[0]), tree_loc] for tree_loc in self.trees_locs if np.linalg.norm(tree_loc-self.position)<=self.fs_range]
        if len(fs_reading) == 0:
            self.fs_reading = None
        else:
            self.notes = "tree"
            fs = sorted(fs_reading, key=lambda i:i[0])
            fs_dist = fs[0][0]
            # from 0 to 1, normalized
            self.fs_reading = (1/np.exp(fs_dist/self.fs_range))

















































































#
