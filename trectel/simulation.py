
import numpy as np
from ring_system import Ringo
# from copy import deepcopy

'''for multiple trials'''
def evaluate(gt,mode='gol',st0=6,n_trials=10,n_steps=1000,world_size=11,world_th0=0.15):
    # same object over multiple trials
    xy = int(world_size/2)
    ringx = Ringo(gt,i=xy,j=xy,st0=st0)
    fts = []
    for _ in range(n_trials):
        trial_ft = trial(ringx,mode=mode,n_steps=n_steps,world_size=world_size,world_th0=world_th0)
        ringx.reset(st0=st0)
        fts.append(trial_ft)
    # compute overall fitness and return
    sorted_fts = sorted(fts,reverse=True)
    ft = 0
    for ti,fti in enumerate(sorted_fts):
        ft += (ti+1)*fti
    ft = ft/((n_trials+1)*n_trials/2)
    return ft


'''trial for the system ring,
v1: for simplicity agent and world are processed as independent objects'''
def trial(ring,mode='gol',n_steps=1000,world_size=11,world_th0=0.15,save_data=False):
    # set world
    xy = int(world_size/2)
    # set world
    if mode == 'rain':
        world = np.zeros((world_size,world_size)).astype(int)
        # v1: random 1st row and downward activations
        rain = np.random.uniform(size=world_size)
        world[0] = np.where(rain<world_th0,1,0).astype(int)
    elif mode == 'gol':
        world = np.random.uniform(size=(world_size,world_size))
        world = np.where(world<world_th0,1,0).astype(int)
        # system's environment is empty at first
        world[xy-2:xy+3,xy-2:xy+3] = 0
    # begin trial
    ti = 0
    ft = 0
    if save_data:
        world_st = env2int(world)
        trial_data = [world_st,ring.st,ring.cx_st]
    while ti < n_steps:
        # update world
        if mode == 'rain':
            # v1: rain drops come only from the top
            rain = np.random.uniform(size=world_size)
            rain = np.where(rain>world_th0,1,0).astype(int)
            world = np.vstack(rain,world[:-1])
            # v1: drops dissapear after contact
            world[xy:,xy-1:xy+2] = 0
        elif mode == 'gol':
            # to avoid numpy inheritance issues
            wcopy = world.astype(int)
            for wi in range(world_size):
                for wj in range(world_size):
                    wij = wcopy[wi,wj]
                    nb = np.sum(wcopy[max(wi-1,0):wi+2,max(wj-1,0):wj+2]) - wij
                    world[wi,wj] = 1 if nb==3 or (wij==1 and nb==2) else 0
        # update system
        wcopy = world.astype(int)
        ring.update(wcopy)
        # v1: system sts override world sts
        for ex in ring.elements:
            world[ex.i,ex.j] = ex.st
        world[xy,xy] = ring.cx_st
        ft += ring.cx_st
        # opt save data and advance
        if save_data:
            world_st = env2int(world)
            trial_data.append([world_st,ring.st,ring.cx_st])
        ti += 1
    if save_data:
        return ft,trial_data
    return ft












#
