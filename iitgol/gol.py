
import numpy as np

def blinker_trial(blinker,timesteps=10,world=[],world_size=10):
    # set world
    xy = int(world_size/2)
    if len(world)==0:
        world = np.zeros((world_size,world_size)).astype(int)
    # trial
    ti=0
    while ti<timesteps:

        # update world

        ti+=1
