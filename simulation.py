
import numpy as np
import world
from tqdm import tqdm
import world_animation
import sim_animation

def world_simulation(lifetime=100, xmax=250, ymax=250, n_walls=6, n_trees=5, n_agents=1, genotype=None, animate=True):
    world_limits = [xmax, ymax]
    simworld = world.World(xmax, ymax, n_walls, n_trees)
    simworld.allocate_agents(n_agents, gen=genotype)
    for tx in tqdm(range(lifetime)):
        simworld.update()
    if animate==True:
        # world_animation.sim_animation(lifetime, world_limits, simworld.walls[4:], simworld.trees, simworld.agents)
        sim_animation.sim_animation(lifetime, world_limits, simworld.walls[4:], simworld.trees, simworld.agents)
    return lifetime, world_limits, simworld.walls[4:], simworld.trees, simworld.agents
