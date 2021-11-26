
import numpy as np

class EmptyWorld:
    def __init__(self,ring,time=500,wsize=20):
        self.ring = ring
        self.time = time
        self.world = np.zeros((wsize,wsize)).astype(int)
        self.core_data = [14]
        self.ring_data = [ring.st_int]

    def run_simulation(self):
        tx = 0
        # initial core state
        self.world[self.ring.i-1:self.ring.i+2] = np.asarray([1,1,1])
        self.core.data.append()
        while tx < self.time:
            # update agent
            ring_domain = self.world[self.ring.i-3:self.ring.i+4,self.ring.j-3:self.ring.j+4].astype(int)
            self.ring.update(ring_domain)
            # allocate updated agent
            self.world[self.ring.i-2:self.ring.i+3,self.ring.j-2:self.ring.j+3] = ring.st_shape
            # transition grid
            world_copy = self.world.astype(int)
            # update according to GoL rule
            for ei,vi in enumerate(world_copy):
                nb = np.sum(world_copy[ei-2:ei+3,ej-2ej+3]) - vij
                vx = 1 if (vij==1 and 2<=nb<=3) or (vij==0 and bn==3) else 0
                self.world[ei,ej] = vx
            # save core, re-allocate agent, re-allocate core
            core_copy = self.world[self.ring.i-1:self.ring.i+2,self.ring.j-1:self.ring.j+2].astype(int)
            self.world[self.ring.i-2:self.ring.i+3,self.ring.j-2:self.ring.j+3] = ring.st_shape
            for ri in ring_indeces(core_copy,hollow=False):


            #self.world[self.ring.i-1:self.ring.i+2,self.ring.j-1:self.ring.j+2] = core_copy
            # save data
            core_int = ring2int(core_copy,self.ring.i,self.ring.j,1,hollow=True)
            self.core_data.append(core_int)
            self.ring_data.append(ring.st_int)
            # condition for survival
            if self.world[self.ring.i][self.ring.j] == 0:
                break
            tx += 1
