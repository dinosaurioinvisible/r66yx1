
import numpy as np
from ring import RingSystem
from copy import deepcopy

'''trial for the system ring,
v1: for simplicity agent and world are modelled as independent objects'''
def trial(gt,st0=6,n_trials=10,time=1000,world_size=10,rain_threshold=1):
    # set empty world
    world = np.zeros((world_size,world_size)).astype(int)
    # init agent
    xy = int(world_size/2)
    agent = RingSystem(gt=gt,i=xy,j=xy,st0=st0)
    # begin trials
    data = []
    for tx in range(n_trials):
        ti = 0
        trial_data = []
        while ti < time:
            # update world
            # v1: rain drops come only from the top
            rain = np.random.normal(0,rain_sd,world_size)
            rain = np.where(rain>1,1,0)
            world = np.vstack(rain,world[:-1])
            # update agent
            # v1: for simplicity, it does not modify world instance
            world_copy = deepcopy(world)
            # v1: agent's states override rain drops
            for ex in agent.elements:
                world_copy[ex.i,ex.j] = ex.st
            world_copy[agent.i,agent.j] = agent.core_st
            agent.update(world_copy)
            # save data (world_st, agent_st)
            # world state as 1 hot vectors
            world_st = np.nonzero(world.flatten())
            data.append([world_st,agent.st])
            # v1: survival condition is to maintain core ON
            if agent.core_st == 0:
                break
            # agent > world
            # v1: drops dissapear after contact with agent
            for ex in agent.elements:
                world[ex.i,ex.j] = 0
        data.append(trial_data)
    # compute fitness and return
    trials_ft = sorted([len(tx)/time for tx in data])
    ft = 0
    for et,trial_ft in enumerate(trials_ft):
        ft += (et+1)*trial_ft
    ft = ft/((n_trials+1)*n_trials/2)
    return ft,data
