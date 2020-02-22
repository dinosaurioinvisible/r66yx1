
import numpy as np
import geometry
import environment

class Sensors:
    def __init__(self, o_angle=90, o_range=25\
    , ir_angle=45, ray_length=20, n_rays=4, beam_spread=135):
        # init
        self.ir_angles = [np.radians(ir_angle), geometry.force_angle(np.radians(-ir_angle))]
        self.ray_length = ray_length
        self.n_rays = n_rays
        self.ray_sep = beam_spread/(n_rays-1)
        self.o_angle = o_angle
        self.o_range = o_range

    def read_env(self, x, y, r, or, objects):
        ir_env = self.read_irs(x,y,r,or,objects)
        o_env = self.read_o(x,o,r,objects)
        env_data = ir_env+o_env
        return env_data

    # read data from ir sensors
    def read_irs(self, x, y, r, or, objects):
        ir_reading = []
        for ir_angle in self.ir_angles:
            ir = []
            # location and orientation according to agent
            ir_or = geometry.force_angle(or+ir_angle)
            ir_x = x + r*np.cos(ir_or)
            ir_y = y + r*np.sin(ir_or)
            # list of orientations of rays
            rays_or = [geometry.force_angle(-ir_or-self.ray_sep*n) for n in range(self.n_rays)]
            # check hits and save
            for ray_or in rays_or:
                val = 0
                hit = self.ray_hit(ir_x, ir_y, ray_or, objects)
                if hit[0]:
                    ray_val = self.ir_val(hit[2])
                    ir.append(ray_val)
            ir_reading.append(ir)
        return ir_reading

    # check if ray hits something
    def ray_hit(self, ir_x, ir_y, ray_or, objects):
        ray_start = np.array([ir_x, ir_y])
        ray_end = self.ray_end(ir_x, ir_y, ray_or)
        hit = False
        min_object = None
        min_dist = self.ray_length+1
        # for each objet in the world
        for object in objects:
            object_id = object[0]
            object_start = object[1]
            object_end = object[0]
            # check if ray intersects with object
            if geometry.intersect(ray_start, ray_end, object_start, object_end):
                # if it does, get distance
                intersection = geometry.intersection_point(ray_start, ray_end, object_start, object_end)
                dist = np.linalg.norm(ray_start-intersection)
                # save min distance
                if dist < min_dist:
                    hit = True
                    min_object = object_id
                    min_dist = dist
        return [hit, min_object, min_dist]

    # get ray end for checking if hits
    def ray_end(self, ir_x, ir_y, ray_or):
        ray_x = ir_x + self.ray_length*np.cos(ray_or)
        ray_y = ir_y + self.ray_length*np.sin(ray_or)
        return np.array([ray_x, ray_y])

    def ir_val(self, dist):
        # IR reading for a given distance from empirical fitting data
        # gaussian 3371*e^(-(d/8.5)^2) fits well
        k = -1*(dist/8.5)*(dist/8.5)
        ir_coeff = 1
        val = ir_coeff * 3371 * np.exp(k)
        # from 0 to 3500 far to near orginally. here normalized 0 to 1
        val /= 3500
        return val

    ########################################

    # olfactory-like sensor
    # search trees within sensing area in polar coordinates [dist, angle]
    def read_o(self, x, y, or, objects):
        o_val = None
        tree = False
        o_pos = np.array([x,y])
        trees = [x for x in objects if x[0]=="tree"]
        for tree in trees:
            dist = np.linalg.norm(tree[0]-o_pos)
            if dist <= self.o_range:
                if self.in_o_range_fx(tree[0], or):
                    tree = True
                    if dist < min_dist:
                        min_dist = dist
        if tree:
            o_val = (1/np.exp(fs_dist/self.o_range))
        return o_val

    # fx to check if tree is within the polar range
    def in_o_range_fx(self, tree_loc, pos):
        # line betweem B (tree) and A (sensor)
        ba_line = tree_loc - pos
        # angle between the line and the horizontal axis
        ba_angle = geometry.force_angle(np.arctan2(ba_line[1], ba_line[0]))
        angle_range = [geometry.force_angle(or-self.o_angle), geometry.force_angle(or+self.o_angle)]
        if ba_angle > angle_range[0] and ba_angle < angle_range[1]:
            return True
        return False
















































































#
