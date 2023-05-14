
import numpy as np

# int > binary array
def int2array(ni,arr_len,mn=1):
    # reversed for cell order
    x = np.array([int(i) for i in np.binary_repr(ni,arr_len) [::-1]])
    if mn > 1:
        return x.reshape(mn,mn)
    return x

# array to int
def array2int(arr):
    xi = np.sum([x<<e for e,x in enumerate(arr.flatten().astype(int))])
    return xi

# game of life transition
def gol_step(world_st):
    world = world_st/1
    world_copy = world_st/1
    for ei,vi in enumerate(world_copy):
        for ej,vij in enumerate(vi):
            nb = np.sum(world_copy[max(0,ei-1):ei+2,max(ej-1,0):ej+2]) - vij
            vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and nb==3) else 0
            world[ei,ej] = vx
    return world

# indexing for saving files
def save_as(file,fname):
    import pickle
    import os
    while os.path.isfile(fname):
        i = 1
        name,ext = fname.split('.')
        try:
            fi = int(name[-1])+1
            fname = '{}{}.{}'.format(name[:-1],fi,ext)
        except:
            fi = i
            fname = '{}{}.{}'.format(name,i,ext)
    with open(fname,'wb') as f:
        pickle.dump(file,f)
    print('saved as: '.format(fname))