
import numpy as np
import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon



class Sensors:
    def __init__(self, s_points=10\
    , ir_angle=60, ray_length=40, beam_spread=120\
    , olf_angle=120, olf_range=20\
    , aud_angle=90, aud_range=50):
        # init
        self.s_points = s_points
        self.ir_angles = [geometry.force_angle(np.radians(-ir_angle)), geometry.force_angle(np.radians(ir_angle))]
        self.ray_length = ray_length
        self.beam_angles = [geometry.force_angle(np.radians(-beam_spread/2)), geometry.force_angle(np.radians(beam_spread/2))]
        self.olf_angles =[geometry.force_angle(np.radians((-olf_angle/2))), geometry.force_angle(np.radians((olf_angle/2)))]
        self.olf_range = olf_range
        self.aud_angles = [geometry.force_angle(np.radians(-aud_angle)), geometry.force_angle(np.radians(aud_angle))]
        self.aud_range = aud_range
        # internal
        self.sensory_domain = {}
        self.sensory_domain["vis"] = []
        self.sensory_domain["olf"] = []
        self.sensory_domain["aud"] = []

    def read_env(self, x, y, o, r, objects):
        ir1, ir2 = self.read_irs(x, y, o, r, objects)
        olf = self.read_olf(x, y, o, r, objects)
        aud1, aud2 = self.read_aud(x, y, o, r, objects)
        env_data = [ir1, ir2, olf, aud1, aud2]
        return env_data

    ########################################

    # read data from ir sensors version 2 (using shapely)
    def read_irs(self, x, y, o, r, objects):
        # data
        vis_sensors_domain = []
        ir_reading = []
        # for each sensor
        for ir_angle in self.ir_angles:
            ir_val = 0
            min_dist = self.ray_length
            # location and orientation according to agent
            ir_o = geometry.force_angle(o+ir_angle)
            ir_x = x + r*np.cos(ir_o)
            ir_y = y + r*np.sin(ir_o)
            # define visual domain
            arc_start = ir_o+self.beam_angles[0]
            arc_end = ir_o+self.beam_angles[1]
            # to be sure the angle is counter-clockwise
            if arc_start > arc_end:
                arc_end += np.radians(360)
            # get arc angle points and force angles
            arc_points = np.linspace(arc_start, arc_end, self.s_points)
            arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
            # get the arc coordinates and create polygon
            arc_x = ir_x + self.ray_length*np.cos(arc_angles)
            arc_y = ir_y + self.ray_length*np.sin(arc_angles)
            vis_coords = [(ir_x,ir_y)]
            [vis_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
            vis_domain = Polygon(vis_coords)
            vis_sensors_domain.append(vis_domain)
            # check for intersections
            for w in objects["walls"]:
                wall = LineString([(w.xmin,w.ymin),(w.xmax,w.ymax)])
                if vis_domain.intersects(wall):
                    dist = Point(ir_x,ir_y).distance(vis_domain.intersection(wall))
                    if dist < min_dist:
                        min_dist = dist
            round_objects = objects["trees"]+objects["agents"]
            for obj in round_objects:
                obj_loc = Point(obj.x, obj.y)
                obj_space = obj_loc.buffer(obj.r)
                if vis_domain.intersects(obj_space):
                    dist = Point(ir_x,ir_y).distance(vis_domain.intersection(obj_space))
                    if dist < min_dist:
                        min_dist = dist
            # get ir value
            if min_dist < self.ray_length:
                # IR reading for a given distance from empirical fitting data
                # gaussian 3371*e^(-(d/8.5)^2) fits well [0, 3500]
                k = -1*((dist/8.5)**2)
                ir_val = (3371 * np.exp(k))/3500
            ir_reading.append(ir_val)
        self.sensory_domain["vis"].append(vis_sensors_domain)
        return ir_reading

    ########################################

    # olfactory-like sensor
    def read_olf(self, x, y, o, r, objects):
        # sensor location-orientation
        olf_x = x + r*np.cos(o)
        olf_y = y + r*np.sin(o)
        olf_val = 0
        # define sensor domain (polygon)
        arc_start = o+self.olf_angles[0]
        arc_end = o+self.olf_angles[1]
        # to be sure the angle is counter-clockwise
        if arc_start > arc_end:
            arc_end += np.radians(360)
        # get arc angle points and force angles
        arc_points = np.linspace(arc_start, arc_end, self.s_points)
        arc_angles = np.array([geometry.force_angle(oi) for oi in arc_points])
        # get the arc coordinates and create polygon
        arc_x = olf_x + self.olf_range*np.cos(arc_angles)
        arc_y = olf_y + self.olf_range*np.sin(arc_angles)
        olf_coords = [(olf_x,olf_y)]
        [olf_coords.append((xi,yi)) for xi,yi in zip(arc_x,arc_y)]
        olf_domain = Polygon(olf_coords)
        self.sensory_domain["olf"].append(olf_domain)
        # check for each tree
        min_dist = self.olf_range
        trees = objects["trees"]
        for tx in trees:
            tree_loc = Point(tx.x, tx.y)
            tree_space = tree_loc.buffer(tx.r)
            if olf_domain.intersects(tree_space):
                dist = Point(olf_x,olf_y).distance(olf_domain.intersection(tree_space))
                if dist <= min_dist:
                    olf_val = (1/np.exp(min_dist/self.olf_range))**2
        return olf_val

    ########################################

    # auditory sensors, one on each side
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





    # ######################################## OLD STUFF
    #
    # # read data from ir sensors
    # def read_irs0(self, x, y, o, r, objects):
    #     ir_reading = []
    #     for ir_angle in self.ir_angles:
    #         ir = []
    #         # location and orientation according to agent
    #         ir_o = geometry.force_angle(o+ir_angle)
    #         ir_x = x + r*np.cos(ir_o)
    #         ir_y = y + r*np.sin(ir_o)
    #         # list of orientations of rays
    #         rays_o = [geometry.force_angle(-ir_o-self.ray_sep*n) for n in range(self.n_rays)]
    #         # check hits and save
    #         for ray_o in rays_o:
    #             ray_val = 0
    #             hit = self.ray_hit(ir_x, ir_y, ray_o, objects)
    #             if hit[0]:
    #                 ray_val = self.ir_val(hit[1])
    #             ir.append(ray_val)
    #         ir_reading.append(ir)
    #     return ir_reading
    #
    # # check if ray hits something
    # def ray_hit(self, ir_x, ir_y, ray_o, objects):
    #     # ray_start = np.array([ir_x, ir_y])
    #     # ray_end = self.ray_end(ir_x, ir_y, ray_or)
    #     xr_end = ir_x + self.ray_length*np.cos(ray_o)
    #     yr_end = ir_y + self.ray_length*np.sin(ray_o)
    #     ray = LineString([(ir_x,ir_y),(xr_end,yr_end)])
    #     hit = False
    #     min_object = None
    #     min_dist = self.ray_length
    #     # for each object in the world, check
    #     for w in objects["walls"]:
    #         wall = LineString([(w.xmin,w.ymin),(w.xmax,w.ymax)])
    #         if ray.intersects(wall):
    #             hit = True
    #             dist = Point(ir_x,ir_y).distance(ray.intersection(wall))
    #             if dist <= min_dist:
    #                 min_dist = dist
    #     round_objects = objects["trees"]+objects["agents"]
    #     for obj in round_objects:
    #         obj_center = Point(obj.x, obj.y)
    #         obj_space = obj_center.buffer(obj.r)
    #         if ray.intersects(obj_space):
    #             hit = True
    #             dist = Point(ir_x,ir_y).distance(ray.intersection(wall))
    #             if dist <= min_dist:
    #                 min_dist = dist
    #     return [hit, min_dist]
    #
    # def ir_val(self, dist):
    #     # IR reading for a given distance from empirical fitting data
    #     # gaussian 3371*e^(-(d/8.5)^2) fits well
    #     k = -1*((dist/8.5)**2)
    #     ir_coeff = 1
    #     val = ir_coeff * 3371 * np.exp(k)
    #     # from 0 to 3500 far to near orginally. here normalized 0 to 1
    #     val /= 3500
    #     return val
    #
    #






































































#
