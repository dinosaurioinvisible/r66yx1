
import numpy as np
from agents import RingB
from helper_fxs import *

'''for multiple trials'''
def evaluate(gt,mode='gol',st0=6,n_trials=10,timesteps=1000,world_size=10,world_th0=0.2):
    # same object over multiple trials
    xy = int(world_size/2)
    #ringx = Ring(gt,i=xy,j=xy,st0=st0)
    fts = []
    for _ in range(n_trials):
        trial_ft = ring_gol_trial(ring_gt=gt,timesteps=timesteps,world_size=world_size,world_th0=world_th0)
        fts.append(trial_ft)
    # compute overall fitness and return
    sorted_fts = sorted(fts,reverse=True)
    ft = 0
    ft_max = 0
    for ti,fti in enumerate(sorted_fts):
        ft += (ti+1)*fti
        ft_max += (ti+1)*timesteps
    ft /= ft_max
    return ft


'''trial for the system ring,
world behaves following Game of Life rules
agent and world are processed as independent objects'''
def ring_gol_trial(ring_gt,timesteps=1000,world_size=50,world_th0=0.25,save_data=False):
    # set world (system's immediate environment is empty at first)
    xy = int(world_size/2)
    world = np.random.uniform(size=(world_size,world_size))
    world = np.where(world<world_th0,1,0).astype(int)
    world[xy-2:xy+3,xy-2:xy+3] = 0
    # set ring
    ring = RingB(ring_gt,xy,xy)
    # data
    if save_data:
        data = [[world.astype(int),ring.st]]
    # trial
    ti,ft = 0,0
    while ti<timesteps:
        # update ring (env triggers st transition)
        ring_domain = world[ring.i-2:ring.i+3,ring.j-2:ring.j+3]
        ring.update(ring_domain)
        # update env (agent is blind to env changes)
        wcopy = world.astype(int)
        for wi in range(world_size):
            for wj in range(world_size):
                wij = wcopy[wi,wj]
                nb = np.sum(wcopy[max(wi-1,0):wi+2,max(wj-1,0):wj+2]) - wij
                world[wi,wj] = 1 if nb==3 or (wij==1 and nb==2) else 0
        # re-allocate ring
        for rv,[ri,rj] in zip(ring.st,ring.locs):
            world[ri,rj] = rv
        ft += ring.st[2]
        # save data
        if save_data:
            data.append([world.astype(int),ring.st.astype(int)])
        ti += 1
    # data
    if save_data:
        ft = ft/timesteps
        return ring,ft,data
    return ft


'''trial for the system ring,
world simulates downward raining activations
agent and world are processed as independent objects'''
def ring_rain_trial(ring,timesteps=1000,world_size=50,world_th0=0.25,save_data=False):
    # set world
    xy = int(world_size/2)
    # set world
    world = np.zeros((world_size,world_size)).astype(int)
    # v1: random 1st row and downward activations
    rain = np.random.uniform(size=world_size)
    world[0] = np.where(rain<world_th0,1,0).astype(int)
    # data
    if save_data:
        data = [[world.astype(int),ring.st]]
    # trial
    ti,ft = 0,0
    while ti < timesteps:
        # update system
        ring_domain = world[ring.i-2:ring.i+3,ring.j-2:ring.j+3]
        ring.update(ring_domain)
        # update env (v1: rain drops come only from the top)
        wcopy = world.astype(int)
        rain = np.random.uniform(size=world_size)
        rain = np.where(rain>world_th0,1,0).astype(int)
        world = np.vstack(rain,world[:-1])
        # v1: drops dissapear after contact
        world[xy:,xy-1:xy+2] = 0
        # re-allocate ring
        for ex_st,[exi,exj] in zip(ring.st,ring.exs_locs):
            world[exi,exj] = ex_st
        # save data
        if save_data:
            data.append([world.astype(int),ring.st])
        ti += 1
    if save_data:
        return ring,ft,data
    return ft












#
