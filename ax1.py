
# from egbert-canamero-2014
import numpy as np


# ROBOT AND EVIRONMENT

# 2d square environment of 8 units wide
# periodic boundary conditions
def pbc(xpos, xmov, xsize=8):
    # restrict coordinates to the environment
    xpos = np.array(xpos)
    xmov = np.floor(np.array(xmov))
    x = []
    for d_xpos,d_xmov in zip(xpos,xmov):
        if d_xmov < (-xsize/2 - d_xpos):
            d_x = xsize+d_xpos+d_xmov
        elif d_xmov > (xsize/2 - d_xpos):
            d_x = -xsize+d_xpos+d_xmov
        else:
            d_x = d_xpos+d_xmov
        x.append(d_x)
    return np.array(x)

# the robot has 2 directional light sensors
# and 2 independently driven motorized wheels

vel_x = cos(a)*(ml+mr)
vel_y = sen(a)*(ml+mr)
vel_alpha = 2(mr-ml)

# alpha : [-pi, pi]
# ml, mr : [-1, 1]

r = 0.25
sx = x+r*cos(alpha+beta)
sy = y+r*sen(alpha+beta)

# r = 0.25 : robot's radius
# beta : [-pi/3, pi/3] : angular offset from a

b = [cos(alpha+beta), sen(alpha+beta)]

# b : unit vector for direction
# c : vector from sensor to the light
# light is located at the center of the arena (0,0)
# s : activation of each sensor
# distance : distance from the sensor to the light

s = (b * eudist(c))/(1 + distance)

# METABOLISM

# the model consists of 3 coupled delayed dif eqs
# G : glucose : blood-glucose, must remain within limits to be healthy
# I : insuline : concentration of insuline, removes G
# U : glucagon : concentration of glucagon, releases G when below a threshold
# [a < b] = 1 when a < b, else = 0

# dG/dt = E + f_U(U) - f_I(IG) - c
# dI/dt = [b_i < G_(t-tau)]*c_I - d_I(I)
# dU/dt = [G_(t-tau) < b_U]*c_U - d_U(U)
# G : [b_U, b_I] : range of the healthy system
# tau : delay
# E represents feeding:
# if the robot is within 2 spatial units : E = 2, else E : 0

def glucose_fx():
