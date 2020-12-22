
import numpy as np
import geometry as geom
from shapely.geometry import Point
from shapely.geometry import LineString


class Sensors:
    def __init__(self,irx):
        # as from Quinn and Shibuya et al
        self.irx = irx
        self.rg = 5
        self.do_front = np.pi/8
        self.do_rear = np.pi/6
        self.ir_angles = self.define_angles()
        self.irs = []
        self.define_irs(x,y,o)
        self.info = np.array([[0]*8])

    def update(self, env):
        # create an array (rows:objects, cols:irs)
        ir_arrs = np.zeros((len(env),8))
        # for each ir, get val
        for i,ir in enumerate(self.irs):
            # if sensor is active for this genotype
            if self.irx[i]:
                # get val for each world object
                for k,wo in env:
                    if ir.intersects(wo.area):
                        sxy = ir.coords[0]
                        dist = Point(sxy).distance(ir.intersection(wo.body))
                        val = (self.sr-dist)/self.sr
                        # noise when val>0, then keep within bounds
                        val += np.random.normal(0,val*0.25)
                        val = np.where(val>1,1, np.where(val<0,0, val))
                    else:
                        # noise for val==0 (nothing in range)
                        val = np.random.uniform(0,0.1)
                    # append to matrix
                    ir_arrs[k][i] = val
        # select object with the highest valued array (min attention?)
        self.info = sorted([i for i in ir_arrs], key=lambda x:sum(x), reverse=True)[0]

    def define_irs(self,x,y,o):
        # update position of active sensors
        self.irs = []
        for irx,ir_angle in zip(self.irx,self.ir_angles):
            ir = None
            if irx==True:
                # IRs: shapely linear objects
                oir = geom.force_angle(o+ir_angle)
                sx = x + self.r*np.cos(oir)
                sy = y + self.r*np.sin(oir)
                rx = sx + self.srange*np.cos(oir)
                ry = sy + self.srange*np.sin(oir)
                ir = LineString([(sx,sy),(rx,ry)])
            self.irs.append(ir)

    def define_angles(self):
        # specific theta for each IR
        ir_angles = []
        # front sensors
        for i in range(1,4):
            ir_angles.extend([geom.force_angle(self.do_front*i), geom.force_angle(-self.do_front*i)])
        # rear sensors
        ir_angles.extend([geom.force_angle(np.pi+self.do_rear), geom.force_angle(np.pi-self.do_rear)])
        return ir_angles




































#
