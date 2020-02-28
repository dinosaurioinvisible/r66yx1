
import numpy as np
import world
from tqdm import tqdm

#TODO
# attention? SM based attention?
# energy
# innner wall could rotate clockwise

def world_simulation(t=100, xmax=250, ymax=250, n_walls=5, n_trees=10, genotypes=[]):
    world_limits = [xmax, ymax]
    simworld = world.World(xmax, ymax, n_walls, n_trees, n_agents)
    for tx in tqdm(range(t)):
        simworld.update()
    return world_limits, simworld.walls[4:], simworld.trees, simworld.agents

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
