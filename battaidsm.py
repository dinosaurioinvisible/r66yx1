
'''agent_system'''

import numpy as np

class SMstate:
    def __init__(self, s, m):
        self.sdim = len(s)
        self.mdim = len(m)
        self.state = np.concatenate((np.array(s), np.array(m)))

    def distance_factor(self, state, kd=1000):
        d = np.exp(kd*(np.linalg.norm(self.state-np.array(state))))
