
import numpy as np
from auxs import *
from tqdm import tqdm
import sys

# make both gliders and indices for every cfg
def mk_gliders(return_cfgs=False):
    # define basic glider configurations
    gliderA = np.zeros((3,3))
    gliderA[0,1] = 1
    gliderA[1,2] = 1
    gliderA[2,:] = 1
    #print(gliderA)
    gliderB = np.zeros((3,3))
    gliderB[0:2,1] = 1
    gliderB[1:,2] = 1
    gliderB[2,0] = 1
    #print(gliderB)
    # (still missing the centered case with 1 or 2 active corners)
    gliderA_cfgs = np.zeros((8,3,3))
    gliderB_cfgs = np.zeros((8,3,3))
    for xo in range(4):
        gliderA_cfgs[xo] = np.rot90(gliderA,xo)
        gliderA_cfgs[(xo+4)] = np.rot90(np.transpose(gliderA),xo)
        gliderB_cfgs[xo] = np.rot90(gliderB,xo)
        gliderB_cfgs[(xo+4)] = np.rot90(np.transpose(gliderB),xo)
    # dicts for indeces
    gliderA_dx = {}
    gliderB_dx = {}
    for gi in range(8):
        gliderA_dx[array2int(gliderA_cfgs[gi])] = []
        gliderB_dx[array2int(gliderB_cfgs[gi])] = []
    # return dicts and opt cfgs
    if return_cfgs:
        return gliderA_dx, gliderB_dx, gliderA_cfgs, gliderB_cfgs    
    return gliderA_dx, gliderB_dx

# gol step fx to look for cfgs that produce gliders
def get_proto_gliders(fname,rows=5,cols=5):
    # get glider dicts
    gliderA_dx, gliderB_dx = mk_gliders()
    # try all previous worlds
    cells = rows*cols
    for wx in tqdm(range(2**cells)):
        world = int2array(wx,arr_len=25,mn=5)
        world2 = gol_step(world)
        # simple version (only for 'clean'/alone gliders)
        if np.sum(world2) == 5:
            # look in windows
            next_world = False
            for i in range(3):
                for j in range(3):
                    # check if it's a glider
                    if np.sum(world2[i:i+3,j:j+3]) == 5:
                        gx = array2int(world2)
                        if gx in gliderA_dx.keys():
                            wx2 = array2int(world2)
                            gliderA_dx[gx].append((wx,wx2))
                        elif gx in gliderB_dx.keys():
                            wx2 = array2int(world2)
                            gliderB_dx[gx].append((wx,wx2))
                        next_world = True
                        break
                if next_world:
                    break
    # print, save and return
    print('for gliderA = {}'.format(sum([len(pgi) for pgi in gliderA_dx.values()])))
    print('for gliderB = {}'.format(sum([len(pgi) for pgi in gliderB_dx.values()])))
    save_as((gliderA_dx,gliderB_dx),fname)
    return gliderA_dx, gliderB_dx

# autorun
if sys.argv[0] == 'proto.py':
    # todo
    auto_plot = True if '--plot' in sys.argv else False
    if '--load' in sys.argv:
        fname = sys.argv[sys.argv.index('--fname')+1]
        if not fname:
            import os
            fname = [fi for fi in os.listdir() if i.split('.')[-1] == 'pgx'][0]
        import pickle
        with open(fname,'rb') as f:
            x = pickle.load(f)
            # todo
            import pdb
            pdb.set_trace()
    rows,cols = 5,5
    if '--dims' in sys.argv:
        rows = sys.argv[sys.argv.index('--dims')+1][0]
        cols = sys.argv[sys.argv.index('--dims')+1][1]
    fname = 'proto-gliders.pgx'
    if '--fname' in sys.argv:
        fname = sys.argv[sys.argv.index('--fname')+1]
    get_proto_gliders(fname,rows,cols)

