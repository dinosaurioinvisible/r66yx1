
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

class Sensors:
    def __init__(self, olf_angle=120, olf_range=20\
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
                    ray_val = self.ir_val(hit[1])
                ir.append(ray_val)
            ir_reading.append(ir)
        return ir_reading

    # check if ray hits something
    def ray_hit(self, ir_x, ir_y, ray_or, objects):
        #ray_start = np.array([ir_x, ir_y])
        # ray_end = self.ray_end(ir_x, ir_y, ray_or)
        xr_end = ir_x = + self.ray_length*np.cos(ray_or)
        yr_end = ir_y = + self.ray_length*np.sin(ray_or)
        ray = LineString([(ir_x,ir_y),(xr_end,yr_end)])
        hit = False
        min_object = None
        min_dist = self.ray_length
        # for each object in the world, check
        for w in objects["walls"]:
            wall = LineString([(w.xmin,w.ymin),(w.xmax,w.ymax)])
            if ray.intersects(wall):
                hit = True
                dist = ray.distance(wall)
                if dist <= min_dist:
                    min_dist = dist
        round_objects = objects["trees"]+objects["agents"]
        for obj in round_objects:
            obj_center = Point(obj.x, obj.y)
            obj_space = obj_center.buffer(obj.r)
            if ray.intersects(obj_space):
                hit = True
                dist = ray.distance(obj_space)
                if dist <= min_dist:
                    min_dist = dist
        return [hit, min_dist]

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
    def read_olf(self, x, y, o, r, objects):
        olf_x = x + r*np.cos(o)
        olf_y = y + r*np.sin(o)
        olf_val = 0
        min_dist = self.olf_range
        # trees = [tx for tx in objects if type(tx)==tree.Tree]
        trees = objects["trees"]
        for tx in trees:
            tree_loc = Point(tx.x, tx.y)
            tree_space = tree_loc.buffer(tx.r)
            # coordinates for polygon rather than area of a circle
            olf_angle1 = geometry.force_angle(o+self.olf_angles[0])
            v1x = olf_x + self.olf_range*np.cos(olf_angle1)
            v1y = olf_y + self.olf_range*np.sin(olf_angle1)
            xfront = olf_x + self.olf_range*np.cos(o)
            yfront = olf_y + self.olf_range*np.sin(o)
            olf_angle2 = geometry.force_angle(o+self.olf_angles[1])
            v2x = olf_x + self.olf_range*np.cos(olf_angle2)
            v2y = olf_y + self.olf_range*np.sin(olf_angle2)
            olf_domain = Polygon([(olf_x,olf_y),(v1x,v1y),(xfront,yfront),(v2x,v2y)])
            if olf_domain.intersects(tree_loc):
            #dist = -tx.r + np.linalg.norm(np.array([tx.x,tx.y])-np.array([olf_x,olf_y]))
                dist = olf_domain.distance(tree_space)
                if dist <= min_dist:
                    olf_val = (1/np.exp(min_dist/self.olf_range))**2
        return olf_val

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
            # agents = [ag for ag in objects if type(ag)==agent.Agent]
            agents = objects["agents"]
            for ag in agents:
                dist = np.linalg.norm(np.array([ag.x,ag.y])-np.array([ax,ay]))
                if dist <= min_dist:
                    # the com output from agent weighted by the distance
                    aud_val = ag.com*(1/np.exp(min_dist/self.aud_range))**2
            aud_vals.append(aud_val)
        return aud_vals













































































#
