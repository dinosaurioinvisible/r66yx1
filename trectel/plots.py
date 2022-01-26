
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from helper_fxs import *


'''
circularity:
robustness of the circular dynamics of the agent,
basically a tree like search
starting from a given state
move to every possible subsequent state
and from that, to all possible states and so on
analyze for emergent recursiveness
'''
def circularity_txmap(gt):
    transitions = {}



'''
selectivity:
visualization of state transitions:
gives the transition map,
from some given state of the system (sti) at time t
to all subsequent system states (stx) at time t+1
according to every possible environmental condition (envx)
v1: only for 4 cells
'''
def env_txmap(gt,sti=6):
    gx = nx.DiGraph()
    # a node for every possible system state
    gx.add_nodes_from(range(2**len(gt)))
    # sti is defined, so only env cells change
    st_e1,st_e2,st_e3,st_e4 = int2arr(sti,arr_len=4)
    # sti -> stx, for every env
    transitions = defaultdict(int)
    env_range = 2**16
    for envi in range(env_range):
        # environment for every element
        envx = int2arr(envi,arr_len=16)
        e1_in = arr2int(np.asarray([envx[1],envx[2],envx[3],envx[4],st_e1,envx[5],st_e2,1,st_e3]))
        e2_in = arr2int(np.asarray([envx[3],envx[4],st_e1,envx[7],st_e2,1,envx[9],envx[10],st_e4]))
        e3_in = arr2int(np.asarray([st_e1,envx[5],envx[6],1,st_e3,envx[8],st_e4,envx[11],envx[12]]))
        e4_in = arr2int(np.asarray([st_e2,1,st_e3,envx[10],1,envx[11],envx[13],envx[14],envx[15]]))
        # responses from elements define system transition
        stx_e1 = gt[0][e1_in]
        stx_e2 = gt[1][e2_in]
        stx_e3 = gt[2][e3_in]
        stx_e4 = gt[3][e4_in]
        # system state
        stx = arr2int(np.asarray([stx_e1,stx_e2,stx_e3,stx_e4]))
        transitions[stx] += 1
    # create edges with recurrence weights
    for tx in transitions.items():
        stx,txs = tx
        gx.add_edge(sti,stx,weight=txs)
    # plot
    x,weights = zip(*nx.get_edge_attributes(gx,'weight').items())
    cbar = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0,vmax=max(weights)))
    plt.colorbar(cbar)
    nx.draw_circular(gx,edge_color=weights,with_labels=True)
    plt.show()

'''
normativity:
for every possible state of the system (sti)
gives all the transitions to a new state (stx)
given some particular environmental condition
'''
def st_txmap(gt,env=0,norm=True):
    gx = nx.DiGraph()
    st_range = 2**len(gt)
    gx.add_nodes_from(range(st_range))
    transitions = defaultdict(int)
    # in this case the env is defined
    envx = int2arr(env,arr_len=16)
    # now for every sti
    for sti in range(st_range):
        st_e1,st_e2,st_e3,st_e4 = int2arr(sti,arr_len=4)
        e1_in = arr2int(np.asarray([envx[1],envx[2],envx[3],envx[4],st_e1,envx[5],st_e2,1,st_e3]))
        e2_in = arr2int(np.asarray([envx[3],envx[4],st_e1,envx[7],st_e2,1,envx[9],envx[10],st_e4]))
        e3_in = arr2int(np.asarray([st_e1,envx[5],envx[6],1,st_e3,envx[8],st_e4,envx[11],envx[12]]))
        e4_in = arr2int(np.asarray([st_e2,1,st_e3,envx[10],1,envx[11],envx[13],envx[14],envx[15]]))
        elements_in = [e1_in, e2_in, e3_in, e4_in]
        # responses
        elements_stx = []
        for ei,ex_in in enumerate(elements_in):
            elements_stx.append(gt[ei][ex_in])
        # system state
        stx = arr2int(np.asarray([elements_stx]))
        transitions[stx] += 1
        # create edges
        if norm:
            # give colors to valid/invalid transitions
            nb = np.sum(elements_stx)+envx[4]+envx[5]+envx[10]+envx[11]
            tx_color = 'blue' if 2 <= nb <= 3 else 'red'
            gx.add_edge(sti,stx,color=tx_color)
    # plot
    if norm:
        x,colors = zip(*nx.get_edge_attributes(gx,'color').items())
        nx.draw_circular(gx,edge_color=colors,with_labels=True)
    else:
        nx.draw_circular(gx,with_labels=True)
    plt.show()


# animated

# descendent states
