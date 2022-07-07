
import numpy as np
from helper_fxs import *
from fast_gol import gol_tx

# glider initial configuration
# glider_cfg0 = np.array([[0,0,0,0,0],[0,1,0,1,0],[0,0,1,1,0],[x,0,1,0,0],[x,0,0,0,x]])

# GoL transitions
def gol_txs():
    t = matrix_reps(512)
    tf = np.zeros(t.shape)
    for i in range(t.shape[0]):
        # so surroundings are 0
        w = np.zeros((t.shape[1]+2,t.shape[2]+2))
        w[1:-1,1:-1] = t[i]
        print(i)
        print(w)
        f = gol_tx(w)
        print(f)
        tf[i] = f[1:-1,1:-1]
    return t,tf

gol_txs()
