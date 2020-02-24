
import numpy as np
import world
import geometry
import world_animation

#TODO
# urgency could also modify the shape of the food sensor, but for an energy cost
# printable urgency and energy
# urgency fx, to define speed
# parameter/variable to differentiate lw and rw speed
# parameter/variable to alter irval
# compute for all ray_spread values (5 in the original)
# innner wall could rotate clockwise
# ir input should see obstacles and food (classify)?
# the input from sensors should concider current position?
# make space circular?
# anticipate collisions -> RNN
# connect ir values to motor behaviour
# toto > 1. reactive rules > 2. landmarks > 3. distributed map of environment
# fixation of reacting rules as patterns (habits)
# ir input -> net -> output motor
# subsumption: avoid > wander > explore
# avoid robot-robot collisions > just put data

def world_simulation(t=100, xmax=250, ymax=250, n_walls=5, n_trees=5, n_robots=3):
    tx = 0
    simworld = world.World(xmax, ymax, n_walls, n_trees, n_robots)
    world_limits = [xmax, ymax]
    while tx < t:
        simworld.update()
        tx += 1
    return world_limits, simworld.opt_walls, simworld.trees, simworld.agents

# def runsim(t=100, print_data=False):
#     tx = 0
#     simrobots = [robot_agent.Robot() for n in range(n_robots)]
#     while tx < t:
#         for simrobot in simrobots:
#             simrobot.act()
#         tx += 1
#     simdata = [simrobot.data for simrobot in simrobots]
#     parameters = simrobot.parameters
#     if print_data==True:
#         print("\ndata:")
#         for dataline in range(len(simdata[0])):
#             print("\nt={}".format(dataline))
#             for simrobot in simdata:
#                 print(simrobot[dataline])
#     return simdata, parameters

# run
world_limits, simdata_opt_walls, simdata_trees, simdata_agents = runsim()
world_animation.animation(world_limits, simdata_opt_swalls, simdata_trees, simdata_agents)
