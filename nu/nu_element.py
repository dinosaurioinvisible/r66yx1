
import numpy as np

class Element():
    def __init__(self,gt,x,y,o,sx):
        # 0=core, 1=inner space, 2=membrane
        self.type = gt.type
        # initial state
        self.x = x
        self.y = y
        # 0=north, 1=east, 2=south, 3=west
        self.o = o
        self.sx = sx

    def update(self,cenv):
        # adjust env info according to current orientation
        env_info = np.rot90(cenv,self.o).flatten()
        # response function
        
