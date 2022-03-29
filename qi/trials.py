
import numpy as np
from systems import ContainerRing
from helper_fxs import ring_locs
from tqdm import tqdm


def ring_container_trial(ring,timesteps=1000,world_size=7,save_data=False):
    # set world
    ij = int(world_size/2)
    world = np.zeros((world_size,world_size))
    env_array = np.random.randint(0,2,size=(5))
    env_locs = ring_locs(i=ij,j=ij,r=1,hollow=False)
    for ex,[ei,ej] in enumerate(env_locs):
        world[ei,ej] = env_array[ex]
    # data
    if save_data:
        data = [[world.astype(int),ring.st]]
    # trial
    ti,ft = 0,0
    while ti<timesteps:
        # update ring
        ring.update(world.astype(int))
        # update world
        for ex,[ei,ej] in enumerate(env_locs):
            ev = world[ei,ej]
            nb = np.sum(world[ei-1:ei+2,ej-1:ej+2]) - ev
            env_array[ex] = 1 if nb==3 or (ev==1 and nb==2) else 0
        for ex,[ei,ej] in enumerate(env_locs):
            world[ei,ej] = env_array[ex]
        # replace ring cells
        for rx,[ri,rj] in enumerate(ring.exs_ij):
            world[ri,rj] = ring.st[rx]
        # ft, save, advance
        fti = 1 if np.sum(env_array) > 0 else 0
        ft += fti
        if save_data:
            data.append([world.astype(int),ring.st])
        ti += 1
    if ft>500:
        print(ft)
        print(ring.gt)
        import pdb; pdb.set_trace()
    if save_data:
        ft = ft/timesteps
        return ring,ft,data
    return ft

for trial in tqdm(range(1000)):
    gt = np.random.randint(0,2,size=(8,4))
    ringx = ContainerRing(gt)
    ring_container_trial(ringx)
