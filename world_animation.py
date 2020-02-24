
import world
import geometry
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import matplotlib.animation as animation

# parameters = [r, ir_range, ir_angle, olf_range, olf_angle, com_range]

def animation(limits, walls, trees, agents, past=True, start=True):
    # organize data
    xmax = limits[0]
    ymax = limits[1]
    
    # defs
    fig = plt.figure()
    ax = plt.axes(xlim=(0,250), ylim=(0,250), aspect="equal")
    # params
    r = params[0]
    ir_r = params[1]
    ir_a = params[2]
    olf_r = params[3]
    olf_a = params[4]
    com_r = params[5]
    # organize data
