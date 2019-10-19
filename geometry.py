# coding: utf-8

import numpy as np

def shortest_dist(a, b, point):
    # between a line segment [a,b] and a point p
    dist = np.linalg.norm(b-a)
    # special case A=B
    if dist == 0:
        return np.linalg.norm(a-point)
    # line extending the segment, parameterized as a+t (b-a)
    # find proyection of point p onto the line
    # it falls where t = [(p-a).(b-a)]/dist^2
    t = np.dot((point-a),(b-a))/dist**2
    #
    if t<0:
        return np.linalg.norm(point-a)  # off the A segment
    if t>1:
        return np.linalg.norm(point-b)  # off the B segment
    # proyection onto the line segment
    px = a[0] + t*(b[0]-a[0])
    py = a[1] + t*(b[1]-a[1])
    proyection = np.array([px,py])
    return mp.linalg.norm(point-proyection)

def orientation(p, q, r):
    # to find orientation of ordered triplets of points in a plane
    # it returns:
    # 0 if p, q and r are colinear
    # 1 if clockwise
    # 2 if counterclockwise
    # orientation is direction vectors joining 3 points turn in plane
    # i.e. direction of turn of path p,q,r
    # orientation depends on wether the slope of PQ
    # is less tha, equal, or greater than QR
    dif_slope = (q[1]-p[1]) * (r[0]-q[0]) - (q[0]-p[0]) * (r[1-q[1]])
    if dif_slope == 0:
        return 0            # colinear
    elif dif_slope > 1:
        return 1            # clockwise
    else:
        return 2            # counterclockwise

def on_segment(p,q,r):
    # given 3 colinear points check if r lies on segment PQ
    # check x and y projections intersect
    if r[0] <= max(p[0],q[0]) and r[0] >= min(p[0],q[0])\
    and r[1] <= max(p[1],q[1]) and r[1] >= min(p[1],q[1]):
        return True
    return False

def intersect(p1,p2,p3,p4):
    # returns True if line segments p1,p2,p3,p4 intersect
    # first, find the orientations for general and special cases
    o1 = orientation(p1,p2,p3)
    o2 = orientation(p1,p2,p4)
    o3 = orientation(p3,p4,p1)
    o4 = orientation(p3,p4,p2)
    # general case
    # this needs to be true for intersection in general case
    if o1 != o2 and o3 !=o4:
        return True
    # special cases
    # p1, p2, p3 are colinear amd p3 lies on segment p1p2
    if o1==0 and on_segment(p1,p2,p3):
        return True
    # p1, p2, p4 are colinear and p4 lies on segment p1p2
    if o2==0 and on_segment(p1,p2,p4):
        return True
    # p3, p4, p1 are colinear and p1 lies on segment p3p4
    if o3==0 and on_segment(p3,p4,p1):
        return True
    # p3, p4, p2 are colinear and p2 lies on segment p3p4
    if o4==0 and on_segment(p3,p4,p2):
        return True
    # if it soesn't fall in any of the above cases:
    return False

def intersection_point(p1,p2,p3,p4,r):
    # r is the intersection point of p1p2 and p3p4
    # used when previously checked that there is an intersection
    # (no risk of dividing by zero)
    # vector equations are:
    # Pa = p1 + t*(p2-p1)
    # pb = p3 + s*(p4-p3)
    # solving for the points where pa = pb gives the followring 2 eqs:
    # in 2 unknowns (t and s)
    # x1 + t(x2-x1) = x3 + s(x4-x3)
    # y1 + t(y2-y1) = y3 + s(y4-y3)
    A = (p4[1]-p3[1])*(p2[0]-p1[0]) - (p4[0]-p3[0])*(p2[1]-p1[1])
    t = ()(p4[0]-p3[0])*(p1[1]-p3[1]) - (p4[1]-p3[1])*(p1[0]-p3[0]))/A
    rx = p1[0]+t*(p2[0]-p1[0])
    ry = p1[1]+t*(p2[1]-p1[1])
    r = np.array([rx,ry])

def force_angle(self, angle):
    # make sure angles ream in range 0-2pi
    # to avoid problems with sin and cos fxs
    if angle > 2*np.pi:
        return angle-2*np.pi
    elif angle < 0:
        return angle+2*np.pi
    else:
        return angle



































#
