
import numpy as np
from helperfxs import *

class Agent:
    def __init__(self, i,j, xells, cfg0=341):
        self.i,self.j = i,j
        self.xells = xells
        self.state = int2arr(cfg0)
        self.data = {}

    def update(self, agent_domain):
        # reset agent
        self.state = np.zeros((3,3)).astype(int)
        # update xell by xell
        for zell in self.zells:

        for di in range(3):
            for dj in range(3):
                zell_domain = agent_domain[di:di+3,dj:dj+3]
                zell.update(zell_domain)
