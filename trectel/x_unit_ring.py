
import numpy as np

def unit_gt(n_cells=4):
    # for every state
    st_range = 2**n_cells
    # for every environmental circumstance
    env_range = 2**(4+n_cells)
    # there should be a transition to another state
    genotype = np.random.randint(0,st_range,size=(st_range,env_range))
    return genotype

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# visualization of state transitions
# same initial state, different environmental conditions
def unit_st_transitions(gt,sti=6):
    gx = nx.DiGraph()
    # transitions from certain state i to different states x
    gx.add_nodes_from(range(len(gt)))
    # count sti->stx transitions
    tx_recurrence = defaultdict(int)
    for stx in gt[sti]:
        tx_recurrence[stx] += 1
    # add edges with recurrence weights
    for stx in gt[sti]:
        gx.add_edge(sti,stx,weight=tx_recurrence[stx])
    # plot
    x,weights = zip(*nx.get_edge_attributes(gx,'weight').items())
    cbar = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0,vmax=max(weights)))
    plt.colorbar(cbar)
    nx.draw_circular(gx,edge_color=weights,with_labels=True)
    plt.show()

# visualization of state transitions
# different initial state, same environmental conditions
def unit_env_transitions(gt,env=0):
    gx = nx.DiGraph()
    # transitions from every state i to different states x
    gx.add_nodes_from(range(len(gt)))
    for txi,txs in enumerate(gt):
        gx.add_edge(txi,txs[env])
    # plot
    nx.draw_circular(gx,with_labels=True)
    plt.show()

'''Ring unit, unique genotype'''
class RingUnit:
    def __init__(self,gt,n_cells,i,j,st0):
        # elements and gt
        self.gt = gt
        self.n_cells = n_cells
        # location
        self.i, self.j = i,j
        self.cell_locs = ring_locs(i,j,r=int(self.ncells/4))
        self.env_locs = ring_locs(i,j,r=int(1+self.ncells/4))
        # state
        self.st = st0
        self.cell_sts = int2arr(st0,arr_len=ncells)
        #self.st_hist = [st0]

    def update(self,world):
        # read environment
        env = []
        for [ci,cj] in self.env_locs:
            env.append(world[ci,cj])
        env_in = arr2int(np.asarray(env))
        # transition to new state
        self.st = self.gt[env_in]
        # individual states
        self.cell_sts = int2arr(self.st,arr_len=self.ncells)
        # save
        #self.st_hist.append(self.st)



'''trial for the ring unit'''
def unit_trial(gt,st0=6,n_trials=10,time=1000,world_size=10,rain_threshold=1):
    # set empty world
    world = np.zeros((world_size,world_size)).astype(int)
    # init and allocate ring agent in the center
    xy = int(world_size/2)
    agent = RingUnit(gt=gt,n_cells=4,i=xy,j=xy,st0=st0)
    # begin trials
    # v1: drops only fall from top to bottom
    # v1: drops dissapear after contact with agent
    end_times = []
    for tx in range(n_trials):
        ti = 0
        while ti < time:
            # update world
            rain = np.random.normal(0,rain_sd,world_size)
            rain = np.where(rain>1,1,0)
            world = np.vstack(rain,world[:-1])
            # update agent
            agent.update(world)
            for [ci,cj],cst in zip(agent.cell_locs,agent.cell_sts):
                world[ci,cj] = cst
            # update core
            nb = np.sum(agent.i-1:agent.i+2,agent.j-1:agent.j+2) - 1
            if nb < 2 or nb > 3:
                break
            ti += 1
        end_times.append(ti)
    return end_times


#
