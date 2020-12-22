
import numpy as np
import geometry as geom
from shapely.geometry import Point
from shapely.geometry import LineString

class Sensors:
    def __init__(self,irx,r,x,y,o):
        # as from Shibuya et al
        self.srange = 5
        self.do_front = np.pi/8
        self.do_rear = np.pi/6
        self.irx = irx
        self.r = r
        self.irs = []
        self.info = [[0]*8]
        self.angles = self.define_angles()
        self.define_sensors(x,y,o)


    def get_info(self, xagents):
        # get max activation for each sensor
        self.info = []
        for enum,ir in enumerate(self.irs):
            # only if sensor is active for genotype
            ir_vals = [0]
            if self.irx[enum]:
                for xagent in xagents:
                    if ir.intersects(xagent.body):
                        sxy = ir.coords[0]
                        dis = Point(sxy).distance(ir.intersection(xagent.body))
                        val = (self.srange-dis)/self.srange
                        ir_vals.append(val)
                # from Quinn thesis (max)
                # I didn't understand Shibuya et al
                # (how are you suppose to add to the same sensor (overposition?))
                ir_val = max(ir_vals)
                # noise
                if ir_val == 0:
                    ir_val += np.random.uniform(0,0.1)
                else:
                    # Shibuya et al sd=0.25, but I think is too much
                    ir_val += np.random.normal(0,ir_val*0.25)
                ir_val = 0 if ir_val < 0 else ir_val
            # when sensor is not active for the genotype
            else:
                ir_val=0
            self.info.append(ir_val)
        return self.info


    def define_sensors(self,x,y,o):
        # define active sensors
        self.irs = []
        for irx,ir_angle in zip(self.irx,self.angles):
            ir = None
            if irx==True:
                # IRs: shapely linear objects
                angle = geom.force_angle(o+ir_angle)
                sx = x + self.r*np.cos(angle)
                sy = y + self.r*np.sin(angle)
                rx = sx + self.srange*np.cos(angle)
                ry = sy + self.srange*np.sin(angle)
                ir = LineString([(sx,sy),(rx,ry)])
            self.irs.append(ir)

    def define_angles(self):
        ir_angles = []
        # front sensors
        for i in range(1,4):
            ir_angles.extend([geom.force_angle(self.do_front*i), geom.force_angle(-self.do_front*i)])
        # rear sensors
        ir_angles.extend([geom.force_angle(np.pi+self.do_rear), geom.force_angle(np.pi-self.do_rear)])
        return ir_angles













#
