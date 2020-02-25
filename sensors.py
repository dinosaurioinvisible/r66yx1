
import numpy as np
import geometry
import world
import tree
import agent

class Sensors:
    def __init__(self, olf_angle=90, olf_range=25\
    , ir_angle=60, ray_length=40, n_rays=4, beam_spread=120\
    , aud_angle=90, aud_range=50):
        # init
        self.ir_angles = [geometry.force_angle(np.radians(-ir_angle)), geometry.force_angle(np.radians(ir_angle))]
        self.ray_length = ray_length
        self.n_rays = n_rays
        self.ray_sep = beam_spread/(n_rays-1)
        self.olf_angles =[geometry.force_angle(np.radians((-olf_angle/2))), geometry.force_angle(np.radians((olf_angle/2)))]
        self.olf_range = olf_range
        self.aud_angles = [geometry.force_angle(np.radians(-aud_angle)), geometry.force_angle(np.radians(aud_angle))]
        self.aud_range = aud_range

    def read_env(self, x, y, o, r, objects):
        ir = self.read_irs(x, y, o, r, objects)
        ir1 = sum(ir[0])
        ir2 = sum(ir[1])
        olf = self.read_olf(x, y, o, r, objects)
        aud = self.read_aud(x, y, o, r, objects)
        aud1, aud2 = aud[0], aud[1]
        env_data = [ir1, ir2, olf, aud1, aud2]
        return env_data

    ########################################

    # read data from ir sensors
    def read_irs(self, x, y, o, r, objects):
        ir_reading = []
        for ir_angle in self.ir_angles:
            ir = []
            # location and orientation according to agent
            ir_or = geometry.force_angle(o+ir_angle)
            ir_x = x + r*np.cos(ir_or)
            ir_y = y + r*np.sin(ir_or)
            # list of orientations of rays
            rays_or = [geometry.force_angle(-ir_or-self.ray_sep*n) for n in range(self.n_rays)]
            # check hits and save
            for ray_or in rays_or:
                ray_val = 0
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
        min_dist = self.ray_length
        # for each objet in the world
        for object in objects:
            if type(object) == world.Wall:
                object_start = [object.xmin, object.ymin]
                object_end = [object.xmax, object.ymax]
            else:
                object_start = [object.x, object.y]
                object_end = [object.x, object.y]
            # check if ray intersects with object
            if geometry.intersect(ray_start, ray_end, object_start, object_end):
                # if it does, get distance
                intersection = geometry.intersection_point(ray_start, ray_end, object_start, object_end)
                dist = np.linalg.norm(ray_start-intersection)
                # save min distance
                if dist <= min_dist:
                    hit = True
                    min_object = object
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
    def read_olf(self, x, y, o, r, objects):
        olf_x = x + r*np.cos(o)
        olf_y = y + r*np.sin(o)
        min_dist = self.olf_range
        trees = [tx for tx in objects if type(tx)==tree.Tree]
        for tx in trees:
            dist = np.linalg.norm(np.array([tx.x,tx.y])-np.array([olf_x,olf_y]))
            if dist <= min_dist:
                if self.in_o_range_fx(tx, x, y, o):
                    min_dist = dist
        olf_val = (1/np.exp(min_dist/self.olf_range))**2
        return olf_val

    # fx to check if tree is within the polar range
    def in_o_range_fx(self, tx, x, y, o):
        # line betweem B (tree) and A (sensor)
        ba_line = np.array([tx.x, tx.y]) - np.array([x,y])
        # angle between the line and the horizontal axis
        ba_angle = geometry.force_angle(np.arctan2(ba_line[1], ba_line[0]))
        angle_range = [geometry.force_angle(o+self.olf_angles[0]), geometry.force_angle(o+self.olf_angles[1])]
        if ba_angle > angle_range[0] and ba_angle < angle_range[1]:
            return True
        return False

    ########################################

    # auditory sensors, one in each side
    def read_aud(self, x, y, o, r, objects):
        aud_vals = []
        for aud_angle in self.aud_angles:
            ao = geometry.force_angle(o+aud_angle)
            ax = x + r*np.cos(ao)
            ay = y + r*np.sin(ao)
            min_dist = self.aud_range
            aud_val = 0
            agents = [ag for ag in objects if type(ag)==agent.Agent]
            for ag in agents:
                dist = np.linalg.norm(np.array([ag.x,ag.y])-np.array([ax,ay]))
                if dist <= min_dist:
                    # the com output from agent weighted by the distance
                    aud_val = ag.com*(1/np.exp(min_dist/self.aud_range))**2
            aud_vals.append(aud_val)
        return aud_vals













































































#
